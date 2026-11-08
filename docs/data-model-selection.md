# เลือกแบบจำลองข้อมูล — CLO5

**สถานะล่าสุด30ตุลาคม:** productionAPIใช้MySQLบนEC2 มีNeo4jจริงเฉพาะinventory16รายการในlab ดูevidence/neo4j-inventory-audit.json ข้อความ27ตุลาคมถัดไปเป็นประวัติprojectionก่อนทดลองengine ไม่ใช่สถานะล่าสุด

รอบทบทวนFinalProject27ตุลาคมเพิ่มinventorygraphจริงจากsource16รายการ มีProcess/Exchange/Flow/Unit/Source/Location พร้อม4process-directionqueriesตรงSQLite/JSONเก็บbasis/boundary/Decimal/periodnull/roleครบ ดูfinal-project-system-review.md ยังเป็นPythonprojection ไม่ใช่Neo4jengine;ไม่สร้างflowclassification/upstreamlinkขึ้นเอง

อัปเดต25ตุลาคม: มีlocalprojectionexperimentแล้ว `scripts/compare_data_models.py` เปรียบเทียบSQL/JSON/Pythongraphtraversalจากreference97รายการ ได้8publisher/yearqueriesตรงกันทั้งหมด เก็บ101nodes/99edgesในbuild/model-comparison/โดยคงrights/source/statusของobservation ดูevidence/model-comparison.json ยังไม่มีNeo4j/MongoDBengineหรือperformancebenchmark การทดลองนี้ไม่เปลี่ยนproductionmodelและไม่นับข้อมูลเพิ่ม

อ้างอิงตารางCLOหน้า3ของคู่มือภาพถ่าย และขอบเขตcanonical modelหน้า6 รายงานนี้เป็นการเปรียบเทียบทางออกแบบจากระบบจริง ไม่ใช่ผลbenchmark graph database

| รูปแบบ | งานที่เหมาะในโครงงาน | ข้อจำกัด | การตัดสินใจปัจจุบัน |
|---|---|---|---|
| Raw CSV/PDF/HTML + manifest | รักษาค่าต้นฉบับ ตาราง/หน้า/บรรทัด และhashเพื่อreplay | ค้นข้ามแหล่งยาก หน่วยและบริบทไม่เป็นมาตรฐาน; rawไม่เท่ากับaccepted | เก็บภายในตามสิทธิ แยกจากข้อมูลที่เว็บค้นและไม่แจกrawสิทธิไม่ชัด |
| JSON document | เก็บsource metadata/payloadที่fieldต่างกัน, reportและAPIexport | โครงสร้างยืดหยุ่นทำให้fieldหายได้; payloadตรงแต่typed columnsผิดได้ | ใช้เก็บหลักฐานและส่งAPI พร้อมschema/rule/roundtrip checks; T39/T42ตรวจtypedและpayloadแยกกัน |
| Relational SQLite/MySQL | identity, PK/FK, reference lookup, release membership, JOIN/filter และnegative constraints | ต้องmappingก่อนโหลด; การรวมคนละscopeในตารางเดียวอาจทำให้ความหมายผิด | ใช้เป็นฐานข้อมูลมีโครงสร้าง SQLiteรองรับเว็บsnapshot; MySQLตรวจเชิงสัมพันธ์ในlocalDocker แยกตามชั้นข้อมูล |
| Graph | สำรวจเส้นทางobservation→metric→context→document→publisher หรือbatch/validationหลายทอด | ต้องกำหนดidentityและsemanticsเช่นเดิม ไม่แก้unit/rights/duplicateเอง; เพิ่มระบบดูแลและqueryอีกชุด | มีการทดลองNeo4jจริงเฉพาะinventory16รายการแล้ว:39nodes68relationships/4queriesตรงSQL;productionยังใช้MySQL ไม่อ้างgraphเร็วกว่า |

## ตัวอย่างเส้นทางเดียวกัน

หนึ่งcorporate observationอ้างmetric/context/documentและreview/release ในSQLใช้FKและJOINเพื่ออ่านค่า/หน่วย/ปี/locator/decisionตามreleaseที่เลือก ในJSONexportค่ากับmetadataอยู่ในrecordเดียว ส่วนgraphอาจแทนด้วยnodesและedgesตามidentityเดียวกัน การทำJSONหรือgraph projectionจากobservationเดิมไม่ใช่ข้อมูลใหม่และห้ามนับเพิ่ม

Rawช่วยตอบว่าอ่านอะไรมา Relationalช่วยบังคับความสัมพันธ์ JSONช่วยส่งรายละเอียดที่ผู้ใช้ต้องอ่าน Graphอาจช่วยสำรวจความเชื่อมโยง ไม่มีรูปแบบใดรับรองความถูกต้องเชิงโดเมนโดยลำพัง

## ขอบเขตหลักฐาน

- คำสั่งSQLจริง: `sql/mysql/reusable-queries.sql` และ schemaแต่ละชุดใน `sql/mysql/`
- ตัวอย่างAPI/exportและข้อจำกัด: `reusable-model.md`, `eppo-source.md`
- หลักฐานตรวจจริง: `pipeline-audit.md`, `evidence/live-mysql-audit.json`
- มีNeo4j5.26.32ในinternalnetworklabตามevidence/neo4j-inventory-audit.json;16inventoryrecords/39nodes/68relationships/4queriesตรงSQL/uniquenessnegativecheckผ่าน ไม่ใช่productiongraph ไม่อ้างgraphเร็วกว่าSQLหรือgraphครบทุกชั้น
