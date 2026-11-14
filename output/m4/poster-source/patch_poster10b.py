"""Second tightening pass: QR into block 10, drop footer, trim blocks 4/7."""
from pathlib import Path
import re

p = Path(__file__).parent / 'poster10.template.html'
s = p.read_text(encoding='utf-8')

# remove footer element, move QR into block 10
s = re.sub(r'<footer class="foot">.*?</footer>\n', '', s, flags=re.S)
s = s.replace('<h2><i>10</i>References<small>แหล่งในทะเบียน docs/source-registry.csv</small></h2>\n    <div class="refs">',
              '<h2><i>10</i>References<small>แหล่งในทะเบียน docs/source-registry.csv</small></h2>\n    <div class="refwrap"><div class="refs">')
s = s.replace('IPCC SR15 Glossary</div>\n    </div>\n  </section>',
              'IPCC SR15 Glossary</div>\n    </div>\n    <div class="qr"><span><b>tamsoodbase.vercel.app</b>เปิดเว็บ · ลองถามผู้ช่วย</span>%%QR%%</div></div>\n  </section>')
s = s.replace('</style>', '.refwrap{display:grid;grid-template-columns:1fr auto;gap:4mm;align-items:center}\n</style>')
pairs = [
 ('<span>HAS_EXCHANGE</span><span>OF_FLOW</span><span>FROM_SOURCE</span>', '<span>HAS_EXCHANGE</span><span>OF_FLOW</span>'),
 ('CSV จาก Table 4 ของงานวิจัย: <b>16 แถว · 32 คอลัมน์ · มี source_id</b> → Neo4j 5.26 ใน container ชั่วคราว',
  'CSV จาก Table 4 ของงานวิจัย <b>16 แถว · 32 คอลัมน์ · มี source_id</b> → Neo4j 5.26 (container ชั่วคราว)'),
 ('<p class="note" style="margin-top:.5mm"><b class="r">ยังไม่ทดสอบ:</b> ไฟดับ/รีสตาร์ต · SERIALIZABLE · โหลดจริง (evidence/mysql-transaction-audit.json)</p>',
  '<p class="note" style="margin-top:.4mm"><b class="r">ยังไม่ทดสอบ:</b> ไฟดับ/รีสตาร์ต · SERIALIZABLE · โหลดจริง</p>'),
 ('<li><b>C</b> CHECK/FK กันค่าผิด (error 3819)</li>', '<li><b>C</b> CHECK/FK กันค่าผิด (3819)</li>'),
 ('<li><b>D</b> COMMIT ยังอยู่เมื่อเปิดการเชื่อมต่อใหม่</li>', '<li><b>D</b> COMMIT ยังอยู่เมื่อต่อใหม่</li>'),
 ('<p class="note">+ <code>rejected_record</code> · 4 schema: research · reusable · supplemental · eppo · <b class="r">ข้อยกเว้นตั้งใจ:</b> raw_value คู่ amount เพื่อ audit จึงไม่อ้าง 3NF ทุก relation</p>',
  '<p class="note">+ <code>rejected_record</code> · 4 schema · <b class="r">ข้อยกเว้นตั้งใจ:</b> raw_value คู่ amount เพื่อ audit จึงไม่อ้าง 3NF ทุก relation</p>'),
 ('<b>ผลค้น:</b> คะแนนอย่างเดียว (cutoff 0.45) 10/12 และปฏิเสธถูก 6/8 → เพิ่มกฎขอบเขต <span class="ok">12/12 และ 8/8</span>',
  '<b>ผลค้น:</b> คะแนนอย่างเดียว (0.45) 10/12 และปฏิเสธถูก 6/8 → เพิ่มกฎขอบเขต <span class="ok">12/12 · 8/8</span>'),
 ('<p class="note">kg CO₂ eq · Well-to-Wheels · ตาราง 5 · <b class="r">ยังไม่ปิด:</b> LCI ครบวงจร → CO₂e รวมของทีมไม่คำนวณ · ฐานเวลา DMF · สิทธิ์ข้อมูล</p>',
  '<p class="note">kg CO₂ eq · Well-to-Wheels · ตาราง 5 · <b class="r">ยังไม่ปิด:</b> LCI ครบวงจร (CO₂e รวมของทีมไม่คำนวณ) · ฐานเวลา DMF · สิทธิ์ข้อมูล · “รับ” ยังไม่ใช่การรับรองจากภายนอก</p>'),
]
for a, b in pairs:
    if a not in s:
        print('MISSING:', a[:60])
    s = s.replace(a, b)
p.write_text(s, encoding='utf-8')
print('ok')
