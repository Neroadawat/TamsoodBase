# คัดแหล่งตรง Petroleum, Natural Gas & Fuels — 4 พฤศจิกายน 2569

คำสั่งล่าสุดให้ยึดโดเมนโครงการและตรวจความเกี่ยวข้องก่อนพัฒนาต่อ เงื่อนไขข้อมูลไทยยังใช้เดิม

## บทบาทข้อมูล

- **หลัก:** การผลิต/แยกก๊าซ การกลั่นและผลิตภัณฑ์น้ำมัน การผลิตเชื้อเพลิงชีวภาพ และการใช้เชื้อเพลิงที่ระบุผลิตภัณฑ์ชัด
- **สนับสนุนเมื่อเชื่อมได้:** ขนส่งเชื้อเพลิง ไฟฟ้า น้ำ สารเคมี และบำบัดของเสียจากกระบวนการเชื้อเพลิง เช่น POMEสำหรับpalmFAME ต้องมีปริมาณและproviderlinkก่อนใช้ ไม่ขยายเป็นโครงงานเกษตร/บำบัดทั่วไป
- **บริบท:** NSO/EPPO/DMFและข้อมูลบริษัท ยังไม่เปลี่ยนเป็นproductLCIโดยอาศัยยอดสถิติหรือขอบเขตองค์กร

## งานใหม่ที่ทำจริง

สร้างbuild/domain-factor-review/review.jsonจากHTMLTGOที่เก็บ3พ.ย. ไม่อ้างว่าเป็นsnapshotสด4พ.ย. รักษา7cellsของ16แถวคือ28–42และ307 sourcehash/versionApril2026ตามต้นทาง เป็นcharacterizedproductEF referenceเท่านั้น ไม่เพิ่มacceptedLCIหรือapplyในfullmodel

แบ่งprocessfamilies GAS_SEPARATION/REFINING/FUEL_SUPPLY_MIX/BIOFUEL แยกLPGจากgas separation(row32)และrefinery(row37);natural-gasmixkg(row33)กับm3(row34)คงidentity/unitแยก ไม่ใช้ย้อนderivegasdensity

row33/34/35เป็นmixturesที่ข้อความระบุimport จึงHOLD_EXPLICIT_IMPORTED_MIX สำหรับstrictThai-only ส่วนแถวอื่นยังstrict_all_inputs_thai_verified=falseเพราะThaiNationalLCIlabelไม่แปลว่าupstreamทุกตัวมาจากไทย

row28“ก๊าซคาร์บอนไดออกไซด์”เป็นผลิตภัณฑ์จากgas separation ค่าfactorใช้ประเมินการจัดหาผลิตภัณฑ์CO2 ไม่ใช่มวลCO2ที่โรงงานปล่อยและไม่ใช่GWPของCO2 ต้องแยกrole PRODUCT_SUPPLYจากelementaryemission

scripts/build_domain_factor_review.pyตรวจsourcehash/แถวไม่ซ้ำ/amount/unit/version/source/method;tests3ข้อผ่าน LPGprocessidentity/importholds/productCO2role NoEC2/webdeploy/rightschange

## แหล่งใหม่ในโดเมนที่อ่านต้นทางแล้ว

1. **Environmental and energy assessment of natural gas production in Thailand using LCA technique**, Charoen Lappitakpong,2007, DOI10.58837/CHULA.THE.2007.2079
   https://digital.car.chula.ac.th/chulaetd/37899/
   หน้ามหาวิทยาลัยระบุinventoryinputs/outputsของPTT GSP1/2/3มาบตาพุดระยอง จึงตรงgas-separationdomain แต่เป็น3โรงแยก ไม่ใช่extraction→transmission→useครบวงจร ปี2007ต้องเก็บtechnology/timecontext ไม่แทนค่าเฉลี่ยปัจจุบัน หน้าระบุCCBY-NC-ND4.0;fulltextDOIอ่านผ่านwebtoolไม่สำเร็จ/HTTPdownloadlanding403 จึงยังไม่importnumericหรืออ้างLCIfilesavailable
2. **Thai national life cycle inventory readiness for product environmental footprint**, Poolsawad etal.,online2016/volume2017, DOI10.1007/s11367-016-1257-8
   https://link.springer.com/article/10.1007/s11367-016-1257-8
   อ่านSections4.1–4.2กรณีdieselmixatrefinery1kg/50ppmsulfur มีการทบทวนrepresentativenessและuntreatedwaste ชี้ว่าควรมีwasteflow→treatmentก่อนคิดimpact แต่caseใช้foreigncrudeoilbackground จึงใช้เป็นmethodologicalevidenceไม่รับเป็นstrictThai-onlynumericmodel ไม่อ้างคุณภาพทั้งหมดของระบบเราจากDQRของบทความ และไม่ใช้สัดส่วนนำเข้าในอดีตเป็นสถิติปัจจุบัน
3. **Spatially differentiated LCA of Thailand's transport**, DOI10.1016/j.spc.2025.04.023
   https://doi.org/10.1016/j.spc.2025.04.023
   ข้อความจากpublisherระบุThaiTTWforegroundแต่fossilWTTtakenfromecoinvent3.8 จึงไม่รับทั้งชุดภายใต้Thai-only fulltextreader403 ไม่รับตารางจากsearchsnippet

## ลำดับต่อที่ตรงโดเมน

1. actualgas-separation/refinerydatasetหรือfulltextที่มีreferenceproduct/exchanges/units/period/allocation
2. Thai-onlytransport/usecandidateที่ตรงfuelroute;ตรวจboundaryของTGOproductfactorsแยกจากbottom-upLCI
3. ThaiFAMEยังเป็นselectedfuelcaseได้ แต่ขนส่ง/POMEเป็นsupportingprocessเฉพาะเมื่อlinkได้ ไม่ย้ายขอบเขตหลักไปเรื่องปาล์มทั่วไป

ยังไม่มีfullLCIclaim ข้อมูลimportmixedยังholdและrightsNOT_CLEAREDคงเดิม
