# Thai fuel-basis and freight sensitivity — 6 November 2026

## ทีมตัดสินใจและทำจริง
เลือกทำกรณีทดลองแยกจาก baseline ไม่รอ MTEC. ใช้เฉพาะsourceThai/ThaiLCIreportedที่ตรวจได้ แต่ไม่อ้างว่าunderlyingbackgroundทุกinputผลิตในไทยทั้งหมด.

1. Fuel-basis sensitivity: baseline Table4ใช้26.3kg;conditionalPNU2021ตีความLHV39.89MJ/kgอย่างเปิดเผย→25.06893958kgต่อ1000MJ. คูณค่าอ้างอิงThaiLCIreportedTGO-CFP307 1.0372kgCO2e/kg ได้27.27836และ26.00150414kgCO2eตามลำดับ. ต่าง-4.68084% **ไม่ใช่หลักฐานลดคาร์บอน** เพราะเป็นฐานเชื้อเพลิงคนละกรณี ไม่ใช่การทดลองก่อน/หลัง. Factorboundaryยังไม่ยืนยันสำหรับรวมทั้งระบบ จึงไม่assignเป็นstageproductiontotalหรือบวกforeground.
2. Freight sensitivity:ตรวจCFProws230–233จากHTMLsnapshot/hashเดิมเฉพาะsubsetใหม่. Row230เป็นkm ห้ามใช้แทนtkm. Rows231/232/233เป็นtkmสำหรับ10ล้อ16ตันB5ที่50/75/100%loading. ใช้3ระยะสมมติ10/50/100kmเพื่อทดสอบ9combinations;ไม่อ้างว่าเป็นเส้นทางจริง. สูตรtkm=masskg/1000×distance. Loadingอยู่ในEFแล้ว ไม่หารซ้ำ. ไม่เพิ่มemptyreturnเพราะconventionยังไม่ยืนยัน และไม่รวมกับbiodieselEF.
3. Road-use research:พบThai2026DPF/B100paperDOI10.1016/j.rineng.2026.110543แต่publisherredirect/HTMLอ่านไม่ได้(403) จึงคงcandidateไม่ใช้ตัวเลขจากsnippet. MDPI2018idlepaper8/12/2665เป็นงานKoreaไม่ใช่Thaiจึงไม่ใช้. TGO-CFOstationarybiodieselไม่แทนroadB100;blankmobileCH4/N2Oไม่ใช่zero. Gasvol%/ppmจากPNUไม่ใช่kg/MJโดยไม่มีexhaustflow.

## รันซ้ำ
`python -m scripts.build_fuel_basis_sensitivity`
`python -m scripts.build_transport_sensitivity`
`python -m unittest tests.test_fuel_basis_scenario tests.test_fuel_basis_sensitivity tests.test_transport_scenario`

ผลอยู่build/fuel-basis-sensitivity/report.json และbuild/transport-sensitivity/report.json เป็นinternalreviewเพราะสิทธิแจกจ่ายยังไม่ชัด. หลักฐานevidence/fuel-basis-sensitivity.json/transport-sensitivity.json. Tests7ผ่านรวมsourceunitguard/no-doubleloading/no-auto-sum/no-fullclaim. ไม่มีfullLCI/CO2e_total/productionหรือwebdatasetเปลี่ยน.

## ตัดสินใจต่อได้โดยไม่รอภายนอก
ใช้distances/loadingsเป็นscenarioที่ผู้ใช้ปรับได้และศึกษาความไว แต่ต้องเก็บassumptionIDs/sourceversion/returnconvention. ถ้าได้Thaiusemassinventoryที่มีconditions/unitsครบจึงเปิดusebranchเพิ่ม;ไม่ย้ายscopeจากexperimentalcaseเป็นnationalaverage. กรณีทดสอบนี้เป็นการคำนวณอ้างอิงแบบแยก ไม่ใช่recreatedcompleteLCIหรือcertifiedCFP.
