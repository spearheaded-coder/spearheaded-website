"""Static checks for the built site: tag balance, links/anchors, duplicate ids, form labels, risky copy."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DIST = Path(sys.argv[1])
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SVG_SELF = {"path", "circle", "rect", "line", "polyline", "polygon", "feturbulence", "stop"}


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.ids, self.links, self.labels_for, self.inputs = [], [], [], [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "label" and "for" in a:
            self.labels_for.add(a["for"])
        if tag in ("input", "select", "textarea") and a.get("type") not in ("hidden", "radio", "checkbox"):
            self.inputs.append(a.get("id") or a.get("name"))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


pages = {p.name: p for p in DIST.glob("*.html")}
ids_by_page = {}
problems = []
for name, path in sorted(pages.items()):
    p = P()
    p.feed(path.read_text())
    ids_by_page[name] = set(p.ids)
    if p.errors:
        problems.append((name, "tags", p.errors[:5]))
    if p.stack:
        problems.append((name, "unclosed", p.stack[-5:]))
    dups = {i for i in p.ids if p.ids.count(i) > 1}
    if dups:
        problems.append((name, "duplicate ids", dups))
    unlabeled = [i for i in p.inputs if i not in p.labels_for and i != "company-website"]
    if unlabeled:
        problems.append((name, "unlabelled fields", unlabeled))
    p.name = name
    pages[name] = (path, p.links)

for name, (path, links) in pages.items():
    for href in links:
        if href.startswith(("http", "mailto:", "tel:")):
            continue
        target, _, frag = href.lstrip("/").partition("#")
        target = target or name
        if target not in ids_by_page:
            problems.append((name, "broken link", href))
        elif frag and frag not in ids_by_page[target]:
            problems.append((name, "missing anchor", href))

risky = re.compile(r"fiduciar|wealth management|guarantee(?!d\.)|best in|leading|award|#1|risk-free|tax-free returns", re.I)
for name, (path, _) in pages.items():
    text = re.sub(r"<[^>]+>", " ", path.read_text())
    for m in risky.finditer(text):
        problems.append((name, "wording", text[max(0, m.start() - 40): m.end() + 30].strip()))

placeholders = sorted({m for path, _ in pages.values() for m in re.findall(r"\[[A-Z][A-Z ’'—:-]{2,}[^\]]*\]", path.read_text())})
print("PROBLEMS:" if problems else "No structural problems found.")
for pr in problems:
    print("  ", pr)
print("\nPLACEHOLDERS STILL TO FILL:")
for ph in placeholders:
    print("  ", ph[:90])
