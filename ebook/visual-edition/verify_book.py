"""Publication checks; these do not test a deployed agent or model quality."""

import hashlib
import json
import re
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pdfplumber
from beginner_content import PROJECT_CHAPTER, VIDEO_URL
from plain_content import CHAPTERS
from pypdf import PdfReader
from resources import RESOURCES
from sources import SOURCES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = ROOT / "output/pdf/agentic-ai-for-devops-visual-ebook.pdf"
ARCHIVE = ROOT / "output/pdf/agentic-ai-for-devops-chapters.zip"


def main():
    reader = PdfReader(PDF)
    layout = json.loads((ROOT / "artifacts/book-layout.json").read_text())
    front_pages = layout["front_pages"]
    assert len(reader.pages) == 89
    assert [c["number"] for c in CHAPTERS] == list(range(1, 25))
    for ch in CHAPTERS:
        assert all(key in SOURCES for key in ch["sources"])
        assert len(ch["steps"]) == len(ch["checks"]) == 4
        assert len(ch["principles"]) == 3
        if ch["number"] < PROJECT_CHAPTER:
            assert not re.search(r"runbookops|gada|bagha|jethalal", json.dumps(ch), re.I)
    text = "\n".join(p.extract_text() for p in reader.pages)
    assert not re.search(r"\b(lab|labs|companion|course_labs|uv sync|pip install)\b", text, re.I)
    assert not any(dash in text for dash in ("\u2011", "\u2013", "\u2014"))
    notices = set(reader.attachments)
    assert len(notices) == 4 and "Lucide-LICENSE.txt" in notices
    destinations = {entry.title: entry for entry in reader.outline}
    for ch in CHAPTERS:
        dest = destinations[ch["title"]]
        assert reader.get_destination_page_number(dest) == front_pages + (ch["number"] - 1) * 3
    contents_links = [annotation.get_object() for page in reader.pages[1:4] for annotation in page["/Annots"]]
    assert len(contents_links) == 24
    for i, link in enumerate(contents_links):
        assert link["/Dest"][0].idnum == reader.pages[front_pages + i * 3].indirect_reference.idnum
    video_links = [
        a.get_object()
        for p in reader.pages
        for a in p.get("/Annots", [])
        if a.get_object().get("/A", {}).get("/URI") == VIDEO_URL
    ]
    assert len(video_links) >= 2
    video_evidence = json.loads((HERE / "VIDEO.json").read_text())["qr_verification"]
    assert video_evidence["decoded_url"] == VIDEO_URL
    assert video_evidence["pdf_sha256"] == hashlib.sha256(PDF.read_bytes()).hexdigest()
    resource_evidence = json.loads((HERE / "RESOURCE_QR.json").read_text())
    assert resource_evidence["pdf_sha256"] == hashlib.sha256(PDF.read_bytes()).hexdigest()
    assert resource_evidence["page"] == len(reader.pages)
    assert set(resource_evidence["decoded_urls"]) == {url for _, _, url in RESOURCES}
    resource_links = [a.get_object()["/A"]["/URI"] for a in reader.pages[-1]["/Annots"]]
    assert set(resource_links) == {url for _, _, url in RESOURCES} and len(resource_links) == 12
    assert reader.get_destination_page_number(destinations["Helpful resources"]) == len(reader.pages) - 1
    overflow = []
    with pdfplumber.open(PDF) as document:
        for i, page in enumerate(document.pages):
            for char in page.chars:
                if char["x0"] < 35 or char["x1"] > 565 or char["top"] < 20 or char["bottom"] > 758:
                    overflow.append((i + 1, char["text"]))
    assert not overflow, overflow[:10]
    with ZipFile(ARCHIVE) as z:
        names = sorted(z.namelist())
        assert len(names) == 24 and all(n.endswith(".pdf") for n in names)
        for i, name in enumerate(names):
            chapter = PdfReader(BytesIO(z.read(name)))
            assert len(chapter.pages) == 3
            assert set(chapter.attachments) == notices
            for j, page in enumerate(chapter.pages):
                original = reader.pages[front_pages + i * 3 + j]
                assert page.extract_text() == original.extract_text()
                assert page.get_contents().get_data() == original.get_contents().get_data()
    overlaps = []
    for page in range(1, len(reader.pages) + 1):
        boxes = [b for b in layout["text_bounds"] if b["page"] == page]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1 :]:
                dx = min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"])
                dy = min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"])
                if dx > 3 and dy > 3:
                    overlaps.append((page, a["text"], b["text"]))
    assert not overlaps, overlaps[:3]
    results = {
        "edition_date": "2026-11-13",
        "book_pages": len(reader.pages),
        "chapters": len(CHAPTERS),
        "standalone_chapter_pages": 3,
        "primary_references": len(SOURCES),
        "helpful_resource_qr_codes_verified": len(resource_links),
        "helpful_resources_page": len(reader.pages),
        "reader_word_count_including_navigation": len(text.split()),
        "page_safe_area_overflow_characters": len(overflow),
        "authoring_text_box_overlap_candidates": len(overlaps),
        "chapter_destinations_verified": len(CHAPTERS),
        "pdf_link_annotations": sum(len(p.get("/Annots", [])) for p in reader.pages),
        "asset_license_attachments": sorted(notices),
        "standalone_pages_match_book_content_streams": len(CHAPTERS) * 3,
        "video_url": VIDEO_URL,
        "video_identity_verified": "YouTube oEmbed: title and TrainWithShubham channel",
        "video_qr_verified_against_pdf_hash": True,
        "2027_scope": "Learning direction; product facts reviewed 2026-11-13",
        "concept_chapters_independent_of_application": True,
        "reader_setup_or_exercise_dependencies": False,
        "aws_resources_created": False,
        "model_calls": 0,
        "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "chapters_zip_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        "visual_review": "All 89 pages rendered; the new chapter, contents, guide and changed reference pages visually reviewed. Existing content compared with the reviewed edition, accounting for shifted page numbers.",
        "limits": [
            "Conceptual content, not production-system verification",
            "Fictional operational examples",
            "No live cloud readiness or model-reliability claim",
            "No tagged-PDF accessibility certification",
        ],
    }
    (HERE / "VERIFICATION.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
