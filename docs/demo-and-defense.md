# Demo และการอธิบายผลงาน

ใช้สถานะจริงของ release ปัจจุบัน ไม่อ้างว่าได้รับอนุมัติ MTEC ไม่ต้องรอคำยืนยันภายนอก และไม่อ้างว่ามี normalized product LCI หากยังไม่มี reference product/การจัดสรรที่รองรับ

## Demo ประมาณ 6–8 นาที

1. **โจทย์และขอบเขต (1 นาที):** สร้างฐานข้อมูลอ้างอิง Petroleum, Natural Gas & Fuels ที่เกี่ยวข้องกับไทยจากข้อมูลกระจัดกระจาย แยก production statistics, organizational inputs/outputs, reported intensity และ context เพื่อใช้ต่อได้ตามความหมายจริง
2. **คุณภาพและ traceability (1 นาที):** เปิดเว็บ สำรวจ DMF → เลือกตัวอย่าง → เปิด CSV line/hash อธิบายว่า raw 34,905, structural pass 34,899, reject 6, exact copies แยก 42, hold 186 และเหลือ deduplicated pending 34,671 ตัวเลขเหล่านี้ไม่ใช่จำนวน accepted reference ของชุดรายงาน
3. **ผลผลิตที่ใช้ต่อได้ (1–2 นาที):** เปิด “พร้อมใช้ต่อ” แสดง 97 accepted reference กับ 4 held context กรอง SPRC / 2024 / reported intensity จะได้ 2.57 GJ/t throughput เปิดหลักฐานหน้าไฟล์ 121/เลขพิมพ์ 120 แล้วส่งออก CSV/JSON ตามตัวกรอง
4. **พิสูจน์การตัดสินใจ (1 นาที):** เปิด “ข้อมูลจากรายงาน” → SPRC ปี 2024 → ปัญหาตารางน้ำ อธิบายว่าชื่อ/หน่วยและบริบทต่างกัน จึงเก็บทั้งคู่และไม่เลือกฝ่ายใด มีหลักฐานหน้า 49/119 ไม่ปรับเลขให้ตรงกัน
5. **ออกแบบและ SQL (1–2 นาที):** เปิด reusable-model.md ชี้ document/context/metric/observation/review/release อธิบาย composite FK ป้องกันขอบเขตข้ามเอกสาร และ policy-version รักษาผล review รุ่นเก่า ใช้ reusable-queries.sql กรอง release ที่ต้องการก่อน query
6. **ใช้ภายนอกเว็บและข้อจำกัด (1 นาที):** รันตัวอย่าง Python ด้านล่าง แสดง source scope ของแต่ละบริษัท ใช้ Decimal ไม่บวกยอดจากคนละขอบเขต จากนั้นเปิด manifest และอธิบายสิทธิใช้งาน/redistribution_status ที่ติดไปกับข้อมูล

## คำสั่งสำหรับเดโม

```powershell
python -X utf8 src/explorer.py
python -X utf8 examples/use_reference.py build/reusable/accepted-reference.json --year 2024
python -X utf8 scripts/check_release.py
```

หาก server เปิดอยู่แล้วไม่ต้องเปิดซ้ำ ถ้าจะสาธิต extraction ใช้ `python -X utf8 scripts/run_reference.py --mysql` ซึ่งอ่าน raw snapshot ในเครื่องและสกัดซ้ำ 101 ค่า ไม่จำเป็นต้องเรียกเว็บไซต์ระหว่างนำเสนอ

SQL ตัวอย่างอยู่ sql/mysql/reusable-queries.sql; benchmark รัน `python -X utf8 scripts/benchmark_sql.py` เฉพาะเมื่อต้องวัดผลใหม่ ไม่สร้าง index หรือแก้ข้อมูลระหว่าง benchmark

## คำถามซ้อมพร้อมหลักคิดคำตอบ

| คำถาม | คำตอบที่ต้องอธิบายจากหลักฐาน |
|---|---|
| 97 accepted หมายถึงอะไร? | ทีมรับเป็น source-attributed reference data ภายใต้ LOCAL_RESEARCH_REFERENCE ไม่ใช่ 97 independent flows หรือ LCI ต่อผลิตภัณฑ์ |
| ทำไมแยก 4 รายการ? | 2 issue คู่ตารางน้ำ ปี 2024 มีสมาชิกไม่ซ้ำ 4 แถว คงทุกค่าและ locator แต่ไม่ให้เข้า default accepted export |
| ทำไมไม่รวมชื่อก๊าซธรรมชาติข้ามบริษัท? | ชื่อเหมือนกันไม่ได้ทำให้ process/boundary เหมือนกัน metric identity จึงรวมเอกสารกับ mapping semantics |
| ทำไม amount ไม่ใช้ FLOAT? | ต้องรักษาทศนิยมต้นฉบับและตรวจ exact scaling จึงใช้ Decimal/MySQL DECIMAL และ SQLite decimal string |
| million GJ เป็น GJ ถือว่า normalization หรือไม่? | เป็น unit scaling ด้วยตัวคูณ ไม่ใช่การหารด้วย reference product หรือ allocation |
| ทำไม m3/year ไม่แก้เป็น m3? | เวลาเป็นส่วนหนึ่งของ unit label เดิม จึงรักษาไว้และระบุ quantity basis แทนการลบตัวหาร |
| จะบวก total fuel กับ fuel components ได้ไหม? | ไม่ได้ เพราะ overlap ใช้ aggregation_role ช่วยให้ผู้ใช้เห็นบทบาท แต่ยังต้องเลือกชุดที่ไม่ซ้ำตาม use case |
| schema ผ่าน 3NF ทุก field หรือไม่? | แยกเอนทิตีตาม FD เพื่อลด anomalies แต่ raw_value กับ scaled_amount เป็น redundancy ที่ตั้งใจเพื่อ audit ต้องอธิบายข้อยกเว้นอย่างตรงไปตรงมา |
| ทำไมมี release_observation? | แยก observation identity จาก membership แต่ละรุ่น ทำให้ reproduce รุ่นเก่าและไม่บวกข้อมูลซ้ำเมื่อ query หลาย release |
| การ re-extract ทุกค่าพิสูจน์อะไร? | พิสูจน์การอ่าน source bytes และ year column ของ subset ที่เลือก ไม่รับรองว่าเอกสารต้นทางถูกต้องทุกบริบท |
| index มีประโยชน์จริงไหม? | แสดง workload, equality ของผลลัพธ์ และ EXPLAIN ANALYZE ที่วัดในเครื่อง ไม่อ้างเวลานี้เป็น production SLA |
| AI ช่วยอะไร? | ช่วยค้น วิเคราะห์ ออกแบบ เขียนโค้ดและเอกสาร สมาชิกต้องตรวจสิ่งที่ใช้และอธิบายงานจริงของตน ห้ามอ้างว่าตรวจเองถ้ายังไม่ได้ตรวจ |
| สมาชิกแต่ละคนทำอะไร? | ตอบจาก contribution log จริงเท่านั้น ยังไม่เติมชื่อหรือย้อนหลังผลงานให้ใคร |

## ก่อนนำเสนอจริง

ตรวจว่า browser/API/SQLite/MySQL ใช้ release_id เดียวกัน ไฟล์ export เปิดได้และ hash ตรง มีสำเนา raw local สำหรับ trace เมื่อเน็ตใช้ไม่ได้ สมาชิกต้องซ้อมอธิบายทั้งตัวอย่างที่รับและตัวอย่างที่พัก การซ้อมจริงและการตอบรายบุคคลต้องทำโดยสมาชิก ไม่สามารถนับจากการมีเอกสารนี้เพียงอย่างเดียว
