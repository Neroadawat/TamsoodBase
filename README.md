# TamsoodBase — Thailand Petroleum, Natural Gas & Fuels

CN230 × MTEC Final Project: ฐานข้อมูลการผลิตเชื้อเพลิงของไทยที่มีต้นฉบับ เกณฑ์ตรวจ และเส้นทางย้อนกลับระดับแถว

ติดตามงานคงเหลือและเกณฑ์จบที่ [Task board](docs/tasks.md) และ [ผลตรวจความพร้อม](docs/release-readiness.md) ฐานข้อมูลใช้งานได้แต่ยังไม่ผ่าน final submission gate

อัปเดต 23 ตุลาคม 2569: NSO273ค่าและงานวิจัยFAME/H-FAME16ค่าโหลดและตรวจอ่านกลับใน MySQL `tamsood_supplemental` แล้ว ดู [schema/ผลตรวจ](docs/supplemental-mysql.md) ทั้งสองชุดยังแยกสถานะจาก97ACCEPTED_REFERENCE เว็บเริ่มที่หน้าเลือกชุดข้อมูลและยังอ่านSQLite/JSON; EPPOนำเข้าCSVโรงกลั่น3012และผลผลิตประเทศ2922ค่าพร้อมMySQLroundtripแล้ว ยังแยกเป็นsource statistics ดู[รายละเอียด](docs/eppo-source.md) ดู [ผลเทียบแผนกับงานจริง](docs/shared-plan-comparison.md)

## ชุดข้อมูลพร้อมใช้อ้างอิง

ใช้ [นโยบายทีม v1](docs/team-data-policy.md) และ [แบบจำลองเชิงสัมพันธ์](docs/reusable-model.md) โดยไม่รอคำยืนยัน MTEC รับเป็น reference data 97 รายการ พักบริบท 4 รายการ จากการสกัดซ้ำต้นฉบับครบ 101 รายการ

เปิดเมนู **พร้อมใช้ต่อ** เพื่อค้น/กรอง/ส่งออก CSV หรือ JSON ข้อมูลแยกชนิด ขอบเขต หน่วย ปี ที่มา และสิทธิทุกแถว คำว่า ACCEPTED_REFERENCE เป็นผลตรวจของทีมสำหรับอ้างอิงภายใน ไม่ใช่ normalized LCI ต่อผลิตภัณฑ์หรือใบอนุญาตแจกจ่ายต่อ

```powershell
python -X utf8 scripts/run_reference.py --mysql
python -X utf8 scripts/package_reference.py
```

MySQL ใช้ schema tamsood_reusable แยกจาก DMF research database ตัวอย่างการใช้งานจริงอยู่ examples/use_reference.py

พร้อมใช้นำเสนอ: [Demo และ defense](docs/demo-and-defense.md), [SQL/performance evidence](docs/sql-performance.md), [Contribution log สำหรับสมาชิกกรอกงานจริง](docs/team-contribution.md)

## สถานะ 22 ตุลาคม 2569

| ขั้น | จำนวน |
|---|---:|
| ต้นฉบับ DMF CSV สามผลิตภัณฑ์ | 34,905 แถว |
| ผ่านรูปแบบเบื้องต้น | 34,899 แถว |
| ไม่ผ่านพร้อมเหตุผล | 6 แถว |
| สำเนา exact ที่แยกจาก view | 42 แถว |
| พักทั้งกลุ่มเพราะรายละเอียดขัดกัน | 186 แถว |
| รายการไม่ซ้ำและไม่อยู่ในกลุ่มขัดกัน | 34,671 candidates |
| Accepted สำหรับแข่งขัน | **0 — ยังรอ domain/unit/numerical review** |

ค่าเทียบเท่าน้ำมันดิบไม่ถูกนับเพิ่มเป็นรายการใหม่
ตัวเลข spot-check ตรง 12/12 ค่า แต่ block label ตรงเพียง 7 ค่า ไม่ใช้แทนอัตราความถูกต้องทั้งชุด
พบคำอธิบาย G0 Open Data Common จาก GD Catalog ที่สนับสนุนการใช้ซ้ำแล้ว ดู evidence/dmf-rights-review-2026-10-22.json; คงบันทึก metadata inconsistency และยังไม่เผยแพร่ raw files

## เริ่มใน VS Code / Python 3.12

### เว็บสำรวจข้อมูลในเครื่อง

```powershell
python -X utf8 src/explorer.py
```

เปิด http://127.0.0.1:8765 เพื่อค้นข้อมูล ดูหลักฐาน ตรวจคุณภาพ และส่งออก CSV ตามตัวกรอง
รายละเอียดอยู่ [คู่มือ Data Explorer](docs/explorer.md) ใช้ข้อมูลจริงจาก pipeline และยังแสดงสถานะรอตรวจ

กด **Ctrl+Shift+B** เพื่อรัน project pipeline จาก snapshot ที่มีอยู่ หรือใช้ Terminal:

```powershell
python -X utf8 scripts/run_pipeline.py
python -m unittest discover -s tests -v
python -X utf8 scripts/trace_dmf.py production-oil 2
```

ใช้ Python standard library ไม่ต้องติดตั้ง package เพิ่ม
สำหรับเครื่องใหม่หรือเมื่อต้องการ snapshot ใหม่:

```powershell
python -X utf8 scripts/run_pipeline.py --acquire
```

คำสั่ง default ทำงาน offline; --acquire ดาวน์โหลด metadata/CSV จาก CKAN ของ DMF และสร้าง snapshot ใหม่
ทุก run ตรวจ checksum, parse, duplicate review, foreign keys, SQLite integrity, จำนวนแถว และสร้าง SQL ชุดเต็มที่รักษาทศนิยมต้นทาง
ผลล่าสุดอยู่ build/project-status.json; รายละเอียดและฐานข้อมูลอยู่ build/dmf/<run_id>/
รันซ้ำจาก snapshot เดิมไม่เพิ่มจำนวนข้อมูล

โหลดชุดเต็มเข้า MySQL ใน Docker ที่ติดตั้งไว้แล้ว (ใช้ image mysql:8.1 ที่มีในเครื่อง):

```powershell
python -X utf8 scripts/run_pipeline.py --mysql
python -X utf8 scripts/mysql_workspace.py status
```

ข้อมูลเก็บใน named volume และไม่มีการเปิดพอร์ตฐานข้อมูลออกจาก container รหัสผ่านสร้างอัตโนมัติใน .local/ ซึ่งไม่เข้า Git

## เปิดอ่านตามลำดับนี้

1. [Requirements และ business rules](docs/requirements.md)
2. [ERD และเหตุผลการออกแบบปัจจุบัน](docs/database-design.md)
3. [Data dictionary](docs/data-dictionary.md)
4. [ผลตรวจหน่วยและข้อมูลซ้ำ](docs/dmf-review-results.md)
5. [ที่มาและ mapping ของ DMF](docs/dmf-data-review.md)
6. [แผนโครงงาน](docs/project-plan.md) และ [ทะเบียนแหล่งข้อมูล](docs/source-registry.csv)

## โครงสร้างงาน

- src/acquire_dmf.py: เก็บ metadata และ exact CSV bytes พร้อม hash
- src/process_dmf.py: source-preserving staging → candidate/rejected
- src/review_dmf.py: exact-copy/conflict disposition และ report spot-check
- scripts/run_pipeline.py: รันครบชุดและตรวจ row accounting
- scripts/trace_dmf.py: ย้อนกลับ candidate ถึงไฟล์ CSV และตรวจค่าต้นทาง
- sql/dmf_review_queries.sql: query สำหรับตรวจสถานะและทุกสมาชิกกลุ่มขัดกัน
- evidence/: acquisition metadata, review results และบันทึกข้อจำกัด

raw files, build outputs และ lecture PDF/text อยู่ local และ gitignore; ไฟล์สรุปกับโค้ดเก็บใน Git ได้
ข้อมูลเต็มอยู่ทั้ง SQLite สำหรับตรวจข้อมูลและ MySQL สำหรับฐานข้อมูลวิจัย: raw 34,905 แถว, observation 34,899 แถว และ rejected 6 แถว
MySQL ผ่านการเทียบค่าทศนิยมทุก observation และ raw JSON ทุกแถว รวมถึง import ซ้ำและทดสอบ constraints 6 กรณี
อ่าน [คู่มือ MySQL ชุดเต็ม](docs/mysql-full.md) และ [schema](sql/mysql/full-schema.sql)
ฐานนี้เก็บสถิติการผลิตที่รอตรวจ ไม่ใช่ canonical LCI schema ที่อนุมัติแล้ว

## งานถัดไป

เพิ่ม [ตัวอย่างข้อมูลพลังงานจากรายงานไทยออยล์](docs/thaioil-report-pilot.md) แล้ว: 48 observations ใน SQLite/MySQL แยกจาก DMF เปิดผ่านเมนู “ข้อมูลจากรายงาน” ทุกค่ายังรอ domain/rights review

เพิ่ม [SPRC และผลทบทวนบริบท](docs/sprc-review.md) อีก 53 observations พร้อมตรวจสมการพลังงาน 8 กรณีและพักความต่างตารางน้ำ 2 คู่ ทั้งสองรายงานมีรวม 101 source observations ซึ่งไม่ใช่ 101 Accepted หรือ flows อิสระทั้งหมด

อ่าน [ผลเทียบเว็บ MTEC กับช่องว่างของโครงการ](docs/mtec-alignment.md) ซึ่งใช้ตัวอย่าง Natural Gas Documentation จริงเป็นแนวทาง โดยแยกข้อสังเกตออกจากกติกาแข่งขัน

ยืนยันหน่วยย้อนหลังและ LCI eligibility, ตรวจ 93 กลุ่มค่าขัดกันด้วยรายงานช่วงเดียวกัน,
แล้ว freeze canonical LCI model และเพิ่มแหล่งข้อมูลด้านจัดหา/นำเข้า/ใช้
lecture W08-W11 ใช้เป็นแนวทางประกอบ Final เท่านั้น ไม่ดำเนินการบ้านย่อย
ยังไม่ได้ดูวิดีโอ Launch; อ่านประกาศและ Q&A ใน Teams แล้ว

AI ช่วยค้นข้อมูล เขียนระบบ และเอกสารในวันที่ 22 ตุลาคม 2569 สมาชิกทีมต้องตรวจและอธิบายผลงาน รวมถึงบันทึก contribution ตามงานที่ตนทำจริง
