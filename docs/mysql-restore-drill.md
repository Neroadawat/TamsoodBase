# ทดสอบกู้คืน MySQL — 28 ตุลาคม 2569

ใช้ backup จริงจาก S3 key ที่ระบุใน `evidence/mysql-backup-latest.json` ไม่ใช้ seed ต้นฉบับแทน backup

1. EC2 ใช้ IAM role อ่าน object จาก S3 ตรวจ SHA256 และขนาดตรง manifest
2. ดึงไฟล์บีบอัดกลับพื้นที่ส่วนตัว `.local/mysql-restore-check/` และตรวจ hash ซ้ำ
3. กู้คืน dump ลง MySQL8.4 container ใหม่ `tamsoodbase-mysql-restore` บน Docker local, volume/network แยกและไม่มี published port ไม่แก้ฐาน EC2 ที่ใช้งาน
4. ตรวจข้อมูลทั้งห้าฐาน: DMF34,899/raw34,905/reference101/supplemental289/EPPO5,934 และ dataset release เดิม
5. สร้าง reader ใหม่ SELECT-only แล้วทดสอบ API จาก restored DB โดยซ่อน build/data/evidence ใน container ไม่ให้อ่าน SQLite/JSON เดิม
6. คำตอบ API 27 กรณีตรง baseline รวม export, pagination, source metadata, invalid filters และ EPPO empty-year
7. สร้าง data-only dump แบบเรียง primary key ทั้งห้าฐานจาก live และ restored แล้ว hash ตรงกันทั้ง56,887,016 bytes: `e0087e96cb3a1070acb253ee49d1db61c7cd8e4b197aab4c771ebeba06b646e1` โดยไม่แสดงข้อมูลรายแถวใน log

ผลอยู่ `evidence/mysql-restore-api-parity.json` และ `evidence/mysql-restore-drill.json` เมื่อบันทึกครบ การทดสอบนี้พิสูจน์ logical backup ของ release นี้ ไม่ได้พิสูจน์ EC2 disaster recovery ทั้งเครื่องหรือทุก backup ในอนาคต

ไฟล์ backup มีข้อมูลภายในและห้ามแจกจ่าย raw/derived ที่สิทธิยังไม่ชัด โฟลเดอร์ `.local/` ไม่ถูก commit
