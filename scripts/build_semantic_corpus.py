"""Build the semantic-retrieval corpus from the released knowledge pack only.

Chunks are the explanatory notes and the catalogue summaries that
docs/rag/knowledge-pack.json already ships to the public chat. Numeric tables
are NOT embedded: figures stay with the structured query engine in
api/rag/ask.js. Output: docs/rag/semantic-corpus.json (stable IDs + version).
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/rag/knowledge-pack.json"
MANIFEST = ROOT / "docs/rag/public-release-manifest.json"
OUT = ROOT / "docs/rag/semantic-corpus.json"
SCHEMA = 2

# Retrieval-only wording (colloquial Thai + English synonyms) written from each
# chunk's own content. Embedded with the chunk but never shown to users.
HINTS = {
    "note:fame-functional-unit": "ฐานเปรียบเทียบ หน่วยเปรียบเทียบ เทียบกันบนฐานอะไร เชื้อเพลิง 1000 เมกะจูล ตาราง 4 functional unit basis",
    "note:palm-upstream-basis": "ปาล์มน้ำมัน ผลปาล์มสด น้ำมันปาล์มดิบ น้ำมันปาล์มกลั่น หน่วยกิโลกรัม ไม่ใช่เมกะจูล บวกรวมหรือเชื่อมตารางไม่ได้ ฐานต่างกัน",
    "note:palm-land-unit-hold": "เตรียมพื้นที่ปลูก เตรียมที่ดิน เมล็ดพันธุ์ land seeding ไม่มีหน่วย ทำไมไม่นำมาใช้ พักข้อมูล",
    "note:palm-cpo-provider-gap": "ย้อนคำนวณ โรงสกัดน้ำมันปาล์มดิบ ผลปาล์มสดเป็นน้ำมันปาล์มดิบ ไม่มีข้อมูลป้อนเข้า เชื่อมไม่ได้ ช่องว่างข้อมูล CPO FFB",
    "note:fame-allocation-caution": "การจัดสรรภาระ ผลพลอยได้ กลีเซอรีน ระวังนับซ้ำ คูณซ้ำ แบ่งสัดส่วน allocation",
    "note:fame-measurement-period": "ปีของข้อมูล ปีที่เผยแพร่บทความ ปีที่วัดจริง ช่วงเวลาเก็บข้อมูล โรงงานนำร่อง ไม่ใช่ค่าเฉลี่ยทั้งประเทศ",
    "note:fame-wtw-boundary": "ตลอดวงจร ตั้งแต่ปลูกจนใช้ในรถ ขอบเขต Well to Wheels ผลกระทบโลกร้อน คาร์บอนทั้งวงจร วิธีประเมิน ไบโอดีเซล",
    "note:fame-allocation-factors": "สัดส่วนแบ่งภาระ ผลพลอยได้ กลีเซอรีน ปันส่วน ร้อยละที่ใช้ allocation factor",
    "note:fame-data-basis": "ที่มาของข้อมูล ข้อมูลมาจากไหน เก็บอย่างไร แหล่งข้อมูลของบทความ เกษตรกร โรงสกัด โรงกลั่น โรงงาน",
    "note:fame-contribution": "ขั้นตอนที่ส่งผลมากที่สุด กระทบมากสุด จุดร้อน hotspot ปลูกปาล์ม ผลิตไบโอดีเซล การใช้ในรถ ปุ๋ย",
    "catalogue:dmf_production": "กรมเชื้อเพลิงธรรมชาติ น้ำมันดิบ ก๊าซ คอนเดนเสท แหล่งผลิต บ่อ ขุดเจาะ ปิโตรเลียม รายเดือน ย้อนหลัง ตั้งแต่ปี",
    "catalogue:eppo_refinery_intake": "โรงกลั่น น้ำมันดิบเข้าโรงกลั่น บาร์เรลต่อวัน แยกบริษัท สนพ.",
    "catalogue:eppo_product_output": "ผลิตภัณฑ์น้ำมันสำเร็จรูป ดีเซล เบนซิน แอลพีจี ล้านลิตร รายเดือน",
    "catalogue:nso_energy": "สถิติพลังงานของประเทศ รายปี สมุดสถิติ สำนักงานสถิติแห่งชาติ จัดหาพลังงาน",
    "catalogue:fame_inventory": "ปัจจัยนำเข้าออกการผลิตไบโอดีเซล วัตถุดิบ เมทานอล ไอน้ำ ไฟฟ้า ขั้นแปรรูป",
    "catalogue:palm_upstream": "ปาล์มน้ำมัน ต้นน้ำ ปลูก สกัดน้ำมัน FFB CPO RBDPO",
    "catalogue:fame_lca_results": "ผลประเมินวัฏจักรชีวิต ก๊าซเรือนกระจก โลกร้อน ไบโอดีเซลเทียบดีเซลฟอสซิล",
    "catalogue:company_reports": "รายงานความยั่งยืน บริษัท Thai Oil SPRC ไทยออยล์ ตัวชี้วัดสิ่งแวดล้อม",
    "catalogue:ethanol_evidence": "เอทานอล แก๊สโซฮอล์ E10 ทดสอบรถ สตาร์ตเย็น ติดเครื่อง น้ำเสีย",
    "catalogue:acceptance": "จำนวนที่ทีมรับแล้ว พักไว้ ตรวจรับข้อมูล คุณภาพ accepted held",
    "catalogue:project_scope": "โปรเจกต์ ระบบนี้คืออะไร ขอบเขต วัตถุประสงค์ ข้อจำกัด ยังไม่ได้ทำ",
}


def build():
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["knowledge_pack"]["content_sha256"] != pack["content_sha256"]:
        raise SystemExit("Owner release decision does not cover this knowledge pack")
    chunks = []
    for note in pack["notes"]:
        chunks.append({
            "id": f"note:{note['id']}", "kind": "note", "ref": note["id"],
            "title": note["title"], "text": note["text"], "locator": note["locator"],
            "source_url": note["source_url"], "licence": note["licence"],
            "role": "team_explanation",  # explanation by the team, not a measured result
        })
    for item in pack["catalogue"]:
        chunks.append({
            "id": f"catalogue:{item['id']}", "kind": "catalogue", "ref": item["id"],
            "title": item["id"], "text": item["summary"], "locator": "catalogue summary",
            "answerable": bool(item["answerable"]), "role": "dataset_description",
        })
    for chunk in chunks:
        chunk["search_hint"] = HINTS[chunk["id"]]  # KeyError = new chunk needs reviewed wording
    body = json.dumps(chunks, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    version = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    return {"schema": SCHEMA, "pack_sha256": pack["content_sha256"],
            "corpus_version": version, "chunks": chunks}


def main():
    corpus = build()
    OUT.write_text(json.dumps(corpus, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"chunks": len(corpus["chunks"]), "corpus_version": corpus["corpus_version"]}))


if __name__ == "__main__":
    main()
