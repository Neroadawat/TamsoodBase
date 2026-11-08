# ข้อเสนอเลือกข้อมูลเพื่อสร้าง LCI ครบวงจรของ FAME ไทย

วันที่ตรวจ: 3 พฤศจิกายน 2569 · งานค้นคว้า T97 · ไม่ใช่การรับรองว่าโมเดลปัจจุบันครบแล้ว

## ข้อสรุปตัดสินใจ

ใช้ **FAME จากปาล์มไทยเพียงเส้นทางเดียว** เป็นกรณีหลัก ประกอบด้วย foreground จากงานวิจัยไทยที่มี inventory จริง, background จาก Thai National LCI ที่ตรงบริบทและได้รับสิทธิ, และ use-phase inventory จากการทดสอบเชื้อเพลิง/รถที่ระบุชัด ใช้ openLCA ตรวจ linking/scaling/inventory totals แยกจากเว็บ MySQL ที่ใช้เก็บ source/version/provenance

การมี5กล่องในแผนภาพไม่ใช่เกณฑ์ครบ ควรเรียกผลสำเร็จว่า **modeled cradle-to-use/well-to-wheel inventory including specified waste treatment** ตาม scope จริง ไม่ใช้คำว่า cradle-to-graveโดยไม่มีexclusion decisions/ปลายทางที่ชัดเจน เชื้อเพลิงถูกใช้โดยเผาไหม้แล้ว ไม่สร้างขยะเชื้อเพลิงหลังใช้ซ้ำ ส่วนบรรจุภัณฑ์/น้ำเสีย/กากเป็นwaste flowsที่เชื่อมtreatmentตามจุดเกิด

## ชุดที่ควรใช้ และขอบเขตการยืนยัน

| ชั้น | เลือกใช้ | ยืนยันอะไรแล้ว | ยังขาดอะไรก่อนใช้จริง |
|---|---|---|---|
| Foregroundหลัก | DOI10.3390/su12229415 (2020), Tables1–4 ที่เราตรวจแล้ว | มี58source observations โดย FAME route52; CC BY4.0 ตามmanifestเดิม; FUstudy1000MJ | calculationbasis/FFBinput/allocation/provider/background; ไม่ถือว่าตารางเหล่านี้คือfull system |
| แบบจำลองไทยสำหรับอุดช่องว่างหรือalternative case | DOI10.1007/978-3-642-34519-7_2 (2013) | ตรวจpublisher+ภาพprint33–36แล้ว มีquantitativeflowdiagram/use emissions/EFB-POMEscenarios | figure1000MJ vsprose1MJ;allocationต่างจาก2020;transport/distributionรายละเอียด;สิทธิแสดงข้อมูล ไม่ใช้แปะปนชุด2020ทันที |
| Backgroundไทยอันดับแรก | Thai National LCI / TIIS-MTEC-NSTDA | หน้าทางการยืนยันมีinventoryและหมวดไฟฟ้า น้ำ ขนส่งรถบรรทุก ปาล์ม และrecycle/wastemanagement | ต้องได้ชื่อdatasetจริง/version/referenceflow/year/systemmodel/ชนิดunitหรือaggregated/ไฟล์exchange/สิทธิใช้งานและสิทธิpublicweb ไม่อ้างว่าdownloadได้แล้ว |
| Backgroundทางเลือกถ้าสถาบันมีสิทธิ | ecoinvent | licensingทางการแยกacademic/developer/interactive-tool sublicensing | ยังไม่มีสิทธิยืนยัน;ห้ามคัดexchangeไปpublicweb;ต้องตรวจprovidergeography/technology/version/systemmodel;ไม่ซื้อเอง |
| ทางเลือกข้อมูลเปิด | Federal LCA Commons / USLCI | คู่มือมีunitprocess/explicitlink/sourceguidanceและpublicdomain/CC0เงื่อนไขที่ต้องตรวจรายrepository | หลักๆUS/NorthAmerica จึงเป็นsurrogate/scenarioไม่ใช่ค่าไทย;ยังไม่ได้เลือกdatasetรายตัว ไม่อ้างใช้ได้ทุกหมวด |
| เครื่องมือทวนสอบ | openLCA | officialmanualมีreferenceprocess/providerlinking/process type/cutoffในการสร้างproductsystem | ยังไม่ได้import/คำนวณcandidateนี้;ต้องexportformatจริงและตรวจผล ไม่อ้างnativecompatibilityจากreviewJSON |

## ข้อมูลที่ต้องใช้ในแต่ละช่วง

1. **วัตถุดิบ:** cultivation/harvest, FFByield, fertilizer/pesticide/diesel/water, fieldemissionsและlanduseตามscope; FFBต่อCPO ต้องตรงreferencebasis ไม่ใช้ผลผลิตจังหวัดแทนprocessyield
2. **ผลิต:** CPO/refining/FAME inputs/outputs, electricity/steam/methanol/catalyst/waterproviders, coproductsและwasteflows ต้องมีหลักฐานว่าallocationทำแล้วหรือยัง แยกphysicalflowจากallocatedburden
3. **ขนส่ง/จำหน่าย:** materialmass, actual/scenariodistance, vehicle/loading/emptyreturnและprovider; transportactivity(t·km)=mass(kg)/1000×distance(km) ใช้เฉพาะเมื่อproviderนิยามtonne-kmตรงกัน หากtruckproviderรวมemptyreturnแล้วไม่คูณซ้ำ ต้องครอบFFB→mill→refinery→FAMEplant→depot/useตามขอบเขตที่เลือก
4. **ใช้งาน:** fuelquantityจากFUและLHVที่เข้ากัน, densityเมื่อจำเป็นแปลงlitre, tailpipeCO2/CH4/N2O/NOx/CO/PMตามหลักฐาน แยกfossil/biogenicCO2และelementarycompartment ชุดpollutantsที่หาได้บางตัวไม่แปลว่าครบทุกemission
5. **Treatment:** POME/COD/CH4capture/fugitiveCH4/energyrecovery, EFB/shell/fibre/cake/disposal/compostingตามscenario;no treatmentburdencreditโดยไร้allocation/substitutionmethod ช่วงนี้อาจเกิดพร้อมการผลิต ไม่ต้องรอหลังใช้เชื้อเพลิง

## คงสองทางเลือกอย่างตรงไปตรงมา

**ทางA แนะนำสำหรับโมเดลไทยใช้งานจริง:** foregroundไทย + Thai National LCIที่เข้าถึงได้ + measuredไทยuseinventory แล้วเชื่อมทั้งระบบ ตรวจสิทธิpublicwebแยกจากสิทธิใช้คำนวณ หากได้aggregatedLCIของผลิตภัณฑ์มา ต้องเลือกใช้เป็นblackboxbackgroundหรือunitprocesschain ไม่เอาaggregatedupstreamมาบวกกับupstreamที่สร้างแล้ว

**ทางB ถ้าต้องทำด้วยข้อมูลเปิดเท่านั้น:** foregroundCCBY + publicbackgroundที่licenseรองรับ + สมมติฐานที่ระบุsource/เหตุผล/range + sensitivity เทียบsurrogate อาจเป็นโมเดลครอบขอบเขตชีวิตได้ แต่ไม่ใช่fullThai measuredLCI ไม่ซ่อนgeography/technology mismatch ผลต้องติดป้ายmodeledscenarioและอาจยังปิดครบไม่ได้ถ้ามีmaterialprocessที่ไม่มีproxyเหมาะสม

การเปลี่ยนไปใช้2013ทั้งชุดอาจช่วยให้use/wasteอยู่ในเรื่องเดียวกัน แต่ไม่แก้missingbackground/rightsโดยอัตโนมัติ และไม่ควรย้ายทิ้งชุด2020ที่ตรวจแล้วจนcandidate2013ผ่านbasisgate

## เกณฑ์รับ dataset ที่ต้องใช้จริง

- referenceproduct/amount/unit;processboundary;time/geography/technology;allocation/systemmodel;version/UUID/hash/locator
- แยกtechnosphereproduct/wasteจากelementaryflow พร้อมcompartmentและunitmapping
- defaultprovider/explicitproviderlink;sourceverification;uncertaintyหรือเหตุผลที่ไม่มี
- licence/use/export/publicredistributionแยกกัน;ถ้าจำกัดสิทธิ เก็บprivateและไม่เปิดrawexchangeบนเว็บ
- no unlinked required exchanges;no double allocation;no duplicateupstream/combustion/treatment;positivefiniteFU/scaling;mass/energyplausibilityพร้อมเหตุผล ไม่บังคับclosedmassbalanceหากsourceไม่ได้แจกทุกน้ำ/อากาศ
- reproducibleunitprocessmatrix/reference-demand calculation หรือเทียบengineที่เลือก;รายงานinventory totalsก่อนLCIA
- sensitivityกับallocation/transport/LHV/treatmentโดยไม่เปลี่ยนsourceobservations;ไม่ใช้EF_CO2eแทนfullLCI

## แผนที่ควรทำต่อเป็นงานจริง

1. คัดactualThaiLCIdatasetsและเงื่อนไข;จัดacquisitionmanifestแยกAVAILABLE/REQUEST_REQUIRED/NOT_FOUND ยังไม่ต้องส่งข้อความถึงหน่วยงาน
2. ปิดbasisgate2020/2013 แล้วเลือกforegroundbaselineหนึ่งชุด แยกalternativecaseก่อนmerge
3. นำtransport/use/treatmentcandidateที่เปิดต้นฉบับได้มาทำfullfield/locatorreview;ตัวเลขจากsnippetไม่รับ
4. เติมcandidateprocesses/providersพร้อมrights/evidenceclassและสร้างLCAmachine-readableexport;runnegativechecksและcomparewithopenLCAเมื่อมีข้อมูลจริง
5. จึงนำcoverage/inventoryresultsขึ้นเว็บ พร้อมsources/scenarios/limitations ไม่เรียกการค้นพบฐานข้อมูลว่าทำโมเดลเสร็จ

## แหล่งทางการที่เปิดอ่านรอบนี้

- https://thainationallci.nstda.or.th/ — portalระบุบริการinventoryและimpactdata แต่publicHTMLยังไม่แสดงdatasetinventoryรายตัว
- https://www.nstda.or.th/home/knowledge_post/nstda-tiis/ — ระบุหมวดinfrastructure/agriculture/wastemanagement
- https://support.ecoinvent.org/licensing — educational/developer/interactive-tool restrictions
- https://greendelta.github.io/openLCA2-manual/prod_sys/Creating.html — product-system creation/providerlinking
- https://flcac-admin.github.io/FLCAC-docs/datasubmissionhandbook/ — unitprocess/provenance/explicitlink/USgeography/publicdomainguidance
- https://link.springer.com/chapter/10.1007/978-3-642-34519-7_2 — Thai2013case identity/scope, actualPDFreviewอยู่ในdocs/thai-lifecycle-source-selection.md

การค้นเพิ่มเติม: ThaiScience10895237PDFตอบ404;RMUTSVreportPDFtimeout;NRCTbibid293083PDF404;TIISlegacycatalogtimeout ไม่รับข้อมูลจากผลค้นแทนต้นฉบับและไม่วนretryชุดนี้ ผลนี้เป็นresearchdecision ไม่มีข้อมูลใหม่import/deploy/no paidpurchase/no messages/no fullLCIclaim
