"""Build the knowledge pack bundled with the public chat function.

The pack holds (1) a catalogue of every dataset layer in the project and
(2) source-reported values only for the layers the project owner released to
the public chat on 2026-11-12: Thai government open data (DMF, EPPO, NSO) and
the CC BY 4.0 article by Permpool et al. (2020).  Company-report values are
deliberately left out; the catalogue only says that they exist and links to
the original reports.

Values are copied from the audited local build artifacts.  Nothing is
estimated, converted or filled in here.

    python -X utf8 scripts/build_rag_knowledge_pack.py          # write
    python -X utf8 scripts/build_rag_knowledge_pack.py --check  # verify only
"""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "rag" / "knowledge-pack.json"
MANIFEST = ROOT / "docs" / "rag" / "public-release-manifest.json"
PACK_SCOPE = "OWNER_RELEASED_GOV_OPEN_DATA_AND_CC_BY_ARTICLE"
ARTICLE_URL = "https://doi.org/10.3390/su12229415"
ARTICLE_ATTRIBUTION = (
    "Permpool, Ghani & Gheewala (2020), Sustainability 12(22), 9415 — CC BY 4.0; "
    "คัดค่าตามที่บทความรายงานโดย TamsoodBase"
)
DMF_PRODUCTS = {
    "production-oil": ("oil", "น้ำมันดิบ"),
    "production-condensate": ("condensate", "คอนเดนเสท (ก๊าซธรรมชาติเหลว)"),
    "production-natural-gas": ("gas", "ก๊าซธรรมชาติ"),
}


def latest_dmf_run() -> Path:
    runs = sorted(p for p in (ROOT / "build" / "dmf").iterdir() if p.is_dir())
    if not runs:
        raise SystemExit("No DMF run found under build/dmf")
    return runs[-1]


def number(text: str):
    """Keep integers exact; fall back to float only for real decimals."""
    text = (text or "").strip()
    if text == "":
        return None
    try:
        return int(text)
    except ValueError:
        value = float(text)
        return int(value) if value.is_integer() else value


def index_of(values: list, item):
    if item not in values:
        values.append(item)
    return values.index(item)


def build_dmf() -> dict:
    run = latest_dmf_run()
    quality = json.loads((run / "quality-report.json").read_text(encoding="utf-8"))
    units = {}
    for package in quality["packages"]:
        key = DMF_PRODUCTS[package["package"]][0]
        multiplier = (package.get("metadata_multiplier") or "").strip()
        units[key] = f"{multiplier}{package['metadata_unit']}".strip()
    urls = {}
    fields: list[str] = []
    blocks: list[str] = [""]
    areas: list[str] = []
    products = [value[0] for value in DMF_PRODUCTS.values()]
    rows = []
    with (run / "deduplicated-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["duplicate_status"] not in ("SINGLETON", "EXACT_REPRESENTATIVE"):
                continue
            product = DMF_PRODUCTS[row["package"]][0]
            urls[product] = row["url"]
            rows.append([
                products.index(product),
                int(row["year_ce"]),
                int(row["month"]),
                index_of(areas, row["area"]),
                index_of(fields, row["source_group"]),
                index_of(blocks, row["block_label"] or ""),
                number(row["decimal_value"]),
                number(row["production_days"]),
            ])
    rows.sort()
    # A value far outside its own field's history is kept as reported but
    # flagged, so the chat can leave it out of averages and say so.
    by_series: dict[tuple, list] = {}
    for row in rows:
        if isinstance(row[6], (int, float)) and row[6] > 0:
            by_series.setdefault((row[0], row[4]), []).append(row[6])
    all_by_product: dict[int, list] = {}
    for (product_index, _), values in by_series.items():
        all_by_product.setdefault(product_index, []).extend(values)
    anomalies = []
    for row in rows:
        if not isinstance(row[6], (int, float)) or row[6] <= 0:
            continue
        product_values = sorted(all_by_product[row[0]])
        typical_max = product_values[int(len(product_values) * 0.999) - 1]
        if row[6] > 100 * typical_max:
            anomalies.append(row)
    return {
        "id": "dmf_production",
        "anomalies": anomalies,
        "anomaly_reason": "สูงกว่าค่าอื่นของชุดเดียวกันเกินร้อยเท่า น่าจะเป็นปัญหาหน่วยในไฟล์ต้นทาง ทีมยังไม่ได้ยืนยันกับกรมเชื้อเพลิงธรรมชาติ",
        "title": "ปริมาณการผลิตปิโตรเลียมรายเดือน แยกแหล่งผลิต (กรมเชื้อเพลิงธรรมชาติ)",
        "publisher": "กรมเชื้อเพลิงธรรมชาติ (DMF)",
        "licence": "Open Data Common (ป้ายบน catalog.dmf.go.th)",
        "attribution": "กรมเชื้อเพลิงธรรมชาติ, catalog.dmf.go.th — ดึงเมื่อ 22 ต.ค. 2569",
        "source_urls": urls,
        "columns": ["product", "year", "month", "area", "field", "block", "amount", "production_days"],
        "dictionaries": {"product": products, "area": areas, "field": fields, "block": blocks},
        "product_labels": {value[0]: value[1] for value in DMF_PRODUCTS.values()},
        "units": units,
        "aggregations": ["avg", "min", "max", "list"],
        "no_sum_reason": "ทีมยังไม่ได้ยืนยันว่าค่ารายเดือนของกรมเชื้อเพลิงธรรมชาติเป็นยอดรวมทั้งเดือนหรืออัตราต่อวัน จึงไม่บวกข้ามเดือน และแสดงเป็นค่าเฉลี่ยของค่ารายเดือนแทน",
        "caveats": [
            "ค่าเป็นตัวเลขรายเดือนตามที่ไฟล์ของกรมเชื้อเพลิงธรรมชาติรายงาน หน่วยมาจาก metadata ของชุดข้อมูล",
            "ทีมยังไม่ได้ยืนยันกับกรมฯ ว่าค่ารายเดือนเป็นยอดรวมทั้งเดือนหรืออัตราต่อวัน ระบบจึงไม่บวกข้ามเดือน แสดงได้เฉพาะค่ารายเดือน ค่าเฉลี่ยรายเดือน และค่าสูงสุด/ต่ำสุด",
            "ตัดแถวซ้ำที่ค่าตรงกันออกแล้ว และไม่รวมแถวที่ค่าขัดแย้งกันซึ่งยังรอตรวจ",
            "ปี 2026 (พ.ศ. 2569) มีข้อมูลถึงเดือนมีนาคมเท่านั้น",
        ],
        "rows": rows,
    }


def build_eppo() -> list[dict]:
    connection = sqlite3.connect(ROOT / "build" / "eppo" / "eppo.sqlite")
    packs = []
    specs = {
        "11_13": (
            "eppo_refinery_intake", "ปริมาณน้ำมันที่ป้อนเข้าโรงกลั่น แยกบริษัท รายเดือน", "company",
            ["avg", "min", "max", "list"],
            ["หน่วยเป็นบาร์เรลต่อวัน (BBL/DAY) ของเดือนนั้น จึงหาค่าเฉลี่ยรายเดือนได้แต่ไม่นำมาบวกรวมข้ามเดือน",
             "เป็นสถิติระดับบริษัท ห้ามนำไปหารกับปริมาณผลิตระดับประเทศเพื่อคิดเป็น yield ของโรงกลั่น"],
        ),
        "11_14": (
            "eppo_product_output", "ปริมาณการผลิตน้ำมันสำเร็จรูปของประเทศ แยกชนิด รายเดือน", "product",
            ["sum", "avg", "min", "max", "list"],
            ["เป็นสถิติระดับประเทศ หน่วยล้านลิตรต่อเดือน",
             "ห้ามนำไปหารกับปริมาณป้อนเข้าโรงกลั่นรายบริษัทเพื่อคิดเป็น yield"],
        ),
    }
    for dataset_id, (pack_id, title, subject_column, aggregations, caveats) in specs.items():
        url, = connection.execute(
            "select url from source_snapshot where dataset_id=?", (dataset_id,)).fetchone()
        subjects: list[str] = []
        rows = []
        unit_seen = set()
        query = ("select o.subject,o.reference_year,o.month,o.amount,o.unit from observation o "
                 "join source_snapshot s using(snapshot_id) where s.dataset_id=?")
        for subject, year, month, amount, unit in connection.execute(query, (dataset_id,)):
            unit_seen.add(unit)
            rows.append([index_of(subjects, subject), int(year), int(month), number(amount)])
        if len(unit_seen) != 1:
            raise SystemExit(f"EPPO {dataset_id}: expected one unit, found {unit_seen}")
        rows.sort()
        packs.append({
            "id": pack_id,
            "title": f"{title} (สนพ. / กรมธุรกิจพลังงาน)",
            "publisher": "สำนักงานนโยบายและแผนพลังงาน (EPPO); ต้นทางกรมธุรกิจพลังงาน (DOEB)",
            "licence": "Open Data Common (ป้ายบน catalog.eppo.go.th)",
            "attribution": "สำนักงานนโยบายและแผนพลังงาน, catalog.eppo.go.th — ดึงเมื่อ 23 ต.ค. 2569",
            "source_urls": {"all": url},
            "columns": [subject_column, "year", "month", "amount"],
            "dictionaries": {subject_column: subjects},
            "units": {"all": unit_seen.pop()},
            "aggregations": aggregations,
            **({} if "sum" in aggregations else {"no_sum_reason": "ชุดนี้มีหน่วยเป็นบาร์เรลต่อวัน จึงไม่บวกข้ามเดือน และแสดงเป็นค่าเฉลี่ยรายเดือนแทน"}),
            "caveats": caveats + ["ปี 2026 (พ.ศ. 2569) เป็นข้อมูลบางเดือน ยังไม่ครบปี"],
            "rows": rows,
        })
    return packs


def build_nso() -> dict:
    connection = sqlite3.connect(ROOT / "build" / "nso" / "nso.sqlite")
    tables: list[str] = []
    labels: list[str] = []
    units: list[str] = []
    urls = {}
    rows = []
    for table_id, year, measure, label, amount, unit, payload in connection.execute(
            "select table_id,reference_year,measure,label,amount,unit,payload from observation"):
        detail = json.loads(payload)
        urls[table_id] = detail["source_url"]
        name = label if measure in (label, None, "") else f"{label} — {measure}"
        rows.append([index_of(tables, table_id), index_of(labels, name), int(year),
                     number(amount), index_of(units, unit)])
    rows.sort()
    return {
        "id": "nso_energy",
        "title": "สถิติพลังงานของประเทศ จากสมุดสถิติรายปี 2569 ตาราง 13.5–13.10 (สำนักงานสถิติแห่งชาติ)",
        "publisher": "สำนักงานสถิติแห่งชาติ (NSO); ต้นทางกรมพัฒนาพลังงานทดแทนฯ และกรมธุรกิจพลังงาน",
        "licence": "ไฟล์ดาวน์โหลดสาธารณะของสำนักงานสถิติแห่งชาติ",
        "attribution": "สำนักงานสถิติแห่งชาติ, สมุดสถิติรายปีประเทศไทย 2569 บทที่ 13",
        "source_urls": urls,
        "columns": ["table", "label", "year", "amount", "unit"],
        "dictionaries": {"table": tables, "label": labels, "unit": units},
        "table_titles": {
            "13.5": "การจัดหาพลังงานขั้นต้น แยกชนิดพลังงาน",
            "13.6": "การจำหน่ายน้ำมันสำเร็จรูป แยกชนิด",
            "13.7": "ปริมาณและมูลค่าการนำเข้าส่งออกน้ำมัน",
            "13.8": "การผลิตและการใช้เชื้อเพลิง แยกชนิด",
            "13.10": "การใช้พลังงานขั้นสุดท้าย แยกสาขาเศรษฐกิจ",
        },
        "aggregations": ["list", "max", "min"],
        "caveats": [
            "เป็นสถิติรายปีระดับประเทศ แต่ละแถวมีหน่วยของตัวเอง จึงแสดงเป็นรายแถวและไม่บวกรวมข้ามแถว",
            "สำนักงานสถิติแห่งชาตินำข้อมูลมาเผยแพร่ต่อจากหน่วยงานต้นทาง ปีในตารางคือปีอ้างอิงของข้อมูล",
        ],
        "rows": rows,
    }


def build_inventories() -> list[dict]:
    packs = []
    connection = sqlite3.connect(ROOT / "build" / "product-inventory" / "inventory.sqlite")
    rows = []
    for process, direction, flow, amount, unit, payload in connection.execute(
            "select process_id,direction,flow,amount,unit,payload from exchange order by process_id,direction,flow"):
        detail = json.loads(payload)
        rows.append({"process": process, "direction": direction, "flow": flow,
                     "stage": detail.get("subprocess"), "amount": number(amount), "unit": unit})
    packs.append({
        "id": "fame_inventory",
        "title": "รายการเข้า–ออกขั้นแปรรูป FAME และ H-FAME ต่อการใช้เชื้อเพลิง 1,000 MJ (ตาราง 4 ของบทความ)",
        "publisher": "Permpool, Ghani & Gheewala (2020), Sustainability 12(22), 9415",
        "licence": "CC BY 4.0",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": ARTICLE_ATTRIBUTION,
        "source_urls": {"all": ARTICLE_URL},
        "aggregations": ["list"],
        "caveats": [
            "ฐานคือการใช้เชื้อเพลิง 1,000 MJ เป็นเฉพาะขั้นแปรรูป ไม่ใช่บัญชีรายการครบทั้งวงจรชีวิต",
            "ปีที่ตีพิมพ์ (2020) ไม่ใช่ปีที่วัดข้อมูล บทความไม่ได้ระบุช่วงปีที่วัด",
        ],
        "records": rows,
    })
    connection = sqlite3.connect(ROOT / "build" / "upstream-inventory" / "candidate.sqlite")
    rows = []
    for process, direction, amount, unit, status, payload in connection.execute(
            "select process_id,direction,amount,unit,status,payload from exchange order by process_id,direction"):
        detail = json.loads(payload)
        rows.append({"process": process, "direction": direction, "flow": detail.get("flow"),
                     "amount": number(amount), "unit": unit, "status": status})
    packs.append({
        "id": "palm_upstream",
        "title": "รายการเข้า–ออกต้นน้ำของปาล์มน้ำมัน: FFB, CPO, RBDPO ต่อผลิตภัณฑ์ 1,000 kg (ตาราง 1–3 ของบทความ)",
        "publisher": "Permpool, Ghani & Gheewala (2020), Sustainability 12(22), 9415",
        "licence": "CC BY 4.0",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": ARTICLE_ATTRIBUTION,
        "source_urls": {"all": ARTICLE_URL},
        "aggregations": ["list"],
        "caveats": [
            "แต่ละกระบวนการใช้ฐาน 1,000 kg ของผลิตภัณฑ์ตัวเอง จึงยังนำมาต่อกันเป็นสายเดียวไม่ได้โดยตรง",
            "แถวที่สถานะ HOLD_MISSING_UNIT คือบทความไม่ได้ระบุหน่วย ทีมจึงพักไว้ ไม่เดาหน่วยให้",
        ],
        "records": rows,
    })
    return packs


def build_notes() -> list[dict]:
    corpus = json.loads((ROOT / "docs" / "rag" / "vercel-preview-corpus.json").read_text(encoding="utf-8"))
    for row in corpus["records"]:
        if row["licence"] != "CC BY 4.0" or row["source_url"] != ARTICLE_URL:
            raise SystemExit(f"Note {row['id']} is not from the CC BY article")
    return [{key: row[key] for key in ("id", "title", "text", "locator", "source_url", "licence",
                                       "licence_url", "attribution")} for row in corpus["records"]]


def build_catalogue() -> list[dict]:
    """Every layer the project holds, including the ones the chat may not quote."""
    registry = list(csv.DictReader((ROOT / "docs" / "source-registry.csv").open(encoding="utf-8-sig")))
    urls = {row["source_id"]: row["url"] for row in registry}
    return [
        {"id": "dmf_production", "answerable": True,
         "summary": "ปริมาณการผลิตน้ำมันดิบ คอนเดนเสท และก๊าซธรรมชาติของไทย รายเดือน แยกแหล่งผลิต บนบก/ในทะเล ตั้งแต่ปี 2003 ถึงมีนาคม 2026 จากกรมเชื้อเพลิงธรรมชาติ"},
        {"id": "eppo_refinery_intake", "answerable": True,
         "summary": "ปริมาณน้ำมันที่ป้อนเข้าโรงกลั่นรายเดือน แยกบริษัท (บาร์เรลต่อวัน) ตั้งแต่ปี 1986 จากสำนักงานนโยบายและแผนพลังงาน"},
        {"id": "eppo_product_output", "answerable": True,
         "summary": "ปริมาณการผลิตน้ำมันสำเร็จรูปของประเทศรายเดือน แยกชนิด เช่น ดีเซล เบนซิน LPG (ล้านลิตร) ตั้งแต่ปี 1986 จากสำนักงานนโยบายและแผนพลังงาน"},
        {"id": "nso_energy", "answerable": True,
         "summary": "สถิติพลังงานรายปีของประเทศจากสมุดสถิติรายปี 2569: การจัดหาพลังงานขั้นต้น การจำหน่ายน้ำมัน การนำเข้าส่งออก การผลิตและใช้เชื้อเพลิง และการใช้พลังงานขั้นสุดท้าย ปีอ้างอิง 2022–2025"},
        {"id": "fame_inventory", "answerable": True,
         "summary": "รายการเข้า–ออกขั้นแปรรูปไบโอดีเซล FAME และ H-FAME ต่อการใช้เชื้อเพลิง 1,000 MJ จากบทความวิจัยของไทยที่เปิดให้ใช้ซ้ำ (CC BY 4.0)"},
        {"id": "palm_upstream", "answerable": True,
         "summary": "รายการเข้า–ออกต้นน้ำของปาล์มน้ำมัน (ทะลายปาล์มสด FFB, น้ำมันปาล์มดิบ CPO, น้ำมันปาล์มกลั่น RBDPO) ต่อ 1,000 kg จากบทความเดียวกัน"},
        {"id": "company_reports", "answerable": False,
         "summary": "ตัวชี้วัดสิ่งแวดล้อมที่คัดจากรายงานความยั่งยืนปี 2024 ของ Thai Oil และ SPRC รวม 101 รายการ ระบบเก็บไว้ใช้อ้างอิงภายใน แชตนี้ไม่คัดตัวเลขมาเผยแพร่ต่อเพราะยังไม่ได้ยืนยันสิทธิ์ ให้เปิดอ่านจากรายงานต้นฉบับ",
         "source_urls": [urls.get("THAIOIL-REPORT-2024"), urls.get("SPRC-REPORT-2024")]},
        {"id": "ethanol_evidence", "answerable": False,
         "summary": "หลักฐานประกอบกรณีศึกษาเอทานอลของไทย เช่น ผลทดสอบรถ E10 ช่วงสตาร์ตเย็น และเอกสารโครงการบำบัดน้ำเสีย/ไบโอแก๊สของโรงงานเอทานอล ระบบเก็บไว้ใช้ภายในและยังไม่มีค่า CO₂e ครบทั้งวงจร แชตนี้ไม่คัดตัวเลขมาเผยแพร่ต่อ",
         "source_urls": [urls.get("UNFCCC-TSM-WASTEWATER-PDD-2009")]},
        {"id": "project_scope", "answerable": True,
         "summary": "TamsoodBase เป็นฐานข้อมูลเชื้อเพลิงของไทยที่ตรวจย้อนกลับถึงแหล่งต้นทางได้ ยังไม่ใช่บัญชีรายการวัฏจักรชีวิต (LCI) ที่เชื่อมครบทั้งวงจร และยังไม่มีค่า CO₂e รวมทั้งวงจรของเชื้อเพลิงใด"},
    ]


def build() -> dict:
    datasets = [build_dmf(), *build_eppo(), build_nso(), *build_inventories()]
    pack = {
        "schema_version": 1,
        "scope": PACK_SCOPE,
        "owner_release_decision": "docs/rag/public-release-manifest.json",
        "contains_company_report_values": False,
        "catalogue": build_catalogue(),
        "datasets": datasets,
        "notes": build_notes(),
    }
    body = json.dumps(pack, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    pack["content_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return pack


def main() -> int:
    pack = build()
    text = json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n"
    counts = {d["id"]: len(d.get("rows") or d.get("records")) for d in pack["datasets"]}
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        recorded = json.loads(MANIFEST.read_text(encoding="utf-8")).get("knowledge_pack", {})
        if current != text or recorded.get("content_sha256") != pack["content_sha256"]:
            print("knowledge pack or its manifest hash is stale; rebuild it", file=sys.stderr)
            return 1
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if "knowledge_pack" in manifest:
            manifest["knowledge_pack"]["content_sha256"] = pack["content_sha256"]
            manifest["knowledge_pack"]["scope"] = pack["scope"]
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "bytes": len(text.encode("utf-8")),
                      "rows": counts, "notes": len(pack["notes"]),
                      "content_sha256": pack["content_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
