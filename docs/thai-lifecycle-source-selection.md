# แหล่งไทยสำหรับกรณีศึกษาครบขอบเขตวงจรชีวิต

ตรวจ 3 พฤศจิกายน 2569 งานค้นต่อจาก T97 ไม่ใช่การรับข้อมูลใหม่เข้า production

## แหล่งที่แนะนำให้พัฒนาเป็นกรณีศึกษาแยก

**Sustainability Assessment of Palm Biodiesel Production in Thailand** — Thapat Silalertruksa และ Shabbir H. Gheewala, 2013, Biofuel Technologies, หน้า29–49, DOI10.1007/978-3-642-34519-7_2

หน้าผู้พิมพ์ https://link.springer.com/chapter/10.1007/978-3-642-34519-7_2 ยืนยันชื่อ ผู้เขียน ปี และเนื้อหาการผลิต/ใช้เชื้อเพลิงไทย หน้าทางการเป็น subscription preview ไม่ได้ซื้อหรือ bypass การเข้าถึง สำเนา PDF ที่ค้นพบเปิดดาวน์โหลดได้ เก็บ local/private/hash ไม่เผยแพร่ซ้ำ สิทธิ redistribution ยัง NOT_CLEARED ดู data/raw/thai-palm-chapter-2013/manifest.json

อ่านภาพเต็มหน้าพิมพ์33–36 (PDF45–48) แล้ว:

- Section2.3/Figure2.2: plantation, milling, biodiesel conversion, transport และ use เชื่อมอยู่ในผังเดียว
- Figure2.2 มี flow ปริมาณด้านวัตถุดิบ พลังงาน ผลผลิตร่วม น้ำเสีย และของเสีย เป็น candidate LCI ไม่ใช่เพียงคะแนน CO2e
- Section2.3.2/Table2.1: มี baseline และ3scenariosของ EFB/POME เช่น dumping/open ponds, co-composting และ biogas recovery
- Section2.3.4: transport capacity/distance อ้าง Pleanjai/Gheewala2009; Figure2.2 มีเชื้อเพลิงของ transport แต่ไม่ได้แปลว่า distribution ทุกขาครบ
- Section2.3.5: มี use-phase pollutants ต่อ litre จาก pickup-truck dynamometer study พร้อมการอธิบาย fossil/biogenic carbon

**เหตุผลที่เหมาะกว่าใช้ MexicoHEFA:** เป็นระบบ palm biodiesel ไทยและมี waste/use/transport อยู่ในเรื่องเดียว แต่ยังไม่ใช่ machine-readable complete inventory ที่ตรวจพร้อมใช้แล้ว

## ประเด็นที่ต้องปิดก่อนนำเข้าหรืออ้างพร้อมคำนวณ

1. **พบ basis ขัดกันจริง:** proseต้นหน้าพิมพ์36ระบุ production of1MJ แต่ Figure2.2 หน้าพิมพ์33 ระบุ1000MJ ในกล่อง biodiesel ต้องเก็บทั้งสอง locator และหาหลักฐานยืนยันก่อน scale ห้ามตัดสินเองจากความสมเหตุผลของตัวเลข
2. Allocationของบทนี้ต่างจากชุดปี2020: CPOประมาณ0.81 และ biodiesel0.92 ในข้อความ ไม่ใช้แทน0.92/0.70ของอีกชุดโดยตรง และยังต้องตรวจว่า flowในfigureเป็นก่อนหรือหลังallocation
3. Treatment scenarios ครอบของเสียจากโรงสกัด ไม่ได้หมายถึงมีปลายทางทุก waste stream หรือการกำจัดรถยนต์หลังใช้งานครบ คำว่า5stagesในบทนี้ไม่ตรงชื่อ5ช่วงของผู้ใช้แบบหนึ่งต่อหนึ่ง
4. ปริมาณการใช้ต่อlitreต้องมีความหนาแน่น/LHVที่ตรงรุ่น/แหล่งก่อนผูกกับFUพลังงาน ห้ามหยิบfuelpropertyอีกบริบทโดยไม่แสดงsurrogate
5. ตาราง/ผังไม่ได้แจกแจง elementary emissions/background ทุกตัว การมีfull-life studyไม่เท่ากับมีfull downloadableLCI dataset สิทธิและขอบเขตแต่ละproviderยังต้องตรวจ

ข้อเสนอ: ตั้งเป็น candidate ชุดไทย2013 แยกจากชุด2020ของเว็บ ตรวจผัง/ตาราง/สมมติฐานทั้งชุดก่อนเลือกใช้ ไม่เอาเฉพาะตัวเลขที่ขาดมาแปะปิดช่องว่างโดยอัตโนมัติ

## แหล่งอื่นที่คัดกรอง

**Energy and Greenhouse Gas Evaluation of Biodiesel and Bio-hydrogenated Diesel from Palm Oil in a Life Cycle Perspective** — Rotwiroon etal.,2012 มี affiliations PTT/MTEC/Chula ตามผลค้น มีtransport/logistics ที่น่าสนใจ แต่ PDFยังเปิดไม่สำเร็จในการตรวจเดิม จึงคง DISCOVERED_NOT_VERIFIED ไม่ใช้ตัวเลขsnippet

**Analysis of energy consumption and GHG emission in biodiesel(B100) production from oil palm**, ChulaETD17869, DOI10.58837/CHULA.THE.2012.1776: https://digital.car.chula.ac.th/chulaetd/17869/ หน้าสถาบันอ่านได้ ระบุข้อมูลสวน/โรงสกัด/โรงผลิตในตรัง กระบี่ ชุมพร แต่ abstractระบุgate-to-gate และไม่ได้รวมการใช้เชื้อเพลิง จึงไม่เลือกเป็นแหล่งครบวงจร มีปีmetadata2012กับabstractภาษาอังกฤษ2013ต้องตรวจfulltextถ้าใช้จริง

ไม่มีการเพิ่มobservationsหรือปิดT97ว่าเสร็จในรอบค้นนี้ ไม่ได้สร้างผลLCIAหรืออ้างรับรองMTEC

