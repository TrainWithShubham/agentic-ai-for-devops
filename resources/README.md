# Company knowledge for the labs

Everything here is synthetic. The online Gada Electronics store and incident were invented for the workshop; no company/customer data is included.

`company-knowledge/manifest.json` defines each document's source ID, access, current/superseded status, version, and update date. The application reads these fields before returning retrieval results. Files remain visible on a learner's own laptop; retrieval RBAC does not claim to restrict local filesystem access.

The pack contains PDF, DOCX, PPTX, Markdown, and text. PDF page numbers, slide numbers, Word paragraph/table locations, and Markdown headings become citations. Scanned pages need OCR; diagrams and speaker notes are not fully interpreted by the supplied text loaders.

Use `incidents/checkout-503.json` as the seeded alert. This fixture represents monitoring input; the course does not provision a monitoring platform.

## Regenerate the fixtures

Learners use the supplied files. Instructors can edit `scripts/build_resources.py` and regenerate with:

```bash
uv run python scripts/build_resources.py
uv run runbookops index --rebuild
```

Regeneration needs LibreOffice for PPTX conversion. The script finds it on PATH or at the standard macOS app location. DOCX and PDF are generated locally; presentation source is editable FODP under `sources`.

Review regenerated files visually and run the extraction tests. Changing a document changes its corpus fingerprint; changing chunking code requires an explicit rebuild as well. Keep the same embedding configuration when comparing indexes.
