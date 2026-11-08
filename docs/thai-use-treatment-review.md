# ตรวจข้อมูลการใช้และการบำบัดไทยเพิ่มเติม — 3 พฤศจิกายน 2569

ดำเนิน T97 ต่อด้วยข้อมูลจริง แยกชุด2013จาก2020 ไม่อ้างว่าครบวงจรแล้ว

## งานที่ทำและตรวจแล้ว

สร้าง scripts/review_thai_use_treatment.py ตรวจhashPDF2013ที่เก็บprivate และอ่านหน้าPDF48/print36ด้วยpypdf+pdfplumber เทียบgas/amount/unit4รายการ:CO2,CO,NOx,PMตามต้นฉบับ มีฐาน1litrebiodieselและบริบทpick-up/LDDVในไทย แหล่งอ้างการทดสอบPleanjai2008ซึ่งยังไม่ได้อ่านโดยตรง จึงติดSECONDARY_REPORTED_THAI_TEST ไม่อ้างเป็นmeasurementของเรา/ค่าเฉลี่ยไทยปัจจุบัน ปีวัดnull

ข้อมูลอยู่ในbuild/thai-use-treatment-review/review.json;sourceURL/hash/page/unitเดิมและamountkgที่คำนวณแสดงคู่กัน ไม่mapPMเป็นPM2.5/PM10เพราะไม่ทราบsizefraction ไม่mapglobalflowก่อนsemanticreview

CO2รวม2.78kg/litreกับreportedfossilsubset0.15kg/litreเป็นคนละบทบาท 0.15เป็นส่วนย่อย ไม่สร้างemissionflowเพิ่ม และยังไม่มีCH4/N2Oครบ จึงไม่ใช้4รายการนี้รับรองผลGHGรวม

ตรวจTable2.1 PDF47/print35 เป็น4qualitativescenarios:baselineEFBdump/openpond;S1EFBdump/biogasrecovery;S2cocompost/openpond;S3cocompost/biogasrecovery ตรวจความสัมพันธ์แต่ละrowกับสองextractors ไม่สร้างemissionquantityจากชื่อscenario ไม่มีtreatmenttotal

แก้การextractsubscriptCO2/NOxที่pdfplumberวางglyphไว้บรรทัดถัดไปแบบexactsentenceที่ตรวจภาพแล้ว ไม่ใช้กฎเดาชื่อก๊าซทั่วไป เพิ่มpdfplumberในrequirements-report.txt;tests3ข้อใหม่ตรวจunitnormalization/subsetdoublecount/scope/rights

## ความพยายามหาขนส่งรอบนี้

พบrepositoryใหม่ของบทความ Full chain energy analysis of biodiesel production from palm oil in Thailand (2009) แต่HTTPScertificateหมดอายุและwebreaderโหลดไม่สำเร็จ ไม่ปิดcertificateverification ไม่รับระยะทาง/โหลดจากsearchsnippet จึงยังไม่มีquantitativetransportที่ผ่านเกณฑ์รอบนี้

## ข้อค้างที่ไม่เติมเอง

- usephase1litreยังไม่เชื่อม1000MJของ2020เพราะLHV/density/technology/basiscompatibilityยังไม่verified
- transportขาและdistribution;CH4/N2Ouse;quantifiedtreatments;upstreamallocation/basis/provider/backgroundoriginไทยยังไม่ครบ
- 2013sourceสิทธิredistributionยังNOT_CLEARED จึงไม่เปิด4observationsใหม่นี้บนpublicweb
- candidateนี้เพิ่มหลักฐานการใช้/สถานการณ์บำบัด ไม่เพิ่มproductioninventory52เดิม และไม่ใช้ปิดfullLCIstatus
