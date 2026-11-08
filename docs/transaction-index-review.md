# Transaction และ Indexing: เทียบเว็บอาจารย์กับผลทดลองจริง

27 ตุลาคม 2569 · [บทเรียนทางการ](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-txn-index.html)

หน้าเว็บให้ใช้ transaction เพื่อโหลดเป็นชุด, ตรวจเงื่อนไขก่อน commit และ rollback เมื่อไม่ผ่าน อธิบาย ACID/isolation และให้โยง index กับ requirement พร้อม EXPLAIN ในบท5/7 ไม่ได้กำหนดให้คัดลอกชื่อ lci_exchange ตัวอย่างมาแทน schema จริงของทีม

## สิ่งที่เพิ่มและผลจริง

เดิมมีเพียง SQLite lab บนสำเนา EPPO ตอนนี้เพิ่ม `scripts/audit_mysql_transactions.py` ทดลอง MySQL8.1/InnoDB ใน container ชั่วคราวไม่มี network/port/volumeร่วม ใช้แถวสังเคราะห์ที่ระบุชัด ไม่เพิ่ม observation หรือเปลี่ยนฐานใช้งาน ลบ container ของ lab หลังจบแล้ว

| การทดลอง | สิ่งที่สังเกตจริง | ความหมาย |
|---|---|---|
| UPDATEแรกสำเร็จ UPDATEที่สองผิดCHECK | ค่าแรกยัง11.000จนกว่าจะROLLBACK | statement error ไม่ใช่ automatic whole-batch rollback |
| Explicit ROLLBACK | ค่ากลับ10.000/20.000 | application ต้องจัดการ transaction ทั้งชุด |
| CHECK amountไม่ติดลบ | error3819และค่าที่ผิดไม่เข้า | consistencyเฉพาะconstraintที่ประกาศ ไม่รับรองความหมายLCI |
| READ COMMITTED | ไม่เห็นค่าค้างcommit;อ่านอีกครั้งหลังcommitเห็นค่าใหม่ | กันdirtyread แต่เกิดnon-repeatablereadได้ |
| REPEATABLE READ / plain SELECT | ค่าเดิมและจำนวนแถวช่วงเดิมคงเดิมในsnapshot | consistentreadของInnoDBไม่ควรถูกเหมารวมจากตารางSQLมาตรฐานเรื่องphantom |
| เริ่มtransactionใหม่ | เห็นแถวที่commitเพิ่มแล้ว | ขอบเขตsnapshotเปลี่ยน |
| SELECT FOR UPDATE แล้วwriterอีกsession | error1205และค่าไม่ถูกทับ | rowlock/timeout ต้องมีrollback/retry policyของงานจริง |
| เปิดclientใหม่หลังcommit | เห็นค่าที่commit | reconnect persistence ไม่ใช่power-loss durabilitytest |

17 checks ผ่าน (เพิ่ม4checksตรวจDDLจริงเรื่องdirection/roleในรอบschemareview) ดู [ผล MySQL](../evidence/mysql-transaction-audit.json) เทียบ [ผล SQLite เดิม](../evidence/transaction-audit.json) ยังไม่ได้ทดลอง READ UNCOMMITTED/SERIALIZABLE,crash/powerloss หรือ production load ไม่ใช้ผลนี้รับรองทุก isolation behavior

## นำไปใช้กับ pipeline อย่างไร

แยก schema DDL ออกจาก transaction โหลด เพราะ MySQL DDL หลายคำสั่งทำ implicit commit อย่าคิดว่า CREATE TABLE จะย้อนพร้อม INSERT เสมอ Parsing/quality gate สามารถเก็บ reject ใน staging ได้ แต่ชุดที่เลือกนำเข้า target ต้องมีขอบเขต transaction ชัดเจน

SQLite EPPO importer มี typed/payload/metadata verification ก่อน commit และ rollback เมื่อผิดแล้ว ส่วน MySQL batch loaders ใช้ mysql CLI แบบไม่เปิด --force: SQL error จบ sessionและrollbackงานที่ยังไม่commit การเปรียบเทียบ roundtrip บางloaderทำหลังCOMMIT จึงเป็นการตรวจหลังโหลด ไม่ใช่ precommit semantic gate ทั้งหมด ห้ามเขียนรายงานเหมารวมว่าทุกloaderตรวจทุกfieldก่อนcommit

สคริปต์ lab ใช้ --force เฉพาะเพื่อสังเกต statement error แล้วสั่งROLLBACKเอง **ไม่ใช่รูปแบบที่ควรเปิดใช้กับ production batch importer** หากเพิ่ม streaming importer ต้อง catch exception→ROLLBACK และตรวจ expected row count/identity/metadata ก่อนCOMMIT การ retry หลังdeadlock/timeoutต้องทำทั้งtransactionอย่างidempotent ไม่retryแค่แถวที่ล้มโดยไม่อ่านสถานะ

## Index และ EXPLAIN ที่มีแล้ว

[sql-performance.json](../evidence/sql-performance.json) เป็นหลักฐานจริง22ตุลาคมของ DMF34899observations: query period2026-01ได้102แถว ทั้งใช้indexและIGNORE INDEXคืนผลhashเดียวกัน หลังwarmupอย่างละ1แล้ววัดสลับ5ครั้ง medianserveriterator0.208msกับ12.0ms เป็น local warm-cache ไม่ใช่ API latency/SLA และไม่ใช่ทดลองCREATE/DROP indexก่อนหลังจริง baselineใช้IGNORE INDEX

`ix_period_context(period_start,context_id)` โยง R01/FR-01 การค้นช่วงเวลาและcontext หลัก leftmostprefixอธิบายได้ แต่ผลทดลองนี้ยังไม่พิสูจน์queryที่กรองcontext_idอย่างเดียวเร็วขึ้น ไม่เพิ่มindexทุกcolumnเพราะมีพื้นที่และwritecost และไม่ได้วัดwriteoverheadในหลักฐานนี้ ตารางเล็กfullscanอาจเป็นแผนที่ถูกต้อง

## ตำแหน่งในรายงาน

- บท5.2: ชื่อindex/workload/SQL/EXPLAINและความเท่ากันของผล
- บท5.3: transaction boundary, rollbackเหตุใด, SQLconstraintกับsemanticgateต่างกัน
- บท6: FR-06/NFR-02→import/replay/transactionlab และ NFR-06→performanceevidence
- บท7: แนบผลจริงแยกMySQL/SQLiteและข้อจำกัด ไม่อ้างpowerfailureหรือproductionmigration

รันlabเมื่อเปลี่ยนการทดลองหรือมีข้อสงสัยใหม่: `python -X utf8 scripts/audit_mysql_transactions.py` ต้องมีDockerและcachedmysql:8.1 ไม่แตะcn230-db-1หรือEC2
