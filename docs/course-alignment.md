# เชื่อม lecture กับ TamsoodBase

วันที่ตรวจ: 22 ตุลาคม 2569; เลขหน้าด้านล่างเป็นหน้าในไฟล์ PDF เริ่มที่ 1
สกัดข้อความทั้ง 239 หน้าเพื่อค้นหัวข้อ อ่านส่วนที่เกี่ยวข้อง และตรวจภาพ W08 หน้า 26, W10 หน้า 6, W11 หน้า 40
ยังไม่ได้ตรวจภาพทุกหน้า และไม่ได้อ่าน lecture ทุกสัปดาห์ของวิชา

## ข้อเท็จจริงที่พบและการนำมาใช้

| แหล่ง | แนวคิดจากเอกสาร | การใช้กับโปรเจกต์ |
|---|---|---|
| W08 หน้า 8-20 | บันทึก source, rights, raw, batch, staging และ provenance | รักษา registry และ metadata; ต้องเพิ่ม raw snapshot จริงก่อนผ่าน review |
| W08 หน้า 21-26 | dictionary, unit/context, missing vs zero, duplicate และ numerical verification | ไม่แทน missing ด้วยศูนย์ ไม่รวมหน่วยต่างชนิด และไม่อ้าง technical PASS เป็น accepted |
| W08 หน้า 70-71 | แยก raw/staging/canonical และใส่ source ในฐานข้อมูล | prototype ยังเป็น observation ของ production statistics; ไม่บังคับสร้าง LCI exchange จน domain ชัด |
| W09 หน้า 11-16, 25-28 | MySQL บน Docker และ DDL/PK/FK | เพิ่ม schema MySQL และการทดสอบ Docker แยกจาก SQLite |
| W10 หน้า 5-7, 40, 47 | JOIN, grouping, HAVING และ relational algebra | เพิ่ม query ตาม provenance, coverage และ source ที่ไม่มีข้อมูล; เตรียมอธิบาย query จากความหมาย |
| W11 หน้า 13, 31-36, 40, 44 | ลด redundancy โดยยึด FD/key และตรวจ lossless join | แยก production_context ออกจาก observation พร้อมบันทึก FD และข้อสมมติ |

## แยกข้อกำหนดการบ้านจาก Final

- W10 หน้า 6 ระบุการบ้านต่อยอด W09: เพิ่ม 20 tuples จาก source ที่สอง รวมอย่างน้อย 40 และมีข้อมูลไม่มีคู่สำหรับ LEFT JOIN
- ตัวเลขเหล่านี้เป็นเงื่อนไขการบ้านที่ปรากฏใน lecture ไม่ใช่เป้าจำนวน accepted tuples ของการแข่งขัน
- คำสั่งให้เขียน algebra/SQL ด้วยลายมือใช้ตาม assessment นั้น ไม่สร้างหรืออ้างลายมือ/คำตอบของสมาชิกแทน
- Q&A ใน Teams W15 วันที่ 9 ตุลาคม 2569 อนุญาตสำรวจ production/supply/trade แต่ให้ทีมให้เหตุผลเชื่อมกับ LCI; ไม่ยืนยันว่าทุก production statistic นับแข่งขันได้
- Teams มีงาน W11 A4 กลุ่มชื่อ Normalization of LCI Database กำหนด 26 ตุลาคม 2569 เวลา 23:59 ตามรายการที่เห็น; ยังไม่ได้เปิดใบงาน จึงยังไม่สรุปเงื่อนไขงานนั้น
- ยังไม่ยืนยันวัน Final จริง และยังไม่เปลี่ยนข้อสันนิษฐานเรื่องเวลา 3 สัปดาห์เป็นวันส่งอย่างเป็นทางการ

## สิ่งที่แก้แล้ว

1. เก็บเอกสาร 4 ชุดแบบไม่ซ้ำพร้อม manifest
2. เพิ่ม MySQL schema/export ที่ใช้ DECIMAL(20,6) และเก็บ raw_value เดิม
3. เพิ่ม query JOIN, LEFT JOIN และ GROUP BY/HAVING สำหรับ use cases ของทีม
4. เพิ่ม integration check กับ mysql:8.1 ที่มีอยู่ในเครื่อง เพื่อให้ตรง environment ตัวอย่างใน lecture
5. ยืนยันว่ารันนำเข้าซ้ำไม่เพิ่มจำนวน และ FK/CHECK/duplicate constraints ปฏิเสธข้อมูลผิด

## ข้อจำกัดที่ยังต้องแก้ก่อนขยาย

- ยังมีเพียงข้อมูลถอด 3 รายการ ขาด snapshot ต้นฉบับและ independent numerical verification
- สิทธิใช้แหล่งข้อมูลและเกณฑ์ LCI ยัง pending; ไม่มี accepted tuples
- source-specific staging ที่รักษาคอลัมน์ต้นทางครบยังต้องทำเมื่อได้ไฟล์จริง
- production_context เป็นชื่อกลุ่มตามรายงาน ไม่ใช่ทะเบียนแปลง/แหล่งทางภูมิศาสตร์ที่แยกสมาชิกแล้ว
- ยังไม่มี human review workflow, source revision reconciliation หรือ dedup ข้ามแหล่ง
- MySQL 8.1 ใช้เพื่อเทียบกับเครื่องมือในคลาสและ image ที่มีอยู่ เป็น environment ทดลอง; รุ่นใช้งานระยะยาวต้องล็อกตาม environment ทีมอีกครั้ง

อ้างอิงเทคนิคที่ตรวจเพิ่ม: MySQL official manual เรื่อง [DECIMAL](https://dev.mysql.com/doc/refman/8.4/en/fixed-point-types.html), [CHECK](https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html) และ [Docker](https://dev.mysql.com/doc/refman/8.4/en/docker-mysql-getting-started.html)
