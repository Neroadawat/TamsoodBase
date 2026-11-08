# การขยาย FAME ทั้งวงจร — 3 พฤศจิกายน 2569

ผู้ใช้อนุญาตเพิ่มข้อมูลที่ขาดและพัฒนาให้ครบวงจร เริ่ม T97 แล้ว แต่ยังไม่ผ่านเกณฑ์ครบวงจร

## ชิ้นงานที่ทำจริง

`python -m scripts.build_lifecycle_candidate` สร้าง `build/lifecycle-candidate/fame.json` จาก full source payload ที่เก็บแล้ว แยก FAME route 52 observations ออกจาก H-FAME 6 observations โดยไม่เปลี่ยนค่า/หน่วย/locator ใด ใช้ห้าช่วงชีวิตและ FU การใช้ 1000 MJ; ฐานตารางต้นน้ำยังแยกตามต้นฉบับ ไม่แอบ scale

เพิ่ม `src/lifecycle_model.py` ป้องกัน observation เดียวถูกนับหลายช่วง, missing ถูกเปลี่ยนเป็น zero โดยไร้หลักฐาน, exclusion ไร้ scope evidence, assumption ถูกอ้างเป็น measurement และการเปิด full-lifecycle claim ขณะ allocation/scaling/provider/background/mapping/double-count gates ยังไม่ผ่าน

4 tests ใหม่ผ่าน รวมตรวจ payload เท่ากันทั้ง52รายการ ไม่ใช่การทดสอบ production หรือการยืนยัน completeness ไม่มี deployment/migration ในรอบนี้

## การค้นที่ทำเพิ่ม

- ตรวจ Section2.1–2.2 ของ DOI10.3390/su12229415 หน้า3–4 พบว่าข้อมูลเบื้องหลังมาจาก national reports และ ecoinvent3 cut-off ผ่าน SimaPro บทความไม่ได้แจกแจงข้อมูลเบื้องหลังทั้งหมด ห้ามคัดลอกฐานที่มีสิทธิจำกัดหรือสร้างค่าขึ้นแทน
- พบบทความ Energy and Greenhouse Gas Evaluation of Biodiesel and Bio-hydrogenated Diesel from Palm Oil in a Life Cycle Perspective (2012) ในผลค้น มี transport table แต่เปิด PDF CiteSeer ไม่สำเร็จ จึงยังไม่รับระยะทางจาก snippet เป็น source-verified
- อ่าน HTML ต้นฉบับ DOI10.3389/fenrg.2021.690725 สำเร็จผ่าน HTTP หลัง web reader ล้มเหลว เก็บ private hash/manifest พบว่าเป็น Mexico HEFA renewable diesel, FU13.13kg, mass allocation และสมมติฐาน combustion ไม่ตรง Thai FAME จึงไม่ผสมเป็นข้อมูลจริงของเส้นทางนี้ ตัวอย่างนี้ใช้เป็นแนวทางโครงสร้าง scenario ได้ แต่ยังไม่ import ตัวเลข
- TCI ThaiJO candidate PDF เปิดไม่สำเร็จ ยังไม่รับข้อมูล ไม่มีการวน URL เดิม

## ข้อค้างที่ต้องใช้หลักฐาน

1. FFB input ต่อ CPO และฐาน allocation ที่ชัดเจนของ Tables1–4
2. ระยะทาง/โหลด/เที่ยวเปล่า/ชนิดรถ และ provider สำหรับขนส่งแต่ละขาและ distribution
3. Use-phase elementary emissions ของเชื้อเพลิง/เครื่องยนต์ตรงบริบท แยก biogenic/fossil ไม่ใช้ CO2e impact score เป็น flow
4. Treatment ของ waste streams และ inclusion/exclusion ที่ระบุชัด ไม่สร้างขยะเชื้อเพลิงหลังเผาไหม้ซ้ำ
5. Background electricity/chemicals ที่มีสิทธิใช้และเข้ากัน; หากใช้ surrogate ต้องแยกเป็น scenario พร้อม justification/sensitivity ไม่อ้างเป็นค่าที่วัดจากต้นฉบับ

สถานะที่สร้างได้จริง: raw material PARTIAL, manufacturing PARTIAL, distribution/use/end-of-life MISSING ไม่ใช้เพียงจำนวนช่วงห้าช่วงเป็นหลักฐานว่าโมเดลเสร็จ
