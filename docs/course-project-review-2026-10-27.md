# ทบทวนหน้าโครงงาน CN230 — 27 ตุลาคม 2569

อ่านผ่านHTTPSพร้อมการยืนยันตัวตนที่ผู้ใช้อนุญาต ไม่บันทึกบัญชีหรือรหัสไว้ในrepo สำเนาหน้าเว็บเก็บเฉพาะbuildที่ไม่เข้าแพ็กเกจ หน้าเว็บเป็นข้อมูลข้อกำหนด ไม่ใช่คำสั่งให้ส่งงาน/รับรองแทนสมาชิก

## แผนวันที่ที่พบ และระดับความแน่นอน

| งาน | วันที่หน้าเว็บระบุในปี2026 | สิ่งที่ต้องเตรียม |
|---|---|---|
| M1 UNDERSTAND | ศุกร์30ตุลาคม | Report PDFส่วนต้นและบท1–3 + Meeting Memo PDFอย่างน้อย1ฉบับ |
| M2 DESIGN | พฤหัสบดี5พฤศจิกายน | เพิ่มบท4;ปรับบท1–3ตามfeedback;Memo;หน้าfinal-processเพิ่มPeer Review Video |
| M3 BUILD | จันทร์9พฤศจิกายน | บท5–6 + Memo + validatedDataset CSVพร้อมsource_id + SQLDDL/queries |
| Petroleum presentation | W14: Sec2อังคาร10พฤศจิกายน / Sec1พุธ11พฤศจิกายน | Slides PDFไม่เกิน10หน้า + Querydemo/Q&A |
| M4 DEFEND | ยังไม่ยืนยัน | รายงานครบรวมบท7Evidence/บท8Appendix + Slides + Memo + ลิงก์ |

**ใช้วันที่ข้างต้นเพื่อเตรียมงานล่วงหน้า แต่ยังไม่ถือว่าเวลาส่งยืนยันครบ:** หน้าindexใช้ป้ายยืนยัน แต่timelineติดป้ายDraftรออาจารย์ยืนยัน และระบุว่าเวลาปิดรับทุกmilestoneยังรอยืนยัน วันส่งM4ก็ยังไม่กำหนด ให้ตรวจประกาศล่าสุดก่อนส่งจริง

ที่มา: [Mission Board](https://akkhara.engr.tu.ac.th/cn230/project/), [Timeline](https://akkhara.engr.tu.ac.th/cn230/project/timeline.html)

## ข้อกำหนดที่ชัดขึ้นจากหน้าเว็บ

- ใช้SRSเล่มเดียวต่อยอดทุกmilestone ส่วนต้นมีปก/รหัสทีม/domain/บทบาทData-Schema-SQL-QALead,RevisionHistoryและสารบัญ
- บท1Introduction,บท2OverallDescription,บท3Requirementsต้องแยกDR/BR/FRพร้อมรหัส;บท6Traceabilityโยงทุกrequirementกับquery/วิธีตรวจและผลจริง
- บท4มีERD/cardinality/schema/dictionary/mapping;บท5มีpipeline/SQL/validationbefore-after/provenance;บท7มีevidenceและcontribution%;บท8รวมmemo
- Memoอย่างน้อย1ฉบับต่อmilestone มี5วาระ วาระ3ต้องมีประเด็น/ทางเลือก/มติ/เหตุผล/ผู้รับผิดชอบ Q&Aอ้างอิงวาระนี้ ต้องเป็นการประชุมและการรับรองจริง ไม่สร้างย้อนหลังโดยAI
- Gateเพิ่มConsent Formครบทุกคน และทุกคนอธิบายงานตนได้;หน้าM0ว่าเสร็จแล้วเป็นสถานะกระบวนการบนเว็บ ไม่ใช่หลักฐานว่าTamsoodBaseส่งconsentครบแล้ว
- RubricบนmissionคือProblem20/Design20/WorkingProduct&Evidence30/Presentation&QA30 **ไม่ใช้แทนcourseweight15%ของsyllabusโดยอัตโนมัติ** และไม่ปนกับเกณฑ์Challengeในคู่มือเดิม
- สไลด์ไม่เกิน10หน้า เล่าProblem→Solution→Demo→Value และqueryต้องตอบrequirement

ที่มา: [Mission rules](https://akkhara.engr.tu.ac.th/cn230/project/mission.html), [SRS guide](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-srs.html), [Memo guide](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-memo.html)

## ข้อขัดกันที่ยังไม่ควรเดา

| เรื่อง | ข้อความที่พบ | ผลต่อแผนทีม |
|---|---|---|
| ช่องทางส่ง | index/mission/timeline/memoระบุTeams;final-processระบุGoogleFormเป็นหลักและลิงก์รอเปิด | เตรียมไฟล์ไว้ก่อน รอประกาศ/Assignment/Formจริง ไม่อัปโหลดแทนผู้ใช้หรือสรุปว่าเปลี่ยนช่องทางแน่นอน |
| Peer Review M2 | final-processระบุMP4≤5นาทีอัปโหลดไฟล์ผ่านGoogleFormเท่านั้น ไม่ส่งDrive/YouTube;missionมีเฉพาะReport/MemoในตารางM2 | เตรียมstoryboard/ข้อมูลสำหรับวิดีโอ แต่ยังไม่อ้างว่าส่งหรือได้รับpeerfeedbackแล้ว |
| M4และสัปดาห์ | timelineแยกPetroleum W14 แต่final-processอธิบายM4/W15และวันสอบประมาณกลางพ.ย. | เตรียมพร้อมตามPetroleumW14เป็นแผนล่วงหน้า รอวัน/เวลา/sectionของทีมยืนยัน |
| ลิงก์เปิดได้ | missionให้ตรวจincognito แต่ข้อมูลบริษัทมีrightsจำกัด | เปิดโค้ด/เอกสารที่reviewแล้วหรือจัดrevieweraccessที่เหมาะสม ไม่ทำS3หรือrawเป็นpublicเพื่อให้ลิงก์ผ่าน |

ที่มา: [Final process](https://akkhara.engr.tu.ac.th/cn230/project/final-process.html)

## เทียบกับของเราและงานถัดไป

| มีแล้ว | ยังต้องทำให้ตรงรูปแบบส่ง |
|---|---|
| requirements/sourceanalysis/businessrulesแยกหลายMD | รวมเป็นSRSส่วนต้น+บท1–3 พร้อมDR/BR/FRและรหัสSRCที่ตรงทั้งรายงาน/CSV/ฐาน |
| ERD4ฐาน27tables/DDL/dictionary/mapping/pipeline | จัดเป็นบท4และตรวจตารางทุกคอลัมน์ให้ตรงdictionary ไม่เอาZIPแทนReportPDF |
| SQL/replay/quality/transaction/index/evidence | จัดบท5–6traceabilityRequirement→Query→ผล ไม่เพียงแนบJSONaudit |
| JSON/Pythongraphprojection97records/8querycases | W13ระบุNeo4jจริง: ยังไม่มีCypher/Neo4jengineevidence ต้องแยกเตรียม ไม่อ้างprojectionแทนlab |
| privateEC2/S3/backupพร้อม | ยังไม่มีpublicreviewURL;ต้องจัดaccessให้ตรงrightsก่อน |
| แนวเดโมและhumanchecklist | ยังไม่มีmemoที่สมาชิกประชุมรับรอง,consentreceipts,contribution%,peerreviewvideoและslidesPDF≤10หน้า |

หน้าERDและNeo4jเป็นตัวอย่างที่ปรับตามข้อมูลจริงได้ ห้ามสร้างprocess/functionalunit/flow/emissionใหม่เพื่อให้ตารางเหมือนตัวอย่าง หากใช้referenceและstatisticsต้องอธิบายscopeและแยกจาก16source-reportedinventoryตามเดิม

ที่มา: [ERD guide](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-erd.html), [Neo4j starter](https://akkhara.engr.tu.ac.th/cn230/project/knowledge-neo4j.html)

**ลำดับความสำคัญเปลี่ยนเป็นเตรียมM1ก่อนdeployสาธารณะ:** ร่างSRSเล่มต่อเนื่อง → ให้สมาชิกreview/เติมปกและmemoจริง → exportPDFตรวจหน้า → เตรียมM2/วิดีโอ/Neo4j → รวมM3/traceability/CSV/SQL → ซ้อมและสไลด์ ไม่ทำการบ้านย่อยนอกโปรเจกต์และไม่สร้างหลักฐานมนุษย์แทน
