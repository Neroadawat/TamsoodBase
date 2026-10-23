# เทียบโปรเจกต์กับเว็บ MTEC / Thai National LCI

ตรวจวันที่ 22 ตุลาคม 2569 ผ่านหน้าเว็บสาธารณะ ไม่เข้าสู่ระบบ ไม่สั่งซื้อ และไม่ได้ดาวน์โหลดบัญชี exchanges ที่มีเงื่อนไขเข้าถึง

## หลักฐานที่อ่าน

- [MTEC: ภารกิจฐานข้อมูล LCI](https://www.mtec.or.th/tiis/lci-database/)
- [MTEC: แนวทางจัดทำฐานข้อมูล](https://www.mtec.or.th/tiis/publications_media-thai-lci-database-manual-2/)
- [Thai National LCI: หน้าแรก](https://thainationallci.nstda.or.th/)
- [หน้าบริการและค้นข้อมูล](https://thainationallci.nstda.or.th/our-services?tab=tnlci-main)

หน้า MTEC อธิบาย LCI ว่าเป็นบัญชีสารและพลังงานเข้า–ออกระบบ และเน้นความโปร่งใสกับความน่าเชื่อถือ เว็บบริการแยกบัญชี LCI ออกจาก Environmental Impact และ Embedded Emission

เส้นทางตรวจจริง: หน้าแรก → WG1 Natural Gas → ก๊าซมีเทน (C1) Sale gas (Natural Gas) → ดูฐานข้อมูล → Documentation

ตัวอย่างที่เห็นระบุหน่วย kg, ประเทศไทย, ISIC 0620, กระบวนการโรงแยกก๊าซ, การปันส่วนโดยมวล และขอบเขตข้อมูลโรงงาน โดยหน้าแสดงปีชุดข้อมูล 2015 แต่ช่วงข้อมูลปฐมภูมิเป็น 1 มกราคม–31 ธันวาคม 2014 ข้อมูลนี้ใช้เป็นตัวอย่าง metadata เท่านั้น ไม่คัดลอกเป็น observation และไม่อ้างว่าดู numerical exchanges แล้ว

## สิ่งที่มีผลต่อโครงงานเรา

ข้อสรุปต่อไปนี้เป็นการวิเคราะห์ของทีมจากเว็บสาธารณะ ไม่ใช่เกณฑ์แข่งขันที่ MTEC ประกาศเพิ่ม:

| ประเด็น | สิ่งที่เรามี | การปรับและเกณฑ์ผ่าน |
|---|---|---|
| Process กับ product | ชนิดผลิตภัณฑ์และกลุ่มแหล่งของ DMF | หาเอกสารที่ระบุ extraction / separation / refining จริง แยก process boundary ออกจากชื่อเชื้อเพลิง |
| Inputs / outputs | ตัวเลข production statistics | ค้นพลังงาน วัตถุดิบ ผลผลิต มลสาร และของเสียที่เชื่อมกับ process เดียวกันได้ตามหลักฐาน |
| หน่วยอ้างอิง | หน่วย metadata แต่ฐานเวลายังไม่ยืนยัน | เก็บ quantity basis/denominator จากต้นทาง ไม่แปลง cubic feet เป็น kg โดยไม่มีสภาวะและองค์ประกอบก๊าซ |
| เวลา | เดือนปีของ observation และเวลาที่ดึง | แยก data period, publication/version year, accessed_at; ห้ามนำปีอัปเดตมาแทนปีที่วัด |
| วิธีคำนวณ | เก็บตัวเลขเดิม ไม่ปันส่วน | เก็บ allocation/calculation method เมื่อเอกสารระบุเท่านั้น ห้ามใช้ mass allocation จากชุดตัวอย่างกับทุกแหล่ง |
| ความเป็นตัวแทน | มี offshore/onshore และชื่อกลุ่มแหล่ง | ระบุ site/national/geographic scope และ coverage ตามคำต้นทาง ไม่เรียกทุกแถวว่าค่าเฉลี่ยประเทศไทย |
| LCI กับผลกระทบ | ยังไม่คำนวณ EF | แยกชนิดข้อมูล inventory/context/impact factor ไม่รวมเป็นจำนวน Accepted เดียวกันโดยอัตโนมัติ |
| หลักฐานและสิทธิ | raw hash/line/license label | คงที่มาระดับแถวและเก็บเงื่อนไข reuse; ใช้หน้า catalog เป็น reference โดยไม่ถือว่าค่า LCI ทั้งหมดเปิดให้คัดลอก |

## ลำดับทำต่อ

1. คง DMF เป็นชุด production context ที่ trace ได้ และรักษา Accepted=0 จนยืนยัน eligibility
2. สำรวจรายงานโรงแยกก๊าซและโรงกลั่นที่เปิดเผย input/output พร้อมเวลา หน่วย และ boundary ให้ตรงกัน
3. ทำตัวอย่าง mapping แบบครบหนึ่ง process ก่อนขยายจำนวน: raw evidence → process/flow/direction/amount/unit/basis/time/geography → validation
4. เมื่อบริบทชัดจึงขยาย schema แยก process, inventory exchange และ context observation โดยมี provenance ร่วมกัน ไม่บังคับข้อมูล DMF ให้เป็น normalized LCI exchange
5. การตีความเกณฑ์แข่งขันยังยึด Handbook และประกาศรายวิชาล่าสุด เว็บนี้ช่วยเข้าใจ domain แต่ไม่แทนคำอนุมัติของผู้สอน

ไม่เปลี่ยนค่า observation เดิมจากการค้นครั้งนี้ และไม่ใช้จำนวน dataset ในเว็บ MTEC เป็นจำนวน tuple ของทีม
