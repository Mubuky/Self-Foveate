"""Validate this static paper-page template using only the Python standard library.

Usage: python scripts/check_site.py [path/to/index.html]
This checks structure and local references, not scientific correctness or rendering.
"""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class SiteParser(HTMLParser):
    voids = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.elements = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag not in self.voids:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing </{tag}> at line {self.getpos()[0]}")
        else:
            self.stack.pop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="?", default=str(Path(__file__).resolve().parents[1] / "index.html"))
    args = parser.parse_args()
    path = Path(args.html).resolve()
    document = SiteParser()
    document.feed(path.read_text(encoding="utf-8"))
    document.close()
    errors = document.errors
    if document.stack:
        errors.append("Unclosed elements: " + ", ".join(document.stack))
    ids = Counter(attrs["id"] for _, attrs in document.elements if "id" in attrs)
    errors.extend("Duplicate ID: " + key for key, count in ids.items() if count > 1)
    if sum(tag == "main" for tag, _ in document.elements) != 1:
        errors.append("Expected exactly one main landmark.")
    html_attrs = next((attrs for tag, attrs in document.elements if tag == "html"), {})
    if not html_attrs.get("lang"):
        errors.append("Set the document language.")
    references = []
    for tag, attrs in document.elements:
        for name in ("src", "href"):
            if attrs.get(name):
                references.append(attrs[name])
        if attrs.get("srcset"):
            references.extend(item.strip().split()[0] for item in attrs["srcset"].split(","))
        if tag == "a" and attrs.get("target") == "_blank":
            if not {"noopener", "noreferrer"} <= set(attrs.get("rel", "").split()):
                errors.append("New-window link needs noopener noreferrer: " + attrs.get("href", ""))
        if tag == "a" and not attrs.get("href"):
            errors.append("Anchors need href; use a button for actions.")
        if tag == "button" and attrs.get("type") != "button":
            errors.append("Navigation controls must declare type=button.")
        if tag == "img":
            if not attrs.get("alt"):
                errors.append("Research figure needs meaningful alt text: " + attrs.get("src", ""))
            if not all(attrs.get(name, "").isdigit() for name in ("width", "height")):
                errors.append("Image needs numeric width and height: " + attrs.get("src", ""))
        for name in ("aria-controls", "aria-labelledby", "aria-describedby"):
            for target in attrs.get(name, "").split():
                if target not in ids:
                    errors.append(f"{name} points to missing ID: {target}")
    for reference in references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        if not url.path:
            if url.fragment and unquote(url.fragment) not in ids:
                errors.append("Missing anchor: " + reference)
            continue
        asset = (path.parent / unquote(url.path)).resolve()
        if not asset.is_relative_to(path.parent) or not asset.is_file():
            errors.append("Missing or out-of-root local file: " + reference)
    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print(f"PASS: HTML structure, {len(ids)} unique IDs, local assets, image metadata, ARIA references, and safe links.")


if __name__ == "__main__":
    main()
