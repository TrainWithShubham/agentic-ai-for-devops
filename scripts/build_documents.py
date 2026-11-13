"""Rebuild the small synthetic PDF, DOCX and PPTX fixtures (optional authoring step)."""

from pathlib import Path

from docx import Document
from pptx import Presentation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1] / "data/deployment-docs"


def main():
    pdf = canvas.Canvas(str(ROOT / "rollback-checklist.pdf"), pagesize=A4)
    pdf.setTitle("Catalog API rollback checklist — synthetic training document")
    lines = [
        "Catalog API rollback checklist",
        "Document ID: rollback-checklist. Version 2. Updated 2026-11-13.",
        "Synthetic training document. No production access or commands.",
        "1. Record the incident, environment and previous healthy image digest.",
        "2. Obtain release-manager approval before a production rollback.",
        "3. Restore that exact digest through the normal deployment pipeline.",
        "4. Validate /health and /catalog and monitor the error rate.",
        "5. If validation fails, stop promotion and escalate to the service owner.",
    ]
    for i, line in enumerate(lines):
        pdf.drawString(48, 790 - 28 * i, line)
    pdf.save()
    doc = Document()
    doc.add_heading("Catalog API release incident", 0)
    for line in [
        "Document ID: release-incident. Version 1. Updated 2026-11-13. Synthetic training material.",
        "During an earlier deployment, /health passed but /catalog returned errors because an index was unavailable.",
        "The release-manager approved rollback to the recorded healthy image digest.",
        "The team added an application smoke test and error-rate observation to the deployment checklist.",
        "This historical incident suggests checks; it does not establish the cause of a new failure.",
    ]:
        doc.add_paragraph(line)
    doc.save(ROOT / "release-incident.docx")
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[1])
    slide.shapes.title.text = "Catalog API deployment architecture"
    slide.placeholders[
        1
    ].text = "Document ID: deploy-architecture. Synthetic training material.\nCI builds an immutable container image.\nStaging receives the image first.\nA release-manager approves promotion to production.\nThe /catalog route reads from a search index."
    deck.save(ROOT / "deployment-architecture.pptx")
    print("Built the three synthetic mixed-format source documents.")


if __name__ == "__main__":
    main()
