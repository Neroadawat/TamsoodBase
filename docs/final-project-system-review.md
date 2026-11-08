# เทียบระบบกับรายละเอียด Final Project ทั้งชุด

ทบทวน27ตุลาคม2569 ตามคำขอผู้ใช้ให้เน้นระบบ **ยังไม่จัดทำงานส่งของแต่ละM** อ่าน12หน้าในหมวดproject: index/timeline/mission/final-process/prepare/knowledge และบทความLCI/SRS/Memo/ERD/Neo4j/Transaction&Indexing สำเนาHTMLอยู่buildที่ไม่เข้าrepo/แพ็กเกจ ไม่รวมเอกสารตัวอย่างDriveหรือการบ้านวิชาอื่น

## ข้อสรุปที่มีผลต่อทิศทางระบบ

TamsoodBaseมีระบบเก็บแหล่งข้อมูล ตรวจย้อนกลับ SQL/API และแยกสถานะที่แข็งแรง แต่ **ความพร้อมทางวิศวกรรมไม่เท่ากับความครบของLCIต่อfunctionalunit** ตามหน้าโครงงาน จุดที่ต้องเน้นคือprocess/flow/exchange/referencebasis/boundary ไม่ใช่ขยายจำนวนสถิติให้มากที่สุด เว็บสวยและdeployได้เป็นส่วนสนับสนุน ไม่แทนหลักฐานเหล่านี้

หน้า[LCI](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-lci.html)ยกตัวอย่างPetroleumเป็นดีเซล1ลิตรหรือ1MJที่ประตูโรงกลั่นและกล่าวถึงallocation แต่ระบุว่าตัวอย่างไม่ใช่ตัวเลขจริง จึงไม่ใช้ตัวอย่างนั้นสร้างค่าดีเซล/CO2หรือหารยอดองค์กร/ประเทศเอง ชุดที่เรามีฐานชัดที่สุดตอนนี้คือFAME/H-FAME16exchangesต่อ1000MJfuelจากงานวิจัย ซึ่งเป็นforegroundconversion ไม่ใช่fullLCIของโรงกลั่นหรือตัวแทนประเทศ

## ตารางตรวจระบบอย่างละเอียด

| ประเด็น | งานปัจจุบัน | ผลเทียบ / สิ่งที่ควรปรับ |
|---|---|---|
| Thailand/domain relevance | แหล่งไทยและfuelrelated;BHD8แยกเพราะเทคโนโลยีต่างประเทศ | คงเกณฑ์นี้ แต่ชื่อpublisherไทยอย่างเดียวไม่ทำให้ทุกค่ามีscopeไทยหรือเป็นnationalaverage |
| Process identity | inventoryมีFAME/H-FAME;corporateใช้context/metric;statisticsมีคนละidentity | Processgraphปรับใช้source+process ไม่ใช้ชื่อบริษัท/ปีแทนunitprocess |
| Functional/reference basis | inventoryฐาน1000MJfuel;corporateบางratioมีตัวหารเดิม;DMF/NSO/EPPOเป็นสถิติ | เก็บreference_amount/reference_unitกับprocessจริง ไม่ตั้งglobalbasis1ตันหรือ1ลิตรให้ทุกชุด |
| System boundary | มีข้อความboundary/technology/source_scope | ต้องแสดงขอบเขตควบคู่ตัวเลขเสมอ ไม่เรียกforegroundtableว่าcradle-to-grave |
| Flow identity/type | flowlabel/unitอยู่inventory;corporatemetricไม่ใช่globalflow | ปรับgraphให้มีFlowsource-local คงหน่วย และยังไม่เดาproduct/elementary/compartmentหากsourceไม่ระบุ |
| Exchange and direction | inventory16รายการมีINPUT/OUTPUT/role | เพิ่มExchange nodeรักษาamount/unit/locator/roleครบ ไม่ยุบสองexchangeเข้าหากันด้วยnameหรือdirectionเพียงอย่างเดียว |
| Allocation/coproduction | เก็บคำอธิบายpaperและrole;ไม่allocateเพิ่ม | ไม่เอาenergytotal/throughputสร้างproductLCI ไม่ถือco-productเป็นemission |
| Geography/time | inventoryThailandแต่data_periodnull/publication2020;สถิติมีปีจริง | ห้ามใช้ปีเผยแพร่เป็นปีวัด;nullableต้องบอกmissingstatusอย่างชัดเจน |
| Source registry/IDs | source-registry.csvมีรหัสจริง DMF-CKAN/THAIOIL/SPRC/NSO/MDPI/EPPO | ไม่จำเป็นเปลี่ยนPKให้SRC-01ทุกฐาน แต่ควรมีcrosswalkจากreadableID→snapshot/document hash;ตอนนี้ยังไม่เรียกว่ามีsource_idชื่อเดียวทุกAPI |
| Provenance | SHA256/URL/page/line/column/batch/release | ครอบคลุมengineeringtrace;actualsourceaccuracyยังแยกจากparserreproducibility |
| Raw/Staging/Mapping | มีpipelineแยกและoffline replay | รักษาrawfields/Decimalและmappingversion ไม่ลบsourcefieldที่ยังไม่ใช้ |
| Validation/reject/hold | schema/typed/payload/source/unit/time/duplicatechecks;rejectและholdเก็บเหตุผล | รักษาสถานะ ไม่เปลี่ยนACCEPTED_REFERENCEเป็นproductLCIเพื่อให้ตรงตัวอย่าง |
| Quality volume | corporate97reference/4hold;DMF34671pending;NSO273;EPPO5934;inventory16 | ไม่รวมเป็นยอดacceptedเดียว;total/component/intensity/republicationไม่ใช่independentflowsทั้งหมด |
| Relational model | MySQL4ฐาน27tables;SQLite/JSONserveweb | โครงสร้างมีเหตุผล แต่ยังไม่ใช่canonicalLCIphysicalshemadeียว ต้องอธิบายintegrationผ่านsemanticsและmapping |
| Unit master/scaling | corporateมีunitmaster/exactscaling;inventoryและstatisticsคงunitlabel | ไม่อ้างว่าทุกฐานใช้globalunitmasterแล้ว;ก่อนconvertต้องมีdimension/ruleprecision/sourceรองรับ การแปลงMJ/kWhไม่ใช่allocation |
| SQL/usecase | JOIN/filter/qualityqueriesและAPIมีจริง | ต้องเน้นqueryที่ตอบprocessinput/output/basisและtrace ไม่ใช้แต่COUNT/searchเป็นคำตอบของfunctionalunit |
| Transaction/ACID | EPPOverifyก่อนcommit;SQLitelabrollback/isolation/writerlock/reopenผ่าน | ยังไม่ใช่MySQLisolationexperimentหรือpowerfailuretest เอกสารwebเป็นแนวคิด ไม่ใช้แทนผลทดลองของเรา |
| Index/EXPLAIN | MySQLDMFworkloadกับ/ไม่ใช้index ผลเท่ากัน วัดmedian5รอบ | ไม่สร้างindexทุกcolumn ไม่อ้างเวลาDockerเป็นproductionSLA;workloadinventory16แถวอาจไม่มีเหตุให้เพิ่มindex |
| Graph/Neo4j | เดิมมีcorporateprovenancegraph/Python;รอบนี้เพิ่มinventorygraph | ตรงprocess-flow-exchangeมากขึ้น แต่ยังไม่มีNeo4j/Cypherengineevidence ไม่เดาupstreamchainsจากชื่อflowเหมือนกัน |
| NoSQL | JSONmetadata/API/documents | ไม่อ้างว่าJSONfileเท่ากับMongoDBengine |
| Restore/operations | EC2private/S3iam-role;backup38membersdownloadhashผ่าน;rollbackdryrun | ไม่ใช่freshmachineDRหรือMySQLbackup;S3ไม่ใช่ฐานMySQLและไม่ได้syncอัตโนมัติ |
| User experience | catalog5ชุด/filters/card-list/mobile/errorretry/sourceviewer | คงการเลือกชั้นข้อมูลและข้อจำกัดใกล้ตัวเลข;ต่อไปควรให้processviewแสดงbasis/boundaryก่อนผล ไม่ซ่อนหน่วยเพื่อความสวย |
| Rights/revieweraccess | rights/statusแยก;S3private ไม่มีrawสิทธิไม่ชัดในdeploy | เว็บขอlinkเปิดได้ไม่ได้อนุญาตให้เผยแพร่raw/derivedที่ไม่clearrights;เตรียมrevieweraccessก่อนpublicrouting |
| Requirementtrace | มีR01–R14และquery/evidenceหลายไฟล์ | ยังไม่ครบone-to-oneformaltraceabilityทุกrequirement อย่าสรุปว่าครบเพียงเพราะtests100ผ่าน;การจัดรายงานMพักตามผู้ใช้ |
| Professional/human evidence | AI-assistedเปิดเผย;ไม่มีชื่อหรือcontributionปลอม | consent/memo/peerfeedback/individualdefenseเป็นงานมนุษย์จริง แยกจากการแก้codeในรอบนี้ |

แหล่งประกอบตาราง: [Prepare](https://akkhara.engr.tu.ac.th/cn230/project/prepare.html), [ERD](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-erd.html), [Neo4j](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-neo4j.html), [Transaction/Index](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-txn-index.html), [Mission](https://akkhara.engr.tu.ac.th/cn230/project/mission.html) และ[คลังความรู้](https://akkhara.engr.tu.ac.th/cn230/project/knowledge.html)

## การปรับจริงรอบนี้

เพิ่มinventorygraphในscripts/compare_data_models.py: **Process→Exchange→Flow/Unit/Source** และProcess→Location/Source ใช้source-localidentity ไม่สร้างข้อมูลใหม่ Exchangeเก็บpayloadเดิมครบทุกfieldรวมDecimalstring/sourcecolumn/basis/periodnull/allocation/role สิทธิCCBYและsourceURLยังอยู่ ห้ามนำgraphprojectionไปนับเพิ่ม

ตรวจSQL/JSON/graphเทียบobservationIDsแยกFAME/H-FAME×INPUT/OUTPUTรวม4กรณีตรงกันครบ16รายการ คงcorporate8กรณี97รายการเดิม ไม่เปลี่ยนacceptanceหรือค่าunitใด ผลในevidence/model-comparison.json มีhashreportต้นทางและimplementation

ไม่เอาตัวอย่างCypherบนเว็บมารันตรงๆกับข้อมูลจริง เพราะMERGEที่ใช้amount/unitเป็นidentityของrelationshipอาจยุบobservationsต่างsourceได้ รูปแบบของเราคงExchangeidentityก่อน หากนำเข้าNeo4jจริงจะต้องใช้uniquenessconstraints/sourceIDsและตรวจroundtripอีกครั้ง

## แผนปรับระบบถัดไปตามลำดับ

1. **P0 Domain fit:** ทำprocessdetailจาก16inventoryให้basis/boundary/time/allocation/locatorเห็นครบ แล้วตัดสินขอบเขตที่นำเสนอจากsourceจริง ไม่เดาตัวเลขโรงกลั่นเพื่อให้ตรงตัวอย่างdiesel
2. **P0 Trace contract:** สร้างreadable source-ID crosswalkที่versionedและตรวจไม่ชนกัน คงhash/PKเดิม ไม่เปลี่ยนpolicy/releaseเงียบๆ
3. **P1 Neo4jจริง:** เตรียมprojectionCSV/Cypherที่preserveexchangeIDและทดลองlocalแยกฐานเมื่อทำงานชิ้นนี้ ไม่เพิ่มengineลงproductionก่อนมีusecaseและผลตรวจ
4. **P1 Query relevance:** queryprocess/direction/flow/unit/source/basisให้ตอบคำถามโดเมนก่อนbenchmarkเพิ่มเติม แยกderivedratioที่ไม่มีหลักฐานเป็นunsupported
5. **P1 Interface:** ปรับinventoryprocessviewให้ทำworkflowอ่านบริบท→รายการ→traceได้ โดยไม่ทำให้statisticsดูเป็นproductLCI
6. **Infrastructure:** คงprivateEC2/S3ที่ตรวจแล้ว ข้อมูลใหม่/สิทธิ/HTTPSaccesscontrolเป็นคนละงานกับการปิดdomainfit

**ไม่ทำในรอบนี้:** SRS/Memo/slide/CSVส่งแต่ละM,วิดีโอpeerreview,การส่งงาน,รายชื่อ/consent/contribution/ลายเซ็น ไม่ปรับวันส่งที่ยังDraftหรือเดาช่องทางTeams/Formที่ขัดกัน ดูcourse-project-review-2026-10-27.mdเฉพาะเมื่อกลับมาทำเรื่องส่งงาน

ตรวจซ้ำและการปรับระบบล่าสุด: [27 October recheck](final-project-recheck-2026-10-27.md)
