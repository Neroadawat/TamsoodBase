"""On Codex's latest book (review-2026-11-15 v2): point the CSV row at the tracked copy and add a poster row to 7.1.
New/changed text is highlighted yellow like the other edits. Idempotent."""
import re
import shutil
import zipfile
from pathlib import Path
from xml.dom import minidom

DOCX = Path(__file__).resolve().parents[1] / 'review-2026-11-15' / 'S2-G05_M4_Report_REVIEW_2026-11-15_v2.docx'
HL = '<w:highlight w:val="yellow"/>'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(p):
    return ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, flags=re.S))


def rewrite(p, new):
    head = re.match(r'<w:p[^>]*>', p).group(0)
    ppr = re.search(r'<w:pPr>.*?</w:pPr>', p, flags=re.S)
    ppr = ppr.group(0) if ppr else ''
    run = re.search(r'<w:r[ >].*?</w:r>', p, flags=re.S)
    rpr = re.search(r'<w:rPr>.*?</w:rPr>', run.group(0), flags=re.S) if run else None
    rpr = rpr.group(0) if rpr else '<w:rPr></w:rPr>'
    if 'w:highlight' not in rpr:
        rpr = rpr.replace('</w:rPr>', HL + '</w:rPr>')
    return f'{head}{ppr}<w:r>{rpr}<w:t xml:space="preserve">{esc(new)}</w:t></w:r></w:p>'


zin = zipfile.ZipFile(DOCX)
x = zin.read('word/document.xml').decode('utf8')
if 'S2-G05_M4_Poster_A4_10blocks' in x:
    raise SystemExit('already patched')

# 1) CSV row path
done = False
out, last = [], 0
for m in re.finditer(r'<w:p[ >].*?</w:p>', x, flags=re.S):
    if text(m.group(0)).strip() == 'build/neo4j-csv/product_inventory.csv (ไฟล์ทดลอง)':
        out += [x[last:m.start()], rewrite(m.group(0), 'output/m4/dataset/product_inventory.csv (สำเนาชุดส่งของ build/neo4j-csv/product_inventory.csv)')]
        last = m.end()
        done = True
        break
out.append(x[last:])
x = ''.join(out)
print('csv path row:', done)

# 2) poster row cloned from the slides row
rows = list(re.finditer(r'<w:tr[ >].*?</w:tr>', x, flags=re.S))
target = next(r for r in rows if 'สไลด์พรี 3 นาที' in text(r.group(0)))
tr = target.group(0)
cells = list(re.finditer(r'<w:tc>.*?</w:tc>', tr, flags=re.S))
new = ['โปสเตอร์ A4 (10 บล็อก)', 'output/m4/S2-G05_M4_Poster_A4_10blocks.pdf (และ .html)',
       '1 หน้า A4 แนวตั้ง ครบ 10 บล็อกตามแนวทางของวิชา ใช้ผลจริงของทีม; ผล SQL Q1–Q2 และ DMF ตรวจบน MySQL 8.4 ฐานทดลองแยก (ไม่ใช่ EC2); ตัวอักษรเล็ก 6–7 pt ควรลองพิมพ์ก่อนส่ง']
newtr = tr
for c, nt in zip(cells, new):
    cp = c.group(0)
    pm = re.search(r'<w:p[ >].*?</w:p>', cp, flags=re.S)
    newtr = newtr.replace(cp, cp.replace(pm.group(0), rewrite(pm.group(0), nt)), 1)
x = x[:target.end()] + newtr + x[target.end():]
minidom.parseString(x.encode('utf8'))
tmp = DOCX.with_suffix('.tmp')
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in zin.infolist():
        zo.writestr(it, x.encode('utf8') if it.filename == 'word/document.xml' else zin.read(it.filename))
zin.close()
shutil.move(tmp, DOCX)
print('poster row added')
