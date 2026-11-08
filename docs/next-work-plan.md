## สถานะรับช่วงล่าสุด 9 พฤศจิกายน 2569

เริ่มที่ [รายการรับช่วงปัจจุบัน](TEAMMATE_NEXT_STEPS_TH.md), `docs/tasks.json` และท้าย PROJECT_STATE.md ก่อนอ่านแผนเก่าด้านล่าง DMF/NSO/RAG/MySQL/Neo4j lab ในเครื่องใหม่ตรวจแล้ว; Corporate กู้และตรวจ 101 รายการครบทุกช่องพร้อม constraint/rollback แล้ว และ HTTP ข้อมูลจริง 144 checks ผ่าน ส่วน EPPO/DOM ต้นฉบับ หลักฐาน LCI และ human review ยังเปิด งานรับช่วงเตรียมส่งผ่าน branch `codex/teammate-runtime-handoff-2026-11-09` ให้ตรวจสถานะ commit/push จาก Git จริง รอบนี้ไม่ deploy หรือทำรายงาน/สไลด์เพิ่ม

## แผนเดิม 30 ตุลาคม 2569

อ่าน [แผนแก้ตามคำวิจารณ์12ข้อ](expert-review-action-plan.md) และ [ข้อค้างปัจจุบัน](remaining-work-2026-10-30.md) ก่อน ข้อความด้านล่างเป็นประวัติและเกณฑ์เดิม;Vercelเผยแพร่แล้ว/EC2MySQLมีหลักฐานแล้ว/S3ไม่ใช่รอbucket/Neo4jlabจริงผ่านแล้ว SRS0.5ยังรอทีมรับรอง อ่าน PROJECT_STATE.md สำหรับหลักฐานล่าสุด

คำสั่งล่าสุด28ตุลาคม: ผู้ใช้ให้ทำSRSละเอียดต่อหลังโควตารีเซ็ต และตรวจข้อมูลทุกobservation/fieldไม่สุ่ม แก้bugพร้อมหลักฐาน ห้ามอ้าง145/273ว่าเป็นครบcross-source ข้อความพักSRSก่อนหน้าถูกแทนโดยคำสั่งนี้

28ตุลาคม: พักSRSรอผู้ใช้และพักโดเมนถาวร;Neo4jengine16รายการผ่าน;cross-source27/273 ดูneo4j-engine-experiment.mdและcross-source-progress-2026-10-28.md

最新แผนปัจจุบัน: [12กลุ่มงานก่อนFinal](final-gap-plan.md) — ใช้รายการนี้เป็นเกณฑ์ปิดงานและทำตามลำดับ ไม่ใช้จำนวนtaskเก่าเป็นเปอร์เซ็นต์สำเร็จ

# แผนงานต่อจนพร้อมส่งและพร้อม deploy

**คำสั่งล่าสุด27ตุลาคม (แทนคำสั่งพักก่อนหน้า):** ผู้ใช้ให้ทำ SRS และงานส่ง Final ต่อ พร้อมพัฒนาเว็บและเตรียม deploy ตลอดกระบวนการ ใช้ docs/submission/FINAL_DELIVERY_PLAN.md และ SRS.md เป็นแผนปัจจุบัน T55 กลับ IN_PROGRESS; งานมนุษย์ต้องมีหลักฐานจริง ไม่แต่ง memo/consent/contribution

**ลำดับล่าสุด27ตุลาคม:** หน้าโครงงานระบุเตรียมM1วันที่30ต.ค.(timelineยังDraft/เวลาปิดรับรอยืนยัน) ให้ร่างSRSส่วนต้น+บท1–3ก่อนงานpublicdeploy สมาชิกต้องทำmemo/consentจริง ส่วนM2เพิ่มPeerReviewMP4≤5นาทีและNeo4jตามแผนW13 ดูcourse-project-review-2026-10-27.mdเพื่อไม่ปนข้อกำหนดที่แต่ละหน้าขัดกัน

อัปเดต25ตุลาคม2569 ใช้ร่วมกับtasks.json งานแต่ละชิ้นต้องมีผลตรวจจริง ไม่ถือจำนวนtaskเป็นเปอร์เซ็นต์สำเร็จหรือคะแนนแข่งขัน

อัปเดต26ตุลาคม: **T51–T53เสร็จแล้ว** S3permissionแก้โดยเจ้าของ,EC2activecdc51c36b5356c41พร้อมS3envถาวร,stage/active16routesผ่าน,backuparchive38membersdownloadhashตรง,rollbackpreflightผ่านและคงรุ่นเก่าไว้ Testsล่าสุด100ผ่าน สิ่งที่เหลือด้านdeployคือdomain/HTTPS/accesscontrol/frontendpublicorigin ไม่ใช่รอbucket/roleแล้ว ดูPRIVATE_BACKEND_OPERATIONS_TH.md

ผลรอบนี้: **T45–T48เสร็จแล้ว** tests93ผ่านไม่มีskip, browser503→200กู้หน้าได้, Dockerrelease0441f968c64f7c61ผ่าน16routes, modelprojection97records/8queriesตรงกัน และมีwalkthroughแล้ว Graphเป็นPythontraversalในเครื่อง ยังไม่ใช่Neo4j/MongoDBengine ข้างล่างคงลำดับและเกณฑ์ตรวจไว้เป็นหลักฐาน งานค้างจริงคือ5–7

| ลำดับ | งาน | จบเมื่อ / ขอบเขต |
|---|---|---|
| 1 — T45 | แก้หน้าเว็บจำผลโหลดล้มเหลวเป็นสำเร็จ | กลับเข้าหน้าแล้วลองใหม่ได้, pendingไม่ยิงซ้ำ, successcache, retryไม่เพิ่มoptions/rowsซ้ำ; deterministic testsและbrowser503→success |
| 2 — T46 | ตรวจแพ็กเกจหลังแก้เว็บ | frontendallowlistและbackendimageรุ่นใหม่ผ่านroutes;เก็บhash/image/rollbacktarget ไม่สลับEC2หรือเปิดpublic |
| 3 — T47 | เตรียม modern-model experiment จากข้อมูลเดิม | ออกแบบgraph/document projectionที่คงidentity/source/status/rights เปรียบเทียบqueryกับrelational;ทดลองengineเฉพาะlocalแยกเมื่อพร้อม ไม่เพิ่มtechnologyในproductionเพียงให้ครบชื่อ |
| 4 — T48 | ชุดซ้อมส่งงานและตรวจรับ | walkthroughพร้อมตัวอย่างaccepted/hold/reject,คำสั่งSQL,expectedresultsตามrelease,วิธีเปิดsourceและข้อจำกัด;ไม่กรอกผลซ้อมแทนคน |
| 5 — T30 | ขยายcross-sourcecomparison | ปัจจุบัน15/273;เพิ่มเฉพาะหลักฐานใหม่ที่เวลา/หน่วย/scopeตรงกัน ไม่วนsourceเดิมหรือเพิ่มจำนวนเพื่อปั่นยอด |
| 6 — เตรียมจริงเมื่อมีข้อมูล | S3และHTTPS/frontend | รอbucket/region/role;กำหนดdomain/accesscontrolให้เหมาะกับสิทธิข้อมูล;ทดสอบprivateก่อน;ไม่แตะGinder/Caddyหรือเปิดpublicเอง |
| 7 — T22/T24 | สมาชิกและfinalfreeze | contribution/peerassessment/defenseจริง,deadline/รูปแบบส่งล่าสุดและrightsพร้อม;จึงfreeze ตรวจhashและเจ้าของเลือกpush/ส่งเอง |

## วิธีดำเนินต่อ

ทำ1→2→3→4ตามลำดับ ส่วน5ทำได้เมื่อมีหลักฐานใหม่ ไม่ไล่เพิ่มแหล่งอย่างไร้ขอบเขต งาน6–7ไม่ขัดขวางการพัฒนาlocalที่อิสระ แต่ห้ามอ้างdeploy/ส่งแล้วเมื่อยังไม่เกิดจริง หากเหลือเฉพาะข้อมูลภายนอกหรือการลงมือของคนให้สรุปข้อค้างและหยุดวนทดสอบเดิม

ผลที่มีอยู่แล้ว: source-to-APIreplay,normalizationcandidateแยก,transactionexperimentสำเนาSQLite,คู่มือW01–W15และhandbookalignment ไม่ทำซ้ำเพียงเพราะรอบautomationทำงาน
