# แหล่งเปิดทดแทน: โรงสกัดปาล์มไทย6แห่ง ปี2019

ตรวจ4พฤศจิกายน2569 หลังผู้ใช้ให้พักThaiNationalLCIเนื่องจากลงทะเบียนไม่ได้

## ต้นฉบับที่ได้จริง

Huailuek, Silalertruksa and Gheewala. **Life cycle assessment and cost-benefit analysis of palm biorefinery in Thailand for different empty fruit bunch (EFB) management scenarios**. Journal of Sustainable Energy & Environment10(2019),65–73.

[PDFจากผู้พิมพ์ รวม Supporting Information](https://www.jseejournal.com/media/219/attachment/Life%20cycle%20assessment%20pp.%2065-73.pdf) ดาวน์โหลดสำเร็จโดยTLSปกติ ไม่ต้องล็อกอิน มี13หน้า ไม่ใช่9หน้าเพราะมีเอกสารประกอบท้ายบทความ เก็บprivatePDF/hashที่data/raw/thai-palm-jsee-2019 สิทธิแจกจ่ายยังNOT_CLEARED ไม่เผยแพร่raw

Section2.1รายงานโรงสกัด6แห่ง:4แห่งกระบี่,1สุราษฎร์ธานี,1ชลบุรี ตารางไม่ได้จับคู่Mill1–6กับจังหวัดทีละแห่ง จึงไม่เดาจังหวัดรายMill ช่วงปีที่วัดไม่ได้ยืนยันจากTableS2 ไม่ใช้ปีตีพิมพ์2019แทนปีวัด

## ช่องว่างที่ช่วยเติม

**TableS2, PDFหน้า11** มี15แถว×6โรงงาน=90ช่องตัวเลข บนฐานCPO1000kgรายโรงงาน ได้แก่FFB,kaolin,water,grid/boiler/biogas electricity,steam,CPO,kernel,EFB,fiber,shell,decantercake,treatedPOME,electricityoutput

ปริมาณFFB/CPOที่คำนวณจากฐานเดียวกันในแต่ละคอลัมน์คือ6.93,6.29,5.95,5.94,6.10,5.65kg/kg ตามMill1–6 **เป็นค่าของแต่ละโรงงานในแหล่งนี้ ไม่ใช่ค่าเฉลี่ยไทยหรือคำยืนยันค่าที่ขาดในชุด2020**

TreatedPOME2.8–4.9m3/1000kgCPOเป็นน้ำเสียที่บำบัดแล้วตามชื่อแถว ไม่แทนPOMEก่อนบำบัดหรือการปล่อยมลสารสู่น้ำ Electricityoutputยังรักษาชื่อแถวเดิม ไม่ยกระดับเป็นnetexportที่พร้อมให้เครดิตอัตโนมัติ

Section2.2.2ยังมีระยะทางสวนถึงโรงสกัดประมาณ5km ส่วนbaselineSection2.3.1มีEFBกลับสวนประมาณ5km เป็นประมาณการตามขอบเขตงานนี้ ยังไม่รับเป็นระยะจริงของเส้นทางFAME2020หรือใช้ปิดทั้งdistribution

## ตรวจอย่างไร

- ตรวจhashก่อนอ่าน; pypdfและpdfplumberสกัดครบ90ช่องตรงกันทั้งหมด
- เทียบกับภาพเต็มPDFหน้า11และtranscriptionในสคริปต์ครบทุกช่อง รักษาชื่อแถว หน่วย และคอลัมน์รายMill
- รักษา0ที่ต้นฉบับรายงาน7ช่อง ไม่ได้เติมmissingเป็น0
- เก็บ90รายการพร้อมsourcehash/table/page/row/column/referencebasis และตรวจJSONroundtripทุกfield
- `python -m scripts.review_thai_mill_2019`
- `python -m unittest tests.test_thai_mill_2019 tests.test_thai_pome_benchmark` ผ่าน6tests รวม3testsใหม่

ผลที่build/thai-mill-2019-review/review.json และevidence/thai-mill-2019-review.json ตรวจโดยAI-assisted single review ไม่อ้างindependent double review

## สิ่งที่ต้องระวังก่อนประกอบโมเดล

1. เป็นalternative foregroundของCPO ไม่ใช่full lifecycle FAME และยังไม่เชื่อมกับ2020 ต้องเลือกsystem/modelversionและพิสูจน์compatibilityก่อน
2. เก็บโรงงานแยกกัน ไม่เฉลี่ยแบบไม่ถ่วงน้ำหนัก และไม่เลือกค่าต่ำสุดจากแต่ละโรงงานมาประกอบเป็นโรงงานสมมติ
3. พลังงานboiler/biogas/steamเป็นการไหลภายในที่ต้องรักษาขอบเขต ไม่เติมupstreamproviderและemissionsซ้ำ
4. ตัวบทใช้system expansion/substitutionสำหรับเปรียบเทียบscenario ขณะที่ชุด2020กล่าวถึงeconomicallocation ห้ามนำเครดิตของบทนี้ไปหักซ้ำจากflowที่allocatedแล้ว
5. Section2.1/Table1ระบุforeignbackground/defaults(Ecoinvent,EEA,IPCC,NREL) และบางscenarioอ้างข้อมูลต่างประเทศ จึงรับเฉพาะforegroundที่แหล่งระบุเก็บจากโรงงานไทย ไม่อ้างว่าทั้งโมเดลไทยล้วน ตารางS1/S3เป็นผลLCIA ไม่รับเป็นelementaryLCI
6. TableS2ยังไม่ให้air/water elementary emissionsครบ,gasleakage,ต้นทางprovidersและการใช้FAME จึงยังปิดT97ไม่ได้

## ขั้นถัดไป

ใช้แหล่งนี้เป็นทางเลือกCPOที่มีFFBและtreatedwaterbasisชัดเจน แล้วหาชุดconversion/use/transportที่เข้ากันก่อนเลือกเส้นทางทั้งระบบ ส่วนThaiNationalLCIพักเพราะฟอร์ม/APIขัดข้อง ไม่ขอให้ผู้ใช้สมัครซ้ำโดยไม่มีการแก้จากเจ้าของเว็บ ไม่มีการdeploy/APIchangeในรอบนี้
