# รีวิวทั้งระบบ: LCI / web database — 5 พฤศจิกายน 2569

## คำตัดสิน

TamsoodBase มีฐานงาน data provenance และ data explorer ที่ดีขึ้นชัดเจน พร้อม local prototype สำหรับประกอบกิจกรรม B100 แบบแยกรุ่น แต่ยังไม่ใช่แพลตฟอร์ม full lifecycle LCI/LCIA ที่นำผลรวมไปเปรียบเทียบผลิตภัณฑ์ได้ ปัญหาปัจจุบันมีทั้ง scientific evidence gaps และข้อบกพร่องของตัวตรวจที่แยกกัน ต้องแก้ทั้งสองด้าน ไม่ใช้จำนวน tests หรือจำนวน flows แทนความครบถ้วน

ไม่ให้คะแนนรวมโดยไม่มี rubric และไม่อ้างว่าโครงการแพ้/ชนะแน่นอน

## ขอบเขตที่ตรวจรอบนี้

- อ่าน AGENTS/PROJECT_STATE/current architecture, schema SQLite/MySQL, store/chain/lifecycle validators, WSGI, MySQL reader, Vercel proxy/build/privacy boundary, deployment scripts, SRS/flow registry และหลักฐานเดิม
- เปิดเว็บจริงหน้า inventory: โหลด FAME10รายการ บอก partial inventory และปีวัดไม่ระบุ; หน้าใหม่ B100ยังไม่มีในเมนู production
- อ่าน API 5ปลายทางแบบ GET: healthz/readyz/product-inventory/reference.json ตอบ200; case-study.jsonตอบ404 ไม่ได้เปลี่ยนค่า production
- สร้าง adversarial probes เฉพาะฐาน SQLiteในหน่วยความจำและสำเนา artifactในหน่วยความจำ พบ4ข้อที่ทำซ้ำได้ ไม่มีการแก้ source/scenario/ฐานจริง
- อ่านหลักฐาน NSO:273 source-cell verified;เทียบข้ามสิ่งพิมพ์169=141exact+24rounding+4scope differences;104ยังไม่เทียบครบ เก็บ source divergence แยก ไม่อ้าง independent measurement
- ไม่รันชุดทดสอบเก่าทั้งหมดซ้ำโดยไม่มีเหตุ รายงาน208testsเป็นผลรอบก่อน;รอบนี้เป็นการตรวจขอบเขตเพิ่ม
- ไม่ได้ SSH ตรวจ runtime/restore EC2 หรือ IAM/S3 ใหม่, ไม่ load test/penetration test, ไม่อ่านภาพต้นฉบับทุกแหล่งทุกหน้าใหม่ ไม่อ้างว่า audit ครบทุกตัวเลขรอบนี้

## ข้อพบและลำดับแก้

### R01 — P0 สำหรับการอ้างผล LCI: ยังไม่มีระบบที่ครบขอบเขตคำนวณ

FAME1000MJเป็น study basis แต่โมเดลกิจกรรมจบที่การผลิต; allocation/tablebasis, transport, use, treatment emissions, Thai background exchanges ยังเปิด ค่ากิจกรรมไม่ใช่ elementary inventory หรือ CO2e การบอกครบ5stageไม่ได้ทำให้ครบ flows

**แก้:** ปิด evidence decisions ทีละเรื่องตาม fame-gate-closure-review.md ใช้ outcome ACCEPTED/REJECTED/SCENARIO_ONLY/UNKNOWN พร้อมเหตุผล ไม่เปลี่ยน UNKNOWN→0 และไม่เอา published CO2e factor มาบวกกับ inventory ที่มีภาระซ้ำ **เกณฑ์จบ:** ทุก required exchange มีค่า/ขอบเขต/เหตุยกเว้นที่ทบทวนแล้ว และผลรวมตาม FU reproduce ได้

### R02 — P1: ปริมาณบน provider edge ยังไม่ถูกตรวจย้อนกับผลของ endpoint

src/activity_model_store.py:validate_case ตรวจ supplied==consumed จากสองฟิลด์บน edge แต่ไม่ได้คำนวณใหม่จาก source exchange × process activity ทั้งสองด้าน Probe เพิ่ม CPO factorและผลทุกแถว CPOเป็นสองเท่าโดยคง edgeเดิม ตัวตรวจยังยอมรับ นี่ไม่พิสูจน์ว่าชุดจริงผิด แต่พิสูจน์ว่าตัวตรวจยังกันความไม่สอดคล้องนี้ไม่ได้

**แก้:** resolve endpoint IDs/roles/units จาก process membership แล้วคำนวณ supplied/consumed ใหม่ ตรวจ edge setครบ3เส้น ไม่มีซ้ำ/ขาด/extra พร้อมผิดfactor/ผิดunit/ผิดdirection tests **เกณฑ์จบ:** mutationนี้ถูกปฏิเสธก่อน persist; baselineเดิมยังผ่าน

### R03 — P1: CHECK บน JSON amount ปล่อย missing key ผ่านได้

sql/activity-model-review.sql:7 ใช้ json_extract(...)=amount;เมื่อ amount keyหาย ผลเป็นSQL NULL ซึ่ง CHECKไม่เท่ากับfalseจึงผ่าน Probe INSERT typed amount12/unitkg แต่ payloadมีเพียงunitสำเร็จ การทดสอบ mismatchเดิมไม่ครอบคลุม missing key

**แก้:** ตรวจ json_type/existence/non-null/stringtype ตาม source contract ก่อนเทียบ typed value;ทดสอบ missing/null/wrongtype/NaN โดยไม่แปลง original lexemeทิ้ง **เกณฑ์จบ:** missingamount INSERTถูกปฏิเสธและ transaction rollback

### R04 — P1: source-process membership ยังไม่เป็น invariant ระดับฐาน

dataset_exchange FK รับ sourceที่มี processFAME ไปอยู่ datasetversionCPOได้ในฐานจำลอง การจับคู่ endpointกับinstance/versionที่มีอยู่เป็นจุดแข็ง แต่ไม่ทดแทนการตรวจ processของ source จริง

**แก้:** typed process identity + composite key/trigger หรือ validated mapping layerพร้อมsource-specific aliases ไม่เทียบ stringเดา **เกณฑ์จบ:** cross-process source membershipถูกปฏิเสธทั้ง insertและ release audit

### R05 — P1: audit() ยังรายงานผลเชิงบวกบนฐานว่าง

src/activity_model_store.py:audit ฐานเพิ่ง initialize มี0runs/0results/0sourcesแล้วคืน foreign_keys_ok=true โดยไม่raise ใน builderปัจจุบันมีpersist/seal/manifestก่อน จึงไม่อ้างว่ารุ่นที่sealแล้วว่าง แต่ helperนี้ยังไม่พอเป็น release acceptance gate

**แก้:** แยก diagnostic statistics จาก assert_release(expected manifest);ตรวจจำนวนและidentity sets,source_countจริง,ทุกscenarioมีrun,inputs/implementation hash,ผลครบ,seal และ transfer replay **เกณฑ์จบ:** empty/missingrun/missingresult/extraunexpectedrowไม่ผ่าน acceptance

### R06 — P1: ระบบใหม่กับ production ยังเป็นคนละผลิตภัณฑ์ข้อมูล

APIจริงยังไม่มี model/scenario/run endpoints; case-study.json404 ขณะที่ localมี6กรณีและsealedstore การทดสอบในเครื่องไม่ได้ทำให้กรรมการเห็นสิ่งเดียวกันบนURLจริง

**แก้:** ระบุ read API contract เช่น model version/scenario detail/run manifest ที่สอดคล้องกับ public rights projection;ย้ายschemaใหม่ไปMySQL candidateและตรวจengineจริงก่อนrelease;ถ้าตั้งใจlocalreviewให้บอกเช่นนั้น ไม่จำเป็นต้องย้ายเพื่อชื่อengine **เกณฑ์จบ:** public frontend/APIแสดงreleaseเดียวกัน พร้อมrollback;ไม่เปิดprivate330rowsตามไปด้วย

### R07 — P1: นโยบายเผยแพร่ corporate reference ยังขัดกับ usage profile

GETจริง /api/reference.json อ่านได้97rows และทั้งหมดระบุ NOT_CLEARED;manifestระบุ LOCAL_RESEARCH_REFERENCE การไม่เปิดraw PDFเป็นเรื่องดี แต่การมีคำเตือนสิทธิไม่ใช่ตัวกรอง distribution

**แก้:** จัด public distribution profile ที่ reviewระดับfield/row แยกmetadata/ค่าที่อนุญาตจากresearch profile;readerไม่ต้องloginตามผู้ใช้ได้ แต่public APIต้องคืนเฉพาะprojectionที่ตัดสินแล้ว **เกณฑ์จบ:** มีallowlistและnegative export test สำหรับสิทธิ/fieldจริง ไม่เปลี่ยนNOT_CLEAREDเป็นCLEAREDเอง ไม่อ้างว่าพบการละเมิดกฎหมายจากflagเพียงอย่างเดียว

### R08 — P1 ก่อน LCIA: flow registry ยังไม่ใช่ elementary-flow mapping

registryปัจจุบันยอมรับเองว่าsource-local labels ไม่ใช่global ontology;input Methanol/electricity/CPOเป็นtechnosphere ไม่ใช่CO2 emission และPOMEเป็นstreamไม่ใช่CH4 leakage

**แก้:** versioned flow/flow property/unit group/compartment/mapping decision/reference product;biogenic CO2/fossil CO2/CH4/N2Oแยก;characterization method/version/horizon/CF sourceแยกจากinventory **เกณฑ์จบ:** ทุกflowที่จะคิดimpactมีmappingที่ทบทวน ไม่มีชื่อคล้ายแล้วรวม และรายงาน unmappedcoverage/exclusions

### R09 — P1: readiness ทางวิทยาศาสตร์ยังพึ่ง label/evidence presence มากเกินไป

src/lifecycle_model.py ตรวจ gate VERIFIED + truthy gate_evidence แต่ยังไม่resolveหลักฐานนั้นกับdecisionรุ่นเดียวกันที่มีhash/source/ผู้ทบทวนจริง ไม่พบหลักฐานว่ามีคนใช้เปลี่ยนสถานะให้ผ่านในproduction ข้อนี้เป็นtrust-boundary weaknessของตัวตรวจ

**แก้:** gate decision IDs/FKs/state transitions/source locators/version + reviewer roleจริง;แยกsoftware_ready,source_verified,model_compatible,scientific_reviewed **เกณฑ์จบ:** labelหรือข้อความทั่วไปไม่ทำให้ model_ready เปลี่ยนโดยไม่มีdecisionที่resolveได้

### R10 — P2: เลือก6โรงสกัดบนหน้าใหม่ แต่ผลสาธารณะที่เห็นยังเหมือนกัน

web/case-study.jsใช้ public_activity_kgชุดเดียวทุกกรณี เพราะค่าโรงสกัด2019ไม่เผยแพร่ตามสิทธิ ผู้ใช้เปลี่ยนdropdownจึงเห็นชื่อเปลี่ยนแต่CPO/RBDPOเดิม ทำให้คาดหวังการเปรียบเทียบที่หน้านี้ไม่ได้ทำ

**แก้:** บอกข้างตัวเลือกว่าเลือกบริบท/ไม่เปรียบเทียบคาร์บอน;แสดงdifferenceเฉพาะmetadataที่ตรวจและแจกได้ หรือซ่อนตัวเลือกจนมีประโยชน์ต่อreader ไม่เปิดrestrictedquantityเพื่อแก้UX **เกณฑ์จบ:** ผู้ใช้บอกได้ว่าเปลี่ยนกรณีแล้วอะไรเปลี่ยน/อะไรคงเดิมโดยไม่ต้องมีคนนำ

### R11 — P2: หน้าจริงยังใช้พื้นที่อธิบายก่อนถึงตารางมาก

ภาพdesktopจริงมีheader/guide/tabs/warning/source/filter/FU/contextซ้อนกันก่อนแถวข้อมูล ภาษาต้นฉบับRBDPO/Steam/Crude glycerineยังอยู่ในแถว แม้มี glossaryและคำเตือนถูกต้อง

**แก้:** summaryสั้นหนึ่งชุด,แสดงchosenbasisติดvalue,ไทยคู่source labelในแถว,ขยายtechnicaldetailsเมื่อขอ;หลักฐานควรบอก“ตารางใด/หน้าใด/ค่าจากไหน”ก่อนdownload **เกณฑ์จบ:** ทดสอบงานค้นหนึ่งflow→อธิบายฐาน→เปิดต้นฉบับ→export โดยมนุษย์จริง ไม่คืนแถบ5ขั้นที่ผู้ใช้ปฏิเสธ

### R12 — P2: endpointถาวรและoperational evidenceยังไม่ปิด

healthz/readyzตอบ200ปัจจุบัน แต่QuickTunnelยังอาศัยhostnameชั่วคราว;permanent-originallowlistเป็นเพียงโค้ดเตรียม และ readinessMySQLตรวจrelease+countsเป็นหลัก จึงไม่พิสูจน์field semantic/ทุกdataset hash/runtime drift

**แก้:** stableendpointเมื่อมีทางที่ผู้ใช้เลือก;releaseidentity endpointและmanifest linkage;monitorerror/latency/stale release และrestore drillตามเวลา สำหรับexport/rate/concurrencyให้ตั้งตามภาระจริงของEC2 ไม่เดาว่ารับtrafficมากได้ **เกณฑ์จบ:** controlledrestart/reconnect/restore testพร้อมowner/rollback ไม่แตะเพื่อนservice

### R13 — P2: SRSตามหลังโมเดลล่าสุด

SRSยังVersion0.6วันที่30ต.ค.;currentarchitectureมี5พ.ย. แต่SRSยังไม่รวมactivity store/scenario/runและแหล่ง2019/2013ใหม่ทั้งหมด Release hashตรงPDFยืนยันเพียงตรงไฟล์เดิม ไม่ยืนยันว่าเนื้อหาทันimplementation

**แก้:** requirement→schema/API/UI/test traceabilityรุ่นใหม่,planned/local/liveแยก,ปรับERD/data dictionary/limitationsก่อนrenderเอกสารใหม่;ไม่แต่งรายชื่อ/contribution **เกณฑ์จบ:** requirementทุกข้อชี้implementationหรือplannedstatusที่ถูกและPDFตรงsourceใหม่

### R14 — P2: reproducibilityจากcheckoutยังเสี่ยง

gitstatusปัจจุบันมี363รายการเปลี่ยน/ใหม่ และไฟล์สำคัญหลายตัวuntracked;build/raw/private artifactsไม่ได้ตามGitโดยตั้งใจ จึงไม่ถือว่าเพื่อนcloneแล้วรันเหมือนเครื่องนี้ได้โดยอัตโนมัติ

**แก้:** manifestโค้ด/dependency/source-acquisition/build prereqs,สะอาดsource-onlyhandoffและfixtureที่สิทธิรองรับ;reproduceจากโฟลเดอร์แยก ไม่pushหรือcommitแทนผู้ใช้โดยพลการ **เกณฑ์จบ:** clean-room runตามREADMEได้โดยไม่พึ่งไฟล์ลับ/absolutepathของเครื่องนี้

### R15 — P2: uncertainty/validation/exportยังต้องยกระดับ

ปัดdisplayเป็น≈ถูกทางแล้ว แต่ยังไม่มีqualityprofile/parameter distributionที่อิงหลักฐาน,การเปรียบเทียบ6millไม่ใช่confidenceinterval,transferเท่ากันจากสูตรเดียวไม่ใช่independentbalance;ยังไม่มีopenLCAimportและuseracceptanceที่ผ่านจริง

**แก้:** แยกreportedprecision/measurementuncertainty/scenario variation,ทำmass/energy/carbonbalanceเฉพาะส่วนที่ข้อมูลพอ,ตรวจpartialbalanceพร้อมexclusions;exportunit/provider/referenceflow/rights/version แล้วimportเครื่องมือจริง **เกณฑ์จบ:** independent checksและinteroperabilityresultsที่reproduceได้ ไม่สร้างuncertaintyตัวเลขขึ้นเอง

## สิ่งที่ทำดีแล้วและควรรักษา

- sourceoriginal/Decimal/หน่วย/hash/locatorไม่ถูกเขียนทับ และHOLDแยกศูนย์
- ข้อมูลสถิติ/บริษัท/source-reportedinventory/scenario/fullLCIแยกความหมาย
- SQLparameterization/read-onlyreader,server-onlysecret,proxyGET/HEADrouteallowlist/redirectreject/responsebounds เป็นฐานป้องกันที่ดี ไม่พบsecretในresponseที่ตรวจ
- โมเดลversioned+seal+transaction+candidateFKเป็นพัฒนาการจริง เพียงยังมีinvariantsที่ต้องเพิ่ม
- หน้าเว็บบอกpartialอย่างตรงไปตรงมา และมีลิงก์ต้นฉบับ/metadataที่ตัดrestrictedrowsออก
- ไม่ต้องเพิ่มframeworkหรือrelationจำนวนมากเพื่อให้ดูซับซ้อน;ยังไม่ควรอ้างทั้งระบบ5NF การnormalizationต้องอาศัยFDของแต่ละrelationและintentionalauditredundancy

## แผนแก้ที่แนะนำ

1. R02–R05 ปิดความถูกต้องของlocalmodelstoreก่อนย้ายฐาน/เผยแพร่รุ่นใหม่;เพิ่มmutationtestsแทนบวกhappy-pathtestsซ้ำ
2. R01/R08/R09 ปิดscientificdecisions/flowmappingทีละชุด;ถ้าไม่มีdataให้rejectlink/retainpartialแทนแต่งค่า
3. R07 ทำpublicprojectionส่วนcorporateก่อนขยายการแจกข้อมูล จากนั้นR06ยกระดับmodelAPI/MySQLcandidate/releaseidentity
4. R10/R11 ทดสอบUXด้วยงานจริง แล้วpublishtestedpackageที่reviewสิทธิแล้ว
5. R12–R15 ปิดoperations/SRS/clean-room/interoperabilityโดยไม่ใช้จำนวนtestsเป็นเป้าหมาย

## หลักฐานและแหล่งเทียบ

- evidence/system-review-probes.json / scripts/probe_activity_review_boundaries.py — reproduce4findingsในmemory ไม่ใช่ข้อมูลเสียที่พบในproduction
- evidence/system-review-live-readonly.json และ system-review-public-rights.json — GETread-onlyปัจจุบัน ไม่เก็บrawresponseของcorporateซ้ำลงรายงาน
- [UNEP/SETAC Global Guidance Principles](https://www.lifecycleinitiative.org/wp-content/uploads/2012/12/2011%20-%20Global%20Guidance%20Principles.pdf),section4.2.1.3–4.2.1.4 และ5.2:referenceflow/allocationdocumentation/temporalcontext
- [openLCA official product-system manual](https://greendelta.github.io/openLCA2-manual/prod_sys/Creating.html):referenceprocess/providerlinking เป็นองค์ประกอบชัดของproductsystem ไม่เทียบชื่อflowแล้วนับว่าครบ

รอบนี้เป็นreviewพร้อมdefectreproductionและแผนแก้ ไม่ได้แก้โค้ดschema/modelหลัก ไม่deployหรือเปลี่ยนEC2/MySQL/S3 และไม่อ้างว่าข้อพบได้รับการแก้แล้ว
