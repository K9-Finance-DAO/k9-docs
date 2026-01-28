from __future__ import annotations
import re
from pathlib import Path

DOCS = Path("docs")

# Match common GitBook/MkDocs asset patterns in markdown and HTML
#  - (.gitbook/assets/...)
#  - (/.gitbook/assets/...)
#  - (/assets/...)
#  - (assets/...)  [we'll normalize too]
MD_PAREN = re.compile(r'\((/?(?:\.gitbook/)?assets/[^)]+)\)')
HTML_SRC = re.compile(r'(<img[^>]+src=")(/?(?:\.gitbook/)?assets/[^"]+)(")', re.IGNORECASE)

def rel_prefix(md_path: Path) -> str:
    rel = md_path.relative_to(DOCS)
    depth = len(rel.parent.parts)
    return "../" * depth

def normalize_link(link: str) -> str:
    # Strip leading slash
    if link.startswith("/"):
        link = link[1:]
    # Convert .gitbook/assets -> assets
    link = link.replace(".gitbook/assets/", "assets/")
    return link

def rewrite_file(p: Path) -> bool:
    text = p.read_text(encoding="utf-8", errors="ignore")
    prefix = rel_prefix(p)

    def md_repl(m: re.Match) -> str:
        link = normalize_link(m.group(1))
        # Only rewrite links that point to assets/
        if not link.startswith("assets/"):
            return m.group(0)
        return f"({prefix}{link})"

    def html_repl(m: re.Match) -> str:
        link = normalize_link(m.group(2))
        if not link.startswith("assets/"):
            return m.group(0)
        return f'{m.group(1)}{prefix}{link}{m.group(3)}'

    new = MD_PAREN.sub(md_repl, text)
    new = HTML_SRC.sub(html_repl, new)

    if new != text:
        p.write_text(new, encoding="utf-8")
        return True
    return False

def main() -> None:
    changed = 0
    files = list(DOCS.rglob("*.md"))
    for p in files:
        if rewrite_file(p):
            changed += 1
    print(f"Updated {changed} file(s) out of {len(files)}.")

if __name__ == "__main__":
    main()
