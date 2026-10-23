# DMF production data: source review และการใช้งาน

## ขอบเขต

ดาวน์โหลดตรงจาก CKAN API ของกรมเชื้อเพลิงธรรมชาติ 22 ตุลาคม 2569
API: https://catalog.dmf.go.th/api/3/action/package_show?id=production-oil
อีกสอง package คือ production-condensate และ production-natural-gas
ทั้งสามเป็น resource ของหน่วยงานเดียวกัน ไม่ถือว่าเป็น publisher อิสระสามแห่ง

Grain: ชื่อกลุ่มแหล่งผลิต/กลุ่มแปลง + ในทะเล/บนบก + เดือน + ชนิดผลิตภัณฑ์ ตามที่รายงาน
เก็บเป็น production observation ที่อาจใช้ประกอบ LCI ยังไม่อ้างเป็น inventory ต่อหนึ่งหน่วยผลิตภัณฑ์
ไม่อนุมาน input, emission, flaring หรือ process efficiency จากยอดผลิตรวม

## Pipeline ที่รันได้จริง

```powershell
python src/acquire_dmf.py
python -X utf8 src/process_dmf.py
python -m unittest discover -s tests -v
```

acquire ทำ network requests เฉพาะ CKAN metadata และ resource URL ที่ metadata ระบุ เว้นระยะ 1 วินาที
สร้างโฟลเดอร์ run ใหม่เสมอ และอัปเดต latest เฉพาะเมื่อได้ครบทุก package
process ทำงาน offline จาก latest snapshot ตรวจ SHA256 ก่อนอ่าน
รัน process ซ้ำสร้างผลใหม่จาก snapshot เดิม ไม่เพิ่มจำนวนแถว

ต้นฉบับอยู่ data/raw/dmf/<run_id>/ ทั้ง CSV, metadata JSON และ manifest
ผลอยู่ build/dmf/<run_id>/ ได้แก่ candidates.sqlite, candidates.csv, duplicate-review.csv, rejected.csv และ quality-report.json
ฐานข้อมูลมี raw_json ทุกแถว และ view traceable_candidate ที่ผูก URL + hash + หมายเลขบรรทัดต้นฉบับ
ข้อความถอดจากเว็บ 3 รายการเดิมไม่ถูกนำมาบวกกับชุด CSV นี้

## Mapping ที่พิสูจน์ได้

- Encoding ของไฟล์: cp874 อ่าน strict; เก็บ byte ต้นฉบับไม่เปลี่ยน encoding
- YEAR เป็น พ.ศ. แปลงเป็น ค.ศ. โดยลบ 543; เดือนต้องเป็น 1–12
- BLOCK_TYPE คงภาษาไทยและยอมรับเฉพาะ บนบก/ในทะเล
- BLOCK ว่างได้ใน staging/candidate พร้อม flag ไม่สร้างรหัสแปลงขึ้นเอง
- SOURCE_GROUP คงชื่อรวม ไม่แบ่งค่าเดียวออกเป็นหลายรายการ
- ค่า OIL/CONDENSATE/GAS เก็บ raw_value และ Decimal แบบ exact ไม่ปัดทศนิยมหรือใช้ float
- ไม่สร้าง candidate เพิ่มจาก GAS_EQUI_OIL และ CONDENSATE_EQUI_OIL แต่เก็บไว้ใน raw_json
- ศูนย์มีความหมายเป็นศูนย์; blank ถูก reject หากเป็น amount ที่จำเป็น
- DAYSOFPRODUCE ตรวจเป็นจำนวนเต็มและไม่เกินวันในเดือน ไม่ใช้คูณสร้าง monthly volume จนกว่ายืนยันฐานเวลา

## ปัญหาที่พบ

1. 34,905 raw rows; 34,899 ผ่านกฎรูปแบบเบื้องต้น และ 6 แถวขาด amount/area/source group
2. ช่วงข้อมูลที่ parse ได้ 2003-01 ถึง 2026-03 แต่ metadata last_year_of_data ยังระบุ 2567 (2024)
3. แต่ละ package มีรายการซ้ำตาม identity 45 แถว บางคู่ค่าขัดกัน ไม่มีการเลือกค่าล่าสุดอัตโนมัติ เพราะลำดับ CSV ไม่พิสูจน์ revision
4. BLOCK ว่างหลายรายการ คงไว้เพื่อ review และไม่ตีความว่าเป็นแหล่งเดียวกันทุกแถว
5. Metadata หน่วยไม่ได้ระบุฐานเวลา /day ทั้งที่รายงาน DMF รายเดือนแสดงอัตรารายวัน; natural gas metadata มี multiplier ล้าน
6. Label ใบอนุญาต Open Data Common, accessible_condition ระบุไม่มีการจำกัดการเข้าถึง แต่ isopen=false และ license_url ไม่มี จึงบันทึกเป็น rights clarification required

## Numerical evidence รอบแรก

ตรวจเทียบ CSV GAS เดือนมกราคม 2569 กับค่าที่อ่านจากรายงาน DMF ของเดือนเดียวกันในรอบก่อน:
ไพลิน / มรกต 260.81, อาทิตย์ 395.94, น้ำพอง 5.9 ตรงกันเชิง Decimal
นี่เป็นเพียง spot-check ภายในข้อมูลจาก publisher เดียว ไม่ใช่การตรวจทั้ง 34,899 รายการหรือหลักฐานอิสระ
ต้องเก็บรายงาน HTML/PDF/XLSX ต้นฉบับของช่วงที่จะตรวจ เพื่อยืนยันหน่วยและ footnotes เพิ่ม

## เกณฑ์ก่อนนับเข้าแข่งขัน

ยืนยันสิทธิใช้/redistribution, ฐานหน่วยและเวลา, numerical check, LCI semantics และ duplicate policy
ปัจจุบัน competition_accepted = 0; structural pass และ unique candidate identities เป็นตัวชี้วัดสำหรับงานตรวจเท่านั้น
ขั้นต่อไป: ตรวจคู่ค่าขัดกันและ metadata/รายงานให้ลงตัวก่อนขยายแหล่งข้อมูลอื่น
