# MySQL pilot และเหตุผลการออกแบบ

## วิธีรันทดสอบ

ใช้ Python standard library, Docker Engine ที่เปิดอยู่ และ image mysql:8.1 ที่ติดตั้งในเครื่อง

```powershell
python src/pilot.py
python src/export_mysql.py
python scripts/verify_mysql.py
```

ตัวตรวจสร้างคอนเทนเนอร์ชั่วคราวชื่อ tamsood-check-<random> ด้วยรหัสผ่านสุ่ม ไม่เปิด port และไม่เชื่อม network
อ่าน schema, import 2 รอบ, ตรวจจำนวน/decimal/constraints/query และลบเฉพาะคอนเทนเนอร์ที่ตัวเองสร้าง
ไม่ดึง image ใหม่อัตโนมัติ ถ้าไม่มี mysql:8.1 จะหยุดและรายงาน
ผลอยู่ใน build/mysql-verification.json และ build/mysql-query-results.tsv

สำหรับ DB ทดลองของทีม ใช้ sql/mysql/schema.sql ตามด้วย build/mysql-pilot.sql และ sql/mysql/queries.sql ผ่าน MySQL client
schema สร้าง database ชื่อ tamsood_pilot; ห้ามใช้ชื่อนี้ร่วมกับระบบงานอื่น
import แทนที่เฉพาะ batch เดิมที่ hash ตรงกัน รันซ้ำจึงไม่เพิ่มข้อมูล;
input/evidence/exporter/schema เปลี่ยนจะได้ batch ใหม่ ต้อง reconcile revision ก่อนนับปริมาณข้าม batch

## Grain และ keys

หนึ่ง observation = หนึ่งค่าการผลิตเชื้อเพลิงในชื่อแหล่ง/กลุ่มแปลงตามรายงาน สำหรับเดือนหนึ่ง ใน extraction batch หนึ่ง
batch เป็น version ของตัวอย่าง ไม่ใช่มิติเพื่อเพิ่มคะแนนข้อมูลซ้ำ
ชื่อกลุ่มแปลงและชื่อกลุ่มแหล่งคงเป็น label ตาม source ไม่ตีความว่าตัวเลขเดียวกระจายให้สมาชิกทุกแหล่งได้

| Relation | Functional dependency ที่ใช้ในการออกแบบ |
|---|---|
| source | source_id → publisher, url, rights_status |
| extraction_batch | batch_id → source_id, hashes, accessed_date, method, evidence_level |
| unit | unit_code → description |
| production_context | context_id → source_id, area, block_label, field_label |
| observation | (batch_id, record_id) → context_id, period_start, fuel_code, raw_value, amount, unit_code, evidence_locator, review_status |

กำหนด alternate unique key ของ observation เป็น batch/context/period/fuel/unit เพื่อป้องกันรายงานค่าเดียวกันซ้ำใน batch
raw_value กับ amount เป็นทั้งหลักฐานและผล parse ที่เก็บคู่กัน จึงเป็น redundancy ที่ตั้งใจให้ audit ได้ ไม่อ้างว่าตารางนี้ผ่าน 3NF อย่างเป็นทางการโดยไม่มีข้อยกเว้น:
ใน pilot หน่วย/เชื้อเพลิงจำกัดชนิด และ numeric amount ถูกกำหนดจาก raw_value ตาม parser rule
ต้องแจกแจง FD จาก business rules ของข้อมูลเต็มก่อนสรุป normal form สำหรับ Final

แยกชื่อ context ที่ซ้ำในหลายเดือนออกเป็น lookup เพื่อแก้ชื่อที่จุดเดียวได้
การ join observation กับ context/batch/unit ผ่าน FK ที่เป็น NOT NULL และชี้ PK ทำให้แต่ละ observation มีคู่หนึ่งรายการ โดยไม่เพิ่มแถวจาก lookup
การทดสอบยืนยันตัวอย่าง 3 แถว round-trip ได้; ไม่ใช่ข้อพิสูจน์ว่า schema รองรับทุก source

## Query ที่มีความหมาย

- Traceability: observation → context + batch → source แล้วดู URL/locator ของค่าที่เลือก
- Coverage: นับรายการตามเดือน/พื้นที่/เชื้อเพลิง/หน่วย ไม่รวมอัตรารายวันข้ามเดือน
- LEFT JOIN: ตรวจ source ที่ลงทะเบียนแต่ยังไม่มี observations จริง ไม่สร้างข้อมูลเชื้อเพลิงขึ้นเพื่อให้เข้าโจทย์
- Status count: นับ PENDING เพื่อเห็นงานตรวจที่เหลือ ไม่มี accepted view ใน prototype นี้

ผล SUM(amount) ใน integration check ใช้ตรวจ round-trip ตัวเลข fixture เท่านั้น ไม่ใช่ยอดผลิตประเทศไทย
