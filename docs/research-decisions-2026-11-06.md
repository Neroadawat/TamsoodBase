# Research-led team decisions — 6 November 2026

ผู้ใช้ย้ำให้ทีมค้นและพิจารณาเอง ไม่รอ MTEC approval. ใช้ AUTOMATED_TEAM_METHOD_REVIEW_V1 AI-assisted actor ไม่สร้างชื่อhumanreviewer. การตัดสินใจเชิงวิธีวิจัยไม่ใช่สิทธิแจกจ่ายหรือการรับรองผล.

## ผลที่ทำจริง
แหล่งใหม่: Palasai et al.(2021), Performance and Gaseous Emission Evaluation of Compression Ignition Engine using Palm Biodiesel Blend on Chassis Dynamometer, PNU Journal13(3)276–293. หน้าเว็บ https://li01.tci-thaijo.org/index.php/pnujr/article/view/251608 ;ดาวน์โหลดPDFต้นฉบับ626677bytes/hash48a24204f83b02415115ff28a4e727c0b4b17ec8ce1a889ee84848c908973496 เก็บprivate.

ตรวจB100rowครบ9selectedcells Tables1–2 PDF9/printed284 ด้วยpdfplumber+pypdfและภาพ. Density862.79kg/m3,LHV39.89แต่หน่วยหัวตารางพิมพ์เพียงMj;คงต้นฉบับไม่เติม/kgให้เป็นsourcefact. CO2reportedเป็นconcentrationและไม่มีexhaustflow จึงไม่แปลงเป็นkg/MJ;NOxไม่ใช่N2O. Nissan2663ccIDI/PNUfuelเป็นspecifictest ไม่ใช่nationalfleet. Publication2021ไม่เท่ากับmeasurementyear.

## ทีมตัดสินใจและลงมือแล้ว
1. รับเป็นThai fuel-property research candidateภายใน ไม่รอMTEC. ยังไม่ผูกเป็นfuelbatchเดียวกับmodel2020หรือThailandaverage.
2. สร้างconditional sensitivity branchโดยระบุสมมติฐาน LHV=39.89MJ/kgชัดเจนก่อนคำนวณ ไม่แก้หน่วยต้นฉบับ. ใช้1000MJและdensityตามtable:25.06894kg/29.05567litresโดยประมาณ. ไม่ใช่ตัวแทน26.3kgของbaselineเดิมและไม่ใช่CO2e.
3. ถ้าไม่มีassumptionID/explicitflag โค้ดต้องปฏิเสธconversion;positivefinitechecks/energyreplayผ่าน3tests. รายละเอียด build/thai-b100-properties-2021/conditional-scenario.json ไม่ส่งpublicเพราะrightsNOT_CLEARED.
4. ไม่ตีความcarbon78.332%เป็นbiogenicทั้งหมดหรือemissionfactorอัตโนมัติ. ต้องแยกcompleteoxidationassumption/methanolfossilcarbon/CH4N2Oก่อนimpact.

## เส้นทางทำงานต่อโดยไม่รออนุมัติภายนอก
- ใช้propertyscenarioนี้ทดสอบความไวของฐานkg/litre/MJแยกจากbaseline;รักษาสมมติฐานและsourcehash.
- ตรวจThaienginepaperที่มีทั้งfuelproperties+fuelconsumption+exhaustmassflow/CH4N2Oก่อนเชื่อมemissioninventory;ไม่เดาปริมาณจากกราฟvol%หรือppm.
- Allocationตีความเป็นสมมติฐานทางเลือกได้แต่ไม่apply70/30ซ้ำกับtableที่ยังไม่รู้gross/allocatedbasis;ไม่รอMTECเพื่อเลือกทางศึกษาแต่ไม่เรียกสมมติฐานเป็นmeasurement.
- พบMDPI2021eco-efficiency/576เป็นcandidateฐาน1000MJ แต่page429และofficialPDFอ่านไม่ได้ในรอบนี้ บันทึกไม่วนretryและไม่promoteจากsnippet.

หลักฐาน: evidence/thai-b100-properties-2021.json;src/fuel_basis_scenario.py;tests/test_fuel_basis_scenario.py. Existingmodel/fullLCI/CO2eและproductionไม่เปลี่ยน. เพิ่มข้อมูลเพราะตอบfuelbasisquestion ไม่เพิ่มจำนวนacceptedLCI.
