# แผนทำงาน 3 สัปดาห์

สถานะงานล่าสุดให้ยึด [Task board](tasks.md) ซึ่งมีเกณฑ์จบและ dependencies รายการด้านล่างเป็นแผนตั้งต้นและบันทึกตามเวลา ไม่ใช่หลักฐานว่าประเด็นเก่าทุกข้อยังค้างอยู่

เริ่ม 22 ตุลาคม 2569; วันส่งจริงยังไม่ยืนยัน จึงใช้วันสัมพัทธ์เป็นหลัก

## สัปดาห์ 1 — พิสูจน์ข้อมูลและระบบ

1. อ่านประกาศล่าสุด, syllabus, lecture และวิดีโอ Launch; ทำตารางข้อกำหนดพร้อมแหล่งอ้างอิง
2. ยืนยันว่าข้อมูลการผลิตระดับแหล่ง/ระดับประเทศนับ LCI ได้แบบใด พร้อมส่งตัวอย่างให้ผู้สอนพิจารณาโดยสมาชิกทีม
3. ตรวจสิทธิใช้งาน DMF/EPPO และวิธีได้ต้นฉบับที่เข้าถึงได้ตามปกติ
4. ทดลองหนึ่งเดือนให้ครบ extraction → staging → mapping → validation → DB → traceability
5. ออกแบบ ERD/schema/data dictionary จากข้อมูลที่ผ่าน review; เลือก DBMS ตามข้อกำหนดคลาส

ผ่านสัปดาห์แรกเมื่อมีข้อมูลต้นฉบับจริง ชี้ตำแหน่งตัวเลขได้ และคนอีกคนรันตาม README ได้

## สัปดาห์ 2 — ขยายและตรวจ

ขยายช่วงเวลาของแหล่งที่ผ่านเกณฑ์ก่อนเพิ่มแหล่งใหม่ ตรวจข้อมูลซ้ำ ขอบเขต หน่วย และ revision
เก็บ raw snapshot + SHA256 + extraction metadata; จัดทำ reject log และ independent numerical checks
พัฒนา SQL use cases: ค้นตามเชื้อเพลิง/เดือน/พื้นที่, ตรวจ coverage, ตาม provenance, สรุปเหตุ reject
เปรียบเทียบต่างแหล่งเฉพาะนิยาม/เวลา/พื้นที่/หน่วยตรงกัน ไม่บังคับให้ค่าตรงกัน

## สัปดาห์ 3 — ตรวจส่งและ defense

หยุดเพิ่มแหล่งหลักต้นสัปดาห์ ตรวจ constraints และการรันซ้ำจากเครื่องอื่น
จัดทำหลักฐาน normalization และ performance เฉพาะ query ที่ใช้จริง
เดโมเลือก record → เปิด evidence → อธิบาย mapping → SQL → ข้อจำกัด
ทุกคนซ้อมอธิบาย schema, duplicate rule, หน่วย, งานตัวเอง และ AI usage

## การแบ่งงานเสนอสำหรับ 5 คน

| บทบาท | ผลงานที่ตรวจได้ |
|---|---|
| Domain/source lead | source registry, ข้อกำหนด, นิยามข้อมูล |
| Acquisition engineer | ตัวดึงข้อมูล, snapshots, run logs |
| Database engineer | schema, SQL, mapping implementation |
| Quality reviewer | ตรวจตัวเลขอิสระ, reject review, test evidence |
| Integration/defense lead | reproducibility, docs, demo, contribution log |

ยังไม่กำหนดชื่อสมาชิกหรืออ้างว่ามีใครทำงานแล้ว แต่ละคนต้องมี reviewer และเข้าใจเส้นทางข้อมูลทั้งระบบ

## คำถามค้างและการตัดสินใจ

- LCI eligibility: production statistics เป็น accepted ได้หรือเป็นข้อมูลประกอบเท่านั้น?
- กฎ duplicate: เทียบเท่าต่างหน่วย รายเดือน/รายปี และข้อมูลที่เผยแพร่ซ้ำต่างหน่วยงานนับอย่างไร?
- คะแนน: คู่มือระบุ 15% และ rubric 20 คะแนน ข้อความประกาศกล่าวถึง 20%; ตรวจประกาศล่าสุด
- อาจารย์กำหนด DBMS, schema กลาง, format ส่ง หรือ AI policy เพิ่มเติมหรือไม่?
- วันส่งและวัน defense จริงคือวันใด?

## งานถัดไป

P0: เข้าถึง lecture/ประกาศ CN230 ใน Teams และต้นฉบับ DMF ที่ดาวน์โหลดได้ตามปกติ
P0: ยืนยันกติกา LCI ด้วยตัวอย่าง 3 รายการก่อนเก็บจำนวนมาก
P1: เพิ่มตัวดึงข้อมูลอัตโนมัติเมื่อมีช่องทางที่ใช้ได้ แล้วทำ numerical verification กับต้นฉบับ
P1: เปลี่ยน schema ทดลองเป็น canonical model ตาม requirement ที่ตรวจแล้ว

อัปเดต 22 ตุลาคม: ได้ lecture W08-W11 และอ่านประเด็นเกี่ยวกับโครงงานแล้ว เพิ่ม MySQL pilot/export/query และ integration checks ดู course-alignment.md
งานถัดไปให้เน้นต้นฉบับข้อมูลจริง/rights review และคุณภาพ dataset สำหรับ Final Project เท่านั้น ตามที่ผู้ใช้ยืนยัน ไม่ดำเนินงานการบ้านย่อย

อัปเดต: ได้ต้นฉบับ DMF CSV สามผลิตภัณฑ์และ offline pipeline แล้ว ดู dmf-data-review.md
ลำดับถัดไปคือ duplicate conflicts, หน่วย/ฐานเวลา, สิทธิใช้ และการยืนยัน LCI eligibility ก่อนเพิ่มแหล่งอื่น

## บันทึกการเริ่มงาน

22 ตุลาคม 2569: AI-assisted pilot; เว็บไซต์ DMF อ่านได้ผ่าน web text แต่ urllib ตอบ 403
Google Docs ตอบ not found ผ่าน connector; วิดีโอ connector transport error; web fallback เปิดไม่ได้
ยังไม่มีหลักฐานการดูวิดีโอหรือ Teams และยังไม่มี raw snapshot จึงไม่มี accepted tuples
