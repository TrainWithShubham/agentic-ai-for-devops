# Sample chapter: RAG Pipelines for DevOps

- `chapter.md`: editable manuscript.
- `build_sample.py`: deterministic ReportLab book typesetter, using the included licensed fonts and unchanged TWS artwork.
- `FACT_CHECK.md`: technical claims, primary references and limits.
- `lab/`: standalone, pinned reader lab with synthetic mixed-format documents.
- `VERIFICATION.json`: captured validation summary.

Final reader artifacts are under `output/pdf` in the repository root. The lab archive extracts to `rag-devops-lab` and runs independently of the course or final application.

Rebuild the PDF from the course root:

```bash
uv run --with reportlab==4.4.10 python ebook/sample-chapter/build_sample.py
```

The generator writes `output/pdf/rag-pipelines-for-devops-sample.pdf`. Code snippets are deliberately narrow enough to typeset without breaking executable lines. Render to PNGs with Poppler and inspect after edits; text extraction alone does not establish layout quality.

The authoring source contains no API key. Optional live lab testing requires the reader's own private configuration. The default lab displays retrieved evidence and does not generate an LLM answer.
