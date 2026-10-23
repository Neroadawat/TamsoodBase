# แผนปรับปรุงเพื่อแข่งขัน

เริ่มรอบปรับปรุง 23 ตุลาคม 2569 ตามคำขอให้ทำต่อเนื่อง ไม่มีการรับประกันอันดับ และไม่เปลี่ยนเกณฑ์รับข้อมูลเพื่อเพิ่มยอด

## ลำดับทำงาน

1. ปิดข้อผิดพลาดการใช้งานจริง: export ที่ว่างต้องมี schema ครบ, pagination ไม่ตกหล่น/ซ้ำ, ตัวกรองค้นเป็น literal และปฏิเสธ input ผิด ผลรอบนี้อยู่ tests/test_reusable.py
2. แสดง coverage และคุณภาพจาก release จริง: รัน scripts/reference_scorecard.py ได้ evidence/reference-scorecard.json ตรวจ context, exact scaling, identity และ counts โดยผูก hash กับ release
3. เพิ่มข้อมูลจากแหล่งใหม่อย่างมีเป้าหมาย: เลือก official candidate ที่มีตารางตัวเลข หน่วย เวลา และ boundary จริง เริ่มจากหนึ่งแหล่งที่ต่างจากสองรายงานเดิม ตรวจสิทธิและ sample ก่อนเขียน extractor; บันทึก source ที่ไม่ผ่านพร้อมเหตุผล ไม่วน URL ที่ forbidden
4. ประเมิน process/reference product ตาม product-lci-screening.md ถ้าหลักฐานครบจึงเพิ่ม model/exchanges ถ้าไม่ครบคงประเภท reference โดยไม่ปันส่วนเอง
5. ทำสาธิตให้ผู้ตรวจทำตามได้: ค้นหนึ่งรายการ → source evidence → mapping → validation → SQL → export และทดลองเคส hold; หลักฐานสมาชิกต้องมาจากงานจริง
6. ทำ final freeze เมื่อข้อกำหนดส่งและหลักฐานทีมครบ ตรวจเฉพาะส่วนเปลี่ยนและความเสี่ยงที่เกิดขึ้นใหม่ ไม่ถือ task count ว่าเป็นคะแนนหรือความสมบูรณ์ร้อยละ

## หลักฐานที่เพิ่มรอบนี้

scorecard ระบุ 2 publishers / 2 documents / ปี 2021–2024 รับอ้างอิง97 พัก4 ไม่พบช่องปีขาดภายในช่วงของแต่ละ selected series แต่ไม่ใช่การพิสูจน์ coverage ระดับประเทศ ข้อมูล 97 รายการประกอบด้วย input74, output7, intensity8, context8 จึงไม่ควรกล่าวว่าเป็น 97 flows อิสระ

ตัวตรวจ scaling อ่านตัวเลขมี comma grouping ตามต้นฉบับอย่างชัดเจน ทดสอบโดยเปลี่ยนค่า/บริบท/release/trace marker และเพิ่ม duplicate แล้วต้องตรวจพบ ไม่อ้างว่าการตรวจสมการนี้เป็น independent source verification

## เกณฑ์จบของแต่ละรอบ

มี artifact ที่ใช้ได้จริงพร้อมหลักฐานตรวจ หรือมีผลคัดแหล่งที่ชัดเจนและไม่ค้นซ้ำโดยไร้เหตุผล แจ้งเฉพาะผลที่สำคัญ ไม่สร้าง contribution ของสมาชิก ไม่ push หรือเผยแพร่ และไม่ส่งข้อความแทนผู้ใช้
