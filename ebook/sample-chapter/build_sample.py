"""Typeset the editable sample chapter. Requires ReportLab; no network or model calls."""

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "output/pdf/rag-pipelines-for-devops-sample.pdf"
W, H = 540, 720
MARGIN, WIDTH = 54, 432
INK = colors.HexColor("#26212D")
MUTED = colors.HexColor("#6D6675")
PURPLE = colors.HexColor("#7444B3")
GOLD = colors.HexColor("#FFCF80")
PAPER = colors.HexColor("#FCFBF8")
LILAC = colors.HexColor("#F0EBF6")
RULE = colors.HexColor("#DAD3E0")
CODE = colors.HexColor("#1A1722")

for name, filename in (
    ("Body", "SourceSerif4-Regular.ttf"),
    ("BodyBold", "SourceSerif4-Bold.ttf"),
    ("Sans", "Manrope-Regular.ttf"),
    ("SansBold", "Manrope-Bold.ttf"),
    ("Mono", "PlexMono-Regular.ttf"),
):
    pdfmetrics.registerFont(TTFont(name, str(HERE / "assets/fonts" / filename)))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold", italic="Body", boldItalic="BodyBold")
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="SansBold", italic="Sans", boldItalic="SansBold")

BODY = ParagraphStyle(
    "Body",
    fontName="Body",
    fontSize=11,
    leading=15.8,
    textColor=INK,
    spaceAfter=9,
    allowWidows=0,
    allowOrphans=0,
)
H2 = ParagraphStyle(
    "H2",
    fontName="SansBold",
    fontSize=17.8,
    leading=23,
    textColor=PURPLE,
    spaceBefore=20,
    spaceAfter=12,
    keepWithNext=True,
)
H3 = ParagraphStyle(
    "H3",
    fontName="SansBold",
    fontSize=11.8,
    leading=16,
    textColor=INK,
    spaceBefore=13,
    spaceAfter=7,
    keepWithNext=True,
)
SMALL = ParagraphStyle("Small", fontName="Sans", fontSize=8.8, leading=12.2, textColor=MUTED, spaceAfter=6)
CELL = ParagraphStyle("Cell", fontName="Body", fontSize=9.5, leading=13.1, textColor=INK)
HEAD = ParagraphStyle("HeadCell", fontName="SansBold", fontSize=8.5, leading=11.8, textColor=PURPLE)
NOTE = ParagraphStyle("Note", fontName="Sans", fontSize=9.8, leading=14, textColor=INK, spaceAfter=5)
CAPTION = ParagraphStyle(
    "Caption", fontName="Sans", fontSize=8.4, leading=11.5, textColor=MUTED, spaceBefore=5, spaceAfter=12
)


def inline(text):
    text = html.escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: f'<link href="{m[2]}" color="#7444B3"><u>{m[1]}</u></link>',
        text,
    )
    text = re.sub(r"`([^`]+)`", r'<font name="Mono" size="9">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def para(text, style=BODY):
    return Paragraph(inline(text), style)


class CodeBlock(Flowable):
    def __init__(self, text, language=""):
        Flowable.__init__(self)
        self.lines = text.rstrip().splitlines()
        self.language = language or "text"
        self.width = WIDTH
        self.height = 30 + max(len(self.lines), 1) * 12
        for line in self.lines:
            if pdfmetrics.stringWidth(line, "Mono", 8.25) > WIDTH - 34:
                raise ValueError(f"Code listing wider than page: {line}")

    def draw(self):
        c = self.canv
        c.setFillColor(CODE)
        c.roundRect(0, 0, self.width, self.height, 5, stroke=0, fill=1)
        c.setFont("SansBold", 7)
        c.setFillColor(GOLD)
        c.drawString(15, self.height - 14, self.language.upper())
        for i, line in enumerate(self.lines):
            c.setFont("Mono", 8.25)
            c.setFillColor(colors.HexColor("#DCD6E9"))
            if line.lstrip().startswith("#"):
                c.setFillColor(colors.HexColor("#A99CB7"))
            elif line.lstrip().startswith(("def ", "from ", "import ", "for ", "if ")):
                c.setFillColor(colors.HexColor("#E8CAFF"))
            c.drawString(15, self.height - 31 - i * 12, line)


def label(c, text, x, y, font="Sans", size=9, color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def arrow(c, x1, y1, x2, y2):
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.1)
    c.line(x1, y1, x2, y2)
    if abs(y2 - y1) < 0.1:
        direction = 1 if x2 > x1 else -1
        c.line(x2, y2, x2 - 4 * direction, y2 + 3)
        c.line(x2, y2, x2 - 4 * direction, y2 - 3)
    else:
        direction = 1 if y2 > y1 else -1
        c.line(x2, y2, x2 - 3, y2 - 4 * direction)
        c.line(x2, y2, x2 + 3, y2 - 4 * direction)


def box(c, x, y, w, h, number, title, subtitle="", fill=LILAC):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 5, stroke=0, fill=1)
    label(c, number, x + 10, y + h - 17, "SansBold", 8, PURPLE)
    label(c, title, x + 10, y + h - 34, "SansBold", 10)
    if subtitle:
        label(c, subtitle, x + 10, y + 11, "Sans", 7.6, MUTED)


class Diagram(Flowable):
    def __init__(self, kind):
        Flowable.__init__(self)
        self.kind = kind
        self.width = WIDTH
        self.height = {"preparation": 171, "query": 171, "chunks": 135, "boundary": 155, "agent": 151}[kind]

    def draw(self):
        c = self.canv
        if self.kind in ("preparation", "query"):
            if self.kind == "preparation":
                data = [
                    ("01", "Source documents", "Files + source metadata"),
                    ("02", "Extract text", "Keep page / slide / paragraph"),
                    ("03", "Create chunks", "Text stays linked to source"),
                    ("04", "Embed chunks", "Semantic mode only"),
                    ("05", "Build the index", "Text + metadata + vectors"),
                    ("06", "Inspect / version", "Check the prepared artifact"),
                ]
            else:
                data = [
                    ("01", "Question + identity", "Trusted serving context"),
                    ("02", "Filter sources", "Current + allowed"),
                    ("03", "Search and rank", "Question matches chunks"),
                    ("04", "Bound the context", "Copy exact source labels"),
                    ("05", "Generate answer", "Optional live model"),
                    ("06", "Review support", "Claims against excerpts"),
                ]
            bw, bh = 134, 64
            for i, item in enumerate(data):
                row, col = divmod(i, 3)
                x, y = col * 149, 99 - row * 86
                box(c, x, y, bw, bh, *item)
                if col < 2:
                    arrow(c, x + bw + 2, y + 31, x + 147, y + 31)
            arrow(c, 365, 97, 365, 82)
            arrow(c, 365, 82, 67, 82)
            arrow(c, 67, 82, 67, 77)
        elif self.kind == "chunks":
            label(c, "A SOURCE SECTION", 0, 122, "SansBold", 8, MUTED)
            c.setFillColor(colors.HexColor("#DFD8E8"))
            c.roundRect(0, 87, WIDTH, 22, 3, stroke=0, fill=1)
            for i, (x, y) in enumerate(((0, 49), (138, 14))):
                c.setFillColor(LILAC)
                c.roundRect(x, y, 294, 24, 3, stroke=0, fill=1)
                c.setFillColor(GOLD)
                c.rect(138, y, 156, 24, stroke=0, fill=1)
                label(c, f"Chunk {i + 1}", x + 9, y + 8, "SansBold", 8)
            label(c, "Shared text at the boundary", 142, 2, "Sans", 8, MUTED)
        elif self.kind == "boundary":
            c.setFillColor(colors.HexColor("#EFEAE2"))
            c.roundRect(0, 12, 134, 130, 5, stroke=0, fill=1)
            label(c, "INDEXED SOURCES", 11, 124, "SansBold", 8, MUTED)
            for i, (title, color) in enumerate(
                (("Current + allowed", PURPLE), ("Retired", MUTED), ("Restricted for caller", MUTED))
            ):
                label(c, title, 11, 98 - i * 29, "Sans", 8.5, color)
            arrow(c, 139, 78, 165, 78)
            box(c, 171, 46, 110, 64, "FILTER", "Eligible only", "Before ranking/context")
            arrow(c, 286, 78, 310, 78)
            box(c, 316, 46, 116, 64, "RETRIEVE", "Model context", "Allowed evidence")
        elif self.kind == "agent":
            box(c, 0, 64, 127, 64, "DECIDE", "Agent application", "State + limits + identity")
            box(c, 154, 64, 125, 64, "REQUEST", "Search tool", "Validated arguments")
            box(c, 307, 64, 125, 64, "OBSERVE", "Cited excerpts", "No deployment action")
            arrow(c, 130, 96, 150, 96)
            arrow(c, 282, 96, 303, 96)
            arrow(c, 369, 60, 369, 30)
            arrow(c, 369, 30, 63, 30)
            arrow(c, 63, 30, 63, 60)
            label(c, "Return observations to the controlled loop", 105, 9, "Sans", 8, MUTED)


CAPTIONS = {
    "preparation": "Figure 1. Prepare a searchable artifact when source knowledge changes. Embedding is optional for the keyword path.",
    "query": "Figure 2. Retrieve within the caller's allowed context, then inspect the answer's support.",
    "chunks": "Figure 3. Overlap repeats text near a boundary. Illustration only; lengths are not to scale.",
    "boundary": "Figure 4. Retired or unauthorized chunks must not enter the model's evidence context.",
    "agent": "Figure 5. A retrieval tool can participate in an agent loop. This chapter's lab uses a fixed RAG workflow.",
}


def table(lines):
    rows = [[v.strip() for v in line.strip().strip("|").split("|")] for line in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", s) for s in r)]
    n = len(rows[0])
    widths = [126, 130, 176] if n == 3 else [110, 322]
    if rows[0][0] == "Source":
        widths = [134, 50, 248]
    if rows[0][0] == "Case":
        widths = [116, 172, 144]
    data = [[para(value, HEAD if i == 0 else CELL) for value in row] for i, row in enumerate(rows)]
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), LILAC),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, PURPLE),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, RULE),
                ("NOSPLIT", (0, 0), (-1, min(2, len(data) - 1))),
                ("NOSPLIT", (0, max(1, len(data) - 2)), (-1, -1)),
            ]
        )
    )
    return result


def quote(lines):
    title = lines[0].lstrip("> ").strip("*")
    body = " ".join(line.lstrip("> ") for line in lines[1:])
    title_style = ParagraphStyle("NoteHead", parent=NOTE, fontName="SansBold", textColor=PURPLE, spaceAfter=5)
    result = Table([[[para(title, title_style), para(body, NOTE)]]], colWidths=[WIDTH])
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LILAC),
                ("LINEBEFORE", (0, 0), (0, -1), 3, PURPLE),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 13),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return result


def draw_page(c, doc):
    c.saveState()
    c.setCreator("Train With Shubham | Sample chapter typesetter")
    if doc.page == 1:
        c.setFillColor(colors.black)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.drawImage(
            str(HERE / "assets/tws-logo.png"), 40, 526, 130, 130, preserveAspectRatio=True, mask="auto"
        )
        label(c, "TRAIN WITH SHUBHAM", 54, 679, "SansBold", 9, GOLD)
        label(c, "CHAPTER 05", 379, 594, "SansBold", 10, GOLD)
        c.setStrokeColor(PURPLE)
        c.setLineWidth(3)
        c.line(54, 500, 486, 500)
        label(c, "Agentic AI", 54, 463, "Sans", 18, colors.HexColor("#C6BDCF"))
        label(c, "for DevOps", 54, 437, "Sans", 18, colors.HexColor("#C6BDCF"))
        label(c, "RAG pipelines", 51, 359, "SansBold", 45, colors.white)
        label(c, "for DevOps", 51, 300, "SansBold", 45, colors.white)
        label(c, "From deployment documents", 54, 240, "Body", 19, GOLD)
        label(c, "to answers you can inspect.", 54, 213, "Body", 19, GOLD)
        c.setFillColor(PURPLE)
        c.rect(54, 139, 52, 4, fill=1, stroke=0)
        label(c, "SHUBHAM LONDHE", 54, 106, "SansBold", 11, colors.white)
        label(
            c,
            "Sample edition | Technically reviewed 13 November 2026",
            54,
            80,
            "Sans",
            8.7,
            colors.HexColor("#C6BDCF"),
        )
        label(c, "READ  /  RUN  /  REVIEW", 54, 43, "Mono", 8, GOLD)
    else:
        c.setFillColor(PAPER)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        label(c, "AGENTIC AI FOR DEVOPS", 54, 680, "SansBold", 7.7, PURPLE)
        label(c, "RAG PIPELINES", 371, 680, "Sans", 7.7, MUTED)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(54, 669, 486, 669)
        c.line(54, 46, 486, 46)
        label(c, "TRAIN WITH SHUBHAM", 54, 31, "SansBold", 7.1, MUTED)
        label(c, "SAMPLE CHAPTER", 230, 31, "Sans", 7.1, MUTED)
        label(c, "CONTENTS" if doc.page == 2 else f"{doc.page - 2:02}", 452, 31, "Mono", 8, PURPLE)
    c.restoreState()


class Book(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(
            str(path),
            pagesize=(W, H),
            title="RAG Pipelines for DevOps | Agentic AI for DevOps",
            author="Shubham Londhe | Train With Shubham",
            subject="A fact-checked practical sample chapter with a standalone document RAG lab",
            pageCompression=1,
        )
        self.addPageTemplates(
            PageTemplate(
                id="book",
                frames=[
                    Frame(
                        MARGIN, 58, WIDTH, 592, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
                    )
                ],
                onPage=draw_page,
            )
        )

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "H2":
            title = flowable.getPlainText()
            key = "section-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=0)
            self.notify("TOCEntry", (0, title, self.page - 2, key))


def build():
    text = (HERE / "chapter.md").read_text()
    if any(dash in text for dash in ("\u2011", "\u2013", "\u2014")):
        raise ValueError("Use ASCII hyphens in the print manuscript")
    story = [PageBreak(), para("Inside this chapter", H2)]
    # The contents title is excluded from its own TOC by giving it a different style.
    story[-1].style = ParagraphStyle("ContentsHeading", parent=H2, spaceBefore=0)
    story += [
        para(
            "Build a small deployment-knowledge pipeline, inspect its evidence and learn where operational judgment is still required."
        ),
        Spacer(1, 9),
    ]
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOC",
            fontName="Sans",
            fontSize=9.5,
            leading=14.5,
            textColor=INK,
            spaceBefore=1,
            leftIndent=0,
            firstLineIndent=0,
            rightIndent=24,
        )
    ]
    story += [toc, PageBreak()]
    lines = text.splitlines()
    i = next(i for i, line in enumerate(lines) if line.startswith("## "))
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("## "):
            story.append(para(line[3:], H2))
            i += 1
        elif line.startswith("### "):
            story.append(para(line[4:], H3))
            i += 1
        elif line.startswith("```"):
            language = line[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            story += [Spacer(1, 3), CodeBlock("\n".join(code), language), Spacer(1, 13)]
            i += 1
        elif line.startswith("<!-- diagram:"):
            kind = re.search(r"diagram: (\w+)", line)[1]
            story.append(KeepTogether([Spacer(1, 7), Diagram(kind), para(CAPTIONS[kind], CAPTION)]))
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            before = Spacer(1, 4)
            before.keepWithNext = True
            story += [before, table(rows), Spacer(1, 13)]
        elif line.startswith(">"):
            block = []
            while i < len(lines) and lines[i].startswith(">"):
                block.append(lines[i])
                i += 1
            story += [Spacer(1, 4), quote(block), Spacer(1, 13)]
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(ListItem(para(lines[i][2:]), leftIndent=12))
                i += 1
            story += [
                ListFlowable(
                    items,
                    bulletType="bullet",
                    start="circle",
                    leftIndent=14,
                    bulletFontName="Sans",
                    bulletFontSize=6,
                    bulletColor=PURPLE,
                ),
                Spacer(1, 6),
            ]
        else:
            block = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].startswith(("#", "```", "|", ">", "<!--", "- "))
            ):
                block.append(lines[i])
                i += 1
            story.append(para(" ".join(block)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Book(OUT).multiBuild(story)
    print(OUT)


if __name__ == "__main__":
    build()
