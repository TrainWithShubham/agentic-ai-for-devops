# Read Nattu Kaka's records

Time: 40 minutes.

Open `resources/company-knowledge`. The change policy is PDF, the incident report is DOCX, the architecture is PPTX, the runbook is Markdown, and support notes are plain text. The files and incident are synthetic.

```bash
uv run python examples/rag_pipeline.py
uv run runbookops --embedding semantic index
uv run runbookops --embedding semantic search "checkout payment URL connection refused"
uv run runbookops --embedding semantic ask "What should Bagha check when checkout returns 503?"
```

The last command uses offline practice unless `--mode openrouter` is supplied before `ask`. Offline mode displays evidence without claiming a live model wrote the answer.

Follow extraction, chunking, metadata, embeddings, Chroma indexing, retrieval, and answer generation in `src/runbookops/rag.py`. PDF sources retain page numbers; PPTX retains slide numbers; DOCX uses paragraph or table locations. Explain why a scanned PDF needs OCR and why diagrams can lose information in text extraction. OCR is an extension, not silently simulated here.

Coding prompt:

> Explain the chunk size and overlap in `rag.py`. Change the defaults for a small experiment, rebuild with `uv run runbookops --embedding semantic index --rebuild`, and compare the returned excerpts. Keep source metadata and access filters intact. Do not treat similarity as a confidence probability.

Use the current runbook, an undocumented question, and the superseded runbook. Open every citation you rely on. RAG does not retrain the model and a citation does not prove that the claim is supported.

Nattu Kaka remembering a similar incident gives us a lead. Today's logs still decide whether it is relevant.

Check understanding: show a useful source location and explain why the old runbook is excluded. Access controls are tested on Day 2.
