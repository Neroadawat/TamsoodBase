# ตรวจและเก็บงานก่อนส่งต่อ — 8 พฤศจิกายน 2569

**ประวัติรอบวันที่ 8:** ผลแก้ retrieval/HTTP ด้านล่างเป็นของรอบที่ระบุ สถานะล่าสุดและวิธีรับช่วงวันที่ 9 อยู่ [ที่นี่](TEAMMATE_NEXT_STEPS_TH.md); Corporate กู้แล้ว และชุด ZIP/patch ล่าสุดเป็นวันที่ 9 ข้อความชุดส่งต่อด้านล่างปรับตามเครื่องมือปัจจุบันแล้ว

## ข้อผิดพลาดที่พบและแก้

ทดสอบคำถามเพิ่ม 26 ข้อที่กำหนดไว้ก่อนแก้ พบ 10 คำถามไม่มีหลักฐานแต่คืนการ์ดผิด ได้แก่ warm start/เครื่องอุ่น, idle/เดินเบา, entire driving cycle, สูตร N₂O ที่เว้นวรรค, ชนิดออกเทนที่ไม่ได้ระบุในหลักฐาน และ H-FAME ที่ถูกจับรวมเป็น FAME จนคืนสัดส่วนจัดสรรผิดเทคโนโลยี

แก้ด้วยการแยก H-FAME ออกจาก FAME (ให้เฉพาะการ์ดหน่วยหน้าที่/ช่วงปี/ฐานต้นน้ำที่ครอบคลุมทั้งสองชนิดรองรับได้), เพิ่มมิติ warm/idle, รูป entire cycle, สูตรสารเว้นวรรคและเลขไทย ส่วนคำถามระบุออกเทนที่ไม่มีหลักฐานตรงบริบทเลือกไม่คืนการ์ด ไม่เปลี่ยนข้อมูลต้นฉบับ ไม่ปรับ cutoff 0.45 และไม่สร้างเวกเตอร์ชุดใหม่

ผลก่อนแก้: positive8/8, negativeปฏิเสธ8/18 ผลหลังแก้: positive8/8, negative18/18 หลักฐาน `evidence/rag-pre-handoff-before-2026-11-08.json` และ `evidence/rag-pre-handoff-after-2026-11-08.json`

ชุดเดิม76ข้อรันซ้ำหลังแก้: positive39/39 และ negative33/33 ผ่าน กำกวม4ข้อยังแยกรายงาน รวมชุดทั้งหมด102ข้อมี98ข้อที่ให้คะแนน ชุดนี้ยังเป็น development/regression ไม่ใช่ user study หรือการยืนยันโดยมนุษย์อิสระ กฎยังครอบคลุมเฉพาะมิติ/คำที่ระบุ ไม่ใช่เครื่องตรวจความเพียงพอทางความหมายทั่วไป

## การใช้งานและข้อผิดพลาดระบบ

- เพิ่ม `/evidence/view?id=...` เป็นหน้าอ่านต้นทางภาษาไทย แสดงปริมาณ หน่วย ฐาน ช่วงปีวัดและตำแหน่งอ้างอิง แสดงหน่วยว่างเป็น “ยังไม่ระบุ” และ HOLD เป็น “พักการใช้” ไม่แทน null ด้วยศูนย์
- ลิงก์ต้นทางและรายการเปิดแยกจากหน้าค้น คงคำถาม/ผลค้นเดิมไว้ ยังมี JSON ต้นฉบับให้ตรวจครบและลิงก์กราฟทดลอง
- HTML escape ข้อความจากข้อมูลและจำกัด source link เป็น HTTPS ที่ไม่มี credentials; ทดสอบข้อความที่มี markup ไม่ให้กลายเป็น script
- แยกสภาพฐานหลักฐานไม่พร้อมเป็น server error แทนการบอกว่าผู้ใช้ส่ง ID ผิด และปฏิเสธคำขอที่มี observation ID มากกว่าหนึ่งค่า
- ใช้กฎแยก H-FAME ใน guard คำตอบ Gemini ด้วย ไม่รับคำตอบที่นำสัดส่วน FAME ไปอ้าง H-FAME

ตรวจ runtime9 tests และ scope6 tests ผ่าน ตรวจ HTTP integration14 checks และ RAG19 checks ผ่าน Browser IAB เปิดรายการ Land seeding ในแท็บแยกได้ เห็นค่าต้นทาง0.48/ฐาน1000kg/หน่วยและช่วงปีวัดยังไม่ระบุ/สถานะพักใช้ ไม่กรอก feedback แทนสมาชิก ไม่มี live Gemini หรือ production changes ในรอบนี้

หลักฐาน HTTP `evidence/handoff-integration-2026-11-08.json`, `evidence/rag-expanded-http-2026-11-08.json` และผล regression ใหม่ `evidence/rag-pre-handoff-{regression,scope,expanded}-2026-11-08.json`

## ชุดส่งต่อ

ใช้ `python -X utf8 scripts/build_teammate_bundle.py --date 2026-11-09` สร้าง ZIP และ Git patch ของไฟล์เพิ่ม/แก้เทียบ HEAD พร้อม SHA256 ทุกไฟล์ ชุดปัจจุบันคือ `build/handoff-package/TamsoodBase-handoff-2026-11-09.zip` และ `.patch` ชื่อเดียวกัน หากแพ็กวันอื่นให้เปลี่ยนวันที่และยึดชื่อจาก `build/handoff-package/MANIFEST.json` ไม่ใช้ ZIP วันที่ 8 แทนรุ่นใหม่

ชุดนี้รวมจุดเริ่มอ่าน `docs/TEAMMATE_NEXT_STEPS_TH.md` ไม่รวม raw/build/.local/credentials ใช้ ZIP หรือ patch อย่างใดอย่างหนึ่งบน base commit ที่ manifest ระบุ ไม่ทับ working tree ของเพื่อนโดยไม่เทียบ diff ตัวแพ็กใช้ Git index ชั่วคราว ไม่ stage ไฟล์ใน index จริงหรือ commit/push ให้

ตรวจชุดส่งต่อบนสำเนาสะอาดของ base commit พร้อม overlay:

```powershell
python -X utf8 scripts/verify_teammate_bundle.py --python build/rag-verified-venv/Scripts/python.exe
```

ผลและข้อข้ามที่ต้องใช้ข้อมูลจริงอยู่ `build/handoff-package/VERIFICATION.json` และ log ข้างกัน ไม่ถือว่าการผ่าน unit tests ในสำเนาที่ไม่มีข้อมูลเป็นผล replay ฐานทั้งหมด

## ข้อค้างที่ส่งให้เจ้าของงานหลัก

รายการค้างปัจจุบันอยู่ [ในคู่มือรับช่วง](TEAMMATE_NEXT_STEPS_TH.md): คำถาม/รีวิวสมาชิกจริง, คีย์ Gemini สำหรับทดสอบ live, EPPO/DOM ต้นฉบับ, NSO104รายการ/4divergences และข้อมูลวิทยาศาสตร์จริงสำหรับปิด LCI ยังเปิด Corporate กู้และตรวจแล้วแต่สิทธิแจกจ่ายยังไม่เคลียร์ งานล่าสุดยังอยู่ working tree จาก `67db1ad` ไม่ได้ commit/push อัตโนมัติ
