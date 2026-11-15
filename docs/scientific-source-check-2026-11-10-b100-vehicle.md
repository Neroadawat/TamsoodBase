# คัดกรองข้อมูลใช้ B100 ในรถกระบะไทย — 10 พฤศจิกายน 2569

## สิ่งที่พบ

พบวิทยานิพนธ์ปฐมภูมิของ Phobkrit Kanokkhanarat (KMITL, 2023), *Influence of Biodiesel and Biodiesel Blended with Ethanol Fuels on Combustion and Emission Characteristics of Diesel Engine and Vehicle*, รหัส KMITL-2023-EN-M-037-012. ไฟล์อยู่บน repository host ของ KMITL: [PDF ต้นฉบับ](https://opacimages.lib.kmitl.ac.th/medias/b00293450/Phobkrit%20Kanokkhanarat.pdf).

หลักฐานข้อความที่อ่านได้ระบุว่าเชื้อเพลิง B100 ในงานทำจากน้ำมันปาล์มด้วย acid-esterification/transesterification กับ methanol (printed pp. 15–17). ผู้วิจัยทดสอบรถ Toyota Hilux Tiger เครื่อง 2KD-FTV ขนาด 2,500 cc น้ำหนัก 1,590 kg บน chassis dynamometer ที่ห้องทดสอบของ Pollution Control Department ตามรอบ New European Driving Cycle: เมือง 4 km/780 s และทางหลวง 7 km/400 s (printed pp. 20–22). Figure 4.85 รายงาน CO₂ ของรถเป็น mg/km แยกช่วงเมือง ทางหลวง และรวม; งานยังรายงาน PM, hydrocarbon, CO และ NOx.

## ประเมินความเกี่ยวข้องและข้อจำกัด

นี่เป็น **ผู้สมัครแหล่งอ้างอิง use-phase ของ B100** ที่ตรงกว่างาน E10 สำหรับอธิบายว่ามีการทดสอบรถกระบะด้วย B100 ปาล์มจริง แต่ยังเป็นเพียงข้อมูลอ้างอิงแยก ไม่ได้ปิด use gate ของกรณีทีม:

- ปีบนวิทยานิพนธ์คือปีเผยแพร่/สำเร็จการศึกษา 2023; ข้อความที่ตรวจไม่ระบุวันหรือช่วงทดสอบเชื้อเพลิงและรถ จึงไม่ตั้ง data period เป็น 2023.
- รอบที่ใช้คือ NEDC ซึ่งเป็น driving cycle ยุโรป แม้ทดสอบในไทย ไม่ใช่หลักฐานว่าผลแทนการขับขี่ไทย.
- ผล CO₂ เป็นต่อกิโลเมตร แต่โมเดลทีมอ้าง 1,000 MJ ของเชื้อเพลิง; ยังไม่มีระยะทางที่ทำได้ต่อพลังงานเชื้อเพลิงในรอบเดียวกันที่ตรวจได้ จึงแปลง mg/km เป็นมวลต่อ FU ไม่ได้.
- ตารางคุณสมบัติเชื้อเพลิงมี carbon, calorific value และ density ของตัวอย่าง B100 แต่ยังไม่ได้พิสูจน์ว่า calorific-value basis ตรงกับ LHV ที่โมเดลต้องใช้ หรือว่าตัวอย่างนี้ตรงกับ B100 ในแหล่งกระบวนการผลิตของทีม.
- แหล่งนี้ไม่ได้ให้ CH₄/N₂O ของรถครบตาม FU; ห้ามถือว่าไม่มี/เป็นศูนย์ และห้ามเปลี่ยน CO₂ ไอเสียรวมเป็น CO₂e ของเชื้อเพลิงทั้งวงจร.
- ข้อความลิขสิทธิ์ในเล่มอนุญาตเพื่อการศึกษา ไม่อนุญาตเชิงพาณิชย์ และห้ามดัดแปลงเนื้อหา; ไม่ได้ให้สิทธิแจกจ่ายชุดข้อมูลต่อ. เก็บเป็น citation/metadata ภายในเท่านั้นจนกว่าจะตรวจสิทธิการใช้ในเว็บ/RAG แยกต่างหาก.

## การตัดสิน

จัด `HOLD_CONTEXT` เป็น historical Thai B100 pickup-use reference candidate; `current_FAME_inventory_imports=0`, `use_gate_closed=false`, `CO2e_total` ไม่เปลี่ยน, `redistribution_status=NOT_CLEARED`, ไม่ใส่ตัวเลขกราฟลงฐาน/เว็บ/RAG. ยังไม่ได้เก็บ local PDF/hash และไม่ได้ตรวจภาพกราฟกับทุกค่าในหน้าต้นฉบับ จึงไม่อ้างว่า source-cell หรือ visual audit ผ่าน. หลักฐาน structured อยู่ใน [`evidence/scientific-source-check-2026-11-10-b100-vehicle.json`](../evidence/scientific-source-check-2026-11-10-b100-vehicle.json).

## หลักฐานที่ต้องมีเพื่อพิจารณาต่อ

1. หน้าต้นฉบับ/ตารางที่ระบุเชื้อเพลิงต่อ cycle หรือ g CO₂e/MJ โดยคงตัวหารและ configuration รถเดิม พร้อมตรวจภาพทุกช่อง.
2. วันที่/ช่วงเก็บข้อมูล, การทำซ้ำ, uncertainty และขอบเขตของ cold start/เครื่องร้อน, ระบบ DOC และ phase labels.
3. การวัดหรือปัจจัย CH₄ และ N₂O ที่เข้ากันกับรถ/รอบ/เชื้อเพลิง; ถ้าไม่มี ให้คงเป็น null.
4. LHV ที่ระบุชัดของ B100 ตัวอย่างเดียวกัน และการจับคู่กับผลิตภัณฑ์/ช่วง/วิธีผลิตของ foreground chain.
5. การยืนยันสิทธิใช้ข้อมูลใน public website/RAG จากผู้ถือสิทธิ; ข้อความเพื่อการศึกษาไม่ถือเป็นใบอนุญาตเผยแพร่ต่อ.
