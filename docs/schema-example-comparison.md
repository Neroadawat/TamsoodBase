# เทียบ schema ตัวอย่างอาจารย์กับ TamsoodBase

27 ตุลาคม 2569 · ตัวอย่างอ้างอิง [ERD guide](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-erd.html) ที่อ่านจากสำเนา authenticated ของวันเดียวกัน ไม่คัดลอกรูป/HTMLของผู้สอนมาแจก

## ข้อสรุป

ของเราละเอียดกว่าในงาน source engineering และ governance แต่ยังไม่ครบกว่าในทุกมิติของ LCI จำนวน27ตารางเทียบตัวอย่าง6entitiesไม่ใช่คะแนนคุณภาพ อาจารย์ใช้ตัวอย่างสอน core LCI;ระบบเราครอบคลุมข้อมูล5ระดับและเก็บ workflowเพิ่ม จึงต้องอธิบายเหตุผลของแต่ละตาราง ไม่ใช้ความซับซ้อนเป็นจุดขายแทนdomainfit

| แนวคิดตัวอย่าง | ของเราปัจจุบัน | ผลเทียบ |
|---|---|---|
| PROCESS | supplemental.process แยกsnapshot/process_id พร้อมbasis/geography/technology | เพิ่มฐาน1000MJfuelที่มีจริงและversionidentity;boundary/allocationบางส่วนยังอยู่payload/report ไม่ใช่typedcolumnครบ |
| FLOW | inventory_exchange.flow เป็นlabel;graphมีsource-localFlow | ตัวอย่างชัดกว่าเรื่องmaster/flow_type/compartment ของเรายังไม่มีsharedrelationalFLOW ห้ามอ้างว่าแยกครบแล้ว |
| LCI_EXCHANGE | inventory_exchange เชื่อมobservation/processด้วยcompositeFK | รักษาexchangeidentity,locator,direction,role;ไม่promoteเป็นfullLCI |
| UNIT | corporate.unitมีFK แต่supplemental/EPPOเก็บunitlabelและCHECKตามชุด | masterไม่ครอบคลุมทั้งระบบ;ไม่มีglobaldimension-safeconversionengine |
| SOURCE | resource_snapshot/document/dataset_snapshot+sourcehash/registry | ละเอียดกว่าเรื่องsnapshot/locator แต่ยังไม่มีreadablesource_idcontractเดียวทุกAPI/export |
| LOCATION | typedgeographyบนprocessและcontextmetadataของชุดอื่น | ยังไม่มีLOCATIONmasterร่วม ไม่เดาจังหวัดจากoffshore/onshore |
| ProcessกับFlow M:N | exchangeแสดงหลายflowต่อprocess แต่flowยังlabel | ยังไม่ใช่normalizedsharedFlowrelationshipเต็มรูปแบบ |
| Sourceระดับprocessและexchange | snapshotผูกprocess;exchangeมีsourcehash+row/column | ตรวจย้อนหลังได้ในsnapshotปัจจุบัน;hashยังไม่ใช่FKเข้าsourcecatalogทุกชั้น |
| PK/FK/NOTNULL/CHECK | มีทั้ง4DDLและpipelinevalidation | มีหลักฐานnegativechecksจริง แต่ไม่มีconstraintใดพิสูจน์sourceถูกต้องเชิงวิทยาศาสตร์ |
| Review/reject/release/rights | corporateและDMFแยกสถานะ/เหตุผล/release | เป็นส่วนที่เราเพิ่มจากตัวอย่างและช่วยทำซ้ำ/ไม่ปนpendingกับaccepted |

## จุดที่แก้จริงรอบนี้

ใน `sql/mysql/supplemental-schema.sql` เดิม CHECKของdirectionและroleตรวจแยกกัน จึงอนุญาตคู่ผิด เช่น INPUT+CO_PRODUCT และ OUTPUT+INPUT เพิ่ม `ck_exchange_direction_role` ให้ INPUTใช้INPUTเท่านั้น และ OUTPUTใช้OUTPUT/REFERENCE_PRODUCT/CO_PRODUCT

ใช้ข้อมูลสังเคราะห์เชื่อมFKครบในMySQLชั่วคราวเพื่อทดสอบvalidoutputcoproduct,invalidinputcoproduct,invalidoutputinputroleและrollback ไม่เติมแถวทดสอบในข้อมูลจริง ผลอยู่ evidence/mysql-transaction-audit.json

**ขอบเขตการเปลี่ยน:** DDLสำหรับสร้างฐานใหม่เท่านั้น `CREATE TABLE IF NOT EXISTS` ไม่อัปเกรดตารางเดิมอัตโนมัติ ยังไม่ได้ALTERฐานถาวร/EC2 ต้องตรวจค่าปัจจุบันก่อนเพิ่มconstraintด้วยmigrationที่ระบุเจ้าของฐานและrollbackpolicy เมื่อทำรอบmigrationจริง ห้ามอ้างว่าruntimeทุกฐานได้constraintใหม่แล้ว

## สิ่งที่ควรทำต่อโดยไม่ฝืนข้อมูล

1. ทำsource-IDcrosswalkให้registry/hash/API/exportโยงกันก่อนเปลี่ยนPKเดิม
2. แยกsource-localFLOWในcandidate schema โดยidentityมีsource/unit/context ไม่รวมชื่อเหมือนกันคนละความหมาย ต้องroundtrip16exchangesและqueryเท่ากันก่อนพิจารณาmigration
3. เก็บflow_type/compartmentเป็นunknownเมื่อsourceไม่ระบุ ไม่เติมair/waterจากชื่อสารอย่างเดียว
4. Unitmasterข้ามชุดต้องรักษาdimensionและdenominator เช่นm3/yearไม่ใช่m3 และBBL/DAYไม่ใช่MillionLitres ไม่ใช้ค่าตัวอย่างปัดเศษเป็นconversionที่ยืนยันแล้ว
5. คงcandidate normalizationแยกproduction ไม่อ้าง5NFจนพิสูจน์dependencies/losslessjoinsตามsemanticsจริง

เกณฑ์นำเสนอ: อธิบายrequirement→entity→relationship→constraint→query→evidenceให้ได้ ของเราเด่นด้านprovenanceและqualityworkflow ส่วนcoreLCIต้องระบุช่องว่างตรงๆ ไม่พูดว่าเหนือกว่าตัวอย่างทุกด้าน
