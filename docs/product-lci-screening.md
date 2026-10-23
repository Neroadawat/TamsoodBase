# การคัดแหล่งสำหรับ LCI ต่อผลิตภัณฑ์

ทบทวน 23 ตุลาคม 2569 เพื่อทำ T18 โดยไม่บังคับให้ข้อมูลอ้างอิงกลายเป็น product LCI และไม่เพิ่มจำนวน observations จากข้อมูลอธิบายวิธีการ

| แหล่งที่ตรวจ | สิ่งที่มีจริง | สิ่งที่ยังขาดสำหรับ product LCI | ผลคัด |
|---|---|---|---|
| Thai Oil sustainability report 2024, subset ในเครื่อง | พลังงานรายปี 5 บริษัท และ refinery throughput พร้อม reported intensity | numerator หลายบริษัทไม่ตรง denominator โรงกลั่น; ไม่มี allocation ให้ผลิตภัณฑ์เชื้อเพลิงแต่ละชนิด | คง source-specific reference; ไม่หารเพิ่ม |
| SPRC sustainability report 2024, subset ในเครื่อง | เชื้อเพลิงรายปี และ GJ/t throughput ตามรายงาน | throughput ไม่ใช่ผลิตภัณฑ์อ้างอิงที่เลือก; report boundary มี distribution/marketing; ไม่มี allocation รายผลิตภัณฑ์ใน subset | คง REPORTED_INTENSITY; ไม่เปลี่ยนเป็น GJ/t diesel |
| [PTTGC: Life Cycle Assessment](https://sustainability.pttgcgroup.com/en/environment/product-stewardship/life-cycle-assessment) | หน้าเว็บอธิบาย LCA และสัดส่วนการประเมินผลิตภัณฑ์ | ในหน้าที่อ่านไม่มีตาราง numerical inventory exchanges ต่อหน่วยผลิตภัณฑ์เชื้อเพลิง | candidate methodology/context เท่านั้น; ไม่ ingest ตัวเลขสัดส่วน LCA เป็น flows |
| [MTEC: ฐานข้อมูล LCI](https://www.mtec.or.th/tiis/lci-database/) และ documentation ที่ตรวจไว้ใน mtec-alignment.md | ขอบเขตบริการ/metadata ตัวอย่าง natural gas | รอบนี้ไม่มี numerical exchange table ที่เข้าถึงและนำมาใช้ได้พร้อม evidence/rights | ใช้เป็นตัวอย่างการกำหนดบริบท ไม่คัด metadata เป็น exchange |

วิธีตรวจรอบนี้: อ่านข้อความหน้าเว็บทางการ PTTGC และ MTEC ผ่าน web tool; สำหรับรายงานสองบริษัทอ้าง subset และการตรวจ PDF ที่บันทึกไว้ ไม่อ้างว่าตรวจรายงานทุกหน้าหรือทุกฐานข้อมูลบนอินเทอร์เน็ตแล้ว

## กฎเมื่อพบแหล่งใหม่

1. มี process/site/boundary และช่วงเวลาที่ชัดเจน
2. มี reference product หรือ reference flow พร้อม amount และ unit จริง
3. ค่า input/output อยู่ในขอบเขตและช่วงเวลาเดียวกับตัวหาร
4. แยก inventory substance/energy ออกจาก impact score เช่น CO2e และ corporate performance indicator
5. ถ้ามีหลายผลิตภัณฑ์ ต้องมีวิธี allocation หรือเหตุผลว่าไม่ต้อง allocation ที่อ้างอิงได้
6. เก็บ source page/table/cell, ค่าดิบ, วิธีคำนวณ และเงื่อนไขใช้ข้อมูล

ถ้าไม่ครบให้คง reference/context หรือพัก ไม่คำนวณย้อนจาก intensity ที่ปัดเศษ ไม่ใช้ conversion factor จากคนละบริบทมาปิดช่องว่าง

ผลปัจจุบัน normalized product LCI = 0 ไม่เปลี่ยน release 97 accepted references / 4 holds และไม่เปลี่ยนสิทธิแจกจ่าย งาน T18 ยังไม่เสร็จเพราะยังไม่มีแหล่งที่ผ่านกฎครบ การค้นรอบต่อไปควรเริ่มเมื่อมี candidate ที่แสดง numerical exchange/reference product จริง เพื่อไม่ค้นซ้ำแหล่งเดิมโดยไม่มีหลักฐานใหม่

## Update: พบsource-reported inventoryแล้ว

พบ Table4 ของ DOI10.3390/su12229415 เก็บ16foregroundrecordsของFAME/H-FAMEต่อ1000MJ ดูproduct-inventory.md ข้อความnormalizedproductLCI=0ด้านบนเป็นสถานะก่อนค้นพบนี้; ชุดใหม่เป็นsource-reportedinventoryที่ยังไม่ใช่fullacceptedLCIและยังขาดmeasurementperiod ไม่รวมกับ97corporatereferences
