
## สถานะล่าสุดสำหรับเตรียมส่ง — 12 พฤศจิกายน 2569

Snapshot readiness ล่าสุดที่ 2026-11-11T23:36:10Z ผ่าน technical checks 68/68 และ reference release ready แต่ `submission_ready=false`; ยังมี 5 gates ที่ไม่ผ่าน (ข้อกำหนดทางการ, สิทธิแหล่งข้อมูล, domain/units, การรับรองจากทีม/การสอบ และ consent). หลังซิงก์แผน/บอร์ด มีการตรวจซ้ำเวลา 23:39:55Z และยังได้ผล 68/68, reference ready, submission not ready, manifest 797 ไฟล์. Snapshot: `evidence/current-release-readiness-2026-11-12-0634.json`. ผลนี้เป็นการตรวจ artifacts ใน workspace ไม่ใช่การตรวจ live service, การรับรองข้อมูล หรือการตอบรับจาก MTEC.

สถานะ Docker ต้องแยกเครื่อง: Docker Desktop Linux Engine บนเครื่องพัฒนาใช้ได้แล้วและ candidate `9c767ef49301347b` ผ่าน package/build/image smoke แบบ isolated ในเครื่อง; แก้ปัญหา package ที่ขาด `retrieval-scope.json` แล้ว. จากผล image ที่ใช้ RAM 499/512 MiB ปรับ first-install preflight เป็น 832 MiB (512 MiB container ceiling + 320 MiB host reserve); targeted tests ผ่าน แต่ยังไม่ได้รัน installer หรือวัด headroom บน EC2 จริง. หลักฐานอยู่ใน `docs/rag/EC2_PRIVATE_DEPLOYMENT.md`, `evidence/rag-ec2-candidate-build-2026-11-12.json` และ `evidence/rag-ec2-install-memory-headroom-2026-11-12.json`. EC2 ยังเป็นหลักฐาน deployment รุ่นเก่า `1c49e9d40b4b3936`; ไม่ได้ตรวจ EC2 สดหรือ deploy รุ่นใหม่ในรอบนี้. Submission gates 5 ข้อยังค้าง จึงไม่มี Production change.

## สถานะ ณ 10 พฤศจิกายน 2569 (ประวัติ)

SRS ระบบฉบับ Markdown รุ่น 0.7.2 มี PDF ตรวจรูปแบบ 29 หน้า render จาก source hash ปัจจุบันและอ้างอิง `evidence/srs-current-review.json`; เอกสาร SRS M2 สำหรับรายวิชาเป็นอีกไฟล์หนึ่งใน Downloads: บท 1–8, revision 0.3, Word/PDF ขนาด A4 38 หน้า ตรวจภาพแล้วเมื่อ 8 พ.ย. หลักฐาน cross-source ล่าสุดครอบคลุม 169/273 รายการ (exact 141, rounding 24, divergences 4); อีก 104 รายการคงสถานะมีเหตุผลชัดเจน ไม่ถือเป็นค่าที่ผ่านการยืนยันข้ามแหล่ง. เว็บไซต์ public frontend ยังเผยแพร่ที่ `https://tamsoodbase.vercel.app`; dataset API routes ที่ตรวจแล้วปิด anonymous access ด้วย 403 แต่ยังไม่มี authenticated user data path. RAG Preview มีหลักฐานทดสอบสดเฉพาะ 9 พ.ย.; RAG บน Production ยังคงปิดและ endpoint ตอบ 503 ก่อนเรียก Gemini. Eligibility ของกลุ่มผู้ใช้ อายุ/ภูมิภาค และสถานะ billing จริงยังไม่ยืนยัน.

## Release review — 9 พฤศจิกายน 2569 (ประวัติ)

ดู [รายงานตรวจ Release](RELEASE_REVIEW_2026-11-09.md) สำหรับผล ณ วันนั้น: Full test suite ผ่าน 287 tests (7 skipped); reference product ถูก rebuild ตาม policy hash ปัจจุบัน และ package/SQLite/isolated SDK/MySQL clean restore ผ่าน. ผลดังกล่าวเป็นประวัติ ไม่ใช่ readiness ล่าสุด.

## Local release readiness — 10 พฤศจิกายน 2569, 07:19 UTC

`python -m scripts.check_release` ตรวจเวลา 2026-11-10T07:19:19Z: technical pass, `reference_release_ready=true`, `submission_ready=false`; snapshot มี 761 files ก่อนเก็บสำเนารายงาน. Gate ที่ยังไม่ผ่านคือ official requirements (PARTIAL), source rights (PARTIAL), domain and units (PARTIAL), team and defense (UNCONFIRMED), และ consent forms (UNCONFIRMED). หลักฐาน: `evidence/current-release-readiness-2026-11-10-0719.json`. ตรวจซ้ำหลังบันทึกหลักฐานที่ 2026-11-10T07:20:51Z ยืนยัน technical pass และ 762 files โดย gate ไม่เปลี่ยน. การตรวจนี้อ่านไฟล์/snapshot ในเครื่อง ไม่ยืนยัน live Vercel/EC2 หรือแทนการอนุมัติจากคน/ผู้สอน.

RAG มี Preview แบบจำกัดและหลักฐาน live Gemini smoke test เฉพาะ 9 พ.ย.; hotfix รุ่น 10 พ.ย. deploy แล้ว แต่ไม่ได้เปิดการตอบ RAG. Production `/api/rag/ask` ตรวจสดหลัง deploy แล้วตอบ 503 ก่อน Gemini; ไม่ใช่ live answer acceptance. ยังไม่มี independent Thai user acceptance. Production RAG ยังคง HOLD เพราะสิทธิ์ corpus, external-model privacy, rate/cost controls, monitoring/capacity และ rollback ยังไม่มีหลักฐานผ่าน.

**Security follow-up:** anonymous Production probes เมื่อ 10 พ.ย. พบ dataset APIs ตอบข้อมูลโดยไม่มี end-user authentication. หลังทดสอบ Preview มีหลักฐาน post-deploy ว่า hotfix ปิด 15 known dataset/login routes บน `https://tamsoodbase.vercel.app` โดย anonymous requests ได้ 403 และ 0 rows; health, release metadata, หน้าเว็บ และหน้า ask ยังตอบได้. ดู `evidence/production-dataset-api-hotfix-2026-11-10.json` และ T149. การแก้นี้ยังไม่มี user-authenticated dataset path และไม่ได้เคลียร์สิทธิ์เผยแพร่ข้อมูล. ห้ามเรียก upstream Basic Auth ว่า user authentication. Vercel WAF rate-limit ยังไม่ได้ตั้ง; plan/billing/threshold ต้องให้ project owner ตรวจตาม `docs/rag/VERCEL_RATE_LIMITER_RUNBOOK.md` ก่อน.

# แผนจากระบบปัจจุบันถึงส่ง Final

ผู้ใช้อนุญาต27ตุลาคมให้กลับมาทำ SRS และชุดส่งทุก milestone แล้ว ลำดับนี้แทนคำสั่งพักงานเอกสารก่อนหน้า การเตรียมไฟล์ไม่เท่ากับ upload/submit

| ลำดับ | ชิ้นงาน | ทำได้ตอนนี้ | ข้อค้างจริง |
|---|---|---|---|
| 1 | SRS ระบบและเอกสาร M2 | SRS Markdown/PDF 0.7.2 (29 หน้า) และเอกสาร M2 บท 1–8 มีร่างพร้อมตรวจ; หลักฐาน render แยกตาม artifact | สมาชิกตรวจเนื้อหา/ชื่อทีม/บทบาทและรับรองฉบับที่ใช้ส่ง; slides ไม่ได้ rebuild ในรอบนี้ |
| 2 | Requirement→schema→query→evidence | SRS traceability, schema, SQL และ release evidence อยู่ใน repository | ทวน link/version ให้ตรงชุดส่งที่ทีม freeze; ห้ามอ้าง Neo4j/RAG เกินผลจริง |
| 3 | ERD/pipeline/dictionary | มี schema, generator, audit และ review bundle | สร้าง snapshot จาก release ที่เลือกและตรวจภาพ/manifest ก่อนแนบ |
| 4 | Validated dataset CSV + SQL | export แยกตามชั้นข้อมูลและสิทธิ; reference ไม่รวมเป็น LCI | ตรวจ source_id/hash/สิทธิไฟล์ทุกชิ้นและสิทธิของผู้รับก่อนแนบ |
| 5 | Memoอย่างน้อย1ต่อM | ใช้แบบฟอร์ม5วาระจากอาจารย์ | สมาชิกประชุมจริง:ประเด็น/ทางเลือก/มติ/เหตุผล/เจ้าของงาน |
| 6 | Peer review MP4≤5นาที | storyboardด้านล่าง | สมาชิกบันทึกจริง/รับpeerfeedbackจริง;ไม่สร้างผลreview |
| 7 | Slides PDF≤10หน้า | PPTX/PDF review 12 พ.ย. มี 10 หน้า; สไลด์ 9 ตรงกับสถานะ API ที่ตรวจ; ตัวเลขสำคัญบนสไลด์ 3, 4, 7, 8, 10 เทียบหลักฐานแล้ว ดู `evidence/final-slides-2026-11-12.json` และ `evidence/final-slides-quantitative-claim-audit-2026-11-12.json` | สมาชิกยังต้องตรวจสไลด์ 2, 5, 6, ซ้อมและรับรอง; ยังไม่ใช่ฉบับส่ง |
| 8 | Deployment/reviewer access | Public frontend ที่ Vercel มีหลักฐาน deploy; RAG Preview มีการป้องกันและจำกัดชุดข้อมูล; Production RAG ยังปิด | Reviewer access สำหรับ backend ยังต้องยืนยันเส้นทางที่ใช้จริง; RAG Production รอ rights/privacy/UAT/rate-cost/capacity/rollback gates; ห้ามแตะ Ginder/Caddy |
| 9 | Final QA/freeze | มี release manifests, source registry, rights status และ checklist | ตรวจ manifest/hash/secrets/rights/link จากชุดที่จะส่งจริง; team review, consent, deadline และ channel ต้องยืนยัน |
| 10 | ส่งงาน | เตรียมreviewpackage | เจ้าของเลือกช่องทางและตรวจreceipt;ยังไม่ส่งแทน |

## โครงวิดีโอ Peer Review ไม่เกิน5นาที

0:00–0:35 ปัญหาและขอบเขตไทย; 0:35–1:20 requirements/แยกชั้นข้อมูล; 1:20–2:10 ERD/identity/keys; 2:10–3:15 demoหนึ่งค่า→sourceพร้อมunit/basis; 3:15–4:10 validation/hold/reject; 4:10–4:45 limitationและคำถามที่อยากให้peerช่วยตรวจ;4:45–5:00สรุป เก็บfeedbackที่เกิดจริงแยกจากscriptนี้

## โครงสไลด์10หน้า

1 Problem/Thai relevance · 2 Scopeและข้อมูล5ชั้น · 3 Requirements/usecases · 4 Architecture/pipeline · 5 ERD/keys/normalization · 6 Mapping/provenance · 7 Validationพร้อมactualresults · 8 Livequeryและtrace demo · 9 Value/limitations/rights · 10 Contributionsที่รับรองจริง/nextsteps

ทุกกราฟระบุหน่วย/ปี/scope ไม่บวกข้อมูลต่างชั้น ไม่ใช้คะแนนwidget100เป็นคะแนนทีม ไม่อ้างอันดับหรือชนะ

## เกณฑ์จบ

เอกสารกับschema/query/releaseตรงกัน,PDFอ่านได้,ลิงก์reviewerใช้ได้ตามสิทธิ,ไม่มีkey/rawที่สิทธิไม่ชัด,consentและmemoจริงครบ,ทุกคนอธิบายงานได้ แล้วจึงfreeze ไม่ทำเครื่องหมายเสร็จแทนสมาชิก

## สถานะล่าสุดสำหรับเตรียมส่ง — 10 พฤศจิกายน 2569

SRS ระบบ Markdown 0.7.2 สร้าง PDF 29 หน้าและตรวจภาพครบทุกหน้า; ดู `evidence/srs-current-review.json`. เพิ่มความแตกต่างของ data API กับ RAG, เงื่อนไข privacy/provider eligibility, และสถานะ Preview/Production ตามหลักฐานปัจจุบัน. ยังเป็นร่างรอทีมตรวจ; สไลด์ฉบับ review 10 หน้าอัปเดตป้าย SRS เป็น 0.7.2 เท่านั้น; เนื้อหาข้อเท็จจริงอื่นในสไลด์ยังไม่ได้เทียบใหม่กับฐานข้อมูลในรอบนี้ ดู `evidence/final-slides-2026-11-10.json`. ไม่มีการ deploy หรือยืนยัน live service ในงานเอกสารรอบนี้.

## สถานะก่อนหน้า — 8 พฤศจิกายน 2569

SRS Markdown0.7.1เดิมสร้างPDFใหม่27หน้าตรงsourcehashและตรวจภาพแล้ว ดู [ผลตรวจรับช่วง](../explorer-performance-fix-2026-11-08.md) กับ `evidence/srs-current-review.json` ยังเป็นร่างรอทีมรับรอง;slides/PPTXยังไม่ได้rebuildรอบนี้ คงงานข้อมูลสมาชิก/consent/peerreview/finalfreezeจริงไว้ ไม่มีการส่งงานหรือรับรองfullLCI ข้อความรุ่นเก่าในตารางถัดไปเป็นประวัติ

## สถานะเดิม 30 ตุลาคม 2569

SRS0.5/PDF21หน้าเป็นร่างรอทีมตรวจ;ข้อมูลต้นน้ำ42และconversion16แยกกัน เว็บเผยแพร่แล้ว ดู [แผน12ข้อ](../expert-review-action-plan.md) และ PROJECT_STATE.md ก่อนใช้ตัวเลข/รุ่นในประวัติด้านล่าง ไม่ได้ส่งFinalหรือรับรองfullLCIแล้ว

# แผนจากระบบปัจจุบันถึงส่ง Final

ผู้ใช้อนุญาต27ตุลาคมให้กลับมาทำ SRS และชุดส่งทุก milestone แล้ว ลำดับนี้แทนคำสั่งพักงานเอกสารก่อนหน้า การเตรียมไฟล์ไม่เท่ากับ upload/submit

| ลำดับ | ชิ้นงาน | ทำได้ตอนนี้ | ข้อค้างจริง |
|---|---|---|---|
| 1 | SRSเล่มต่อเนื่องบท1–8 | SRS0.4 PDF19หน้าและMDมีDR/BR/FR/NFR/traceability;renderตรวจแล้ว | ข้อมูลทีมและteamreviewจริง |
| 2 | Requirement→schema→query→evidence | matrixบท6และDDL4ชุด | source-IDcrosswalk/ตรวจdomainเพิ่มตามหลักฐาน |
| 3 | ERD/pipeline/dictionary | generatorและreviewbundleเดิม | freezeจากDDL/releaseที่ส่งจริงแล้วrenderตรวจใหม่ |
| 4 | Validated dataset CSV + SQL | เลือกexportตามชั้นและสิทธิ;ไม่ปน97referenceเป็นLCI | ตรวจsource_idทุกexportและสิทธิผู้รับก่อนแนบ |
| 5 | Memoอย่างน้อย1ต่อM | ใช้แบบฟอร์ม5วาระจากอาจารย์ | สมาชิกประชุมจริง:ประเด็น/ทางเลือก/มติ/เหตุผล/เจ้าของงาน |
| 6 | Peer review MP4≤5นาที | storyboardด้านล่าง | สมาชิกบันทึกจริง/รับpeerfeedbackจริง;ไม่สร้างผลreview |
| 7 | Slides PDF≤10หน้า | PPTX/PDF review 12 พ.ย. มี 10 หน้า; สไลด์ 9 ตรงกับสถานะ API ที่ตรวจ; ตัวเลขสำคัญบนสไลด์ 3, 4, 7, 8, 10 เทียบหลักฐานแล้ว ดู `evidence/final-slides-2026-11-12.json` และ `evidence/final-slides-quantitative-claim-audit-2026-11-12.json` | สมาชิกยังต้องตรวจสไลด์ 2, 5, 6, ซ้อมและรับรอง; ยังไม่ใช่ฉบับส่ง |
| 8 | Deployment/reviewer access | Vercelpublicfrontend/EC2MySQL/S3restoreพร้อมตามevidence | QuickTunnelยังชั่วคราว;ไม่มีdomain;ผู้ใช้ให้browserไม่loginโดยเก็บupstreamsecretฝั่งserver;ห้ามแตะGinder/Caddy |
| 9 | Final QA/freeze | ตรวจmanifest/hash/secrets/rights/links | teamreview/consent/deadline/channelยืนยันจริง |
| 10 | ส่งงาน | เตรียมreviewpackage | เจ้าของเลือกช่องทางและตรวจreceipt;ยังไม่ส่งแทน |


## ตรวจสไลด์ที่ยังไม่ได้ทวน — 12 พฤศจิกายน 2569

สไลด์ 2, 5 และ 6 ใน review deck ถูกเทียบกับ SRS, mapping, DDL และ inventory evidence แล้ว ไม่พบข้อความที่ต้องแก้; caveat ของ source-local co-product, ช่วงปีที่ไม่ระบุ, allocation ที่ยังค้าง และ Flow/Unit candidate ถูกเก็บใน `evidence/final-slides-scope-schema-provenance-audit-2026-11-12.json`. สไลด์ยังเป็น draft รอทีมตรวจ/สิทธิ์ ไม่มีการส่งงานหรือ deploy.


### ปรับคำตอบ RAG ภาษาไทย — 12 พฤศจิกายน 2569

Prompt contract กำชับให้ตอบตรงก่อน ตัดข้อมูลค้นพบที่ไม่เกี่ยว และอธิบายช่องว่างอย่างสั้น; targeted mock test ผ่าน ดู `evidence/rag-thai-answer-focus-2026-11-12.json`. ยังไม่ใช่ผล live Gemini/UAT และไม่เปลี่ยนสถานะ RAG Production (HOLD).


## Local consistency snapshot หลังปรับ RAG — 12 พฤศจิกายน 2569, 06:14 ICT

`python -X utf8 scripts/check_release.py` ผ่าน technical/reference checks; submission ยังไม่พร้อมและ 5 external/human gates ยังค้าง ดู `evidence/current-release-readiness-2026-11-12-0614.json`. การตรวจเป็น local-only ไม่ใช่ live service verification หรือ MTEC acceptance.


## Security action required before RAG re-enable — 12 พฤศจิกายน 2569

A Gemini credential was disclosed in chat; revocation/replacement is unverified. The owner must rotate it in the provider console and update only the server-side secret store without sharing the new value. See T170 and `evidence/gemini-credential-rotation-gate-2026-11-12.json`; Production RAG remains HOLD.


### Gemini structured-output contract — 12 พฤศจิกายน 2569

GenerateContent request เปลี่ยนจาก field `responseSchema` ที่ deprecate เป็น `responseFormat.text`; mock contract test ผ่าน ดู `evidence/gemini-generatecontent-response-format-review-2026-11-12.json`. ยังไม่มี live provider call; Production RAG คง HOLD.


### ตรวจ consistency หลัง rebuild frontend — 12 พฤศจิกายน 2569, 07:13 ICT

หลังแก้ generated ask page ให้ตรงกับ privacy notice ใน source, local consistency checker ผ่าน 46/46 checks; candidate `70f60e044947b42e16f82a14c69da066c4bba6e500138714dcbb86363b1f0dd1`. Local build ปิด Public RAG/Preview, ใช้ same-origin และไม่รวม private research data. Evidence: `evidence/local-release-consistency-2026-11-12.json`. นี่ไม่ใช่ live verification หรือ approval; submission readiness ยัง false, Production RAG ยังคง HOLD และไม่มีการ deploy.


### Guard ตรวจ ID ซ้ำใน release catalog — 12 พฤศจิกายน 2569, 07:18 ICT

ปิดกรณี fail-open ที่ duplicate manifest decision อาจถูกยุบเหลือแถวอนุมัติท้ายสุด: builder ปฏิเสธ ID ซ้ำใน manifest/source registry/corpus; targeted catalog tests ผ่าน 8/8 และ catalog ปัจจุบันยังมี 0 public-cleared records. Evidence: `evidence/rag-catalog-duplicate-approval-guard-2026-11-12.json`. เป็น local hardening เท่านั้น; สิทธิจริงและ release gates ยังไม่ผ่าน, ไม่มีการ deploy และ Production RAG คง HOLD.


### ซิงก์ ID ของ RAG release manifest — 12 พฤศจิกายน 2569, 07:23 ICT

ซิงก์ manifest ให้มี IDs ตรงกับ active corpus (narrative 10, facts 10), เพิ่มเฉพาะ decision สถานะ `PENDING` และลบ placeholder ที่ไม่อยู่ใน corpus โดยไม่มีการเปลี่ยนสิทธิ. Catalog tests ผ่าน 9/9 และ frontend deployment guard ผ่าน 1/1; public-cleared records = 0 และ release gates ยังคงปิด. Evidence `evidence/rag-corpus-manifest-sync-2026-11-12.json`. ไม่ได้ deploy หรือเรียก Gemini; Production RAG ยังคง HOLD.


### ป้องกันตัวเลขคำตอบที่ไม่มีหน่วย — 12 พฤศจิกายน 2569, 14:54 ICT

Parser ปฏิเสธการตอบตัวเลขโดยตัดหน่วยออก เมื่อหลักฐานที่อ้างรายงานค่านั้นพร้อมหน่วย; targeted `node tests/rag-vercel-api.cjs` ผ่าน. Guard ยังเป็น lexical ไม่ใช่ semantic validation และไม่แทน independent Thai user evaluation. Evidence `evidence/rag-unitless-numeric-answer-guard-2026-11-12.json`; ไม่มี Gemini/Production call และ RAG Production คง HOLD.


### แยก abstention ออกจาก service error ในหน้า RAG — 12 พฤศจิกายน 2569, 15:54 ICT

เมื่อเลขที่ Gemini สร้างไม่ผ่าน grounded-unit guard, route แสดงคำชี้แจงภาษาไทยและไม่อ้างแหล่งกับคำตอบที่ปฏิเสธ; source cards ยังเปิดตรวจได้. Mock route, static UI contract และ build-copy tests ผ่าน. ไม่ได้เรียก Gemini จริง, ตรวจภาพ browser หรือ deploy; Production RAG ยังคง HOLD. Evidence `evidence/rag-grounding-abstention-ux-2026-11-12.json`.


### Local frontend consistency หลัง grounding abstention — 12 พฤศจิกายน 2569, 16:52 ICT

สร้าง static frontend ใหม่โดยปิด RAG/Preview และตรวจ source/build ผ่าน 46/46 local consistency checks; build มี 16 assets และไม่มี private research/raw documents. Evidence `evidence/local-release-consistency-after-grounding-ux-2026-11-12.json`. ไม่ใช่ live verification, browser UAT หรือ submission approval; ไม่มี Production change และ RAG ยังคง HOLD.
