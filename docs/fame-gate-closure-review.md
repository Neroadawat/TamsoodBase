# ปิดข้อค้างก่อนรวม CO₂e — ผลตรวจ 5 พฤศจิกายน 2569

ผู้ใช้ให้ดำเนินเรื่อง allocation/compatibility/ขนส่ง/use/ของเสียต่อจากงาน UX รอบนี้ตรวจข้อความต้นฉบับที่รองรับการตัดสิน 7 ตำแหน่งด้วย pypdf และ pdfplumber เก็บ source hash/หน้า/ข้อความที่ตรวจเป็น hash ใน evidence/fame-gate-closure-review.json ไม่ใช้เพียงชื่อบทความหรือ snippet และไม่อ้างว่าได้ visual review ใหม่

## สิ่งที่ยืนยันเพิ่ม

1. งาน2020 PDF4 ระบุวิธี economic allocation และ PDF7 ระบุ FAME70%/glycerine30% จริง แต่ยังไม่มีหลักฐานว่าทุกค่าของ Table4 เป็น gross หรือแบ่งภาระมาแล้ว การตัดสินจึงเป็น BLOCKED_TABLE_BASIS_UNKNOWN ไม่ใช่ไม่มีวิธี allocation และไม่คูณ0.70ซ้ำ
2. ปี2019/2020ในชื่อแหล่งเป็นปีเผยแพร่ ไม่ใช่หลักฐานว่ามีช่วงเก็บข้อมูลหรือโรงงานใน supply chain เดียวกัน อนุญาตเฉพาะ explicit activity scenario ต่อไป ยังไม่ยอมรับ burden linking
3. FAME26.27kg ในข้อความ PDF2 เทียบกับ26.3kg ใน Table4/PDF7 ต่าง0.03kg สอดคล้องกับการปัดแสดงหนึ่งทศนิยม ไม่แก้ค่าต้นฉบับ และข้อมูลนี้ไม่ได้ให้ลิตรต่อ1000MJ จึงยังไม่ปิด density/LHV bridge ของuse2013
4. งาน2020 PDF4 ระบุใช้ ecoinvent เป็น background จึงไม่ใช้ผลรวมงานนั้นรับรองว่าการสร้างซ้ำของเราเป็น Thai-only background

## ตารางการตัดสินและสิ่งที่ปิดประเด็นได้จริง

| เรื่อง | สถานะ | หลักฐานที่จำเป็น |
|---|---|---|
| Allocation | ยังไม่ใช้ factor | workbook หรือคำอธิบายฐานแต่ละตารางก่อน/หลัง allocation รวม co-products และ upstream treatment |
| Compatibility ต่างแหล่ง | ไม่ยอมรับ burden link ในรุ่นนี้ | product specification, technology, measurement period, geography, allocation และ representativeness ราย link; ไม่ต้องเป็นปีเดียวกันเสมอ แต่ต้องมีเหตุผลรองรับ |
| ขนส่ง | ขาด provider และขาอื่น | ระยะ/น้ำหนัก/รถ/โหลด/เที่ยวกลับครบตามขอบเขต และพิสูจน์ว่าไม่ซ้ำดีเซลในกิจกรรมสวน/โรงงาน |
| ใช้งาน | ขาดฐานลิตร↔พลังงานที่เข้ากัน | fuel properties ของ B100 ที่เลือก และ engine inventory พร้อม CH4/N2O/biogenic–fossil/ปีการวัด |
| ของเสีย | ขอบเขตการบำบัดยังไม่ปิด | raw/treated stream, สิ่งที่รวมในโรงงานแล้ว, discharge/leakage/flare จริง และขอบเขตเครดิตพลังงาน |
| Background ไทย | ยังขาด process exchanges | ไฟฟ้า สารเคมี และเชื้อเพลิง provider ที่เข้ากันพร้อมสิทธิใช้ ไม่ใช้ aggregate EF แทนทุก exchange |

## แหล่งใหม่ที่ได้และคัดแล้ว

[COMPETE Thailand report](https://www.compete-bioafrica.net/publications/publ/2nd_Report/Annex4-2-5-COMPETE-032448-2ndReport-D4.1-Thailand-Final.pdf) ดาวน์โหลดTLSปกติได้61หน้า SHA256 eb487f2fb400f1112e5ea54fcdff35b9ea180148d9a03509c91c8169a9a831c2 เก็บต้นฉบับภายใน NOT_CLEARED

Section3.1 PDF11–13 ครอบคลุมสามขั้นผลิตและระบุว่าจะพิจารณาการเผาไหม้ภายหลัง มีช่วงค่าตารางต่อ1ตันไบโอดีเซล แต่ไม่ให้ใช้ชื่อlife cycleหรือช่วงค่ารวมเพื่อปิดuse/transportของโมเดล2020 จึงยังไม่นำเข้าแถวตัวเลขหรือรวมกับ52observationsเดิม การค้นฉบับARDA2017และงานวัดPleanjai2008รอบนี้ยังไม่ให้ workbook/engine inventory ที่ตรง หยุดการใช้snippetเป็นข้อมูล เว็บMDPIตอบ429แต่มีPDFต้นฉบับพร้อมhashอยู่แล้วจึงใช้หลักฐานท้องถิ่น

## ผลตรวจและผลกระทบ

python -m scripts.review_fame_gate_closure สร้างทะเบียน6decisions/7sourcepassages; testsใหม่3ข้อและactivity chainเดิม4ข้อผ่านรวม7 ไม่มีการคำนวณburdenใหม่/เปลี่ยนsource values/เปิดraw/deploy/API/EC2/MySQL/S3

ยัง CO2e_total=null และ full_lifecycle_inventory=false งานT107ยังIN_PROGRESS สิ่งที่เสร็จคือทะเบียนการตัดสินจากหลักฐานและเงื่อนไขปิดแต่ละเรื่อง ไม่ใช่การประกาศว่าช่องว่างทางวิทยาศาสตร์หายแล้ว ขั้นต่อไปที่คุ้มค่าคือหา table-specific allocation workbook กับ engine/fuel-property inventory ที่ตรงก่อน ไม่ขยายจำนวนscenariosแทนการปิดหลักฐาน
