"""Add the Index/EXPLAIN and transaction evidence paragraph (course requirement for 5.2/5.3/7) to the v2 book copy.

Source numbers: evidence/sql-performance.json (MySQL 8.1.0 lab, 34,899 observations, EXPLAIN ANALYZE medians)
and evidence/mysql-transaction-audit.json (synthetic isolated lab). New text is highlighted yellow like other changes.
"""
import re
import shutil
import zipfile
from pathlib import Path
from xml.dom import minidom

DOCX = Path(__file__).resolve().parents[1] / 'S2-G05_W12_A4_M4_Final_UPDATED_REVIEW_2026-11-13_v2.docx'
ANCHOR = 'ผลเทียบข้อมูลที่อ่านกลับจาก MySQL อยู่ใน evidence/live-mysql-audit.json'
HL = '<w:highlight w:val="yellow"/>'
NEW = ('Index และ Transaction (หลักฐานจากเครื่อง lab ไม่ใช่ production): ดัชนี ix_period_context บน observation(period_start, context_id) สร้างเพื่อ FR-01 ค้นตามผลิตภัณฑ์และงวด '
       'ใน MySQL 8.1.0 กับ 34,899 observation การค้นงวด 2026-01-01 (102 แถว) ใช้ Index lookup มัธยฐาน 0.208 ms เทียบ 12.0 ms เมื่อสั่ง IGNORE INDEX ให้เป็น table scan '
       'ตาม EXPLAIN ANALYZE และผลลัพธ์เท่ากัน (evidence/sql-performance.json) ด้านธุรกรรม ผลทดสอบ MySQL/InnoDB บนชุดสังเคราะห์พบว่า ROLLBACK คืนทั้งชุดคำสั่ง, CHECK กันค่าผิด (error 3819), '
       'READ COMMITTED ไม่เกิด dirty read, REPEATABLE READ เห็น snapshot คงที่, แถวที่ล็อกถูกกันเขียนทับ (lock timeout 1205) และ COMMIT ยังอยู่เมื่อเปิดการเชื่อมต่อใหม่ '
       '(evidence/mysql-transaction-audit.json) ยังไม่ได้ทดสอบกรณีไฟดับ/รีสตาร์ต และ SERIALIZABLE')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(p):
    return ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, flags=re.S))


zin = zipfile.ZipFile(DOCX)
x = zin.read('word/document.xml').decode('utf8')
if 'ix_period_context บน observation' in x:
    raise SystemExit('already patched')
m = next(m for m in re.finditer(r'<w:p[ >].*?</w:p>', x, flags=re.S) if ANCHOR in text(m.group(0)))
p = m.group(0)
head = re.match(r'<w:p[^>]*>', p).group(0)
ppr = (re.search(r'<w:pPr>.*?</w:pPr>', p, flags=re.S) or [''])[0] if re.search(r'<w:pPr>.*?</w:pPr>', p, flags=re.S) else ''
run = re.search(r'<w:r[ >].*?</w:r>', p, flags=re.S).group(0)
rpr = re.search(r'<w:rPr>.*?</w:rPr>', run, flags=re.S)
rpr = rpr.group(0) if rpr else '<w:rPr></w:rPr>'
if 'w:highlight' not in rpr:
    rpr = rpr.replace('</w:rPr>', HL + '</w:rPr>')
newp = f'{head}{ppr}<w:r>{rpr}<w:t xml:space="preserve">{esc(NEW)}</w:t></w:r></w:p>'
x2 = x[:m.end()] + newp + x[m.end():]
minidom.parseString(x2.encode('utf8'))
tmp = DOCX.with_suffix('.tmp')
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in zin.infolist():
        zo.writestr(it, x2.encode('utf8') if it.filename == 'word/document.xml' else zin.read(it.filename))
zin.close()
shutil.move(tmp, DOCX)
print('paragraph added after 5.2 evidence line')
