# กฎตรวจรับและสิ่งที่ยังไม่ยืนยัน

ฉบับร่างของทีม 22 ตุลาคม 2569 ไม่ใช่คำอนุมัติจาก MTEC กฎนี้แยกความพร้อมทางเทคนิคออกจาก eligibility ของการแข่งขัน

ปรับตามคำตัดสินของผู้ใช้: การใช้ข้อมูลอ้างอิงไม่รอคำยืนยันจาก MTEC ให้ใช้ [นโยบายทีม v1](team-data-policy.md) และผล ACCEPTED_REFERENCE/HOLD_CONTEXT ในฐานข้อมูลใหม่ ส่วนกฎด้านล่างเป็นรายการตรวจและความเหมาะสมตาม use case ไม่ใช่การบังคับให้ขอคำอนุมัติภายนอก

| Rule | ตรวจอะไร | เมื่อไม่ผ่าน |
|---|---|---|
| A01 | ระบุ subject, metric/flow และความหมายได้ | พัก domain review |
| A02 | ค่า หน่วย ตัวคูณ และฐานอ้างอิงชัดเจน | พัก unit/basis review ไม่เดาตัวหาร |
| A03 | ปี/ช่วงข้อมูลแยกจากปีเอกสารและวันที่ดึง | พัก temporal review |
| A04 | มีขอบเขตพื้นที่ องค์กร หรือ process พร้อมหลักฐาน Thailand relevance | พัก scope review |
| A05 | ชี้กลับ URL/ไฟล์ hash หน้า/แถว และ version ของ extraction/mapping ได้ | ไม่เข้า trusted view |
| A06 | ตรวจค่าและคอลัมน์จากหลักฐานต้นทาง พร้อมบันทึกวิธีและขอบเขตการตรวจ | พัก numerical review |
| A07 | ผ่าน schema/FK/domain constraints และไม่มี missing ที่กฎกำหนด | rejected พร้อมเหตุผล หรือแก้ staging ด้วยหลักฐาน |
| A08 | ไม่ซ้ำตาม identity/context ที่อนุมัติ; ambiguity เก็บทุกฝ่าย | exclude exact copy หรือ hold context |
| A09 | มีหลักฐานสิทธิใช้ตามวิธีนำไปใช้จริง | พัก rights review ไม่เผยแพร่ raw |
| A10 | ชนิดข้อมูลตรง use case และนโยบายทีม พร้อมเปิดเผยขอบเขต | จัดประเภทเป็น reference/context/intensity หรือพักเฉพาะรายการที่ใช้ไม่ได้ |

ผ่าน A01–A09 ไม่ได้แปลว่าเหมาะกับทุก use case ผล tests ตรวจการทำงานของระบบ ไม่ใช่ใบรับรองความถูกต้องของข้อมูลจากภายนอก

ทุกการเปลี่ยนสถานะต้องมี record identity, rule version, ผล, evidence reference, ผู้ตรวจ/วิธีตรวจ, เวลา และเหตุผล การตรวจอัตโนมัติต้องใช้ actor เป็นชื่อเครื่องมือหรือ AI-assisted ไม่ปลอมเป็นชื่อสมาชิกทีม

สถานะการทำงานที่ใช้ได้ตอนนี้: EXTRACTED → STRUCTURAL_PASS / REJECTED → PENDING_REVIEW / HOLD / EXACT_COPY_EXCLUDED ส่วน ACCEPTED เปิดได้หลังมีกฎยืนยันและหลักฐานผ่านครบเท่านั้น

## ห้ามนับซ้ำโดยโครงสร้าง

- snapshots ใหม่ของ observation เดิมไม่ใช่ข้อมูลใหม่โดยอัตโนมัติ
- total กับ components เป็นชุดที่ overlap; ไม่บวกรวมทั้งหมดหรือถือเป็น independent inventory flows
- reported intensity กับ annual amount แยกประเภทและฐานอ้างอิง
- หน่วยที่แปลงได้และตัวคูณต่างกันไม่ทำให้เกิด tuple เพิ่ม
- การไม่พบความขัดแย้งไม่ใช่หลักฐานว่า semantics เท่ากัน

## เกณฑ์พร้อมส่งจริง

ต้องมีการยืนยันกติกาและ eligibility, source rights ที่รองรับวิธีส่ง, canonical design ที่อธิบาย FD/keys/constraints ได้, การทดสอบรันซ้ำ, numerical/domain review ตามกฎ, contribution จริงของสมาชิก และ demo/individual defense ฐานข้อมูลที่เปิดได้อย่างเดียวยังไม่ผ่าน final gate
