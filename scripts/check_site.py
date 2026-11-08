"""Check portfolio links and real model output without starting Ollama."""

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from studynote import validate_note


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            assert values["id"] not in self.ids, f"Duplicate id: {values['id']}"
            self.ids.add(values["id"])
        for name in ["href", "src"]:
            if name in values:
                self.links.append(values[name])


def main():
    site = ROOT / "site"
    for filename in ["index.html", "app.html"]:
        parser = Links()
        parser.feed((site / filename).read_text(encoding="utf-8"))
        for link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            if not parsed.path and parsed.fragment:
                assert parsed.fragment in parser.ids, f"Missing anchor: {link}"
            elif parsed.path:
                target = (site / unquote(parsed.path)).resolve()
                assert target.is_relative_to(site.resolve()), f"Outside site: {link}"
                assert target.is_file(), f"Missing file: {link}"
    result = json.loads((site / "data/example.json").read_text(encoding="utf-8"))
    validate_note(result["note"])
    assert result["meta"]["source"] == "live-ollama"
    article = (site / "data/article.txt").read_text(encoding="utf-8").strip()
    assert result["meta"]["input_characters"] == len(article)
    assert article == (ROOT / "examples/article.txt").read_text(encoding="utf-8").strip()
    print("PASS: local links, anchors, captured model result, source consistency")


if __name__ == "__main__":
    main()
