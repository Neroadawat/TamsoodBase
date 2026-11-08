# ได้ต้นฉบับ GSP ไทยและตรวจตาราง — 4 พฤศจิกายน 2569

## การเข้าถึงใหม่ที่แก้ข้อค้างเดิม

DOI10.58837/CHULA.THE.2007.2079 redirectไป https://digiverse.chula.ac.th/Info/item/dc:78111 หน้าสาธารณะระบุshow_download=true/isLogin=false และใช้publicBiblio/detailData/78111 ได้fileIDsจริง จึงดาวน์โหลดผ่านปุ่ม/APIที่เว็บไซต์เผยแพร่ ไม่เดาfileIDหรือbypassauthentication

ได้chapter3(method)7หน้า,chapter4(results)17หน้า,back20หน้า เก็บprivatehash/manifest ไม่เผยraw ภาคผนวกมีrawinputs/air/water/วิธีคำนวณ เป็นsourceสำหรับgas-separationdomainที่อ่านต่อได้จริงจากที่เดิมมีเพียงabstract

## ขอบเขตและการตรวจ

อ่านภาพchapter3 PDF1/print24,PDF4/print27 และchapter4 PDF1/print31:gate-to-gateGSP1/2/3ของPTTมาบตาพุดระยอง FU1kgของแต่ละproduct/massallocation จึงไม่ถือเป็นextraction→useครบวงจร ไม่กำหนดyearmeasurementจากpublication2007

ทุกchapterเป็นscanไม่มีtextlayer ตัวpypdfอ่านตัวเลขไม่ได้ จึงrenderภาพแล้วถอดTables4.1/4.2/4.3แบบmanualvisualครบ42cells(14ต่อโรง) บันทึกrawvalue/scientificnotation/unit/direction/compartment/page/hash แยก41numericกับ1dash ไม่อ้างtwoextractorOCRหรือindependentreview

มีenergyinput,rawgasinput,airNOx/CO2/CO/SOx/H2SและwaterSS/TDS/Oils/BOD/CODไม่รวมsubtotalsเป็นflowซ้ำ ต้นฉบับheadersใช้mgสำหรับemissions จึงรักษาmgไม่เปลี่ยนเป็นkgจากการเดา ชุดนี้เป็นgas-separationreviewแยกจากFAME/องค์กร/SPRC

## Source issues ที่พบจริง

- GSP3CO2ตาราง4.3=6.26E+04mg แต่ตาราง4.4=6.3E+04mg รักษารายละเอียด62600และสรุป63000แยกเป็นprecisiondifference ไม่แก้ให้ตรงเอง
- GSP3EGATelectricityเป็นdashในตาราง4.3/4.4 แม้narrativeบอกใช้in-house จึงคงNULL/HOLD ไม่auto0
- GSP1capacitychapter3=390แต่chapter4=350MMSCFD คงunresolved ไม่ใช้scaleใดๆ
- wateremissionsแหล่งรวมหลายโรงและจัดสรรตามcapacityก่อนmassallocationตามmethod ไม่อ้างเป็นdirectmeasurementของแต่ละGSPทุกflow
- Table4.4มีCO2แตกแหล่งเป็นg ต้องไม่บวกกับCO2รวมmgจากTables4.1–4.3ซ้ำ
- ไม่มีCH4fugitivesครบ/ส่งก๊าซ/การใช้ปลายทาง/completewastetreatment/backgroundorigin จึงไม่ผ่านfullLCI

## ชิ้นงาน

- scripts/build_thai_gsp_review.pyตรวจchapterPDFhash+transcriptionhash/typeddecimal/42uniqueIDs/roundtripทุกfield
- build/thai-gsp-review/review.jsonและevidence/thai-gsp-review.json
- tests/test_thai_gsp_review.pyตรวจหน่วย/scientificnotation/detailed-vs-summary/dash/scope/provenance3ข้อผ่าน

สิทธิยังNOT_CLEARED/CCBY-NC-ND4.0ที่landingระบุยังต้องreviewการนำข้อมูลมาเผยแพร่ ไม่ขึ้นpublicwebหรือclaimcertification ไม่applyallocationซ้ำ ไม่ใช้generic1kgproductแทนmethaneเฉพาะตัวก่อนproductmapping

งานต่อที่มีหลักฐานจริง:ตรวจrawgascomposition/volumeconditionsในappendicesกับวิธีคำนวณ และหาข้อมูลส่งก๊าซ/ใช้ปลายทางไทยที่เชื่อมreferenceproductได้ ส่วนโมเดลFAMEเดิมยังรักษาข้อค้างT97 ไม่ประกาศว่าfullLCIจากการมีตารางเพิ่ม
