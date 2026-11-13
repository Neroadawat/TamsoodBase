# ตรวจความพร้อม Release — 9 พฤศจิกายน 2569

สถานะเอกสารนี้คือ **ผลตรวจภายในสำหรับทีม** ไม่ใช่การอนุมัติจากรายวิชา ไม่ใช่การรับรอง full LCI และไม่ใช่การส่งงานแล้ว

## ผลตรวจที่ทำเสร็จ

| ส่วน | หลักฐาน/ผล | ขอบเขต |
|---|---|---|
| SRS ระบบ | `evidence/srs-current-review.json`; PDF review 27 หน้า ผูกกับ source hash ปัจจุบัน | ตรวจการ render และขอบเขตหน้า ไม่ใช่การตรวจเนื้อหาวิทยาศาสตร์หรือการรับรองจากทีม |
| เอกสารส่ง M2 | เอกสารบท 1–8 และผลตรวจรูปแบบเดิมบันทึกใน `PROJECT_STATE.md` | ยังต้องให้ทีมยืนยันชื่อ บทบาท และเนื้อหาที่จะใช้ส่ง |
| Slides | `evidence/final-slides-2026-11-09.json`; 10 หน้า ตรวจความสอดคล้องกับ SRS/evidence | ยังต้องซ้อมและรับ feedback จริง |
| Regression | `python -X utf8 -m unittest discover -s tests`: 287 ผ่าน, 7 skipped | เป็นการตรวจ code/test behavior ไม่ยืนยันความถูกต้องของแหล่งข้อมูล |
| Reference package | `build/reusable/manifest.json`, `evidence/reference-package-verification.json`; rebuild ตาม policy hash ปัจจุบัน, 101 records, 97 accepted reference, 4 hold; SQLite/SDK/package extraction และ MySQL clean restore ผ่าน โดย import ซ้ำ 2 ครั้งแล้วตรวจ 97 accepted + 101 records | ตรวจในฐานชั่วคราวแยกจากฐานใช้งาน; สคริปต์ลบฐานชั่วคราวหลังตรวจ |
| Release audit | `build/release/readiness.json` | `technical_pass=true`, `reference_release_ready=true`, `submission_ready=false`; technical/reference checks ผ่านครบ ส่วนข้อค้างเป็น official requirements, source rights, domain/time-basis, team/defense และ consent |
| LCI/FAME | `docs/fame-gate-closure-review.md`, `docs/thai-fame-completion-plan.md`, `docs/scientific-source-check-2026-11-09.md` | แหล่งที่ตรวจเพิ่มยังไม่ปิด allocation, provider compatibility, use, treatment หรือ Thai background gates; `CO2e_total` ยังคง null |

## ต้องรับจากสมาชิกจริง

- กรอกรายชื่อ/รหัส/บทบาทที่สมาชิกตกลงใน `docs/submission/MEMBER_INPUTS.md` และตรวจข้อมูลบนหน้าปก
- เพิ่ม Meeting Memo จากการประชุมจริง พร้อมวันเวลา ผู้เข้าร่วม มติ และผู้รับผิดชอบ; ห้ามใช้ memo สมมติเป็นหลักฐานประชุม
- ให้สมาชิกแต่ละคนกรอก contribution พร้อม artifact/commit/ผลที่ตรวจได้ และยืนยัน consent ตามข้อกำหนดจริง
- ซ้อม demo/defense และบันทึก peer feedback จริง; storyboard ไม่ใช่หลักฐานว่าซ้อมแล้ว
- ยืนยันประกาศล่าสุดเรื่องกำหนดส่ง ช่องทางส่ง ชื่อไฟล์ และสิทธิผู้ตรวจเข้าถึง backend
- หลังทีมเลือกชุดส่ง ให้สร้าง ERD/pipeline/export snapshot จาก release เดียวกัน แล้วตรวจ manifest/hash ใหม่ก่อน freeze

## การตัดสินใจ Release

ยัง **ไม่ freeze เป็นชุดส่ง final** เพราะยังไม่มีข้อมูลยืนยันจากสมาชิก/consent/ประกาศส่งงานล่าสุด/สิทธิใช้รายงานซ้ำครบถ้วน และ DMF time-basis/report boundary ยังมีข้อจำกัดตาม readiness audit งานที่ทำได้ใน workspace เสร็จแล้วตามรายการด้านบน; ข้อค้างที่เหลือผูกกับหลักฐานและการรับรองจากคนจริง หรือการยืนยันสิทธิ/ขอบเขตจากต้นทาง ไม่สามารถปิดอย่างซื่อสัตย์ด้วยการสร้างข้อมูลแทน

RAG/evidence-chat คงพักตามคำขอผู้ใช้ และไม่ได้เป็นส่วนหนึ่งของรายการปิดงานนี้
