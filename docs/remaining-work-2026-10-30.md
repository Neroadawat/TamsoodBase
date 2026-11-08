# แผนปิดงานหลักและงานรอง — 30 ตุลาคม 2569

ยึด PROJECT_STATE.md และหลักฐานรายงานล่าสุดเหนือข้อความประวัติในแผนเก่า ผู้ใช้อนุญาตดำเนินงานต่อและตรวจทั้งหมด แต่การอนุญาตไม่ทำให้ข้อมูลที่ขาดกลายเป็นข้อมูลที่ยืนยันแล้ว

## งานหลักที่ยังไม่ปิด

| งาน | หลักฐานที่มี | เกณฑ์ปิดและสิ่งที่ยังขาด |
|---|---|---|
| Allocation application | CPO92/6/2 และ FAME70/30 ตรงบทความ | ต้องยืนยัน Tables1–4 ก่อน/หลัง allocation จากคำอธิบายหรือ calculation sheets; ห้ามคูณซ้ำเพื่อให้ต่อโมเดลได้ |
| FFB→CPO | Table2 มี CPO output | ไม่มี FFB input amount; ต้องมีแหล่งตรงบริบท ไม่คำนวณจาก coproduct totals |
| Provider/background | 3 potential provider pairs | ต้องตรวจ technology/time/basis/allocation; electricity/chemicals/transport/use และ elementary emissions ยังไม่ครบ |
| Cross-publication | NSO169/273 มีผลเทียบ | 104 มีเหตุค้างและ 4 divergences ต้องเก็บสองแหล่ง; ปิดด้วยหลักฐานใหม่ ไม่เปลี่ยนตัวเลขให้ตรงกัน |
| Final release | เว็บใช้งานได้; SRS0.5/PDF21หน้าเป็นร่าง | ต้องผูกเอกสาร/diagram/dictionary/export กับรุ่นที่ส่งจริงและให้สมาชิกตรวจ |

## งานรองที่ช่วยปิดงานหลัก

| งาน | ผล/ลำดับต่อ |
|---|---|
| รวมทะเบียนตรวจ 5 processes | T86:58 source payloads เก็บทุก field เดิม; 51 exact label/unit keys; ไม่ใช่ global flow equivalence |
| Model-ready gate | ทั้ง5ยัง false; แยก source verification ออกจาก allocation/provider/measurement completeness |
| Review export | เว็บมี filtered upstream JSON พร้อม attribution และ HOLD; ยังไม่ใช่ ILCD/openLCA exchange format |
| Interoperable export | ทำหลัง model contract พร้อมและต้องนำเข้าเครื่องมือจริงตรวจ roundtrip ก่อนอ้าง compatible |
| Database migration | candidate กับ production แยก; ไม่เปลี่ยน EC2 เพียงเพื่อให้ชื่อ schema ตรงแผน ต้อง backup/stage/parity/rollback |
| Deployment | Vercelมีลิงก์เดิม; QuickTunnelยังชั่วคราว โดเมนพักตามผู้ใช้ ไม่ซื้อหรือแตะ Ginder/Caddy |
| UX | คงแยกต้นน้ำ/แปรรูปและปุ่มดูต้นฉบับ; ไม่คืน demo overlay ที่ผู้ใช้ไม่รับ; เปลี่ยนเฉพาะปัญหาที่ตรวจพบ |
| เอกสาร | ใช้ addendum ด้านล่างประกอบ SRS0.5 ก่อน merge; ไม่เขียนทับ Introduction ที่สมาชิกแก้ |

## ข้อความประกอบ SRS / ขอบเขตข้อมูลล่าสุด

ระบบมีข้อมูลต้นน้ำ Tables1–3 จำนวน42 observations และขั้นแปรรูป Table4 จำนวน16 observations จาก DOI10.3390/su12229415 ข้อมูลเหล่านี้อ้างถึง5กระบวนการ ไม่ใช่58 complete LCI datasets การศึกษาระบุ Functional Unit เป็นการใช้เชื้อเพลิง1000MJ แต่ตารางต้นน้ำอ้างอิง1000kgผลิตภัณฑ์ของแต่ละกระบวนการ จึงไม่มีสิทธิรวมปริมาณหรือเปลี่ยนฐานโดยตรง

ทะเบียนรวมเก็บ source payload เดิมทุก field พร้อม identity, decimal string, null, unit, direction, role, reference basis และ locator การจับคู่ label/unit ตรงกันเป็น source-local lookup เท่านั้น ไม่ยืนยันว่ากระบวนการเป็น provider ที่เข้ากันได้หรือว่า flow นั้นเป็น elementary emission ปัจจุบันไม่มี allocation หรือ provider scaling ที่โครงงานนำมาใช้ ไม่มี whole-lifecycle total และยังไม่มี interoperable LCA-tool export ที่ทดสอบแล้ว

Land seeding ที่ไม่มีหน่วยคง HOLD_MISSING_UNIT; ช่วงเวลาการวัดที่ไม่รายงานคง null ไม่ใช้ปีตีพิมพ์แทนปีวัด ตัวเลขต้นฉบับที่ดูผิดปกติ เช่น Water0.11kg คงตามต้นฉบับและต้องทบทวน ไม่แก้เป็นหน่วยที่คาดว่าเหมาะกว่าเอง

## งานที่ต้องเกิดจากสมาชิกจริง

รายชื่อ/บทบาท, contribution, memo, consent, peer review/วิดีโอ, การซ้อม defense, การรับรองเอกสาร, ช่องทาง/เวลาส่งและ receipt ผู้ช่วยเตรียมโครงและตรวจไฟล์ได้ แต่ไม่สร้างเหตุการณ์หรือคำรับรองแทนสมาชิก งานเหล่านี้ไม่ถูกทำเครื่องหมายเสร็จเพียงเพราะผู้ใช้อนุญาตให้ทำต่อ

## วิธีตรวจทะเบียนรวม

`python -m scripts.build_combined_inventory_review`

ผลอยู่ build/combined-inventory-review/review.json และ evidence/combined-inventory-review.json ตรวจทุก58payloadหลัง JSON serialization ไม่ใช่สุ่มตรวจ ค่าเดิมไม่เปลี่ยน ไม่รวมข้อมูลนี้เข้า production MySQL หรือเพิ่มยอด accepted
