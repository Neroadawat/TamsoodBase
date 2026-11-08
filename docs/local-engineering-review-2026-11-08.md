# ตรวจวิศวกรรมในเครื่องก่อนส่งต่อ — 8 พฤศจิกายน 2569

**สถานะข้อมูลใหม่กว่า:** Corporate กู้และตรวจแล้ว ดู [คู่มือปัจจุบัน](TEAMMATE_NEXT_STEPS_TH.md) ข้อความ reference unavailable และผล tests ด้านล่างเป็นของรอบที่ระบุ ไม่ใช่ข้อค้างล่าสุด

**ผลต่อจากรายงานนี้:** พบและแก้คอขวด export/metadata พร้อม all-row parity และ HTTP ยืนยันสองรอบแล้ว ดู [ผลแก้ล่าสุด](explorer-performance-fix-2026-11-08.md) ตัวเลขด้านล่างเป็นก่อนแก้คอขวด ไม่ใช่ผลล่าสุดหรือ production SLA

รอบนี้ทำส่วนที่ตรวจได้ของ T109/T114: แป้นพิมพ์และ focus, คำขอพร้อมกันอย่างจำกัด, หน่วยความจำของ process, query plans และการกู้สถานะเมื่อบริการล้มเหลว งานทั้งสองยังเป็น IN_PROGRESS เพราะการตรวจ production, screen reader/UAT โดยคนจริง และประตูวิทยาศาสตร์ยังไม่ครบ ไม่มี commit/push/deploy รอบนี้

## สิ่งที่แก้และตรวจแล้ว

- หน้า RAG มีลิงก์ข้ามไปคำถาม, focus ที่มองเห็น, Ctrl+Enter, สถานะสำหรับเทคโนโลยีช่วยอ่าน และชื่อคำถามที่ส่งจริง ปิดการแก้คำถาม/ปุ่มตัวอย่างระหว่างรอเพื่อไม่ให้คำถามบนจอกับผลค้นเหลื่อมกัน
- คำขอค้นเกิน 12 วินาทีจะยกเลิกฝั่งหน้าเว็บและคืนปุ่มให้ใช้ต่อ ทั้งกรณี HTTP 503 และ timeout ตรวจผ่านเบราว์เซอร์จริงกับบริการจำลองในเครื่อง ไม่ส่ง feedback แทนสมาชิก การยกเลิกฝั่งหน้าเว็บไม่ได้รับรองว่า computation ฝั่งเซิร์ฟเวอร์ถูกยกเลิกด้วย
- เซิร์ฟเวอร์ในเครื่องทั้ง Explorer/RAG กำหนดคิวรับการเชื่อมต่อ 32 และ read timeout 5 วินาทีตั้งแต่รับ socket จึงไม่ปล่อย header ที่ส่งไม่ครบค้างไม่มีกำหนด RAG ยังคงประมวลผลทีละคำขอ ไม่เปลี่ยนเป็น inference พร้อมกัน
- เพิ่มดัชนี SQLite 3 ตัวตาม filter/ลำดับจริงของ Explorer และใส่ในขั้นสร้าง DMF รอบถัดไป ตรวจสำเนาก่อนใช้กับฐาน local; fingerprint ทุกแถวของ resource/staging/candidate/rejected/duplicate_disposition ตรงเดิม ผล query และลำดับแถวตรงเดิม รวมทั้ง integrity_check ผ่าน รัน pipeline ออฟไลน์จาก snapshot จริงแล้วข้อมูลยังตรง hash เดิม
- จำกัด embedding ที่ 2 threads หลังทดลองใน process แยก: 10 batches × 3 คำถาม ใช้เวลา 14,123 → 1,336 ms ในการทดลองนี้; vector ตัวอย่างต่างสูงสุด 0.0 ไม่ใช้ตัวนับ CPU ของ Windows เป็นข้ออ้างเรื่องประหยัดพลังงาน คำถาม regression ทั้ง 4 ชุดยังผ่าน 47 positive + 51 negative; อีก 4 ambiguous ไม่ให้คะแนน ไม่ใช่ independent evaluation หรือการรับรองคำตอบ Gemini

## Query plans และเวลา SQL

วัด 25 ครั้งต่อ query บนสำเนา local ที่ warm cache; เมื่อตรวจซ้ำจะถอดเฉพาะดัชนี 3 ตัวนี้ในสำเนาชั่วคราวก่อนวัด baseline ไม่ถอดดัชนีจากฐานใช้งาน ผลรอบสุดท้าย:

| Query | แถว | median ก่อน (ms) | median หลัง (ms) |
|---|---:|---:|---:|
| หน้า records ไม่กรอง | 30 | 121.558 | 0.269 |
| หน้า records กรอง product/year | 30 | 14.143 | 0.292 |
| export กรอง product/year | 375 | 8.778 | 2.212 |

แผนหลังเพิ่มดัชนีไม่ต้องสร้าง temporary B-tree เพื่อเรียงแถวใน 3 query นี้ ตรวจ MySQL/Neo4j lab ที่มี owner marker แบบ read-only เพิ่ม: observation ใช้ PRIMARY, ช่วงเวลา DMF ใช้ ix_period_context, graph lookup ใช้ IndexSeek ทั้งหมดเป็นฐานทดลองในเครื่อง ไม่ใช่แผนของ production

## คำขอพร้อมกันและหน่วยความจำ

ทดสอบเฉพาะ 127.0.0.1:8765/8767 ที่ concurrency 1/4/8 ระดับละ 24 คำขอต่อบริการ รวม 144 ต่อรอบ ทุกคำขอทั้ง 5 รอบได้สถานะ/ผลตามคาด รวมการปฏิเสธ export กว้างด้วย 400 และคำถามนอกขอบเขตด้วยผลว่าง ไม่ใช่ทุกคำขอจะต้องเป็น HTTP 200

| บริการ | p95 ก่อน c1/c4/c8 (ms) | p95 รอบสุดท้าย c1/c4/c8 (ms) |
|---|---|---|
| Explorer | 206.43 / 198.37 / 597.03 | 138.84 / 709.27 / 1383.43 |
| RAG | 32.71 / 33.50 / 509.75 | 43.01 / 147.76 / 300.83 |

**ยังอ้างไม่ได้ว่า HTTP เร็วขึ้นทั้งระบบ** แม้ SQL ดีขึ้นชัด รอบ Explorer c4/c8 ช้ากว่า baseline; ระหว่างรอบมีความผันผวนและมีการ restart process ควรหาสาเหตุและวัดซ้ำใน staging ที่ควบคุมสภาพก่อนกำหนด performance budget หรือรับโหลดจริง ไม่สรุปสาเหตุว่าเป็น network/Windows โดยยังไม่ได้พิสูจน์

PeakWorkingSet64 หลัง c8 รอบสุดท้าย: Explorer 76,296,192 bytes (~72.8 MiB), RAG 679,030,784 bytes (~647.6 MiB) เป็น peak ตลอดอายุ process รวมโมเดล/งานก่อนหน้า ไม่ใช่ peak เฉพาะช่วงทดสอบหรือการตรวจ memory leak และไม่ใช้ตั้งขนาดเครื่อง production

## แป้นพิมพ์และการรับมือข้อผิดพลาด

ตรวจผ่าน IAB ด้วยแป้นพิมพ์จริงใน flow ที่เลือก: RAG skip link → ช่องคำถาม → Ctrl+Enter → focus สถานะ → Tab ไปต้นทาง; Explorer skip link → เครื่องมือหลัก, Enter เปลี่ยนหน้า, เปิดรายละเอียดแถว, Tab ภายใน native dialog และ Escape คืน focus ไปปุ่มเดิม การตรวจชื่อ controls ในหน้า DMF ที่โหลดพบว่าไม่มีชื่อว่างตาม heuristic ที่ใช้ ไม่ใช่ผล axe audit ใหม่หรือการรับรองทั้งเว็บ

Proxy fault simulation 12 คำขอเหลื่อมกัน: deadline 4, client disconnect 4, success 4; ไม่ยกเลิกข้ามคำขอ, ไม่จบ response ซ้ำ และเพิกเฉย late callbacks 8 ครั้ง ตรวจ socket จริงเพิ่มด้วย header ไม่ครบและ timeout แบบย่อใน fixture แล้วคำขอถัดไปใช้ได้ ข้อนี้ไม่ใช่ chaos test ของ production หรือการเรียก upstream จริง

ผลตรวจรอบสุดท้าย: runtime 9, scope 6, HTTP resilience 1, frontend 13 tests ผ่าน; proxy behavior เดิมและ fault fixture ใหม่ผ่าน; HTTP RAG 19, lineage/integration 14 และ Explorer 9 checks ผ่าน ข้อมูลชั้น corporate reference/EPPO ยัง 503 ตามสภาพ snapshot ที่ขาด ไม่ปิดว่า available ครบ

## หลักฐานและวิธีตรวจซ้ำ

- `evidence/local-keyboard-review-2026-11-08.json`: สิ่งที่สังเกตจากเบราว์เซอร์และข้อจำกัด ไม่มี feedback ของคนจริง
- `evidence/local-query-plans-2026-11-08.json`, `evidence/local-engine-query-plans-2026-11-08.json`
- `evidence/local-load-{before,after,current,tuned,final}-2026-11-08.json`: เก็บทุกช่วง รวมผลที่ช้าลง
- `evidence/local-embedding-threads-2026-11-08.json`, `evidence/rag-engineering-*-2026-11-08.json`
- `evidence/local-proxy-faults-2026-11-08.json`, `evidence/rag-expanded-http-2026-11-08.json`, `evidence/handoff-integration-2026-11-08.json`, `evidence/handoff-explorer-2026-11-08.json`

เปิด runtime ตาม `docs/handoff-execution-2026-11-08.md` ก่อน แล้วเลือกตรวจตามส่วนที่เปลี่ยน ไม่รัน load ต่อ production:

```powershell
python -X utf8 scripts/audit_local_query_plans.py
python -X utf8 scripts/audit_handoff_engine_plans.py
python -X utf8 scripts/benchmark_local_review.py --label current
python -X utf8 -m unittest discover -s tests -p test_rag_http.py -v
node tests/proxy-concurrent-faults.cjs
```

Thread profiler และ CLI evaluation ต้องหยุด RAG ที่เปิด Qdrant Local เดียวกันก่อน ใช้ Python จาก `build/rag-verified-venv/Scripts/python.exe`; คำสั่ง profiler ใช้โมเดล cache เท่านั้น ไม่ดาวน์โหลดใหม่

## งานที่ส่งต่อ

1. สืบ HTTP latency ของ Explorer และวัด staging ด้วย workload/ข้อมูล/ทรัพยากรที่คงที่ ก่อนสรุปความเร็ว ความจุ หรือ SLA; เก็บ memory ระยะยาวและ query plans จาก environment เป้าหมาย
2. คนจริงลองใช้และให้คำถามอิสระ รวม screen reader/manual accessibility และรับรองงานสมาชิกตามจริง ไม่ใช้ browser automation แทน UAT
3. คีย์ Gemini/live validation, snapshots ที่ขาด, NSO 104 รายการ/4 divergences, scientific allocation/provider/matched operating data และ stable endpoint ยังเปิดตาม `docs/TEAMMATE_NEXT_STEPS_TH.md`
4. ก่อน production migration/deploy ยังต้อง scope/identity/สิทธิ/backup/rollback จริง ชุด source ZIP รอบใหม่ไม่มี raw/runtime/secrets
