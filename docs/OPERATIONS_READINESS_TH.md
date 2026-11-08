# ตรวจความพร้อมการดูแลระบบ

รัน `python -m scripts.check_operational_readiness` เพื่อตรวจpublicready/modelidentityและอายุหลักฐานbackupที่บันทึก ไม่restartหรือสร้างautomation. Exit0=เกณฑ์ครบ;exit2=ยังมีgateเปิด เช่นQuickTunnel แม้HTTP/backupผ่าน.

6พฤศจิกายน:backupใหม่S3AES256และrestoreครบ5ฐานในMySQLแยกผ่าน ข้อมูลเรียงPKทั้ง56,887,016bytes/hashตรงlive. Evidence/mysql-backup-latest.json และmysql-restore-2026-11-06.json. ไม่ใช่wholemachineDR/APIloadtestหรือหลักฐานของbackupอนาคต.

ยังต้องstablehostname/monitorowner/retentionpolicyและscheduleที่อนุญาตจริง. ไม่แตะGinder/Caddy/SG/ซื้อdomainเพื่อให้gateดูผ่าน. Productionupgradeต้องownercheck/testedpackage/backup/rollback. ห้ามเผยprivatearchivesหรือrowdata.
