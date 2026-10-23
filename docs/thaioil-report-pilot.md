# ตัวอย่างข้อมูลพลังงานจากรายงานไทยออยล์

ตรวจวันที่ 22 ตุลาคม 2569 ใช้ [รายงานที่เผยแพร่โดยบริษัท](https://investor.thaioilgroup.com/storage/download/sustainability/2024/top-sustainability2024-en.pdf) ต้นฉบับอยู่ local และไม่ได้ใส่ใน Git

## สิ่งที่ทำได้จริง

อ่านตาราง PDF หน้าไฟล์ 60 (เลขพิมพ์ 63) และเชิงอรรถหน้าไฟล์ 62 (เลขพิมพ์ 65) เลือก 12 ตัวชี้วัด × ปี 2021–2024 = 48 observations: วัตถุดิบป้อน พลังงาน เชื้อเพลิงแยกชนิด ไฟฟ้าใช้/ซื้อ/ขาย และความเข้มพลังงานตามรายงาน

เก็บ SHA256 ต้นฉบับ URL เวลาเข้าถึง หน้า PDF เลขหน้าพิมพ์ ตำแหน่งแถวข้อความ หน่วย และค่าเดิม ทุกค่าคง PENDING_DOMAIN_AND_RIGHTS_REVIEW; Accepted ของชุดนี้เป็น 0

ต้นฉบับ SHA256: cd4f1f887a7c4b584262f1f19f0c9c22129b8b6e2c026d83c1d8efc83fdd0621

## ข้อค้นพบที่เปลี่ยนวิธีทำ

- เชิงอรรถระบุพลังงานครอบคลุม TOP, TPX, TLB, LABIX และ TOPSPP ส่วน throughput คือวัตถุดิบป้อนโรงกลั่น จึงไม่มีหลักฐานพอให้หารสองชุดนี้เป็น GJ ต่อหนึ่งตัน
- Total energy, total fuel และ electricity มีความเกี่ยวข้องกัน ไม่ใช่ flows อิสระที่นำมาบวกได้ทั้งหมด
- ค่าแบบ “น้อยกว่า” และช่องว่างไม่ใช่ศูนย์ ตัวดึงชุดนี้เลือกเฉพาะแถวตัวเลขชัดเจนและปฏิเสธแถวกำกวม
- หนึ่งแถว PDF อาจมีผลสกัดตัวอักษรผิด แม้บางแถวอ่านถูก จึงตรวจภาพจริงและใช้ตัวตรวจจำนวนคอลัมน์ด้วย ไม่เชื่อ parser ทั้งหน้า
- แปลง Million GJ → GJ ด้วยตัวคูณ 1,000,000 เท่านั้น ใช้ Decimal รักษาค่าทศนิยม ไม่ทำ allocation หรือประมาณค่าก๊าซเป็นมวล
- หน่วย GJ/BOE เป็น intensity ที่รายงาน ไม่ตีความเป็น LCI ต่อ kg และไม่เอามาปนกับปริมาณ annual input/output

รายงานนี้ช่วยเพิ่มข้อมูล input/output ระดับองค์กร แต่ยังไม่ใช่ inventory ครบหนึ่ง process ที่ normalize แล้ว ต้องทบทวนขอบเขตโรงงาน/ประเทศ วิธีปันส่วน และสิทธิใช้ซ้ำก่อนส่งต่อหรือใช้แข่งขัน

## ทำซ้ำ

Acquisition ใช้ Python standard library:

```powershell
python -X utf8 scripts/acquire_thaioil.py
```

การอ่าน PDF ต้องใช้ pypdf==6.10.0 (แยกจาก DMF pipeline ซึ่งไม่ต้องติดตั้ง package) ใน Python ที่มี package นี้:

```powershell
python -X utf8 -m src.report_pilot
python -X utf8 scripts/mysql_workspace.py load --reports
python -m unittest discover -s tests -v
```

ครั้งนี้รัน extractor ด้วย Python ของ bundled runtime ที่มี pypdf อยู่แล้ว ไม่ได้ติดตั้ง package เพิ่มให้ Python ของผู้ใช้

ผลอยู่ build/report-pilot/: report.json, reports.sqlite, page60-layout.txt, load-mysql.sql และ mysql-verification.json คำสั่ง --reports นำเข้า SQLite-derived export ในตาราง report_metric ที่แยกจาก DMF observation และเทียบตัวเลขครบ 48 ค่าใน MySQL

หน้าเว็บเมนู “ข้อมูลจากรายงาน” อ่านข้อมูลที่ build ไว้ แสดงค่าเดิมและหลักฐานแยกจาก DMF ไม่เพิ่มจำนวนนี้เข้าการ์ด DMF หรือ Accepted

การเข้าถึงสาธารณะยังไม่เท่ากับใบอนุญาตแจกจ่ายซ้ำ raw PDF จึงเก็บ local และคงสถานะ rights pending ทะเบียนแหล่งข้อมูลต้องไม่เรียกแหล่งนี้ว่า approved
