# Versioned inventory review schema

> ส่วนนี้อธิบายรุ่น 30 ต.ค. สำหรับ58รายการ รุ่นโมเดลกิจกรรม 5 พ.ย. เพิ่ม scenario/process instance/provider candidate/calculation run แยกอีกฐาน ดู [สถาปัตยกรรมปัจจุบัน](CURRENT_ARCHITECTURE.md) ไม่ได้เปลี่ยน MySQL production

30 ตุลาคม 2569 — local candidate สำหรับ58รายการ/5กระบวนการ ไม่ใช่การเปลี่ยนproductionMySQLเป็นSQLite

## สิ่งที่แก้ตามคำวิจารณ์ข้อ1/6/12

`scripts/build_versioned_inventory.py` สร้างฐานreviewแยกตามrelease hash:

| Relation / key | หน้าที่และdependency |
|---|---|
| source_observation / observation_id | ค่าต้นทางและoriginal payload;typed fieldsต้องตรงpayload;UPDATE/DELETEถูกปฏิเสธ |
| process_dataset_version / version_id | process,contract,referencebasis,referenceproduct,status;versionผูกกับcanonicalsource payloads;ไม่สมมติprocess_idเป็นkeyเพราะมีหลายรุ่นได้ |
| dataset_exchange / (version_id,observation_id) | สมาชิกของแต่ละรุ่น;triggerตรวจprocessตรงกันและปฏิเสธเพิ่มเมื่อsealed |
| numeric_parse_audit / observation_id | input lexeme,parser version,output decimal;ไม่มีunitconversion/allocation;insertต้องตรงoriginalและห้ามแก้ย้อนหลัง |
| review_export / view | joinกลับค่าต้นทางพร้อมversion/basis/statusโดยไม่เขียนทับsource |

versionสร้างจากข้อมูลเรียงตามobservationIDจึงไม่ขึ้นกับลำดับอ่าน;release hashครอบschemaและparser contractด้วย เมื่อเปลี่ยนsource/contextของprocessหนึ่ง versionprocessอื่นไม่จำเป็นต้องเปลี่ยน

Sealเป็นtransition0→1เท่านั้นและเปลี่ยนmetadataพร้อมsealไม่ได้ หลังsealห้ามแก้version/membership ถ้าเปลี่ยนต้องสร้างรุ่นใหม่ โครงนี้ยังไม่มีendpointให้ผู้ใช้เขียนข้อมูลหรือapplyallocation/provider

original_jsonเป็นsnapshotที่เก็บซ้ำโดยเจตนาเพื่อaudit ไม่ถือJSONหรือhashPKเป็นข้อพิสูจน์5NF ทั้งschema ไม่มีการอนุมานmultivalued/join dependenciesจากsnapshotเดียว และไม่มีการอ้างผลSQLiteว่าเป็นผลMySQLmigration

## การอ่านตัวเลขและfootnote

ตรวจDecimalจากraw_valueครบ58รายการอีกครั้งในparseaudit ใช้scientificnotationparserของTables1–3 และregexTable4เดิมที่อนุญาตfootnote `a` เฉพาะเมื่อannotationเป็น `Calculated power for semi-batch reactor` ดังนั้น `0.08 a` คงrawเดิม มีamount `0.08` และannotationเดิม ไม่ทำให้ตัวอักษรaหายจากหลักฐานและไม่ตีความว่าเป็นการวัดจริงของโครงงาน

## เกณฑ์ตรวจที่ผ่าน

- originalpayloadทุกfield58รายการอ่านกลับตรง รวมNULL/HOLD1รายการ
- negativechecks:แก้/ลบsource,แก้sealedversion,ผิดprocess,แก้numericparse,typed-payloadไม่ตรง,เปลี่ยนmembership ถูกปฏิเสธ
- insertหนึ่งแถวTEST_ONLYในmemoryแล้วแถวถัดไปผิดFK ทำให้ทั้งtransactionrollback;ไม่เพิ่มแถวสังเคราะห์ลงชุดวิจัย
- source valueที่ไม่ตรงraw lexemeถูกปฏิเสธ
- dataset versions5รุ่นsealedแล้ว;ไม่มีallocation/scaling/fullLCIclaim

รัน `python -m scripts.build_versioned_inventory` และ `python -m unittest tests.test_versioned_inventory` หลักฐานอยู่ `evidence/versioned-inventory.json` ไม่มีการสลับฐานบนEC2 ทดสอบengineMySQLสำหรับschemaใหม่นี้ยังไม่เกิดขึ้น;รอบนี้DockerCLIไม่คืนผลจึงหยุดคำสั่ง ไม่แตะcontainer/volumeใด

## การตัดสินใจเรื่องproduction

ระบบที่เปิดเว็บยังเป็นMySQLread-onlyตามreleaseเดิม การmigrationเพื่อให้มีชื่อtableใหม่เพียงอย่างเดียวไม่ช่วยเติมallocationหรือbackgroundและเพิ่มความเสี่ยง จึงเก็บcandidateนี้เป็นหลักฐานออกแบบ/ทดสอบ ก่อนmigrationจริงต้องมีMySQLequivalentDDL,engineconstrainttests,typedjoin/APIparity,ownercheck/backup/rollback ไม่ทำเครื่องหมายproductionmigrationเสร็จ

## อัปเดต31ตุลาคม2569: MySQLengineตรวจจริงแล้ว
เพิ่มsql/mysql/versioned-review.sqlและscripts/verify_versioned_mysql.py ทดสอบMySQL8.4.13ในschemaชั่วคราวเฉพาะของเราบนownedruntime ตรวจownerก่อนทำ:58fullpayload/typedjoinsตรง,5sealedversions,1NULL/HOLD,8negativecasesต้องได้ERROR1644ที่คาดและlatebatchFKต้องERROR1452พร้อมrollback59→58 จากการปิดconnectionเมื่อclientabort ไม่เหมารวมว่าSQLerrorทุกกรณีrollbackทั้งbatchเอง ลบเฉพาะschemaที่สร้างรอบนี้หลังตรวจowner marker;containerIDsเดิมไม่เปลี่ยน/APIreadyหลังจบ หลักฐานevidence/versioned-mysql.json ไม่ใช่productionmigration ไม่แก้grant/port/Ginder/Caddy
