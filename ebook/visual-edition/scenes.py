"""Original vector scenes. Everyday analogies are illustrations, not system diagrams."""

from reportlab.lib.colors import toColor


def draw_scene(b, kind, x=48, y=247):
    c = b.c
    c.saveState()
    c.translate(x, y)
    purple, gold, ink = b.purple, b.gold, b.ink
    teal = "#3C8B82"

    def box(x, y, w, h, fill="white", radius=9, stroke=None):
        c.setFillColor(toColor(fill))
        c.setStrokeColor(toColor(stroke or fill))
        c.setLineWidth(2)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=int(bool(stroke)))

    def circle(x, y, r, fill, stroke=None):
        c.setFillColor(toColor(fill))
        c.setStrokeColor(toColor(stroke or fill))
        c.setLineWidth(2.5)
        c.circle(x, y, r, fill=1, stroke=int(bool(stroke)))

    def line(x1, y1, x2, y2, fill=ink, width=3):
        c.setStrokeColor(toColor(fill))
        c.setLineWidth(width)
        c.setLineCap(1)
        c.line(x1, y1, x2, y2)

    def poly(points, fill, stroke=None):
        c.setFillColor(toColor(fill))
        c.setStrokeColor(toColor(stroke or fill))
        c.setLineWidth(2)
        p = c.beginPath()
        p.moveTo(*points[0])
        for point in points[1:]:
            p.lineTo(*point)
        p.close()
        c.drawPath(p, fill=1, stroke=int(bool(stroke)))

    def glyph(name, x, y, size=30, fill=purple):
        b.icon(name, x, y, size, fill)

    def paper(x, y, w=93, h=119, tint="white"):
        box(x + 5, y - 5, w, h, "#D8CDE4")
        box(x, y, w, h, tint, stroke=ink)
        rows = 2 if h < 80 else 3 if h < 110 else 4
        for i, length in enumerate([0.61, 0.78, 0.68, 0.47][:rows]):
            yy = y + h - 24 - i * (h - 45) / (rows - 1)
            line(x + 13, yy, x + w * length, yy, "#B3A1C3", 3)
        box(x + 13, y + 10, min(25, w - 26), 6, gold, 3)

    def person(x, y, shirt=purple):
        circle(x + 25, y + 82, 21, "#E8B780")
        poly([(x + 3, y + 87), (x + 4, y + 103), (x + 24, y + 110), (x + 47, y + 102), (x + 48, y + 89)], ink)
        box(x, y, 52, 59, shirt, 17)
        line(x + 14, y, x + 10, y - 28, ink, 7)
        line(x + 38, y, x + 42, y - 28, ink, 7)
        circle(x + 18, y + 83, 2, ink)
        circle(x + 32, y + 83, 2, ink)
        line(x + 21, y + 72, x + 30, y + 72, ink, 1.4)

    def laptop(x, y, w=154):
        box(x, y + 16, w, 105, ink, 8)
        box(x + 8, y + 24, w - 16, 88, "#E9E2F1", 3)
        glyph("brain-circuit", x + w / 2 - 20, y + 45, 40, purple)
        poly([(x - 14, y + 16), (x + w + 14, y + 16), (x + w + 25, y), (x - 24, y)], "#7D618F", ink)
        line(x + w * 0.37, y + 8, x + w * 0.63, y + 8, gold, 3)

    def book(x, y, w=28, h=100, fill=purple):
        box(x, y, w, h, fill, 3)
        line(x + 5, y + 7, x + 5, y + h - 6, "#FFFFFF", 1)
        line(x + 10, y + h - 20, x + w - 7, y + h - 20, gold, 2)

    def shelf():
        box(84, 31, 327, 191, ink, 10)
        box(95, 42, 305, 170, "#F5EBD8", 5)
        for row in [58, 139]:
            for i, (w, h) in enumerate(
                [(27, 60), (32, 53), (24, 65), (38, 55), (26, 64), (30, 58), (25, 51)]
            ):
                book(107 + i * 39, row, w, h, [purple, teal, "#C28A46", purple, "#A98ABC"][i % 5])
            line(99, row - 5, 394, row - 5, ink, 5)

    def parcel(x=173, y=61):
        poly([(x, y), (x + 143, y), (x + 143, y + 115), (x, y + 115)], gold, ink)
        poly([(x + 143, y), (x + 188, y + 32), (x + 188, y + 143), (x + 143, y + 115)], "#BE945A", ink)
        poly([(x, y + 115), (x + 48, y + 146), (x + 188, y + 143), (x + 143, y + 115)], "#FFE4AC", ink)
        box(x + 57, y + 5, 24, 109, "#9569C9", 0)
        paper(x + 10, y + 34, 43, 58)

    # Pale field with a few drawn marks keeps the scene distinct from the diagram page.
    box(0, 0, 504, 271, "#F0EAF7", 18)
    circle(372, 160, 100, "#E5D9EE")
    circle(100, 75, 43, "#F9E8C8")
    for px, py in [(28, 235), (43, 235), (28, 220), (469, 35), (454, 35), (469, 50)]:
        circle(px, py, 2, "#BBA5CF")
    line(50, 35, 450, 35, "#C5B2D7", 2)

    if kind in ("helper", "workbench"):
        person(82, 74)
        if kind == "helper":
            laptop(227, 76)
        else:
            box(239, 91, 157, 49, gold, 5, ink)
            line(252, 105, 381, 105, "#BF914E", 2)
            line(252, 122, 366, 122, "#BF914E", 2)
            box(251, 149, 142, 16, "white", 2, ink)
            for xx in range(259, 387, 12):
                line(xx, 151, xx, 157, ink, 1)
        line(63, 72, 421, 72, ink, 8)
        line(92, 70, 82, 36, ink, 6)
        line(396, 70, 407, 36, ink, 6)
        paper(176, 149, 66, 80)
        glyph("search" if kind == "helper" else "list-checks", 322, 197, 34, teal)
    elif kind == "toolbox":
        box(115, 53, 269, 113, purple, 12, ink)
        box(204, 170, 91, 22, ink, 8)
        box(215, 177, 69, 13, "#F0EAF7", 4)
        box(115, 150, 269, 28, "#A17ACD", 8, ink)
        box(233, 131, 33, 40, gold, 5, ink)
        glyph("list-checks", 148, 77, 51, gold)
        line(348, 183, 367, 228, teal, 12)
        circle(370, 234, 12, teal)
        line(147, 183, 131, 223, ink, 7)
        box(115, 222, 33, 14, gold, 4)
    elif kind in ("kitchen", "order", "restaurant"):
        person(90, 77, teal)
        if kind == "kitchen":
            circle(107, 190, 13, "white", ink)
            circle(126, 197, 16, "white", ink)
            circle(145, 190, 13, "white", ink)
            box(106, 176, 40, 13, "white", 3, ink)
        box(59, 60, 366, 19, purple, 5)
        box(92, 37, 18, 23, ink, 2)
        box(379, 37, 18, 23, ink, 2)
        box(267, 80, 84, 71, "white", 8, ink)
        c.setStrokeColor(toColor(ink))
        c.setLineWidth(4)
        c.circle(355, 116, 20, stroke=1, fill=0)
        for sx in (281, 310, 335):
            c.setStrokeColor(toColor("#A48BB8"))
            c.setLineWidth(2)
            path = c.beginPath()
            path.moveTo(sx, 167)
            path.curveTo(sx - 13, 177, sx - 10, 184, sx + 1, 193)
            c.drawPath(path)
        paper(184, 151, 65, 81)
        glyph("circle-check", 364, 188, 32, teal)
    elif kind == "packing":
        box(110, 51, 286, 134, purple, 17, ink)
        box(214, 196, 80, 18, ink, 6)
        line(136, 74, 136, 159, gold, 8)
        line(369, 74, 369, 159, gold, 8)
        paper(174, 138, 85, 103)
        paper(263, 127, 77, 102, "#FFF5DD")
        glyph("search", 301, 65, 36, gold)
    elif kind == "detective":
        box(101, 62, 307, 163, "#DBC3A2", 6, ink)
        paper(120, 94, 67, 89)
        paper(286, 114, 77, 93)
        line(181, 128, 290, 159, purple, 3)
        line(183, 162, 289, 123, purple, 3)
        circle(178, 129, 4, gold)
        circle(293, 159, 4, gold)
        glyph("search", 221, 58, 73, purple)
    elif kind == "plug":
        box(282, 64, 111, 148, "white", 18, ink)
        circle(319, 157, 7, ink)
        circle(356, 157, 7, ink)
        box(327, 104, 20, 12, ink, 3)
        box(104, 93, 100, 71, purple, 15, ink)
        line(204, 115, 240, 115, gold, 7)
        line(204, 145, 240, 145, gold, 7)
        line(68, 127, 103, 127, ink, 7)
        line(57, 74, 57, 126, ink, 7)
        line(57, 74, 109, 74, ink, 7)
        glyph("git-branch", 129, 112, 34, gold)
    elif kind in ("map", "journey"):
        poly(
            [(83, 52), (186, 73), (287, 51), (416, 81), (416, 223), (291, 197), (184, 224), (83, 198)],
            "#FFFBF0",
            ink,
        )
        for xx in (186, 287):
            line(xx, 74, xx, 199, "#C8B1D7", 2)
        points = [(112, 108), (187, 161), (259, 108), (332, 169), (388, 137)]
        for p1, p2 in zip(points, points[1:]):
            line(*p1, *p2, purple, 6)
        for i, (xx, yy) in enumerate(points):
            circle(xx, yy, 9, gold if i == 4 else "white", purple)
        if kind == "journey":
            glyph("clock", 344, 52, 48, teal)
    elif kind in ("library", "books"):
        shelf()
        if kind == "library":
            person(350, 53, teal)
            paper(227, 52, 95, 118)
            glyph("search", 247, 98, 45, purple)
        else:
            paper(198, 51, 119, 151)
            box(206, 117, 103, 22, "#FFE3A6", 3)
            box(316, 152, 18, 27, teal, 2)
            box(316, 113, 18, 26, purple, 2)
    elif kind in ("badge", "gate"):
        box(309, 36, 112, 186, ink, 7)
        box(320, 42, 90, 169, "#6F4A99", 3)
        circle(393, 125, 5, gold)
        person(102, 71, teal)
        box(186, 104, 73, 95, "white", 8, ink)
        line(221, 198, 215, 220, purple, 3)
        circle(222, 170, 13, "#D7BD93")
        box(202, 135, 39, 16, purple, 5)
        glyph("circle-check" if kind == "badge" else "shield-check", 268, 162, 37, teal)
    elif kind in ("parcel", "ticket"):
        parcel()
        paper(97, 109, 81, 110)
        glyph("circle-check", 111, 143, 45, teal)
        if kind == "ticket":
            glyph("refresh-cw", 337, 162, 49, purple)
            line(99, 222, 164, 222, teal, 4)
    elif kind == "bicycle":
        for xx in (135, 365):
            circle(xx, 82, 57, "white", ink)
            circle(xx, 82, 43, "#F0EAF7")
        for p1, p2 in [
            ((135, 82), (218, 82)),
            ((218, 82), (178, 165)),
            ((178, 165), (135, 82)),
            ((178, 165), (320, 165)),
            ((320, 165), (218, 82)),
            ((320, 165), (365, 82)),
        ]:
            line(*p1, *p2, purple, 7)
        line(178, 165, 169, 189, ink, 5)
        line(148, 192, 191, 192, ink, 7)
        line(320, 165, 307, 204, ink, 5)
        line(307, 204, 337, 216, ink, 5)
        circle(218, 82, 12, gold, ink)
        line(218, 82, 244, 63, ink, 4)
        circle(249, 232, 19, "#E8B780")
        line(239, 211, 206, 177, teal, 20)
        line(231, 205, 304, 202, "#E8B780", 7)
        line(206, 177, 251, 138, teal, 12)
        line(251, 138, 221, 88, "#E8B780", 8)
        line(216, 85, 238, 85, ink, 7)
    elif kind == "fridge":
        box(177, 39, 152, 195, "white", 17, ink)
        line(178, 161, 328, 161, ink, 3)
        line(308, 179, 308, 204, purple, 5)
        line(308, 98, 308, 134, purple, 5)
        box(197, 91, 91, 49, "#C7E4DA", 8, ink)
        box(193, 137, 100, 10, teal, 3)
        box(213, 105, 57, 22, "#FFF3D9", 3)
        glyph("clock", 353, 147, 51, purple)
    elif kind == "exam":
        paper(142, 47, 176, 183)
        for i in range(3):
            glyph("circle-check", 267, 159 - i * 43, 27, teal)
        line(332, 59, 382, 202, purple, 11)
        poly([(328, 46), (328, 68), (340, 65)], gold, ink)
        circle(382, 205, 7, gold)
    elif kind == "assembly":
        box(65, 62, 375, 37, ink, 15)
        for xx in range(87, 431, 32):
            circle(xx, 80, 8, "#B3A2C3")
        for xx, fill in [(90, gold), (222, "#BFA1DE"), (352, "#B4D6C9")]:
            box(xx, 100, 64, 69, fill, 8, ink)
            glyph("circle-check", xx + 16, 120, 31, teal)
        line(255, 179, 255, 235, purple, 9)
        line(255, 234, 352, 234, purple, 9)
        glyph("shield-check", 377, 183, 43, purple)
    elif kind == "shop":
        box(105, 50, 295, 135, "#FFF6DF", 3, ink)
        for i in range(8):
            box(99 + i * 38, 176, 38, 49, purple if i % 2 == 0 else gold, 3)
        box(226, 52, 70, 99, purple, 3, ink)
        box(124, 86, 79, 63, "white", 3, ink)
        glyph("activity", 138, 101, 48, teal)
        person(340, 62, teal)
    elif kind == "building":
        for xoff, fill in [(87, "#D9C7EB"), (287, "#B9DBD0")]:
            box(xoff, 44, 134, 178, fill, 4, ink)
            for dx in (18, 77):
                for dy in (86, 133):
                    box(xoff + dx, dy, 37, 27, "white", 3)
            box(xoff + 50, 46, 39, 42, purple, 3, ink)
        glyph("git-branch", 129, 173, 37, purple)
        glyph("brain-circuit", 329, 173, 37, teal)
    else:
        raise ValueError(kind)
    c.restoreState()
