# Requirements — Final Project / Petroleum, Natural Gas & Fuels

สถานะ: baseline ทำงานของทีม จากคู่มือที่ผู้ใช้ให้, lecture W08–W11 และ source จริง
ไม่ใช่การประกาศอนุมัติกติกาแทนอาจารย์/MTEC

ผลเทียบเว็บ MTEC และตัวอย่าง Natural Gas Documentation วันที่ 22 ตุลาคม 2569 อยู่ [MTEC alignment](mtec-alignment.md)
ต้องแยก process boundary, reference basis, data period และ publication year เมื่อเพิ่ม inventory exchange; ชุด DMF ปัจจุบันยังเป็น production context รอตรวจ eligibility

## คำถามที่ระบบต้องตอบ

| ID | ความต้องการและเกณฑ์ตรวจรับ | หลักฐานปัจจุบัน |
|---|---|---|
| R01 | ค้นข้อมูลการผลิตตามผลิตภัณฑ์ เดือน ในทะเล/บนบก และชื่อกลุ่มแหล่งได้ | candidate / traceable_candidate |
| R02 | ทุกค่าชี้กลับ package, CSV URL, snapshot hash และ source line ได้ | scripts/trace_dmf.py |
| R03 | รันซ้ำจากต้นฉบับเดิมได้โดยไม่เพิ่มแถวและไม่ต้องเรียกเว็บ | scripts/run_pipeline.py |
| R04 | แยก source parsing error จาก semantic uncertainty | rejected กับ PENDING review_status |
| R05 | ตรวจ missing, datatype, period/day bounds, duplicate และ context | process_dmf.py / review_dmf.py |
| R06 | เลือกเฉพาะรายการที่ไม่ซ้ำและไม่ขัดกันโดยคงหลักฐานทุกแถว | deduplicated_candidates view |
| R07 | amount เก็บทศนิยมตรงต้นฉบับ พร้อมค่าดิบก่อนแปลง | Decimal parser + raw_value/decimal_value |
| R08 | แยก structural pass, duplicate disposition, numerical checks และ competition acceptance | quality-report / review-report |
| R09 | มี dictionary, relational design, mapping และเหตุผลการออกแบบที่อธิบายได้ | docs/database-design.md / data-dictionary.md |
| R10 | ค้น coverage และ missing context โดยไม่รวมหน่วย/ขอบเขตผิด | sql/dmf_review_queries.sql; ยังต้องเพิ่ม query ชุด Final |

## Business rules ที่ใช้จริง

อัปเดตขอบเขต23ตุลาคม2569: ครอบคลุมข้อมูลหลายชั้นเพิ่มจากDMF โดยไม่รับทุกชั้นเป็นLCI ดู [EPPO mapping](eppo-source.md), [corporate model](reusable-model.md), [supplemental model](supplemental-mysql.md)

| ID | ความต้องการเพิ่ม | หลักฐาน |
|---|---|---|
| R11 | ค้นข้อมูลอ้างอิงองค์กรโดยคงreview/release/rights | reusable-model.md; reference_catalog |
| R12 | สถิติประเทศและinventoryต่อหน่วยเก็บแยกสถานะและbasis | supplemental-mysql.md; NSO/product inventory |
| R13 | ค้นEPPOรายเดือนแยกcompany intake/product nationaloutputโดยไม่สร้างyield | eppo-source.md; /api/eppo |
| R14 | versionedsourceidentityและตรวจSQLroundtripทุกfieldของชุดใหม่ | evidence/supplemental-mysql.json; eppo-mysql.json |

แบบจำลองกลางยังเป็นงานถัดไป: ชนิดข้อมูล/หน่วย/พื้นที่/ที่มาต้องสอดคล้อง แต่ไม่บังคับสถิติองค์กรหรือประเทศให้เป็นprocessLCIexchangeเมื่อboundaryไม่รองรับ

- ประเทศไทยเป็น scope ตาม metadata; offshore/onshore เป็นประเภทพื้นที่ ไม่ใช่ชื่อจังหวัด
- แหล่งผลิตที่เขียนเป็นชื่อกลุ่มคงเป็นกลุ่ม ไม่กระจายตัวเลขไปให้แต่ละสมาชิก
- ทุก observation ผูกกับ resource และ snapshot ที่ใช้ แม้ URL เดิมมีข้อมูลเปลี่ยนได้
- year แปลง พ.ศ. → ค.ศ. อย่างเปิดเผย; ศูนย์ไม่ใช่ missing
- ไม่รวมอัตรารายวันเป็นยอดรายเดือนหรือยอดปีเมื่อยังไม่มี rule/ฐานเวลาที่พิสูจน์ได้
- สำเนาเหมือนกันทุก source field จึงรวมตัวแทนได้; conflicting identity ต้องพักทุกสมาชิก
- raw rows, structural pass และ deduplicated pending ต่างจาก accepted tuples
- ค่าเทียบเท่าน้ำมันดิบยังไม่ถูกนับเพิ่มเป็น observation ใหม่
- ข้อมูลจาก DMF สามผลิตภัณฑ์เป็นความหลากหลายของผลิตภัณฑ์ ไม่ใช่ publisher อิสระสามแห่ง

## สิ่งที่ยังต้องตัดสินจากหลักฐานเพิ่มเติม

Definition ของ accepted LCI tuple และวิธีจัดประเภท production statistics,
reference time basis ของ CSV ตลอดช่วงย้อนหลัง, revision ของกลุ่มค่าขัดกัน และ process/reference-product basis ของแหล่งใหม่ (typed integration สองรายงานทำแล้ว ดู reusable-model.md)
รับรองเฉพาะขอบเขตที่มีหลักฐานรองรับ ไม่ตั้ง target accepted count จากจำนวน raw
