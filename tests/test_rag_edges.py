import dataclasses

import numpy as np
import pytest
from docx import Document

from runbookops.rag import Retriever, chunks, extract
from runbookops.security import principal


def test_extract_tables_empty_text_and_unsupported_formats(tmp_path):
    doc = Document()
    doc.add_paragraph("")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Key"
    table.cell(0, 1).text = "Value"
    path = tmp_path / "table.docx"
    doc.save(path)
    assert ("table 1", "Key | Value") in extract(path)
    for suffix in (".ppt", ".json"):
        with pytest.raises(ValueError):
            extract(tmp_path / ("invalid" + suffix))
    assert list(chunks([("blank", "   ")])) == []


def test_semantic_vectors_are_reused_and_invalid_embedding_rejected(settings, monkeypatch):
    import fastembed

    made = []

    class Embeddings:
        def __init__(self, *args, **kwargs):
            made.append(kwargs)

        def embed(self, texts):
            return [np.array([1.0, 0.0]) for _ in texts]

    monkeypatch.setattr(fastembed, "TextEmbedding", Embeddings)
    retriever = Retriever(dataclasses.replace(settings, embedding="semantic"))
    assert retriever.embed(["one"]) == [[1.0, 0.0]]
    assert retriever.embed(["two"]) == [[1.0, 0.0]] and len(made) == 1
    invalid = Retriever(dataclasses.replace(settings, embedding="invalid"))
    with pytest.raises(ValueError):
        invalid.embed(["hello"])


def test_rebuild_handles_missing_collection_but_not_database_failure(settings, monkeypatch):
    r = Retriever(settings)
    original = r.client.delete_collection

    def absent(name):
        raise ValueError("does not exist")

    monkeypatch.setattr(r.client, "delete_collection", absent)
    assert r.index(force=True) > 0
    monkeypatch.setattr(r.client, "delete_collection", original)
    assert r.index(force=True) > 0

    def failed(name):
        raise RuntimeError("storage is unavailable")

    monkeypatch.setattr(r.client, "delete_collection", failed)
    with pytest.raises(RuntimeError, match="storage"):
        r.index(force=True)


def test_rag_existing_collection_empty_documents_and_cache_expiry(settings, monkeypatch, tmp_path):
    import runbookops.rag as module

    r = Retriever(settings)
    original_chunks = module.chunks
    monkeypatch.setattr(module, "chunks", lambda parts: [("empty", ""), *original_chunks(parts)])
    original = module.extract
    # An extracted blank section must not become an indexed empty row.
    monkeypatch.setattr(module, "extract", lambda p: [("blank", "")] + original(p))
    assert r.index() > 0
    r2 = Retriever(settings)
    assert r2.index() == r.index()
    actor = principal("bagha")
    assert not r.search("checkout payment service", actor)["cache_hit"]
    monkeypatch.setattr(module.time, "monotonic", lambda: 10**15)
    assert not r.search("checkout payment service", actor)["cache_hit"]
    for question in ("", "x" * 1201, 123):
        with pytest.raises(ValueError):
            r.search(question, actor)
