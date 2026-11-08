# ผลแก้รีวิว LCI / web database — 5 พฤศจิกายน 2569

| ข้อรีวิว | งานที่แก้แล้ว | สิ่งที่ยังไม่อ้าง |
|---|---|---|
| Versioned product system / scenario / run | ฐาน append-only แยกรุ่นตาม hash พร้อม transaction, source membership FK, seal และ replay ทั้ง 330 ผล | ไม่ใช่ production migration หรือการวัด 330 ครั้ง |
| Provider / allocation / assumptions | candidate links อ้าง exchange และ instance ที่ถูกต้อง; เก็บเหตุ unresolved / applied=false | ไม่คูณ allocation ซ้ำหรือประกาศ compatibility ผ่าน |
| หน้าเว็บยังไม่เห็นโมเดลใหม่ | หน้า B100 เลือก 6 กรณี คลิก 4 process ดูฐาน/ปี/สิทธิ/หลักฐาน พร้อม 6 ประเด็นที่ยังเปิด | ไม่คืนแถบเดโม 5 ขั้นที่ผู้ใช้ไม่รับ |
| อ่านตัวเลขยาก / หลักฐานไม่ชัด | ≈ 27.1 kg พร้อมเปิดค่าเต็ม 27.0600; ลิงก์ต้นฉบับ process และตาราง 2020 ที่รองรับตัวเลขแยกกัน | ไม่แสดง CO2e เป็นศูนย์หรือเผยแพร่ปริมาณโรงสกัดที่สิทธิยังไม่ชัด |
| Backend ผูกกับ Quick Tunnel | เตรียม exact-origin allowlist ฝั่ง server และตรวจ invalid origins | ยังไม่มี HTTPS domain ถาวร ไม่เปลี่ยน production settings |
| เอกสารประวัติปนปัจจุบัน | CURRENT_ARCHITECTURE.md แยก local / production / scientific status และเชื่อมจากเอกสารออกแบบ | ไม่เขียนประวัติเดิมให้ดูเหมือน deploy แล้ว |

## ผลตรวจจริง

- python -m unittest discover -s tests: 208 tests ผ่าน ไม่มี skip (tmp/expert-review-tests.log)
- หลังเพิ่มลิงก์หลักฐานตัวเลข 2020: frontend + release consistency 14 tests ผ่าน (tmp/expert-review-followup.log)
- Node proxy tests ครอบคลุม exact-origin, invalid hosts และ server-only secret; case tests ครอบคลุม precision/false completeness/private data
- Release consistency ผ่าน และ package source 12 files ไม่รวม raw/private research/credentials
- Browser ในเครื่อง: เปลี่ยน dropdown โรงสกัด 1→6, คลิก CPO, เปิดค่าเต็ม 27.0600, ตรวจต้นฉบับที่แสดง; ตรวจภาพ desktop และ viewport 390×844 พร้อมเมนูมือถือ ภาพเก็บ output/review-2026-11-05/
- คำสั่งหน้าเว็บบางแบบ locator ไม่รองรับใน browser นี้ จึงตรวจด้วย native accessibility ที่เห็นค่าหลังเลือกจริง ไม่อ้าง automated browser suite หรือ user study

## ขอบเขตที่ยังต้องทำจากหลักฐาน

T107 ยัง IN_PROGRESS: ต้องปิดความเข้ากันและ allocation ก่อนเติมภาระขนส่ง/use/treatment/background ของไทยอย่างเข้ากัน ไม่มีการรับรองสมดุลมวล/พลังงานอิสระ ไม่มี import/export openLCA ที่ผ่านจริง และยังไม่มี user acceptance โดยมนุษย์

ชุดแก้พร้อมตรวจในเครื่องและแพ็กเกจ Vercel แต่รอบนี้ยังไม่ deploy เว็บไซต์หรือเปลี่ยน EC2/S3 งาน model store เป็น local review โดยตั้งใจ
