# Primary supply ปี2024 — 28 ตุลาคม 2569

ใช้DEDE revised workbookเดิมที่ตรวจhashแล้ว ไม่ดาวน์โหลดซ้ำ สกัดแถวTOTAL PRIMARY ENERGY SUPPLYของsheetktoe ตรวจปี/unitและหัวเชื้อเพลิงแต่ละคอลัมน์ก่อนอ่านvalue

เพิ่ม14comparisonsที่บริบทตรงNSO13.5:13exact;อีก1ยอดรวมNSO136320กับDEDE136319.6ต่าง0.4 อยู่ในhalf-step0.5ของintegerdisplay ไม่ใช่exactmatch รักษาค่าทั้งคู่ ดูevidence/nso-dede-primary-2024.json

คงค่าลบnatural gasoline-23/petroleum products-6765ตามต้นทาง ไม่ใช้absolute แอนทราไซต์ต้องอ่านE24พร้อมE5='แอนทราไซต์' ไม่อ่านคอลัมน์ข้างเคียง และลิกไนต์ใช้U24ที่เป็นยอดรวมพร้อมO5/U7guards

ยังไม่เทียบrenewable/other-energyที่มีการรวมองค์ประกอบต่างกัน ไม่รวมค่าหลายคอลัมน์เองเพื่อให้ตรงNSO ไม่อ้างการวัดอิสระเพราะNSOนำสถิติDEDEมาเผยแพร่ต่อ

รวมสถานะปัจจุบัน159/273:131exact,24rounding-compatible,4source-divergence;114ยังค้าง แบ่ง36ตารางปี2024,3aggregate scope,27fuelclassification,21ปี2025ไม่มีDOEBsnapshot,9mass-vs-volume,18percentไม่มีexternalcellตรง

เพิ่มregressiontestsสำหรับheaderเชื้อเพลิงผิด,ปีผิด,booleanที่ไม่ใช่numeric,เครื่องหมายค่าลบ และแยกroundingออกจากexact ผลใหม่ยังเป็นrepo evidence ไม่ได้อัปเดตcomparisonartifactของEC2หรืออ้างlive-source freshness
