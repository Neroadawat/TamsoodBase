## ผลตรวจล่าสุด27ตุลาคม — source cells และ normalization

ดู [รายงานรอบFinal](source-normalization-audit-2026-10-27.md): replayทุกชั้นผ่าน/PDF101สกัดซ้ำจริง;directcell41223รายการไม่มีmismatch;7SQLiteintegrity/FKผ่าน;105testsหลังแก้emptyyearEPPO ข้อความ24ตุลาคมด้านล่างเป็นประวัติ ไม่ใช่สถานะEC2/S3ล่าสุด

# ตรวจทั้งกระบวนการ — 24 ตุลาคม 2569

## ตรวจเพิ่มเติมคืน 24–25 ตุลาคม

พบและแก้ช่องโหว่ในตัวตรวจสองจุด ไม่ใช่การพบว่าข้อมูลจริงเสีย:

- SQLite audit เคยเลือกเฉพาะ observation ID ที่อยู่ใน report ทำให้แถวส่วนเกินไม่ถูกตรวจ ตอนนี้ NSO/inventory เทียบทั้งตาราง ส่วน EPPO เลือกทั้ง snapshot ปัจจุบัน จึงยังเก็บประวัติ snapshot เก่าได้โดยไม่ซ่อนแถวส่วนเกินของรุ่นปัจจุบัน
- EPPO import เคยตรวจเพียง amount/unit/payload หลัง commit ตอนนี้ตรวจ snapshot metadata และทุก typed column รวมปี เดือน ชื่อรายการ ก่อน commit หากไม่ตรงให้ rollback และปิด connection โดยไม่เขียน report สำเร็จ

ผลตรวจ: 90 tests ผ่าน ไม่มี skip; read-only layer audit 29 checks ผ่าน; EPPO 5,934 แถวและ metadata ตรงครบ การ replay ทั้ง pipeline ผ่าน DMF raw34,905/candidate34,899/reject6/pending34,671, NSO273, inventory16 และ reference API101/accepted97/hold4 ฐาน DMF เดิมไม่เปลี่ยน hash รอบนี้ไม่ได้สกัด PDF ซ้ำ ไม่ตรวจ MySQL live ซ้ำ และไม่เปลี่ยนเว็บหรือ image ที่ตรวจไว้ก่อนหน้า

หลักฐานเพิ่มเติม `evidence/system-integrity-followup.json` และ `evidence/pipeline-audit.json` การตรวจนี้ไม่ยืนยัน EC2 รุ่นใหม่/S3/public deployment และไม่ใช่การรับรอง 5NF

รอบนี้ตรวจจาก snapshot ที่มีจริง ไม่ดาวน์โหลดทับต้นฉบับ ไม่เพิ่มจำนวนข้อมูล และไม่เปลี่ยน acceptance/rights การสร้างผลซ้ำใช้โฟลเดอร์ชั่วคราวแยกจากฐานที่เว็บอ่าน

## ผลตรวจ

| ขั้นตอน | สิ่งที่ตรวจจริง | ผล |
|---|---|---|
| รับข้อมูล DMF | manifest ครบ 3 packages ไม่ซ้ำ, run ID, hash, byte count, metadata package/resource identity, CSV header/encoding | ผ่าน และเพิ่ม preflight ก่อนเริ่มเขียน build |
| DMF raw → staging → candidate/reject → duplicate review | สร้างใหม่ใน temporary workspace เทียบทุกคอลัมน์ของ 5 ตาราง และ quality/review report ทั้งฉบับ | raw 34905; candidate 34899; reject 6; pending หลัง dedup 34671 ตรงเดิม; live DB hash ไม่เปลี่ยน |
| รายงานบริษัท → reference → API | สกัดซ้ำจาก PDF 101 ค่า, ตรวจ scaling/context/status, เทียบ API export ทุก field กับ artifact | 101 ต้นทาง / 97 รับอ้างอิง / 4 พัก ตรงเดิม |
| NSO/EPPO/งานวิจัย | parse CSV/DOM ต้นทางใหม่ เทียบ report payload ทุกแถว และเซลล์ที่แยกออก | NSO273 / EPPO5934 / inventory16 / excluded BHD8 ตรงเดิม; NSO additive18 ผ่าน |
| SQLite | integrity/FK, JSON payload และ typed columns ที่ใช้ค้น/แสดงผลแยกกัน; process basis ของ inventory | ผ่าน |
| MySQL ที่รันจริงในเครื่อง | SELECT ใน READ ONLY transaction; DMF rawJSON34905, candidate typed34899, disposition34899, context fields/reject reasons; corporate catalog30fieldsครบ101; supplemental parent/subtype/process typed+payload289; EPPOtyped+payload5934 | ผ่าน ไม่แก้ schema หรือข้อมูลเดิม |
| Normalization candidate บน MySQL | สร้างฐานทดลองแยกtamsood_nf_c4a3f824c950;catalogทุกช่อง101/accepted97ตรง;4negativeconstraintchecks | ผ่าน ไม่สลับฐานproduction;ยังไม่อ้าง5NF |
| Backend readiness | เปิดอ่าน DMF database/reports, current reference release และ JSON datasets จริง | พร้อมในเครื่อง; ไม่ใช่หลักฐานว่า EC2 อัปเกรดแล้ว |
| หน้าเว็บ | browser กรอง HOLD ได้4, เปิดหลักฐานหน้า49และหน่วยm3/year, releaseล่าสุด; ค้น161ตัวอักษรให้ error โดย rowsว่าง/exportไม่มีhref/pagerปิด | ผ่าน; เพิ่ม tests จัดลำดับ async request ของ3หน้าค้นหา |
| Docker backend image | buildจากarchiveallowlist35ไฟล์ที่ตรวจSHA;Gunicorn13routes;UID10001,read-only,networknone,ไม่มีpublishedport;ลบเฉพาะtemporarycontainerที่สร้างเองเมื่อจบ | ผ่าน;image local-57ad16e4a4e8f790;ยังไม่อัปเกรดEC2 |

## สิ่งที่แก้

- `process_dmf.validate_snapshot`: ไม่เชื่อเพียง complete=true เมื่อ manifest ขาด package หรือ package ซ้ำ ตรวจ source ทุกไฟล์ก่อนเริ่ม build; จำกัดปีตามช่วงที่ระบบรองรับ1900–2100
- `audit_dataset_layers`: เดิม JSON อาจตรงแต่ typed amount/unit/year ผิดแล้วหลุดการตรวจได้ ตอนนี้ตรวจแยกกัน รวม process basis/geography
- `/readyz`: เดิมแค่มี manifest ก็อาจบอกพร้อมทั้งที่ไม่มี DMF database ตอนนี้เปิดอ่านฐาน/current release จริงและตอบ503เมื่อใช้ไม่ได้
- หน้าเว็บ: ล้างผลเก่าระหว่างโหลด ปิด export/pager จนสำเร็จ และไม่ให้ error จาก request เก่าทับ request ใหม่ แสดงข้อความคำค้นยาวเป็นภาษาไทย
- Normalization candidate: เปลี่ยน assert สำคัญเป็น explicit validation เพื่อไม่ให้ถูกข้ามด้วย `python -O` และตรวจ integrity ของ source ก่อนคัดลอก
- Task board: เพิ่ม T38 ลง `tasks.json` ซึ่งเป็นแหล่งหลัก (ก่อนหน้านี้เพิ่มแค่ Markdown) แล้ว generate ใหม่; release audit ตรวจว่า Markdown ตรงกับ JSON

## ทำซ้ำ

```powershell
python -X utf8 scripts/audit_pipeline.py
python -X utf8 scripts/audit_pipeline.py --pdf
python -X utf8 scripts/audit_live_mysql.py
python -X utf8 -m unittest discover -s tests
python -X utf8 scripts/check_release.py
```

ใช้ `--pdf` เมื่อต้องสกัดซ้ำจริงและ environment มี pypdf; เครื่องนี้ใช้ bundled Python ที่มี pypdf การรันแบบไม่ใส่ --pdf บันทึกยอด PDF ที่สกัดซ้ำรอบนั้นเป็น0อย่างตรงไปตรงมา ไม่สวมผลเก่ามารวม ห้ามรันซ้ำเรื่อย ๆ เมื่อไม่มีการเปลี่ยนแปลงหรือข้อกังวลใหม่

หลักฐาน: `evidence/pipeline-audit.json`, `evidence/live-mysql-audit.json` และ `evidence/pipeline-ui-audit.json` ผล replay เป็นการตรวจ reproducibility ด้วย parser เดิม ไม่ใช่การวัดอิสระจากหน่วยงานต้นทาง

Dockerหลักฐานเพิ่มเติม: `evidence/backend-image-audit.json` / คำสั่ง `python scripts/verify_backend_image.py` ต้องมีแพ็กเกจจาก `scripts/package_backend.py` ก่อน จะ buildเฉพาะarchiveที่ตรวจhash ไม่buildจากrepoทั้งโฟลเดอร์ จึงไม่ลากraw/credentialsอื่นเข้าภาพcontainer

ผลชุดทดสอบรวมหลังแก้: 81 tests ผ่านบนเครื่องนี้ ไม่มี skip รวม regression ของ source preflight, corruption ใน typed columns โดย JSON ยังเดิม, source locator ที่ถูกแก้, readiness เมื่อฐานหาย และ async stale-error ของหน้าDMF/reference/EPPO

## สิ่งที่ยังค้างจริง

- Normalization candidate ยังไม่แทนฐาน production; ยังไม่รับรอง5NF
- โค้ด readiness/เว็บที่แก้รอบนี้ยังอยู่ local ไม่ได้อัปเกรด container EC2 เดิม; S3 ยังไม่มี bucket/role
- T30 ล่าสุดขยายเป็น15distinctค่า (DEDErevised total1+subtotal5;DOEB9) อีก258ยังไม่เทียบ ดูnso-source.md ไม่ถือ republication เป็น independent measurement
- historical DMF time basis, สิทธิแจกจ่ายรายงานบริษัท และข้อกำหนดส่งล่าสุดยังมีข้อจำกัดตามเอกสารเดิม
- contribution/individual defense ต้องมาจากมนุษย์จริง ไม่มีการกรอกแทนหรือ freeze รุ่นส่งในรอบนี้
