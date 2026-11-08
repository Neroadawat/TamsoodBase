# นำหัวข้อ CN230 มาใช้ใน TamsoodBase

ทบทวน25ตุลาคม2569 จาก Student Course Syllabus Version1.0 วันที่30กรกฎาคม2569 จำนวน11หน้า ที่ผู้ใช้แนบในแชต: ชื่อเอกสาร `[TSE69(1)-Syllabus-CN230-TABEE-V1] Database Systems.pdf` หน้าที่3คือCLO, หน้า4แผนรายสัปดาห์, หน้า5–6เกณฑ์โครงงาน ไม่ใช่ประกาศแก้ไขล่าสุดของTeams

## หัวข้อเรียนกับงานจริง

| สัปดาห์ / หัวข้อหลักหน้า4 | นำมาใช้ในโปรเจกต์ | หลักฐาน / ข้อจำกัด |
|---|---|---|
| W01 Introduction | แยกdata/information/database; จำนวนแถวไม่เท่ากับข้อมูลใช้ต่อได้ | requirements.md, team-data-policy.md |
| W02 DBMS | แยกstorage/pipeline/API/frontend; SQLiteสำหรับsnapshot, MySQLสำหรับrelational verification | dataset-model-index.md, ec2-backend.md; เว็บยังไม่ได้queryMySQLโดยตรง |
| W03 Requirements | ออกแบบจากคำถามใช้งานและbusiness rules | requirements.md R01–R14 |
| W04 ERD | identity,entity/attribute,cardinalityตามsemanticsของแหล่ง | database-design.md, reusable-model.md; ไม่บังคับทุกแหล่งเป็นprocessLCI |
| W05 Relational Model | ERD→tables/PK/FK/UNIQUE/CHECK | sql/mysql/*schema.sql และผลnegative checks |
| W06 Database Design Practice | เชื่อมrequirement→model→schema อธิบายtrade-offs | dataset-model-index.md; มีหลายschemaเพราะboundaryต่างกัน |
| W07 Schema Development | ทบทวนFD/constraintsก่อนเปลี่ยนschema | normalization-audit.md; candidateSQLite/MySQLแยกฐานยังไม่แทนproduction |
| W08 SQL Fundamentals | DDLสร้างโครงสร้าง, DMLโหลดข้อมูล, DQLตอบคำถาม | sql/mysql/, build load artifacts และREADME |
| W09 Definition/Manipulation | INSERT/UPDATEอยู่ในtransactionและมีconstraint; ไม่สาธิตDELETEกับproduction | import_eppo.pyตรวจtyped/source metadataก่อนcommit; transaction experimentใช้สำเนาทิ้ง |
| W10 Querying | SELECT/JOIN/GROUP BY/subquery/viewsตามuse caseและrelease | reusable-queries.sql, full-queries.sql; ไม่SUMข้ามหน่วยหรือtotalกับcomponents |
| W11 Normalization/Integrity | วิเคราะห์FDและlossless join ลดupdate anomalies | normalization-audit.md, normalization-mysql.json; syllabusหน้า2ระบุ1NF–3NF ไม่ได้บังคับ5NFทุกตาราง |
| W12 Graph | เปรียบเทียบpathของprovenanceกับrelationalJOIN | data-model-selection.mdเป็นdesign comparison; ยังไม่มีNeo4j/Cypher run evidence |
| W13 Transaction/Index | rollbackทั้งtransactionเมื่อconstraintผิด, isolationระหว่างconnections, writer lock, commit/reopen; indexจากworkloadจริง | เพิ่มtransaction-audit.json; sql-performance.jsonเป็นผลindexเดิม ไม่ปนผลSQLiteกับMySQL |
| W14 NoSQL/Modern | JSONเหมาะกับmetadataต่างรูป; เลือกtechnologyตามquery/constraints | data-model-selection.md; JSONfileไม่เท่ากับได้ทดลองMongoDBแล้ว |
| W15 Integration/Reflection | เชื่อมsource→requirements→schema→SQL→quality→demo และอธิบายข้อจำกัด | handbook-alignment.md, demo-and-defense.md, pipeline-audit.md; reflection/contributionต้องสมาชิกจริง |

ตารางงาน/หลักฐานในsyllabusหน้า4มีคำด้านarchitectureปะปน เช่นSOLID/Pattern/UML จึงยึดหัวข้อหลัก/CLOและข้อกำหนดprojectหน้า5–6 ไม่สร้างงานย่อยนอกโปรเจกต์เพื่อไล่ชื่อให้ครบ ไม่ถือว่าเอกสารmappingนี้คือการส่งงานรายสัปดาห์แล้ว

## สิ่งที่เพิ่มให้ทำงานจริงในรอบนี้

`python -X utf8 scripts/audit_transactions.py` อ่านEPPO databaseแบบread-onlyแล้วbackupไปtemporarydirectory ใช้schema/dataสำเนาเดิมในการทดลอง:

1. เปลี่ยนamountในtransactionแล้วสั่งmonth=13ให้CHECKล้ม ต้องrollbackทั้งการเปลี่ยนamountและmonth
2. อีกconnectionต้องไม่อ่านamountที่ยังไม่commit
3. ระหว่างBEGIN IMMEDIATE writerอีกตัวต้องได้SQLITE_BUSY จึงไม่แอบเขียนพร้อมกัน
4. หลังcommitอีกconnectionต้องเห็นค่าที่เปลี่ยน และปิดเปิดconnectionใหม่ยังอ่านได้
5. SHA256ฐานต้นทางต้องเหมือนก่อนทดลอง สำเนาทดลองถูกลบอัตโนมัติ ค่าทดลองไม่เข้าreport/export/จำนวนแข่งขัน

ผลจริงอยู่ `evidence/transaction-audit.json` ผ่าน6checksบนSQLite3.45.3 นี่เป็นหลักฐานACIDบางส่วนในขอบเขตที่ทดลอง ไม่ใช่การพิสูจน์power-loss durability/production concurrency หรือMySQL isolation levelsทั้งหมด ยังไม่จำเป็นต้องเปลี่ยนฐานของเว็บเพื่อให้มีหลักฐานนี้

## CLO และส่วนที่ยังต้องทำโดยคน

- CLO2–3: requirements/model/schema/SQLมีหลักฐานใช้งาน แต่สมาชิกต้องอธิบายidentityและJOINของตนได้
- CLO4: มีFD/integrity/indexและเพิ่มtransaction evidenceจริง ไม่อ้างnormal formสูงเกินที่พิสูจน์
- CLO5: มีselection rationaleแล้ว ส่วนhands-onNeo4j/MongoDBของรายวิชายังไม่ถูกอ้างว่าครบจากโปรเจกต์นี้ หากข้อกำหนดFinalเรียกหลักฐานengineจริงค่อยทำแยกตามคำสั่งนั้น
- CLO6: ระบบlocalใช้งานได้และมีgovernance;26ตุลาคมอัปเกรดEC2privateและเชื่อมS3ถาวร/backupตรวจกลับแล้ว ส่วนpublicHTTPS/accesscontrol/frontendยังค้าง ดูPRIVATE_BACKEND_OPERATIONS_TH.md
- CLO7: peer assessment, contributionและindividual defenseยังต้องเกิดจริง ไม่ให้AIกรอกแทน

หน้า5ยืนยันMiniProject15%ในรุ่นนี้ และหน้า6กำหนดSQL/schema/repository/evidenceพร้อมการอธิบายรายคน ไม่ใช้จำนวนข้อมูลหรือเว็บสวยเป็นหลักฐานแทนความเข้าใจฐานข้อมูล
