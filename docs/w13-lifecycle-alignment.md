# เทียบ W13 กับแผนขยาย LCI ทั้งวงจรชีวิต

ตรวจวันที่ 3 พฤศจิกายน 2569 จาก CN230-W13-A2-Lecture.pdf 40 หน้า โดยอ่านภาพหน้า 4–5 และข้อความส่วนสถาปัตยกรรม/การแปลงกราฟ หน้า 1, 3, 24–27 เอกสารนี้เป็นผลทบทวนและข้อเสนอ ไม่ใช่ข้อมูล LCI เพิ่มหรือการแก้ production

## สิ่งที่เลกเชอร์บอก และสิ่งที่ยังสรุปไม่ได้

หน้า 4 แสดงวงจร วัตถุดิบ → ผลิต → ขนส่ง → ใช้งาน → จัดการซาก และแยกกรอบ LCA 4 ระยะ: Goal & Scope, Inventory, Impact, Interpretation งานวิศวกรรมข้อมูลเน้น Inventory และตรวจกลับถึงแถวต้นทางได้ จึงควรรองรับทั้งห้าช่วง แต่สไลด์หน้านี้เพียงอย่างเดียวยังไม่ยืนยันเกณฑ์คะแนน final ว่าต้องมีค่าครบทุกช่วงหรือทำ LCIA เต็มรูปแบบ

หน้า 5 ให้แนวคิด activity × EF และการ JOIN/SUM โดย EF มี version/วันที่มีผล ตัวเลข 120 kWh, 0.5, 97 kgCO2e เป็นตัวอย่างสมมติ สไลด์ระบุว่าไม่ใช่ค่า EF จริงของ อบก. ห้ามนำเข้าฐานข้อมูลจริง หน้า 1/3 ให้ RDBMS เก็บความจริงด้วย ACID ส่วน graph ใช้ไล่ความสัมพันธ์ หน้า 25 ให้คง identity/FK/property เมื่อแปลงเป็นกราฟ การมี Neo4j จึงไม่ทดแทนหลักฐานว่ากระบวนการเชื่อมกันได้จริง

## เลือกกรณีศึกษาเดียวก่อน

แนะนำ FAME จากปาล์มก่อน เพราะเรามีข้อมูล FFB/CPO/RBDPO/FAME จากการศึกษาเดียวกันอยู่แล้ว H-FAME เป็นอีกเส้นทาง ไม่รวมเข้ากับ FAME อัตโนมัติ รักษา FU ของการศึกษาเดิมเป็นการใช้เชื้อเพลิง 1,000 MJ และฐานตารางต้นน้ำ 1,000 kg แยกกัน จนมี reference-flow conversion และ allocation ที่ตรวจได้

## สถานะทั้งห้าช่วงจากหลักฐานของระบบ

| ช่วง | มีอะไรจริง | ช่องว่างก่อนเชื่อมเป็นโมเดล | ข้อมูลที่ต้องหา |
|---|---|---|---|
| 1 ได้มาซึ่งวัตถุดิบ | FFB 19 observations และ CPO 12 จาก Tables 1–2 | 1 ค่าไม่มีหน่วยต้อง HOLD; ปริมาณ FFB เข้า CPO ขาด; allocation ยังไม่ชัด | FFB input ต่อฐาน CPO, ปี/พื้นที่/ผลผลิต, ปุ๋ยและ emissions ตรงบริบท, วิธีจัดสรร |
| 2 ผลิต | RBDPO 11, FAME 10, H-FAME 6 จาก Tables 3–4 | รวม 58 observations ใน 5 processes ไม่ใช่ 58 datasets; provider links ยังไม่ apply; background ไฟฟ้า/สารเคมียังไม่เชื่อม | calculation basis, provider ที่เข้ากัน, วิธีป้องกันคูณ allocation ซ้ำ, elementary-flow mapping |
| 3 ขนส่งและจำหน่าย | ยังไม่มี inventory ขนส่งที่เชื่อมกับชุดนี้ | ห้ามใช้ยอดขนส่งประเทศแทนเที่ยวขนส่งผลิตภัณฑ์ | สินค้า/ต้นทาง/ปลายทาง/ระยะทาง/พาหนะ/น้ำหนัก/โหลด/เที่ยวเปล่า/เชื้อเพลิงหรือ t·km และขอบเขตของ provider |
| 4 ใช้งาน | แหล่งวิจัยกำหนด FU การใช้ 1,000 MJ แต่ยังไม่ได้นำเข้าชุด use-phase exchanges | การมี FU ไม่ได้แปลว่ามี emissions จากการใช้ครบ | fuel properties/LHV/ประสิทธิภาพที่ตรงกรณีศึกษา, การเผาไหม้และสารปล่อยพร้อมหน่วย/compartment; แยก fossil/biogenic ตามวิธีที่เลือก |
| 5 หลังใช้งาน | ยังไม่มี treatment process ที่เชื่อมและตรวจแล้ว | สำหรับเชื้อเพลิงที่ถูกเผาไหม้ ต้องไม่สร้าง 'ขยะเชื้อเพลิง' ซ้ำกับ use emissions | ของเสีย/น้ำเสีย/กาก/บรรจุภัณฑ์ที่อยู่ในขอบเขตจริงและเส้นทางบำบัด; เหตุผลรวม/ไม่รวม; cut-off ที่ระบุชัด |

ขอบเขต 'การจัดการหลังใช้งาน' ต้องระบุว่าหมายถึงอะไรในผลิตภัณฑ์เชื้อเพลิง ของเสียจากโรงงานเกิดในช่วงผลิตแต่เชื่อมไป treatment process ได้ ไม่ควรนับ emissions ซ้ำทั้งช่วงผลิตและปลายทาง ไม่รวมการกำจัดรถยนต์โดยอัตโนมัติหากไม่ได้อยู่ใน goal/scope

## การปรับฐานข้อมูลที่เสนอ

เป็นแบบร่างต่อจาก versioned-review schema ไม่ใช่ migration ที่ติดตั้งแล้ว:

- `STUDY_SCOPE`: product route, FU amount/unit/service, geography, time, boundary, cut-off, method version และแหล่งอ้างอิง
- `LIFECYCLE_STAGE`: รหัสห้าช่วง เพื่อจัดหมวด ไม่ถือว่ามีข้อมูลเพียงเพราะมีรหัส
- `STUDY_STAGE_COVERAGE`: study version + stage, สถานะ PARTIAL/MISSING/EXCLUDED_WITH_REASON, inclusion reason, evidence และ open issue ไม่ใช้จำนวนแถวคำนวณความครบถ้วน
- ความสัมพันธ์ study–process version: process หนึ่งใช้ได้ในหลายการศึกษา/ช่วงตามบริบท จึงไม่เพิ่ม stage เป็นข้อความคงที่ใน FLOW เช่น diesel อาจเป็นวัตถุดิบหรือเชื้อเพลิงขนส่ง
- provider link ต้องระบุ consuming exchange, producing process version/reference product, conversion factor และหลักฐานความเข้ากัน มีสถานะ CANDIDATE/VERIFIED/APPLIED แยกกัน
- หากเพิ่ม EF ในอนาคต: version, publisher, effective period, geography, technology, flow/unit compatibility, boundary coverage, method/GWP และสิทธิ ต้องแยก direct combustion factor จาก life-cycle factor เพื่อป้องกัน upstream double counting

การบันทึก source + process version + exchanges + audit ต้องเป็น transaction เดียว และ rollback เมื่อ FK/หน่วย/ฐานไม่ตรง กราฟเป็น projection จาก release ที่ปิดเวอร์ชันแล้ว รักษา observation ID/version/hash และตรวจ SQL–Cypher บนข้อมูลชุดเดียวกัน ก่อนอ้างว่าผลเท่ากัน ไม่เพิ่ม APPLIED edge เพื่อให้ภาพ supply chain ดูครบ

## ลำดับลงมือที่เหมาะ

1. ปิด calculation basis/allocation/FFB-input ของเส้นทาง FAME ก่อน หาหลักฐานจากการศึกษาเดียวกันก่อนหา surrogate
2. ตรวจ transport/use sections และภาคผนวกของการศึกษาเดิม เก็บ locator/ค่า/หน่วย/ฐาน/ปี/สิทธิครบ หากไม่มีให้ลง MISSING ไม่เติมศูนย์
3. กำหนด waste/end-of-life relevance และเหตุผลตัดขอบเขตอย่างชัดเจน แยก emissions จาก treatment กับ emissions จาก use
4. เมื่อได้หลักฐานจึงสร้าง candidate schema/projection และทดสอบ reference-flow scaling, provider compatibility, allocation-once และ no-double-counting โดยยังรักษาข้อเท็จจริงเดิม
5. แสดงบนเว็บเป็นแผนภาพห้าช่วงพร้อมคำว่า มีบางส่วน/ยังขาด/ไม่รวมพร้อมเหตุผล และเปิดต้นทางได้ ไม่แสดงเปอร์เซ็นต์พร้อมใช้หรือป้ายครบวงจรจากจำนวนแถว
6. LCIA/คาร์บอนเป็นขั้นต่อไปหลัง inventory เชื่อมได้ ใช้ EF จริงที่มีเวอร์ชันและขอบเขตตรงกัน ไม่ใช่ตัวเลขจากตัวอย่างในเลกเชอร์ ไม่อ้างฉลากหรือการรับรอง

เกณฑ์จบ: ทุกช่วงมี inclusion decision ที่อธิบายได้; ทุก process ที่รวมมี exchanges/reference basis/provenance; ทุก link ที่ apply ผ่าน compatibility; scaling และ allocation ทำซ้ำได้; ไม่มี missing-as-zero/double count; ข้อจำกัดยังปรากฏใน export/UI/SRS การเขียนแผนครบห้าช่วงไม่ใช่การผ่านเกณฑ์เหล่านี้

หลักฐานระบบที่ใช้: evidence/combined-inventory-review.json, docs/inventory-scope-contract.md, docs/expert-review-checkback.md และ docs/team-data-policy.md ไม่มีการเพิ่ม observations, เปลี่ยนสิทธิ, deploy หรือรับรองผลทดสอบระบบใหม่ในการทบทวนนี้
