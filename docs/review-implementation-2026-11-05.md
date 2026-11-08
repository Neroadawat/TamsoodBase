# ผลดำเนินการตามรีวิว15ข้อ - 5พฤศจิกายน2569

เพิ่มเติม 8 พฤศจิกายน: ผล keyboard/load/memory/query-plan/fault checks ในเครื่องใหม่อยู่ที่ [local engineering review](local-engineering-review-2026-11-08.md) ไม่ใช่ production verification รอบใหม่; T109 ยัง IN_PROGRESS ตาม gates ด้านล่าง

## สถานะส่งมอบจริง

เผยแพร่ frontend/API metadata ที่ https://tamsoodbase.vercel.app/#case-study แล้ว deployment dpl_BoUuYRBhKZS8TFU9HYZyUBauyFXi รุ่นโมเดล657aa71137bdcd70d11ed3e15b0aa1066246393c409517f757a0a10d9ddec89f ไม่ใช่productionDBmigration

ทดสอบรวม219testsผ่าน;4isolatedprobesจากรีวิวถูกปฏิเสธครบ;MySQL8.4.13candidateตรวจsourcepayload130และresult330ทุกfieldพร้อมnegative5ข้อ/expectederrorcodes;publicfrontendcleanroom12sourcefiles/9assetsผ่าน;releaseconsistencyผ่าน;ตรวจHTTPจริง10ปลายทางและpublicmodelmetadataตรงlocalทุกfield;SRS0.7.1/PDF28หน้าrenderครบและตรวจภาพแล้ว ไม่มีการสร้างmember/contribution/userstudy/approvalแทนคน

## เช็กกลับทุกข้อ

| Review | สิ่งที่ทำแล้ว | สถานะและข้อค้างจริง |
|---|---|---|
| R01 Full LCI scope | ตรวจ7sourcepassages/6gatedecisions และคงtotal=null/full=false;ค้นThaiARDA/workbook/useหลักฐานใหม่อย่างมีขอบเขต | **ยังเปิดด้านวิทยาศาสตร์**:ไม่พบworkbook/table-specificbasisหรือmatcheduse/backgroundที่จะปิดได้ ไม่เดาค่า |
| R02 Stale provider edge | resolveendpointmembership/direction/kg;คำนวณsource×activityทั้งสองฝั่ง;rejectmissing/duplicate/extra/staleedges | **แก้แล้ว**;mutationtestsผ่าน |
| R03 Missing JSON amount | JSONkeyexistence/texttype/typedvaluechecksในSQLiteและMySQL | **แก้แล้ว**;missing/null/nontext/mismatchถูกปฏิเสธ |
| R04 Wrong process membership | triggerตรวจsource.processหรือreferenceproductที่มีจริงเทียบdatasetprocess;ไม่แก้payloadต้นฉบับ | **แก้แล้ว**;SQLiteและMySQLnegativecaseผ่าน |
| R05 Empty/incomplete release | assertcountsทุกrelation/source_count,scenario/runidentity,source/resultreplay,manifest/seal;rejectorphanextra | **แก้แล้วสำหรับขอบเขต6กรณีนี้** ไม่อ้างgenericarbitrarydatasetvalidator |
| R06 Local/live gap | /api/model,/api/release+หน้าB100บนVercel;allfieldmatch;MySQLequivalentschema+enginecandidateผ่าน | **ส่งมอบmetadata/APIแล้ว**;ตารางโมเดลยังlocalreview/temporaryMySQLverified ไม่ย้ายruntimeโดยไม่มีความจำเป็น/rollbackpackage |
| R07 Public rights boundary | referencepublicfieldallowlistไม่มีraw/scaledquantity/nestedpayload;publicCSV/reportquantities403;sourceURLsยังเปิด | **แก้ขอบเขตcorporateแล้ว**;97rowsmetadataยืนยันจริง ไม่รับรองสิทธิแหล่งอื่นทั้งหมด |
| R08 Flow mapping | source-localflowidentity/role/unitdimensionครบ130sourcesพร้อมcompartment/CFnullและeligibleLCIA=false | **โครงสร้างและexclusionsแล้ว**;ไม่มีelementaryinventory/provider/CFที่มีหลักฐานให้อนุมัติ ต้องเติมจริงก่อนLCIA |
| R09 Gate evidence binding | VERIFIEDต้องresolvecontent-hashdecision/modelversion/sourcehash/locator/reviewerrole ไม่รับข้อความลอย ๆ;แยกstructuralreadinessจากindependentreview | **แก้structuralbindingแล้ว**;ยังไม่มีindependenthumanreviewและไม่สร้างชื่อผู้ตรวจ |
| R10 Meaningful case choice | บอกชัดว่าเลือกบริบทโรงสกัด;ตัวเลขปลายทางปี2020คงเดิม ไม่แสดงคาร์บอนเปรียบเทียบ | **แก้คำอธิบายและส่งขึ้นเว็บแล้ว**;ไม่เปิด2019restrictedquantitiesเพื่อทำcomparison |
| R11 Readable UX | เพิ่มชื่อflowไทยคู่originalในตาราง/หลักฐาน,choicesoptionaltypingเดิมคงไว้;case/page/sourceidentityตรวจbrowserจริง | **แก้ส่วนภาษาและcaseclarityแล้ว**;ยังต้องhumanuseracceptanceและปรับdensityตามfeedbackจริง ไม่คืน5stepbar |
| R12 Operations | ตรวจownerprojectVercel/เก็บpreviousdeploymentrollback;10liveHTTPchecks;remoteMySQLowner/APIbefore-afterตรวจจริง | **ตรวจส่วนนี้แล้ว**;QuickTunnelยังชั่วคราว/ไม่มีdomain,ไม่มีrestart/restore/loadtestรอบใหม่ ไม่แตะGinder/Caddy/SG |
| R13 SRS/ERD | SRS0.7.1เพิ่มrequirements/traceability/schema/pipeline/privacy/science limitations;ERDใหม่+PDF28หน้า | **ร่างเทคนิคอัปเดตแล้ว**;ทีมต้องกรอกข้อมูลและreviewรับรองเอง ไม่ใช่ฉบับส่งงานแล้ว |
| R14 Reproducibility | แยก12sourcefilesสร้างpublicfrontendในtemporarydirไม่มีraw/private;hash9assetsตรวจครบ;คู่มือhandoff | **frontendcleanroomผ่าน**;fullresearchpipelineต้องsourceที่มีสิทธิ ไม่แนบprivateเพื่อให้cloneผ่าน และไม่Gitpush |
| R15 Uncertainty/balance/interoperability | แยกreportedprecision/scenariospreadจากdistribution/CI;ยืนยันconstructedtransferไม่ใช่independentbalance;CFไม่มีไม่คำนวณ | **guard/limitationsแล้ว**;ยังไม่มีองค์ประกอบพอสำหรับmass/energy/carbonclosure/uncertaintydistributionหรือopenLCAengineimportจริง |

## หลักฐาน

- evidence/system-review-probes.json:4ข้อพบเดิมตอนนี้accepted=falseทั้งหมด จากscripts/probe_activity_review_boundaries.py
- evidence/activity-model-store.json และactivity-model-mysql.json:sealedlocalrelease+isolatedengine;ไม่มีAPIproductionmigration
- evidence/review-production-verification.json:deployment/10routes/metadataallfieldmatch/assetmatch/rightsprojection
- evidence/frontend-cleanroom.json และmodel-flow-contract.json
- tmp/review-complete-suite.log:219tests;tmp/review-final-regression.log:14targetedchecksหลังเพิ่มorphanvalidation
- evidence/srs-current-review.json และoutput/pdf/TamsoodBase-SRS-review.pdf:0.7.1/28pages/28rendered
- output/review-implementation/live-b100.png:ภาพproduction;browserยังยืนยันThai flowlabelsและreferencequantitywithheldได้

## ข้อจำกัดการเปลี่ยนproduction

Vercelเผยแพร่จากbuild/vercel-uploadallowlist ไม่uploadresearchrepo/raw/credentials ตรวจremoteprojectIDตรงก่อนdeployและเก็บdeploymentเดิมdpl_EfA4ngG9mh1uqX9UBDd1rt8i3R4Wสำหรับrollback ไม่มีการpushGit ซื้อdomain สร้างautomation ส่งข้อความ หรือใช้subagent

MySQLใช้ฐานทดลองชื่อสุ่มพร้อมowner markerบนcontainerที่ตรวจlabelแล้ว ไม่แก้productiontables/APIimage/grants ก่อนcleanupตรวจmarkerตรงและลบเฉพาะฐานที่สร้างเอง ทดสอบnegativeต้องได้3819หรือ1644ตามชนิด ไม่ถือSQLsyntaxerrorเป็นผลผ่าน

## ลำดับที่ยังต้องทำเมื่อมีหลักฐาน/ผู้ใช้จริง

1. ปิดtable-specificallocationและmatchedThaiuse/backgroundก่อนรวมภาระ;ถ้าหลักฐานไม่พอให้rejectlinkหรือคงscenario-only
2. เลือกstablebackendendpointเมื่อมีdomainหรือทางเลือกที่ทีมตัดสิน;ยังไม่ซื้อหรือถามซ้ำเรื่องdomainที่ยังไม่มี
3. ให้สมาชิกทดลองค้นflow→อ่านbasis→เปิดsource→exportmetadataจริงแล้วเก็บfeedbackตามจริง รวมทั้งreviewSRS/contribution
4. เมื่อelementarymapping/providersมีจริงจึงทำindependentbalance/CFmethod/interoperability ไม่อ้างว่าทุกข้อสำเร็จจากจำนวนtestหรือจำนวนแถว
