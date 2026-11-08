# รีวิว LCI / ฐานข้อมูล / เว็บ — 5 พฤศจิกายน 2569

## คำตัดสินและขอบเขตการตรวจ

ระบบมีจุดแข็งด้านsource-preserving data engineering และการเปิดหลักฐาน แต่ยังเป็นdata explorerร่วมกับlocalactivity-model prototype ไม่ใช่completeLCI modellingplatform ตรวจPROJECT_STATE/evidence/sourcecode/design และเปิดproductionหน้าinventoryอ่านAX+ภาพหน้าจอจริง หน้าแสดงFAME10รายการและคำเตือนpartialinventoryถูกต้อง ไม่ได้ตรวจsecuritypenetration/EC2restart/restoreใหม่หรือรันทดสอบชุดเดิมซ้ำในรอบรีวิว

ไม่ให้คะแนนความพร้อมหรือเปอร์เซ็นต์ที่ไม่มีrubric และไม่เหมาว่าunit testsผ่านเท่ากับscientificvalidation

## จุดแข็งที่ควรรักษา

- คงrawvalue/Decimal/หน่วย/locator/sourcehash และแยกHOLD/nullจากศูนย์
- แยกACCEPTED_REFERENCE,source-reportedinventory,scenarioactivityและfullLCI ไม่เอาสถิติประเทศมาเป็นผลิตภัณฑ์อัตโนมัติ
- มีversionedcandidate/seal/immutablepayloadและMySQLengineverificationตามหลักฐานเดิม ไม่อ้างว่าcandidateDDLทั้งหมดอยู่productionแล้ว
- เว็บจริงมีfilters/คำศัพท์/หลักฐานรายแถว และบอกว่าTable4ไม่ครบวงจร
- proxyเก็บupstreamsecretฝั่งserver/GET-HEADallowlist ไม่ต้องบังคับreaderloginตามคำสั่งผู้ใช้

## ข้อวิจารณ์ลำดับเร่งด่วน

| ลำดับ | ข้อพบจริง / ผลกระทบ | วิธีแก้และเกณฑ์จบ |
|---|---|---|
| P0-1 | Localchainใช้CPO2019+FFB/RBDPO/FAME2020 ต่างชุดและไม่ทราบmeasurementperiod;Mill1เลือกfirstcolumn ไม่ใช่representativesample | เก็บเป็นexplicit scenarioต่อไป;ทำcompatibilitydecisionรายlinkทั้งproductspec/technology/geography/year/allocation;ต้องมีเหตุผลยอมรับหรือปฏิเสธก่อนburdenlink |
| P0-2 | Allocationยังไม่ทราบว่าtableก่อนหรือหลังแบ่งภาระ | เก็บUNALLOCATED/ALLOCATED/UNKNOWNแยกจากmethod/factor;ตารางunknownห้ามคูณ;หาต้นฉบับcalculationที่ตรงหรือเลือกconsistentunallocatedsource;เก็บcoproductทุกตัวและไม่หักcreditซ้ำ |
| P0-3 | Physicalsupplied=consumedเกิดจากสูตรเดียวกัน ไม่ใช่independentbalance | เรียกtransferarithmeticcheck;เพิ่มmass/energy/carbonbalanceเท่าที่flows/องค์ประกอบครบ ระบุwater/steam/moisture/stockchangesและexclusions;อย่าใช้100%balanceบนpartialinventory |
| P0-4 | สถานะfive-stagesมีข้อมูลแต่ยังขาดtransport/use/treatment/backgroundelementaryflows | ทำrequired-exchange/required-decisionregisterตามscope;missingnull/unknown/outofscopewithreason;ไม่เพิ่มstageชื่อครบแล้วให้ผ่าน;ใช้phasegateตามแผนT107 |
| P0-5 | Unitprocessreview schemaมีแล้ว แต่scenarioใหม่ยังJSON/CLIและไม่มีAPIrouteในproxy | เพิ่มmodelversion/scenario/processinstance/providerlink/calculationrun/result/assumption relationsต่อจากsource/version/exchangeเดิม;FKต้องชี้datasetversion/exchangeและfreezeinputhash/schema/parser/parameters;ผลเก่าต้องreproduceได้โดยไม่ดูlatestmutablefile |
| P1-1 | เว็บจริงยังแสดงTable4เดิม งานMill2019/6scenariosล่าสุดยังlocal | เพิ่มหน้ากรณีศึกษาแยกจากcatalog แสดงmodelversion/FU/boundary/status;ไม่เอาข้อมูลrightsunclearedเผยแพร่อัตโนมัติ;previewmetadataและสูตรได้ตามสิทธิ |
| P1-2 | หน้าinventoryมีหลายnotice/contextก่อนถึงตาราง;ตัวย่อ/ศัพท์อังกฤษยังอยู่ในแถวข้อมูล | ใช้summaryสั้นด้านบนหนึ่งชุด;ไทยก่อนศัพท์ต้นฉบับในtooltip/details;หน่วยและฐานชิดตัวเลข;เก็บwarningสำคัญไม่ซ่อน แต่รายละเอียดเทคนิคยุบได้ |
| P1-3 | ค่าคำนวณFFB187.52580ดูแม่นกว่าข้อมูลโรงงานและระยะประมาณ5km | จัดsignificantfiguresเฉพาะdisplay เช่น≈188kg;exportauditเก็บเลขคำนวณเต็ม;แยกreportedprecision/measurementuncertainty/scenario spreadไม่สร้างconfidenceintervalเทียม |
| P1-4 | Proxyorigin()รับเฉพาะhostnameลงท้าย.trycloudflare.com | เมื่อมีendpointถาวรต้องแก้validationเป็นexplicitallowlist/configที่reviewแล้วก่อนเปลี่ยนenv;ทดสอบnegativeorigin/redirect/credentialleak/timeout/cache+rollback;อย่าเปิดรับURLอิสระหรืออ้างว่าเปลี่ยนenvอย่างเดียวพอ |
| P1-5 | หน้าdatabase-designยังกล่าวรอapprovalmeaning และหน้าversionedมีประวัติตรวจengineที่supersedeกัน | สร้างcurrentarchitecture/releasestatusหน้าเดียวและลิงก์history;แยกsource/data/model/API/frontendversions;ระบุlocalvsproductionทุกส่วน |
| P2 | ยังไม่มีinteroperability/useracceptancetestของmodelล่าสุด | ส่งออกpackageมีflowtypes/units/referenceprocess/parameters/rightsแล้วลองimportopenLCAจริง;ทดสอบผู้ใช้ค้น→อ่านขอบเขต→เปิดหลักฐาน→ส่งออกโดยไม่ช่วยนำทาง |

## โครงสร้างข้อมูลเป้าหมาย

ต่อจากsource_observation → process_dataset_version → dataset_exchangeที่มีอยู่:

- product_system_version:scope/FU/period/cutoff/modelstatus
- scenario/assumption:baselineหรือalternative,เหตุผล,origin,ขอบเขต/ช่วงค่าที่มีหลักฐาน
- process_instance:datasetversionที่เลือกและactivityfactorของรุ่นนั้น
- provider_link:consumerexchange↔providerreferenceexchange,amountbasisและcompatibilitydecision ไม่เชื่อมด้วยชื่อstringอย่างเดียว
- allocation_rule_application:method/factor/basis/appliedbywho/sourcepreallocatedstatus
- calculation_run/run_input/result_exchange:immutableinputmanifest/runtimeversion/resulttype/หน่วย/rights พร้อมtransactionที่ไม่ทิ้งผลครึ่งชุด

ไม่ต้องย้ายทุกอย่างเพื่ออ้าง5NF:relationalnormalizationต่างจากการnormalizeปริมาณLCIต่อreferenceflow ต้องอธิบายFD/keys/constraintsตามrelationจริง และเก็บauditredundancyที่ตั้งใจไว้ได้

## รูปแบบหน้าเว็บที่แนะนำ

ไม่คืนแถบเดโม5ขั้นบังคับที่ผู้ใช้เคยไม่รับ ใช้หน้ากรณีศึกษาเดียว:

1. เลือกผลิตภัณฑ์และกรณีจากchoices พร้อมoptionalsearch
2. ด้านบนบอกกรณีอะไร/FUอะไร/รุ่นไหน/คำนวณอะไรได้/ส่วนไหนยังขาดในภาษาสั้น
3. ผังกระบวนการคลิกได้แสดงproductflowและข้อมูลขาด;สีไม่เป็นสัญญาณเพียงอย่างเดียว ต้องมีlabel
4. เลือกกล่องแล้วเห็นinput/output/source/refbasis/assumption และปุ่มเว็บไซต์ต้นทางคู่กับไฟล์ตาราง
5. ผลคำนวณแสดงเฉพาะtypeที่รองรับ;CO2eไม่พร้อมต้องเขียนยังคำนวณรวมไม่ได้ ไม่แสดง0;downloadmanifestพร้อมข้อมูลที่สิทธิรองรับ

ไม่ใช้ภาพตกแต่งแทนผังข้อมูลจริง และไม่เพิ่มframeworkmigrationเป็นงานจำเป็นโดยยังไม่มีประโยชน์UXที่ชัด

## ขอบเขต “ข้อมูลไทย”

ต้องแยกsourcepublishedinThailand,Thai-operationmeasurementและThai-representativesupplychainออกจากกัน ข้อมูลไฟฟ้าหรือสารเคมีที่แทนตลาดไทยอาจมีสัดส่วนนำเข้าจริง จึงไม่ควรลบทิ้งหรืออ้างว่าเป็นการผลิตภายในประเทศทั้งหมด การใช้GWPmethodสากลไม่ใช่สิ่งเดียวกับนำactivity/emissionfactorของประเทศอื่นมาแทนไทย นี่เป็นข้อเสนอให้กำหนดscopeชัด ไม่ใช่การยกเลิกข้อจำกัดThai-onlyของผู้ใช้หรืออนุญาตforeignsurrogateเอง

## ลำดับส่งมอบที่เหมาะ

ปิดscope/compatibility/allocationก่อนCO2e → ทำversionedscenario/calculationrun → เติมmissingexchangesตามความสำคัญ → นำcaseที่reviewแล้วขึ้นเว็บพร้อมสิทธิ → ตรวจimport/export/reproduce/usertaskและdeploymentfailure การเพิ่มsourcecountหรือtestcountไม่ใช่เป้าหมายแทนงานเหล่านี้

## แหล่งมาตรฐานประกอบการรีวิว

- UNEP/SETAC Global Guidance Principles,section4.2.1–4.2.2:FU/referenceflows,allocation,sourceoriginและqualitycontexts: https://www.lifecycleinitiative.org/wp-content/uploads/2012/12/2011%20-%20Global%20Guidance%20Principles.pdf
- openLCA officialmanualproductsystems/providerlinking: https://greendelta.github.io/openLCA2-manual/prod_sys/Creating.html
- openLCAexchange/schema: https://greendelta.github.io/olca-ipc.py/olca/schema.html

รอบนี้เป็นการรีวิว ไม่ได้applyschema/newUI/deployหรืออ้างว่าแก้ข้อเสนอทั้งหมดแล้ว
