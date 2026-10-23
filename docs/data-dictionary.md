# Data Dictionary — DMF candidate database

MySQL ชุดเต็มและชนิดข้อมูล DECIMAL/JSON/DATE ดู [Data dictionary MySQL](mysql-full.md)

ขอบเขตของตารางด้านล่าง: SQLite จาก process_dmf.py + review_dmf.py; TEXT decimal ห้าม SUM ผ่าน SQLite floating-point แล้วอ้าง exact amount

| Table.field | SQL type | ความหมาย / กฎ |
|---|---|---|
| resource.package | TEXT PK | CKAN package name; หนึ่ง resource ต่อ package ใน snapshot นี้ |
| resource.url | TEXT NOT NULL | CSV URL จาก CKAN metadata |
| resource.csv_sha256 | TEXT NOT NULL | SHA256 ของ byte CSV ที่ดาวน์โหลดจริง |
| resource.metadata_sha256 | TEXT NOT NULL | SHA256 ของ metadata response จริง |
| resource.license_label | TEXT | label สิทธิจาก publisher; ไม่ได้แปล isopen เป็นกฎอนุญาตเอง |
| resource.metadata_unit | TEXT | หน่วยตาม metadata โดยยังไม่เติม /day เอง |
| resource.acquired_at | TEXT NOT NULL | เวลา acquisition UTC ISO8601 |
| staging.package / source_line | TEXT / INTEGER composite PK | FK resource + เลขบรรทัดสิ้นสุด record CSV ตาม csv.reader.line_num |
| staging.raw_json | TEXT NOT NULL | ทุก field ของ source row; จำนวน/ชื่อ field คงตามต้นทาง |
| candidate.package / source_line | composite PK/FK | อ้างถึง staging record ที่ parse ผ่าน |
| candidate.year_ce / month | INTEGER NOT NULL | ปี ค.ศ. จาก YEAR-543 / เดือน 1–12 |
| candidate.area | TEXT NOT NULL | BLOCK_TYPE บนบก / ในทะเล |
| candidate.block_label | TEXT nullable | BLOCK ต้นทาง; blank → NULL โดยคง blank ใน raw_json |
| candidate.source_group | TEXT NOT NULL | ชื่อแหล่ง/กลุ่มแหล่งตาม source ไม่แตกชื่อกลุ่ม |
| candidate.amount_column | TEXT NOT NULL | OIL / CONDENSATE / GAS |
| candidate.raw_value | TEXT NOT NULL | ค่า text ใน amount column |
| candidate.decimal_value | TEXT NOT NULL | Decimal ที่ finite และไม่ติดลบ ไม่มีการแปลงหน่วย |
| candidate.production_days | TEXT NOT NULL | DAYSOFPRODUCE เป็น integer 0–วันในเดือน; คง text |
| candidate.identity_sha256 | TEXT NOT NULL | hash package/period/area/block/group สำหรับจัดกลุ่ม review |
| candidate.duplicate_of_line | INTEGER nullable | อ้าง first occurrence สำหรับตรวจเบื้องต้น ไม่ใช่การตัดสินเลือกค่าถูก |
| candidate.review_status | TEXT CHECK | PENDING เสมอใน prototype นี้ |
| rejected.package / source_line | composite PK/FK | record ที่ parse ไม่ผ่าน |
| rejected.reasons_json | TEXT NOT NULL | รายชื่อกฎที่ไม่ผ่าน ไม่ลบแถวต้นฉบับ |
| duplicate_disposition.package / source_line | composite PK/FK | record ที่ตรวจ duplicate แล้ว |
| duplicate_disposition.status | TEXT NOT NULL | SINGLETON / EXACT_REPRESENTATIVE / EXCLUDE_EXACT_COPY / HOLD_CONFLICT |
| duplicate_disposition.representative_line | INTEGER nullable | บรรทัดตัวแทนเฉพาะสำเนา exact ใน package เดียวกัน |

Validation บางข้ออยู่ใน Python ไม่ใช่ SQL CHECK ทั้งหมด; ไม่ควรเขียนตรงเข้าฐานข้อมูลโดยข้าม pipeline
view deduplicated_candidates รวม SINGLETON + EXACT_REPRESENTATIVE เท่านั้น ทั้งหมดยังรอตรวจ unit/semantics/numerical/eligibility
