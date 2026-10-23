# TamsoodBase Data Explorer

เว็บในเครื่องสำหรับสำรวจข้อมูลจริงและสาธิต provenance เชื่อมฐานข้อมูล candidate ที่ pipeline สร้างแล้ว
นำแนวคิด data catalog และ metadata จาก Thai National LCI / GLAD มาปรับใช้ ไม่มีการอ้างว่าเป็นระบบของหน่วยงานเหล่านั้น

## เปิดใช้งาน

```powershell
python -X utf8 scripts/run_pipeline.py
python -X utf8 src/explorer.py
```

เปิด http://127.0.0.1:8765 ใช้เฉพาะเครื่องนี้ และหยุดด้วย Ctrl+C ใน terminal ที่รัน
ถ้า port ถูกใช้งาน เปลี่ยนเป็น `python -X utf8 src/explorer.py --port 8766`
VS Code: Terminal → Run Task → Tamsood: Open local data explorer
ไม่ต้องติดตั้ง dependency เพิ่ม และไม่ต้องใช้บัญชีผู้ใช้

## สิ่งที่ทำได้

- พร้อมใช้ต่อ: ชุดที่ทีมรับเป็นข้อมูลอ้างอิงตาม team-data-policy.md กรองประเภท/แหล่ง/ปี/ผลรับข้อมูล ส่งออก CSV/JSON พร้อมขอบเขตและ usage profile; ไม่รอการอนุมัติ MTEC

- ข้อมูลจากรายงาน: ตัวอย่างไทยออยล์ 48 observations ปี 2021–2024 พร้อมปี ขอบเขต หน้า PDF hash และ mapping ไม่ปนจำนวนกับ DMF และไม่นับเป็น Accepted

- สำรวจ: ค้นชื่อแหล่ง/แปลง กรองผลิตภัณฑ์ ปี พื้นที่ และผลตรวจข้อมูลซ้ำ; แสดงครั้งละ 30 แถว
- หลักฐาน: เปิด raw fields, CSV source line, URL, snapshot hash, วันที่ได้ข้อมูล และสมาชิกทุกแถวใน identity group
- คุณภาพ: แยก raw, pending, hold, reject, spot-check และ coverage ตามจำนวนรายการ
- แหล่งข้อมูล: เปิด CSV ทางการและเห็น checksum ของทั้งสามผลิตภัณฑ์จาก DMF
- ส่งออก: CSV เฉพาะผลตามตัวกรอง พร้อม provenance, unit multiplier, unit_time_basis=UNCONFIRMED และ PENDING
- คัดลอก metadata: browser clipboard หลังผู้ใช้กดปุ่ม เพื่อใช้อ้างอิงรายการที่เปิด

ตารางใช้ค่าต้นฉบับโดยไม่มีการปัดเลข/คูณหน่วยเพิ่ม
หน่วยก๊าซแสดงตัวคูณล้านจาก metadata ชัดเจน ส่วน /day ยังไม่เติมให้ CSV ทั้งชุด
ชื่อคอนเดนเสทใน UI map จาก production-condensate ของ DMF ไม่ตีความเป็น LNG
กราฟ coverage แสดงจำนวน candidates ตามปี ไม่ใช่ปริมาณผลิต/ผลกระทบสิ่งแวดล้อม

## API ในเครื่อง

| GET endpoint | ผลลัพธ์ |
|---|---|
| /api/summary | ตัวเลขคุณภาพและทะเบียนแหล่งข้อมูล |
| /api/records | records + total + pagination; q/product/year/area/status/page |
| /api/record?package=...&line=... | provenance และสมาชิกกลุ่มเดียวกัน |
| /api/export | CSV ตาม filters เดียวกับ records |

status=eligible ใน API หมายถึงผ่าน duplicate selection เท่านั้น ไม่ใช่การแข่งขัน accepted
API เปิด SQLite ด้วย mode=ro ไม่มีปุ่มแก้ข้อมูล อนุมัติ หรือส่งข้อความไปภายนอก
ปุ่มเปิด CSV นำไปยัง URL ต้นทางของ DMF โดยตรง
ใช้ SQL parameter binding และ textContent สำหรับข้อความต้นทาง ไม่แทรก source strings เป็น HTML
CSV neutralize formula prefixes ใน text fields สำหรับการเปิดใน spreadsheet

## ข้อจำกัดและผลตรวจ

ข้อมูลยังไม่ผ่าน LCI eligibility/หน่วยย้อนหลัง/numerical verification ทั้งชุด
ไม่มีการอ้างว่า 34,671 candidates เป็น verified LCI exchanges หรือ 12/12 spot-check คือความแม่นยำ 100%
ทดสอบ browser ค้นน้ำพอง เปิด provenance ดู quality/source registry และ conflict detail แล้ว
ทดสอบ API filters, literal SQL-injection string, export row count และการรักษาตัวคูณหน่วย
ทดสอบมือถือยังไม่ได้ทำ; มี responsive CSS แต่ไม่อ้างว่าตรวจทุกขนาดหน้าจอแล้ว

จากการเปิด conflict detail พบตัวอย่าง เอราวัณ มีนาคม 2566 ของ condensate สองแถว DAYSOFPRODUCE=7 และ 24 ซึ่งรวมได้ 31 วัน
นี่เป็นข้อบ่งชี้ว่า identity ระดับเดือนอาจขาด subperiod ไม่ใช่หลักฐานว่าต้นทางผิด ต้องตรวจรายงานก่อนรวม/ตัดสินค่าถูก
ระบบจึงคงทุกสมาชิกเป็น HOLD ไม่ใช้ first/last wins
