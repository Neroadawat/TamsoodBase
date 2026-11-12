# ดัชนีแบบจำลองและ mapping กลาง

ผลตรวจ Normal Form ล่าสุดและ candidate ที่แก้ metric/document redundancy: [normalization-audit.md](normalization-audit.md) — ยังไม่ย้ายฐาน API/EC2 และไม่รับรองทั้งระบบเป็น 5NF

ปรับ23ตุลาคม2569 เอกสารนี้เป็นสัญญาความหมายร่วมและดัชนีschemaจริง ไม่อ้างว่ารวมทุกชุดเป็นphysicalschemaเดียวแล้ว

| ชั้น | Database / schema | หน่วยข้อมูลและสถานะ | Dictionary / mapping |
|---|---|---|---|
| DMF | tamsood_research / sql/mysql/full-schema.sql | source record → observation → duplicate disposition; pending ไม่ใช่acceptedLCI | data-dictionary.md, mysql-full.md, mapping.md |
| รายงานบริษัท | tamsood_reusable / sql/mysql/reusable-schema.sql | document → context → metric → observation → review → release;101ต้นทาง/97reference/4hold | reusable-model.md |
| NSO | tamsood_supplemental / sql/mysql/supplemental-schema.sql | snapshot → observation → national_statistic;273staged | nso-source.md, supplemental-mysql.md |
| งานวิจัย | tamsood_supplemental / schemaเดียวกัน | snapshot → process → inventory_exchange → observation;16source-reported | product-inventory.md, supplemental-mysql.md |
| EPPO | tamsood_eppo / sql/mysql/eppo-schema.sql | source_snapshot → observation;5934staged | eppo-source.md |

## Vocabulary ร่วมสำหรับเชื่อมความหมาย

| แนวคิด | Field ที่ใช้จริง | กฎกลาง |
|---|---|---|
| Identity | record_id / observation_id / snapshot_id | identityผูกsourceและcontext; ไม่JOINคนละdatasetด้วยชื่อflowอย่างเดียว |
| Publisher | publisher / publisher_id | ผู้เผยแพร่แยกจากoriginating_agency; NSO/EPPOเผยแพร่ซ้ำไม่ใช่การวัดใหม่ |
| Source artifact | csv_sha256 / source_sha256 / pdf_sha256 / source_snapshot_sha256 | hashระบุbytesหรือDOMsnapshotตามวิธีcapture ไม่รับรองmeasurementaccuracy |
| Locator | source_line / source_column / pdf_page / source_row | ใช้ร่วมกับhash ไม่ใช้เลขหน้า/บรรทัดลอย ๆ |
| Period | year_ce+month / reference_year / data_period | ปีpublicationและaccessed_atไม่แทนmeasurementperiod; nullคงไว้เมื่อไม่ทราบ |
| Quantity | raw_value + amount/value_decimal/scaled_amount | Decimal; คงค่าดิบ; scaleเฉพาะที่มีfactorชัด ไม่ทำallocationเพิ่มเอง |
| Unit | unit_code / unit / metadata_unit | ต้องอ่านคู่timebasis/denominatorและdimension ไม่ตัด/yearหรือ/day |
| Scope | context/source_scope / geography / scope / boundary | country,companyและforegroundprocessแยกกัน แม้เป็นประเทศไทยทั้งหมด |
| Decision | review.decision / status / review_status | ACCEPTED_REFERENCE,STAGED_SOURCE_VERIFIED,SOURCE_REPORTED_PRODUCT_INVENTORY,PENDINGไม่เท่ากัน |
| Rights | rights_status / redistribution_status / license_label | คุณภาพผ่านไม่ทำให้สิทธิเปลี่ยน; labelที่พบไม่อนุมานlicenseฉบับอื่น |

## หน่วยที่ห้ามรวมกันโดยอัตโนมัติ

- `BBL/DAY`: volume rateของEPPOintake ไม่ใช่ยอดบาร์เรลในเดือน
- `Million Litres`/`Million litre`: volume scale; ต้องตรวจนิยามmetricและช่วงเวลาแม้ข้อความหน่วยคล้ายกัน
- `Thousand litre`กับ`Thousand kilogram`: NSO13.8มีเชิงอรรถmassoverrideสำหรับบางเชื้อเพลิง ห้ามบวกmassกับvolume
- `m3`กับ`m3/year`: แยกตามต้นฉบับ; gasvolumeห้ามแปลงkgโดยเดาสภาวะ/องค์ประกอบ
- `kg`, `kWh`, `mg`ต่อ`1000 MJ fuel`: เป็นsource-reportedinventorybasis ไม่ใช่ปริมาณรวมรายปี
- `GJ`,financialvalue,percentและintensityมีความหมายต่างกัน; aggregationต้องอาศัยrole/denominatorไม่ใช้SUMทุกแถว

Unitmasterยังแยกตามmodel ไม่มีglobalunitFKครบทุกschema การมีvocabularyนี้ไม่ใช่หลักฐานว่าทำunitnormalizationทุกแหล่งแล้ว

## เส้นทางการตรวจ release

`python -X utf8 scripts/check_release.py --tests --package`

ตัวตรวจเดิมครอบคลุมDMF/corporate; audit_dataset_layers.pyเติมNSO/inventory/EPPO ตรวจidentity,status,sourcehash,rowprovenance,SQLiteintegrity/payloadและผูกstoredMySQLevidenceกับreport/schemaปัจจุบัน ไม่เรียกliveMySQLในreleaseauditนี้ ต้องรันloaderเมื่อต้องการหลักฐานliveใหม่

แพ็กเกจinternal-review.zipรวมcode/docs/evidenceและwebHTML/CSS/JSที่เคยตกหล่น ไม่รวมraw/PDF/credentials/generatedDB ชุดนี้จึงไม่ใช่แพ็กเกจself-containedพร้อมข้อมูลทุกชั้นบนเครื่องใหม่ และไม่อ้างสิทธิredistributeข้อมูลบริษัท

## ข้อค้างจริง

Cross-sourceNSOล่าสุดเทียบ15/273 อีก258ยังไม่เทียบ;DEDErevised2024totalและ5subtotalตรง โดยคงpreliminaryที่ต่างแยกไว้ ไม่ถือเป็นindependentmeasurements;historicalDMFtimebasisยังไม่ชัด;สมาชิกยังต้องมีcontribution/defenseจริง;deadline/channelและข้อกำหนดส่งล่าสุดต้องมีหลักฐานก่อนfinalfreeze การผ่านtechnicalauditไม่ใช่submissionreadyหรือMTECapproval
## ตรวจ freshness ของ DMF — 10 พฤศจิกายน 2569

การตรวจ snapshot ต้องจัดกลุ่มด้วยคู่ `(year_ce, month)` ก่อนเรียงช่วงล่าสุด ห้ามหา `MAX(year_ce)` และ `MAX(month)` แยกกัน เพราะอาจหยิบค่าจากคนละแถว. ผลตรวจ CKAN ทั้งสามชุดล่าสุดคือ `2026-03`; การดึง candidate รอบ 10 พ.ย. ได้ SHA-256 ตรงกับ snapshot ปัจจุบันทุกไฟล์ จึงไม่มีข้อมูลใหม่จากช่องทาง CKAN. หน้าเผยแพร่รายงานรายเดือนของ DMF แสดงถึง ก.ย. 2569 ซึ่งเป็นคนละเส้นทางข้อมูลและยังไม่ได้ reconcile กับ CKAN. คงข้อมูลเป็น `PENDING` และห้ามเผยแพร่/ส่งให้ external LLM จนยืนยันหน่วย ฐานเวลา และเงื่อนไขเผยแพร่. รายละเอียด: `evidence/dmf-refresh-check-2026-11-10.json`.

การเปรียบเทียบเดือนมีนาคม 2569 กับรายงาน Excel จากผู้เผยแพร่รายเดียวกันตรงกันใน 170 ช่องตัวเลขภายใน precision ที่แสดงและจำนวนวันผลิต แต่ไม่ใช่การตรวจวัดอิสระ; พบ label แปลง `14A16A`/`14A-16A` ต่างกัน 2 package จึงคง raw label ทั้งคู่. รายงานกันยายน 2569 มี 33 แถวและไฟล์ HTML/XLSX ที่ตรวจ hash แล้ว แต่ยังไม่ import. แหล่งรายงานรายเดือนทั้งสองถูกเพิ่มใน source registry เป็น `acquired_pending_review`, สิทธิ `NOT_CLEARED`; หลักฐาน `evidence/dmf-monthly-candidate-2026-11-10.json`.
