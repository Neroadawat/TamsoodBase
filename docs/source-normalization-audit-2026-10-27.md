# ตรวจต้นฉบับ ที่มา และ normalization รอบ Final

27 ตุลาคม 2569 · ตรวจ snapshot ที่ระบบใช้อยู่ ไม่ดาวน์โหลดข้อมูลรุ่นใหม่มาทับ และไม่เปลี่ยนตัวเลข/acceptance/สิทธิ

## ผลเทียบต้นฉบับ

| ชุดที่ใช้ | จำนวนรายการตรวจตรงเซลล์/หลักฐาน | ผล | วิธีตรวจ |
|---|---|---|---|
| DMF candidates | 34,899 | ไม่พบค่าหรือcontextคลาดเคลื่อน | อ่านCSV cp874ตามphysicalendingline เทียบraw value/Decimal/ปีพ.ศ.→ค.ศ./เดือน/พื้นที่/แปลง/กลุ่มแหล่ง/วันผลิต พร้อมhash |
| NSO | 273 | ไม่พบเซลล์หรือปีผิดตำแหน่ง | เปิดCSVตามline/column เทียบsource_row/raw value/amount/yearheaderและhash |
| EPPO | 5,934 | ไม่พบค่า/หน่วย/ปี/เดือน/subjectคลาดเคลื่อน | เปิดCSVตรงline/Quantity และunit/period/CompanyหรือProduct โดยไม่ใช้productionparser |
| งานวิจัย FAME/H-FAME | 16 | ไม่พบค่าหรือcolumnกระบวนการผิด | เปิดDOMtablecaptureตามrow/column เทียบflow/unit/raw/Decimal/processheader/hash |
| รายงานบริษัท | 101 รวม4HOLD | สกัดPDFซ้ำครบ101ค่าตรง | sourcePDFhash/URL/page/textline/yearcolumn;ตรวจraw×scale=scaledแบบDecimalและเทียบAPI/export |
| รวมข้อมูลderivedที่ใช้อยู่ | **41,223** | **ไม่พบmismatchในรายการที่ตรวจ** | มีreadableSourceIDและsourcehash/locatorครบ ผูก13source snapshots |

Pipeline replayยังตรวจ DMF raw34,905แถว/structuralreject6แถว และBHD8เซลล์ที่แยกออก ผลตรงเดิม ไม่มีการย้ายreject/holdเข้าacceptedเพื่อเพิ่มจำนวน

หลักฐานหลัก: `evidence/source-cell-audit.json`, `evidence/pipeline-audit.json`; ledgerรายobservationอยู่ `build/source-cell-audit/ledger.jsonl` (ภายใน ไม่เผยแพร่อัตโนมัติ) ตัวตรวจdirectcellไม่เรียกparserเดิมสำหรับCSV/DOM ส่วนPDFใช้ขั้นre-extractionที่รันจริงในรอบนี้

## คำตอบเรื่องแหล่งที่มาครบไหม

ครบสำหรับ41,223derivedobservationsที่อยู่ในcurrentcontract: ตรวจว่าSourceIDมีในregistry,sourcehashผูกsnapshotที่ใช้จริง,locatorอ่านกลับได้และค่าตรง ไม่ใช่เพียงมีURLไม่ว่าง Candidate sourcesที่ยังไม่ได้acquireไม่ถูกอ้างว่ามีข้อมูลแล้ว

แต่ **ตรงต้นฉบับไม่เท่ากับต้นฉบับถูกต้องทางวิทยาศาสตร์หรือใช้รวมกันได้** การตรวจนี้ไม่รับรองว่าเว็บสดยังมีไฟล์เดิมหรือค่ารุ่นล่าสุด ทุกข้อสรุปผูกกับsnapshot/hashที่ใช้จริง

- DMF: ฐานเวลาย้อนหลังยังUNCONFIRMED จึงยังpending ไม่เดาว่าเป็นrateรายวันแล้วคูณวัน
- Corporate: 97ACCEPTED_REFERENCE/4HOLD_CONTEXT;ขอบเขตองค์กรไม่ใช่productLCI;สิทธิredistributionยังNOT_CLEARED
- NSO: เทียบcross-source15/273;อีก258ยังไม่เทียบ ไม่เรียกrepublicationว่าการวัดอิสระ
- Inventory: หลักฐานต้นทางเป็นrenderedDOMและvisibletext ไม่ใช่originalHTTP/PDFbytes;ปีวัดไม่ระบุและไม่ใช่fullLCI

## ตรวจ normalization / keys / integrity

- ฐานSQLite7ไฟล์ (DMF/reference/NSO/EPPO/inventory/สองcandidate) integrity_checkผ่านและforeign_key_checkไม่มีviolation SHA256ก่อน–หลังอ่านไม่เปลี่ยน
- Corporate production metric26แถวใช้context4ค่า ยังคงเก็บdocument_idซ้ำกับcontext_id→document_id จึงยังไม่รับรอง3NFทั้งrelationเดิม Candidateแยกdocument_idออกและJOINผ่านcontext reconstructทุกfieldตรง;catalog101/accepted97ตรงและsourceไม่เปลี่ยน
- Flow/Unitcandidateแยกsource-localidentity คง16payload/typedjoin,15flows,4units,2processes;unknownflow_type/compartmentคงNULL ไม่สร้างfactsใหม่จากการjoin
- SupplementalDDLใหม่ตรวจconstraint direction/roleผ่านMySQLlabและfreshload NSO273/inventory16 แต่ไม่ได้ALTERฐานถาวร จึงไม่อ้างว่าconstraintsใหม่มีอยู่ทุกruntime
- EPPOมีsnapshot→unitในชุดปัจจุบันและpayloadเก็บsourcefieldซ้ำโดยตั้งใจ ต้องแยกauditrawกับtypedmodel และไม่ใช้hashPKเป็นเหตุอ้างว่าเป็นBCNF/5NF
- ยังไม่มีMVD/JDbusinessrulesครบทุกrelation จึงไม่รับรอง4NF/5NFทั้งระบบ ไม่แยกProcess/Flow/Sourceเป็นคู่แล้วสร้างcombinationsที่ต้นทางไม่มี

หลักฐาน: `evidence/storage-integrity-2026-10-27.json`, `evidence/normalization-audit.json`, `evidence/inventory-candidate.json` และ `docs/normalization-audit.md`

## ข้อผิดพลาดจริงที่แก้เพิ่ม

HTTPqueryparserเดิมตัดblankparameter เมื่อผู้ใช้ล้างปีEPPO (`year=`) ระบบจึงเลือกdefault2024แทนทุกปี แก้ให้คงblankvalueแล้ว เพิ่มWSGIregressionและตรวจAPIจริง: dataset11_13+yearว่างคืนtotal3,012ตรงreport ไม่เปลี่ยนข้อมูลต้นทาง หลักฐาน `evidence/eppo-empty-year-fix.json`

Fullsuiteหลังแก้ **105testsผ่าน**;ข้อมูลไม่ถูกแก้เพื่อให้testผ่าน การแก้ตัวกรองต้องใช้backendreleaseใหม่ แยกจากผลsourceauditซึ่งไม่มีmismatch
