# ข้อมูลข้ามแหล่ง — 28 ตุลาคม 2569

เทียบใหม่12ค่า NSO13.10 ปี2022/2023กับDEDE Energy Balance2023 ตาราง14 PDFหน้า38/หน้าพิมพ์24:ถ่านหิน/น้ำมันสำเร็จรูป/ก๊าซธรรมชาติ/ไฟฟ้า/พลังงานหมุนเวียน/รวมยอด ปีละ6ค่า ทั้ง12ตรงตามค่าพิมพ์

Coverageเพิ่มจาก15เป็น27/273 เหลือ246รายการ ไม่เพิ่มobservationsหรือแก้sourcevalue ไม่ใช่การวัดอิสระเพราะNSOเผยแพร่DEDEต่อ

ต้นทาง [PDF2023](https://www.dede.go.th/uploads/2566_forweb_b67cef3cc6.pdf) และ [DEDE catalog](https://pei.dede.go.th/en/dataset/2566-energy-balance-of-thailand-2023);เก็บPDF/hash/เวลาที่ดึงในprivate data/raw/dede/balance-2023/ ไม่แจกraw CatalogระบุCreative Commons Attributionsแต่ไม่ระบุเวอร์ชัน ไม่เปลี่ยนสิทธิแหล่งอื่น

ตรวจภาพrenderตารางร่วมกับpdfplumber coordinates,ปีพ.ศ./ค.ศ.,หัวตาราง,หน่วยktoeและ5components=totalก่อนเทียบNSOidentity ผลรายค่าในevidence/nso-dede-historical.json;coverageในevidence/cross-source-coverage.json

NSOreporthashเดิมไม่เปลี่ยน ผลรอบนี้เป็นหลักฐานในrepository ยังไม่ได้เปลี่ยนcomparisonartifactบนEC2 จึงไม่อ้างว่าเว็บแสดงcomparisonชุดใหม่นี้แล้ว SRSพักตามคำสั่งผู้ใช้
