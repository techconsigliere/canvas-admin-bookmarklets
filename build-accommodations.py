#!/usr/bin/env python3
"""
Build the Quiz Accommodations bookmarklet for canvas-admin-bookmarklets.

Reads   src/accommodations.js
Writes  dist/accommodations.bookmarklet.txt
Updates docs/teacher/index.html, replacing the <a> between the BOOKMARKLET
        marker comments

Run from the repository root:

    python3 build-accommodations.py

The page edit is why this exists. Hand-pasting a 68 KB URL into an href after
every source change is how a stale build ends up published without anyone
noticing.

NOTE ON COMMENTS: this does not strip them, unlike whatever built the existing
dist files. Stripping JavaScript comments correctly means parsing the language,
because // and /* appear inside strings and regex literals, and a naive regex
quietly corrupts the tool. This dist file therefore decodes back to src byte
for byte. If the site's wording says dist is stripped, that sentence now needs
an exception, or this tool needs its own.
"""

from pathlib import Path
from urllib.parse import quote
import sys

ROOT = Path(__file__).parent
SOURCE = ROOT / "src" / "accommodations.js"
DIST = ROOT / "dist" / "accommodations.bookmarklet.txt"
PAGE = ROOT / "docs" / "teacher" / "index.html"

LABEL = "Quiz accommodations"
START = "<!-- BOOKMARKLET:START -->"
END = "<!-- BOOKMARKLET:END -->"

# Characters left unencoded. Quotes and angle brackets must NOT be listed: the
# URL lands inside href="...", where a bare double quote ends the attribute and
# a bare < can open a tag. Parentheses are encoded too, matching the existing
# builds on this site.
SAFE = "!#$&*+,-./:;=?@_~"


def main() -> int:
    if not SOURCE.exists():
        print(f"Missing {SOURCE.relative_to(ROOT)}", file=sys.stderr)
        print("Run this from the repository root.", file=sys.stderr)
        return 1

    url = "javascript:" + quote(SOURCE.read_text(encoding="utf-8"), safe=SAFE)

    for bad in ('"', "'", "<", ">", " "):
        if bad in url:
            print(f"Encoded URL contains {bad!r}, which would break the href.", file=sys.stderr)
            return 1

    DIST.parent.mkdir(parents=True, exist_ok=True)
    DIST.write_text(url + "\n", encoding="utf-8")
    print(f"Wrote {DIST.relative_to(ROOT)} ({len(url) / 1024:.1f} KB)")

    if not PAGE.exists():
        print(f"\n{PAGE.relative_to(ROOT)} not found, so no page was updated.", file=sys.stderr)
        return 1

    page = PAGE.read_text(encoding="utf-8")
    if START not in page or END not in page:
        print(f"\n{PAGE.relative_to(ROOT)} has no {START} / {END} markers.", file=sys.stderr)
        return 1

    head, _, rest = page.partition(START)
    _, _, tail = rest.partition(END)
    anchor = f'<a class="chip" href="{url}">{LABEL}</a>'
    PAGE.write_text(f"{head}{START}\n    {anchor}\n    {END}{tail}", encoding="utf-8")
    print(f"Updated {PAGE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
