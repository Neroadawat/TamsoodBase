# Final Project: ตรวจซ้ำจากเว็บไซต์ทางการ 27 ตุลาคม 2569

อ่านหน้าโครงการ 12 หน้าและ JavaScript 2 ไฟล์ที่หน้าเว็บเรียกใช้ เทียบกับระบบจริง โดยยังไม่จัดทำงานส่งแต่ละ M ตามคำสั่งผู้ใช้ รายงานเดิม: [technical gap matrix](final-project-system-review.md)

## ขอบเขตและข้อค้นพบเพิ่มเติม

- หน้าหลัก, timeline, mission, final-process, prepare และ knowledge ทั้งบทนำ/LCI/SRS/Memo/ERD/Neo4j/transaction-index รวม 12 หน้า ตรวจลิงก์ภายในกลุ่มหน้าโครงการแล้ว
- อ่าน assets/rubric-live.js และ assets/site.js เพิ่ม: คะแนนเริ่มต้น 100 ใน widget เป็นตัวอย่างที่ปรับได้ ไม่ใช่คะแนนประเมินทีมจริง การติ๊ก checklist ใน browser ไม่ใช่หลักฐานการยินยอมหรือส่งงาน
- ERD ตัวอย่างเป็นแนวทาง ต้องอธิบาย identity, cardinality, constraints และ provenance จากความหมายข้อมูลจริง ไม่จำเป็นต้องคัดชื่อตารางทุกตัว
- ตัวอย่าง SUM ไม่พิสูจน์ functional unit หรือ normalization ต้องมีฐานอ้างอิงและขอบเขตที่รองรับก่อนอ้างค่าต่อหน่วย
- ตัวอย่างแปลงหน่วยที่ปัดเศษไม่ควรถูกนำมาเป็นค่าคงที่ความแม่นยำสูงโดยไม่มีที่มา
- Graph ต้องรักษา Exchange identity: การ MERGE ด้วย amount/unit อย่างเดียวเสี่ยงรวมแถวต่างแหล่ง/บริบท ระบบปัจจุบันยังเป็น local projection ไม่ใช่ Neo4j engine
- ตาราง ACID/isolation ในเอกสารเป็นแนวคิด ไม่ใช่ผลทดลองของระบบเรา
- วันที่บางส่วนยัง Draft และช่องทางส่ง Teams/Google Form ขัดกัน บันทึกเป็นข้อค้าง ไม่เลือกแทนผู้สอน

ไม่ได้อ่านไฟล์ตัวอย่าง Drive/Memo DOCX หรือจัดทำเอกสารส่งแต่ละ M ในรอบนี้ ลิงก์ภายนอกและหน้าเนื้อหารายวิชาอื่นไม่ถูกอ้างว่าได้ตรวจครบทั้งหมด เก็บ HTML ต้นฉบับเฉพาะ build ที่ไม่แจกจ่าย ไม่บันทึกรหัสผ่าน

## สิ่งที่แก้ในระบบจริง

หน้า inventory เลือก FAME/H-FAME และ input/output ได้ แสดงฐานอ้างอิง เทคโนโลยี พื้นที่ ปีเผยแพร่แยกจากช่วงปีข้อมูล พร้อมขอบเขตและ allocation ก่อนอ่านตาราง ใช้ค่าจากข้อมูลแทน hardcode ฐาน/ปี เพิ่มบทบาท reference product และ co-product โดยไม่คำนวณ allocation เพิ่ม ไม่รวมค่าข้ามกระบวนการหรือหน่วย

ตรวจ browser: FAME 10 แถว, H-FAME 6 แถว; output FAME 2 และ H-FAME 1 แถว Crude glycerine แสดง co-product และย้อนถึง Table 4/source row 24 ได้ แสดงปีข้อมูลที่ต้นฉบับไม่ระบุอย่างตรงไปตรงมา มือถือ 390×844 ไม่มี document overflow

เพิ่ม deterministic test สำหรับ filter/context/decimal string/ไม่แก้ข้อมูลต้นทาง Full suite 102 tests ผ่านไม่มี skip ภาพตรวจอยู่ build/inventory-process-desktop.jpg และ build/inventory-process-mobile.jpg ผล image build แยกบันทึกใน evidence/backend-image-audit.json

## งานสำคัญที่ยังเหลือ

1. Petroleum product LCI: ยังขาด dataset ที่มี functional unit, boundary และ allocation รองรับจริง ห้ามใช้ยอดบริษัทหรือสถิติประเทศแทนค่าต่อผลิตภัณฑ์
2. Global source-ID crosswalk และหน่วยมาตรฐานข้ามชุดข้อมูลยังควรพัฒนาจากนิยามที่ตรวจสอบได้
3. หากต้องสาธิต Neo4j ต้องทดสอบ engine/Cypher จริง ปัจจุบัน projection ไม่ใช่หลักฐานว่าใช้ engine แล้ว
4. Public deployment ยังต้อง HTTPS/access control/CORS และโดเมน รุ่น EC2 ไม่ถือว่าเปลี่ยนตามการแก้ local นี้
5. สิทธิแจกจ่ายข้อมูลบริษัท หลักฐานสมาชิก/consent และข้อขัดแย้งกำหนดส่งยังเป็นข้อค้างจริง

อ้างอิง: [เว็บไซต์โครงการ](https://akkhara.engr.tu.ac.th/cn230/project/), [ERD](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-erd.html), [Neo4j](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-neo4j.html), [Transaction/index](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-txn-index.html)
