# Agentic AI for DevOps: a visual field guide

Beginner learning edition for 2027; technical review dated 13 November 2026. By Shubham Londhe, Train With Shubham.

The book has 107 pages and 23 standalone chapters. It follows the six v2 course modules, then adds separate Temporal and Amazon Bedrock AgentCore bonuses. It assumes no AI background; basic Linux and Python familiarity helps. Models, inference, APIs and learning mistakes come before tools and frameworks. Examples are fictional, require no setup and do not depend on exercise files. Application-specific material first appears in chapter 21.

Reader deliverables in the repository root:

- [Complete PDF](../../output/pdf/agentic-ai-for-devops-visual-ebook.pdf)
- [Individual chapter PDFs](../../output/pdf/agentic-ai-for-devops-chapters.zip)

The individual chapters preserve printed book page numbers for easy cross-reference. Each has its own introduction, explanation, worked scenario, failure review and external source links. No other chapter is required to understand its example.

## Editable source

- `content.py`: original core chapter copy and diagram data.
- `beginner_content.py`: beginner chapters, final reading order and explanatory updates.
- `VIDEO.json`: YouTube metadata confirming the linked Hindi-channel tutorial.
- `illustrations.py`: original vector diagrams.
- `build_book.py`: ReportLab renderer and standalone exports.
- `sources.py`: primary-source links and glossary.
- [MANUSCRIPT.md](MANUSCRIPT.md): reading transcript, regenerated from the canonical source.
- `chapters/`: one regenerated Markdown transcript per chapter, including diagram reading order.
- [FACT_CHECK.md](FACT_CHECK.md): source and claim review scope.
- `VERIFICATION.json`: publication checks and artifact hashes.

Edit the Python content data before rebuilding; edits made only to a generated Markdown transcript will be overwritten. Shared font, icon and branding assets live in `../sample-chapter/assets`. They are included in this repository, not downloaded at build time. Asset license notices are embedded in the PDFs. The earlier approved sample remains available independently.

Rebuild from the repository root:

```bash
uv run --with reportlab==4.4.10 --with svglib==1.6.0 --with pypdf==6.21.4 python ebook/visual-edition/build_book.py
```

The authoring runtime also needs the SVG dependencies resolved by svglib. Render the result with Poppler and inspect after changes:

```bash
pdftoppm -scale-to 1100 -png output/pdf/agentic-ai-for-devops-visual-ebook.pdf tmp/pdfs/book-review
```

The renderer checks text fit while authoring. It is not a substitute for visual review or a technical content review. `artifacts/book-layout.json` is an ignored authoring record, not reader content.

The Claude Code chapter includes a clickable lesson link and QR code. A first-month learning plan and a 2027 skills compass follow the chapters. The 2027 framing is a learning recommendation, not a forecast of product capabilities.

## Maintenance

Recheck the linked primary references before each new edition. Review changes to MCP protocol versions, LangGraph persistence, Temporal replay/retry behavior and AgentCore Harness/Runtime capabilities in particular. Model prices, quotas, framework hiring rankings and deployment readiness are deliberately not asserted.

The book explains engineering concepts. It does not certify a production architecture, provide tagged-PDF accessibility, establish model reliability or claim a fresh cloud deployment. No infrastructure provisioning or model calls occur during the build.

The publication verifier checks the decoded-QR evidence recorded in `VIDEO.json` against the final PDF hash. After rebuilding an edited edition, render the video page, decode its QR, then refresh that public evidence before running `verify_book.py`. The current edition was decoded with zxing-cpp 3.1.1. The verifier needs pypdf and pdfplumber in the authoring environment; these are publication tools, not reader requirements.
