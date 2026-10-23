# EPPO: วัตถุดิบโรงกลั่นและผลผลิตน้ำมัน

ตรวจและนำเข้าวันที่ 23 ตุลาคม 2569 จาก CKAN resource CSV ทางการผ่าน browser downloadMedia; HTTP download โดยตรงและ package_search ได้403 จึงไม่ใช้ endpointนั้นซ้ำ ไม่ใช้การ bypass authentication/CAPTCHA

| ชุด | จำนวน | หน่วยต้นฉบับ | ขอบเขต |
|---|---:|---|---|
| [dataset_11_13](https://catalog.eppo.go.th/th/dataset/dataset_11_13) | 3012 | BBL/DAY | การใช้น้ำมันในการกลั่นแยกรายบริษัท |
| [dataset_11_14](https://catalog.eppo.go.th/th/dataset/dataset_11_14) | 2922 | Million Litres | การผลิตน้ำมันสำเร็จรูปแยกชนิด รวมประเทศ |

ข้อมูลจริง1986-01ถึง2026-07 ไม่ใช้metadataปีล่าสุด2567ทับช่วงCSV MetadataระบุรวบรวมจากDOEBและประมวลผลโดยEPPO จึงไม่ถือว่าเป็นการวัดอิสระจากDOEB/NSO; บริษัทที่เปลี่ยนชื่อยังคงlabelเดิม ไม่มีการรวมย้อนหลังอัตโนมัติ

## Mapping / dictionary

| Source | Target | กฎ |
|---|---|---|
| Year | reference_year | ค.ศ.ตามCSV ไม่ลบ543 |
| Month | month | English month lookup1–12 |
| Company / Product | subject + subject_type | คงชื่อและชนิด แยกcompanyจากproduct |
| Quantity | raw_value + amount | decimal string / MySQL DECIMAL(30,12); ไม่แปลงหน่วย |
| UNIT | unit / unit_code | ตรวจตรงBBL/DAYหรือMillion Litresของdatasetนั้น |
| file bytes + CSV line | source_sha256 + source_line | hashsnapshot + locatorค่าที่มา |
| metadata source | originating_agency | DOEB; publisherเป็นEPPO |

`source_snapshot`1:N`observation` ในMySQL tamsood_eppo; PKของobservationอิงsnapshot+line และUNIQUE(snapshot,year,month,subject) sourcepayloadเก็บครบ จำนวนลบ/เดือนผิด/ไม่มีparentถูกconstraintsปฏิเสธ ค่าศูนย์33รายการในintakeคงเป็นศูนย์ ไม่ตีความว่าmissingหรือโรงงานปิดโดยไม่มีหลักฐาน

## วิธีใช้และตรวจ

```powershell
python -X utf8 scripts/import_eppo.py
python -X utf8 scripts/load_eppo_mysql.py
python -X utf8 -m unittest tests.test_eppo -v
```

SQLite build/eppo/eppo.sqlite และJSON build/eppo/report.json; MySQLตรวจnumeric/unit/year/month/subject/status/locatorและpayloadครบ5934แถว หลักฐานevidence/eppo-import.jsonและeppo-mysql.json เว็บเมนูสถิติEPPOกรองdataset/year/subjectและแบ่งหน้า40ค่า พร้อมเปิดหลักฐาน ไม่ส่งrawไฟล์ในแพ็กเกจ

## ข้อจำกัดที่ต้องรักษา

- ทั้ง5934เป็นSTAGED_SOURCE_VERIFIED ยังไม่เพิ่ม97ACCEPTED_REFERENCEหรือnormalizedLCI
- intakeรายบริษัทกับผลผลิตประเทศคนละboundary ห้ามJOINเพื่อคำนวณyieldรายโรงกลั่น
- BBL/DAYไม่ใช่ยอดบาร์เรลรายเดือน และMillion Litresไม่ใช่มวล ไม่มีการคูณวันหรือคำนวณallocation
- 2026เป็นpartialyear ไม่annualize
- catalog/resourceแสดงOpen Data Common และข้อมูลเปิดเผย; ยังไม่ยืนยันspecificredistributionterms ไม่อ้างCC0/ODbLเอง
- สำรวจEPPOหน้าOilพบXLSXรายปีแต่directHTTP403และbrowserdownloadไม่สำเร็จ จึงใช้CSVจากresourceที่ดาวน์โหลดได้จริงแทน
- ลองscreening DIESEL2024ครบ12เดือนรวม27897.552Million Litres ขณะที่NSO13.6highspeeddieselผลิต27664Million litre ชื่อclassificationไม่ตรงพอ จึงไม่ประกาศnumerical mismatchของmetricเดียวกัน ไม่แก้ค่าและไม่นับเพิ่มcross-sourceverifiedcoverage

## ผลตรวจเว็บ

ค้นSPRCปี2024พบ12ค่า เปิดมกราคมพบ159590BBL/DAYที่CSVบรรทัด2801 ตรงJSON/SQL; ภาพbuild/explorer/eppo-sprc.png การทดสอบpaginationไม่ซ้ำ/คำค้นliteral/invalidfiltersผ่าน
