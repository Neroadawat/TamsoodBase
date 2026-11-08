# ข้อมูลไทยเท่านั้น และวิธีคำนวณคาร์บอน

คำสั่งผู้ใช้ 3 พฤศจิกายน 2569 supersedes ทางเลือกใช้ foreign surrogate ในรายงานค้นคว้าก่อนหน้า ไม่ใช้ ecoinvent/USLCI หรือกรณีMexicoเติม candidate นี้ การเผยแพร่โดยหน่วยงานไทยไม่เพียงพอ ต้องตรวจว่ากิจกรรม/ค่าแทนกระบวนการไทยจริง ค่าของไทยอาจใช้ระเบียบวิธี IPCC ได้ แต่ค่า default ต่างประเทศที่หน่วยงานไทยนำมาเผยแพร่ยังไม่ผ่านข้อจำกัดนี้

## แหล่งที่ตรวจพบจริง

TGO Emission Factor CFP แถว307: ไบโอดีเซล ค่าเฉลี่ยประเทศไทย, 1.0372 ต่อkg, แหล่ง Thai National LCI Database TIIS-MTEC-NSTDA with TGOelectricity2022–2024, Update_April2026, LCIA method IPCC2013GWP100aV1.03

URL: https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9

เก็บHTMLsnapshot/private/hash และ exact7cells ของแถวนี้ ตรวจเทียบwebreaderกับHTTPparserตรงกัน ค่านี้เป็น characterized EF ไม่ใช่ full elementary-flow inventory ไม่ยืนยัน provenance ของbackgroundทุกinputจากแถวสรุป และยังไม่ยืนยันboundaryสำหรับรวมทั้งวงจร ไม่มีrawredistribution/licencepromotion

TGO CFO มีBiodieselหลายแถวตามชนิดการเผาไหม้และอ้างIPCCdefaults จึงไม่หยิบมาเป็นThai-onlyvehiclefactorโดยอัตโนมัติ ไม่เอาstationaryfactorแทนpickuptruck และไม่รวมbiogenicCO2เหมือนfossilโดยไม่อ่านวิธีรายงาน

## สูตรสองแบบที่ต้องแยก

1. **เมื่อมี EF ที่แสดง kgCO2e ต่อหน่วยกิจกรรมแล้ว:** ผลkgCO2e = activity × EF ใช้หน่วยตรงกัน ห้ามคูณGWPซ้ำ ปริมาณkgห้ามใช้กับEFต่อlitreโดยไม่มีdensityที่เข้ากัน
2. **เมื่อมีมวลก๊าซจากLCI:** ผลkgCO2e = sum(mass_gas_kg × GWP_gas_method_version) บันทึกCO2/CH4/N2Oและbiogenic/fossilแยกก่อนเลือกวิธีcharacterization NOx/PM/COไม่ใช่การเอาทุกสารมาคูณGWPเดียวกัน

CO2kg คือมวลก๊าซคาร์บอนไดออกไซด์ ส่วนCO2eคือผลกระทบจากหลายก๊าซเทียบCO2 จึงไม่แปลงกลับจากEF_CO2eไปเป็นมวลCO2จริง

## เครื่องมือที่ทำแล้ว

`python -m scripts.screen_thai_carbon --kg 1000`

ใช้exactdecimalคำนวณตัวอย่างกิจกรรมผู้ใช้กรอก1000kg × 1.0372 =1037.2000kgCO2e ผลเป็น **SCOPED_FACTOR_SCREENING** ของEFแถวนี้เท่านั้น ไม่ใช่ผลปล่อยจริงจากโรงงาน/ทั้งวงจรของเรา กิจกรรม1000kgเป็นตัวอย่างที่กรอก ไม่ใช่measurementใหม่ คำสั่งสร้างbuild/thai-carbon-screening/result.jsonและevidence/thai-carbon-factor-review.json ไม่ขึ้นproduction

เพิ่มtests3ข้อผ่าน ตรวจเลขจริง/หน่วย/NaN/ค่าลบ/foreigngeography/Thai-publisher-with-default rejection;รันร่วมlifecycle4ข้อรวม7ผ่าน ไม่ได้รันfullsuiteหรืออ้างว่าทดสอบเว็บแล้ว

## ก่อนรวมค่าแต่ละช่วง

- เลือกเส้นทางเดียว: **aggregateEFของไบโอดีเซล** หรือ **bottom-upตั้งแต่FFB→CPO→RBDPO→FAME** สำหรับขอบเขตเดียวกัน ไม่บวกสองทางนี้ทับกัน
- aggregateEFอาจรวมupstreamหลายขั้น ต้องขอ/อ่านdatasetboundaryก่อนบวกCPO/electricity/transport/treatment;ไม่เดาว่ารวมอะไรจากชื่อสั้น
- ขนส่งคำนวณactivitykg/1000×kmเป็นt·kmเฉพาะproviderที่ใช้หน่วยนี้ ระบุload/emptyreturnและป้องกันบวกdieselซ้ำถ้าproviderรวมไว้แล้ว
- allocationใช้เมื่อbasisชัดและยังไม่ถูกapply;เก็บmethod/versionและผลต่อreferenceflow ไม่คูณallocationซ้ำกับfactorที่allocatedแล้ว
- กำหนดFU: fuel-energy1000MJตามstudy แยกจากผลิตภัณฑ์mass1000kg;ต้องมีLHVไทยที่ตรงเชื้อเพลิงก่อนconvert ห้ามเอาตัวอย่าง1000kgไปแสดงเป็น1000MJ
- ที่มาของแต่ละinputต้องตรวจTHจริงหรือยังUNKNOWN_TH_PROVENANCE ไม่ถือว่าpaperไทยทำให้backgroundecoinventกลายเป็นThai-only

ข้อค้าง: actualThaiLCIexchangefiles/rights, Thaiusephasefactorที่ตรงรถ/FAME, distributionactivity, treatmentinventory และbasis/allocation ยังไม่ปิด ไม่มีผลfull-lifecyclecarbonหรือCFPcertification
