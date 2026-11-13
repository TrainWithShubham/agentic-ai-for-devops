"""Run sample-chapter boundaries without generative model calls."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from course_labs.rag import DOCS, build_index, extract, retrieve, split


class LabChecks(unittest.TestCase):
    def test_manifest_and_formats(self):
        manifest = json.loads((DOCS / "manifest.json").read_text())
        self.assertEqual(
            {(DOCS / d["file"]).suffix for d in manifest}, {".pdf", ".docx", ".pptx", ".md", ".txt"}
        )
        self.assertEqual(len(manifest), 7)
        for doc in manifest:
            self.assertTrue(any(text.strip() for _, text in extract(DOCS / doc["file"])))

    def test_index_and_current_sources(self):
        index = build_index()
        self.assertEqual(len(index["chunks"]), 18)
        results = retrieve(index, "production rollback approval", limit=20)
        self.assertIn("rollback-checklist", {c["id"] for c in results})
        self.assertNotIn("deploy-old", {c["id"] for c in results})
        self.assertTrue(all(c["current"] and c["location"] for c in results))

    def test_permission_filter(self):
        index = build_index()
        self.assertNotIn(
            "restricted-operations", {c["id"] for c in retrieve(index, "signing rotation", limit=20)}
        )
        self.assertIn(
            "restricted-operations",
            {c["id"] for c in retrieve(index, "signing rotation", role="release-manager", limit=20)},
        )
        with self.assertRaises(PermissionError):
            retrieve(index, "rollback", role="administrator-by-prompt")

    def test_empty_retrieval_skips_generation(self):
        from course_labs.rag import main

        with (
            patch("sys.argv", ["rag", "--live", "--question", "zebras astrophysics xyzzy"]),
            patch("course_labs.rag.complete") as model,
            patch("course_labs.rag.show"),
        ):
            main()
            model.assert_not_called()

    def test_changed_source_rebuilds_fingerprint_and_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docs = root / "data/deployment-docs"
            shutil.copytree(DOCS, docs)
            with patch("course_labs.rag.ROOT", root), patch("course_labs.rag.DOCS", docs):
                before = build_index()
                source = docs / "release-process.md"
                source.write_text(
                    source.read_text() + "\n\nBookverificationphrase: inspect the validation note.\n"
                )
                manifest = json.loads((docs / "manifest.json").read_text())
                manifest[0]["version"] += 1
                (docs / "manifest.json").write_text(json.dumps(manifest))
                after = build_index()
                self.assertNotEqual(before["corpus_version"], after["corpus_version"])
                self.assertIn("deploy-process", {c["id"] for c in retrieve(after, "Bookverificationphrase")})

    def test_split_boundaries(self):
        chunks = split("0123456789abcdefghij", size=8, overlap=2)
        self.assertEqual(chunks[0][-2:], chunks[1][:2])
        self.assertTrue(all(len(c) <= 8 for c in chunks))
        with self.assertRaises(ValueError):
            split("text", size=8, overlap=8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
