"""Render the article's reported Well-to-Wheels results into the B100 page.

The figures come from docs/rag/knowledge-pack.json (dataset fame_lca_results),
which is read from the stored article PDF.  Nothing is typed by hand here, and
the block is labelled as the study's own result, not a TamsoodBase calculation.

    python -X utf8 scripts/build_reported_results_html.py          # write
    python -X utf8 scripts/build_reported_results_html.py --check  # verify only
"""
from __future__ import annotations

import html
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "index.html"
PACK = ROOT / "docs" / "rag" / "knowledge-pack.json"
START, END = "<!-- reported-results:start -->", "<!-- reported-results:end -->"
ANCHOR = '<div class="case-controls">'
FUELS = [("FAME", "ไบโอดีเซล FAME"), ("H-FAME", "H-FAME"), ("BHD", "BHD"), ("Fossil diesel", "ดีเซลฟอสซิล")]
CATEGORY_TH = {
    "Global warming": "ภาวะโลกร้อน",
    "Fine particulate matter formation": "ฝุ่นละเอียด",
    "Terrestrial acidification": "ภาวะกรดบนบก",
    "Freshwater eutrophication": "สารอาหารเกินในน้ำจืด",
    "Marine eutrophication": "สารอาหารเกินในทะเล",
    "Human carcinogenic toxicity": "ความเป็นพิษก่อมะเร็ง",
    "Land use": "การใช้ที่ดิน",
    "Fossil resource scarcity": "การใช้ทรัพยากรฟอสซิล",
    "Human health": "สุขภาพมนุษย์ (ปลายทาง)",
    "Ecosystem quality": "คุณภาพระบบนิเวศ (ปลายทาง)",
    "Resource availability": "ทรัพยากรที่เหลือใช้ (ปลายทาง)",
}


def shown(value) -> str:
    """Plain decimal text; small values keep every significant digit."""
    # Decimal keeps tiny values exact; format(float, "f") would cut them to six places.
    text = format(Decimal(str(value)), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    whole, _, fraction = text.partition(".")
    whole = f"{int(whole):,}"
    return f"{whole}.{fraction}" if fraction else whole


def render() -> str:
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    dataset = next(item for item in pack["datasets"] if item["id"] == "fame_lca_results")
    cell = {(row["flow"], row["process"]): row for row in dataset["records"]}
    warming = [cell[("Global warming", fuel)] for fuel, _ in FUELS]
    highest = max(row["amount"] for row in warming)
    tiles = "".join(
        f'<div class="reported-tile{" reported-tile--fossil" if fuel == "Fossil diesel" else ""}">'
        f'<small>{html.escape(label)}</small><strong>{shown(row["amount"])}</strong>'
        f'<span>kg CO₂ eq</span><i style="width:{max(2, round(row["amount"] / highest * 100))}%"></i></div>'
        for (fuel, label), row in zip(FUELS, warming))
    categories = list(dict.fromkeys(row["flow"] for row in dataset["records"]))
    body = "".join(
        "<tr><th scope=\"row\">" + html.escape(CATEGORY_TH.get(name, name))
        + f'<small>{html.escape(name)}</small></th>'
        + "".join(f'<td>{shown(cell[(name, fuel)]["amount"])}</td>' for fuel, _ in FUELS)
        + f'<td class="unit">{html.escape(cell[(name, "FAME")]["unit"])}</td></tr>'
        for name in categories)
    head = "".join(f'<th scope="col">{html.escape(label)}</th>' for _, label in FUELS)
    url = html.escape(dataset["source_urls"]["all"])
    return (
        f'{START}\n<section class="reported-results" aria-labelledby="reported-results-title">'
        '<p class="eyebrow">WELL-TO-WHEELS · ผลที่งานวิจัยรายงาน</p>'
        '<h3 id="reported-results-title">ผลทั้งวงจรชีวิตตามที่งานวิจัยตีพิมพ์</h3>'
        '<p>ภาวะโลกร้อนต่อการใช้เชื้อเพลิง 1,000 MJ นับตั้งแต่ปลูกปาล์ม ขนส่ง สกัด กลั่น ผลิตเชื้อเพลิง จนถึงใช้ในรถกระบะ</p>'
        f'<div class="reported-tiles">{tiles}</div>'
        '<p class="reported-caveat"><strong>อ่านก่อนใช้:</strong> เป็นผลที่ผู้วิจัยคำนวณและรายงานไว้ ไม่ใช่ผลที่ TamsoodBase คำนวณเอง '
        'ผู้วิจัยใช้ฐานข้อมูลพื้นหลัง ecoinvent 3 และปันส่วนตามมูลค่าทางเศรษฐกิจ BHD ใช้ข้อมูลการผลิตจากฟินแลนด์ และ H-FAME มาจากโรงงานต้นแบบ '
        'โมเดลของทีมด้านล่างยังคำนวณ CO₂e รวมเองไม่ได้</p>'
        '<details class="reported-table"><summary>ดูผลกระทบทั้ง 11 หมวด</summary><div class="table-scroll"><table>'
        f'<thead><tr><th scope="col">หมวดผลกระทบ</th>{head}<th scope="col">หน่วย ต่อ 1,000 MJ</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div></details>'
        f'<p class="reported-source">ที่มา: <a href="{url}" target="_blank" rel="noopener noreferrer">Permpool, Ghani &amp; Gheewala (2020), '
        'Sustainability 12(22), 9415</a> · ตาราง 5–6 · วิธี ReCiPe 2016 · '
        '<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a> · '
        '<a href="/ask.html">ถามผู้ช่วยเรื่องผลชุดนี้ ↗</a></p></section>\n'
        f'{END}')


def main() -> int:
    page = PAGE.read_text(encoding="utf-8")
    block = render()
    if START in page:
        updated = page[:page.index(START)] + block + page[page.index(END) + len(END):]
    else:
        if page.count(ANCHOR) != 1:
            raise SystemExit("Could not find a single insertion point in the B100 section")
        updated = page.replace(ANCHOR, block + "\n" + ANCHOR)
    if "--check" in sys.argv:
        if updated != page:
            print("reported-results block in web/index.html is stale; rebuild it", file=sys.stderr)
            return 1
    else:
        PAGE.write_text(updated, encoding="utf-8", newline="")
    print(json.dumps({"page": "web/index.html", "block_chars": len(block)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
