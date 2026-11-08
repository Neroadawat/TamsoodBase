# Expert review: LCI + web database — 6 November 2026

ตรวจแบบread-only liveChrome desktop1440/mobile390,6HTTPrequests,source/schema/codeและหลักฐานเดิม ไม่ทดสอบsourceทุกcellใหม่ ไม่stress/restart/restoreEC2 ไม่เปลี่ยนproduction ดูevidence/expert-review-2026-11-06.json

## คำตัดสิน
เหมาะเป็นแหล่งสำรวจสถิติเชื้อเพลิงไทยและพื้นที่reviewหลักฐาน/กิจกรรมของกรณีศึกษา ยังไม่ใช่ฐานLCIครบวงจรหรือเครื่องคำนวณLCIA production. ความสวยดีขึ้นแต่ความสามารถเปรียบเทียบ/เลือกข้อมูลไปใช้จริงและoperationalmaturityยังตามหลัง.

## สิ่งที่ตรวจพบใหม่

1. **P1 navigation/focus**: story step5→B100 URLเปลี่ยนจริงแต่scrollY222และh2top-59.2px focusBODY;หัวข้อใหม่พ้นviewport. activateViewไม่resetตำแหน่ง/ย้ายfocus. แก้routeentryfocus/scrollและเก็บbackpositionอย่างแยกนโยบาย ไม่ใช้globalscroll0จนstoryjumpเสีย.
2. **P1 shareable filters**: diesel2024ให้2rows27664/25120จริง แต่URLยัง#nsoไม่มีfilters;reloadqueryว่าง69rows. เก็บtable/year/topicในURLพร้อมvalidateและtestback/reload/share.
3. **P1 mobile information order**:390x844หน้าสถิติส่วนแรกมีheader/warning/storylink/5topicbuttons/summarycards ทำให้ตารางอยู่นอกfirstviewport. เป็นdesigntradeoffไม่functionalbug. ให้แสดงresultcount+activefiltersก่อนและย่อsupportingcards/warningsแบบอ่านเพิ่มโดยคงcriticalboundaryเสมอ.
4. **P1 data capability clarity**: categorymapบอกdatasetแต่ยังไม่บอกactionต่อdatasetครบว่าreadquantities/metadataonly/exportได้หรือไม่. Corporate97เป็นmetadataonly/CSV403โดยตั้งใจ;ต้องบอกก่อนกด ไม่สร้างexportปลอม.
5. **P1 comparison semantics**: ยังไม่มีworkspaceเลือก2recordแล้วตรวจunit/year/scope/denominator/boundaryแบบอธิบายรายfield;เริ่มNSOtableเดียวก่อน ไม่หารEPPOBBL/DAYกับMillionLitres.
6. **P2 navigation density**:10sidebarentriesและ5catalogtopics+5storycategorylinksซ้อนหลายระดับ. แยกผู้สำรวจทั่วไปกับtechnicalreviewด้วยprogressivedisclosure ไม่ลบหลักฐาน.
7. **P2 frontend maintainability**:app.jsมี41function/state declarationsจากsearchcount,style.css198609bytesและหลายoverrideblocksต่อเนื่อง. Refactorเป็นcomponent/modulesตามdomainและtokenก่อนเพิ่มfeatures;frameworkเป็นchoiceไม่ใช่ความจำเป็น. ตรวจrender/filter/error/keyboardไม่ใช่แค่stringpresence.
8. **P2 typography/assets**:Thai fontใหม่โหลดจริง/อ่านดีขึ้น แต่ฝังWOFF2base64ในCSSทำให้CSSdecoded198609/transfer125312bytesในหนึ่งmeasurementและฟอนต์cacheแยกไม่ได้. ย้ายfontassetselfhostที่มีhash/OFL+preloadตามจำเป็นแล้วทดสอบlayoutshift/slowdevice ไม่สรุปCoreWebVitalsจากoneprobe.
9. **P2 accessibility/UAT**:contrast4samplesผ่านไม่ใช่fullWCAG. smallhero2labels11pxจริง;screenreader/keyboardroutefocus/zoom200%/targetspacing/shortlandscape/longlabelsต้องตรวจเพิ่ม และให้ผู้ใช้จริงทำtaskพร้อมบันทึกfeedback ไม่แต่งผล.

## จุดหลักทางLCIและฐานข้อมูลที่ยังเปิด

10. **P0 scientific scope**:live/api/modelfull=false,CO2e=null;flowcontract130sourceobservationsแต่eligibleelementary0/CFmethodnull/independentbalancefalse. ต้องยืนยันFU/referenceflow/systemboundary/coverageและallocationของตารางต้นฉบับก่อนapplyburdens. เรื่องเล่า5ช่วงเป็นconceptualpetroleum ไม่ใช่FAMElinkedmodelที่complete.
11. **P0 compatible inventory**:ยังต้องThai transport/use/waste/backgroundที่เข้ากันทั้งปี/geography/technology/unitและสิทธิ. มีข้อมูลทุกstageไม่เท่ากับเชื่อมได้;missingต้องnull+reasonไม่แทน0. 6scenariosไม่ใช่6independentmeasurementsหรือCI.
12. **P1 schema evolution**:activitymodelแยกsource/datasetversion/instance/run/result/sealดีแล้ว,R02–R05แก้แล้วไม่กล่าวหาซ้ำ. แต่schemafixedOPEN/UNRESOLVED/6caseเป็นreviewstoreตามintent ไม่ใช่multiuserdraft-review-publish-retractworkflow. ถ้าจะเป็นdatabaseplatformต้องออกแบบlifecycle/actor/role/auditeventsและconcurrencyจริง.
13. **P1 normalization/query projection**:MySQLcandidateamount/scaled_amountเป็นVARCHARเพื่อexactdecimalreplay ไม่ใช่ข้อผิดพลาดเอง แต่numericaggregate/orderต้องtypedprojectionพร้อมprecision/domaincontract และUNIQUEbusinesskeys/FDanalysisรายrelation;ไม่อ้าง5NFทั้งระบบ. Corporateเดิมและcandidateไม่ใช่schemaเดียวกัน;productionmigrationยังไม่พิสูจน์จากlocalcandidate.
14. **P1 operations**:6routesรอบนี้ready200/model200/reference200metadata97/CSV403ตามpolicy ไม่ใช่uptime/load/DRcertificate. QuickTunnelยังtemporary;ต้องstableendpoint,healthalert,restorefreshness/backupretention,resourcebudgetและrollbackdrillที่ตรวจownerและไม่แตะGinder/Caddy/SGเอง.
15. **P2 API/performance**:NSO273rowsส่ง448586bytesในprobe2.09sเพราะmetadata/notesซ้ำ;APIcacheprivate/no-storeและproxytimeout30s/client15s. แยกimmutablemanifestกับrowsและconditionalcacheเฉพาะข้อมูลpublicที่มีสิทธิ;aligntimeout/error/retry/cancellation ไม่cacheprivateหรืออ้างโหลดเร็วทุกเครือข่าย. Globalconnectioneventรายrequestยังไม่ใช่per-datasethealthควรแยกสถานะเมื่อconcurrentrequests.

## สิ่งที่ดีและต้องรักษา
แยกstatistics/reference/activityจากnormalizedLCI;sourceURL/locator/hash;เก็บrawvalue/หน่วย;immutableversionsและtransaction/replay;publiccorporatequantitieswithheldตามrights;server-onlysecret;read-onlyAPI;rollbackpreviousdeployment;nativebuttons/reducedmotion;selfhostThaiOFLfont. ห้ามเพิ่มCO2eหรือfullclaimเพื่อให้demoดูcomplete.

## แผนที่แนะนำ
A. แก้routefocus/URLfilters/mobilehierarchy/capabilitylabelsก่อนเพื่อให้demoค้น→อ่าน→เปิดต้นฉบับได้สั้นลง.
B. สร้างcompatiblecomparisonและdatasetdetailหนึ่งรูปแบบ พร้อมyear/unit/scope/source/license/lastreview/release.
C. จัดmodules/tokens/fontassets/APIpublicpayloadให้ดูแลง่าย;เพิ่มbrowserbehavior testsที่จับnavigation/filterreloadได้.
D. ดำเนินLCIgatesด้วยหลักฐานจริงและtypedDBprojection/workflowตามขอบเขต;stableendpoint/restore/UATเป็นงานแยกไม่ถูกปิดด้วยUI.

## เอกสารมาตรฐานที่ใช้ประกอบคำแนะนำ
- https://www.lcacommons.gov/quick-start-guide — แยกunit/systemprocess/background/LCIAmethods
- https://www.lcacommons.gov/flcac-resources — elementaryflowmapping guidance
- https://www.w3.org/TR/WCAG22/ — focus/targetsize/accessibility ไม่อ้างconformanceจาก4samples

ข้อจำกัด:ไม่มีnewsource-cell verification,noaccessibilitycertification,noindependentreviewer,noactualDBloadtest/noEC2restart ไม่มีproductionmutationในรอบรีวิวนี้.
