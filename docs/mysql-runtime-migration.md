# MySQL runtime — 28 ตุลาคม 2569

Backend ส่วนตัวบน EC2 เปลี่ยนมาอ่าน MySQL 8.4 จริงแล้ว รุ่น `dea667bbd79dc1d9` แทน `00c68ca585cf0220` ไม่ใช่เพียงส่งออกไฟล์ SQL และไม่ต้องเพิ่ม Supabase

## โครงสร้างที่ใช้งาน

- API: `tamsoodbase-api`, เปิดเฉพาะ `127.0.0.1:8765`, ผู้ใช้ container 10001, read-only filesystem
- MySQL: `tamsoodbase-mysql-runtime`, volume `tamsoodbase-mysql-runtime-data`, จำกัด RAM 512 MB ไม่มี host/public port
- network ภายใน: `tamsoodbase-mysql-runtime-private`; API มี bridge เดิมด้วยเพื่อใช้ instance-role/S3
- ฐาน typed: `tamsood_research`, `tamsood_reusable`, `tamsood_supplemental`, `tamsood_eppo`
- `tamsood_api`: projection views, metadata, ลำดับแสดงผล และข้อความต้นฉบับ เพื่อรักษารูปแบบ API/ทศนิยมเดิม การค้นและ JOIN ใช้ตาราง typed
- API ใช้บัญชี SELECT เท่านั้น ไม่ได้รับ root credential และไม่มีการ fallback ไป SQLite หาก MySQL เสีย

ข้อมูล DMF 34,899 รายการ, raw staging 34,905, corporate reference 101 (accepted 97/hold 4), NSO 273, inventory 16, EPPO 5,934 โหลดเข้า MySQL แล้ว ประเภทและสิทธิข้อมูลเหมือนเดิม ไม่ยกระดับ statistics/reference เป็น normalized LCI

## หลักฐาน

- `evidence/ec2-upgrade.json`: ตรวจ staging และ active 17 routes, S3 IAM-role และบริการอื่นไม่เปลี่ยน
- `evidence/ec2-mysql-runtime.json`: schema counts, persistent volume และไม่เปิดพอร์ต
- `evidence/mysql-api-parity.json`: API 27 กรณีตรงกับ SQLite baseline หลัง canonical JSON; มี pagination, literal search, export, detail, invalid filters, EPPO empty-year
- local MySQL API ถูกทดสอบโดย mount พื้นที่ build/data/evidence ว่าง จึงอ่านไฟล์ SQLite/JSON เดิมไม่ได้ ยังผ่าน parity
- reader บน EC2 ถูกปฏิเสธ UPDATE ด้วย MySQL error 1142; ชุด unit tests 109 ข้อผ่าน

พบและแก้ detail query ที่เลือก raw_json ซ้ำ ซึ่ง PyMySQL จะเพิ่มชื่อคอลัมน์ `s.raw_json` ต่างจาก SQLite

นี่ไม่ใช่การพิสูจน์ 5NF ทั้งระบบ มี representation JSON เพื่อรักษา API และ source evidence; schema normalization และข้อจำกัดต้องอธิบายแยกตาม entity

## สำรองและย้อนกลับ

`deploy/backup_mysql.py` สร้าง logical dump ของทั้งห้าฐานด้วย single transaction แล้วอัปโหลด private S3 พร้อม AES256/checksum ใช้ instance role ผ่าน API ไม่ส่ง root credential เข้า API ผลจริงดู `evidence/mysql-backup-latest.json` เมื่อมีไฟล์นั้น การมี dump ไม่เท่ากับทดสอบ restore สำเร็จ ให้ยึดฟิลด์ restore_tested ตามจริง

บริการเก่าเก็บเป็น `tamsoodbase-rollback-00c68ca585cf0220` และ env ก่อนเปลี่ยนอยู่บน EC2 ที่ `backend.env.before-dea667bbd79dc1d9` การ rollback ต้องคืนทั้ง container และ env ด้วยเครื่องมือ rollback ของโครงการ ไม่ลบ MySQL volume ห้ามแตะบริการ Ginder/Caddy

Seed และ credential อยู่ใน private `.local/` / โฟลเดอร์ EC2 `mysql-runtime/` ห้าม commit หรือแจกไฟล์เหล่านี้

## ยังเหลือสำหรับเปิดให้คนอื่นใช้

Frontend ยังไม่ publish Vercel ขณะนี้มี HTTPS ชั่วคราวพร้อมรหัสทุก route สำหรับเปิดเว็บจาก EC2 origin เดียวกันแล้ว ดู `HTTPS_TEST_TH.md` การเชื่อม Vercel ข้าม origin ยังต้องตั้ง login/CORS/โดเมนถาวร ส่วน localhost ของผู้ใช้ยังเป็น server local เดิม ไม่ได้หมายความว่าหน้า localhost ใช้ MySQL EC2 โดยอัตโนมัติ
