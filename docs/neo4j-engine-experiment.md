# Neo4j engine experiment — 28 ตุลาคม 2569

ทดลอง Neo4j Community5.26.32 จริงผ่านแล้ว หลักฐาน `evidence/neo4j-inventory-audit.json`: inventory16รายการ →39nodes/68relationships;4Cypher queriesแยกFAME/H-FAMEกับINPUT/OUTPUTตรงSQL;originalpayload16อ่านกลับตรง;Entity idซ้ำถูกUNIQUEปฏิเสธ

ก่อนแก้ containerหยุดexit3 ไม่มีOOMKilled;verboseระบุconfiguration invalidแต่neo4j-admin validate-configผ่านทั้งneo4j.conf/Log4j จึงไม่อ้างว่าพิสูจน์ไฟล์configเสียหรือRAMไม่พอ

เปลี่ยนnetwork=noneเป็นbridgeใหม่แบบ--internalที่ไม่publishพอร์ต และเปลี่ยนreadinessเป็นwgetแทนเปิดJVMcypher-shellซ้ำ พร้อมจำกัดJVMของshell ผลชุดisolationใหม่นี้เริ่มและqueryสำเร็จ ไม่อ้างroot causeภายในNeo4jทุกจุด

Labสร้างcontainer/networkชื่อสุ่มพร้อมownerlabel ตรวจownerก่อนลบหลังจบ ไม่แตะEC2/MySQL/เว็บproduction;reproduceด้วยscripts/audit_neo4j_inventory.py;Cypherจริงในbuild/neo4j-lab/import.cypherและqueries.cypher

ขอบเขตเฉพาะsource-reportedforegroundinventory16รายการ ไม่ใช่corporate97/fullLCI;ไม่อนุมานupstream/compartment;amountเก็บstringรักษาทศนิยม;ไม่มีperformanceclaim
