# เริ่มรับช่วงงานรอบนี้

สถานะปัจจุบัน 9 พฤศจิกายน 2569 งานรับช่วงเตรียมส่งผ่าน branch `codex/teammate-runtime-handoff-2026-11-09` จากฐาน `67db1ad` ของ branch เดิม `codex/share-project-with-teammate` ให้ผู้รับ fetch แล้วเปิด branch ใหม่ที่ผู้ส่งแจ้ง ตรวจ commit/remote จริงก่อนรวมงาน ไม่ใช้การ pull branch เดิมแทนงานรอบนี้ หากใช้ ZIP ให้ตรวจฐานตาม MANIFEST ไม่ต้องนำเข้า ZIP ซ้ำหลังรับ commit เดียวกันผ่าน Git รอบนี้ไม่ deploy หรือเปลี่ยน production

เอกสารนี้เป็นจุดเริ่มรับช่วงปัจจุบัน รายงานวันที่ 8 พฤศจิกายนเก็บผลเฉพาะรอบ ไม่ใช้ข้อความว่า Corporate ขาดหรือ Docker ไม่พร้อมในรายงานเก่าแทนสถานะนี้ รอบต่อไปเน้นโค้ด/ระบบ/ข้อมูล ไม่ทำรายงานหรือสไลด์เพิ่ม

## อ่านก่อนทำ

1. `AGENTS.md` และ `PROJECT_BRIEF.md`
2. รายการล่าสุดท้าย `PROJECT_STATE.md`
3. `CODEX_PROJECT_GUIDE_TH.md` — ภาพรวมและกฎโดเมน
4. `README.md` และ `docs/rag/README.md` — dependencies และการเตรียม RAG/index
5. `docs/handoff-execution-2026-11-08.md` — ขอบเขตฐานทดลองและการเปิดระบบ
6. `docs/rag/member-validation.md` — ให้สมาชิกลองถามและประเมิน
7. `docs/explorer-performance-fix-2026-11-08.md` และ `docs/local-engineering-review-2026-11-08.md` — ประวัติผล performance/keyboard/fault checks
8. `docs/scientific-source-check-2026-11-08.md` — ผลค้นและเงื่อนไขที่ยังใช้ปิด LCI ไม่ได้

## สิ่งที่เครื่องผู้ส่งตรวจแล้ว

- Corporate: 101 รายการ, 97 ACCEPTED_REFERENCE / 4 HOLD_CONTEXT; MySQL เทียบ SQLite ครบทุกช่องใน 11 ตารางและ reference view, constraint 7 กรณีและ late rollback ผ่าน โดยข้อมูลชั้นทดลองเดิมไม่เปลี่ยน ยัง NOT_CLEARED และ normalized LCI exchanges = 0
- DMF: 34,905 raw / 34,899 candidates / 6 rejected / 34,671 deduplicated pending; NSO 273 และ FAME/H-FAME 16 จาก API ที่ตรวจแล้ว ไม่ใช่ DOM replay
- ค้น/กรอง/ส่งออก/ตรวจที่มาผ่าน HTTP 144 ครั้ง ครอบคลุม Corporate 101, DMF 34,899, NSO 273, foreground 16 และ upstream 42; ไม่เรียก Gemini หรือส่ง feedback แทนคน
- หลักฐานส่งต่อ: `evidence/handoff-corporate-mysql-2026-11-09.json`, `evidence/handoff-data-http-2026-11-09.json` และ `evidence/handoff-runtime-2026-11-08.json` ให้ดู timestamp ภายในด้วย ผลเครื่องผู้ส่งไม่ใช่ผลเครื่องผู้รับหรือ production capacity

รอบตรวจโค้ดก่อน commit แก้การตรวจ immutable store ให้เทียบ source/process/observation/card links และ schema ครบ พร้อมแก้ MySQL readiness ให้รอ TCP ของเซิร์ฟเวอร์จริงแทน socket ของช่วง bootstrap แล้ว ชุดที่เกี่ยวข้องรัน 118 tests: ผ่าน 117 และข้าม EPPO integration 1 ข้อ; ชุดทดสอบรวมทั้ง repository ยังไม่ผ่าน เพราะขาด artifacts/dependencies และหลักฐาน MySQL NSO เก่าผูกกับ report hash คนละรุ่น ดู `evidence/prepush-review-2026-11-09.json` ห้ามอ้างว่า full suite ผ่าน

## เตรียมและตรวจในเครื่องผู้รับ

ตรวจ Git status และ prerequisites ตาม README ก่อน ต้องมี Python พร้อม dependencies ของ pipeline รวม `pypdf` และ Docker Desktop Linux engine ที่พร้อมใช้งาน; RAG ใช้ environment/index แยกตาม `docs/rag/README.md` จากโฟลเดอร์ repository รัน:

```powershell
python -X utf8 scripts/prepare_handoff_runtime.py --restore-corporate --acquire-dmf-if-missing --verify-labs
```

คำสั่งใช้แหล่งสาธารณะเมื่อไฟล์ขาด และสร้างเฉพาะฐานทดลองที่มี owner marker หากมีไฟล์และ Docker images ครบแล้ว เพิ่ม `--offline` เพื่อไม่ดึงข้อมูลหรือ image ใหม่ การ acquire DMF เมื่อไม่มี snapshot จะได้รุ่น ณ เวลารัน ต้องตรวจใหม่ ไม่รับรองจำนวน/hash ตรงเครื่องผู้ส่ง ส่วน Corporate/NSO รับเฉพาะ bytes ที่ตรง hash ที่บันทึกไว้ หาก URL เปลี่ยนหรือขาด prerequisites ต้องหยุดตามจริง

ตรวจ `requested_steps_passed` และรายละเอียดแต่ละขั้นแยกจาก `full_runtime_restored`; ค่าสุดท้ายยัง false ได้เพราะ EPPO/DOM ขาด ห้ามตีความว่าระบบกู้ครบทุกแหล่ง

เปิด Explorer แล้วตรวจจากอีก terminal:

```powershell
python -X utf8 src/explorer.py
```

```powershell
python -X utf8 scripts/check_restored_data_end_to_end.py
```

เปิด `http://127.0.0.1:8765/` ผลตรวจละเอียดอยู่ `build/handoff/end-to-end-data-verification.json` สำหรับ RAG เปิดด้วย Python ใน environment ที่สร้างตามคู่มือและ `scripts/rag_retrieve.py serve --lineage`; หยุด RAG ก่อนสร้าง index หรือประเมินออฟไลน์เพราะ Qdrant Local เปิดได้ทีละ process ผลประเมินรอบใหม่ให้ใช้โฟลเดอร์เฉพาะรอบตาม README ไม่เขียนทับหลักฐานเก่า

## งานที่ต้องรับช่วงต่อ

- ตรวจโหลด/หน่วยความจำ/query plans ใน staging ที่ควบคุม workload/ทรัพยากรต่อ: คอขวด export กว้างและ metadata แก้แล้ว p95 HTTP c8 local2377.42→236.24/234.05ms สองรอบยืนยัน แต่ยังไม่กำหนด production capacity/SLA
- ให้สมาชิกลองคำถามจริงก่อนดูตัวอย่าง แล้วทบทวนผลประเมิน ไม่อ้างว่าชุดพัฒนาเป็น user study
- ให้คนจริงตรวจ screen reader/manual accessibility; keyboard flow ที่เลือกในเครื่องผ่านแล้วตามรายงาน แต่ยังไม่ใช่ UAT หรือ certification
- ตั้ง `GEMINI_API_KEY` ใน environment ฝั่งเครื่อง/เซิร์ฟเวอร์แล้วทดสอบ live; ไม่ส่งคีย์ในแชตหรือเก็บใน Git
- หา EPPO และ DOM ต้นฉบับ Table 4/article-visible ที่ยังขาด พร้อม manifest/hash รุ่นที่ถูกต้อง ห้ามใช้ข้อมูลสมมติแทน; Corporate กู้แล้วแต่สิทธิแจกจ่ายยังไม่เคลียร์
- NSO ยังเหลือ104รายการและ4divergences ต้องใช้หลักฐานนิยาม/ปี/หน่วยเพิ่มเติม ไม่เปลี่ยนค่าต้นทางให้ตรงกัน
- LCI ยังต้องปิด allocation/provider compatibility และข้อมูลเดินระบบจริง โดยเฉพาะ CH₄ คู่ยอดเอทานอลงวดเดียวกัน คงค่ารวมเป็น null จนกว่าจะพอ
- ก่อน production migration/deploy ให้ตรวจสิทธิข้อมูล stage/parity/backup/rollback และขอบเขตที่เจ้าของสั่ง ฐานทดลองรอบนี้ไม่ใช่ production
- งานส่งรายวิชายังรอทีม review/final freeze; รอบนี้ไม่ทำรายงานหรือสไลด์เพิ่ม

## ใช้ชุดไฟล์ส่งต่อ

ชุดปัจจุบันคือ `build/handoff-package/TamsoodBase-handoff-2026-11-09.zip` หรือ `.patch` ชื่อเดียวกัน ใช้อย่างใดอย่างหนึ่ง ตรวจ base commit ใน `MANIFEST.json` และ Git status ก่อนนำเข้า ถ้ามีงานแก้ค้างหรือฐานเดินต่อไปแล้วให้เทียบ diff และรวมเป็นรายไฟล์ ไม่ทับทั้งโฟลเดอร์ ชุดนี้ไม่รวม raw/build/.local/credentials ใช้ตัวเตรียมระบบกู้ข้อมูลในเครื่องผู้รับและไม่คัด runtime secrets ข้ามเครื่อง

ผลตรวจชุดส่งต่ออยู่ `build/handoff-package/VERIFICATION.json` ต้องตรงชื่อ/hash ของ ZIP และ patch ที่ส่งจริง แยกผล unit tests ในสำเนาไม่มีข้อมูลออกจาก replay ข้อมูลจริง; PDF/รายงานและ slides ไม่รวมในชุดโค้ดนี้
