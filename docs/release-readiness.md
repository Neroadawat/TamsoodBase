# ตรวจความพร้อมและแพ็กเกจภายใน

```powershell
python -X utf8 scripts/check_release.py --tests
python -X utf8 scripts/task_board.py
```

ตัวตรวจอ่านฐาน SQLite แบบ read-only ตรวจ hash ต้นฉบับ DMF/รายงาน, row accounting, report identities, สถานะไม่ promote อัตโนมัติ, หลักฐาน MySQL ที่ผูกกับ hash รายงาน และ dependency ของ task board ส่วน --tests รัน unit/integration tests ที่มีในเครื่อง

ผลอยู่ build/release/readiness.json และ source-manifest.json โดย technical_pass กับ submission_ready แยกกัน จึงแสดงว่าระบบตรวจผ่านได้ทั้งที่ยังไม่พร้อมส่ง

เพิ่ม reference_release_ready สำหรับชุดข้อมูลพร้อมอ้างอิงตามนโยบายทีม โดยตรวจ source/code/schema/export hashes, ผล MySQL roundtrip และหลักฐานแพ็กเกจที่รัน client แยกจาก repo/restore ลง database ว่างแล้ว ค่านี้ไม่ต้องรอคำยืนยัน MTEC และแยกจาก readiness ของการส่งงานทั้งรายวิชา

ประตู final อยู่ docs/review-decisions.json ประตูที่ยังไม่ VERIFIED ต้องรายงานข้อค้าง ส่วน VERIFIED ระดับทีมไม่ใช่การอนุมัติภายนอก การเปลี่ยนสถานะต้องอ้างไฟล์หลักฐานที่มีจริงและตรวจความหมายด้วย การมีไฟล์หรือ checksum ตรงเพียงอย่างเดียวไม่ใช่การรับรองจาก MTEC

ถ้าต้องการสำเนาภายในเพื่อ review ใช้ `python -X utf8 scripts/check_release.py --package` ได้เมื่อ technical checks ผ่าน จะสร้าง build/release/internal-review.zip พร้อม manifest ภายใน archive แต่ไม่ส่งหรือเผยแพร่อัตโนมัติ และไม่ใช่ final submission

แพ็กเกจใช้ allowlist เฉพาะ code/docs/SQL/evidence กับ README และการตั้งค่า VS Code ตัด .local, .env, raw data, PDF, generated databases และ symlinks ออกโดยโครงสร้าง ไม่มี credentials หรือไฟล์ lecture อยู่ในแพ็กเกจ สิทธิของ derived evidence ยังต้องพิจารณาก่อนเผยแพร่เช่นกัน

ขอบเขตที่ตรวจเสร็จแล้ว เช่น re-extraction ครบ 101 และ isolated client/fresh database restore ให้ดูหลักฐานเฉพาะงานใน task board; readiness check ไม่แทนการตรวจสิทธิในรูปแบบเผยแพร่ การตรวจต้นฉบับ DMF ทั้งชุด หรือ individual defense จริง
