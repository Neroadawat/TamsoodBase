"""Focused release checks for the public catalog skin and private RAG page."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


class PageCheck(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.h1_count = 0
        self.form_count = 0
        self._in_h1 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "h1":
            self.h1_count += 1
        if tag == "form":
            self.form_count += 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    public_html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    skin = (ROOT / "web/design-refresh.css").read_text(encoding="utf-8")
    page = (ROOT / "scripts/rag_demo.html").read_text(encoding="utf-8")

    require('/design-refresh.css' in public_html, "catalog skin is linked from the page")
    require("prefers-reduced-motion" in skin, "catalog animation respects reduced motion")
    require("@media (max-width: 760px)" in skin, "catalog skin includes a mobile layout")

    parser = PageCheck()
    parser.feed(page)
    parser.close()
    require(parser.h1_count == 1, "chat page has one primary heading")
    require(parser.form_count == 1, "chat page has one question form")
    require(len(parser.ids) == len(set(parser.ids)), "chat page IDs are unique")
    require({"question", "status", "results", "thread", "ask-form"}.issubset(parser.ids),
            "chat API/UI integration IDs remain available")
    require("<!-- mode-notice -->" in page, "server mode notice placeholder remains")
    require("/ask" in page and "JSON.stringify({question: asked})" in page,
            "only the current question is sent to the private API")
    require("innerHTML" not in page, "dynamic answers are rendered without HTML injection")
    require("target = '_blank'" in page and "noopener noreferrer" in page,
            "source links open safely in a separate tab")
    require("prefers-reduced-motion" in page, "chat animation respects reduced motion")
    require("คำถามแต่ละครั้งค้นแยกกัน" in page, "stateless question behavior is disclosed")

    script_match = re.search(r"<script>(.*?)</script>", page, flags=re.S)
    require(script_match is not None, "chat page has its integration script")
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as file:
        file.write(script_match.group(1))
        script_path = Path(file.name)
    try:
        check = subprocess.run(["node", "--check", str(script_path)],
                               capture_output=True, text=True, check=False)
        require(check.returncode == 0, "chat JavaScript parses: " + check.stderr.strip())
    finally:
        script_path.unlink(missing_ok=True)

    print("PASS: catalog integration, mobile/reduced-motion styles, chat markup, privacy boundary, safe source rendering, and JavaScript syntax")


if __name__ == "__main__":
    main()
