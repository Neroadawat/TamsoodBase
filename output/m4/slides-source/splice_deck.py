"""One-off: drop the pipeline slide, insert ERD + SQL slides (new_blocks.js), fix notes timing."""
from pathlib import Path

here = Path(__file__).parent
p = here / 'build_slides_3min.js'
s = p.read_text(encoding='utf-8')
if 'ERD + key design decisions' in s:
    raise SystemExit('already spliced')
a = s.index('// ───────── 3 · How data travels')
b = s.index('// ───────── 4 · Demo slide')
s = s[:a] + s[b:]
c = s.index('// ───────── 5 · Results')
s = s[:c] + (here / 'new_blocks.js').read_text(encoding='utf-8') + s[c:]
rep = [
    ('// 7 main slides + 2 backup slides for Q&A (9 total, within the 10-slide limit).',
     '// 8 main slides + 2 backup slides for Q&A (10 total = course limit). Covers ERD + SQL (W15 demo steps 5-6).'),
    ('[0:10–0:35 · 25 วินาที] MTEC', '[0:10–0:35 · 25 วินาที แล้วพูดว่า ต่อไปดูของจริง 5 นาที] MTEC'),
    ('[หลังคลิป · 0:00–0:40] สรุปตัวเลข', '[หลังคลิป · 1:00–1:25 · 25 วินาที] สรุปตัวเลข'),
    ('[หลังคลิป · 0:40–1:20] เราแยก', '[หลังคลิป · 1:25–1:55 · 30 วินาที] เราแยก'),
    ('[หลังคลิป · 1:20–2:00] ก้าวต่อไป', '[หลังคลิป · 1:55–2:10 · 15 วินาที] ก้าวต่อไป'),
    ('[1:00 → เปิดคลิป 5 นาที]', '[0:35 → เปิดคลิป 5 นาที]'),
]
for old, new in rep:
    if old not in s:
        print('MISSING', old[:30])
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('ok; slide blocks =', s.count('const s = '))
