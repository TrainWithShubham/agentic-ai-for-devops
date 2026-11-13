"""Vector explanations. All geometry is original; outline symbols are Lucide."""


def draw(b, ch):
    nodes = ch["nodes"]
    kind = ch["kind"]
    p, t, r, a, ic, node = b.prose, b.text, b.rect, b.arrow, b.icon, b.node
    if kind in ("mistakes", "models", "claude-habits"):
        names = {
            "mistakes": ["git-branch", "file-text", "triangle-alert", "list-checks"],
            "models": ["file-text", "brain-circuit", "layers", "database"],
            "claude-habits": ["file-text", "git-branch", "lock-keyhole", "circle-check"],
        }[kind]
        for (x, y), (title, body), name in zip(
            [(48, 427), (312, 427), (48, 222), (312, 222)], nodes, names, strict=True
        ):
            node(x, y, 240, 152, title, body, name)
        if kind == "claude-habits":
            b.center("SMALL SCOPE / REAL EVIDENCE", 300, 404, 9, b.purple)
    elif kind == "prompt-pattern":
        for i, (title, body) in enumerate(nodes):
            y = 480 - i * 84
            node(
                48,
                y,
                504,
                75,
                title,
                body,
                ["brain-circuit", "files", "shield-check", "list-checks"][i],
                compact=True,
            )
            if i < 3:
                a(300, y - 1, 300, y - 10)
    elif kind == "decision":
        # Branching decision tree; the labels are examples, not model recommendations.
        r(48, 318, 142, 180, b.dark)
        ic("git-branch", 96, 425, 43, b.gold)
        p("How much choice does the task need?", 65, 403, 110, 16, "#FFFFFF", font="Serif")
        for i, (title, body) in enumerate(nodes):
            y = 469 - i * 104
            a(198, 410, 238, y + 37)
            node(247, y, 305, 87, title, body, ["clock", "list-checks", "brain-circuit"][i], compact=True)
            t(["SCRIPT", "WORKFLOW", "AGENT"][i], 263, y + 92, 8, "Mono", b.purple)
    elif kind == "stack":
        for i, (title, body) in enumerate(nodes):
            y = 489 - i * 79
            x = 48 + i * 12
            r(x, y, 504 - i * 12, 67, b.pale if i != 3 else "#F5EDDD")
            ic(["file-text", "user-round", "files", "list-checks"][i], x + 13, y + 24, 24)
            t(title, x + 51, y + 43, 12, "Bold")
            p(body, x + 51, y + 31, 424 - i * 12, 10.7)
        for i, (title, body) in enumerate(ch["memory_tiles"]):
            x = 48 + i * 172
            r(x, 171, 160, 61, b.pale)
            t(title, x + 12, 211, 11, "Bold", b.purple)
            p(body, x + 12, 198, 136, 10.5, max_height=22)
        b.record_diagram(ch["memory_tiles"])
    elif kind == "sequence":
        positions = [111, 300, 489]
        for x, title, name in zip(
            positions,
            ["Model", "Application", "Tool"],
            ["brain-circuit", "shield-check", "list-checks"],
            strict=True,
        ):
            ic(name, x - 17, 529, 34)
            b.center(title, x, 510, 12)
            b.line(x, 495, x, 220, "#D8CDE2", dashed=True)
        for y, x1, x2, label in [
            (464, 111, 300, "request"),
            (384, 300, 489, "validated call"),
            (304, 489, 300, "observed result"),
            (224, 300, 111, "context update"),
        ]:
            a(x1, y, x2, y)
            b.center(label, (x1 + x2) / 2, y + 12, 10, b.muted)
        b.record_diagram(nodes)
    elif kind == "cycle":
        for (x, y), (title, body), name in zip(
            [(48, 435), (328, 435), (328, 239), (48, 239)],
            nodes,
            ["brain-circuit", "shield-check", "search", "circle-check"],
            strict=True,
        ):
            node(x, y, 224, 133, title, body, name)
        a(279, 501, 320, 501)
        a(440, 426, 440, 381)
        a(320, 305, 280, 305)
        a(160, 381, 160, 427)
        b.center("Budget checked at every turn", 300, 403, 10, b.purple)
    elif kind == "mcp":
        r(48, 345, 260, 229, b.pale)
        t("HOST APPLICATION", 65, 548, 10, "Mono", b.purple)
        ic("brain-circuit", 68, 492, 28)
        t("Model + policy", 112, 503, 13, "Bold")
        node(68, 366, 220, 104, nodes[1][0], nodes[1][1], "git-branch", compact=True)
        node(363, 393, 189, 149, nodes[2][0], nodes[2][1], "list-checks")
        a(315, 431, 355, 431)
        b.center("MCP", 335, 451, 9, b.purple)
        node(363, 219, 189, 122, nodes[3][0], nodes[3][1], "database")
        a(457, 383, 457, 350)
        p(nodes[0][1], 65, 319, 243, 12)
    elif kind == "graph":
        node(48, 430, 224, 138, *nodes[0], "brain-circuit")
        node(328, 430, 224, 138, *nodes[1], "list-checks")
        node(328, 223, 224, 138, *nodes[2], "user-round")
        node(48, 223, 224, 138, *nodes[3], "circle-check")
        a(279, 519, 320, 519)
        a(328, 455, 280, 455)
        a(441, 420, 441, 371)
        a(321, 291, 280, 291)
        a(161, 421, 161, 370)
        b.center("tool request", 300, 536, 8.7, b.purple)
        b.center("result", 300, 440, 8.7, b.muted)
        b.center("write proposal", 442, 393, 8.2, b.purple)
        b.center("answer", 185, 395, 8.5, b.muted)
        b.line(555, 260, 566, 260, b.purple)
        b.line(566, 260, 566, 352, b.purple)
        a(566, 352, 553, 352)
        b.center("RESUME = RESTART THE REVIEW NODE", 300, 181, 9, b.purple)
    elif kind == "rag":
        t("PREPARATION", 48, 568, 9, "Mono", b.purple)
        node(48, 443, 224, 104, *nodes[0], "files")
        node(328, 443, 224, 104, *nodes[1], "database")
        a(280, 495, 320, 495)
        t("QUESTION TIME", 48, 413, 9, "Mono", b.purple)
        node(48, 318, 504, 79, *nodes[2], "search", compact=True)
        a(440, 434, 440, 405)
        for i, (title, body) in enumerate(ch["rag_outcomes"]):
            x = 48 + i * 172
            a(300, 310, x + 80, 293)
            r(x, 177, 160, 107, ["#E8F1EB", b.pale, "#F7E9EB"][i])
            ic(["circle-check", "files", "triangle-alert"][i], x + 12, 253, 20)
            t(title, x + 39, 258, 10.6, "Bold")
            p(body, x + 12, 239, 136, 11.4, max_height=53)
        b.record_diagram(ch["rag_outcomes"])
    elif kind == "chunks":
        r(48, 434, 504, 143, b.dark)
        t("SOURCE / POLICY / SECTION 4", 67, 550, 9, "Mono", b.gold)
        p(nodes[0][1], 67, 529, 465, 18, "#FFFFFF", font="Serif")
        for i in range(11):
            r(67 + i * 42, 445, 35, 5, b.gold if i in (4, 5) else "#655573", radius=1)
        node(48, 234, 240, 151, *nodes[1], "circle-x", fill="#F7E9EB")
        node(312, 234, 240, 151, *nodes[2], "circle-check", fill="#E8F1EB")
        a(169, 425, 169, 395)
        a(432, 425, 432, 395)
        p(nodes[3][1], 48, 202, 504, 11)
    elif kind == "identity":
        for i, (title, body) in enumerate(nodes):
            y = 480 - i * 90
            node(
                48,
                y,
                504,
                76,
                title,
                body,
                ["user-round", "shield-check", "brain-circuit", "lock-keyhole"][i],
                compact=True,
            )
            if i < 3:
                a(300, y - 2, 300, y - 12)
        t("USER IDENTITY  /  APP POLICY  /  SCOPED TOOL CREDENTIAL", 48, 173, 8.7, "Mono", b.purple)
    elif kind == "approval":
        for i, (title, body) in enumerate(nodes):
            y = 476 - i * 87
            b.circle(75, y + 28, 17, b.purple)
            b.center(str(i + 1), 75, y + 23, 12, "#FFFFFF")
            t(title, 112, y + 47, 14, "Bold")
            p(body, 112, y + 31, 420, 11)
            if i < 3:
                a(75, y + 6, 75, y - 26)
        t("APPROVED ONLY", 112, 281, 8.5, "Mono", b.green)
        r(48, 162, 504, 33, "#F7E9EB", radius=7)
        b.center("Rejected = stop. Changed or expired = re-review.", 300, 173, 9, b.red)
    elif kind == "gates":
        b.line(76, 382, 524, 382, b.purple)
        for i, (title, body) in enumerate(nodes):
            x = 48 + i * 130
            r(x + 18, 344, 78, 78, b.dark, radius=16)
            ic(["files", "list-checks", "shield-check", "file-text"][i], x + 41, 369, 30, b.gold)
            p(title, x, 321, 114, 12, b.ink, max_height=42)
            p(body, x, 276, 114, 10.5, max_height=100)
        p("A REQUEST MUST SATISFY EVERY RELEVANT BOUNDARY", 48, 528, 504, 10, b.purple, font="Mono")
    elif kind == "harness":
        for (x, y), (title, body), name in zip(
            [(48, 451), (328, 451), (48, 222), (328, 222)],
            nodes,
            ["files", "list-checks", "clock", "activity"],
            strict=True,
        ):
            node(x, y, 224, 123, title, body, name)
        for x, y in [(160, 445), (440, 445), (160, 353), (440, 353)]:
            b.line(300, 397, x, y, "#BEACD0")
        b.circle(300, 397, 41, b.dark)
        ic("brain-circuit", 281, 378, 38, b.gold)
    elif kind == "cache":
        node(48, 451, 224, 124, *nodes[0], "user-round")
        node(328, 451, 224, 124, *nodes[1], "filter")
        a(280, 513, 320, 513)
        node(48, 237, 224, 143, *nodes[2], "circle-check", fill="#E8F1EB")
        node(328, 237, 224, 143, *nodes[3], "refresh-cw")
        a(440, 441, 440, 391)
        a(329, 442, 161, 391)
        t("MATCH", 192, 411, 9, "Mono", b.green)
        t("MISS", 454, 411, 9, "Mono", b.purple)
    elif kind == "trace":
        t("ONE TASK / CONNECTED SPANS", 48, 557, 10, "Mono", b.purple)
        for x in range(204, 553, 58):
            b.line(x, 198, x, 532, "#E6E0EB", dashed=True)
        for i, (title, body) in enumerate(nodes):
            y = 459 - i * 77
            x = [204, 220, 310, 435][i]
            width = [348, 75, 115, 117][i]
            t(title, 48, y + 23, 11, "Bold")
            r(x, y + 13, width, 24, b.purple if i % 2 == 0 else b.dark, radius=4)
            p(body, 204, y + 4, 348, 9.7, max_height=40)
        b.center("TIME / illustrative, not measured", 366, 181, 9, b.muted)
    elif kind == "eval":
        for (x, y), (title, body), name in zip(
            [(48, 427), (312, 427), (48, 222), (312, 222)],
            nodes,
            ["list-checks", "git-branch", "file-text", "activity"],
            strict=True,
        ):
            node(x, y, 240, 152, title, body, name)
        b.circle(300, 401, 26, b.dark)
        ic("circle-check", 286, 387, 28, b.gold)
    elif kind == "ops-map":
        for (x, y), (title, body), name in zip(
            [(48, 427), (312, 427), (48, 240), (312, 240)],
            nodes,
            ["activity", "database", "files", "shield-check"],
            strict=True,
        ):
            node(x, y, 240, 152, title, body, name)
        r(48, 170, 504, 48, "#F5EDDD", radius=9)
        ic("layers", 61, 182, 24)
        p(
            "Platform engineering supplies shared identity, tools and deployment paths for people and agents.",
            102,
            207,
            432,
            10.5,
            max_height=32,
        )
    elif kind == "release":
        for i, (title, body) in enumerate(nodes):
            y = 469 - i * 84
            node(
                48,
                y,
                504,
                72,
                title,
                body,
                ["layers", "shield-check", "git-branch", "activity"][i],
                compact=True,
            )
            if i < 3:
                a(300, y - 1, 300, y - 11)
        b.line(561, 247, 570, 247, b.purple)
        b.line(570, 247, 570, 547, b.purple)
        a(570, 547, 555, 547)
        b.center("VERSIONED COMBINATION", 300, 182, 9, b.purple)
    elif kind == "case-map":
        node(48, 439, 224, 137, *nodes[0], "user-round")
        node(328, 439, 224, 137, *nodes[1], "git-branch")
        node(328, 235, 224, 137, *nodes[2], "files")
        node(48, 235, 224, 137, *nodes[3], "shield-check")
        a(280, 508, 320, 508)
        a(441, 430, 441, 383)
        a(320, 303, 280, 303)
        a(160, 381, 160, 430)
        b.center("FICTIONAL SIMULATOR", 300, 404, 8.5, b.purple)
    elif kind == "temporal":
        t("DURABLE PROCESS", 48, 568, 9, "Mono", b.purple)
        for i, (title, body) in enumerate(nodes):
            y = 465 - i * 84
            b.circle(73, y + 27, 16, b.purple)
            ic(["search", "clock", "shield-check", "circle-check"][i], 63, y + 17, 20, "#FFFFFF")
            t(title, 111, y + 43, 13, "Bold")
            p(body, 111, y + 27, 418, 11)
            if i < 3:
                b.line(73, y + 9, 73, y - 39, b.purple)
        r(337, 407, 215, 32, "#F5EDDD", radius=6)
        b.center("worker restart / history retained", 444, 418, 8.7, "#624A28")
        t("WORKFLOW ORCHESTRATES; ACTIVITIES DO EXTERNAL WORK", 48, 174, 8.7, "Mono", b.purple)
    elif kind == "cloud":
        node(48, 389, 240, 178, *nodes[0], "git-branch", fill=b.pale)
        node(312, 389, 240, 178, *nodes[1], "brain-circuit", fill="#F5EDDD")
        b.center("AgentCore Runtime", 168, 412, 12, b.purple)
        b.center("Managed Harness", 432, 412, 12, "#624A28")
        node(48, 196, 240, 145, *nodes[2], "lock-keyhole")
        node(312, 196, 240, 145, *nodes[3], "lock-keyhole")
        a(168, 381, 168, 366)
        a(432, 381, 432, 366)
        b.line(168, 366, 432, 366, b.purple)
        b.center("SHARED CONCERNS", 300, 350, 8, b.purple)
    else:
        raise ValueError(kind)
