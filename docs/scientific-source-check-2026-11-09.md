# ตรวจแหล่งข้อมูล FAME/LCI เพิ่ม — 9 พฤศจิกายน 2569

ค้นต่อแบบเจาะจงเรื่องการขนส่ง การใช้ B100 และฐานข้อมูล LCI ไทย โดยใช้ผลค้นของวารสาร/หน่วยงานและเปิดต้นฉบับที่เข้าถึงได้ ผลรอบนี้ไม่ทำให้ตัวเลขของกรณี FAME ปัจจุบันเพิ่มขึ้น และไม่ปิด gate ที่ต้องการความเข้ากันได้กับ functional unit, process, engine, provider และงวดข้อมูลของกรณีนี้

## แหล่งที่ตรวจ

| แหล่ง | ข้อมูลที่ตรวจได้ | การตัดสินต่อกรณีปัจจุบัน |
|---|---|---|
| Rewlay-ngoen et al. (2013), [ต้นฉบับ PDF](https://ph02.tci-thaijo.org/index.php/ennrj/article/download/83884/66780/203319), หน้า 25–26 | อธิบาย case biodiesel จากปาล์มไทย ใช้ระยะขนส่งสมมติ 20 km round trip ในช่วงที่ระบุ และ mass allocation ระหว่าง CPO/kernel และ biodiesel/glycerin; ระบุแหล่งข้อมูลผสม Thai LCI, ecoinvent และงานเดิม | เป็นหลักฐานสำหรับ benchmark ทางประวัติศาสตร์เท่านั้น ขอบเขต/วิธี/ปีไม่ตรงกับกรณี 1000 MJ ปี 2020 และไม่ให้ provider/vehicle/เที่ยวขนส่งที่ตรงกับ chain ของเรา จึงไม่เติมระยะทางหรือ allocation ให้กรณีปัจจุบัน |
| Spatially differentiated LCA of Thailand’s transport (2025), [DOI](https://doi.org/10.1016/j.spc.2025.04.023) | ผลค้นของบทความระบุว่าศึกษา transport หลาย mode และ biodiesel 100% ที่อิง Thai LCI ปี 2013 ขณะเดียวกัน background ใช้ ecoinvent 3.8; DOI redirect เปิดตัวเนื้อหาฉบับเต็มจากเครื่องมือค้นรอบนี้ไม่ได้ | Candidate สำหรับเทียบวิธี/บริบท transport เท่านั้น ยังตรวจตารางและข้อมูลดิบไม่ได้ ไม่คัดลอก inventory และไม่ใช้แทนขนส่งในขอบเขต FAME ของทีม |
| Thai National LCI Database, [หน้าทางการ](https://thainationallci.nstda.or.th/) | ยืนยันว่ามีบริการเผยแพร่ LCI ไทยและข้อมูลผลกระทบ | หน้า landing ไม่แสดง process record, version, exchange, provider, period หรือ license ของ record biodiesel ที่ต้องใช้ จึงไม่ใช้เป็นหลักฐานตัวเลขหรือสิทธิของชุดข้อมูล |
| Limratana et al. (2010), [หน้าบทความ](https://li01.tci-thaijo.org/index.php/anres/article/view/245102) | ทดลอง B100 จาก palm oil กับเครื่องเรือและ generator; รายละเอียดหน้า journal จำกัดที่ BSFC, thermal efficiency, exhaust temperature และ CO ภายใต้ engine/load ที่ศึกษา | ไม่ใช่ pickup-truck engine และไม่ให้คู่ CH4/N2O ที่ตรงกับ study 2020; ใช้ปิด use-phase ไม่ได้ |

## ผลต่อสถานะข้อมูล

- ไม่เพิ่ม observation หรือ factor ให้ `evidence/lifecycle-candidate.json` และไม่ใช้ระยะ 20 km ในบทความปี 2013 แทนหลักฐานเดิมของขนส่ง FFB ราว 5 km ใน scenario ปี 2019
- ไม่ใช้ข้อมูลเครื่องเรือแทน pickup truck และไม่ผสม biodiesel ที่ผลิตจาก waste cooking oil หรือสูตร blend กับกรณี FAME จาก palm oil
- ไม่เปิดหรือดาวน์โหลดชุดข้อมูลที่ต้อง login/ไม่มีสิทธิยืนยัน และไม่ตีความหน้า landing เป็นการอนุญาตนำข้อมูลไปแจกจ่าย
- `CO2e_total=null`; ยังไม่เรียกกรณีนี้ว่า full lifecycle inventory

นี่เป็น targeted source screen ไม่ใช่ systematic review และการเข้าถึงบทความปี 2025 ที่ไม่สำเร็จไม่ใช่หลักฐานว่าไม่มีข้อมูลในฉบับเต็ม
