# แผนประกอบกรณีศึกษา B100 ไทยและสถานะจริง

ผลตรวจเพิ่มเติม5พ.ย.: ดู [ทะเบียนปิดข้อค้าง](fame-gate-closure-review.md) มี6การตัดสิน/7ข้อความต้นฉบับตรวจ2extractors;ยืนยันmethod/factorsแต่tablebasisยังไม่ชัด ไม่คูณซ้ำ;แหล่งCOMPETEใหม่production-onlyไม่ปิดuse/transport งานT107ยังไม่เสร็จ

อัปเดต5พฤศจิกายน2569 หลังผู้ใช้อนุญาตให้ทำตามลำดับทั้งหมด งานหลักT97ยังไม่เสร็จ ไม่ใช้จำนวนtask/จำนวนแถวเป็นเปอร์เซ็นต์ความครบLCI

## ตรวจเพิ่ม 10 พฤศจิกายน 2569 — use-phase Pleanjai (2008)

บท Springer ปี 2013 รายงานค่าปล่อยไอเสียต่อ L จาก pickup/LDDV และอ้าง Pleanjai (2008), *Integrated environmental assessment of biodiesel from palm oil* (PhD dissertation, JGSEE/KMUTT). ยังหา full text ทางการของวิทยานิพนธ์ไม่พบ; ค่าที่เห็นจึงเป็น secondary-reported ไม่ใช่ข้อมูลทดสอบที่ตรวจซ้ำได้. ห้าม scale เข้ากับ FU 1,000 MJ ของโมเดลปี 2020 เพราะยังไม่มี LHV/density และ test/provider compatibility ที่ยืนยัน. สถานะ `HOLD_CONTEXT`, ไม่เพิ่ม inventory, ไม่ปิด T97/T107. รายละเอียด: [source screen](scientific-source-check-2026-11-10-pleanjai-use.md).

## กรณีศึกษาที่เริ่มประกอบ

เลือกเส้นทางFAMEจากปาล์มไทยบนฐาน **use of1000MJfuel** ตามงาน2020 DOI10.3390/su12229415 ส่วนphysicalmodelที่สร้างได้ขณะนี้จบที่การผลิตFAME การระบุstudyFUไม่ได้แปลว่าusephaseถูกคำนวณแล้ว

เลือกMill1ของTableS2ปี2019เป็นbaselineเชิงคำนวณด้วยกฎfirstsourcecolumnที่อธิบายได้ และเก็บMill2–6เป็นทางเลือกทั้งหมด ไม่เลือกเพราะได้คาร์บอนต่ำสุด ไม่อ้างความเป็นตัวแทนประเทศไทย และไม่เดาชื่อ/จังหวัดโรงงานรายMillเพราะต้นฉบับไม่ได้จับคู่ไว้

การแทนCPO2020ด้วยโรงสกัด2019เป็น **explicit mixed-vintage activity scenario** เท่านั้น ผลไม่ได้เป็นการวัดห่วงโซ่อุปทานจริงที่โรงงานเหล่านี้ซื้อขายกัน และยังไม่ผ่านquality/technology/period compatibility ห้ามใช้ไฟล์นี้เป็นcompleteenvironmentalLCI

## ลำดับงานและเกณฑ์จบ

| ลำดับ | งาน | สถานะ5พ.ย. | หลักฐานหรือสิ่งที่ยังต้องปิด |
|---|---|---|---|
| 1 | เลือกผลิตภัณฑ์/กรณี/ขอบเขต | ตั้งกรณีแล้ว | FAME1000MJ,Mill1baseline+5alternatives;ต้องยืนยันperiod/providercompatibilityก่อนใช้ผลจริง |
| 2 | เชื่อมปริมาณและallocation | physicalactivityเชื่อมแล้ว;allocationยังเปิด | RBDPO24.6kg→CPO27.06kg→FFBตามMill;3transferbalancesตรง แต่ไม่รู้tableก่อน/หลังallocationจึงไม่คูณ0.92/0.70 |
| 3 | ขนส่งและจำหน่าย | บางส่วน | FFB→millประมาณ5kmจาก2019ตรวจ2extractors+ภาพ;เที่ยวกลับ/โหลด/รถ/providerยังไม่มี อีก3ขาระยะยังnull |
| 4 | ใช้งาน | มีcandidate2013ยังไม่เชื่อม | ต่อlitre/pickup;ต้องมีfuelpropertybasisที่เข้ากัน/รายงานวัดต้นทาง/CH4,N2O,PMfraction/biogenic-fossil |
| 5 | ของเสีย/น้ำเสีย | เก็บoutputsแล้ว;ยังไม่ครบtreatmentinventory | TreatedPOMEไม่ใช่rawPOME;ไม่ต่อเครื่องบำบัดซ้ำ;ต้องแยกการไหลภายในและการรั่วจริง |
| 6 | backgroundไทยและสิทธิ | ยังไม่ครบ | actualexchangesของไฟฟ้า/สารเคมี/เชื้อเพลิงขนส่ง;TGOCO2eไม่แทนLCI;ThaiLCIportalพักตามผู้ใช้ |
| 7 | รวมelementaryinventoryและทวนสอบ | ยังไม่พร้อม | ต้องปิดด้านบนแล้วตรวจelementarymapping,allocation,sum/unit,duplicates,exclusions/uncertainty/rights |

ไม่มีขั้นใดรอคำอนุมัติMTEC แต่ข้อมูลที่ยังไม่มีไม่สามารถสร้างแทนการวัดได้

## ชิ้นงานที่สร้างและตรวจแล้ว

`python -m scripts.build_thai_fame_activity_chain`

สร้างbuild/thai-fame-activity-chain/scenarios.json มี6กรณี กรณีละ55sourcepayloads:FFB19,CPO2019จำนวน15,RBDPO11,FAME10 แยกCPO2020เดิมและH-FAMEออกจากกรณีใหม่นี้ แต่ไม่ลบจากทะเบียนต้นฉบับ เก็บsourcefieldsเดิมครบและscaled_amountแยกจากค่าต้นฉบับ แถวLandseedingขาดหน่วยยังHOLDและscaled_amount=null

baselineMill1มีปริมาณกายภาพ:

- RBDPO24.6kgตามTable4ปี2020
- CPO=24.6×1100/1000=27.06kgตามTable3
- FFB=27.06×6930/1000=187.5258kgจากMill1TableS2ปี2019

สมการเหล่านี้เป็นการปรับกิจกรรมเพื่อแสดงphysicaldemand ไม่ใช่การพิสูจน์ว่าenvironmentalburdenควรรับทั้งหมดหรือคูณallocationซ้ำ และไม่ใช่สมดุลมวล/พลังงานครบทุกsubprocess

เก็บ3physical_transfer_candidatesโดยผูกprovideroutputIDและconsumerinputID ตรวจsuppliedkg=consumedkgทุกกรณี แต่burden_link_applied=false เพราะprovidercompatibilityยังไม่ผ่าน

## ขนส่งขาที่เริ่มเติม

ต้นฉบับ2019Section2.2.2 PDF3/printed67บอกระยะสวนถึงโรงสกัด **ประมาณ5km** ตรวจpypdf+pdfplumberเฉพาะคอลัมน์ขวาและภาพtmp/pdfs/thai-palm2019-page3.pngแล้ว ไม่ระบุoneway/roundtripหรือรถที่ผูกกับMill1โดยตรง

จึงเปิดเผยสมมติฐานทดลองใช้ระยะนี้หนึ่งครั้งกับขาบรรทุก:187.5258kg/1000×5km=0.937629tkm ไม่มีemissionfactorหรือemptyreturnค่า0 ขาอื่นCPO→refinery,RBDPO→FAME,FAME→userยังnull ไม่ขยาย5kmไปทุกขา และต้องตรวจว่าขนส่งนี้ไม่ได้รวมอยู่ในกิจกรรมดีเซลของสวนก่อนคิดภาระจริง

## ทวนสอบ

`python -m unittest tests.test_thai_fame_activity_chain tests.test_mill_inventory_scaling tests.test_lifecycle_model` ผ่าน16tests รวม4testsของchainใหม่ ตรวจทั้ง6กรณี/55sourcefields,transferbalances,missing-unitHOLD,ผิดหน่วย/ฐาน/โรงงานสมมติ,transportnullและไม่สร้างCO2e ตรวจJSONroundtripครบทุกfieldและhashraw2020ทั้งPDF/DOMกับraw2019

หลักฐานevidence/thai-fame-activity-chain.json ไม่มีการเปลี่ยนproduction/API/เว็บ/สิทธิ ข้อมูลraw2019ยังprivateNOT_CLEARED และCO2e_total=nullทุกกรณี

## ผลตรวจallocationจากต้นฉบับ

PDF2020หน้า4กล่าวถึงeconomicallocation;หน้า5ระบุCPO92/kernel6/shell2%;หน้า7ระบุFAME70/glycerine30% แต่ข้อความที่ตรวจยังไม่บอกชัดว่าตัวเลขทุกช่องTable1–4เป็นgrossphysicalinventoryหรือallocatedinventory ไม่อ้างว่าแก้ประเด็นนี้แล้ว และไม่เอาCPO92%จาก9millsปี2020ไปใช้กับMill1ปี2019โดยอัตโนมัติ

การค้นรายงานARDA2017ตามreference18พบชื่อโครงการในข่าวJGSEE แต่ยังไม่ได้calculationfilesฉบับต้นทาง URLebookARDAที่ค้นพบเปิดไม่ได้ จึงไม่ใช้title/snippetเป็นหลักฐานcalculationbasis ขั้นต่อไปต้องหาต้นฉบับตรงโครงการ/compatibletransport-useproviders ไม่วนURLเดิมโดยไม่มีหลักฐานใหม่

ตรวจข้อความส่วนใหม่ของรายงานNSTDA2021ที่เก็บไว้ PDF30–31/Table2 พบคอลัมน์Heatingvalueของเชื้อเพลิงผสมB7/B10/B20 ส่วนB100FAMEอยู่ในส่วนenergycarrierpathway ไม่ใช่ค่าheatingvalueรายB100ที่แยกไว้ จึงไม่หยิบค่าในแถวblendมาใช้แปลงusephaseของB100 งานนี้เป็นtextscreenใหม่ ไม่ได้อ้างvisual/allcellverificationของTable2 และไม่มีการรับตัวเลขใหม่จากตารางนี้
