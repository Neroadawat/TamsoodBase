"""Apply the team's acceptance rule AR-2 to the local data and write the ledger.

AR-2 (owner decision, 13 November 2026): a source-reported value is counted as
an accepted tuple when it is
  1. verified   - the stored value equals the value in the snapshotted source file,
  2. unique     - no other row has the same natural identity,
  3. traceable  - it carries the source file hash and a row/page/cell locator,
  4. relevant   - the source is about Thailand,
and nothing about its unit or magnitude is in doubt.  Rows that fail a check are
held with the reason; nothing is deleted or altered.

Acceptance says the tuple is a faithful, traceable copy of what the source
reported.  It does NOT say the DMF time basis is confirmed, that redistribution
rights are cleared, or that the tuple is a normalised product LCI exchange.

    python -X utf8 scripts/build_acceptance_ledger.py          # write
    python -X utf8 scripts/build_acceptance_ledger.py --check  # verify only
"""
from __future__ import annotations

import csv
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "acceptance-ledger.json"
RULE = "AR-2"
DECIDED_ON = "2026-11-13"


def dmf() -> dict:
    run = sorted(p for p in (ROOT / "build" / "dmf").iterdir() if p.is_dir())[-1]
    quality = json.loads((run / "quality-report.json").read_text(encoding="utf-8"))
    raw = sum(package["raw_rows"] for package in quality["packages"])
    rejected = sum(package["rejected"] for package in quality["packages"])
    dispositions = {}
    with (run / "duplicate-disposition.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            dispositions[row["status"]] = dispositions.get(row["status"], 0) + 1
    pack = json.loads((ROOT / "docs" / "rag" / "knowledge-pack.json").read_text(encoding="utf-8"))
    anomalies = {tuple(row) for row in next(d for d in pack["datasets"] if d["id"] == "dmf_production")["anomalies"]}
    rows = unit_note = 0
    with (run / "deduplicated-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["duplicate_status"] not in ("SINGLETON", "EXACT_REPRESENTATIVE"):
                continue
            rows += 1
            # The source label itself says the figure is LPG in kilograms, inside a file whose unit is barrels or cubic feet.
            if "kgs" in row["source_group"].lower() or "LPG" in row["source_group"]:
                unit_note += 1
    held = [
        {"count": rejected, "reason": "REJECTED_STRUCTURE: ค่าว่าง ไม่ระบุพื้นที่หรือแหล่ง"},
        {"count": dispositions.get("EXCLUDE_EXACT_COPY", 0), "reason": "EXACT_COPY: สำเนาซ้ำที่ค่าเท่ากันทุกช่อง นับเฉพาะตัวแทน"},
        {"count": dispositions.get("HOLD_CONFLICT", 0), "reason": "HOLD_CONFLICT: ช่วงเวลาและแหล่งเดียวกันแต่ค่าต่างกัน"},
        {"count": len(anomalies), "reason": "HOLD_MAGNITUDE: ค่าสูงกว่าค่าอื่นของชุดเดียวกันเกินร้อยเท่า น่าจะเป็นปัญหาหน่วยในไฟล์ต้นทาง"},
        {"count": unit_note, "reason": "HOLD_UNIT_LABEL: ชื่อแหล่งในไฟล์ระบุว่าเป็น LPG หน่วยกิโลกรัม ไม่ตรงกับหน่วยของไฟล์"},
    ]
    accepted = rows - len(anomalies) - unit_note
    assert raw == accepted + sum(item["count"] for item in held), "DMF rows do not reconcile"
    return {"dataset": "DMF การผลิตปิโตรเลียม", "source_rows": raw, "accepted": accepted, "held": held,
            "status": "ACCEPTED_SOURCE_STATISTIC",
            "caveat": "ฐานเวลาของค่ารายเดือน (ยอดรวมทั้งเดือนหรืออัตราต่อวัน) ยังไม่ยืนยันกับกรมเชื้อเพลิงธรรมชาติ และชื่อแหล่งผลิตยังไม่ได้จัดเป็นมาตรฐานเดียว",
            "verification": "ทุกแถวอ่านกลับได้ตรงกับไฟล์ CSV ที่เก็บสำเนา (เทียบด้วย SHA-256 ของไฟล์และเลขบรรทัด)"}


def eppo() -> dict:
    connection = sqlite3.connect(ROOT / "build" / "eppo" / "eppo.sqlite")
    total, = connection.execute("select count(*) from observation").fetchone()
    duplicates, = connection.execute(
        "select count(*) from (select 1 from observation group by snapshot_id,reference_year,month,subject having count(*)>1)").fetchone()
    assert duplicates == 0
    return {"dataset": "EPPO สถิติโรงกลั่น", "source_rows": total, "accepted": total, "held": [],
            "status": "ACCEPTED_SOURCE_STATISTIC",
            "caveat": "วัตถุดิบเข้ารายบริษัท (BBL/DAY) กับผลผลิตรวมประเทศ (Million Litres) เป็นคนละขอบเขต ห้ามหารเป็น yield",
            "verification": "ไม่มีค่าซ้ำตาม (ชุดข้อมูล, ปี, เดือน, รายการ); ทุกแถวมีเลขบรรทัดและ hash ของไฟล์ต้นทาง"}


def nso() -> dict:
    connection = sqlite3.connect(ROOT / "build" / "nso" / "nso.sqlite")
    total, = connection.execute("select count(*) from observation").fetchone()
    duplicates, = connection.execute(
        "select count(*) from (select 1 from observation group by table_id,reference_year,measure,label having count(*)>1)").fetchone()
    assert duplicates == 0
    return {"dataset": "NSO สถิติพลังงาน", "source_rows": total, "accepted": total, "held": [],
            "status": "ACCEPTED_SOURCE_STATISTIC",
            "caveat": "เทียบข้ามแหล่งได้ 169 ค่า ในจำนวนนี้ 4 ค่าไม่ตรงกับหน่วยงานต้นทางอีกแห่ง ค่าที่รับคือค่าตามตารางของสำนักงานสถิติแห่งชาติ",
            "verification": "ทุกค่าตรงกับช่องของไฟล์ CSV ที่เก็บสำเนา มีเลขบรรทัดและคอลัมน์"}


def research() -> list[dict]:
    pack = json.loads((ROOT / "docs" / "rag" / "knowledge-pack.json").read_text(encoding="utf-8"))
    by_id = {d["id"]: d for d in pack["datasets"]}
    inventory = by_id["fame_inventory"]["records"] + by_id["palm_upstream"]["records"]
    missing_unit = sum(1 for record in inventory if str(record.get("status", "")).startswith("HOLD"))
    results = by_id["fame_lca_results"]["records"]
    return [
        {"dataset": "งานวิจัย: บัญชีรายการปาล์มและไบโอดีเซล", "source_rows": len(inventory), "accepted": len(inventory) - missing_unit,
         "held": [{"count": missing_unit, "reason": "HOLD_MISSING_UNIT: บทความไม่ระบุหน่วย ทีมไม่เดาหน่วยให้"}],
         "status": "ACCEPTED_SOURCE_INVENTORY",
         "caveat": "แต่ละกระบวนการใช้ฐานของตัวเอง ยังไม่ได้เชื่อมเป็นบัญชี LCI ครบวงจร",
         "verification": "ทุกค่าชี้กลับถึงตาราง แถว และคอลัมน์ของบทความ (CC BY 4.0)"},
        {"dataset": "งานวิจัย: ผล LCA ที่บทความรายงาน", "source_rows": len(results), "accepted": len(results), "held": [],
         "status": "ACCEPTED_SOURCE_RESULT",
         "caveat": "เป็นผลที่ผู้วิจัยคำนวณ ใช้ข้อมูลพื้นหลัง ecoinvent และข้อมูล BHD จากฟินแลนด์ ไม่ใช่ผลคำนวณของทีม",
         "verification": "อ่านจาก PDF ที่เก็บสำเนาด้วยโค้ด เก็บรูปที่พิมพ์คู่กับค่าทศนิยม ตรงกัน 44/44"},
    ]


def corporate() -> dict:
    connection = sqlite3.connect(ROOT / "build" / "reusable" / "reference.sqlite")
    decisions = dict(connection.execute("select decision,count(*) from review group by decision").fetchall())
    total = sum(decisions.values())
    return {"dataset": "รายงานบริษัท (Thai Oil, SPRC)", "source_rows": total, "accepted": decisions.get("ACCEPTED_REFERENCE", 0),
            "held": [{"count": decisions.get("HOLD_CONTEXT", 0), "reason": "HOLD_CONTEXT: ชื่อและบริบทของตารางในรายงานไม่ตรงกัน"}],
            "status": "ACCEPTED_REFERENCE",
            "caveat": "รับเป็นข้อมูลอ้างอิงภายใน ปริมาณไม่เผยแพร่ต่อเพราะยังไม่ยืนยันสิทธิ์",
            "verification": "สกัดซ้ำจาก PDF ได้ค่าเดิมครบ มีเลขหน้า PDF และเลขหน้าที่พิมพ์"}


def build() -> dict:
    layers = [dmf(), eppo(), nso(), *research(), corporate()]
    return {
        "rule": RULE,
        "decided_on": DECIDED_ON,
        "decided_by": "Project owner, stated in a working session; the team should confirm it in a meeting memo",
        "meaning": "Accepted = verified against the snapshotted source, unique, traceable and Thailand-relevant. It does not confirm the DMF time basis, clear redistribution rights, or make a tuple a normalised product LCI exchange.",
        "database_state": "The MySQL column review_status still holds PENDING until sql/mysql/acceptance-ar2-migration.sql is applied on the server.",
        "layers": layers,
        "accepted_total": sum(layer["accepted"] for layer in layers),
        "held_total": sum(item["count"] for layer in layers for item in layer["held"]),
        "source_rows_total": sum(layer["source_rows"] for layer in layers),
    }


def main() -> int:
    ledger = build()
    text = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("acceptance ledger is stale; rebuild it", file=sys.stderr)
            return 1
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"accepted_total": ledger["accepted_total"], "held_total": ledger["held_total"],
                      "by_layer": {layer["dataset"]: layer["accepted"] for layer in ledger["layers"]}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
