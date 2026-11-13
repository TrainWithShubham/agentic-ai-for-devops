"""Typeset the visual ebook, standalone chapters and editable reading transcripts."""

import html
import json
import math
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZIP_DEFLATED, ZipFile

from beginner_content import CHAPTERS, CLAUDE_CHAPTER, PROJECT_CHAPTER, PROMPT_CHAPTER, VIDEO_URL
from illustrations import draw
from pypdf import PdfReader, PdfWriter
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from sources import GLOSSARY, SOURCES
from svglib.svglib import svg2rlg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSETS = HERE.parent / "sample-chapter/assets"
OUT = ROOT / "output/pdf/agentic-ai-for-devops-visual-ebook.pdf"
RECORDS = []
FRONT_PAGES = 5


class Book:
    ink = "#272131"
    muted = "#62596C"
    purple = "#7243B3"
    gold = "#FFCE80"
    paper = "#FCFBF8"
    pale = "#F0EAF7"
    dark = "#18131F"
    green = "#236650"
    red = "#A53348"

    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=(600, 780))
        self.c.setTitle("Agentic AI for DevOps | A visual field guide")
        self.c.setAuthor("Shubham Londhe | Train With Shubham")
        self.c.setCreator("TWS | Beginner learning edition | Reviewed 13 November 2026")
        self.page_number = 0
        self.current_text = []
        self.text_bounds = []
        self.chapter_ranges = []
        for name, filename in [
            ("Sans", "Manrope-Regular.ttf"),
            ("Bold", "Manrope-Bold.ttf"),
            ("Serif", "SourceSerif4-Regular.ttf"),
            ("Mono", "PlexMono-Regular.ttf"),
        ]:
            pdfmetrics.registerFont(TTFont(name, str(ASSETS / "fonts" / filename)))

    def rect(self, x, y, w, h, fill, radius=12):
        self.c.setFillColor(colors.HexColor(fill))
        self.c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

    def circle(self, x, y, r, fill):
        self.c.setFillColor(colors.HexColor(fill))
        self.c.circle(x, y, r, fill=1, stroke=0)

    def line(self, x1, y1, x2, y2, fill, dashed=False):
        self.c.saveState()
        self.c.setStrokeColor(colors.HexColor(fill))
        self.c.setLineWidth(1.3)
        if dashed:
            self.c.setDash(3, 4)
        self.c.line(x1, y1, x2, y2)
        self.c.restoreState()

    def text(self, s, x, y, size=12, font="Sans", fill=None):
        width = pdfmetrics.stringWidth(s, font, size)
        assert x >= 35 and x + width <= 565, (self.page_number, s, x + width)
        self.c.setFillColor(colors.HexColor(fill or self.ink))
        self.c.setFont(font, size)
        self.c.drawString(x, y, s)
        self.current_text.append(s)
        self.text_bounds.append(dict(page=self.page_number, text=s, x=x, y=y, width=width, height=size))

    def center(self, s, x, y, size=12, fill=None, font="Sans"):
        self.text(s, x - pdfmetrics.stringWidth(s, font, size) / 2, y, size, font, fill)

    def prose(self, s, x, top, width=504, size=12, fill=None, font="Sans", max_height=100):
        style = ParagraphStyle(
            "copy",
            fontName=font,
            fontSize=size,
            leading=size * 1.43,
            textColor=colors.HexColor(fill or self.muted),
        )
        p = Paragraph(html.escape(s), style)
        _, height = p.wrap(width, 700)
        assert height <= max_height + 0.1, (self.page_number, s, height, max_height)
        assert top - height >= 53, (self.page_number, s, top - height)
        p.drawOn(self.c, x, top - height)
        self.current_text.append(s)
        self.text_bounds.append(
            dict(page=self.page_number, text=s, x=x, y=top - height, width=width, height=height)
        )
        return height

    def icon(self, name, x, y, size=28, fill=None):
        svg = (ASSETS / f"icons/{name}.svg").read_text().replace("currentColor", fill or self.purple)
        d = svg2rlg(BytesIO(svg.encode()))
        d.scale(size / d.width, size / d.height)
        renderPDF.draw(d, self.c, x, y)

    def arrow(self, x1, y1, x2, y2, fill=None):
        fill = fill or self.purple
        self.line(x1, y1, x2, y2, fill)
        angle = math.atan2(y2 - y1, x2 - x1)
        for offset in (-0.48, 0.48):
            self.line(x2, y2, x2 - 6 * math.cos(angle + offset), y2 - 6 * math.sin(angle + offset), fill)

    def node(self, x, y, w, h, title, body, name, fill=None, compact=False):
        self.rect(x, y, w, h, fill or self.pale)
        self.icon(name, x + 14, y + h - 38, 25)
        if compact:
            self.prose(title, x + 50, y + h - 13, w - 64, 12, self.ink, font="Bold", max_height=36)
            self.prose(body, x + 50, y + h - 35, w - 65, 10.6, max_height=h - 42)
            return
        title_height = self.prose(title, x + 50, y + h - 16, w - 64, 12, self.ink, font="Bold", max_height=36)
        body_top = y + h - max(54, title_height + 25)
        self.prose(body, x + 15, body_top, w - 30, 10.6, max_height=body_top - y - 10)

    def record_diagram(self, nodes):
        self.current_text.extend(f"{title}: {body}" for title, body in nodes)

    def page(self, title, section="", dark=False, bookmark=None):
        self.page_number += 1
        self.current_text = []
        self.c.setFillColor(colors.HexColor(self.dark if dark else self.paper))
        self.c.rect(0, 0, 600, 780, fill=1, stroke=0)
        self.text("AGENTIC AI FOR DEVOPS", 48, 744, 8, "Bold", self.gold if dark else self.purple)
        self.text(section.upper()[:27], 391, 744, 7.5, "Mono", "#D3C6E0" if dark else self.muted)
        self.line(48, 49, 552, 49, "#3C3149" if dark else "#DED6E6")
        self.text("TRAIN WITH SHUBHAM", 48, 29, 8, "Bold", "#D3C6E0" if dark else self.muted)
        self.text(f"{self.page_number:02}", 532, 29, 9, "Mono", self.gold if dark else self.purple)
        if bookmark:
            self.c.bookmarkPage(bookmark)
            self.c.addOutlineEntry(title, bookmark, 0)
        self.page_title = title

    def heading(self, title, intro, eyebrow=""):
        if eyebrow:
            self.text(eyebrow.upper(), 48, 699, 9, "Mono", self.purple)
        h = self.prose(title, 48, 678, 504, 25, self.ink, font="Bold", max_height=73)
        self.prose(intro, 48, 678 - h - 17, 504, 11.6, max_height=68)

    def note(self, s):
        self.rect(48, 73, 504, 79, "#F5EDDD")
        self.icon("book-open", 64, 103, 25, "#7E5520")
        self.prose(s, 106, 133, 428, 10.6, "#624A28", max_height=56)

    def finish(self):
        RECORDS.append(dict(page=self.page_number, title=self.page_title, text=self.current_text))
        self.c.showPage()

    def opener(self, ch):
        self.page(ch["title"], ch["module"], True, f"chapter-{ch['number']}")
        self.text(f"{ch['number']:02}", 45, 603, 94, "Mono", "#80609B")
        for radius in (40, 62, 86):
            self.c.setStrokeColor(colors.HexColor("#3E304C"))
            self.c.circle(462, 628, radius, stroke=1, fill=0)
        self.circle(462, 628, 40, "#2A2035")
        self.icon(ch["icon"], 439, 605, 46, self.gold)
        self.circle(410, 559, 5, self.gold)
        self.circle(530, 679, 4, self.purple)
        h = self.prose(ch["title"], 48, 533, 504, 32, "#FFFFFF", font="Bold", max_height=96)
        top = 533 - h - 25
        self.prose(ch["question"], 48, top, 490, 21, self.gold, font="Serif", max_height=66)
        self.prose(ch["intro"], 48, top - 83, 496, 12, "#D8CEE3", max_height=105)
        for i, (title, body) in enumerate(ch["principles"]):
            x = 48 + i * 176
            self.rect(x, 91, 152, 150, "#2A2035")
            self.text(f"{i + 1:02}", x + 14, 218, 9, "Mono", self.gold)
            self.prose(title, x + 14, 201, 124, 12, "#FFFFFF", font="Bold", max_height=36)
            self.prose(body, x + 14, 164, 124, 10.4, "#D8CEE3", max_height=60)
        self.finish()

    def diagram(self, ch):
        self.page(ch["diagram_title"], f"{ch['number']:02} / Visual model")
        self.heading(ch["diagram_title"], ch["diagram_intro"], "Understand the system")
        draw(self, ch)
        self.note(ch["diagram_note"])
        self.finish()

    def example(self, ch):
        self.page(ch["case_title"], f"{ch['number']:02} / In practice")
        self.heading(ch["case_title"], ch["case_intro"], "A worked example")
        if ch["number"] == PROMPT_CHAPTER:
            for i, (title, body) in enumerate(ch["steps"]):
                y = 446 - i * 94
                self.rect(48, y, 504, 84, self.pale)
                self.text(title, 64, y + 63, 12, "Bold", self.purple)
                self.prose(body, 64, y + 51, 471, 10.5, self.ink, max_height=47)
            self.note(ch["case_note"])
            self.finish()
            return
        for i, (title, body) in enumerate(ch["steps"]):
            top = 548 - i * (80 if ch["number"] == CLAUDE_CHAPTER else 103)
            self.circle(73, top - 13, 22, self.dark)
            self.center(f"{i + 1:02}", 73, top - 18, 12, self.gold, font="Mono")
            if i < 3:
                self.line(73, top - 42, 73, top - 71, "#C8B5D8")
            self.text(title, 113, top - 5, 14, "Bold", self.purple)
            self.prose(body, 113, top - 22, 422, 12, max_height=59)
        if ch["number"] == CLAUDE_CHAPTER:
            self.video_panel(ch["case_note"])
        else:
            self.note(ch["case_note"])
        self.finish()

    def video_panel(self, caption):
        self.rect(48, 73, 504, 159, "#F5EDDD")
        qr = QrCodeWidget(VIDEO_URL, barLevel="M")
        x0, y0, x1, y1 = qr.getBounds()
        drawing = Drawing(112, 112, transform=[112 / (x1 - x0), 0, 0, 112 / (y1 - y0), 0, 0])
        drawing.add(qr)
        renderPDF.draw(drawing, self.c, 65, 96)
        self.text("2026 VIDEO / HINDI / TRAINWITHSHUBHAM", 197, 210, 8, "Mono", "#624A28")
        self.prose("Claude Code In One Shot", 197, 194, 338, 16, self.ink, font="Bold", max_height=47)
        self.prose(caption, 197, 163, 332, 10.3, "#624A28", max_height=60)
        self.text("Open the YouTube lesson", 197, 93, 10, "Bold", self.purple)
        self.c.linkURL(VIDEO_URL, (61, 86, 538, 225), relative=0)

    def review(self, ch):
        self.page("When it goes wrong", f"{ch['number']:02} / Engineering review")
        self.heading(
            "When it goes wrong",
            "Inspect the boundary that failed. Keep the observed result separate from the explanation.",
            "Failure and correction",
        )
        for x, title, body, name, fill, tint in [
            (48, "Failure", ch["failure"], "circle-x", "#F7E9EB", self.red),
            (312, "Correction", ch["correction"], "circle-check", "#E8F1EB", self.green),
        ]:
            self.rect(x, 369, 240, 211, fill)
            self.icon(name, x + 17, 532, 30, tint)
            self.text(title, x + 17, 512, 15, "Bold", tint)
            self.prose(body, x + 17, 496, 206, 11.4, max_height=113)
        for i, check in enumerate(ch["checks"]):
            y = 329 - i * 45
            self.icon("circle-check", 48, y - 6, 20)
            self.prose(check, 81, y + 10, 461, 12, self.ink, max_height=35)
        self.text("FURTHER READING", 48, 125, 8, "Mono", self.purple)
        for i, key in enumerate(ch["sources"]):
            label, _ = SOURCES[key]
            x = 48 + (i % 2) * 264
            y = 104 - (i // 2) * 16
            # Short handles point to the complete source entry at the back.
            label = label.replace("Anthropic: ", "").replace("AgentCore: ", "AWS: ")
            if pdfmetrics.stringWidth(label, "Sans", 8.1) > 240:
                label = label[:40]
            self.text(label, x, y, 8.1, fill=self.muted)
            self.c.linkURL(SOURCES[key][1], (x, y - 2, x + 240, y + 10), relative=0)
        self.finish()


def front(b):
    b.page("Agentic AI for DevOps", "Beginner / 2027 learning", True, "cover")
    b.c.drawImage(str(ASSETS / "tws-logo.png"), 39, 577, 125, 125, mask="auto", preserveAspectRatio=True)
    b.text("Agentic AI", 48, 534, 48, "Bold", "#FFFFFF")
    b.text("for DevOps", 48, 474, 48, "Bold", "#FFFFFF")
    b.prose("A beginner's visual guide", 48, 427, 480, 24, b.gold, font="Serif")
    b.prose(
        "Start with models and useful prompts. Build the engineering habits to carry into 2027.",
        48,
        379,
        455,
        16,
        "#D8CEE3",
        max_height=60,
    )
    for x, name, title in [
        (48, "brain-circuit", "Reason"),
        (224, "files", "Retrieve"),
        (400, "shield-check", "Review"),
    ]:
        b.rect(x, 180, 152, 117, "#2A2035")
        b.icon(name, x + 56, 235, 39, b.gold)
        b.center(title, x + 76, 203, 13, "#FFFFFF")
    b.text("SHUBHAM LONDHE", 48, 130, 12, "Bold", "#FFFFFF")
    b.text("TRAIN WITH SHUBHAM / BEGINNER LEARNING EDITION", 48, 104, 8, "Mono", b.gold)
    b.text("Technically reviewed 13 November 2026", 48, 80, 9, "Sans", "#D8CEE3")
    b.finish()
    for start, end, subtitle in [
        (0, 8, "Start from scratch, then understand tools and loops"),
        (8, 16, "Connect knowledge, control actions and operate the system"),
        (16, 23, "Measure, release, integrate and explore the bonuses"),
    ]:
        b.page("Contents", "Find your chapter", bookmark="contents" if start == 0 else "contents-2")
        b.heading("Contents", subtitle, "Read in sequence or choose a chapter")
        for i, ch in enumerate(CHAPTERS[start:end]):
            y = 553 - i * 46
            b.text(f"{ch['number']:02}", 48, y, 11, "Mono", b.purple)
            b.text(ch["title"], 89, y, 12, "Bold")
            pg = FRONT_PAGES + 1 + (ch["number"] - 1) * 4
            b.text(f"{pg:02}", 529, y, 10, "Mono", b.muted)
            b.line(89, y - 16, 552, y - 16, "#E4DEEA")
            b.c.linkRect("", f"chapter-{ch['number']}", (45, y - 13, 553, y + 17), relative=0, thickness=0)
        if start == 16:
            b.prose(
                "A first-month learning plan, a 2027 skills compass, glossary and linked sources follow. Every example is self-contained; no setup is needed.",
                48,
                102,
                504,
                11,
                max_height=48,
            )
        b.finish()
    b.page("How to use this guide", "Six modules / one foundation", bookmark="guide")
    b.heading(
        "How to use this guide",
        "New to AI? Start at chapter 1. Basic Linux and Python familiarity helps; models, prompts and agent terms are explained as you go.",
        "Before you begin",
    )
    rows = [
        ("01", "Foundations", "Chapters 1-6 / mistakes, models, prompts and Claude Code."),
        ("02", "Agents and tools", "Chapters 7-10 / tools, bounded loops, MCP and LangGraph."),
        ("03", "Company knowledge", "Chapters 11-12 / RAG, extraction and retrieval quality."),
        ("04", "Control and approval", "Chapters 13-15 / identity, review and guardrails."),
        ("05", "Operate the system", "Chapters 16-20 / harness, cost, traces, evaluations and releases."),
        ("06", "Integrated application", "Chapter 21 / a fictional simulator case study."),
    ]
    for i, (num, title, body) in enumerate(rows):
        y = 540 - i * 64
        b.circle(65, y, 15, b.purple)
        b.center(num, 65, y - 4, 9, "#FFFFFF", font="Mono")
        b.text(title, 100, y + 6, 13, "Bold")
        b.prose(body, 100, y - 5, 440, 10.8, max_height=33)
    b.note(
        "Bonuses cover Temporal and AgentCore. Policies and scenarios are fictional. Architecture illustrations do not claim a live deployment, production safety certification or hiring outcome."
    )
    b.finish()


def learning_path(b):
    b.page("Your first month", "A suggested learning path", bookmark="first-month")
    b.heading(
        "Your first month",
        "Move at your own pace. Use public or sanitized examples; these milestones do not require the course application.",
        "Learn through small, explainable changes",
    )
    milestones = [
        (
            "Week 1 / understand",
            "Explain one CI error using its log. Compare a vague prompt with a request that includes evidence and a validation check.",
        ),
        (
            "Week 2 / retrieve",
            "Follow a deployment question from source text to selected evidence. Explain why a current policy should beat a retired procedure.",
        ),
        (
            "Week 3 / control",
            "Draw one read-only tool call and its validation. Describe how you would deny an unknown resource or an unauthorized write.",
        ),
        (
            "Week 4 / assess",
            "Review a successful case and a failure. State which observation supports the answer and what your checks cannot establish.",
        ),
    ]
    for i, (title, body) in enumerate(milestones):
        top = 548 - i * 101
        b.circle(73, top - 13, 21, b.purple)
        b.center(str(i + 1), 73, top - 18, 13, "#FFFFFF")
        b.text(title, 113, top - 5, 14, "Bold", b.purple)
        b.prose(body, 113, top - 23, 422, 11.6, max_height=58)
    b.note(
        "Keep a short learning record: the question, the observed evidence, one change and its result. Explain the result without relying on the generated summary."
    )
    b.finish()
    b.page("Carry these habits into 2027", "2027 / Learning direction", bookmark="2027-compass")
    b.heading(
        "Carry these habits into 2027",
        "Products will change. Invest in the engineering skills that let you inspect a new tool instead of trusting its label.",
        "What to keep learning",
    )
    skills = [
        ("Linux + debugging", "Read processes, logs and errors so you can challenge a diagnosis.", "search"),
        (
            "Python + APIs",
            "Understand the tool contract, inputs, exceptions and returned evidence.",
            "list-checks",
        ),
        ("IAM + security", "Separate identity, permissions, credentials and human approval.", "lock-keyhole"),
        (
            "CI + evaluations",
            "Test changes to prompts, tools and models against reviewed cases.",
            "git-branch",
        ),
        ("Observability", "Explain a trace, a cost increase and an incomplete outcome.", "activity"),
    ]
    for i, (title, body, name) in enumerate(skills):
        y = 475 - i * 64
        b.icon(name, 52, y + 18, 28)
        b.text(title, 105, y + 40, 13, "Bold", b.purple)
        b.prose(body, 105, y + 24, 430, 11.2, max_height=34)
    b.note(
        "This is a recommended learning direction for 2027, based on documentation reviewed on 13 November 2026. Recheck product behavior, models, prices and permissions before use."
    )
    b.finish()


def back(b):
    for start in range(0, len(GLOSSARY), 14):
        b.page("A compact glossary", "Terms in plain language", bookmark=f"glossary-{start}")
        b.heading(
            "A compact glossary",
            "Definitions describe the meaning used in this book.",
            "Keep these distinctions clear",
        )
        for i, (term, definition) in enumerate(GLOSSARY[start : start + 14]):
            y = 559 - i * 33
            b.text(term, 48, y, 10.5, "Bold", b.purple)
            b.prose(definition, 204, y + 10, 348, 9.6, max_height=28)
        b.finish()
    keys = list(SOURCES)
    for start in range(0, len(keys), 12):
        b.page("Primary sources", "Reviewed 13 November 2026", bookmark=f"sources-{start}")
        b.heading(
            "Primary sources",
            "Links support technical review and further reading. Product capabilities can change after this edition.",
            "References and credits",
        )
        for i, key in enumerate(keys[start : start + 12]):
            title, url = SOURCES[key]
            y = 557 - i * 36
            chapter_numbers = ", ".join(str(ch["number"]) for ch in CHAPTERS if key in ch["sources"])
            b.text(title, 48, y, 10.5, "Bold", b.purple)
            b.text(f"{urlparse(url).netloc}  /  Chapters {chapter_numbers}", 48, y - 14, 8.3, fill=b.muted)
            b.c.linkURL(url, (45, y - 20, 555, y + 14), relative=0)
        if start + 12 >= len(keys):
            b.prose(
                "Original diagrams and explanations by Train With Shubham. TWS artwork is used unchanged. Lucide icons and included fonts retain their license notices; asset notices are embedded in this PDF.",
                48,
                107,
                504,
                9.5,
                max_height=47,
            )
        b.finish()


def manuscripts():
    directory = HERE / "chapters"
    directory.mkdir(exist_ok=True)
    expected = {
        f"{ch['number']:02}-{re.sub(r'[^a-z0-9]+', '-', ch['title'].lower()).strip('-')}.md"
        for ch in CHAPTERS
    }
    for stale in directory.glob("*.md"):
        if stale.name not in expected:
            stale.unlink()
    paths = []
    for ch in CHAPTERS:
        slug = re.sub(r"[^a-z0-9]+", "-", ch["title"].lower()).strip("-")
        path = directory / f"{ch['number']:02}-{slug}.md"
        lines = [f"# {ch['title']}", f"\n{ch['module']}\n", f"## {ch['question']}", ch["intro"], ""]
        lines.extend(f"**{title}.** {body}\n" for title, body in ch["principles"])
        lines.extend([f"## {ch['diagram_title']}", ch["diagram_intro"], "\n### Diagram reading order\n"])
        lines.extend(f"{i + 1}. **{title}:** {body}" for i, (title, body) in enumerate(ch["nodes"]))
        lines.extend(["", ch["diagram_note"], f"\n## {ch['case_title']}", ch["case_intro"], ""])
        lines.extend(f"{i + 1}. **{title}:** {body}" for i, (title, body) in enumerate(ch["steps"]))
        lines.extend(
            [
                "",
                ch["case_note"],
                "\n## Failure and correction",
                ch["failure"],
                "",
                ch["correction"],
                "\n## Engineering review\n",
            ]
        )
        lines.extend(f"- {s}" for s in ch["checks"])
        lines.extend(
            ["\n## Further reading\n"] + [f"- [{SOURCES[k][0]}]({SOURCES[k][1]})" for k in ch["sources"]]
        )
        path.write_text("\n\n".join(lines) + "\n")
        paths.append(path)
    (HERE / "MANUSCRIPT.md").write_text(
        "# Agentic AI for DevOps\n\nA visual field guide by Shubham Londhe.\n\n"
        + "\n\n---\n\n".join(p.read_text() for p in paths)
    )


def attach(writer):
    for path in sorted((ASSETS / "fonts").glob("*.txt")):
        writer.add_attachment(path.name, path.read_bytes())
    writer.add_attachment("Lucide-LICENSE.txt", (ASSETS / "icons/LICENSE.txt").read_bytes())


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    b = Book(OUT)
    front(b)
    for ch in CHAPTERS:
        start = b.page_number
        b.opener(ch)
        b.diagram(ch)
        b.example(ch)
        b.review(ch)
        b.chapter_ranges.append((ch, start, b.page_number))
    learning_path(b)
    back(b)
    b.c.save()
    reader = PdfReader(BytesIO(OUT.read_bytes()))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    attach(writer)
    with OUT.open("wb") as f:
        writer.write(f)
    # Standalone exports preserve the book's printed page numbers for reference.
    with ZipFile(OUT.parent / "agentic-ai-for-devops-chapters.zip", "w", ZIP_DEFLATED) as z:
        for ch, start, end in b.chapter_ranges:
            w = PdfWriter()
            for page in reader.pages[start:end]:
                w.add_page(page)
            w.add_metadata({"/Title": ch["title"], "/Author": "Shubham Londhe | Train With Shubham"})
            attach(w)
            buff = BytesIO()
            w.write(buff)
            slug = re.sub(r"[^a-z0-9]+", "-", ch["title"].lower()).strip("-")
            z.writestr(f"{ch['number']:02}-{slug}.pdf", buff.getvalue())
    manuscripts()
    (ROOT / "artifacts/book-layout.json").write_text(
        json.dumps(
            {
                "pages": RECORDS,
                "text_bounds": b.text_bounds,
                "front_pages": FRONT_PAGES,
                "project_chapter": PROJECT_CHAPTER,
            },
            indent=2,
        )
    )
    print(f"Created {b.page_number} pages, {len(CHAPTERS)} chapters and standalone exports.")


if __name__ == "__main__":
    main()
