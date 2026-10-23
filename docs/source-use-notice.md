# Third-party source notice / วิธีใช้หลักฐาน

ตรวจ 23 ตุลาคม 2569 แยกความพร้อมข้อมูลออกจากสิทธิแจกจ่าย เอกสารนี้บันทึกหลักฐานที่พบและการตัดสินใจของโครงการ ไม่ได้ออกใบอนุญาตแทนเจ้าของข้อมูล

| แหล่ง | หลักฐานที่ตรวจ | การใช้ในโครงการ |
|---|---|---|
| DMF CSV 3 packages | metadata ระบุ Open Data Common/เข้าถึงไม่จำกัด แต่ isopen=false; evidence/dmf-rights-review-2026-10-22.json | เก็บ attribution และ metadata anomaly; raw อยู่ local; ไม่ขยายสิทธิไปยังทุกหน้าเว็บ DMF |
| Thai Oil report 2024 | [เว็บ IR เจ้าของรายงาน](https://investor.thaioilgroup.com/en/home) มี footer Copyright 2024 / All rights reserved | รายงานและ observations อยู่ local research; เก็บ URL/page/hash; ยังไม่รับรองสิทธิแจกจ่าย raw หรือฐาน derived data สาธารณะ |
| SPRC report 2024 | [เว็บ IR เจ้าของรายงาน](https://investor.sprc.co.th/en/home) มี footer Copyright 2024 / All Rights Reserved | เช่นเดียวกัน ไม่ถือ public download ว่าเป็น open-data license |
| Lecture / handbook | เอกสารที่ผู้ใช้ส่งเพื่อประกอบโครงการ | ไม่รวม PDF หรือข้อความ lecture ทั้งฉบับในแพ็กเกจ |

หลักฐาน footer เป็นข้อมูลจากข้อความหน้าเว็บที่เครื่องมืออ่านได้ ไม่ใช่การเก็บหน้า HTML ต้นฉบับ และไม่ได้พิสูจน์ว่าเงื่อนไขของทุกเอกสารเหมือนกัน การไม่พบ open license ในหน้าที่ตรวจไม่ใช่ข้อสรุปว่าไม่มีใบอนุญาตอื่นอยู่เลย

## รูปแบบส่งหลักฐานที่เตรียมได้

- ส่ง code, schema, mapping และคำสั่งสร้างซ้ำ พร้อมรายการ attribution/URL/page/hash
- ใช้ demo จากไฟล์ในเครื่อง และเปิดลิงก์เจ้าของรายงานเพื่อชี้ตำแหน่งต้นฉบับ
- แพ็กเกจ reference-data-local.zip เป็นสำเนาเพื่อใช้งานภายใน ไม่ใช่ public release หรือการอนุญาตใช้เชิงพาณิชย์
- ก่อนส่งแพ็กเกจข้อมูลออกนอกเครื่องหรือเผยแพร่ ต้องตรวจเงื่อนไขที่ใช้กับรูปแบบนั้นจริง ไม่แนบ raw PDF เพียงเพราะดาวน์โหลดได้
- ไม่ใช้ privacy statement ของระบบสมัครอีเมลเป็นใบอนุญาตนำข้อมูลรายงานกลับมาแจกจ่าย

ผลตรวจสิทธิรอบนี้เสร็จเป็น notice แล้ว แต่สถานะ redistribution ของรายงานยัง NOT_CLEARED อย่างตั้งใจ ไม่รอคำยืนยัน MTEC เพื่อทำฐานข้อมูลต่อ และไม่ส่งข้อความขอสิทธิแทนผู้ใช้
