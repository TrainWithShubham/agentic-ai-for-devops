"""Check local Markdown links and the two timed teaching schedules."""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    files = [
        p
        for p in ROOT.rglob("*.md")
        if not any(
            part.startswith(".") or part in ("artifacts", "node_modules")
            for part in p.relative_to(ROOT).parts
        )
    ]
    for path in files:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            target = target.strip("<>").split("#")[0]
            if not target or "://" in target or target.startswith(("mailto:", "plugin:")):
                continue
            resolved = path.parent / unquote(target)
            if not resolved.exists():
                errors.append(str(path.relative_to(ROOT)) + ": " + target)
    text = (ROOT / "CURRICULUM.md").read_text()
    for section in (4, 5):
        body = text.split(f"## {section}. ", 1)[1].split("\n## ", 1)[0]
        blocks = re.findall(r"^\| (\d\d:\d\d) to (\d\d:\d\d) \| (\d+) \|", body, re.M)
        last = 0
        for start, end, minutes in blocks:

            def convert(time):
                return int(time[:2]) * 60 + int(time[3:])

            if convert(start) != last or convert(end) - convert(start) != int(minutes):
                errors.append(f"Day {section - 3}: inconsistent timing")
            last = convert(end)
        if last != 180:
            errors.append(f"Day {section - 3}: expected 180 minutes")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Checked local links in {len(files)} Markdown files and both 180-minute schedules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
