"""Check the built Pages artifact without requesting external websites."""

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.canonical = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == "img":
            self.images.append(attrs)


def check_site(root, baseurl):
    pages = {path: Page(path) for path in root.rglob("*.html")}
    errors = []
    # The canonical origin comes from the generated home page, not a hardcoded domain.
    homepage = root / "index.html"
    if homepage not in pages:
        return ["Missing index.html"], 0
    canonical = pages[homepage].canonical
    origin = f"https://{urlsplit(canonical).netloc}" if canonical else "https://local.invalid"

    for path, page in pages.items():
        name = path.relative_to(root)
        duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
        if duplicates:
            errors.append(f"{name}: duplicate IDs: {', '.join(duplicates)}")
        for image in page.images:
            label = image.get("src", "image")
            if not image.get("alt", "").strip():
                errors.append(f"{name}: missing descriptive alt text: {label}")
            if any(not image.get(key, "").isdigit() or int(image[key]) <= 0 for key in ("width", "height")):
                errors.append(f"{name}: missing positive image dimensions: {label}")
        for link in page.links:
            url = urlsplit(urljoin(f"{origin}{baseurl}/{name.as_posix()}", link))
            if url.scheme not in ("http", "https") or url.netloc != urlsplit(origin).netloc:
                continue
            target_path = unquote(url.path)
            if baseurl:
                if not target_path.startswith(baseurl + "/"):
                    errors.append(f"{name}: link escapes baseurl: {link}")
                    continue
                target_path = target_path[len(baseurl):]
            target = root / target_path.lstrip("/")
            if target.is_dir():
                target = target / "index.html"
            elif not target.suffix and not target.exists():
                target = target.with_suffix(".html")
            if not target.is_file():
                errors.append(f"{name}: missing local target: {link}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{name}: missing fragment: {link}")

    dev_names = {"readme.md", "AGENTS.md", "Gemfile", "Gemfile.lock", ".ruby-version"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if (relative.parts[0] in {"scripts", "tests", "vendor", ".bundle"}
                or path.name in dev_names or path.name.startswith("secrets")
                or path.suffix in {".py", ".pyc", ".map"}):
            errors.append(f"Development file published: {relative}")
    for filename in ("feed.xml", "sitemap.xml"):
        try:
            ET.parse(root / filename)
        except (OSError, ET.ParseError) as error:
            errors.append(f"Invalid {filename}: {error}")
    return errors, len(pages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--baseurl", default="")
    args = parser.parse_args()
    errors, count = check_site(args.site.resolve(), args.baseurl.rstrip("/"))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {count} HTML pages: links, fragments, IDs, image metadata, feeds, and publication exclusions passed.")
