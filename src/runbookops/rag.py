"""Mixed-format retrieval with source locations, metadata filters, and scoped caching."""

import hashlib
import json
import math
import os
import re
import threading
import time
import zipfile
from collections import Counter
from xml.etree import ElementTree

from .security import redact, require

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
CACHE_TTL = 120
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def extract(path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader

        return [(f"page {i}", page.extract_text() or "") for i, page in enumerate(PdfReader(path).pages, 1)]
    if suffix == ".docx":
        from docx import Document

        doc = Document(path)
        parts = [
            (f"paragraph {i}", para.text) for i, para in enumerate(doc.paragraphs, 1) if para.text.strip()
        ]
        for i, table in enumerate(doc.tables, 1):
            parts.append(
                (f"table {i}", "\n".join(" | ".join(cell.text for cell in row.cells) for row in table.rows))
            )
        return parts
    if suffix == ".pptx":
        with zipfile.ZipFile(path) as archive:
            names = sorted(
                (n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                key=lambda n: int(re.search(r"slide(\d+)", n)[1]),
            )
            return [
                (f"slide {i}", "\n".join(ElementTree.fromstring(archive.read(name)).itertext()))
                for i, name in enumerate(names, 1)
            ]
    if suffix in (".md", ".txt"):
        text = path.read_text()
        if suffix == ".md":
            chunks = re.split(r"(?m)^## ", text)
            return [(chunk.splitlines()[0].lstrip("# "), chunk) for chunk in chunks if chunk.strip()]
        return [("text", text)]
    if suffix == ".ppt":
        raise ValueError("Convert legacy PPT to PPTX before indexing")
    raise ValueError(f"Unsupported document format: {suffix}")


def chunks(parts, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    for location, text in parts:
        text = re.sub(r"[ \t]+", " ", text).strip()
        for start in range(0, len(text), size - overlap):
            yield location, redact(text[start : start + size])


class Retriever:
    def __init__(self, settings):
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        self.settings = settings
        self.folder = settings.root / "resources/company-knowledge"
        self.client = chromadb.PersistentClient(
            path=str(settings.data / "chroma"), settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.cache = {}
        self.lock = threading.RLock()
        self.model = None
        self.collection = None
        self.version = None

    def fingerprint(self):
        h = hashlib.sha256(
            (f"{self.settings.embedding}:chunk{CHUNK_SIZE}-overlap{CHUNK_OVERLAP}:v2").encode()
        )
        manifest = json.loads((self.folder / "manifest.json").read_text())
        h.update(json.dumps(manifest, sort_keys=True).encode())
        for item in manifest:
            h.update((self.folder / item["file"]).read_bytes())
        return h.hexdigest()[:20], manifest

    def embed(self, texts):
        if self.settings.embedding == "semantic":
            if self.model is None:
                from fastembed import TextEmbedding

                self.model = TextEmbedding(
                    EMBEDDING_MODEL,
                    cache_dir=os.getenv("RUNBOOKOPS_MODEL_CACHE", str(self.settings.data / "models")),
                )
            return [vector.tolist() for vector in self.model.embed(texts)]
        if self.settings.embedding != "hash":
            raise ValueError("Embedding must be hash (lexical, offline) or semantic (download once)")
        result = []
        for text in texts:
            vector = [0.0] * 384
            words = re.findall(r"[a-z0-9_]+", text.lower())
            for word, count in Counter(words).items():
                index = int(hashlib.sha256(word.encode()).hexdigest()[:8], 16) % len(vector)
                vector[index] += count
            norm = math.sqrt(sum(v * v for v in vector)) or 1
            result.append([v / norm for v in vector])
        return result

    def index(self, force=False):
        with self.lock:
            version, manifest = self.fingerprint()
            if self.version == version and self.collection is not None and not force:
                return self.collection.count()
            name = "gada-" + version
            if force:
                try:
                    self.client.delete_collection(name)
                except Exception as error:
                    if "does not exist" not in str(error) and "not found" not in str(error).lower():
                        raise
            collection = self.client.get_or_create_collection(
                name, embedding_function=None, metadata={"hnsw:space": "cosine"}
            )
            if not collection.count():
                rows = []
                for item in manifest:
                    for number, (location, text) in enumerate(chunks(extract(self.folder / item["file"]))):
                        if text:
                            rows.append(
                                (
                                    f"{item['id']}:{number}",
                                    text,
                                    {
                                        "source": item["id"],
                                        "file": item["file"],
                                        "location": location,
                                        "title": item["title"],
                                        "access": item["access"],
                                        "current": item["current"],
                                        "version": item["version"],
                                        "updated": item["updated"],
                                        "service": item["service"],
                                    },
                                )
                            )
                collection.upsert(
                    ids=[r[0] for r in rows],
                    documents=[r[1] for r in rows],
                    metadatas=[r[2] for r in rows],
                    embeddings=self.embed([r[1] for r in rows]),
                )
            self.collection = collection
            self.version = version
            self.cache.clear()
            return collection.count()

    def search(self, query, actor, limit=5):
        require(actor, "read")
        if not isinstance(query, str) or not 1 <= len(query) <= 1200:
            raise ValueError("Query must contain 1 to 1200 characters")
        with self.lock:
            self.index()
            key = (actor.user, actor.role, tuple(sorted(actor.scopes)), query, self.version, min(limit, 8))
            cached = self.cache.get(key)
            if cached and time.monotonic() - cached[0] < CACHE_TTL:
                return {
                    "results": cached[1],
                    "cache_hit": True,
                    "corpus_version": self.version,
                    "embedding": self.settings.embedding,
                }
            response = self.collection.query(
                query_embeddings=self.embed([query]),
                n_results=min(limit, 8),
                where={"$and": [{"current": {"$eq": True}}, {"access": {"$in": ["public", actor.role]}}]},
                include=["documents", "metadatas", "distances"],
            )
            matches = []
            for text, metadata, distance in zip(
                response["documents"][0], response["metadatas"][0], response["distances"][0]
            ):
                score = 1 - distance
                # A similarity is a retrieval rank signal, never a confidence probability.
                if score >= (0.25 if self.settings.embedding == "semantic" else 0.09):
                    matches.append({**metadata, "text": text, "similarity": round(score, 4)})
            self.cache[key] = (time.monotonic(), matches)
            return {
                "results": matches,
                "cache_hit": False,
                "corpus_version": self.version,
                "embedding": self.settings.embedding,
            }
