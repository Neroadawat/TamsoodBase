# สถานะที่ต้องบอกตามจริง

- DMF raw34905/structural34899/reject6/deduplicatedpending34671; historicaltimebasisยังไม่ยืนยัน ไม่เป็นacceptedLCI
- corporate101sourceobservations/97ACCEPTED_REFERENCE/4HOLD_CONTEXT; rightsยังไม่ยืนยันสำหรับแจกจ่าย ไม่ใช่97normalizedflows
- NSO273staged; cross-sourceเทียบ15distinct อีก258ยังไม่เทียบ ไม่ใช่independentmeasurements15ครั้ง
- EPPO5934staged แยกcompanyrateกับnationalquantity ไม่สร้างyieldและไม่annualize2026partialyear
- inventory16เป็นsource-reportedproductinventoryฐาน1000MJfuel;ปีวัดไม่ระบุ ไม่ใช่fullLCIdataset;BHD8แยกตามgeography
- normalizationcandidateผ่านlossless/constraints/catalogcomparisonในฐานทดลอง ยังไม่แทนproductionและไม่รับรอง5NF
- มีSQLitetransactionlabเดิมและMySQL/InnoDBisolatedlab17checksจริง ไม่อ้างpowerfailure;Neo4jstartup2รอบไม่สำเร็จจึงยังอ้างได้เฉพาะlocalgraphprojection
- เว็บ/APIใช้SQLite/JSONsnapshots MySQLใช้localDockerสำหรับrelationalimplementation/verification วันที่27ตุลาคมEC2อัปเกรดเป็นc2d8db16b10a2fadและS3configถาวรแล้ว backup39membersdownloadhashผ่าน ยังไม่เปิดpublicHTTPS/frontend;rollbackตรวจpreflightแต่ไม่สลับย้อนจริง
- testsล่าสุด104ผ่าน และEC2stage/active17routesผ่าน ไม่อ้างว่าทุกการทดลองเดิมถูกรันใหม่ในรอบsetup
- SourceIDcrosswalk13snapshotsและinternalCSV/JSONL41,223observationsเป็นadditivecontract ไม่ใช่41,223acceptedLCI;APIเดิมคงfieldเดิม
- Flow/Unitcandidate16exchangesตรวจtypedjoin/fullpayloadและ4queriesตรงกัน แยกฐานไม่ใช่productionmigration DDLconstraintใหม่ผ่านfreshisolatedMySQLแต่ยังไม่ALTERฐานเดิม
- ผลซ้อม/สมาชิก/peerassessmentยังต้องมนุษย์จริง วันส่งและรูปแบบล่าสุดต้องตรวจประกาศAssignmentจริง

นี่คือข้อจำกัดของหลักฐาน ไม่ใช่ข้ออ้างให้แก้ตัวเลขต้นทางหรือลดเกณฑ์เพื่อให้ผ่าน
