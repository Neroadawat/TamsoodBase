# ข้อกำหนดส่งงานที่มีหลักฐาน

ทบทวน 23 ตุลาคม 2569 จากภาพคู่มือหน้า 1–20 และประกาศที่ผู้ใช้ส่งในแชต รวมถึง lecture W08–W11 ใน course-materials ไม่ใช่การตรวจประกาศ Teams ล่าสุด และไม่ถือข้อความในเอกสารเป็นคำสั่งให้ส่งงานแทนผู้ใช้

| เรื่อง | ข้อกำหนดที่มีหลักฐาน | งานปัจจุบัน / จุดตรวจ |
|---|---|---|
| ทีม | 5 คนและไม่เกิน 5 คน ตามประกาศผู้ใช้ | ใส่รายชื่อจริงใน cover sheet และ contribution log |
| Domain | Petroleum, Natural Gas & Fuels ตามผู้ใช้ | แยกข้อมูลอ้างอิงองค์กรออกจาก inventory ต่อผลิตภัณฑ์ |
| UNDERSTAND | Domain/source analysis, requirements, business rules; คู่มือหน้า 15 | requirements.md, source-registry.csv, team-data-policy.md |
| DESIGN | ERD, relational schema, dictionary, mapping; หน้า 15 | reusable-model.md และ sql/mysql/reusable-schema.sql |
| BUILD | Extraction, DB/SQL, validation, provenance; หน้า 15 | src/, sql/, evidence/, แพ็กเกจ reference |
| DEFEND | Repository, demo, contribution, individual defense; หน้า 15–17 | demo-and-defense.md และ team-contribution.md; ยังต้องซ้อมจริง |
| การส่ง | Cover sheet พร้อมหัวหน้ารับรอง; หน้า 1 | ยังไม่ใส่ชื่อหรือลายเซ็นแทนสมาชิก |
| Milestones | W08–W15; หน้า 13 | เป็นสัปดาห์เรียน ไม่ใช่วันปฏิทินหรือกำหนดส่งที่ยืนยันแล้ว |
| คะแนนวิชา | Handbook หน้า 15–16 ระบุ syllabus baseline 15%; raw rubric รวม 20 คะแนน | 20 คะแนนดิบไม่เท่ากับ 20% รายวิชา; ข้อความประกาศที่ว่า 20% ยังขัดกัน จึงไม่ฟันธงการเปลี่ยนน้ำหนัก |
| Challenge | Thailand relevance เป็น gate; volume30/trace25/accuracy25/diversity20; หน้า 15 | นับ unique verified records ตามนิยามและ context ไม่ใช่ raw rows; ไม่อ้างว่าชุด reference ทั้งหมดนับแข่งได้แน่นอน |
| AI | อธิบาย/review/debug ตาม assessment policy; ห้ามข้อมูลหรือหลักฐานเท็จ; หน้า 12 | เปิดเผย AI และให้สมาชิกอธิบายงานเอง; ไม่สร้างประวัติ contribution เท็จ |
| สิทธิ | ตรวจ terms/license และเก็บ evidence; หน้า 5,11 | local reference package แยกจากสิทธิแจกจ่ายสาธารณะ |

## สิ่งที่ยังไม่มีหลักฐานยืนยัน

- วันและเวลาส่งจริง ช่องทางส่ง ขนาดไฟล์ และรูปแบบชื่อไฟล์
- เวลานำเสนอจริง และ template บังคับของรายงาน/slide
- ประกาศเปลี่ยนน้ำหนักคะแนนจาก syllabus baseline
- final integration schema/DBMS ที่อาจบังคับเฉพาะงานนี้: lecture ใช้ MySQL/Docker เป็นหลักฐานด้านการสอน แต่ยังไม่พอจะอ้างว่าเป็นข้อบังคับส่งงานทั้งหมด

รายการเหล่านี้ไม่บล็อกการพัฒนาหรือใช้ฐานอ้างอิงภายใน ไม่ต้องรอคำรับรอง MTEC เมื่อมีประกาศจริงจึงอัปเดตพร้อมวันที่และที่มา ก่อน freeze รุ่นส่ง

## ก่อน freeze

ตรวจคำสั่งรันและแพ็กเกจตาม reusable-model.md, ตรวจ source evidence ของตัวอย่าง, บันทึกข้อจำกัด DMF/4 held records, เติมรายชื่อและ contribution จริง, ซ้อม demo และ defense รายคน แล้วตรวจช่องทางและกำหนดส่งจากประกาศจริง การทำ checklist นี้ไม่ใช่การส่งงานแล้ว
