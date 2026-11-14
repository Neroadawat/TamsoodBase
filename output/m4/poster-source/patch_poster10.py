"""Tighten poster10.template.html so all 10 blocks fit on one A4 page."""
from pathlib import Path

p = Path(__file__).parent / 'poster10.template.html'
s = p.read_text(encoding='utf-8')
pairs = [
 # global density
 ('font-size:7.3pt;line-height:1.42', 'font-size:6.8pt;line-height:1.36'),
 ('padding:5mm 9mm 4mm;display:grid', 'padding:3.4mm 9mm 2.8mm;display:grid'),
 ('h1{font-size:24pt', 'h1{font-size:20pt'),
 ('.tagline{font-size:9.4pt', '.tagline{font-size:8.4pt'),
 ('.team{font-size:6.6pt;line-height:1.5', '.team{font-size:6.2pt;line-height:1.4'),
 ('padding:3.2mm 9mm 0;display:grid;grid-template-columns:1fr 1fr;gap:2.8mm', 'padding:2.4mm 9mm 0;display:grid;grid-template-columns:1fr 1fr;gap:2mm'),
 ('padding:2.2mm 2.8mm;min-width:0', 'padding:1.6mm 2.4mm;min-width:0'),
 ('h2{font-size:9pt;font-weight:800;color:var(--pine);display:flex;align-items:center;gap:1.8mm;margin-bottom:1.3mm',
  'h2{font-size:8.4pt;font-weight:800;color:var(--pine);display:flex;align-items:center;gap:1.6mm;margin-bottom:.9mm'),
 # block 1
 ('<p>MTEC ต้องการข้อมูล LCI ของไทยที่รวมเป็นฐานเดียวและตรวจย้อนกลับได้ เป้าหมายของทีมคือตอบ 3 คำถามนี้ด้วยหลักฐาน:</p>',
  '<p>เป้าหมาย: ฐานข้อมูลสถิติเชื้อเพลิง/LCI ของไทยที่ตรวจย้อนกลับได้ ตอบ 3 คำถามของ MTEC ด้วยหลักฐาน</p>'),
 ('<p class="flowline">ค้นแหล่ง → ดึงและเก็บสำเนา → อ่านความหมาย → จัดรูปแบบ → ตรวจและคัด → จัดเก็บ MySQL</p>',
  '<p class="flowline">ค้น → ดึง+เก็บสำเนา → อ่านความหมาย → จัดรูปแบบ → ตรวจ/คัด → เก็บ MySQL</p>'),
 # block 2
 ('<p class="note">+ <code>rejected_record</code> เก็บแถวที่ปฏิเสธพร้อมเหตุผล · แยกเป็น 4 schema ตามความหมาย: research · reusable · supplemental · eppo<br>\n    <b class="r">ข้อยกเว้นที่ตั้งใจ:</b> raw_value เก็บคู่ amount เพื่อ audit จึงไม่อ้างว่าผ่าน 3NF ทุก relation</p>',
  '<p class="note">+ <code>rejected_record</code> · 4 schema: research · reusable · supplemental · eppo · <b class="r">ข้อยกเว้นตั้งใจ:</b> raw_value คู่ amount เพื่อ audit จึงไม่อ้าง 3NF ทุก relation</p>'),
 # block 3
 ('<p class="note" style="margin-top:.8mm">รับ = ตรงต้นทาง · ไม่ซ้ำ · ย้อนได้ · เป็นข้อมูลไทย (เกณฑ์ของทีม ไม่ใช่การรับรองจาก MTEC)</p>',
  '<p class="note" style="margin-top:.5mm">รับ = ตรงต้นทาง · ไม่ซ้ำ · ย้อนได้ · เป็นข้อมูลไทย (เกณฑ์ทีม ไม่ใช่การรับรองจาก MTEC)</p>'),
 # block 4
 ("<em>MERGE</em> (p)-[:HAS_EXCHANGE]-&gt;(e)-[:OF_FLOW]-&gt;(f:Flow)\n<em>MERGE</em> (e)-[:FROM_SOURCE]-&gt;(s:Source)</pre>",
  "<em>MERGE</em> (p)-[:HAS_EXCHANGE]-&gt;(e)-[:OF_FLOW]-&gt;(f:Flow)</pre>"),
 ('<span>HAS_EXCHANGE</span><span>OF_FLOW</span><span>IN_UNIT</span><span>FROM_SOURCE</span><span>LOCATED_IN</span>',
  '<span>HAS_EXCHANGE</span><span>OF_FLOW</span><span>FROM_SOURCE</span>'),
 ('<p class="note" style="margin-top:.8mm">ไม่ใช่ graph ของเว็บจริง · ไม่ได้อนุมานความสัมพันธ์ต้นน้ำ</p>',
  '<p class="note" style="margin-top:.5mm">lab ไม่ใช่ graph ของเว็บจริง · ไม่อนุมานความสัมพันธ์ต้นน้ำ</p>'),
 # block 5
 ('<td>Q1 FAME ใช้ INPUT อะไรบ้าง พร้อมหน่วย?<br><span class="ok">8 รายการ ตรงกัน</span></td>',
  '<td>Q1 FAME ใช้ INPUT อะไรบ้าง? <span class="ok">8 = 8</span></td>'),
 ('<td>Q2 แต่ละกระบวนการมี INPUT/OUTPUT กี่รายการ?<br><span class="ok">FAME 8/2 · H-FAME 5/1</span></td>',
  '<td>Q2 นับ INPUT/OUTPUT ต่อกระบวนการ <span class="ok">8/2 · 5/1</span></td>'),
 ('<td>Q3 ค่านี้มาจากบทความไหน? (ย้อนที่มา)<br><span class="mute">ตัวอย่างรูปแบบ ยังไม่ได้วัดผล</span></td>',
  '<td>Q3 ค่านี้มาจากบทความไหน? <span class="mute">(ตัวอย่าง)</span></td>'),
 ('<p class="note" style="margin-top:.7mm"><b class="r">ข้อสังเกต:</b> SQL เหมาะกับการนับ/กรอง/คุมข้อกำหนดด้วย CHECK และ FK · Cypher อ่านเส้นทางหลายทอดได้สั้นกว่า แต่ lab นี้ยังเล็ก (16 แถว) ไม่ได้วัดประสิทธิภาพ</p>',
  '<p class="note" style="margin-top:.5mm"><b class="r">ข้อสังเกต:</b> SQL เหมาะกับนับ/กรอง/คุมด้วย CHECK+FK · Cypher อ่านหลายทอดสั้นกว่า · lab เล็ก (16 แถว) ไม่ได้วัดประสิทธิภาพ</p>'),
 # block 6
 ('<p class="note"><code>SELECT … FROM deduplicated_pending WHERE product_code=\'crude_oil\' AND period_start=\'2026-03-01\' ORDER BY amount DESC LIMIT 4;</code></p>',
  '<p class="note"><code>… FROM deduplicated_pending WHERE product_code=\'crude_oil\' AND period_start=\'2026-03-01\' ORDER BY amount DESC LIMIT 4</code></p>'),
 ('<p class="note">ไฟล์ไม่บอกว่าเป็นยอดรวมเดือนหรืออัตราต่อวัน จึงไม่บวกข้ามเดือน</p>',
  '<p class="note">ไม่ระบุว่ารวมเดือนหรือต่อวัน จึงไม่บวกข้ามเดือน</p>'),
 ('<div class="hop"><em>2</em><span>ไฟล์ <code>production_condensate.csv</code> บรรทัด <code>11394</code> → SHA-256 <code>79f5ac2a…ae678d1c</code> (ดึง 22 ต.ค. 2569)</span></div>\n    <div class="hop"><em>3</em><span>กรมเชื้อเพลิงธรรมชาติ · catalog.dmf.go.th</span></div>',
  '<div class="hop"><em>2</em><span><code>production_condensate.csv</code> บรรทัด <code>11394</code> · SHA-256 <code>79f5ac2a…ae678d1c</code> · กรมเชื้อเพลิงธรรมชาติ (ดึง 22 ต.ค. 2569)</span></div>'),
 # block 7
 ('<li><b>I</b> READ COMMITTED ไม่เกิด dirty read · REPEATABLE READ (ค่าเริ่มต้น) เห็น snapshot คงที่ · แถวที่ล็อกถูกกันเขียนทับ (error 1205)</li>',
  '<li><b>I</b> ไม่เกิด dirty read (READ COMMITTED) · snapshot คงที่ (REPEATABLE READ) · แถวที่ล็อกกันเขียนทับ (1205)</li>'),
 ('<li>ระบบรันเป็นโหนดเดียว ยังไม่มีการทำสำเนา จึงยังไม่ได้ทดสอบ partition</li>\n        <li>เลือกความสอดคล้อง (C) ก่อนความพร้อมใช้ เพราะข้อมูลต้องย้อนที่มาได้ตรงกัน</li>\n        <li>Neo4j/Qdrant เป็น lab บนเครื่องเดียว ไม่ใช่ cluster</li>',
  '<li>โหนดเดียว ไม่มีสำเนา จึงยังไม่ได้ทดสอบ partition</li>\n        <li>เลือกความสอดคล้อง (C) ก่อน เพราะที่มาต้องตรงกัน</li>\n        <li>Neo4j/Qdrant เป็น lab เครื่องเดียว ไม่ใช่ cluster</li>'),
 ('<p class="note" style="margin-top:.8mm"><b class="r">ยังไม่ได้ทดสอบ:</b> ไฟดับ/รีสตาร์ต, SERIALIZABLE, โหลดจริง · หลักฐาน: evidence/mysql-transaction-audit.json</p>',
  '<p class="note" style="margin-top:.5mm"><b class="r">ยังไม่ทดสอบ:</b> ไฟดับ/รีสตาร์ต · SERIALIZABLE · โหลดจริง (evidence/mysql-transaction-audit.json)</p>'),
 # block 8
 ('<div><b>ฝังข้อความ:</b> evidence-card (ชื่อ + ข้อความ) 10 ใบ ด้วย <code>paraphrase-multilingual-MiniLM-L12-v2</code> · 384 มิติ · cosine</div>\n      <div><b>Vector index:</b> Qdrant Local <code>public_evidence_299826cac729177fd62b</code> (10 points)</div>',
  '<div><b>ฝัง + ดัชนี:</b> evidence-card 10 ใบ · <code>paraphrase-multilingual-MiniLM-L12-v2</code> · 384 มิติ · cosine · Qdrant Local (10 points)</div>'),
 ('<div><b>ผลทดสอบ retrieval:</b> ใช้คะแนนความคล้ายอย่างเดียว (cutoff 0.45) ได้ 10/12 และปฏิเสธถูก 6/8 → เพิ่มกฎขอบเขตได้ <span class="ok">12/12 และ 8/8</span></div>',
  '<div><b>ผลค้น:</b> คะแนนอย่างเดียว (cutoff 0.45) 10/12 และปฏิเสธถูก 6/8 → เพิ่มกฎขอบเขต <span class="ok">12/12 และ 8/8</span></div>'),
 ('<div><b>ตัวอย่าง:</b> “ตอนสตาร์ตเย็น E10 ค่าเท่าไร?” → การ์ด e10-cold-start: 2.36 กม./ลิตร · CO₂ ท่อไอเสีย 934.990 g/km (ไม่ใช่ CO₂e ตลอดวงจร)</div>',
  '<div><b>ตัวอย่าง:</b> “สตาร์ตเย็น E10 ค่าเท่าไร?” → 2.36 กม./ลิตร · CO₂ ท่อไอเสีย 934.990 g/km (ไม่ใช่ CO₂e ตลอดวงจร)</div>'),
 ('<p class="note" style="margin-top:.8mm">ข้อจำกัด: ชุดคำถามทีมเขียนเอง วัด retrieval ไม่ใช่ความถูกต้องของคำตอบ · multi-hop อยู่ที่ Neo4j (บล็อก 5)</p>',
  '<p class="note" style="margin-top:.5mm">ข้อจำกัด: คำถามทีมเขียนเอง วัด retrieval ไม่ใช่ความถูกต้องของคำตอบ</p>'),
 # block 9
 ('<li>รับ <b>41,072</b> จาก 41,315 · พัก DMF 228 = สำเนา 42 + ค่าขัดกัน 186 (+ 4 แถวหน่วย/ขนาด)</li>\n      <li>ทุกค่าเปิด “ดูที่มา” ถึงบรรทัดต้นฉบับ + SHA-256 ได้</li>\n      <li>ผลวิจัย (ไม่ใช่ผลคำนวณของทีม) ภาวะโลกร้อนต่อ 1,000 MJ:</li>',
  '<li>รับ <b>41,072</b> จาก 41,315 · DMF พัก 228 = สำเนา 42 + ขัดกัน 186 (+4 หน่วย/ขนาด)</li>\n      <li>ทุกค่าเปิด “ดูที่มา” ถึงบรรทัดต้นฉบับ + SHA-256 ได้</li>\n      <li>ผลวิจัย (ไม่ใช่ผลคำนวณทีม) ต่อ 1,000 MJ:</li>'),
 ('<p class="note">kg CO₂ eq · Well-to-Wheels · ตาราง 5 · <b class="r">ยังไม่ปิด:</b> บัญชี LCI ครบวงจร (ขนส่ง ของเสีย) → CO₂e รวมของทีมจึงไม่คำนวณ · ฐานเวลา DMF · สิทธิ์ข้อมูลบางแหล่ง</p>',
  '<p class="note">kg CO₂ eq · Well-to-Wheels · ตาราง 5 · <b class="r">ยังไม่ปิด:</b> LCI ครบวงจร → CO₂e รวมของทีมไม่คำนวณ · ฐานเวลา DMF · สิทธิ์ข้อมูล</p>'),
 # block 10 + footer
 ('<div>สำนักงานนโยบายและแผนพลังงาน (EPPO). การใช้น้ำมันในการกลั่น (11_13) · การผลิตน้ำมันสำเร็จรูป (11_14). catalog.eppo.go.th</div>\n      <div>Thai Oil PCL (2024) และ Star Petroleum Refining PCL (2024). Sustainability Report: environmental performance tables</div>\n      <div>สำนักงานสถิติแห่งชาติ. Statistical Yearbook 2026 ตาราง 13.5–13.8, 13.10 (พลังงาน)</div>',
  '<div>EPPO. การใช้น้ำมันในการกลั่น (11_13) · การผลิตน้ำมันสำเร็จรูป (11_14). catalog.eppo.go.th</div>\n      <div>Thai Oil PCL และ Star Petroleum Refining PCL (2024). Sustainability Report · NSO Statistical Yearbook 2026 ตาราง 13.5–13.10</div>'),
 ('.refs{display:grid;grid-template-columns:1fr 1fr;gap:.6mm 5mm;font-size:6.1pt', '.refs{display:grid;grid-template-columns:1fr 1fr;gap:.3mm 5mm;font-size:5.9pt'),
 ('<p class="limits"><b>ข้อจำกัดที่บอกตรง ๆ:</b> ยังไม่ใช่บัญชี LCI ที่ทีมเชื่อมครบทั้งวงจรเอง · “รับ” คือผ่านเกณฑ์ของทีม ไม่ได้ยืนยันฐานเวลาของข้อมูล DMF และยังไม่มีการรับรองจากภายนอก · ตัวเลขรายงานบริษัทไม่เผยแพร่ต่อเพราะยังไม่ยืนยันสิทธิ์ · Neo4j/Qdrant เป็น lab ไม่ใช่ระบบ production</p>',
  '<p class="limits"><b>ข้อจำกัดที่บอกตรง ๆ:</b> ยังไม่ใช่บัญชี LCI ที่ทีมเชื่อมครบวงจรเอง · “รับ” = ผ่านเกณฑ์ของทีม ยังไม่มีการรับรองจากภายนอก และไม่ได้ยืนยันฐานเวลา DMF · ตัวเลขรายงานบริษัทไม่เผยแพร่ (สิทธิ์ยังไม่ยืนยัน) · Neo4j/Qdrant เป็น lab</p>'),
 ('padding:2mm 9mm 3.4mm;border-top', 'padding:1.6mm 9mm 2.6mm;border-top'),
]
for a, b in pairs:
    if a not in s:
        print('MISSING:', a[:60].replace('\n', ' '))
    s = s.replace(a, b)
p.write_text(s, encoding='utf-8')
print('patched')
