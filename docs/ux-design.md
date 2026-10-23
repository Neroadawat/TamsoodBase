# UX pass — 23 October 2026

เป้าหมาย: ค้นง่าย อ่านง่าย เปิดต้นทางสะดวก บนคอมและมือถือ ใช้เว็บในเครื่องเดิม ไม่เผยแพร่ dataset หรือ deploy

## Reference ที่อ่าน

- [Our World in Data: redesign](https://ourworldindata.org/redesigning-our-interactive-data-visualizations): ใช้แนวคิด contrast ของตาราง, การจัดแนวตัวเลข, ที่มาที่เปิดดูได้ และ download ที่อยู่ใกล้ข้อมูล
- [World Bank Open Data](https://data.worldbank.org/indicator/index): ใช้แนวคิดค้นจากชื่อข้อมูลและเลือกเงื่อนไข พร้อม download ใกล้ผลลัพธ์

เป็นการประยุกต์ interaction และลำดับข้อมูล ไม่คัดลอก code, artwork หรือ branding และไม่อ้างว่าเว็บเราเป็นขององค์กรเหล่านั้น

## ปรับจริง

- หน้าแรกเริ่มที่ reference ที่รับตามนโยบายทีม แยกจาก DMF pending research
- แสดงสถิติ DMF เฉพาะเมนูสำรวจ/คุณภาพ เพื่อไม่ดันตัวค้นหาของ reference ลง
- ปรับตัวอักษร controls/table หลักเป็น 14px พร้อม line-height และ contrast มากขึ้น
- ปุ่มหลักสูงอย่างน้อย44px, focus ring, skip link, dialog accessible name และ aria-current สำหรับเมนู
- ตารางแถวสลับสี/hover, sticky header, เลขและหน่วยอยู่ด้วยกัน
- ข้อจำกัดยาวอยู่ใน details ที่เปิดอ่านได้ ไม่ลบคำอธิบายสิทธิหรือความหมายข้อมูล
- reference มีปุ่มล้างทั้งหมดและ empty state พร้อมคำแนะนำ
- เมนูมือถือ wrap ให้ทุกเมนูเห็นได้ แทนการให้ปุ่มแต่ละอันกว้างเต็มจอในแถบเลื่อน

## ตรวจ

JavaScript syntax ผ่าน Node; explorer tests5ผ่าน ตรวจ browser จริงที่ขนาดปกติและ390×844: หน้า reference โหลด97, ค้นข้อความที่ไม่มีผลแสดง0พร้อมคำแนะนำ, reset กลับ97; บันทึกภาพ build/explorer/ux-desktop.png และ ux-mobile.png การตรวจนี้ยังไม่ใช่ usability study กับคนจริงหรือการรับรอง WCAG ทุกข้อ


## ปรับจาก EPPO — 23 ตุลาคม 2569

ตรวจ https://data.eppo.go.th/Oil ใน browser พบการแบ่งหมวดและ topic พร้อมไฟล์ Current/Month/Quarter/Year; static web reader เดิมแสดง No data จึงไม่ใช้ผลนั้นสรุปว่าไม่มีรายงาน หลักฐาน candidate อยู่ evidence/eppo-catalog-review.json ยังไม่ import ค่าจาก Excel

หน้าเริ่มต้นใหม่เป็น catalog 4 กลุ่ม: DMF, NSO, องค์กร และงานวิจัย ค้นชื่อหรือคำเกี่ยวข้องและกรองระดับได้ แต่ละการ์ดบอกขอบเขต/เวลา/ข้อจำกัดและมีปุ่มไปหน้าเดิม ไม่รวมจำนวนต่างชนิดให้ดูเหมือน accepted เดียวกัน เพิ่มลิงก์ EPPO ในรายละเอียดแหล่งเพิ่มเติมพร้อมป้ายยังไม่ได้นำเข้า

ตรวจจริงใน browser: เริ่ม4ชุด, ค้นดีเซลพบ2ชุด (รวมไบโอดีเซล), เลือกระดับ product พบ1, คำไม่พบแสดงempty state, resetคืน4; ปุ่มNSOเปิดตาราง13.6จำนวน69ค่า/ทั้งชุด273ได้ ตรวจmobile390pxเป็นคอลัมน์เดียวไม่มีhorizontal overflow คืนviewportเดิมแล้ว JS syntaxผ่านและ explorer tests5ผ่าน ไม่อ้างuser study
