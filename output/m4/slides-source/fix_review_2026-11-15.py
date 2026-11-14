"""Apply the wording/ERD fixes from docs/review-after-claude-2026-11-15.md to the 3-minute deck and the poster."""
from pathlib import Path

base = Path(__file__).resolve().parents[1]
slides = base / 'slides-source' / 'build_slides_3min.js'
poster = base / 'poster-source' / 'poster10.template.html'


def apply(path, pairs):
    s = path.read_text(encoding='utf-8')
    for a, b in pairs:
        if a not in s:
            print('MISSING in', path.name, ':', a[:70].replace('\n', ' '))
            continue
        s = s.replace(a, b)
    path.write_text(s, encoding='utf-8')


apply(slides, [
    ("มี 9 ตารางใน MySQL schema tamsood_research ",
     "มี 9 ตารางใน MySQL schema tamsood_research (ภาพนี้ย่อ 7 ตาราง ไม่วาด publisher กับ product) "),
    ("  arr(4.75, 3.25, 4.75, 3.85); arr(3.0, 4.47, 3.4, 4.47); arr(6.1, 4.47, 6.5, 4.47);",
     "  arr(4.75, 3.25, 4.75, 3.85); arr(3.0, 4.47, 3.4, 4.47); arr(6.1, 4.47, 6.5, 4.47);\n"
     "  // composite FK: observation -> source_record (drawn from source_record down-left to observation)\n"
     "  s.addShape(pres.ShapeType.line, { x: 5.9, y: 3.25, w: 1.0, h: 0.6, flipH: true, line: { color: C.rust, width: 2.25, dashType: 'dash', endArrowType: 'triangle' } });"),
    ("T(s, '9 ตาราง · MySQL InnoDB · schema tamsood_research · ERD ฉบับเต็มอยู่ที่หัวข้อ 4.1 ในเล่ม', { x: 0.7, y: 6.0, w: 8.3, h: 0.35, fontSize: 12, color: C.mute });",
     "T(s, 'ภาพย่อ 7 จาก 9 ตาราง (ไม่วาด publisher, product) · เส้นประ = FK ประกอบ (snapshot_id, source_line) ระหว่าง observation กับ source_record (1 : 0..1) · ERD เต็มที่หัวข้อ 4.1 ในเล่ม', { x: 0.7, y: 6.0, w: 8.3, h: 0.6, fontSize: 11.5, color: C.mute });"),
    ("'ต่อจากนี้: บรรทัด 11399 → ไฟล์ต้นฉบับ → หน่วยงาน (ดูในคลิปฉาก 4)'",
     "'ตัวอย่าง trace ในคลิปใช้แถวเอราวัณ บรรทัด 11202 (หน้าปกใช้ไพลินเหนือ 11394)'"),
    ("'ถ้าถูกขอให้รันสด ใช้ sql/mysql/full-queries.sql ได้ (ตรวจกับฐานจริงก่อนขึ้นเวที)'",
     "'ผลทั้ง 4 แถวตรงกับ API จริง (ตรวจ 15 พ.ย.) แต่ยังไม่ได้รัน query นี้กับ MySQL โดยตรง จึงอย่าอ้างว่ารันสดบนฐาน ตัวอย่างอื่นอยู่ใน sql/mysql/full-queries.sql ' +\n    'ชื่อ view เป็นชื่อเดิม กรองแค่แถวที่ไม่ใช่สำเนา ไม่ได้กรองเฉพาะ Accepted (4 แถวนี้เป็น Accepted ตาม API) ถ้าพูดถึงการย้อนที่มาในคลิปคือแถวเอราวัณ 11202 คนละตัวอย่างกับ 11399 และไพลินเหนือ 11394 บนหน้าปก'"),
    ("อีก 243 รายการไม่รับ แต่ทุกแถวมีเหตุผลกำกับ", "อีก 243 รายการยังไม่รวมในยอดรับ (พักตรวจหรือแยกออก) ทุกแถวมีเหตุผลกำกับ"),
    ("pill(s, 0.75, 4.4, 3.5, 0.42, C.amber, '243 รายการไม่รับ · มีเหตุผลทุกแถว'",
     "pill(s, 0.75, 4.4, 4.6, 0.42, C.amber, '243 รายการยังไม่รวมในยอดรับ · มีเหตุผลทุกแถว'"),
    ("'41,315 พิจารณา → รับ 41,072 · ไม่รับ 243 (โครงสร้างผิด สำเนา พักตรวจ) มีเหตุผลทุกแถวใน acceptance-ledger'",
     "'41,315 พิจารณา → รับ 41,072 · อีก 243 ยังไม่รวมในยอดรับ (โครงสร้างผิด สำเนา ค่าขัดกัน พักหน่วย/ขนาด) มีเหตุผลทุกแถวใน acceptance-ledger'"),
    ("'ตารางยอดรับ-ไม่รับ แยกตามแหล่ง (กฎ AR-2)'", "'ยอดรับและยอดที่ยังไม่รวม แยกตามแหล่ง (กฎ AR-2)'"),
    ("['ชุดข้อมูล', 'พิจารณา', 'รับ', 'ไม่รับ', 'เหตุผลที่ไม่รับ']", "['ชุดข้อมูล', 'พิจารณา', 'รับ', 'ไม่รวม', 'เหตุผลที่ยังไม่รวมในยอดรับ']"),
])

apply(poster, [
    ('<small>MySQL InnoDB · 9 ตาราง (ชุด DMF)</small>', '<small>MySQL InnoDB · ภาพย่อ 7 จาก 9 ตาราง (ชุด DMF)</small>'),
    ('<p class="note">+ <code>rejected_record</code> · 4 schema · <b class="r">ข้อยกเว้นตั้งใจ:</b> raw_value คู่ amount เพื่อ audit จึงไม่อ้าง 3NF ทุก relation</p>',
     '<p class="note">+ <code>rejected_record</code> · FK ประกอบ (snapshot_id, source_line): observation → source_record · <b class="r">ยังไม่ได้พิสูจน์ normal form</b> ครบทุก relation (raw_value คู่ amount ไว้ audit)</p>'),
    ('ไม่รับ 243 มีเหตุผลทุกแถว', 'อีก 243 ยังไม่รวมในยอดรับ มีเหตุผลทุกแถว'),
    ('<small>3 คำถามเดียวกัน · ผลตรวจกับ lab: Q1–Q2 ตรง SQL ทุกกรณี (4/4)</small>',
     '<small>ผลเดิมเทียบ SQLite · ยืนยันกับ CSV/Neo4j/API · ยังไม่รัน SQL นี้กับ MySQL รอบล่าสุด</small>'),
    ('<th>SQL (MySQL · tamsood_supplemental)</th>', '<th>SQL สำหรับ MySQL · tamsood_supplemental</th>'),
    ('lab ไม่ใช่ graph ของเว็บจริง · ไม่อนุมานความสัมพันธ์ต้นน้ำ', 'ตัวอย่างย่อ ไม่ใช่คำสั่งพร้อมรัน (scripts/load_product_inventory_csv.cypher) · lab ไม่ใช่ graph ของเว็บจริง'),
    ('<p class="note">ไม่ระบุว่ารวมเดือนหรือต่อวัน จึงไม่บวกข้ามเดือน</p>',
     '<p class="note">ไม่ระบุว่ารวมเดือนหรือต่อวัน จึงไม่บวกข้ามเดือน · view ใช้ชื่อเดิม ไม่ได้กรองเฉพาะ Accepted (4 แถวนี้ Accepted ตาม API)</p>'),
    ('<li>เลือกความสอดคล้อง (C) ก่อน เพราะที่มาต้องตรงกัน</li>', '<li>แนวทางออกแบบเน้นความสอดคล้อง (ไม่ใช่ผลพิสูจน์ว่าเป็น CP)</li>'),
    ('kg CO₂ eq · ตาราง 5 · ', 'kg CO₂ eq · ตาราง 5 (BHD ใช้ข้อมูลโรงงานฟินแลนด์ · H-FAME เป็น pilot plant) · '),
])
print('done')
