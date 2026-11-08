## ไฟล์ร่างล่าสุด27ตุลาคม

ดู output/pdf/TamsoodBase-SRS-review.pdf,output/pdf/TamsoodBase-final-slides-review.pdf และ output/presentations/TamsoodBase-final-review.pptx;ชุดเอกสารoutput/final-reviewแยกข้อมูลภายในออกจากเอกสาร ยังต้องteamreviewและไม่ใช่ส่งแล้ว รายละเอียดSourceIDอยู่source-contract.md;ข้อมูลสมาชิกใช้MEMBER_INPUTS.md

# ชุดหลักฐานโครงงาน CN230 × MTEC

**ข้อกำหนดเว็บที่ตรวจ27ตุลาคม:** อ่าน[course-project-review-2026-10-27.md](../course-project-review-2026-10-27.md)ก่อนใช้ชุดนี้ส่งจริง ต้องรวมเป็นSRSเล่มเดียวและส่งReport/Memoเป็นPDFตามmilestone ZIPนี้ยังเป็นชุดหลักฐาน ไม่ใช่รายงานฉบับส่ง มีconsent/PeerReviewMP4≤5นาที/slides≤10หน้าเพิ่มในแผน วันที่บางหน้ามีDraftและช่องทางTeams/Formยังขัดกัน

สถานะ25ตุลาคม2569: **ชุดเตรียมตรวจและนำเสนอ ยังไม่ใช่ final submission** จากคู่มือภาพถ่ายหน้า15–17 และsyllabusหน้า3–6 งานต้องมีUNDERSTAND/DESIGN/BUILD/DEFEND ไม่ได้กำหนดให้ส่งเฉพาะเว็บ

เริ่มอ่านไฟล์นี้ แล้วเปิดภาพในโฟลเดอร์ `diagrams/` ของ ZIP ที่สร้างโดย `scripts/build_submission_evidence.py` ในrepoภาพอยู่ `build/submission-evidence/diagrams/` ทุกERDสร้างจากDDLปัจจุบัน ไม่ใช้ภาพtemplateLCIแทนschemaที่ทำจริง

## รายการส่งกับไฟล์หลักฐาน

| หมวด | สิ่งที่ต้องเตรียมตามเอกสาร | เปิดไฟล์ |
|---|---|---|
| UNDERSTAND | โจทย์/ขอบเขต/ผู้ใช้/requirements/business rules | [requirements](../requirements.md), [นโยบายทีม](../team-data-policy.md) |
| UNDERSTAND | แหล่งข้อมูล เจ้าของ ที่มา เวลาเข้าถึง ชนิด สิทธิ สถานะ | [Source Registry](../source-registry.csv), [source use](../source-use-notice.md) |
| DESIGN | ERD/cardinality/identity/เหตุผลออกแบบ | corporate-erd,dmf-erd,supplemental-erd,eppo-erd ในdiagrams; [ดัชนีแบบจำลอง](../dataset-model-index.md) |
| DESIGN | Relational schema/PK/FK/UNIQUE/CHECK/datatype | `sql/mysql/reusable-schema.sql`, `full-schema.sql`, `supplemental-schema.sql`, `eppo-schema.sql` จากrootZIP |
| DESIGN | Data Dictionary | [DMF](../data-dictionary.md), [MySQL DMF](../mysql-full.md), [corporate](../reusable-model.md), [supplemental](../supplemental-mysql.md), [EPPO](../eppo-source.md) |
| DESIGN | Source-to-canonical mapping/transform/validation/evidence | [mappingและกฎรวมสำหรับตรวจ](mapping-validation.md), เอกสารแหล่งที่ลิงก์ในนั้น |
| BUILD | Extraction pipeline/raw→staging→mapping→validated products | pipeline.png/svg ในdiagrams, [pipeline audit](../pipeline-audit.md), `evidence/pipeline-audit.json` |
| BUILD | Database/SQL/query results/constraints | schemaและqueriesในsql/mysql, `evidence/live-mysql-audit.json`, `normalization-mysql.json` |
| BUILD | Data quality/accepted/reject/duplicate/provenance | `evidence/dmf-quality-2026-10-22.json`, `dmf-review-2026-10-22.json`, `reference-scorecard.json`, `system-integrity-followup.json` |
| BUILD | Normalization/FD/lossless/index/transaction evidence | [Normalization](../normalization-audit.md), `evidence/normalization-audit.json`, `sql-performance.json`, `transaction-audit.json` |
| BUILD | Reproduce/backup/export/restore/environment | rootREADME, [reference model](../reusable-model.md), `evidence/reference-package-verification.json`; DB/rawไม่รวมในZIPหลักฐานนี้ |
| BUILD | Modern model selection | [เปรียบเทียบแบบจำลอง](../data-model-selection.md), `evidence/model-comparison.json`; ไม่อ้างว่ารันNeo4j/MongoDB |
| DEFEND | Demoพร้อมtraceหนึ่งรายการ/SQL/ข้อจำกัด | [Demo8ขั้น](../demo-and-defense.md), [Walkthrough](../final-walkthrough.md) |
| DEFEND | Team contribution/peerreview/reflection/individual defense | [Team contribution](../team-contribution.md); สมาชิกต้องกรอกงานที่เกิดขึ้นจริง |
| Professional | AI disclosure/rights/limitations | team-contribution.mdส่วนAI-assisted; [ข้อจำกัดและสถานะ](status-and-limitations.md) |
| ก่อนส่ง | Coverสมาชิก/รหัส/หัวหน้ารับรอง/deadline/ชื่อไฟล์ | [ข้อมูลที่เจ้าของต้องเติม](human-final-checklist.md) ไม่ใส่ชื่อหรือลายเซ็นแทน |

## ลำดับเปิดดูภาพ

1. **pipeline.png** — กระบวนการต้นทางถึงผลิตภัณฑ์ข้อมูล แยกทั้ง5ชั้นและสถานะ ไม่บวกทุกแถวเป็นacceptedLCI
2. **corporate-erd.png** — modelหลักของreference97/hold4: publisher/document/context/unit/metric/observation/review/release/issues
3. **dmf-erd.png** — MySQLresearchที่รักษาraw/snapshot/context/observations/reject/duplicate review
4. **supplemental-erd.png** — NSOและproductinventory แยกsubtypeและreferencebasis
5. **eppo-erd.png** — snapshotกับmonthlyobservationและbusinesskey

PNGใช้แทรกรายงาน/สไลด์ SVGใช้ซูม/พิมพ์ และ`.mmd`ใช้แก้ต่อในเครื่องมือMermaid ส่วนmanifestระบุhashของDDLและไฟล์ทั้งหมด เส้นFKบางเส้นอาจซ้อนกันในoverview ให้ดูFK ledgerใต้ภาพและMermaidเพื่ออ่านคอลัมน์/cardinalityที่แน่นอน

ERDในชุดนี้คือ**MySQL schemaที่ใช้อยู่** ไม่ใช่SQLiteprocessingdiagramทุกตาราง และไม่ใช่normalizedcandidateที่ยังแยกฐาน Candidateแสดงหลักฐานในnormalization-audit.mdอย่างชัดเจน จึงไม่สับสนว่าได้migrateproductionแล้ว

## ใช้แพ็กเกจอย่างไร

- อ่านและตรวจlink/ภาพ/เหตุผลร่วมกับทีมก่อนใส่รายงานหรือสไลด์ ไม่ถือว่าแพ็กเกจนี้แทนการdefenseได้
- หากอาจารย์ต้องการDatabase file/SQLload/dataตัวอย่าง ให้จัดส่งแยกตามสิทธิและข้อกำหนดจริง ZIPนี้จงใจไม่แนบrawPDF/CSV,lectures,SQLiteหรือcredentials
- เลขหน้า/ช่วงข้อมูล/ยอดต่างๆเป็นsnapshotปัจจุบัน ไม่อ้างว่าMTECรับรองหรือทุกชุดนับคะแนนแข่งได้
- ไม่ได้push/ส่งTeams/เผยแพร่ในขั้นนี้

6 November engineering addendum: REVIEW_2026_11_06_ADDENDUM.md covers deployed discovery/transport plus local DB candidates and fresh restore. Existing SRS0.7.1 PDF does not yet include this addendum; no final human approval implied.
