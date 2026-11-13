# RAG pipelines for DevOps: visual chapter

A standalone, ten-page introduction using a fictional production-rollback question. Reading requires no repository setup, account, external application or exercise files.

The reader PDF is `output/pdf/rag-pipelines-for-devops-sample.pdf` in the repository root. `chapter.md` is its searchable reading transcript. The visual composition and copy are authored in `build_sample.py`; the renderer refreshes the transcript. `FACT_CHECK.md` retains the technical source ledger, and `VERIFICATION.json` records publication checks.

Rebuild from the repository root:

```bash
uv run --with reportlab==4.4.10 --with svglib==1.6.0 --with pypdf==6.21.4 python ebook/sample-chapter/build_sample.py
```

Fonts, unchanged TWS artwork and Lucide SVG icons are included with license notices. The PDF carries the icon license as an embedded attachment. Diagrams remain vector graphics at any zoom. No network or model call is made while typesetting. Render all pages to PNG and inspect after changing the composition.
