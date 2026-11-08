# ตรวจระบบก่อนพัฒนาต่อ — 3 พฤศจิกายน 2569

ตรวจ code/data contracts ของ lifecycle และ carbon screening ใหม่ พร้อม full unit suite และ release consistency ไม่ได้อ้างเป็น external scientific review หรือรับรองทุกข้อมูลจากการวัดอิสระ

## ข้อผิดพลาดที่พบและแก้

1. selected-row.json เดิมเช็คค่าหลักบางช่อง แต่ไม่ผูกทุกช่องกับ HTML ต้นฉบับ: เพิ่ม parser ตรวจ exact7cells กับsource snapshotที่hashตรง และnegative testเปลี่ยนแต่ละช่องต้องถูกปฏิเสธ
2. stage observations เดิมตรวจซ้ำแต่ไม่ตรวจ unknown/omitted IDs: เพิ่มตรวจทุกIDกับsourcepayloadและต้องอยู่ในstageครบ ไม่รับincluded observationsในMISSING/EXCLUDED stage
3. Thai-reported factorไม่เท่ากับall-inputsThaiverified: ผลscreeningแสดงสองสถานะแยกและคงstrict_all_inputs_thai_verified=false ห้ามใช้ปิดThai-onlyfullmodelgate
4. Decimal defaultprecisionอาจปัดเศษกิจกรรมตัวเลขยาว: เพิ่มboundedplain-decimalinput/precisionเพียงพอพร้อมtestexactmultiplication ปฏิเสธexponentialnotationขนาดไม่จำกัด
5. source_measured_completeเดิมอาจถูกเปิดบนmodelที่ยังไม่ready: เพิ่มrequirementพร้อมจริงและไม่มีassumption;all-excludedemptyไม่เป็นready

## ผลที่ตรวจได้

- Full suite173testsผ่าน ไม่มีfail
- releaseconsistency25checksผ่าน
- FAMEcandidate52sourcepayloadคงเดิม;3stagesยังMISSING;6scientificgatesยังunresolved
- carbon1000kgเป็นuser-enteredscenarioเท่านั้น ผล1037.2000kgCO2eเฉพาะfactorไม่ใช่1000MJ/wholelifecycle/directCO2
- ไม่reextractsourceเดิม/ไม่deploy/ไม่แตะEC2production/ไม่เปลี่ยนrights

## งานต่อที่ทำแล้ว

สร้างdocs/thai-source-acquisition.jsonจำแนกหลักฐานจริงของแหล่งไทย/แหล่งที่ยังไม่มีfile/Thai-onlyข้อจำกัด ไม่เอาecoinvent/USLCI/Mexicoมาอุดช่องว่างของcandidateนี้ แต่ยังรักษาข้อมูลปี2020เดิมเป็นsourceobservations ไม่ลบเพราะbackgroundoriginยังไม่ครบ

ข้อค้างวิทยาศาสตร์ยังallocation/referenceflow/provider/background/elementarymapping/doublecount;ขนส่ง/use/treatmentต้องได้Thaiinventoryที่เข้ากันก่อน จึงไม่อ้างfullLCIจากการผ่านsoftwaretests
