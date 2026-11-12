## 10 พฤศจิกายน 2569 — ตรวจ live connectivity ก่อนต่อฐานข้อมูลเข้ากับ RAG

- จาก Vercel Production ตรวจ `/api/healthz` และ `/api/readyz` ได้ 200 ผ่าน server-side backend proxy; dataset `/api/records` ยัง 403, RAG POST ยัง 503 และ route `/api/rag/search`/`/api/rag/query` ยัง 404.
- บน EC2 API/MySQL/RAG healthy; MySQL release `9f6475ff...c705ea`; API reader มี 6 grants และทุก grant เป็น SELECT หรือ USAGE. RAG อยู่ `tamsoodbase-rag-private` แยกจาก `tamsoodbase-mysql-runtime-private`.
- Aggregate สถานะจาก MySQL แบบไม่ดึง row values: DMF 34,899 `PENDING`; NSO 273 และ EPPO 5,934 `STAGED_SOURCE_VERIFIED`; research inventory 16 `SOURCE_REPORTED_PRODUCT_INVENTORY`; company references 97 ACCEPTED แต่สิทธิ reuse ของเอกสารยังไม่ยืนยัน. ไม่มีชุดใดพิสูจน์ public-clearance ได้ จึงยังห้ามส่งข้อมูลเข้าเว็บ/Gemini.
- หลักฐาน: `evidence/rag-live-backend-connectivity-2026-11-10.json`. การตรวจนี้ยืนยันได้เพียง backend health path ไม่ใช่ RAG-to-DB search. ขั้นถัดไปคือทำ fixed-query/search API พร้อม rights predicates; ต้องคงผลลัพธ์ว่างจนมี source/record release ที่ยืนยันได้. ไม่มี deploy หรือเปลี่ยน production.

## 10 พฤศจิกายน 2569 — ซิงก์เอกสารสถานะเผยแพร่และตรวจ release readiness

- แก้ runbook RAG ให้ระบุ candidate ล่าสุด `51d0ef861af7eb51` แทนรุ่นก่อน และแก้ public distribution profile ให้ไม่สื่อว่า reference routes เปิดอยู่ หลัง Production lockdown ที่พิสูจน์ด้วย post-deploy probe.
- `tests.test_release_consistency` ผ่าน 4 tests; `tests/vercel-proxy-behavior.cjs` และ `tests/rag-vercel-api.cjs` ผ่าน; `git diff --check` ผ่าน (มีเพียง line-ending notices).
- Local `scripts/check_release.py` เวลา 12:15:20Z ผ่าน technical/reference; `submission_ready=false`, 5 gates ค้างเดิม, manifest 775 files. ไม่ใช่ live health check หรือการยืนยันสิทธิ์.
- หลักฐาน deployment lock: `evidence/production-dataset-api-hotfix-2026-11-10.json`; candidate/RAG checks: `evidence/rag-runtime-contract-reconciliation-2026-11-10.json`. ไม่มี Docker build, deploy, DB mutation หรือสิทธิ์เปลี่ยน.

## 10 พฤศจิกายน 2569 — ปรับสัญญา runtime/package ของ RAG ให้ตรงกับ Docker candidate

- เพิ่ม runtime options สำหรับ in-memory startup, configurable bind host, `/healthz`/`/readyz`, exact-Origin check และ optional bearer token; กำหนด feedback path ไปยัง `/tmp` ใน image และรวมโมดูลที่ขาดใน allowlist/Dockerfile. ปรับ smoke ของ image/install ให้ถาม narrative card ที่มีใน corpus จริง แทนสถิติ TSM ที่ไม่มีในชุด 10 cards.
- สร้าง private candidate `51d0ef861af7eb51`; ตรวจ manifest/archive 19 ไฟล์ 252,217,236 bytes และ SHA-256 ZIP `9b627d4440d849badc172e9d8ccf77e3002a60b70693c6c0e68ea9c32a09ba1d`; packaged import ผ่าน. ตอนตรวจครั้งแรกมี `__pycache__` จากคำสั่ง import ปะปนใน build context จึงลบเฉพาะ cache ที่คำสั่งสร้าง แล้ว verifier ผ่าน; archive ไม่เปลี่ยน.
- แก้ `docs/rag/EC2_PRIVATE_DEPLOYMENT.md` ให้ระบุ `4c61c7690224d841` เป็นแพ็กเกจรุ่นก่อน และ `51d0ef861af7eb51` เป็น candidate ปัจจุบันที่ยังไม่ build/deploy.
- ระบุใน `docs/PUBLIC_DISTRIBUTION_PROFILE.md` ว่า projection allowlist รุ่นเดิมไม่ใช่ Production API ที่ใช้งานอยู่: dataset/reference routes ถูกปิด 403 และ RAG 503 ตามหลักฐาน post-deploy ของ 10 พ.ย.
- ตรวจ targeted Python 37 ผ่าน/1 ข้าม; Vercel RAG contract, proxy behavior, shell syntax และ `git diff --check` ผ่าน. Release check 07:56Z technical/reference ผ่าน แต่ submission ยังไม่พร้อม (5 gates ค้าง; manifest 771 files).
- ไม่ได้ build Docker เพราะ Docker Desktop Linux Engine ใช้งานไม่ได้ในเครื่อง (`dockerDesktopLinuxEngine` pipe ไม่มี), ไม่ deploy EC2/Vercel และไม่เปลี่ยน DB/สิทธิข้อมูล. EC2 ยังเป็น release `1c49e9d40b4b3936`; candidate ไม่เชื่อม live MySQL, Vercel HTTPS/auth หรือ fixed-query SQL. หลักฐาน: `evidence/rag-runtime-contract-reconciliation-2026-11-10.json`.

## 10 พฤศจิกายน 2569 — สืบที่มาข้อมูล use-phase ของ FAME ต่อ

ตรวจ metadata ของ Springer chapter ปี 2013 และตัวบท Section 2.3.5: รายงาน emissions ต่อ litre จาก pickup/LDDV และอ้าง Pleanjai (2008), วิทยานิพนธ์ PhD ชื่อ *Integrated environmental assessment of biodiesel from palm oil*. ยังไม่พบ full text ในคลังทางการและไม่ได้ตรวจข้อมูลเครื่องยนต์ต้นฉบับ; จึงคงเป็น `HOLD_CONTEXT` ไม่ scale เป็น FU 1,000 MJ, ไม่ import, ไม่แก้ `CO2e_total`, ไม่ปิด T97/T107. เอกสารและหลักฐาน: `docs/scientific-source-check-2026-11-10-pleanjai-use.md`, `evidence/scientific-source-check-2026-11-10-pleanjai-use.json`.

## 10 พฤศจิกายน 2569 — ตรวจ final readiness ล่าสุด

Final local check after T152 at 2026-11-10T07:27:14.320546Z: technical_pass=true, reference_release_ready=true, submission_ready=false, 68/68 technical checks and 763 manifest files. The intermediate 07:20 run is superseded by this successful check. Five gates remain: official requirements/PARTIAL, source rights/PARTIAL, domain and units/PARTIAL, team and defense/UNCONFIRMED, consent forms/UNCONFIRMED. Evidence: `evidence/current-release-readiness-2026-11-10.json`; T24 and latest review point to this snapshot. No MTEC acceptance, contribution, or consent was invented.

ขั้นถัดไปที่ทำเองได้: ปิดข้อขัดแย้ง/ความครบถ้วนเอกสารและตรวจงาน FAME จากหลักฐานที่มี; rights, ข้อมูลต้นทางที่ยังไม่มี, contribution/defense และ consent ต้องรอผู้เกี่ยวข้อง.

## 10 พฤศจิกายน 2569 — ปิด API ข้อมูลที่เปิด anonymous ใน Production

ก่อนแก้ probe anonymous พบ dataset/login API ตอบ 200 และคืนข้อมูลที่ยัง `PENDING`/`NOT_CLEARED`; ไม่เก็บค่าระเบียนลงหลักฐาน. ทดสอบ Preview ก่อน แล้ว deploy Vercel proxy hotfix ไป `https://tamsoodbase.vercel.app`: 15 dataset/login routes ตอบ 403 และคืน 0 rows; หน้าเว็บ, `/ask.html`, health และ release metadata ยังเปิดได้; RAG POST ตอบ 503 ก่อน Gemini. ตรวจ banner จำกัดข้อมูลบน JS ที่ deploy แล้ว. หลักฐาน: `evidence/production-dataset-api-hotfix-2026-11-10.json`; T149 ปิดเฉพาะ anonymous disclosure.

ยังไม่มี end-user authentication, approved rights, Vercel-to-EC2 path, normalized clearance ledger หรือ fixed-query SQL API. ดัชนี FTS5 41,017 records ยังคง private/local และ public/external-LLM output = 0. Production RAG ยังคง HOLD.

ทบทวนขั้นตอนอัปเกรด/rollback EC2 แบบอ่านไฟล์: พบว่า trap เดิมพยายามคืนรุ่นก่อนแต่ไม่ได้ตรวจผล /readyz/Docker health หรือยืนยัน API/Ginder baseline หลังคืน. เพิ่มการตรวจดังกล่าวและคำเตือน CRITICAL ที่ระบุให้เจ้าของตรวจเครื่อง หาก rollback ไม่ผ่าน. Git Bash syntax check และ mock tests ผ่าน 3 กรณี (คืนรุ่นเดิมได้, readiness ล้มเหลว, API image เปลี่ยน); ไม่ได้รันสคริปต์หรือแตะ EC2. T152 DONE; หลักฐาน `evidence/rag-rollback-verification-hardening-2026-11-10.json`.

รัน offline narrative retrieval evaluation ใหม่กับ corpus ปัจจุบันหลังตรวจพบว่า benchmark hybrid เก่าใช้ narrative hash คนละรุ่น: `scripts/evaluate_rag.py --questions docs/rag/evaluation-questions.json` ผ่าน top-1 12/12 positive cases, ปฏิเสธ 8/8 negative cases, 4 ambiguous ไม่มีคะแนน; 10 cards, current corpus SHA ตรง `public-evidence.json`. ไม่มี Gemini call. แก้ `docs/rag/research-implementation.md` ให้แยกผล narrative ปัจจุบันจาก hybrid benchmark ย้อนหลัง และแก้ตัวเลข Recall/MRR ที่เดิมพิมพ์ไม่ตรง evidence. ข้อจำกัด: คำถามเขียนโดยทีม, ไม่ใช่ answer-quality หรือ human UAT. หลักฐาน: `evidence/rag-current-retrieval-eval-2026-11-10.json`.

ทบทวนเอกสารทางการ Vercel เรื่อง client-IP header: `api/rag/ask.js` ใช้ค่าแรกของ `x-forwarded-for` สำหรับ in-memory Preview limiter; Vercel ระบุว่าเขียนทับ header นี้ด้วย public client IP เพื่อป้องกัน spoofing. ไม่พบเหตุเปลี่ยนโค้ดสำหรับ direct `*.vercel.app` ในรอบนี้ แต่ยังไม่ได้ probe header สด และ limiter ยังไม่ global/durable หรือเป็น cost cap. หากมี proxy หน้า Vercel ต้องทวน header อีกครั้ง. หลักฐาน: `evidence/rag-vercel-forwarded-for-review-2026-11-10.json`; ขั้น rate/cost ยัง WAITING ที่ T151.

## 10 พฤศจิกายน 2569 — ตรวจ API surface ในเครื่องและเพิ่ม Production RAG closed-gate regression

ไล่ inventory `api/` พบสอง route patterns: catch-all `/api/[route]` และ `/api/rag/ask`. เพิ่ม regression ให้ RAG route โดยจำลอง `VERCEL_ENV=production` และ manifest `HOLD_RIGHTS_REVIEW`; route ตอบ 503 ก่อนอ่าน body และไม่เรียก Gemini. `node --check tests/rag-vercel-api.cjs` และ `node tests/rag-vercel-api.cjs` ผ่าน. หลักฐาน local: `evidence/production-api-route-surface-local-2026-11-10.json`. ต่อมา evidence post-deploy ของ T149 ยืนยัน hotfix บน Vercel ปิด 15 dataset/login routes ด้วย 403/0 rows; health, release metadata, home, ask page ยังตอบ และ RAG POST ที่ไม่มีคำถามคง 503 โดยไม่เรียก Gemini. T149 DONE สำหรับการปิด anonymous dataset disclosure เท่านั้น; ไม่มี user-authenticated dataset access. หลักฐาน: `evidence/production-dataset-api-hotfix-2026-11-10.json`.

Local release check ล่าสุดก่อนซิงก์เอกสารผ่าน 68/68 checks ที่ 2026-11-10 07:24 UTC; `reference_release_ready=true`, `submission_ready=false`, manifest 763 files. สถานะนี้อ่านไฟล์ในเครื่อง ไม่ใช่การตรวจสุขภาพ Vercel/EC2. แผน Final แยกหลักฐาน Production hotfix ออกจาก local RAG gate; WAF rate-limit ยังรอเจ้าของตรวจ plan/billing/threshold. หลักฐาน: `evidence/current-release-readiness-2026-11-10.json`, `evidence/production-dataset-api-hotfix-2026-11-10.json` และ `evidence/production-api-route-surface-local-2026-11-10.json`.

## 10 พฤศจิกายน 2569 — เตรียมเกณฑ์ rate limit ของ RAG บน Vercel โดยไม่แก้ Production

ตรวจเอกสาร Vercel WAF ปัจจุบันและเขียน `docs/rag/VERCEL_RATE_LIMITER_RUNBOOK.md`: WAF มี fixed-window limit บนทุกแผน, key IP/JA4 บน Hobby/Pro และ counter แยกตาม region จึงไม่ใช่ global spend cap. เอกสารอัตราปัจจุบันระบุ $0.50 ต่อ 1 ล้าน allowed requests; ตาราง Hobby ระบุ quota 1 ล้าน ส่วน Pro usage-based. เก็บข้อควรตรวจ billing/plan, ขอบเขตเฉพาะ `POST /api/rag/ask`, การทดสอบ 429, analytics และ rollback ไว้ใน runbook. หลักฐาน `evidence/rag-vercel-rate-limit-research-2026-11-10.json`. ไม่มีการเปิดดูบัญชี/configure rule/publish หรือเปลี่ยน Production; T151 คง WAITING จนเจ้าของโครงการยืนยันแผน ค่าใช้จ่าย และ threshold.


## 10 พฤศจิกายน 2569 — ป้องกันเลขหลักใหญ่ชนกันในตัวตรวจ grounding ของ RAG

ระหว่างตรวจ T145 พบว่าตัวตรวจตัวเลขใช้ JavaScript `Number()` ทำให้จำนวนเต็มที่ต่างกันแต่เกินความละเอียดปลอดภัยของ JavaScript อาจถูกปัดเป็นค่าเดียวกัน และผ่านการเทียบกับหลักฐานผิดได้. เปลี่ยนเป็น canonicalize ตัวเลขเป็นข้อความโดยคงทุกหลักไว้; ยังรองรับเลขไทย, comma grouping และรูปทศนิยมที่เท่ากัน. เพิ่ม regression tests: ปฏิเสธคำตอบ `9007199254740992` เมื่อหลักฐานมี `9007199254740993` และยอมรับเลขไทย `๑๐๐๐` เมื่อแหล่งแสดง `1,000.00`. `node tests/rag-vercel-api.cjs` ผ่าน. หลักฐานและ hash: `evidence/rag-numeric-token-precision-2026-11-10.json`; T150 บันทึก DONE ตามขอบเขตเฉพาะนี้.

ข้อจำกัดเดิมยังอยู่: การพบ token ตัวเลขไม่ตรวจหน่วย/ช่วงเวลา/ฐาน/ความหมาย ไม่เช็คจำนวนที่เขียนเป็นคำ และไม่ใช่การตรวจ semantic entailment. ไม่เรียก Gemini จริงและไม่ deploy; Local release gate หลังแก้ T150: technical_pass=True (68/68 checks), reference_release_ready=True, submission_ready=False, manifest 752 files; evidence `evidence/current-release-readiness-2026-11-10.json`. RAG Production ยัง HOLD.

## 10 พฤศจิกายน 2569 — Candidate รายงาน DMF รายเดือนและดัชนี RAG อัปเดต
ดึง HTML/Excel ทางการของมีนาคมและกันยายน 2569 เข้าโฟลเดอร์ ignored `tmp/dmf-refresh-candidate` พร้อม hash โดยไม่แก้ `data/raw`, canonical build, MySQL หรือฐาน production. ตรวจ March CKAN กับ Excel จากผู้เผยแพร่เดียวกัน: 34 area/source-group rows, 170 numeric fields อยู่ในช่วงความละเอียดทศนิยมที่พิมพ์, production days ตรงกัน; พบ `BLOCK` ของน้ำมันและก๊าซ 2 แถวต่างเครื่องหมายขีด (`14A16A`/`14A-16A`) จึงเก็บทั้งคู่และไม่ normalize อัตโนมัติ. นี่เป็นการเทียบรูปแบบข้อมูลผู้เผยแพร่เดียวกัน ไม่ใช่การยืนยันอิสระ. September Excel อ่านได้ 33 detail rows พร้อมหน่วยอัตราต่อวัน, revision 19 ต.ค. 2569, field/block และ sheet-row locators; CKAN CSV ยังจบ มี.ค. 2569.

เพิ่ม `DMF-MONTHLY-2569-03` และ `DMF-MONTHLY-2569-09` ใน `docs/source-registry.csv` ด้วยสถานะ `acquired_pending_review`, `NOT_CLEARED`; เพิ่ม T148 เป็น DONE ในขอบเขตตรวจช่องทางและเก็บ candidate โดยไม่อนุมัติข้อมูล. rebuild catalog/FTS: 22 registry sources, 41,017 FTS docs, integrity `ok`, index internal ค้น “กันยายน” พบ source ใหม่ แต่ public/external-LLM ผลลัพธ์ยัง 0. ชุด RAG database/catalog/scope 24 tests ผ่านหลังแก้ test ที่เดิมล็อก source count เป็น 20; Vercel route contract ผ่านและ public route ยังปิด. หลักฐาน `evidence/dmf-monthly-candidate-2026-11-10.json`, `evidence/rag-private-database-index-2026-11-10.json`.

CKAN ระบุ license label `Open Data Common` แต่ `isopen=false`; source rights และการส่ง Gemini ยังไม่เคลียร์. ไม่ import รายงานใหม่เข้า MySQL, ไม่ deploy, ไม่ส่งข้อมูลออก, และไม่เปลี่ยน Production.


## 10 พฤศจิกายน 2569 — ตรวจ freshness ของข้อมูล DMF และแก้การคำนวณช่วงข้อมูล
การตรวจครั้งก่อนใช้ `MAX(year_ce)` และ `MAX(month)` คนละ aggregate จึงสรุปผิดว่ามีแถว ธ.ค. 2569; ตรวจใหม่ด้วยกลุ่มปี/เดือนเดียวกัน (`GROUP BY year_ce, month ORDER BY year_ce DESC, month DESC`) แล้วไม่พบข้อมูลอนาคต และ latest exact period ของทั้ง 3 CKAN packages คือ 2026-03. ขอโทษสำหรับข้อสรุปก่อนหน้า.

ดึง CKAN metadata/CSV รอบใหม่ไว้เฉพาะ `tmp/dmf-refresh-candidate/20261109T192432Z` โดยไม่รัน pipeline; SHA-256 ของ CSV ทั้งสามไฟล์ตรงกับ snapshot ปัจจุบันทุกชุด จึงไม่มีข้อมูลใหม่จาก CKAN และไม่ได้เปลี่ยน `data/raw`, `build`, MySQL หรือ RAG index. ตรวจหน้า DMF ทางการซึ่งแสดงรายงานรายเดือนถึง ก.ย. 2569 (หน้า ก.ย. ระบุปรับปรุง 19 ต.ค. 2569) จึงบันทึกความต่างของช่องทาง/ชุดข้อมูลเป็นงานค้าง ห้าม merge ข้ามแหล่งหรือเดาหน่วยเวลา. ทะเบียนยังระบุ review/rights pending; candidate ไม่เผยแพร่และไม่ส่งให้ Gemini. หลักฐาน: `evidence/dmf-refresh-check-2026-11-10.json`. ทดสอบซ้ำเฉพาะ `test_rag_database_index`, `test_rag_catalog`, `test_rag_scope` รวม 24 tests ผ่าน และ `node tests/rag-vercel-api.cjs` ผ่านพร้อมยืนยัน public route ปิด. `git diff --check` และ JSON parse ของ evidence/tasks ผ่าน.

# สถานะ TamsoodBase — 28 ตุลาคม 2569

## 10 พฤศจิกายน 2569 — กลับมาทำ RAG ภายใต้เกณฑ์ Final readiness
### ตรวจ secret exposure ใน working tree — 10 พฤศจิกายน 2569
สแกนไฟล์ข้อความใน source/docs/tests/config จำนวน 782 ไฟล์ด้วยรูปแบบ Google AIza, AQ-prefixed และ literal API-key assignments โดยไม่พิมพ์ค่าที่ตรงออกมา: ไม่พบ match ใน scope นี้. พบชื่อไฟล์ `.env.local` ที่ root; ไม่อ่านค่า, `git ls-files` ไม่พบไฟล์ env และ `.gitignore` ละเว้น `.env*`. สแกนนี้ไม่ครอบคลุม raw snapshots, build artifacts หรือประวัติ Git และไม่ยืนยันว่าคีย์ที่เคยวางในแชตยังปลอดภัย; คีย์นั้นยังต้องหมุนแยกต่างหาก. รายละเอียด: `credential_scan` ใน `evidence/rag-readiness-review-2026-11-10.json`.

ผู้ใช้สั่งกลับมาทำแผนค้น/เปิดใช้ RAG อย่างปลอดภัยและให้ Production ได้เฉพาะเมื่อการตรวจครบ จึงเดิน T145 ต่อและกำหนด 5 gates: (1) สิทธิ/รายการ corpus (2) privacy และการส่งข้อมูลให้โมเดลภายนอก (3) rate limit/โควตา/งบ (4) คุณภาพคำตอบและ UAT ภาษาไทยอิสระ (5) deployment/capacity/monitoring/rollback. สร้าง goal ต่อเนื่องและปรับ automation รายชั่วโมงเดิมให้ทำหนึ่ง bounded review ต่อรอบในเธรดนี้.

ตรวจ local working tree ที่มี RAG catalog/provenance builder, API gate บังคับ `geminiConsent` ฝั่ง server และ numeric-query abstention. ผลตรวจรอบนี้: RAG unit/scope/catalog 13 ผ่านไม่มี skip (ใช้ `build/rag-verified-venv`), frontend/release consistency 18 ผ่าน, `node tests/rag-vercel-api.cjs` ผ่าน, frontend build ผ่านโดย `publicRagEnabled=false`, `ragMode=closed`, ไม่มี private research data, catalog check ผ่านแต่ public-cleared records = 0, และ `git diff --check` ผ่าน. หลักฐาน `evidence/rag-readiness-review-2026-11-10.json`.

Production RAG ยัง HOLD: ไม่มี record ที่ผ่าน rights clearance ใน output ปัจจุบัน; external Gemini/privacy, durable global rate/cost controls, independent user evaluation, production ingress/capacity/monitoring และ acceptance/rollback sign-off ยังไม่มีหลักฐานครบ. EC2 RAG มีหลักฐาน deploy private เดิมลงวันที่ 8 พ.ย. (`1c49e9d40b4b3936`) แต่ไม่ได้ probe remote ซ้ำหรือเปลี่ยน service รอบนี้; Vercel public RAG ไม่ได้ deploy/เปิด. ไม่อ้างว่า UI/answer quality ผ่าน user acceptance.

ปรับคำตอบเมื่อถามรวม/เฉลี่ยตัวเลขให้เป็นภาษาไทยตรง ๆ โดยอธิบายว่าแชตชุดนี้ยังไม่มีส่วนคำนวณที่ตรวจหน่วย ช่วงเวลา และที่มา; ไม่เดาตัวเลขและไม่ส่งคำถามดังกล่าวไป Gemini. เพิ่ม assertions ใน `tests/rag-vercel-api.cjs`; ตรวจ route test, `node --check`, closed-mode frontend build และ `git diff --check` ผ่าน. ยังไม่ได้ทดสอบกับผู้ใช้จริงหรือ deploy.

## 9 พฤศจิกายน 2569 — กรอก Ch6.x.1–6.x.5 ในสำเนาเทมเพลต Word
สร้าง `output/m3/CN230-F3-Template-V1_Ch6x_Serving_Layer_filled.docx` จากไฟล์ Downloads; กรอก CSV, กราฟ Neo4j, Qdrant vector index, semantic/multi-hop examples และ requirement traceability ตามหลักฐานจริง. ทำเครื่องหมายชัดว่า Neo4j inventory lab และ Qdrant/RAG เป็นต้นแบบแยกกัน ไม่ใช่ระบบรวมและไม่ใช่ production. ต้นฉบับ Downloads ไม่ถูกแก้; เทียบ package แล้วมีเฉพาะ `word/document.xml` เปลี่ยน. เรนเดอร์ด้วย Microsoft Word และตรวจภาพครบ 3 หน้า; ตารางอยู่ในขอบหน้าและข้อความไม่ทับกัน. เนื้อหาเป็น draft ทางเทคนิค ยังรอทีมพิจารณาตามคำชี้แจงในเทมเพลต.

## 9 พฤศจิกายน 2569 — เติมหลักฐานโปรเจกต์ในร่าง Meeting Memo สำหรับ M3 BUILD
ปรับ `output/m3/S2-G05_W12_A4_M3_Memo.docx` จากหลักฐาน M3 เพิ่มสถานะ CSV 16 source-reported Table 4 rows/31 columns และ Neo4j LOAD CSV + MERGE ที่เทียบฟิลด์ 16/16 แถว, 39 nodes/68 relationships และ 4 process-direction checks ผ่าน (`evidence/neo4j-csv-import-2026-11-09.json`). ตรวจ header เพิ่มพบ CSV ปัจจุบันมี `observation_id`/source locator/hash/license/status แต่ **ไม่มีคอลัมน์ `source_id` ตามข้อกำหนด M3**; ยังต้อง map จาก registry, regenerate และตรวจสิทธิ/manifest ก่อนใช้ส่ง. ระบุว่าเป็น disposable lab ไม่ใช่ production/full LCI; แยกสถานะจริงจากมติประชุม; บันทึกว่า Graph + Semantic Search end-to-end ยังไม่ established และ submission readiness ยัง false. เชื่อมกับ SRS Full Draft rev0.3 และงานอัปเดตบท 5–6 ที่ยังค้าง. ใช้ Memo M2 ที่แนบเป็นรูปแบบ (SHA-256: `5415b8eb0c91ce57c683d13be980d38d7b610bba66daf05b09a965e07da069a4`); Word render 6 หน้า ตรวจภาพครบแล้ว. วัน/เวลา/เลขครั้งและผู้เข้าร่วม M3, มติ, ผู้ทำจริง/ผู้รับผิดชอบ, คำตอบผู้เชี่ยวชาญและการรับรองยังเว้นให้ทีมกรอกตามจริง; รายชื่ออ้างจาก M2 เพื่อยืนยัน. ยังไม่ได้ส่งงาน.

## 9 พฤศจิกายน 2569 — M3 Serving Layer: สร้าง CSV สำหรับ Neo4j จาก LCI subset
ผู้ใช้ถามต่อหัวข้อ 6.x.1 ที่เดิมยังไม่มี CSV จึงเพิ่มตัวส่งออกเฉพาะ inventory ที่ตรวจแล้ว 16 รายการจาก `build/product-inventory/report.json` ไป `build/neo4j-csv/product_inventory.csv` (31 คอลัมน์ เก็บ source locator/hash/license/status) และสคริปต์ `LOAD CSV WITH HEADERS` + `MERGE` สำหรับ Neo4j ใน lab ภายในเครื่อง. ตรวจโหลดกับ Neo4j Community 5.26.32 ใน disposable internal network สำเร็จ: 16/16 observation fields ตรงกับ report, graph 39 nodes/68 relationships ตรงกับ projection, FAME/H-FAME × INPUT/OUTPUT ทั้ง 4 query ตรง CSV. หลักฐาน `evidence/neo4j-csv-import-2026-11-09.json`.

ขอบเขตยังเป็น source-reported Table 4 foreground inventory ไม่ใช่ full lifecycle LCI หรือ production graph; CSV เป็นไฟล์ส่งออกที่สร้างจากรายงาน ไม่ใช่ไฟล์ต้นฉบับ. ไฟล์ CSV อยู่ใน build (local/ignored) เพื่อใช้แนบหรือสร้างใหม่. งานถัดไปสำหรับเอกสาร: กรอก 6.x.1 ด้วยไฟล์นี้และคำอธิบายว่าเป็น derived export; แยก 6.x.2/6.x.3 ตามหลักฐานจริง.

## 9 พฤศจิกายน 2569 — เตรียม RAG เว็บแบบ Vercel-native ตามทางเลือกใช้ฟรี
หลังผู้ใช้เลือกให้ทำ Function บน Vercel เรียก Gemini โดยตรง ปรับ `api/rag/ask.js` จาก proxy ไป EC2 เป็น retrieval ใน Function จาก corpus JSON แล้วเรียก Gemini ด้วย API key ฝั่ง server เท่านั้น; เพิ่ม timeout, ขนาดคำขอ/คำตอบ, same-origin HTTPS check, scope anchors, abstention, และตรวจว่า source IDs ในคำตอบเป็นหลักฐานที่ส่งให้โมเดลจริง. เพิ่ม `vercel.json` ให้ bundle เฉพาะ corpus/manifest ที่ใช้และจำกัดเวลาฟังก์ชัน 30 วินาที; ปรับ build gate ให้ต้องผ่าน external-LLM/privacy และ release criteria ที่เกี่ยวข้องกับสถาปัตยกรรมนี้. หน้า RAG แจ้งว่าคำถามกับข้อความหลักฐานจะถูกส่งให้ Gemini และอธิบายความเสี่ยงโควตาฟรีตามเงื่อนไข Google.

ตรวจ `node --check` สำหรับ API/build script, `node tests/rag-vercel-api.cjs` และ `python -m unittest tests.test_frontend -v` (14 tests ผ่าน). การทดสอบ Gemini ใช้ fetch จำลองเท่านั้น; ไม่เรียก Gemini สด, ไม่ deploy Vercel, ไม่ตั้ง environment/secret, ไม่เปลี่ยน EC2. ต่อมาผู้ใช้ redeploy Vercel Production commit บน `main`; หน้าสถานะเป็น Ready แต่ GET `https://tamsoodbase.vercel.app/ask.html` และ `/api/rag/ask` ยังตอบ 404 แสดงว่าโค้ดที่เตรียมใน working tree ยังไม่ได้อยู่ใน deployment. Route/build ยังคงปิดเพราะ `public-release-manifest.json` ระบุสิทธิ์ corpus และ external LLM เป็น PENDING/false. ยังต้องทำ rights/privacy review, real ingress rate-limit กับ Gemini quotas/spend controls, independent generated-answer UAT, monitoring/capacity และ rollback/production acceptance ก่อนเปิดจริง. รายละเอียด: `docs/rag/PUBLIC_WEB_READINESS.md`.

## 9 พฤศจิกายน 2569 — รับ commit จากเพื่อนเข้ามาใน branch ปัจจุบัน
Fast-forward `codex/share-project-with-teammate` จาก `67db1ad` ถึง `cef3f81` (`codex/teammate-runtime-handoff-2026-11-09`) หลังตรวจรายการเปลี่ยน 127 ไฟล์และ `git diff --check`; รายงานผู้ส่งระบุ targeted 117/118 ผ่านโดยข้าม EPPO integration 1 รายการ, full suite ยังไม่ผ่าน (252 รายการ: failures 2, errors 42, skipped 9) เพราะ artifacts/dependencies ขาดและหลักฐาน NSO เก่าผูก report hash คนละรุ่น. นี่เป็น handoff code/local-review เท่านั้น ไม่มี production change.

นำงานค้างในเครื่องกลับหลัง fast-forward โดยเก็บ `stash@{0}` และ patch สำรองไว้; รวม task state และเอกสารโดยคงทั้งบันทึกรับช่วงกับการอัปเดตล่าสุดของผู้ใช้. RAG ยังคงพักตามคำสั่ง: corpus/scope ใน branch ตรงกันที่ 10 cards, แต่ release manifest ปิด public route; ยังไม่รัน evaluation/deploy ในรอบ pull นี้. Working tree ยังมีงานแก้ค้างและไม่ได้ push.

## 9 พฤศจิกายน 2569 — ปิด cross-source และ SRS draft; พัก RAG ตามคำขอ
ตรวจ `evidence/nso-review-ledger.json` และ `evidence/cross-source-coverage.json`: 273/273 NSO source cells มี audit เดิม, cross-publication comparison 169/273 แบ่งเป็น exact 141, display rounding 24, source divergence 4; อีก 104 มีเหตุผลค้างแจกแจง; derived consistency 18 เป็นการตรวจสูตรภายใน ไม่ใช่ external confirmation; independent measurements verified = 0 และ source values ไม่เปลี่ยน. ปรับ T30 เป็น DONE ตามเกณฑ์ที่ให้รายงานช่องว่างอย่างชัดเจน ไม่ได้อ้างว่าทุก 273 ค่าได้รับการยืนยันอิสระ.

ยืนยันร่าง SRS ระบบ `docs/submission/SRS.md` v0.7.1 กับ `evidence/srs-current-review.json` (PDF review 27 หน้า render จาก Markdown hash ปัจจุบันและตรวจภาพแล้ว) และเอกสาร M2 บท 1–8 ใน Downloads (Word rev0.3, 38 หน้า; Word/PDF render และตรวจรูปแบบตามบันทึกรอบ 8 พ.ย.). ปรับ T55 เป็น DONE ในขอบเขต “ร่างที่จัดทำแล้ว”; team review/sign-off/contribution/final freeze ยังเป็นงานมนุษย์ใน T22/T24/T58.

ผู้ใช้สั่งพัก RAG/evidence-chat ไว้ จึงย้าย T145 เป็น WAITING และจะไม่เปิด public route/deploy/ทำต่อจนกว่าจะสั่งใหม่. อัปเดต final delivery plan ให้ระบุสถานะจริง ณ 9 พ.ย.; `docs/tasks.md` สร้างใหม่จาก `docs/tasks.json`. งานที่ยัง active คือ FAME source gaps, end-to-end final review และ final gate; ไม่แต่งหลักฐานสมาชิก.

ปรับสไลด์ฉบับสำเนา `output/presentations/TamsoodBase-final-review-2026-11-09.pptx` ให้แสดง SRS 0.7.1 โดยคงไฟล์เดิมไว้; ส่งออก PDF 10 หน้าเป็น `output/pdf/TamsoodBase-final-slides-review-2026-11-09.pdf` และตรวจภาพครบ 10 หน้า/เทียบหลักฐานปัจจุบันแล้ว. Hash และขอบเขตตรวจ: `evidence/final-slides-2026-11-09.json`. T58 ยัง active เพราะ ERD/export snapshot ต้อง freeze กับชุดส่งจริงและยังรอสมาชิกตรวจ/ซ้อม; T24 final gate ยังไม่ปิด.

ปิด T61 ในขอบเขตการบันทึก F01–F12 และ UX task-entry เท่านั้น: `docs/final-gap-plan.md` ระบุ workstream ครบ และ `evidence/final-task-entry.json` บันทึก browser check ของ inventory shortcut; ไม่ได้ปิด acceptance workstreams ที่ยังค้างจริง.

## 9 พฤศจิกายน 2569 — เตรียม RAG สำหรับเว็บไซต์โดยคง closed state
เพิ่ม `web/ask.html` ที่ปิดช่องถามไว้จนกว่า build config จะเปิด, `api/rag/ask.js` สำหรับ same-origin HTTPS proxy แบบ fail-closed, shared-token validation ฝั่ง `scripts/rag_retrieve.py`, และ build gate ที่ตรวจ source-rights/release manifest. สร้าง `docs/rag/public-release-manifest.json` และ `docs/rag/PUBLIC_WEB_READINESS.md`; อัปเดต `docs/rag/README.md`. หน้า catalog เปลี่ยน compass/topic emoji เป็น source-desk numbering และเปลี่ยน CTA ให้ไม่สื่อว่าบริการเปิดแล้ว.

เพิ่ม allowlist ใน `.vercelignore` ให้หน้า/stylesheet/API ซ้อน `api/rag/ask.js` ถูกนำเข้า deployment artifact; ก่อนแก้ รายการ ignore จะตัดไฟล์เหล่านี้ออก.

สถานะจริงยังไม่พร้อมเปิด public: EC2 RAG ปัจจุบันเปิดเฉพาะ Docker internal network และ SSH forward; ไม่มี Vercel-to-AWS private route, source rights ของ 8 narrative cards/10 facts ยัง PENDING, rate limiter/production policy ยังไม่มีหลักฐาน, และ capacity/privacy/acceptance gates ยังไม่ผ่าน. Manifest บล็อก public-enabled build โดยตั้งใจ. อ้างอิง `evidence/rag-ec2-deploy.json`, `docs/rag/public-release-manifest.json`, และ `docs/rag/PUBLIC_WEB_READINESS.md`. ไม่ deploy หรือเปลี่ยน Vercel/EC2 ในรอบนี้. ขั้นต่อไป: เคลียร์สิทธิแหล่งข้อมูลและเลือก private network gateway/Vercel plan ก่อนเก็บ evidence ของ gate ที่เหลือ. การตรวจ interactive production, live upstream, mobile และ runtime limits ยังไม่ได้ทำ.

## 9 พฤศจิกายน 2569 — ปรับหน้าหลักและหน้าแชต RAG โดยคงข้อจำกัดความเป็นส่วนตัว
ปรับแคตตาล็อกเป็นโทน editorial/field desk และปรับหน้า RAG ส่วนตัวให้มีตัวอย่างคำถาม ประวัติแสดงเฉพาะในแท็บ สถานะค้น การ์ดอ้างอิงพร้อมตำแหน่ง และคำอธิบายว่าคำถามแต่ละครั้งค้นแยกกัน ส่งเฉพาะคำถามปัจจุบันให้ `/ask`; ไม่เปลี่ยน retrieval/data/deployment และไม่เพิ่มเส้นทาง RAG สาธารณะ. `python scripts/verify_ui_refresh.py` ผ่านการตรวจโครงสร้าง จุดเชื่อมต่อ ขอบเขตข้อมูล การ render แบบปลอดภัย รูปแบบ mobile/reduced-motion และ JavaScript syntax. หลักฐาน: `evidence/rag-ui-refresh.json`.

ตรวจภาพ desktop ด้วย Edge headless และเก็บภาพหน้าแคตตาล็อก/แชตไว้ใน `evidence/ui-refresh/`; แต่ CUA kernel เริ่มไม่ได้และ Edge รายงาน CSS viewport 477 px แม้ขอภาพกว้าง 390 px จึงยังไม่ยืนยัน mobile viewport 390 px หรือการกดส่งคำถามกับ API จริง. ยังไม่ทำ EC2 preflight หรือ deploy; runbook ต้องมี RAM ว่างอย่างน้อย 720 MiB แต่การตรวจวันที่ 8 พ.ย. เคยเห็น 560884 KiB ซึ่งต่ำกว่าเกณฑ์และไม่ใช่ค่าปัจจุบัน. คง RAG ไว้หลัง SSH forward. Gemini API key ที่เคยแปะในแชตควรถูก revoke หากยังใช้งานอยู่.

## 8 พฤศจิกายน 2569 — T144 deploy RAG รุ่น private บน EC2 และตรวจ UX/rollback (เสร็จ)

- แก้บั๊กจากคำถามจริง “CO₂e รู้ได้จากไหน/ต้องคำนวณเองไหม” ซึ่งเคยถูกตอบด้วยยอดลดการปล่อยรายปีของโครงการคนละชนิด; เพิ่มคำอธิบายวิธีคำนวณภาษาไทยจากข้อมูลกิจกรรม × ตัวคูณที่หน่วย/ขอบเขตตรงกัน, เตือนห้ามคูณ GWP ซ้ำถ้า factor เป็น CO₂e อยู่แล้ว และอธิบาย CO₂e ด้วยคำทั่วไป
- เพิ่มหลักฐานวิธีคำนวณจาก GHG Protocol Product Life Cycle Standard sections 8.3.4–8.3.5 และนิยาม IPCC พร้อมลิงก์/locator ทั้งคู่; คงข้อสรุปว่าข้อมูลทีมยังไม่พอคำนวณ CO₂e ต่อลิตร และไม่สร้างค่ารวม
- เพิ่มตัวอย่างคำถามบนหน้าเดโมและกรณี regression สองคำถาม; ปรับคำค้นหนึ่ง alias ที่ทำให้ “วิธีปลูกกล้วยไม้ในกระถาง” ไปติดผลค้นผิด. Evaluation 18 cases: hybrid Recall@3=1.0, MRR@3=0.8667, out-of-domain abstention=1.0, 11/11 statistical facts, 2/2 methodology answers cite both sources, value/style guards pass; ดู `evidence/rag-hybrid-eval.json`
- Image รุ่น `tamsoodbase-rag:1c49e9d40b4b3936`, `linux/amd64`, ID `sha256:ed7d7b8e87db81df63205b7fee62f3338516b2fc9ec6992c6c3fd877e2f1a8fd`; allowlist package 16 files / 252,213,297 bytes; archive SHA `b4be20e1bd93a4586e5339a5e6f7fc1a0fc460b70b700d670a5f65139d960b94`
- Offline image checks: 18 records ready, method answers cite exact GHG/IPCC IDs, capacity/methane/full-life gaps map to exact facts, OOD abstains, wrong Origin 403; read-only, UID 10001, no capabilities, no-new-privileges, 512 MiB/1 GiB RAM+swap, 0.5 CPU/64 PIDs; local measured ~491 MiB. Model pooling warning remains informational.
- EC2 now runs owner-labelled release `1c49e9d40b4b3936`, healthy on internal-only network `10.253.77.0/29` at `10.253.77.2`, no host port mappings; use SSH forward `127.0.0.1:8877 -> 10.253.77.2:8767` and open `http://127.0.0.1:8877/`. Remote page/readiness and method, capacity, methane-gap, whole-life-gap, OOD and bad-Origin checks passed through this forward.
- Previous release `bbbe648cba3fc42b` remains stopped with owner labels as rollback. One live candidate was automatically rolled back after health check remained in Docker start period; the wait was fixed and the subsequent upgrade passed. Existing API image/readiness and Ginder container states stayed unchanged. `tamsoodbase-https-gateway` was already unhealthy and untouched.
- Host available memory was observed around 587 MiB after deployment; swap use was about 1,054 MiB but no pre-deployment swap baseline exists, so do not attribute that usage to RAG. Keep this service private and do not add workloads without checking headroom.
- No raw PDF/CSV, credentials, local Qdrant disk database, or Gemini runtime key in image; no public endpoint, Vercel path, Caddy/Ginder change, or rights upgrade. Source redistribution remains uncleared, corpus is not full LCI, and browser screenshot could not be captured because CUA kernel failed to start.
- Evidence: `evidence/rag-ec2-deploy.json`, `evidence/rag-ec2-package.json`, `evidence/rag-image-verification.json`, `evidence/rag-hybrid-eval.json`. Rollback runbook: `docs/rag/EC2_PRIVATE_DEPLOYMENT.md`.

## 8 พฤศจิกายน 2569 — T143 ทำคำตอบ RAG ภาษาไทยให้อ่านง่ายและแก้การแสดงผลซ้ำ

- ศึกษางาน RAG ด้านความเข้าใจและความซื่อตรงต่อหลักฐาน พร้อมคู่มือภาษาง่าย; แยกข้อความภาษาไทยที่ตรวจแล้วออกจาก source facts ไว้ใน `docs/rag/thai-answer-copy.json` จึงไม่เปลี่ยนค่าตัวเลข/หน่วย/ปี/แหล่งต้นทาง
- ปรับคำตอบให้เริ่มจากประเด็นหลัก อธิบายว่าเป็นผลวัด/ค่าประเมิน/แผนออกแบบ แปลศัพท์จำเป็น เช่น CO₂e เป็นคำทั่วไป และใส่ข้อจำกัดโดยไม่แสดง machine status codes; จัดหลักพันเพื่อให้อ่านตัวเลขง่ายโดยค่าที่เก็บยังเดิม
- ปรับ Gemini prompt ให้ตอบภาษาผู้ใช้ด้วยถ้อยคำธรรมชาติ ประโยคสั้น ลดคำย่อ อธิบายคำจำเป็น และยึดหลักฐานเท่านั้น; ยังไม่ได้เรียก Gemini สด
- เอาการ์ดหลักฐานชุดเดิมที่ซ้ำใต้คำตอบออก เหลือคำตอบครั้งเดียวพร้อมลิงก์แหล่งและตำแหน่งเอกสาร; เพิ่มป้ายไทยสำหรับ fact sources
- HTTP ทดลองเผยบั๊กคำถาม “กำลังผลิตติดตั้ง TSM” ไปเลือกอัตราออกแบบปี 2009 แทนกำลังผลิตปัจจุบัน; แก้การเทียบคำไทยหลัง Unicode normalization และเพิ่ม regression case แล้ว
- บันทึก validation ตอนปิด T143 เคยระบุชุด 16 cases แต่ไม่มี raw output/hash ของรุ่นก่อน T144 แยกเก็บ จึงไม่ยืนยันตัวเลขเดิมย้อนหลัง. ภายหลัง T144 มี combined 18-case hybrid report ใน `evidence/rag-hybrid-eval.json` (เป็นผล corpus รุ่น 8 cards ไม่ใช่ corpus ปัจจุบัน); ผล local narrative retrieval ปัจจุบันดูใน `evidence/rag-current-retrieval-eval-2026-11-10.json`.
- ข้อจำกัด: style guard ตรวจคำ/ตัวเลขอัตโนมัติ ไม่ใช่ user study; Gemini narrative ยังไม่ได้ทดสอบสด; FastEmbed pooling warning ยังมี. ไม่มีการ reindex เพราะไม่ได้เปลี่ยน corpus, ไม่มีการ deploy หรือเผยแพร่

## 8 พฤศจิกายน 2569 — T142 ปรับ RAG ให้ค้นและตอบสถิติอย่างมีที่มา

- อ่าน TableRAG (EMNLP 2025), T²-RAGBench (accepted EACL 2026) และงาน table-aware dense retrieval (NAACL 2021); ใช้แนวคิด hybrid dense+sparse, แยก fact structure จาก narrative และวัด target retrieval แยกจากการเลือก fact ของคำตอบ ดู `docs/rag/research-implementation.md`
- เปลี่ยน Thai sparse tokenization จาก overlapping bigrams เป็น trigrams พร้อม BM25 score + query-coverage gating; รวมอันดับกับ dense ด้วย RRF; แยกสถิติเป็น fact records ที่รักษา value/unit/period/basis/status/qualifier/source; statistical answer เลือก metric/alias ที่ตรงและตอบหนึ่ง fact เว้นแต่ถามเปรียบเทียบ; actual-value query ไม่ยืม design/capacity estimate
- แก้ benchmark false positive ของคำถามกล้วยไม้และการหยิบระเบียน ethanol-output มาแทน actual methane; เพิ่ม guard ปฏิเสธการเปรียบเทียบ CO₂e/year กับ kg CO₂e/L ที่คนละหน่วย/ช่วง/ฐาน; 15-case targeted suite: hybrid Recall@3 1.0, MRR@3 0.9167 (dense 0.8333), OOD abstention 1.0, statistical fact IDs ตรง 10/10; exact result/hash/config: `evidence/rag-hybrid-eval.json`
- หลังผู้ใช้พบหน้า CO₂e แสดงตัวเลข TSM ที่ไม่เกี่ยวโดยตรง แก้ answer panel ให้เหลือเฉพาะ cited fact และ narrative parent; เพิ่ม evaluator guard ว่าไม่มี uncited fact ปรากฏใน panel. Restart server แล้วตรวจหน้าและถามผ่าน HTTP: คำถาม CO₂e แสดงเฉพาะ ethanol full-life null + narrative ethanol-gap; คำถาม methane แสดง methane-null + PDD narrative ไม่โชว์ ethanol-output null หรือ unrelated TSM stats. Server รุ่นแก้ไขกำลังรันบน loopback สำหรับผู้ใช้ทดลอง.
- Validation: `py_compile` สำหรับ RAG/evaluation scripts และ in-memory Qdrant targeted evaluation ผ่าน; local collection `public_evidence_ef3b9de0485c9fc1ef2d` มี 16 records; 15-case quality gate ผ่านและ HTTP GET/POST 200 สำหรับ 2 กรณี ดู `evidence/rag-hybrid-eval.json` กับ `evidence/rag-http-smoke.json`; ไม่มี live Gemini/API call และไม่ deploy/push. FastEmbed แสดง pooling-configuration warning ซึ่งบันทึกเป็นข้อจำกัดเพื่อประเมิน embedding configuration ภายหลัง
- ขั้นต่อไป: เก็บคำถามจริงจากผู้ใช้โดยไม่ส่งข้อมูลออก; หากนำตัวเลขจาก relational tables มาตอบ ให้ต่อผ่าน query catalog/allowlisted SQL พร้อม lineage และ scope checks แทน SQL ที่ LLM สร้างเอง. ผลประเมินนี้เป็น smoke suite ขนาดเล็ก ไม่ใช่การรับรองทั่วไป

## 8 พฤศจิกายน 2569 — T141 ตรวจ PDD โครงการน้ำเสีย TSM จาก UNFCCC

- ตรวจรายการโครงการและ PDD Version 01 ลงวันที่ 5 กรกฎาคม 2009; เอกสารเชื่อม TSM Bio Energy กับโรง Thai Sugar Ethanol ที่กาญจนบุรี และบันทึกขอบเขตบำบัด/พลังงานและแผน monitoring อย่างชัดเจน
- เก็บตัวเลข 100 m³ ethanol/day, 600 m³/day vinasse, COD สูงสุด 351,353 mg/L, ก๊าซคาด 62,000 m³/day / methane content 55%, 300 วัน/ปี และไฟฟ้าประมาณ 18 GWh/year เป็น project-design values เท่านั้น
- ตรวจเลขเพิ่มพบ 600×300 = 180,000 m³ น้ำเสีย/ปี แต่ PDD ใช้ 219,000; 62,000×300 = 18.60 ล้าน m³ biogas/ปี แต่ PDD ใช้ 22.81/22.63 ล้าน; ไฟฟ้า 18,000/17,520/18,613 MWh/ปี; และสมการ leakage เมื่อนำ 22.63m×5%×0.0067 kg/m³×GWP 21 มาแทนตรงได้ 159.20205 tCO₂e/ปี ไม่ตรงผลพิมพ์ 87.56. Methane 55% ยังไม่มี basis ชัดและ 5% leakage semantics ต่างกันระหว่าง trigger กับ ex-ante. เก็บค่าเดิมทั้งหมด ไม่แก้แทนต้นฉบับ
- 146,023 tCO₂e/ปีเป็น ex-ante project avoidance เทียบ baseline ไม่ใช่ product LCI หรือผลวัด; GWP 21 เป็นค่าตาม first commitment period ไม่ใช้เป็น factor ปัจจุบัน
- ค้นโดเมน UNFCCC ต่อแบบจำกัดสองคำค้นหา monitoring report แยกแล้วยังพบเพียงหน้า validation/PDD; ไม่อ้างว่าไม่มีรายงานที่อื่น
- อัปเดต `docs/ethanol-tsm-wastewater.md`, `docs/source-registry.csv`, `evidence/ethanol-tsm-unfccc-pdd-review.json`, T141 และ task board. Actual methane/output/electricity matched period และ CO₂e/L ยังคง null; redistribution rights not cleared. ไม่มี raw PDD เก็บใน repo, ไม่มี code/data/production change.
- ตรวจเฉพาะ JSON/CSV/task board และ consistency ของ arithmetic หลังบันทึก; ไม่รันชุดทดสอบหรือดาวน์โหลด/เผยแพร่เอกสารต้นฉบับ.

## 8 พฤศจิกายน 2569 — T139 ตรวจ LCI โรงงานอ้อยบูรณาการไทย

- ตรวจสำเนา JSEE 2014 จากผู้ใช้ hash `7c6ae50432f80e98ed1ad7585e9a7fae3a6379ed948872763ff5cb98db199747` ตรง manifest; เทียบ PDF text กับภาพ Table 1–2 หน้า PDF 4–5 แล้ว
- บันทึกขอบเขตอ้อย 1 ตันถึงประตูโรงงานและ flow ตัวอย่าง; ทวนสมดุลชานอ้อย กากน้ำตาล กากกรอง ไอน้ำ และไฟฟ้า 5 สมการตรงค่าที่พิมพ์; อัตราต่อ L เอทานอลติดป้ายเป็นค่าคำนวณของทีม
- Table 2 รายงาน 5.52 kg CO₂e/kg BOD สำหรับ CH₄ จากบ่อไร้อากาศ โดยหมายเหตุรวม CH₄+N₂O ไม่รวม CO₂ จึงไม่ใช่มวล CH₄; trace ไป Table 3 ของบทความปี 2008 พบ default 0.22 kg CH₄/kg BOD แต่ไม่ใช่ผลวัด และยังไม่สามารถ reconcile ตัวคูณรวม 5.52 แบบรายก๊าซได้
- แถว BOD น้ำเสียโรงเอทานอลให้ค่า 0.052 mg/L เมื่อแปลงตามหน่วยที่พิมพ์ จึงคงค่าต้นฉบับและ HOLD รอหลักฐานอิสระ
- คงบทความเป็น Thai production-to-gate reference ไม่เชื่อมกับ TSM/DEDE ไม่ปิด full fuel lifecycle หรือ project CO₂e; สิทธิแจกจ่าย PDF/ตารางยัง NOT_CLEARED ไม่มีการเปลี่ยนข้อมูล production หรือ deploy
- เอกสาร `docs/ethanol-whole-cycle-reference.md`; machine-readable evidence `evidence/thai-biorefinery-2014-lci-audit.json`; T139 เพิ่มใน `docs/tasks.json` และ generate task board แล้ว
- ขั้นต่อไป: หาแหล่งติดตามผลจริงของ TSM ที่มีงวดเดียวกันสำหรับ CH₄, เอทานอล, COD, ไฟฟ้า และ leakage; PDD เป็นแบบออกแบบย้อนหลัง ไม่ใช้ปิดข้อมูลจริง และไม่วนอ่านไฟล์เดิมซ้ำหากไม่พบหลักฐานใหม่

## 8 พฤศจิกายน 2569 — T140 ตรวจ disclosure ปัจจุบันของ TSM

- พบและตรวจสองหน้าองค์กรใหม่ที่ไม่ซ้ำกับ URL ในรายการอ้างอิงเดิม: หน้าน้ำเสียบอกระบบส่วนกลางที่มี Activated Sludge และ MCL กับขอบเขตการติดตามคุณภาพน้ำ; หน้าพลังงานบอกเส้นทาง spent wash → biogas/CH₄ → electricity ขาย PEA
- หน้าองค์กรยังไม่ยืนยันว่าระบบบำบัดส่วนกลางครอบคลุมโรงเอทานอลแห่งเดียว/โรงท่าไม้หรือรับน้ำจากหลายบริษัท และไม่ระบุลำดับหน่วยบำบัด; เก็บเป็น qualitative lead เท่านั้น
- ข้อความ “CH₄ 1 ตันเทียบเท่าลด CO₂ 28 ตัน” ไม่มี GWP horizon, baseline, leakage boundary, ปริมาณ CH₄, output ไฟฟ้า หรือช่วงเวลา จึงเก็บเป็น company-reported claim ไม่ใช้เป็น inventory/factor
- ไม่มีค่ามวล CH₄ หรือเอทานอลงวดเดียวกันบนหน้า; คง methane emitted/recovered, matched output และ CO₂e เป็น null; สิทธิใช้/แจกจ่ายหน้าเว็บยัง NOT_CLEARED
- เพิ่ม `evidence/ethanol-tsm-current-disclosure.json`, อัปเดต `docs/ethanol-tsm-wastewater.md`, เพิ่ม T140 และ regenerate task board; ไม่มีการเปลี่ยน production/deploy หรือเปลี่ยนตัวเลขเดิม
- ขั้นต่อไปต้องใช้รายงาน EIA/monitoring หรือบันทึกโรงงานที่มี period และขอบเขตชัด; ถ้าเปิดสาธารณะไม่มีข้อมูลต่อให้หยุดค้น URL เดิมและคงช่องว่างเป็น null

## 30 ตุลาคม 2569 — References SRC-01 ถึง SRC-10

- SRS Markdown เป็นฉบับ 0.6 เพิ่มรหัสอ้างอิงสำหรับคนอ่าน และ mapping กลับ `source_id`; `SRC-06` รวมตาราง NSO จาก Statistical Yearbook ฉบับเดียว; `SRC-09` ครอบคลุมบทความ MDPI Tables 1–4 พร้อมเพิ่ม source ID สำหรับ Tables 1–3 ใน registry; `SRC-10` แยกเป็นแหล่งประกอบการเปรียบเทียบ DEDE
- เว็บแสดง SRC badges บน source crosswalk และอ้าง `SRC-09` บน inventory conversion/upstream; หน้า Sources มี `SRC-10` พร้อม `DEDE-SIT-DEC2024`; คง technical source IDs, hash และ rights status เดิมไว้
- Build frontend และแพ็ก Vercel แบบ allowlist ผ่าน; production deployment ล่าสุด `dpl_EvmU2Pqb1wUgiuiGNxbvGi8fZ468` พร้อมที่ alias เดิม `https://tamsoodbase.vercel.app`; ตรวจ HTTP 200 สำหรับหน้าแรก, app.js และ `/api/source-crosswalk`; HTML production มี SRC-09/SRC-10/DEDE source ID และ app.js มี mapping SRC-01
- ไม่สร้างหรือแก้ PDF; งานในรอบนี้ยังเป็น SRS Markdown/registry/web เท่านั้น; visual browser check ของหน้า Sources ยังไม่ยืนยัน
- ขั้นต่อไป: สมาชิกตรวจรหัสอ้างอิง/เนื้อหาและทำต่อบท Requirements; หากแก้ลำดับ SRC ภายหลังให้ปรับ mapping ใน `web/app.js` ให้ตรง SRS

## 29 ตุลาคม 2569 — SRS Introduction 0.5

- ปรับ `docs/submission/SRS.md` บท 1 ตามตัวอย่างผู้สอน: Purpose, Scope, Definitions และ References; ระบุขอบเขตข้อมูลจริง 5 ชั้น และชี้ชัดว่ายังไม่มี Functional Unit/System Boundary กลางหรือ full lifecycle LCI
- References ใช้ source IDs ที่ตรวจพบใน `docs/source-registry.csv` พร้อมสถานะ review/สิทธิและข้อจำกัด ไม่ได้นำโดเมนตัวอย่างข้าวหรือข้อความตัวอย่างมาใช้เป็นข้อเท็จจริง
- สร้าง `output/pdf/TamsoodBase-SRS-review.pdf` ใหม่: 21 หน้า; เรนเดอร์ครบและตรวจภาพหน้า 2–4 ซึ่งมีบท Introduction/ตารางนิยาม/แหล่งอ้างอิงแล้ว ไม่พบข้อความตัดหรือส่วนล้น; `evidence/srs-current-review.json` มี hash ฉบับล่าสุด
- ปรับ footer วันที่ใน `scripts/build_final_documents.py` ให้ตรง 29 Oct 2026; ยังเป็นร่าง AI-assisted ที่รอสมาชิกตรวจและรับรอง ไม่ใช่ฉบับส่ง
- ขั้นต่อไป: สมาชิกทบทวน/เติมข้อมูลทีมจริง; จากนั้นทำบทถัดไปโดยเทียบตัวอย่างและยึด source/runtime หลักฐานปัจจุบัน

ผู้ใช้สั่งเริ่มทันทีและให้ทำSRSละเอียด/ตรวจข้อมูลทุกrecordต่อ ไม่ต้องรอเวลารีเซ็ต รักษาautomation tamsoodbase-srsรายชั่วโมงไว้ แต่ไม่ใช้resetcreditเอง

- SRS0.4ขยายusecases8กรณี กฎข้อมูล/API/acceptance และแก้สถาปัตยกรรมให้ตรงEC2MySQL/Vercelจริง PDFร่าง19หน้าrenderและตรวจภาพแล้ว ดูevidence/srs-current-review.json;slides10หน้าrebuildแล้ว;ไม่ใช่ฉบับสมาชิกอนุมัติ
- NSO273มีreviewledgerครบ;cross-publication169=141exact24displayrounding4divergence;104ยังค้าง ดูevidence/nso-review-ledger.json ห้ามอ้างว่าทั้ง273ผ่านcross-source
- Neo4jจริงinventory16/39nodes/68edges/4queriesผ่านในinternalnetworklab ไม่รันซ้ำไร้เหตุ ไม่ใช่productiongraph
- EC2MySQLdea667bbd79dc1d9และS3restore5schemasผ่าน;Vercel URLคงเดิม browserไม่ต้องloginตามเจ้าของ server-onlyupstreamsecretยังต้องเก็บลับ QuickTunnelยังชั่วคราว ไม่มีdomain ไม่แตะGinder/Caddy
- งานถัดไป:หาคู่หลักฐานให้104ที่เหลือ สืบ4divergencesโดยไม่แก้sourcevalueเอง เติมSRS/diagram/dictionaryและfreezeตามreleaseจริง สมาชิกต้องเติมข้อมูลทีม/memo/consent/contribution/defenseจริง

- รอบล่าสุด:เพิ่มprimary-supply2024อีก14comparisonจากDEDEworkbookhashเดิม;13exact/1roundingcompatible;ไม่มีsourcevalueเปลี่ยน;124testsผ่าน;PDF0.3ยัง19หน้าrenderตรวจแล้ว ดูdocs/primary-supply-2024-review.md

## ตรวจเพิ่ม 28 ตุลาคม: T77

- NSO273รายการแจกแจงสถานะครบ;cross-publication169=141exact/24rounding/4divergence อีก104มีเหตุผลรายรายการ ไม่เรียกผ่านครบ
- พบDEDE2024หน้า52พิมพ์พ.ศ.2567/ค.ศ.2034ขัดกันจริงจากภาพ จึงhold23รายการ;หน้า56importsเพิ่ม10exact อีก2ขีดไม่แทนศูนย์;derivedpercent18ตรวจสูตรผ่านไม่นับdirectcomparison
- 127testsผ่าน;SRS0.4PDF19หน้าrenderตรวจ;หลักฐานevidence/nso-remaining-audit.json และ docs/source-completion-review.md ไม่เปลี่ยนค่าต้นทาง/production
- ขั้นต่อไป:ใช้ข้อจำกัดเหล่านี้ในfinal;สมาชิกเติมข้อมูลทีมและหลักฐานมนุษย์จริง การปิด104ต้องใช้หลักฐานเพิ่มเติมไม่ใช่รันซ้ำ

- T78:ปรับสไลด์PDF10หน้าและPPTXแก้ไขได้ให้ตรงSRS0.4/169comparison/EC2MySQL/Vercel/Neo4j;renderPDFตรวจภาพแล้ว ไม่อ้างว่าเปิดrenderPPTXด้วยPowerPointจริง ดูevidence/final-document-draft.json สไลด์ไม่ค้างรุ่น15/273อีกแล้ว

## T79 UX สำหรับเดโม 28 ตุลาคม

เพิ่มลิงก์หน้าเว็บไซต์คู่CSVในNSO/EPPO/DMFและpreviewคอลัมน์NSO เพิ่มเส้นทางเดโม5ขั้น/โหมดซ่อนภาพรวม/ตัวอย่างดีเซล2024;128testsผ่าน;deploy dpl_FZytDstFb6KTKAHPBJkNy2Uyno2Cบนลิงก์Vercelเดิม;hashHTML/JS/CSSตรงbuild ไม่แก้backend/data/rights ผลbrowservisualยังตรวจไม่ได้เพราะCUA/nodekernelเริ่มไม่ได้ ดูevidence/demo-evidence-ux.json และ docs/DEMO_QUICK_START_TH.md

## T80: ผู้ใช้ไม่รับ UX T79 ให้ทำใหม่
นำแถบเดโม/โหมดfocusออก ลดหน้าแรกเหลือ5topiccardsและNSOก่อน ลบทางเข้าซ้ำ เก็บDMFmetricsเฉพาะexplore/quality หน้าอื่นเริ่มตารางทันที ปุ่มดูที่มา/websiteคู่CSVยังอยู่แต่fullrowยุบได้;128testsผ่าน production dpl_9Qd5GhZtJ85fmuGidkUdLasfB5yj hashassetsตรงbuild/NSO273 APIปกติ ยังไม่อ้างvisualbrowserverification ดูevidence/catalog-simplification.json;T79demo-guide superseded

## หยุดรอบอัตโนมัติที่ไม่มีงานใหม่
ลบautomation tamsoodbase-srsหลังหลายรอบไม่มีหลักฐาน/งานอิสระใหม่ ไม่ได้หมายถึงโปรเจกต์เสร็จ ข้อค้าง104comparisonsและข้อมูลสมาชิก/finalreviewยังอยู่ ไม่รันซ้ำหรือประกาศผ่านแทนทีม

## T81 ตรวจFU/Boundary 30ตุลาคม2569
ต้นฉบับSection2.1กำหนดFUเป็นการใช้เชื้อเพลิง1000MJแล้ว แยกจากขอบเขตนำเข้าTable4ที่เป็นforeground16ค่า เพิ่มsrc/inventory_scope.pyและเรียกตรวจจากextractor ตรวจprocessbasis/boundary/year/source/referenceproduct/role/fullclaim;133testsผ่าน ทั้ง16ค่าบนAPIจริงตรงsavedreportและผ่านสัญญาใหม่ หน้าinventoryอธิบายFUทั้งการศึกษา/ขอบเขตที่นำเข้าและส่วนขาด พร้อมguardไม่รวมcontextต่างกัน deployfrontend dpl_A5ss1LP5Cyvx99eQS5gPmbcAe47c hashassetsตรงbuild Backendcodeยังไม่deploy/ไม่migrateMySQL ไม่เปลี่ยนตัวเลขหรือfullLCIstatus ไม่อ้างbrowservisual ดูdocs/inventory-scope-contract.md และevidence/inventory-scope-review.json ไม่เขียนทับSRS0.5ที่มีอยู่ใหม่

## T82 เริ่มแผนพัฒนาLCI 30ตุลาคม
ผู้ใช้อนุญาตค่อยปรับตามคำวิจารณ์และหาข้อมูลเพิ่ม เลือกFAMEconversionเป็นกรณีหลัก ทำsource-localflowregistry15flowsครอบ16exchanges/readiness2processes พบFAME→H-FAMEprovidercandidate1คู่แต่ไม่applyเพราะallocation/period/modelcompatibilityยังไม่ชัด modelready0 ไม่เปลี่ยนตัวเลขหรือproduction;136testsผ่าน ดูevidence/inventory-model-review.json และdocs/lci-development-plan.md ค้นพบupstreamTables1-3ในบทความเดิมแต่ผู้ตีพิมพ์429จึงไม่promoteค้นsnippet;COMPETEPDFเปิดผ่านwebtoolไม่สำเร็จ บันทึกcandidateไว้ ไม่วนเรียก แก้docs/data-model-selection.mdที่ข้อความgraphเก่าให้แยกประวัติจากNeo4jlabจริง

## T83 ได้upstreamPDFจริง
พบPDFv3URLทางการใหม่สาธารณะ (ไม่วนHTML429) เก็บsnapshot/hash/licenceCCBY4.0 ตรวจTables1–3หน้า5–6สองextractorsและภาพครบ42cells:FFB18มีหน่วย+1HOLD/CPO12/RBDPO11 สร้างSQLitecandidateprocess3exchange42ตรวจroundtrip/FK/negativechecks พบ3providercandidateแต่0apply;FFBinputTable2ขาด,Water0.11kgคงเดิม,NaOHnarrative vsKOHTable4เก็บissue,allocationยังunresolved;140testsผ่าน ไม่เพิ่ม16productioninventoryหรือmigrateEC2 ดูdocs/upstream-inventory-review.md/evidence/upstream-inventory-review.json งานต่อallocation+missingfeedstock+candidateUIแยก ไม่สร้างfullLCIclaim

## T84 ข้อมูลต้นน้ำขึ้นเว็บแล้ว
ผู้ใช้ให้ทำจนเสร็จนำขึ้นเว็บและย้ำตรวจก่อน:ขึ้นVercel dpl_5metZ1Rnpd7NgAn5SFjaspKtyjpG มีแท็บต้นน้ำFFB/CPO/RBDPOแยกจาก16conversion มี42observations/41unitpresent/1HOLD ค่าทุกfieldของpublicsnapshotตรงreviewedreport สร้างJSONเฉพาะCCBY4.0พร้อมattributionบนVercel (เป็นข้อยกเว้นcode-onlyเดิม) ไม่เผยrawPDF/ข้อมูลบริษัทเพิ่มและไม่migrateEC2/MySQL ตรวจ143tests/API27routesและbrowserจริงก่อน/หลังdeploy (เครื่องมือกลับมาใช้ได้):FFB19/CPO12/RBDPO11/filterOUTPUT1/holdno-unit/PDFpage6 ถูกต้อง ทดสอบ390pxไม่มีpageoverflow/tableเลื่อนได้ ดูevidence/upstream-web-release.json และภาพbuild/ux-verification/upstream-live-proof.png ยังไม่applyallocation/providerหรืออ้างfullLCI งานที่ยังขาดยังแสดงตรงไปตรงมา

## T85 Allocation/readiness/export
ตรวจreportedallocationจากPDF:CPO92/6/2หน้า5,FAME70/30หน้า7 รวม100%แต่ไม่applyเพราะtablebasisยังไม่resolved หาARDAreference18เพิ่มพบNRCT3152ที่เกี่ยวข้องแต่ยังไม่ยืนยันidentity/calculations จึงไม่ใช้ปิดgate ขึ้น3processreadinessprofilesและfilteredreviewJSONพร้อมsource/decimal/hold/license/limitations บนVercel dpl_9ATkhNM3ybpM297dYszZ38iix1Si;146testsผ่าน ตรวจbrowserdownloadจริงCPO12localและFFBINPUT18production/parsefullroundtripรวมNULL/HOLD;HTTP42rows+profilesตรงbuild/16originalconversionrowsทุกfieldไม่เปลี่ยน ดูevidence/upstream-export-review.json และdocs/allocation-and-review-export.md งานถัดไปยังcalculationbasis/missingFFB/backgroundเชื่อม ไม่อ้างfullLCIหรือILCD/openLCAformat ไม่migrateEC2

## T86 ทะเบียนรวมและแผนปิดงาน 30ตุลาคม2569
ผู้ใช้ยืนยันทำงานหลัก/รองครบตามแผน สร้างcombinedreview5processes58payloads/51exactlabelunitkeys เก็บทุกfieldเดิมและ1HOLD ตรวจJSONroundtripครบ58ไม่สุ่ม;148testsผ่าน เพิ่มremaining-work-2026-10-30.mdรวมgateallocation/missingFFB/provider/background/crosssource/finalและSRSaddendumแยกไม่เขียนทับ0.5 ไม่applyfactor/link ไม่เปลี่ยนproductionหรือเว็บเพราะรอบนี้เป็นreviewartifact ข้อค้างหลักยังต้องcalculationbasis/ข้อมูลตรงบริบทและงานสมาชิกจริง ไม่ปิดว่าfullLCIหรือส่งfinalแล้ว

## T87-T88 expert critique follow-up — 2026-10-30
User authorized detailed implementation and repeat review against all twelve critique points. Added docs/expert-review-action-plan.md with explicit remaining acceptance gates. T87 local release manifest audits22checks (source hashes/public projection/all build assets/SRS source-PDF-render hashes); records historical deployment IDs without claiming live runtime health. Negative tests detect stalebuild/contextchanges/stalePDF. Added current-status notices above historical deployment/workplan/submission documents. T88 covers5processes/58source IDs/1HOLD; separates source verification/cross-publication/independent measurement/context/model statuses; no fake score/completeness percent; rejects wrong provider identity and applied scaling. Full154tests passed. No website/API/EC2 changes; allocation/missingFFB/background and human reviews remain open. Next integrate reviewed coverage into process UI with browser checks, then scoped primary-source review and export/schema/security gates; do not mark all12 complete.

## T89-T90 — 2026-10-30 quality UI and bounded proxy live
Published dpl_BSZ6yCPZUmiHXzJT7RBDcsqmdbCM:3upstream profiles show boundary/usable-for/6quality dimensions/rights;public_snapshot_id shared by UI/export;source modal raw-vs-stored and PDF-page clarification. All42 values/1HOLD preserved. Browser localCPO12 and productionFFB19 native download roundtrip including profile/version;mobile390/page375;Escape closes modal. 155tests and27productionAPIroutes pass. Added32MiBstream export limit/HEADnobody/erroronce guards;noEC2MySQLchange. evidence/current-frontend-release.json + docs/quality-contract-web-review.md. FoundNRCT20pagepolicybrief through newPDFsource;visualpage9yield context2013 does not establish missingFFB/ARDAcalculationidentity;0observationsadded/rightsunclearrawprivate. Releasechecker currentlyfailsSRSsource-PDF:anotheredit advancedMarkdown0.6 whilePDF remains0.5;preserve concurrentwork/do not claimfreeze. Next source/model gates and finaldocument synchronization after edits settle;remaining twelve-point plan not all closed.

## T91-T92 — 2026-10-30 document synchronization and bounded primary review
Rendered frozenSRS0.6 snapshot to separatecandidate21pages;reviewed allpagecontactsheets and fullreferencepage4;verified liveMarkdownhashstillmatched beforepromotingPDF. Retained previousPDF under output/pdf/archive;didnoteditSRSMarkdown. evidence/srs-current-review.json nowmatches0.6;DRAFT/teamreviewpending remains. Generator detects source change duringrender and derivesfooterdatefromsourcebydefault. Releaseconsistency now24checks includingpackagedproxy/source;allpass. NRCTcandidate20pagepolicybrief officialPDF retainedprivate/hash/page9visual;2013aggregateyieldnotcompatible proof for selectedTables1-4,0newobservations. TasksT91/T92closeonlytheseactions;allocation/missingFFB/background/104unpairedNSO/4divergences/humancontribution remainopen. Full155testspassed aftercodechanges;finaltargetedrelease4testspass. NoEC2MySQL/Ginder/Caddy/SGchange,Gitpush ornewautomation.

## T93-T94 — 2026-10-30 implement outstanding schema/export critique items
Added immutable source_observation/process_dataset_version/dataset_exchange/numeric_parse_audit localcandidate:58fullpayloads/5sealedversions/58parseaudits. Typed-vs-payload mismatch, wrong process, source/version/membership changes, allocation mutation and late-batch FK failure/rollback tested. Numeric source0.08a remainsraw with reviewedannotation,amount0.08;noallocation/unitconversion/providerapply. Candidate release d35788b1f8008932ede94ebe98b724834f48564c470b9e52db763d88a5b4814f;notMySQLmigration. DockerCLIinventory didnotreturn;terminated query without touching containers/volumes.
Web FAME/H-FAME now quality/sourceversion/reviewJSON with guards. NativebrowserFAME10local and H-FAME6production exports match every sourcefield/basis/null/footnote. Mobile390/page375/table697;source-vs-stored modal verifiedproduction. Latestfrontend dpl_GrAZ3mNQ7mroNG7EWCu8J5nkoUXw;4liveassets matchbuild. Previousdeployment27APIchecks passed/APIproxy/backendunchanged in finalpresentationonlydeploy. Full161tests passed;releaseaudit25checks includescandidateDBhash. Newdocs/versioned-inventory-design.md and expert-review-checkback.md auditall12points;canonicalplan tableupdated ratherthan claimingallcomplete. Remainingrealgates:allocation/FFB/background/globalmapping,permanentendpoint,user/teamreview,MySQLcandidateenginechecks beforeanymigration. NoEC2/SG/Caddy/Ginderchange,Gitpush,newautomation,or fabricateddata.

## T95 — 2026-10-31 MySQL equivalent engine verification
LocalDocker12stimeout;ownedEC2MySQL8.4.13reachable/ownerlabelverified. Addedsql/mysql/versioned-review.sql and isolatedschema verifier.58fullsourcepayloads+typedjoins match;5sealedversions/1HOLD.8negativecases confirmedexpectedMySQLERROR1644 ratherthan arbitraryfailure;lateFK1452 afterfirstinsert59 rollbackto58 onclientconnectionclose. Temporaryschemaownercheckedandremoved;runningcontainerIDsunchanged/APIreadyafter.NoAPI/prodschematables/grants/ports/Ginder/Caddychanges. UseraskednewUXafterthiswork:plain-languageacronyms/searchchoices(optionaltyping)/purposefulillustration. T95done beforeUXstarts;scientificgatesremainopen.
# T96 — 2026-10-31 guided discovery live
After T95 MySQL verification completed, added 29 plain-language terms, choices plus optional typing across five views, source-backed dynamic topic lists, SVG topic illustrations and optional conceptual process guide. Published dpl_EfA4ngG9mh1uqX9UBDd1rt8i3R4W. 163 tests/27 live API routes pass; four production assets match build; live browser NSO acronym/catalog filter/diesel2024 2values verified; local desktop/mobile checks recorded in evidence/guided-discovery-ux.json. No source values/rights/EC2 changes; no full lifecycle or production schema migration claim. Scientific gates and human final review remain open.

## W13 lifecycle review — 2026-11-03
Read attached40pagelecture; visuallycheckedp4–5. Added docs/w13-lifecycle-alignment.md mapping five lifecycle stages to existing58observations/5processes and evidence gaps; distinguishes4LCAphases, FU vs processbasis, transport/use/treatment gaps and hypotheticalEF. Proposed study-stage coverage/provider/EF version design, no fabricated flows/no schema migration/deploy/tests claim. Next close allocation/FFB basis then examine matching transport/use evidence; no fullLCI claim.
# T97 lifecycle implementation — 2026-11-03
User requested full lifecycle completion with missing data added. Implemented FAME-only candidate52sourcepayloads/fivestages and evidence/scenario/completeness guards;4newtests pass. No scaling/provider/allocation applied, no deployment. Original study background depends on nationalreports/ecoinvent; Frontiers690725 actualHTML reviewed/privatehash, MexicoHEFA/FU13.13kg/massallocation incompatible,0observationsimported;CiteSeer/TCI PDFs unavailable not promoted from snippets. docs/lifecycle-build-progress.md records actual gaps. T97 IN_PROGRESS, fullLCIfalse; transport/use/treatment and upstreammodel gates remain, not a completed lifecycle dataset.

## Thai lifecycle source selected — 2026-11-03
Found Springer2013Thai palm-biodiesel chapter DOI10.1007/978-3-642-34519-7_2, publisher identityverified and actualPDFvisualprint33–36 reviewed. Fig2.2 quantitative chain + usephase + EFB/POME scenarios; privatecopy/hash NOT_CLEARED. Criticalprose1MJ vsfigure1000MJ conflict anddifferentallocation recorded, not scaled/imported. ChulaETD17869 screened gate-to-gate notfullcycle. docs/thai-lifecycle-source-selection.md records suitability/gates. T97remainsinprogress;nextresolvebasis/checkfullinventory/rights,keep2013separatefrom2020.

## Lifecycle research decision — 2026-11-03
OfficialThaiNationalLCIportal/NSTDAcategorydocs verified;recommendedThaiFAMEforeground+ThaiLCIbackground+compatibleuseinventory,notonearticle. Ecoinventlicensingexplicitdeveloper/interactive restrictions;USLCIonlysurrogateifcompatible;openLCAofficialproviderlinkdocsread,nocandidateimportclaim. docs/lci-research-decision-2026-11-03.md/evidence/lci-research-decision.json. ActualThaiLCIfiles/rightsnotobtained;0newobservations/nodeploy;2020baselinekept2013alternativebasisunresolved. T97remainsinprogress.

## Thai-only + carbon screening — 2026-11-03
UserrestrictstoThai-onlyandaddsCO2methodrequest. VerifiedTGOCFPactualHTMLrow307biodieselThaiNationalLCI1.0372kgCO2e/kg/April2026/methodIPCC2013GWP100a;privatehash/7cells. AddedscopedDecimalcalculator/notfullresult,3newtests+4lifecyclepass. Example1000kguser-scenario=1037.2000kgCO2eonlyfactorcoverage,nomeasurement/noFU1000MJclaim. CFOIPCCdefaultsnotadmittedThai-only. ThaiNationalLCIportalreachablebutnoexchangefilesyet;T97stillopen;T98scopedtaskdone. docs/thai-only-carbon-method.md.NoEC2/webdeploy/rightschange.

## T99 system review — 2026-11-03
Fixedfactor7cellsHTMLbinding/lifecycleunknown-or-omittedIDs/emptyfalse-readiness/measurementcompleteness/Decimalrounding;strictThaiinputoriginfalseexplicit.173fulltests+25releaseconsistency+27liveAPIparitypass;staticcredentialleaknotdetected. docs/thai-lifecycle-system-review.md/evidence counterpart. ContinuedThaiacquisitionledger;noimport/deploy/EC2change.52FAMEsourcepayloadpreserved;T97scientificgatesremainopen.

## T100 Thai use/treatment review — 2026-11-03
Reviewed2013PDF48use4gases/amounts/unitperlitre andPDF47fourqualitativetreatmentrows usingpypdf+pdfplumber/hash;exactsubscriptreattachmentchecked. Fossil0.15subsetnotadditionalCO2flow;CH4/N2O/PMfraction/measurementyearunknown;no2020merge/CO2etotal/fullLCIclaim.3newtestspass;transport2009newrepositorySSLexpired/webtimeoutnotbypassednotpromoted. report/evidence/buildseparateprivateNOT_CLEARED;noAPI/deploy/source52change. T97remainsopenforquantitativeThaiinputs/compatibility.

## Thai missing-data source screen — 2026-11-03
FoundofficialNSTDA2021WTW64pagereport;webtextPDF45print37footnote11FAMEWTT1.7096+TTW0.1550=WTW1.8646kgCO2eq/Ldecimalverified. BenchmarkonlypendinglocalPDFhash/visual/underlyingorigin,noLCIimport. Downloadclosed/screenshotcachemissnotclaimedverified. UBUusedcookingoilthermal andKMUTNBglycerollabMFC contextmismatchnotpromoted;IIETAethanolEVnotFAME. docs/thai-gap-search-2026-11-03.md/acquisitionledgerupdated. No testsrerun/doc-only;T97quantitativegapsremain.

## T101 POME + benchmark verification — 2026-11-03
NSTDA2021PDFdownloadnowvalidTLS;localhash/visualPDF45footnote11+2extractorsverify3WTWvalues/sum. NewThaiKrabi2011fullscalePOMEPDF3Table2all4x5cells+2generationratios/hash/visual/2extractors;3newtestspass. Methanegeneratednotfugitiveemission;gross50kWh/m3derivednotnetcredit;noFFB/FAMElinkinvented. docs/thai-pome-benchmark-review.md/evidence;acquisitionledgerupdated. RightsNOT_CLEARED/private/noAPIdeploy. T97stillopentransport/usegas/basis/Thai-backgroundgates.

## T102 domain alignment — 2026-11-04
UserreemphasizedPetroleumNaturalGasFuels. Addedsource-boundTGO16rows28–42/307reference-onlyregistryfromNov3snapshot;LPGgas-vsrefineryidentity/CO2product-notemission;33/34/35explicitimportmixhold,allupstreamThaiunverified.3newtestspass. NewChulaGSP1–3Rayong2007abstractverified/fulltextpending;SpringerThaiLCI2017dieselcaseforeigncrudeexcludednumericbutmethodologicalwastetreatmentrelevant. docs/domain-source-review-2026-11-04.md/evidence/domain-factor-review.json. POMEremainsfuel-linked_supportonly,noAPIdeploy/rights/fullLCIclaim.

## T103 actual Thai GSP inventory — 2026-11-04
ResolvedChulaDOIredirecttoDigiverse78111;publicdownloadIDs454804/5/7obtainedmethod7/results17/back20scannedPDFpages/hash. ManualvisualTables4.1–4.3(42cells/41numeric1dash) typedcandidate+rawnotation/units/locators/roundtrip/transcriptionhash;notOCR/independentreview. PreservedGSP3CO262600vs63000mgsummaryandGSP1capacity390vs350conflicts.9relatedtestspassincluding3new. Sourcegate-to-gate/massallocated1kgproductnotfullLCI;rightsNOT_CLEARED/private/noAPIdeployment. docs/thai-gsp-source-review.md/evidencecounterpart. T97extraction/transmission/distribution/use/provider/provenancegatesremain.

## T104 lifecycle readiness guards + new Thai transport source — 2026-11-04
Required parameter removal/duplicates, source HOLD/unit/provenance and gate evidence now checked; both PDF/HTML hash fields preserved.14targetedtests pass (4new), candidate52payloads unchanged;1HOLD missingunit has2reasons not2rows. NewThaiTransport2025 DOI10.1016/j.spc.2025.04.023 authorrepository/Crossrefmetadata verified/privatehash;actualPDF403/supplement pending,0numericalimports. KU2011 production-only/foreignbackground identified;2009webfulltext localSSLexpired/screenshotmiss andThaiScience2004notPDF notpromoted. docs/lifecycle-readiness-review-2026-11-04.md/evidence. NoAPI/deploy/rightschange;T97stillopen actualThai-only background,transport compatibility,usegas/wastebasis. Do not rerun failed source URLs without new evidence.

## Thai LCI access handoff — 2026-11-04
Liveportalservicessearchfoundactual16t10wheel100%normalB5tkm2009dataset;collectionBE2549–2551/attributional;Documentation_truck.pdf+XLSX/CSVnamesvisible. Openedsignin;userofferedlogin;do not ask credentials. Scientificcompatibility/rights/filespending,notfuel-tankerassumption/noimport. ScienceDirect2025visiblehumancheckhandoff;requestAppendixAsuppPDF+spreadsheet. evidence/thai-lci-access-review.json.NoAPI/deploy.

## ThaiLCI signup diagnostic — 2026-11-04
Userreportedcountry/provinceunselectable;originalselectsenabledbutplaceholderonly,freshseparatetabreproduced+twoAPI500errors(exactendpointnotcaptured).Likelybackend/reference-datafailure,noclaimrootcauseproven.Originalfilledformnotreloaded,noPIIpersisted/noregistrationsubmitted.Contactpageverified;inventoryaccessstillpending.Seeevidence/thai-lci-access-review.json.

## T105 open-source Thai CPO mill alternative — 2026-11-04
UserpausedbrokenThaiLCIsignup/choseothers. AcquiredpublisherJSEE2019Huailuek13pagePDFwithSI/privatehash;TableS2PDF11all90numericcells/15flows6millsverifiedpypdf+pdfplumber+fullvisual;7literalzeros/JSONallfieldroundtrip. FFB/CPO6.93/6.29/5.95/5.94/6.10/5.65kg/kg andtreatedPOMEbasis retained perplant,not2020patch/nationalaverage.3newtests6relatedpass. docs/thai-mill-alternative-2019.md/evidence/thai-mill-2019-review.json. Foreignbackground/defaultsandcreditsnotimported;elementaryemissions/use/compatibilitystillmissing,T97open.NoAPI/deploy/rightschange.

## T106 source-basis review and usable mill activity scaling — 2026-11-04
Added auditedsinglemillCPOkgscaling preserving15fullsourcepayloads/nocredits/background/CO2e;all6millsreference1000kgandfractional1.25kgconservation tested.3newtests15relatedpass. CLI500kgdemonstrationMill1FFB3465kg/water0.520m3/treatedPOME1.55m3/sourceCPO500kg;scenarioonly. JStageThaiEFB2019fulltextusesIDEA/IPCCdefaultsnotimported;WURdownloadincomplete renamed.partial/statusINCOMPLETE_DO_NOT_USE;Inderscience403notbypassed. docs/thai-mill-scaling.md/evidence/thai-mill-scaling.json.NoAPI/deploy/fullLCIclaim;T97compatibility/background/use/treatmentemissionsgatesremain.

## T107 ordered Thai FAME assembly begun — 2026-11-05
Userauthorizedallorderedsteps. Created6explicitmixedvintagephysicalactivityscenarios/Mill1stablefirst-columnbaseline(notnationalaverage/lowestburden),55sourcepayloadseach/1unitHOLD;FAME1000MJ→RBDPO24.6kg→CPO27.06kg→FFB187.5258kg(Mill1).3physicaltransferbalancesmatch/all6;burdenlinksnotapplied/allocationunresolved. Reviewed2019PDF3estimatedFFB5kmby2extractors+visual;loadedlegscenario0.937629tkm,return/provider/other3legsstillnull/noemissions.16targetedtests(4newchain)pass,JSONallfieldroundtrip/hashchecks. docs/thai-fame-completion-plan.md/evidencecounterpart;T107IN_PROGRESSnotcomplete. NoAPI/webdeploy/rightschange. Nextcloseallocation/compatibletransport-use/treatment/backgroundactualdata;donotclaimfullLCIor0CO2e.

## LCI/web/database expert review — 2026-11-05
Readlocalmodels/schema/proxyevidenceandliveproductioninventoryAX+screenshot(FAME10/partialwarning). Reviewdocs/lci-web-expert-review-2026-11-05.mdprioritizescompatibility/allocation,independentvsconstructedbalance,versionedscenario/runrelations,local-vs-webdeliverygap,UXinformationhierarchy/significantfigures,andproxytrycloudflare-onlycoupling.Noupdates/deploy/testsclaim;currentUIhonestbutnew55rowscenariosstilllocal. ScopeThai-specificvsforeignsurrogateneedsdefinition,nopolicyoverride.

## T108 expert-review engineering — 2026-11-05
Added sealed content-addressed local activity model DB (130 sources/9datasetversions/6runs/330results), transactional FK membership and Decimal replay; immutable post-seal guards. Added rights-aware B100 case metadata/UI with6choices/4processes/actual-source links/rounded+exact quantities/open gates, no2019restrictedinventorypublic. Proxy exact-origin allowlist prepared server-side, env unchanged. 208tests passed plus14post-source-link frontend/release checks; local desktop/mobile390x844 and selection/27.0600/source links verified, screenshots output/review-2026-11-05. 12file Vercel source package ready, NOT deployed; EC2/MySQL/S3 unchanged. CURRENT_ARCHITECTURE.md resolves historical design status. T108scopedengineeringDONE;T107scientificcompatibility/allocation/transport/use/treatment/background remainsIN_PROGRESS;no fullLCI/CO2total/independentbalance/openLCAimport/userstudy claim. See evidence/expert-review-implementation.json and docs/expert-review-implementation-2026-11-05.md.

## T107 gate-closure follow-up — 2026-11-05
Reviewed7sourcepassageswith2PDFextractors;economic70/30confirmedbuttablegross/allocatedbasisunknown;26.27vs26.3kgconsistentdisplayroundingnotlitre/MJbridge. NewCOMPETEThai61pagePDFdownload/hashprivate;Sect3.1PDF11–13productiononly/combustiondeferred,0rowsimported. Sixexplicitgate decisions/required-evidence recorded evidence/fame-gate-closure-review.json;3new+4chain=7testspass. No burdenlink/allocation applied/CO2total/deploy/productionchange. T107remainsIN_PROGRESS;nexttable-specificworkbookandmatchedThaiuse/fuelpropertyevidence;do not treatpublicationyearasmeasurementperiod or generationasleakage.

## Detailed system expert review — 2026-11-05
Readschema/store/chain/lifecycle/API/proxy/deploy/SRS and liveinventory;5read-onlyURLs:health/ready/productinventory/reference200,newcaseJSON404. Publicreference97rowsNOT_CLEARED/profileLOCAL_RESEARCH_REFERENCE confirmed;needsdistributiondecision,notlegalviolationclaim. Fourisolatedmemoryprobes reproduced:missingJSONamountpassesCHECK,wrongprocessdatasetmembershipaccepted,emptyauditreturns0withFKtrue,anddoubledCPOactivity/resultswithstaleedgesaccepted. No actualsourcecorruptionorproductionexploitclaimed. Report docs/system-expert-review-2026-11-05.md has15prioritizedfindings/criteria/sequence;evidence/system-review-*.json. No maincode/schemafix/deploy/EC2change/fulltests rerun;208testspreviousnotnew. NextfixR02–R05beforemigration;closeLCIevidence/flowmapping/publicprojection;thenmodelAPI/UX/SRS/operations.

## T109 apply15review findings — 2026-11-05
FixedR02–R05:sourceJSONpresence/type,processmembership,endpointquantityreplay+edge-set,completecounts/runmanifest/seal+orphanrejection. Fourmemoryprobesnowrejectall. Sealedmodel657aa71137bdcd70d11ed3e15b0aa1066246393c409517f757a0a10d9ddec89f/130sources/330results. MySQL8.4.13equivalenttestedowner-markedtemporaryschema130payload/330resultallcells+5negativeexpectederrorcodes,APIreadybefore-after,cleanupdone,noproductiontables/APIimagechange. 219fulltestspass;frontendcleanroom12files/9assets. Addeddecisionbinding,flowcontract130with0eligibleelementary/CFnull. Vercel dpl_BoUuYRBhKZS8TFU9HYZyUBauyFXi live10routechecks/modelmetadataallfieldmatch/appassetmatch;publicreference97metadataonly/CSV-reports403;Thai flowlabels/casecontextclarityverifiedbrowser. SRS0.7.1PDF28pages/render28+newactivityERD. Reviewmatrix docs/review-implementation-2026-11-05.md;T109IN_PROGRESSnotallscientificgatesclosed;T107stillopen. Remainingactualallocation/compatibility/Thaiuse-background/waste/elementarydata,stableendpoint,humanreview/UAT/openLCA/fullresearchcleanroom. NoGitpush/rawpublic/subagents/automation/messages/domainpurchase/Ginder-Caddy-SGchange.

## T110 Friendly statistics UX — 5 November 2026
ผู้ใช้ชอบอีโมจิเพราะช่วยอ่านสถิติไม่น่าเบื่อ:เพิ่มไอคอนพร้อมข้อความ/5ปุ่มเลือกสถิติและ2มุมมองโรงกลั่น/การ์ดจำนวนรายการปีหน่วยตามตัวกรองจริง ไม่รวมค่าต่างหน่วย;ยุบผลเทียบแหล่งข้อมูลรองไว้ในdetails หน้าแรกหัวเรื่องเดียวและ5topiccards. 13targetedtests/cleanroom/32releasechecks/liveassethashesผ่าน ตรวจdesktopและmobile390ไม่ล้น ขึ้นVercel dpl_8EhVpAddLmxTd9P2sehEKPe2gyFR rollback dpl_BoUuYRBhKZS8TFU9HYZyUBauyFXi ดูevidence/friendly-statistics-ux.json ไม่เปลี่ยนข้อมูล/backend/LCIstatus;T107/T109scientific/externalgatesยังค้างตามเดิม.

## T111 Motion UX — 5 November 2026
เพิ่มfinite page enter/summary stagger/button press/hoveremoji,เคารพreduced-motionและcancelแอนิเมชันก่อนหน้า ไม่แก้ตัวเลข ไม่มีtimerloop. 13frontendtests+motionguardtest/cleanroom/live3assethashes+modelreleaseเดิมผ่าน deploy dpl_9LjuP2FBh37D8r4FsR7geUTQmvf7 rollback dpl_8EhVpAddLmxTd9P2sehEKPe2gyFR. Browser visualยังตรวจไม่ได้:browser.user unavailable ไม่อ้างตรวจมือถือหรือภาพเคลื่อนไหวจริงในรอบนี้ ดูevidence/motion-ux.json;ขั้นถัดไปvisualQAเมื่อbrowserกลับมา ไม่มีbackend/datachange.

## T112 Scroll-driven fuel story — 5 November 2026
ผู้ใช้เลือกภาพเล่าเรื่องแทนmicroanimation:สร้าง5SVGscenesต้นทาง/โรงกลั่น/รถ/เมือง/บำบัด,sticky+IntersectionObserverและnumberednavigation พร้อมลิงก์จากNSOและลิงก์ไปข้อมูลแต่ละช่วง ข้อความแยกconceptualpetroleumกับB100/ไม่อ้างfullLCI. ตรวจheadlessChromeจริงlocal/live natural-scroll/click/reducedmotion/link/errors/mobile390ไม่มีoverflow;แก้mobilekickerใต้ภาพแล้ว. 13tests+2behavior suites/cleanroom/live3hashesผ่าน deploy dpl_Dyqy1gp5WcA8X1iXfm4YQcjTF6VW rollback dpl_9LjuP2FBh37D8r4FsR7geUTQmvf7. ภาพoutput/fuel-story/live-*.png evidence/fuel-story-ux.json ไม่แก้backend/data;เครื่องมือPlaywrightใน.localไม่ส่งขึ้นเว็บ ไม่มีframeworkdependencyใหม่ ข้อค้างscientificเดิมไม่เปลี่ยน.

## T113 Thai readability and data-map — 5 November 2026
ฝังNotoSansThaiWOFF2พร้อมOFLในCSSไม่พึ่งCDN,body16/story18/notes14pxเพิ่มcontrast;5categorymapและมีในเว็บตามฉาก;รถ/progressตามscrollใช้1queuedrAFไม่loop. Local/liveChromefontloaded/4textcontrast6.25–7.86/320-390nooverflow-nooverlap/storylinks/reducedmotionผ่าน.13tests+2nodesuites/cleanroom/32consistency/live3hashesผ่าน deploy dpl_AGT7vMdWaEpSmzejavDBGJK3EpCw rollback dpl_Dyqy1gp5WcA8X1iXfm4YQcjTF6VW. evidence/story-readability-ux.json ภาพoutput/story-readability ไม่เปลี่ยนข้อมูล/backend/scientificgates;ไม่อ้างfullWCAGcertification.

## Expert review — 6 November 2026
Read-onlyliveChrome/6HTTP/source-schema review พบrouteB100h2top-59.2/focusBODYหลังstorylink,NSOdiesel20242rowsแต่reload69เพราะfiltersไม่อยู่URL;mobileข้อมูลจริงต่ำกว่าfold,capability/metadataexportclarity,largeCSSfontbase64/duplicatedstyles. APIready200/reference97metadata/CSV403/fullfalseCO2null. เก็บ15findings+phasedplan docs/expert-review-2026-11-06.md evidence/expert-review-2026-11-06.json ไม่แก้โค้ด/production/ข้อมูล ไม่รันfulltestsหรือsourceauditซ้ำ. ขั้นต่อไปroutefocus+shareablefilters+mobilehierarchyก่อนเพิ่มeffects;LCIallocation/compatibility/elementarygatesยังเปิด.

## T114–T117 Apply expert review — 6 November 2026
DeliveredVercel dpl_Wz7EhN4xyjaj2aUsuFp56wjyhLeB rollback dpl_AGT7vMdWaEpSmzejavDBGJK3EpCw:routefocus/historyscroll,validatedNSOURLfilters,2rowcontextcomparison(noarithmetic),mobilecollapsedfilters/capabilitycards/technicalmenu;discovery/story/theme modules and hashedfontOFLasset;compactNSO433169→146019bytes/live273allfieldhydrate;perdataseterror/client35s/EPPOabort.226fulltests+15finalARIA-targeted;axe3pages0violations(incomplete/manualstillopen);local/livebrowser320/390keyboardhistory pass.17source/14assetcleanroom/livehashes. Decimalcandidate460rowsMySQL8.4.13/453eligible7excluded/noround;localworkflowtests,noauthservice/noDBmigration. FreshprivateS3backup20261105T192449Z/AES256;ownlocalrestore5schemas/livecanonical56,887,016byteshashmatch;noEC2image/Ginder/Caddy/SGchange. ReadinessHTTPhealthy/backupfresh/stableendpointfalse. T114IN_PROGRESS(scientific/human/stableendpointgates),T115-117DONEscoped. docs/review-implementation-2026-11-06.md/evidence/review-implementation-2026-11-06.json +SRSaddendum(PDFnotregenerated). Diskfullfirstreportwritefailed,recreatednonemptyafterdeletingonlyownverifiedrestorearchivecopy;developerdrive~100MBfree needsownerattention. NoGitpush/subagents/automation/newscientificimports. Nextrequiresmatchedscience/hostname/humanreview;do not claimallgatesclosedorloopoldtests.

## T118 Research-led decisions — 6 November 2026
Userreaffirmedteamresearch/decidewithoutMTECapproval. AcquirednewPNU2021B100enginePDF626677bytes/hash48a242.../18pages,9propertiesTable1–2PDF9printed284checkedpdfplumber+pypdf+visual. LHV39.89headerMjmissingdenominator/density862.79kgm3;teamscenarioexplicitMJ/kgassumption1000MJ→25.06894kg/29.05567L allowedonlywithassumptionID;3newtests pass. NoCO2e/emissionfactor/baselinechange/publicraw. ContextspecificNissanIDI/PNUfuel,yearnotmeasurement;vol%/ppmnotmasswithoutflow. MDPI576page429/PDFunavailableloggednotretried. docs/research-decisions-2026-11-06.md/evidence/thai-b100-properties-2021.json/sourceacquisitionupdated. Drivefree~5.8GBnow(owner/externalstatechange,notclaimedcleanedbyagent). Nextmatchedexhaustmass/CH4N2O/fuelbasisresearch;notMTECapproval.

## T119 Try research-led scenarios — 6 November 2026
Useraskedtry:built2fuelbasis×ThaiLCIreportedEFscreen(27.27836vs26.001504kgCO2e,-4.68084%basis-sensitivityNOTcarbon saving),noassignstageboundary/noforegroundsum. ReviewedCFP230–233subsetfromhashsnapshot;3tkmloadings×3hypotheticaldistances=9screens,kmunitguard/nodoubleloading/noemptyreturnguess. Thai2026DPFpaper403candidate;Korea2018excluded;CFOstationarynotroad,blankCH4/N2Onotzero.2newbuilders/transporthelper/7relatedtests passed. docs/fuel-and-transport-sensitivity-2026-11-06.md and evidence/fuel-basis-sensitivity.json/transport-sensitivity.json. Internalonly/NOT_CLEARED/noexistingmodel/web/EC2change/fulltotalnull. NextmatchedThaigas-massinventory/returnboundary evidence,notMTECapproval.

## T120 Thai wastewater source screening — 6 November 2026
NewCDM2076LamthapKrabi2013candidate;participant corroborates coveredpond/biogas system. Web-reader text only;rawdownload212byteHTML/notPDF;nohash/visual/dualparser claim. Held7numericcandidates and5issues incl provisional29389vs21131 arithmeticgap8258, electricityunits/GWP21/site-denominator/flowsemantics. docs/thai-lamthap-candidate-review.md and evidence/thai-lamthap-candidate-review.json. Noimport/baseline/publication/productionchange;fulltotalnull. Nextobtain genuineversionedPDF via newofficialcue and verify selectedcells beforepromotion;notwaitingMTEC.

## T120 revision follow-up — 6 November 2026
IssuancehistoryofficialSIRIM1402397031.65 listsV4Jan15/revisedER11Feb15/verification andIssued22May2015/CER40326 vsoldV01May2014text21131. This isversionreconciliationnotprovensourceerror. New2directdownloadsHTTP200HTML850/844bytesnotPDF;calculationwebreaderunavailable. Addedrevisionprovenance/6thissue/sourceacquisitionmanifest. Zeroimport/noexistingmodelorproductionchange. NextrequiresgenuineV4/verification/calculationnormalaccess thenallselectedfielddiff/CPOdenominator;noURLretrywithoutnewcue.

## T121 Same-site denominator investigation — 6 November 2026
NewRSPOprimaryauditor2015reporttext62pages:2014certifiedestateCPOcalculated/notwholemill;cannotdenominate2013CDMwastewater. PDF34water310100/FFB196145→1.58097vsreported0.63provisionalissue. RawHTTP403/screenshotcachemiss,nofakehash/visualclaim. scripts/review_lamthap_denominator.py/evidence/thai-lamthap-denominator-review.json preserve5blockreasons/noimport/nullnormalizedandCO2total. Manifest/boardupdated. ThisresearchbranchlimitedbyactualV4raw andmatched2013wholemillCPO;noURLloops/noproductionchange.

## T122 Full-chain example search — 6 November 2026
10Thai-fuelcase screening acrossB100/ethanol/UCO/CNG/gasoline;primarySpringerconfirmsThai2008cassava+molassesWTW/fullchainstudies,fulltextaccesspending(useraskedhowlibraryaccess). NewactualUCO2022PDF33pages/hash715ee2... andWTW2025PDF11pages/hashe153daa...;scopepage5bothdualparser+visualchecked,notallinventorycells. UCOexcludescollection/transport+foreignbackground;WTWopenCCBYmethoddemo,notfullinventory. docs/thai-fullchain-example-search.md/evidence/thai-fullchain-example-search.json. Noimport/productionchange/fullclaim. NextuserinstitutionalPDFthenallfieldreview;researchpreviewpossiblewithhonestlabels.

## T123 User fulltexts acquired — 6 November 2026
Userdownloadedcassava685577bytes8pages/fc6c643... andmolasses557359bytes11pages/fa0c483...;privatecopies/manifests. Selectedscopefiguresvisual and3cassavatransportrowsallfield2parsers+visualverified;molasses12/88spentwash and89.6/10.4economicallocationchecked. Recommendmolassesfullchainstudydemo;notcompleteelementaryLCIdataset/notallThai background. CassavaTable4acidification3.00→3.07vs−6.8visuallyinconsistent;holdrow/nosilentfix. scripts/review_thai_ethanol_2008.py/evidence/thai-ethanol-2008-review.json/docs/thai-ethanol-2008-demo.md. Searchaccesspendingstatussuperseded. Noexistingmodel/productionchange/publicraw. Nextremaininginventory/impactcells/providerreviewbeforequantitativeimport.

## T124 Both-book completion audit — 6 November 2026
Bothfulltexts gapreview/Fig1PDF2visual;molassesphysicalbatch→equal13.46kmFUwithE10~1.011269722L. src/ethanol_demo.py3testspass(noeconomiccutofphysicalmass/noGHGtotal). build/evidencecomplete-gapreport12stageentries;fullLCIfalse. MolassesTable2procedure/Table5LCIA;neatethanolusedataunavailablePDF8;CassavasettledsludgedataexcludedPDF2,Table4LCIA. CompanionEnergyPolicyDOI10.1016/j.enpol.2008.01.008publisherexplicitTable7LCIidentified/userdownloadrequestedasync;notimportedsnippet. docs/ethanol-demo-completion.md. Noexistingmodel/productionchange/rawpublic. NextactualcompanionPDFthenallselectedgasrows/basiscompatibility;cannotrecoverunpublishedunitprocessinventoryfromLCIA.

## T124 access change and open alternative — 6 November 2026
UserconfirmedTUdoesnotsubscribeEnergyPolicycompanion. No purchase/credentialrequest. FoundactualopenCOMPETEauthorinstitutionJGSEEreportMarch2009,61pages742013bytes/SHAeb487f...;PDF20Table7visual showsgCO2eq/Lethanol/IPCC2001NOTphysicalgasinventory/notthesameTable7asEnergyPolicy. evidence/ethanol-open-access-followup.json. Noimport/productionchange;notwaitinguserpaidaccess. Nextauthoraccepted/thesisphysicaltableoruserchosenlibrarydelivery;do notreverseCO2eq/roundedcostsintogasLCI.

## T125 Carbon calculator and source replay — 6 November 2026
Addedgascharacterization/guardedpartialsum,7targetedtests pass. MolassesFigure1stillage106.8L/BODapprox40gL×88percentpond×Table3default0.22→0.8270592kgCH4/tcane;IPCC2001GWP23→1870.44gCO2e/Letoh matchesCOMPETEpond1870integerrounding(<0.5),same-researchreplaynotindependentvalidation. Equal13.46kmE10basispond-only~0.18915kgCO2e/notwholefuelvehicleimpact. sourcefactorPDF5twoextractors+visual;GWPTable7footnotevisual. docs/ethanol-carbon-calculator.md/evidence/ethanol-carbon-calculator.json. Historicdefaultapproxconditional/private/notThaiempiricalfactor;fulltotalnull/noexistingmodelorproductionchange. Nextmatchedmissingstages/capturedgasleakage/combustion/transport/gasoline/use notzeros;noGWPmix.

## T126 Available-stage completion — 6 November 2026
COMPETEPDF18energyandPDF20GHGvisualreview;17contributionrows×2years34cells rastervisualtranscription/provenance/privateCSV. Parentchildrenallmatch;stage+credit totals0.1different withinrounding;2006percent31.3vs819.8/2638.9~31.1held/sourceprose31.1. src/reported_balance.py3newtests guardsparentchildduplicate. ReportedgCO2eqcontributionsNOTgasLCI;labourincluded andproductionboundaryNOTE10WTW so nojoiningtoexistingdemo/pondaddition. docs/ethanol-reported-stage-review.md/evidence/ethanol-reported-stage-review.json. Noexistingmodel/production/publicchange/fulltotalnull. AvailablebranchnowrequiresnewphysicalLCIsourceorclearlyseparatedassumptions,notzero-fill/oldURLloops.

## T127 New Thai acquisition inventory research — 6 November 2026
AcquiredSIIT2025doi10.14456/scitechasia.2025.60PDF15pages383076bytes/SHA4a3d9d...;18Table8quantitiesallnumeric2parsers+visualrowmapping;Table9visualconfirmslime100percentallocationarithmeticconflict/Table6vs9caneEFconflicts/ROprecision+scope+foreignbackground6issues. Newcaseacquisitiononly/not2008link/nofullclaim. scripts/review_ethanol_siit_2025.py/evidence/thai-ethanol-siit-2025-review.json/docs/thai-ethanol-siit-2025-review.md. Bibliographicthesisnotactualfulltext/KUraw404logged,noloops. NextactualDEDEThaiEnvironmentFoundation2007sourceorcompatibleinventoryexport;noexistingmodel/productionchange.

## T128 official DEDE ethanol survey — 2026-11-06
Acquired actual DEDE bioethanol1 waste21p and bioethanol2 PCD use26p PDFs/private manifests. Table2PDF11 all26quantity cells numeric+visualchecked:24ranges/2dash preserved. Decimal source150000L/day normalization, no pairedplant/measurementyear/airCO2/parentchildsum/CH4 inference. evidence/dede-ethanol-survey-review.json. UsePDFlegacyThaiencoding means absoluteinventorynotyetverified;nextvisualunit/testcontextreview. HistoricalDEDE2550LCIreportnotacquired. No production/publicraw/fullLCI/CO2total change.

## T129 verified-source foreground selection — 2026-11-06
DEDEFigure6PDF12all11arrows/t/day/directions2parsers+visual;5Decimalbalancespassprintedrounding (distillation/factory−0.01t/day). Sourcephysicalexampleverified notactualplant/measurementyear/completeenergy/airCO2/fullLCI;recyclesexcluded. docs/verified-thai-ethanol-example.md/evidence/dede-molasses-balance.json. New2022Energies9515PDF21pSHA2367ac...actualLAPSEcopy;scopeproduction-wastescenarios/foreignbackground/74-26allocationnot2008;A7visualcandidateonly. No model/production/publicrawchanges. Next samecase energy and waste fate or matched wholechain actualinventory, notpercent/use orforeigncasepadding.

## T130 missing-use evidence — 2026-11-06
Acquired actual ThaiAER2017vehicleCO2PDF10pSHAe4f87bc...;6LDGgasohol91/E20speedconditions12mean±numericcells2parsers+visualPDF6;methods5vehicles/fuel2000ccEUROIII2005standardnotmeasurementyear. Decimal10kmexamples onlytotalCO2, fossil/biogenic/CH4/N2O/supplierunknown;no2008/DEDEjoin. docs/ethanol-missing-parts-review.md/evidence/thai-vehicle-co2-review.json. Plantenergy/transport/waste remainmatchedcasegaps;duplicateDEDEsurveycitationsnotindependentvalidation. No production/rawpublic/fullLCIsum.

## T131 proxy-method support — 2026-11-06
PrimaryGHGProduct8.3.6/7/10webPDFsupportssecondaryproxy/DQI/gapestimates;local403explicit. ActualIPCCmobile78pSHA b0b7d96.../wastewater28pSHA20b27f...;carbonorigin/CH4N2O/CODsludgerecoverymethodreview. CorrectsameplantasabsoluteSCENARIOblocker:5bridgesdocumented;stillnotmeasuredsameplant/fullchainproof. NoforeignEFadoption/CO2total/productionchange. docs/ethanol-proxy-method-support.md +evidenceJSON. NextselectexplicitThai-rangeenergy/transportscenarioandfuelconsumptionbridge,scientificinputsremainopen.

## T132 ethanol proxy scenario — 2026-11-06
Addedsrc/ethanol_proxy_scenario.py+builder:DEDEFigure6mass1Letohbasis/Table2molassesenergyrangeproxy,2separatefreightlegs×hypothetical10/50/100km/TGOCFP23275percentloadingnotappliedtwice. Decimal60/sourcehashDEDE+TGOchecked/4targetedtestspass. evidence/ethanol-proxy-scenario.json+docs/ethanol-proxy-scenario.md;notmeasurementsameplant/notfullLCI/noautomaticlegsorGHGsum/noforeignEFadded/noexistingmodel-productionchange. NextThai electricity/boiler steam sourceandboundary plusperkmfuelbridge/wasteinputs/allocation;nooldsource/testloopswithoutnewwork.

## T133 ethanol assumption validation — 2026-11-07
Two Thai source PDFs checked with hashes and page markers. CMU Table4.5 electricity 0.3095 kWh/L and steam 2.9 kg/L above DEDE ranges, retained separately. TSRI interview estimate 150–500 km round trip and two truck fuel rates produce conditional diesel intensity ranges. Inbound pipe is a candidate with distance unverified. Site identity, route logs, and energy records remain open. See docs/ethanol-assumption-validation.md and evidence/ethanol-assumption-validation.json.

## T134 Thai wastewater benchmark — 2026-11-07
World Bank P110095 appraisal and implementation PDFs checked via web. Derived 11 and 6 L vinasse per L ethanol before/after evaporation using appraisal quantities. 2013 grid replacement recorded separately. Methane inventory still requires matched monitoring data. Local TLS download failed. See docs/ethanol-tsm-wastewater.md.

## T135 TSM boundary follow-up — 2026-11-07
World Bank audit confirms about 60 km waste haul and nearby sugar mill steam supply. Derived conditional 0.36 m3 km/L ethanol on appraisal basis. UNFCCC ex-ante estimate kept separate. PDD web timeout, matched methane and production not found in reviewed public reports.

## T136 Thai vinasse experiment — 2026-11-07
Verified ThaiScience abstract for 300-day laboratory trial. Shared-influent COD removals sum to 73.6%. Methane conversion up to 97% retained as experiment metric. TSM capture and emissions still unknown. Evidence: evidence/ethanol-uasb-lab-benchmark.json.

## Expert review — 2026-11-07
Read-only local and live review. 245 Python tests passed. 7 public route checks, headless Chrome three views at 390/1440. Reproduced ethanol builder evidence mismatch in temporary copy: mass evidence mutation leaves freight unchanged, energy mutation accepted with original source hash. Review across LCI, database, UX, frontend, and operations in docs/expert-review-2026-11-07.md.

## T137 review fixes — 2026-11-07
Ethanol builder uses source observations and hash-pinned extracted inputs. Local metadata cases with shareable routing, 5000-row export limit, proxy overall deadline and disconnect cleanup. 247 tests and local Chrome 390/1440 pass. Production deployment, full versioned persistence, user testing, endpoint and science gaps tracked in docs/review-implementation-2026-11-07.md.

## T138 review verification — 2026-11-07
Isolated replay of 10 pinned files is byte-identical. Internal SQLite registry records four immutable case drafts and zero actual approval events. Public cleanroom 17 files / 14 hashes pass. Proxy mock verifies deadline 504 and upstream disconnect cancellation. External review gates remain tracked.

## Ethanol self-review — 2026-11-07
User authorized Codex self-review. Four evidence files matched their immutable registry versions and received scoped internal-use approval. See evidence/ethanol-internal-self-review.json. Publication workflow and source rights are separate.

## Ethanol source cards — 2026-11-07
Local frontend includes attributed Songkitti 2022 CC BY E10 cold-start values with conversions and a metadata-only JSEE bagasse case linking to Table 1 PDF page 4. Cleanroom build and Chrome 390px direct-link/case-switch checks passed. Production deploy remains pending.

## Ethanol public release — 2026-11-07
Promoted dpl_CYLwYSyHEyp5p5hEbXHCyBfHAUkP after staged HTML/readiness checks. Live HTML and app asset hashes matched, four endpoint checks passed, Chrome 390/1440 confirmed E10 deep link and bagasse switching. Rollback dpl_Wz7EhN4xyjaj2aUsuFp56wjyhLeB. Evidence: evidence/current-frontend-release.json.

## Ethanol allocation replay — 2026-11-08
Verified local JSEE 2014 PDF hash and replayed all 33 economic, energy and exergy allocation factors in Tables 4–5 from reported quantities and per-unit weights. All match to three decimals. Documented the separate mill/CHP allocation steps and steam burden loop in docs/ethanol-whole-cycle-reference.md. DEDE/TSM factors and total remain null pending matching process data. Rights remain NOT_CLEARED.

## E10 full driving-cycle reference — 2026-11-08
Matched six E10 vehicles by ID in Sirithian et al. 2022 Tables 1, 3 and 4 using the authors' full-text copy. Derived sample means for tailpipe CO₂ and CH₄ across the Bangkok driving cycle. Recorded locators, CC BY 4.0 notice and scope in docs/ethanol-whole-cycle-reference.md. PDF hash, matched fuel consumption, carbon split and N₂O remain unverified. No model total or production change.

## TSM production denominator review — 2026-11-08
TSM plant page and BBGI 2024 plant table report 200,000 L/day capacity. Kept separate from P110095 appraisal capacity of 100,000 L/day and from unknown period-matched output. Recorded in docs/ethanol-tsm-wastewater.md. Methane intensity and lifecycle total remain null.

## TSM fermentation CO₂ boundary — 2026-11-08
Verified the operator's July 2025 announcement of biogenic CO₂ capture at Tha Mai. Documented capacity separately from actual captured mass and historical wastewater CH₄ in docs/ethanol-tsm-wastewater.md. CO₂ capture intensity and avoided emissions remain null pending matched operating data and end-use evidence.

## Northeast ethanol production benchmark — 2026-11-08
Checked the DTU proceedings PDF text, printed page 86 Table 1 and sections 3.1–3.2. Converted published base and improvement impacts to kg CO₂e/L. Kept the mixed-background production benchmark separate from Thai-only project calculations and the 2008 cradle-to-use reference. Visual, hash and redistribution checks remain open.

## Qdrant retrieval prototype — 2026-11-08
Added four public evidence cards, a FastEmbed/Qdrant Local indexing and search CLI, and a separate parameterized Cypher example for the inventory lab. Python and JSON syntax pass. Dependency installation stopped with disk full and Docker Engine was unavailable. Verify index and retrieval after freeing space. No generated answers or deployment in this round.

## Qdrant retrieval verified — 2026-11-08
Installed isolated dependencies after disk cleanup and indexed four 384-dimensional embeddings. Offline queries ranked the expected card first in all four in-scope Thai smoke cases and returned no results for one off-topic question after applying the pilot 0.45 cosine cutoff. All returned cards had source URLs and locators. Scores and limits are recorded in docs/rag/README.md. Next validate with independent questions, then connect answer generation and approved observation IDs for Cypher. Docker Engine unavailable this round.

## Local evidence question UI — 2026-11-08
Added loopback browser demo and optional Qdrant Cloud configuration. Real HTTP checks returned expected evidence at ranks 1 and 2 for two Thai paraphrases and no hits for an unrelated question. Blank, malformed and cross-origin requests were rejected. No live Cloud, LLM or Cypher integration verified.

## Optional Gemini synthesis — 2026-11-08
Added opt-in Gemini 2.5 Flash-Lite synthesis of retrieved public cards with validated source IDs and evidence-only fallback. Local Qdrant HTTP checks passed; Gemini response, invalid citation, quota and timeout branches checked with mocks. No key was configured for live verification. See docs/rag/README.md.

## CDM 3334 wastewater comparator — 2026-11-08
Checked the Pornvilai monitoring report for February–July 2018. Gross generation minus auxiliary demand matches reported net export at displayed precision. Recorded the unit label and distinguished calculated biogas volume and default capture efficiency from measured net CH₄. See docs/ethanol-tsm-wastewater.md. No matched ethanol output verified and no join with TSM.

## Codex teammate handoff guide — 2026-11-08
Added `CODEX_PROJECT_GUIDE_TH.md` as a portable Thai context guide covering the project purpose, latest data statuses, LCI evidence rules, architecture, graph experiment limits, clone/runtime caveats and recommended reading order. It summarizes existing evidence and points back to source documents; it adds no data, approval, deployment or test claim. Pushed 482 source/documentation/evidence files on `codex/share-project-with-teammate`; generated `output/` and `tmp/` artifacts are excluded. Remote branch is ready for the teammate to pull.

## SRS full draft — 2026-11-08
Created `C:\Users\HP\Downloads\S2-G05_W12_A4_M2_SRS_Full_Draft.docx` from the original M2 SRS template. Retained and refreshed chapters 1–3, added requirements/use cases plus chapters 4–8, kept SRC-01–SRC-18, and distinguished production schema, candidate/local models, and unknowns using repository evidence available through 8 Nov. Added Rev 0.2 as a draft pending team review; contribution and approval fields remain unfilled. Word COM export rendered 33 A4 pages; visually reviewed pagination, TOC, tables, and typography (TH SarabunPSK: chapter headings 18 pt bold, subsections 16 pt bold, body/tables 14 pt; table headers bold). Packaged `render_docx.py` remains unavailable because LibreOffice `soffice.exe` is not installed; Word export and Poppler were used for visual QA. Original source SHA-256 remains `85C351381499969194AF25B71AA9AA977D0BB232F5653436D6417A059D5B24F9`. Open items: team review/sign-off, contribution entries, and refresh evidence if branch/release changes before submission.

## SRS DOCX format repair — 2026-11-08
Built `S2-G05_W12_A4_M2_Updated_Original_Format.docx` in Downloads from the original template to restore its A4 layout, front matter, TOC, definitions/references/source-analysis/user/DR/BR/FR tables, and section styling. Added Rev 0.2 plus current architecture and bounded TSM/Tha Mai constraints from the updated draft; refreshed manual TOC page numbers. Verified 19-page A4 rendering in Microsoft Word and inspected all pages; all 12 tables and chapter 3 remain. Packaged `render_docx.py` could not run because LibreOffice `soffice.exe` is absent, so Word PDF export was used for visual QA. Original and Updated inputs remain unchanged. Follow-up: confirm whether the SRS cover/TOC should remain labeled M1 while the filename is M2.

## SRS F3 template alignment — 2026-11-08
Updated `C:\Users\HP\Downloads\S2-G05_W12_A4_M2_SRS_Full_Draft.docx` to revision 0.3 using the CN230 F3 Full Report and chapter 4–8/Serving Layer templates from the Google Drive folder supplied by the user. Kept the SRS as one evolving M1–M4 volume; aligned chapters 4–8 to ERD/cardinality, relational schema and dictionary, source mapping, extraction/validation/provenance, requirement→query→result traceability, Thailand/unit/SRC checks, Graph + Semantic Search serving evidence, contribution/memo register and attachment checklist. Production schema remains separate from candidate/local models; contribution/sign-off fields remain unfilled; M1 memo date is marked approximate and requires file confirmation. Added complete manual TOC page numbers and fixed subsection-heading pagination. Word COM produced a 38-page A4 PDF; all pages were visually inspected across the final render cycle, including TOC and changed chapter pages. Representative typography confirmed TH SarabunPSK: chapter headings 18 pt bold, subsection headings 16 pt bold, body/tables 14 pt. `render_docx.py` was attempted but cannot run because LibreOffice `soffice.exe` is unavailable; Word export plus Poppler was used for the visual QA. Original source SHA-256 remains `85C351381499969194AF25B71AA9AA977D0BB232F5653436D6417A059D5B24F9`. Open items: team confirms content and source snapshots, verifies actual M1 memo, fills contribution and real evidence links, then refreshes evidence before submission. Draft is not final or team-approved.

## รับช่วงเครื่องใหม่: งาน 1–2 — 8 พฤศจิกายน 2569

- ตรวจจาก `67db1ad` สถานะก่อนเริ่มสะอาด; Python 3.13.3/Node 22.12.0; frontend build และ isolated allowlist ผ่าน เปิด Explorer/metadata HTTP 200 แต่ records/NSO/reference 503 เพราะไม่มี raw/build snapshot; Docker Linux engine ติดต่อไม่ได้ ไม่ restore หรือเปลี่ยน production
- ติดตั้ง RAG environment แยกและดาวน์โหลดโมเดล สร้าง Qdrant Local จริง 4 การ์ด/384 มิติ; ค้นออฟไลน์ได้; HTTP demo 11 checks ผ่าน ตรวจข้อความ/ที่มากลับตรง corpus โดยไม่เรียก Gemini/Cloud
- คำถามใหม่ 24 ข้อ: ในขอบเขตอันดับแรกถูกและผ่าน cutoff 11/12; ไม่มีคำตอบปฏิเสธ 7/8; กำกวม 4 ข้อแยกรายงาน พบ E20/N₂O คืน E10 ผิดขอบเขต และ Songkitti/cold start ค้นไม่พบ; เทียบ 6 cutoff แล้วยังคง 0.45 พร้อมข้อจำกัด ไม่ถือว่ารับรองคำตอบ ปรับหน้าค้นให้แสดงขอบเขต 4 การ์ดและข้อจำกัด
- Frontend tests 12/13 ผ่าน อีกข้อขาด `build/product-inventory/report.json`; ไม่สร้างข้อมูลแทน ไม่มี browser visual check ในรอบนี้
- รายงาน/วิธีเปิด `docs/local-readiness-2026-11-08.md`; ผลรายข้อ `evidence/rag-local-evaluation-2026-11-08.json`, `evidence/rag-local-http-2026-11-08.json`; เพิ่มคำถามและ scripts ตรวจซ้ำ
- ขั้นต่อไป: snapshot/manifest จริงและ Docker สำหรับระบบวิจัยเต็ม; ปิด evidence sufficiency และทดสอบคำถามจากสมาชิกก่อนต่อ Gemini/กราฟหรือใช้งานจริง ไม่ปรับคะแนนเพื่อให้ชุดประเมินดูผ่าน

## แก้การค้นผิดขอบเขต — 8 พฤศจิกายน 2569

- เพิ่ม `scripts/rag_scope.py` และทะเบียน `docs/rag/retrieval-scope.json` ผูก corpus hash; กรองเชื้อเพลิง/สาร/ช่วงทดสอบ/คำถามปริมาณก่อนคืนผล เพิ่มคำค้นไทย–อังกฤษโดยคง raw cards/index/cutoff 0.45 เดิม HTTP/CLI ใช้เส้นทางเดียวกัน
- คำถามเดิมในขอบเขต 12/12 (เดิม 11/12), ไม่มีคำตอบปฏิเสธ 8/8 (เดิม 7/8); คำถามเพิ่ม 26 ข้อผ่าน 8 positive+18 negative; อีก 4 ambiguous จากชุดเดิมไม่ให้คะแนน ผลเป็น development/regression ไม่ใช่ held-out หรือ human review
- Unit checks 5 tests และ HTTP 15 checks ผ่าน รวม E20/N₂O/hot-start ไม่คืน E10 และคำถาม Songkitti/cold start ค้นได้; ข้อความต้นฉบับ/ที่มาคงเดิม หลักฐาน `evidence/rag-scoped-*-2026-11-08.json`
- รายงาน `docs/rag/scope-fix-review-2026-11-08.md`; ไม่มี deploy/production DB/Cloud/Gemini หรือ browser visual check รอบนี้
- ข้อค้าง: กฎครอบคลุมเฉพาะคำ/มิติที่ระบุ ไม่ใช่ general semantic verifier; คำกำกวมยังอาจคืนการ์ด ต้องรับคำถามอิสระจากสมาชิกและตรวจขอบเขตทุกครั้งที่เพิ่มการ์ด

## เพิ่มการ์ดหลักฐานค้นได้ 4 → 10 — 8 พฤศจิกายน 2569

- เพิ่ม 6 การ์ดจากเอกสาร Permpool et al. ที่มีอยู่: FU/ขอบเขต Table 4, ฐานต้นน้ำปาล์ม, Land seeding ขาดหน่วย, FFB→CPO gap, allocation และ measurement period; ตรวจข้อความ PDF ทางการและ CC BY 4.0 notice ซ้ำ พร้อม attribution/locator/claim type/review files ทุกใบ ไม่ใช่ผลวัดใหม่ ไม่ยืนยัน PDF hash ใหม่หรือ visual re-audit
- ตัวตรวจ `scripts/audit_rag_corpus.py` ผ่าน ยืนยัน 4 การ์ดเดิมคงเดิม/10 IDs/ทะเบียนตรง hash/หลักฐานและสิทธิของการ์ดใหม่; รายงาน `evidence/rag-corpus-expansion-2026-11-08.json`
- สร้าง Qdrant Local รุ่นใหม่ 10 points/384 มิติ ปรับคำหัวข้อสองภาษาและกรองหัวข้อ/คำถามขอตัวเลขของการ์ด metadata หน้าแสดงจำนวนจริงและ attribution
- ตรวจคำถาม 76 ข้อ: 39 positive และ 33 negative ผ่าน; อีก 4 ambiguous ไม่ให้คะแนน ชุดใหม่ใช้พัฒนาต่อจาก 13/19 เป็น19/19 จึงเป็น development/regression ไม่ใช่ held-out/human review; unit6/HTTP19 ผ่าน ดู `evidence/rag-expanded-*-2026-11-08.json`
- รายงาน/วิธีตรวจซ้ำ `docs/rag/corpus-expansion-review-2026-11-08.md`; ไม่ deploy/แก้ production/เรียก Cloud หรือ Gemini และไม่อ้าง browser visual check
- ขั้นต่อไป: คำถามอิสระจากสมาชิกและตรวจคำ/มิติที่กฎยังไม่รู้จัก ก่อนขยายแหล่งอื่นหรือเพิ่มระบบเรียบเรียงคำตอบ; สิทธิเอกสารเก่า NOT_CLEARED คงเดิม

## ทำต่อทั้ง 6 ส่วนในเครื่องรับช่วง — 8 พฤศจิกายน 2569

- Docker ใช้งานได้แล้ว; กู้ NSO5CSVตรงhashเดิมและนำเข้า273, กู้ FAME/H-FAME16จากliveAPIตรวจmetadata/contract (ไม่ใช่DOMreplay), acquireDMFใหม่/pipelineผ่าน34905raw/34899observations/6reject/34671pending ไม่เพิ่มaccepted
- ReviewSQLiteแยกรุ่นตามhash331records (42upstream+16foreground+273NSO) payloadตรงครบ; MySQLlab331พร้อมDMF34899/34905rawตรงครบ; Neo4j5.26.32lab58records/97cardlinksตรงSQL พร้อมparameterizedlookup/duplicateconstraint;ไม่มีproductionmigration/ports public ไม่แตะGinder/Caddy
- RAG `serve --lineage` ผูก6การ์ดกับsource observationsจริง เปิดเฉพาะ58licensedarticle rows; card/source/graphHTTP9checksผ่าน คงnullunitและHOLD ไม่ใช่providerlink/fullLCI; NSOไม่เปิดผ่านpublicevidence routeนี้
- เพิ่มแบบประเมินคำถาม/ผลค้นเก็บ`.local/rag-feedback.jsonl` ผูกรุ่นและผลที่ออกจริง;ตรวจUIผ่านIABเห็นการ์ด/ลิงก์/แบบประเมิน ไม่ส่งผลแทนคน; actualfeedbackยัง0และไม่รับรองตัวตนอัตโนมัติ
- Geminiเพิ่มguardเลข/อัตราส่วนหน่วย/เชื้อเพลิง/สาร/ช่วงและอ้างเฉพาะการ์ดที่มี พร้อมfallbackเมื่อconnection/429/คำตอบผิด;runtime8tests/scope6/frontend13ผ่าน EPPOparser4ผ่าน/1ข้าม;ยังไม่มีliveGeminiเพราะไม่พบคีย์ในenvironmentที่ใช้
- NSOทวน273identities/context,169เลขเทียบเดิม,18totals/18percentผ่าน;ยัง104ค้าง/4divergence ไม่มีnewexternalcomparison แยกเหตุรายรายการในevidence/nso-restored-review-2026-11-08.json
- อ่านPDDTSMต้นทางทางเว็บได้73หน้า(ตรวจเฉพาะsectionที่เลือก);localdownloadเป็นnonPDFจึงไม่มีhashclaim คงex-ante/monitoring planแยกจากผลจริง;ยังไม่มีCH4คู่ยอดผลิตและCO2e/Lยังnull ดูevidence/tsm-pdd-review-2026-11-08.json และdocs/ethanol-tsm-wastewater.md
- EPPO2URLยังดาวน์โหลดไม่ผ่านHTTP ไม่สร้างไฟล์แทน;corporate reference/DOMเดิมยังขาด ExplorerDMF/NSO/inventoryกลับ200 แต่reference/EPPO503;boundedexport200/broadexport400ตามขีดจำกัด5000
- คู่มือ/ผล/ขั้นตอนซ้ำ `docs/handoff-execution-2026-11-08.md`;หลักฐานชุดevidence/handoff-*-2026-11-08.json ข้อค้างที่ต้องใช้ภายนอก:คำถาม/รีวิวสมาชิกจริง,คีย์Gemini,snapshotsที่ขาด,หลักฐานวิทยาศาสตร์เพิ่มเติม ไม่มีdeploy/push/automationใหม่

## ตรวจและเตรียมส่งต่อเจ้าของงานหลัก — 8 พฤศจิกายน 2569

- ชุดคำถามใหม่26ข้อพบ10false positives: warm/idle/entire cycle/N₂Oเว้นวรรค/ออกเทน/H-FAMEจับรวมFAME;แก้แยกมิติและชนิดเชื้อเพลิง คงsource/cutoffเดิม ผลใหม่8positive+18negativeผ่าน ชุดเดิม76ข้อยัง39positive+33negativeผ่าน/4ambiguousแยกไว้ ไม่ใช่human review
- เพิ่มหน้าอ่านsourceภาษาไทยแยกแท็บ แสดงamount/basis/unit/year/HOLDตรงเดิมและJSONคู่กัน แยกฐานหลักฐานไม่พร้อมจากclient error ปฏิเสธหลายID;runtime9/scope6/HTTPintegration14/RAG19ผ่าน ตรวจIABเห็นหน้าLand seedingและnullunitจริง
- เพิ่ม `docs/TEAMMATE_NEXT_STEPS_TH.md` และ `docs/pre-handoff-review-2026-11-08.md`;เครื่องมือแพ็กsource overlay+manifest/hashที่ `build/handoff-package/` และตรวจสำเนาbaseสะอาดด้วย `scripts/verify_teammate_bundle.py` ผลแยกในVERIFICATION.json ไม่รวมraw/build/.local/credentials
- ข้อค้างมนุษย์/คีย์/ไฟล์และวิทยาศาสตร์เดิมยังเปิด ไม่ทดแทนด้วยข้อมูลสมมติ งานอยู่working treeจาก67db1ad ยังไม่commit/push/deploy ไม่ส่งไฟล์ให้บุคคลอื่นในรอบนี้

## ตรวจวิศวกรรม local T109/T114 — 8 พฤศจิกายน 2569

- RAG เพิ่ม skip link/focus/Ctrl+Enter/สถานะ/ชื่อคำถามที่ส่งจริงและ client timeout 12s; ตรวจ IAB selected keyboard flows ทั้ง RAG/Explorer/native dialog และการคืนปุ่มหลัง503/timeoutผ่าน ไม่มี human feedback หรือ screen reader/UAT จริง
- SQLite เพิ่ม3ดัชนีตามqueryจริงและให้pipelineสร้างต่อ;วัด25ครั้งในสำเนา medianหน้ารวม121.558→0.269ms/หน้ากรอง14.143→0.292ms/export8.778→2.212ms ทุกแถว/ลำดับ/hashเดิม;pipelineออฟไลน์ผ่าน MySQL/Neo4j lab EXPLAIN ใช้PRIMARY/period index/IndexSeek ไม่แก้production
- โหลดlocalhost5รอบ รอบละ144คำขอที่concurrency1/4/8ได้ผลตามคาดครบ;HTTPlatencyยังผันผวน โดยExplorer c8 p95รอบสุดท้าย1383.43ms เทียบก่อน597.03ms ไม่อ้างเร็วขึ้นทั้งระบบ PeakWorkingSetตลอดprocessรอบสุดท้ายExplorer~72.8MiB/RAG~647.6MiB ไม่ใช่capacityหรือmemory-leak audit
- จำกัดembedding2threadsหลังprofile30คำถาม/10batchesและvectorsตัวอย่างตรงเดิม;regression47positive+51negativeผ่าน/4ambiguousแยก คิวserver32/readtimeout5sตั้งแต่accept โดยRAGยังserial;socketค้างไม่ครบheaderกู้ได้ Proxyจำลอง12คำขอทับซ้อน(deadline4/disconnect4/success4)ไม่cancelข้ามหรือendซ้ำ
- runtime9/scope6/HTTPresilience1/frontend13และproxybehaviorผ่าน;live-local RAG19/lineage14/Explorer9checksผ่าน โดยreference/EPPO503ยังเป็นข้อค้าง snapshotจริง ไม่มีGemini live/key
- หลักฐาน `docs/local-engineering-review-2026-11-08.md` และ `evidence/local-*-2026-11-08.json`;อัปเดตtaskboard/คู่มือส่งต่อ คงT109/T114 IN_PROGRESS;ชุดsourceoverlayใหม่ที่ `build/handoff-package/` ตรวจbase+hash+runtime/scope/HTTP/DMF suitesด้วย `scripts/verify_teammate_bundle.py` ผลจริงในVERIFICATION.json ไม่รวมruntime/raw/secrets
- ขั้นต่อไป:สืบExplorerHTTPlatency/วัดstagingคงที่และproductionqueryplans/memory;ให้คนจริงตรวจscreenreader/UAT;คงscientific/provider/allocation/matchedCH4-output/NSO104+4/snapshotขาด/Gemini/permanentendpointไว้ตามคู่มือ ไม่มีcommit/push/deploy/automationใหม่

## แก้คอขวด Explorer/ค้น primary เพิ่ม/สร้าง SRS PDF — 8 พฤศจิกายน 2569

- พบ export กว้างเดิมสร้าง5001wide rowsก่อนปฏิเสธ และหน้ารายการอ่านmetadata30ครั้ง/หน้า เปลี่ยนเป็นboundedCOUNTก่อนดึงรายละเอียดและcachemetadataเฉพาะคำขอ คงlimit5000/filters/guardเดิม;เทียบAPIทุกfield/ลำดับ+CSVbytesครบ34899candidate rowsใน72product/yearpartitionsตรงเดิม พร้อมfingerprintทุกตารางเดิม
- Profileฟังก์ชันc8:ปฏิเสธexport p95 3406.962→12.283ms;records106.537→28.290ms แต่filteredexport328.772→339.932msไม่อ้างทุกoperationเร็วขึ้น HTTPworkloadผสม144คำขอ/รอบ baseline+after+confirmationผ่านครบ Explorerc8 p95 2377.42→236.24/234.05ms ไม่ใช่productioncapacity/SLA;MySQLlabread-only boundedprobe3กรณีตรงexpected
- boundary4/Explorer5/MySQLstore4/WSGI6/diagram3/frontend13testsผ่าน;HTTPExplorer9checksผ่าน โดยCorporate/EPPOยัง503ตามsnapshotขาด ดู `docs/explorer-performance-fix-2026-11-08.md` และevidence/explorer-performance-fix/local-load-performance/local-export-probe-mysql
- พบSRS0.7.1sourceในHEADไม่ตรงrenderhashเก่าและPDFไม่มีในเครื่อง สร้างจากMarkdownเดิมไม่แก้เนื้อหา/สร้างERDจากDDL ปรับhistorytableให้พอดีหน้า;PDF27หน้าrenderครบและตรวจภาพ+headings/draftlabels/bounds/hashผ่าน source c2299cd48cad6bf7c4105be8f97a3d9f7317ee4482a13722b2b2b543a1cbd3a3;PDF647444a9ae5086e10b5328edf09a9ed84c4363860e4dbb9ab05c274d1c76c067 อยู่output/pdf/TamsoodBase-SRS-review.pdf เก็บrenderrecordเดิมแยกและอัปเดตsrs-current-review ยังรอทีมตรวจ/slidesไม่rebuild
- ค้นprimaryเพิ่ม:NRCT3152ยังไม่พิสูจน์identityรายงานARDA2017;JGSEEข่าวทุน2021ระบุPhaseIIไม่ใช้แทนworkbookเดิม;UNFCCCหน้าvalidationเป็นex-ante;หน้าoperatorแยกTSMBioEnergy/2012และcapacityไม่ใช่operatingoutput ไม่มีnumericimportsหรือpairedCH4/ethanolจริง คงallocation/CO2e gates ดูdocs/scientific-source-check-2026-11-08.md
- แก้taskT30ที่พิมพ์131exactเป็น141ตามevidence169=141+24+4;ปรับT55จากsnapshotSRSเก่าเป็นผลrenderปัจจุบัน;T55/T58/T97/T107/T109/T114ยังIN_PROGRESS อัปเดตguide/workplans/handoffและsourceZIP+cleanroomverifier ผลจริงที่build/handoff-package/VERIFICATION.json PDFส่งแยกจากZIP ไม่มีraw/secrets/commit/push/deploy/automationใหม่
- ขั้นต่อไป:staging/productionvalidationและmemoryระยะยาว;source snapshots/ARDA workbook/operatinglogsที่ตรงentity+งวด;Gemini key/live;humanreview/screenreader/contribution;slidesและfinalpackageให้ตรงreleaseจริงก่อนfreeze ไม่ถือว่าทำงานต่อไม่ได้ทุกอย่างเพียงเพราะgatesภายนอกยังเปิด

## สถานะรับช่วงและปรับคู่มือก่อนส่งต่อ — 9 พฤศจิกายน 2569

- ผลระบบที่ตรวจแล้วก่อนปรับคู่มือ: Corporate กู้ 101 รายการ (97 ACCEPTED_REFERENCE / 4 HOLD_CONTEXT), MySQL เทียบ SQLite ครบทุกช่องใน 11 ตารางและ reference view; constraint 7 กรณีและ late rollback ผ่าน ข้อมูลชั้นทดลองเดิมไม่เปลี่ยน สิทธิยัง NOT_CLEARED และ normalized LCI exchanges = 0
- HTTP ข้อมูลจริง 144 checks ผ่าน ครอบคลุม Corporate101/DMF34899/NSO273/foreground16/upstream42 ไม่เรียก Gemini/ส่ง feedback/แก้ production เก็บสำเนาหลักฐานเดิมพร้อม timestamp ไม่แก้ผลที่ `evidence/handoff-corporate-mysql-2026-11-09.json` และ `evidence/handoff-data-http-2026-11-09.json`
- ตรวจ Markdown ที่เพิ่ม/แก้ 22 ไฟล์ ปรับคู่มือหลัก/แผน/จุดรับช่วงให้ใช้สถานะปัจจุบัน แยกรายงานวันที่ 8 เป็นประวัติ คำสั่งเตรียมเครื่องรวม Corporate/DMF/owned labs แล้ว และคำสั่งประเมิน RAG ระบุ output แยกรอบใต้ build ไม่ทับหลักฐานเก่า ไม่ทำรายงานหรือสไลด์ใหม่
- ตรวจลิงก์ภายใน Markdown ทั้ง 22 ไฟล์และไวยากรณ์ PowerShell 17 code blocks ผ่าน แก้ลิงก์ ZIP runtime เก่าใน T21 ให้ชี้ตัวสร้างแทนไฟล์ที่ไม่ตาม Git; `git diff --check` ผ่าน ไม่มีการแก้โค้ดระบบในรอบปรับคู่มือนี้
- ชุดส่งต่อวันที่ 9 เป็น ZIP หรือ Git patch อย่างใดอย่างหนึ่งบน base67db1ad ผลตรวจชุดที่ส่งต้องตรงชื่อ/hash ใน `build/handoff-package/VERIFICATION.json`; raw/build/.local/keys ไม่ตาม Git หรือ ZIP งานทั้งหมดในรอบรับช่วงยังไม่ commit/push/deploy
- ข้อค้าง: EPPO/DOM ต้นฉบับ, NSO104+4 divergences/ฐานเวลาและหน่วย DMF, allocation/provider/background/transport-use-treatment และ CH4 คู่ยอดเอทานอลงวดเดียวกัน, Gemini live, independent human/screen-reader review และ staging/production validation ขั้นต่อไปใช้ `docs/TEAMMATE_NEXT_STEPS_TH.md` ให้ผู้รับตรวจ Git status และรันยืนยันในเครื่องตนเองก่อนรวม/เผยแพร่

## ตรวจโค้ดและเตรียม commit/push ตามคำสั่งผู้ใช้ — 9 พฤศจิกายน 2569

- ใช้ branch ใหม่ `codex/teammate-runtime-handoff-2026-11-09` จาก67db1ad ไม่แตะ main หรือ branch งานเดิมของเพื่อน ตรวจ remote ก่อนเริ่ม; ผล commit/push ให้ยืนยันจาก Git/remote จริง ไม่ถือข้อความยังไม่ push ในประวัติเป็นสถานะปัจจุบัน
- พบและแก้ 2 จุด: immutable review store เดิมเทียบเฉพาะ observation จึงเพิ่มตรวจ schema/ข้อมูลทั้ง source/process/observation/card_observation ก่อนใช้ซ้ำ; MySQL ping ทาง socket อาจผ่านช่วง bootstrap แล้ว shutdown จึงเปลี่ยน readiness เป็น TCP ของ final server เพิ่ม regression tests3 และสร้าง MySQL lab ใหม่เฉพาะรอบนี้เพื่อทดสอบ โดยคง labs รุ่นเดิมไว้
- ชุดที่เกี่ยวข้อง 118 tests: ผ่าน117/ข้าม1เพราะ EPPO snapshot ขาด; frontend build14assets/proxy concurrent faults12 ผ่าน เตรียม runtime offline พร้อม owned MySQL/Neo4j4ขั้นผ่าน และ HTTPข้อมูลจริง144/RAG19/lineage14 checks ผ่าน ไม่เรียก Gemini/ส่ง human feedback/เปลี่ยน production
- Full repository suite ที่ลองก่อนแก้2จุด:252 tests, failures2/errors42/skipped9 ยังไม่ผ่าน สาเหตุเป็น artifacts/dependencies ที่ไม่มีในเครื่อง และ historical MySQL NSO evidence ไม่ตรง hash ของ report ที่กู้ใหม่ ไม่แก้ค่าต้นทางหรือเขียนผลเก่าให้ดูผ่าน ผลจำแนกใน `evidence/prepush-review-2026-11-09.json` ความพร้อมรอบนี้คือส่งต่อโค้ดใน branch ไม่ใช่ production หรือ full-suite certification
- ตรวจ Python syntax/JSON และ credential patterns ของไฟล์ที่เลือก แยก raw/build/.local/output/keys ออกจาก commit; sync T21 ใน tasks.json ให้ตรง Markdown ที่แก้ลิงก์ไว้ ข้อค้างแหล่งข้อมูล/LCI/คนจริง/production เดิมยังเปิด ให้ผู้รับเริ่มที่ `docs/TEAMMATE_NEXT_STEPS_TH.md`
# รับช่วงงานปิดรายการก่อนส่ง — 9 พฤศจิกายน 2569

- ผู้ใช้ให้ทำรายการค้างทั้งหมด ยกเว้น RAG; งานนี้ไม่เปิด/ไม่ deploy RAG และไม่เปลี่ยนข้อมูล lifecycle เพื่อบังคับให้ผ่าน
- รัน full suite หลังแก้ test fixtures ของ public frontend: `python -X utf8 -m unittest discover -s tests` ผ่าน 287 tests, skipped 7. ปรับเฉพาะ `tests/test_frontend.py` ให้ fixture รวม manifest/public assets ที่ build script ใช้
- สร้าง SRS review PDF ใหม่ 27 หน้าและตรวจภาพครบ contact sheets/ตัวอย่างหน้าจริง; source hash ผูกกับ `evidence/srs-current-review.json`. ตรวจ slides ปัจจุบัน 10 หน้าใน `evidence/final-slides-2026-11-09.json`.
- ตรวจ release gates แล้วแก้ task board sync และ policy hash mismatch ด้วยการ rebuild report/reference product/package ตามนโยบายปัจจุบัน. เปิด Docker Desktop; โหลด release เข้า workspace MySQL ที่สคริปต์ยืนยัน owner/volume แล้ว และ clean restore แยกฐานชั่วคราว import 2 ครั้งผ่าน: 97 accepted records/101 records, ลบฐานชั่วคราวแล้ว. `evidence/reference-package-verification.json` อัปเดตตาม release ID `55e8648d44dc0402b07291a1ecd4e4ff37158e68f07aa9cb8171e2a758600fc6`.
- `python -X utf8 scripts/check_release.py` ล่าสุด: `technical_pass=true`, `reference_release_ready=true`, `submission_ready=false`; technical/reference checks ผ่านทั้งหมด. Remaining gates ระบุใน `build/release/readiness.json`: official requirements, source rights, DMF time-basis/domain, member contribution/defense และ consent.
- เขียน `docs/submission/RELEASE_REVIEW_2026-11-09.md`; ทำ T58 complete ตามขอบเขต end-to-end review โดยยังไม่อ้างว่าส่ง/final. T24 ยังค้าง IN_PROGRESS จนหลักฐาน human/official gates ครบและทีมเลือก snapshot freeze.
- ค้น FAME/LCI เพิ่มและบันทึก `docs/scientific-source-check-2026-11-09.md` กับ `evidence/scientific-source-check-2026-11-09.json`: paper ไทยปี 2013 เป็นคนละสมมติฐาน/วิธี allocation จึงไม่เอาระยะขนส่ง/ตัวเลขมาแทนกรณีปัจจุบัน; paper transport ปี 2025 เข้าถึงต้นฉบับเต็มไม่ได้; Thai National LCI landing page ไม่แสดง exchange/version/license ที่ใช้ได้; งาน B100 เรือไม่ตรง pickup. ไม่มี inventory ใหม่หรือ gate ปิด; `CO2e_total=null`, T97/T107 ยัง IN_PROGRESS.
- ยังต้องให้สมาชิกจริงกรอกบทบาท/contribution, memo, consent และซ้อม defense; ยืนยันกำหนดส่ง/ช่องทาง/สิทธิ reuse และผู้ตรวจ backend; แล้วสร้าง release snapshot ที่ทีมเลือกและ freeze. แบบกรอกอยู่ `docs/submission/MEMBER_INPUTS.md` และรายการเรียงใน `docs/submission/RELEASE_REVIEW_2026-11-09.md`.

## ตรวจ Vercel และทดสอบคำถามผู้ใช้ RAG — 9 พฤศจิกายน 2569

- ผู้ใช้เปิดสิทธิ์เข้าหน้า Vercel; ตรวจหน้า Team Networking ที่ล็อกอินอยู่ เห็น Secure Compute ระบุ Enterprise only. สถานะ billing ที่ตรวจใน team ก่อนหน้าเป็น Hobby; ไม่เปลี่ยนแผน/ค่าบัญชี. เอกสาร Vercel ระบุ AWS PrivateLink ใช้ได้ Pro/Enterprise, connection แรกอยู่ใน Advanced Networking, เพิ่มอีก $30/เดือน และ transfer $0.04/GB; Secure Compute เป็น Enterprise custom. AWS endpoint service ต้องมี NLB/GWLB จึงมีงาน/ค่า AWS เพิ่มด้วย.
- เพิ่มชุดคำถามภาษาไทยแบบผู้ใช้ทั่วไป 28 ข้อ (ตอบได้ 18, ไม่มีหลักฐาน 10) ใน `docs/rag/public-user-uat-questions-2026-11-09.json`; แก้ preference สำหรับเปรียบเทียบ basis ต้นน้ำปาล์มกับ Table 4, คำถามย้อน FFB จากยอด CPO, และข้อถามปีวัด FAME ที่ตอบได้เพียง caveat ว่าไม่ระบุช่วงวัด. ผลล่าสุด `evidence/rag-public-user-eval-2026-11-09.json`: top-1 18/18, ปฏิเสธคำถามไม่มีหลักฐาน 10/10; focused RAG tests 9/9 ผ่าน.
- ชุดนี้เขียนโดยผู้ช่วย ไม่ใช่ผู้ใช้จริงอิสระ; ตรวจเฉพาะการค้นการ์ด ไม่ได้ตรวจความถูกต้องของคำตอบ Gemini/การสร้างคำตอบ. `GEMINI_API_KEY` ยังไม่มีใน environment จึงยังไม่มี live Gemini call.
- Regression suite ของ repository ผ่าน 290 tests, skipped 10 ด้วย Python โปรเจกต์; RAG focused suite ผ่าน 9 tests. Full-suite run ใน RAG virtualenv ใช้ไม่ได้เพราะ env นั้นไม่มี `pypdf`/`pdfplumber`; ใช้ Python โปรเจกต์รันยืนยันแทน.
- สถานะเผยแพร่ยัง HOLD: manifest มีสิทธิ์การ์ด/ข้อเท็จจริง PENDING, private network, auth, rate/cost limits, privacy/retention, capacity/monitoring, rollback และ public human acceptance ยังไม่ผ่าน. ไม่ deploy หรือเปิด route สาธารณะ. ไฟล์ `docs/rag/PUBLIC_WEB_READINESS.md` และ `docs/rag/public-release-manifest.json` เป็นสถานะหลัก.

## ตั้ง Gemini key บน EC2 — 9 พฤศจิกายน 2569

- ผู้ใช้ป้อน key เข้า secret file บน EC2 เองโดยไม่ส่งผ่านแชต; ตรวจเฉพาะ metadata ได้ไฟล์ non-empty, mode `0400`, UID/GID `10001:10001`. ไม่อ่าน/บันทึกค่า key.
- ตรวจ Gemini API จาก EC2 host: DNS/TCP ออกได้, key แสดงรายชื่อโมเดล และคำขอสั้นที่ไม่มีข้อมูลโปรเจกต์ผ่านกับ `gemini-3.5-flash-lite`. โมเดลเดิม `gemini-2.5-flash-lite` คืน 404 สำหรับ key/โปรเจกต์นี้.
- RAG container ที่กำลังรันยังอยู่บน Docker internal network และ resolve DNS ภายนอกไม่ได้; secret ยังไม่ได้ mount เข้า container, runtime ยังไม่ได้เปิด Gemini, และไม่ได้เปลี่ยน/รีสตาร์ต container. ไม่ได้เปิด public route.
- ทดลองต่อ default Docker bridge ชั่วคราวกับคอนเทนเนอร์ปัจจุบันแล้ว DNS/TCP ไป Gemini ผ่าน จากนั้น disconnect bridge และตรวจว่าเหลือเฉพาะ internal network เดิม. ไม่ publish port และไม่ได้เปิดทางออกค้างไว้.
- หลักฐาน `evidence/rag-gemini-ec2-key-check-2026-11-09.json`. ก่อนใช้ในเว็บต้อง reconcile source/package ของ runtime ที่ deploy กับ source ปัจจุบัน, ปรับโมเดลที่ใช้, วาง egress path ที่ตรวจได้, แล้วทดสอบและค่อยเชื่อม Vercel; public release gates/สิทธิ์เนื้อหายังคง pending.

## 9 พฤศจิกายน 2569 — เตรียม Gemini RAG บน Vercel Preview
Push branch `codex/rag-gemini-preview-2026-11-09` ถึง commit `3915dbf` (แก้ Vercel allowlist ที่เดิมตัด `api/web/scripts/docs` ออก); dry-run ยืนยันอัปโหลดเพียง 22 ไฟล์รวมหน้าเว็บ, API และ manifest/corpus ที่อนุญาต. Deploy Preview `dpl_7vgLenydTdBsPf94JWVRv7rGdMK2` READY ที่ `https://tamsoodbase-nrz225u1v-neroadawats-projects.vercel.app`; Preview มี Vercel Authentication. ตั้ง Preview-only flags และ WAF rule จำกัด `/api/rag/ask` 12 คำขอต่อ IP ต่อ 60 วินาที. `/ask.html` ตอบสำเร็จและ API route ตอบ 503 ตามคาดเพราะ `GEMINI_API_KEY` ยังมีเฉพาะ Production; ไม่ส่งคำถามไป Gemini สด. ผู้ใช้ต้องเพิ่ม secret `GEMINI_API_KEY` ใน Preview แล้ว redeploy ก่อนทดสอบคำถามจริง. Production RAG ยังปิดตาม release manifest; ไม่ promote.

## 9 พฤศจิกายน 2569 — ยืนยันการถาม Gemini ผ่าน RAG Preview
หลังผู้ใช้เพิ่ม `GEMINI_API_KEY` ใน Vercel Preview และ redeploy, deployment ล่าสุด `dpl_7TB8sJAU88SUhu2iLsWdhdHfkYb5` (commit `d057e07`) READY. แก้ป้ายสถานะหน้า Preview ให้ตรงกับโหมดจริง; ตรวจหน้า `/ask.html` แสดง `RAG Preview · ชุดข้อมูลจำกัด` และไม่มีแถบปิดบริการค้าง. ทำ live smoke test ผ่าน UI พร้อมกดยินยอมต่อคำถาม: “CO₂e คิดยังไง?” Gemini ตอบว่าหลักฐานที่จับคู่ไม่ได้แจกแจงวิธีคำนวณ แต่รายงาน economic allocation FAME 70%/crude glycerin 30%; แสดง source ID `fame-allocation-caution`, DOI article, ตำแหน่ง Section 3.1.4/PDF p.7 และ CC BY 4.0. ตรวจข้อความเทียบกับ corpus แล้วตรงกัน. `node tests/rag-vercel-api.cjs` ผ่าน และ `python -m unittest tests.test_frontend -v` ผ่าน 14/14. เป็นการตรวจ integration หนึ่งคำถาม ไม่ใช่ independent user UAT. Preview ยังป้องกันด้วย Vercel Authentication; Production public release ยังคง HOLD ตาม manifest และไม่ได้ promote.

## ปรับทางเข้าและหน้าคุย RAG — 9 พฤศจิกายน 2569
- เพิ่มลิงก์ “ถามจากหลักฐาน” ในเมนูและหน้าแรกให้ชี้ไป `/ask.html`; เพิ่มทางกลับหน้าหลัก ปรับ textarea ให้ขยายตามข้อความ ตัวนับ 500 ตัวอักษร คีย์ลัด Ctrl+Enter และ `role=log` สำหรับข้อความสนทนาที่เพิ่มใหม่
- แนวทางประกาศบทสนทนาใช้ WAI-ARIA `log`/polite live region; ดู [W3C ARIA23](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA23.html). เปลี่ยนเฉพาะ UI ไม่เปลี่ยน retrieval/corpus/การส่งข้อมูล
- `node scripts/build_frontend.mjs` ผ่านใน local closed mode (`publicRagEnabled=false`, `ragMode=closed`); `git diff --check` ผ่าน; รอบนี้ไม่ได้รัน test suite
- commit `1702590` push ไป `codex/rag-gemini-preview-2026-11-09`. ตรวจ Vercel dashboard แล้วแต่ยังไม่พบ deployment ของ commit นี้; Preview ที่เห็นล่าสุดยังเป็น deployment `dpl_7TB8sJAU88SUhu2iLsWdhdHfkYb5` จาก `d057e07`. หน้า Production ยังเป็น `main` ที่ `aff41e1` และ RAG production ยังคงปิด
- PR #1 ที่ตั้ง base `main` ปิดแล้วหลังพบว่าจะดึงความต่างประมาณ 593 ไฟล์จากฐาน main ที่เก่ากว่า ไม่ merge ชุดนั้น
- ค้าง: ต้องสร้าง deployment Preview จาก commit `1702590` และตรวจหน้าเว็บจริงใน Preview ก่อน; การขึ้น Production ต้องทำบนสายโค้ดที่อัปเดตและรักษา release gates เดิม โดยห้ามเปิด Production RAG จนกว่าสิทธิ/ความเป็นส่วนตัว/UAT และ gate อื่นผ่าน

## Preview publication follow-up — 9 November 2026
Rechecked Vercel at 22:58 Asia/Bangkok. The deployed Preview still serves the earlier UI: its home navigation has no visible RAG link and it predates commit `1702590` (commit time 21:13). Production is unchanged. Vercel Settings → Git reports the project is not connected to a Git repository; Preview environment variables are present. Local `node scripts/build_frontend.mjs` succeeds, but builds with RAG closed when run without Vercel Preview variables. The updated commit and scoped PR #2 are ready; creating a Preview for the new commit requires a Vercel CLI credential/login or connecting the GitHub repository. No credential was found locally. Connecting GitHub would grant Vercel new access to `Neroadawat/TamsoodBase`, so pause for user confirmation before changing that access. No Production deployment or RAG release was made.

## Hosted Preview check after schema fix — 9 November 2026
User approved connecting only `Neroadawat/TamsoodBase` to the Vercel project. Connected the repository, removed the unsupported `public` property from `vercel.json`, committed as `b5b53cf`, and pushed only that file on the existing feature branch. Vercel Preview deployment `dpl_BauBwNZFV1BqVRfk2z1kemNRVFLA` is Ready from `b5b53cf`; the home page now visibly links to `/ask.html`, and the link opens the chat. A live Preview request for “CO₂e คิดยังไง?” returned a Gemini answer with the cited paper, section/page, and CC BY 4.0 attribution. This is a single integration smoke test, not public-user acceptance. Production remains on the old `main` build; no Production deploy or RAG activation was performed. The newly connected GitHub integration can now create deployments for future repo changes.

## ตรวจระบบรอบรวมและปรับ fail-closed — 9 พฤศจิกายน 2569

- ตรวจโค้ด RAG endpoint, Vercel proxy, ภาพ Docker และสคริปต์ install/upgrade/rollback ที่มีใน working tree โดยไม่แตะ EC2 หรือ deploy. พบจุดใน `api/rag/ask.js` ที่เมื่อ `VERCEL_ENV=preview` แต่ปิด preview flag จะไหลไปตรวจ production gate ต่อ; ปรับให้ Preview ที่ไม่ได้เปิดโดยชัดแจ้งปิดทันที และเพิ่ม regression assertion ใน `tests/rag-vercel-api.cjs`.
- หลังปรับ: `python -X utf8 -m unittest discover -s tests -v` ผ่าน 290 tests, ข้าม 10; CJS tests ทั้ง 17 ไฟล์ผ่าน; focused Vercel RAG contract ผ่าน; `git diff --check` ผ่าน (มีเพียงคำเตือน line ending CRLF). ผลก่อนหน้านี้ของ frontend build, Vercel packager และ local consistency audit ยังเป็นผลในเครื่อง; ไม่ใช่ live production attestation.
- formal Codex Security standard scan เริ่มไม่สำเร็จจาก runtime/plugin database command และไม่ได้คืน scan ID/report; หยุดตามข้อกำหนดของ scan workflow ไม่สลับไปสร้างผล scan ด้วยวิธีอื่น. การทบทวน source ด้วยมือในรอบนี้ไม่เท่ากับ security audit.
- Production ไม่ถูก deploy/เปลี่ยน; endpoint ที่แก้ยังอยู่ใน working tree และไม่ได้ push. Preview deployment เดิมจึงยังไม่รวม regression fix นี้. สถานะ submission ยังคง `submission_ready=false` และ release gates ที่ค้างยังอ้างตาม `build/release/readiness.json`.
- Follow-up hardening ใน Preview: จำกัด rate-limit buckets ไว้ 2,048 IP, ปฏิเสธ header address ที่ยาวผิดปกติ และกวาด bucket หมดอายุเมื่อเต็ม; มี regression checks ครบเพดาน/การกวาดรายการ. ข้อจำกัดนี้ช่วยป้องกันหน่วยความจำโตไม่จำกัดใน instance เดียว แต่ไม่ทดแทน distributed ingress limiter.
- ปรับ gate เพิ่มให้ทุก deployment ที่ `VERCEL_ENV` ไม่ใช่ `production` หรือ Preview ที่เปิด flag ชัดเจน ปิดไว้เสมอ; กัน local/development environment ไหลเข้า gate Production.

- แก้คำถามภาพรวม RAG Preview: คำถามแนว “ทำอะไรได้บ้าง/มีข้อมูลอะไรบ้าง” เดิมถูก scope-anchor filter ตัดก่อนถึง Gemini ทั้งที่เป็นคำถามเกี่ยวกับขอบเขตคลัง. เพิ่มคำตอบ catalog แบบ deterministic จาก corpus จริงทั้ง 6 cards พร้อม source links; เปลี่ยน quick prompts ให้ตรงกับบทความ Permpool (2020). Endpoint test ยืนยัน HTTP 200, คืน 6 citations และไม่เรียก Gemini. Full Python tests 290 passed/10 skipped, CJS 17 files passed, build/package/local consistency audit ผ่าน. เตรียม deploy เฉพาะ branch Preview; Production ยังปิดและไม่ถูกแก้.
- ปรับข้อความ consent ในหน้าแชตให้ตรงการทำงาน: คำถามภาพรวมคลังตอบในระบบ ส่วนคำถามเฉพาะเนื้อหาจึงส่งคำถาม/หลักฐานไป Gemini; ไม่อ้างว่าทุก query ถูกส่งไปโมเดล.

## ยืนยัน RAG corpus overview บน Preview — 9 พฤศจิกายน 2569

- Commit `7539147` สร้าง Vercel Preview deployment `7BaDSeCKYL7vDFweUpgD8rqjTqjd` สถานะ Ready: https://tamsoodbase-neyr5o5v6-neroadawats-projects.vercel.app/ask.html
- ทดลองในหน้าเว็บจริง 2 คำถาม ได้แก่ “แชตนี้มีข้อมูลเรื่องอะไรบ้าง?” และ “แชตนี้ทำอะไรได้บ้าง”; ทั้งคู่ตอบสำเร็จจาก catalog ในระบบ พร้อมแสดงเอกสาร/locator ทั้ง 6 รายการจากบทความ Permpool et al. (2020). Handler เส้นทางนี้ไม่เรียก Gemini; คำถามเฉพาะเนื้อหายังคงใช้ retrieval/Gemini ตาม flow เดิม.
- Preview ยังคงเป็นชุดข้อมูลจำกัดและต้องผ่าน Vercel Preview protection; Production ไม่ได้ถูก deploy หรือเปิด RAG.

## RAG data catalog and guarded numeric path — 10 November 2026

- ผู้ใช้สั่งทำตามแนวทาง data catalog → searchable index → แยก narrative/numeric → authenticated backend → rights filter และให้ตั้ง project review ทุกชั่วโมง
- เพิ่ม `docs/rag/dataset-catalog-map.json` จับคู่ DMF, company reports, NSO, research, EPPO กับ schema/table และสถานะ/สิทธิ์ตามเอกสาร schema; supporting methodology/context sources แยกจาก database tables. `scripts/build_rag_catalog.py` สร้าง local ignored index จาก source registry + evidence JSON: 20 source registry entries, 20 curated narrative/fact records, และ 6 limited Preview cards. ปีตีพิมพ์แยกจาก measurement period; ค่า unit/scope/year/locator ที่ไม่มีหลักฐานเก็บเป็น `null`. ไม่อ่าน live MySQL; ไม่รวม raw PDFs/CSVs.
- `build/rag/catalog/public-source-index.json` มี 0 source และ 0 evidence record เพราะ public manifest/registry ยังไม่ผ่านสิทธิ์; Preview allowlist 6 cards คงแยกอยู่ตามเดิม. ไม่เปลี่ยน manifest, Vercel, EC2, MySQL หรือสิทธิ์ข้อมูล.
- `api/rag/ask.js` แยกคำถามเชิงตัวเลขที่ต้องดึง/รวมจากฐานให้คืนสถานะว่า numeric SQL API ยังไม่เชื่อม และไม่เรียก Gemini; evidence synthesis ต้องส่ง `geminiConsent: true` ซึ่ง server ตรวจเอง. `web/ask.html` แสดงคำตอบสถานะสำหรับ numeric guard. นี่เป็น guard/abstention เท่านั้น—ยังไม่มี authenticated numeric SQL endpoint และยังไม่ query database.
- หลักฐานทดสอบรอบนี้: full Python suite `python -X utf8 -m unittest discover -s tests -v` ผ่าน 294 tests / 10 skipped; CJS test files ทั้ง 17 ผ่าน, รวม `node tests/rag-vercel-api.cjs`; frontend focused tests ผ่าน 14/14; `node scripts/build_frontend.mjs` สร้าง closed-mode build ได้; catalog `--check` ผ่าน (20 private / 0 public); `git diff --check` ผ่านโดยมีคำเตือนเดิมเรื่อง CRLF. ทั้งหมดเป็น local checks ไม่ใช่ live Preview/Production acceptance.
- ข้อค้าง: source-by-source redistribution/external Gemini review, Vercel→authenticated HTTPS ingress ไปยัง service ที่ออกแบบไว้, fixed SQL query IDs/read-only DB role/rights joins, durable rate/cost controls, independent generated-answer evaluation และ privacy/capacity/rollback acceptance. EC2 RAG ยังคง internal Docker-only ตาม runbook; Production public release ยัง HOLD. Preview protected; local patch ยังไม่ deploy/push.
- สร้าง heartbeat automation `tamsoodbase-hourly-project-review` สถานะ ACTIVE ให้ทำ review หนึ่งรอบต่อชั่วโมงใน thread นี้; จำกัดให้ตรวจสถานะ/แก้ local code ที่ย้อนกลับได้/รัน tests ที่เกี่ยวข้อง และห้ามเปลี่ยน rights, secrets, DB, Production, push/deploy หรืออ้าง final โดยไม่มีหลักฐาน.
- ขั้นถัดไป: ตรวจ config/runtime ที่มีจริงของ backend/API/DB โดยไม่อ่าน secrets, เติม test ห้าม Gemini ได้รับ payload เมื่อตัวเลข, ระบุ query IDs ที่กำหนดได้จาก schema พร้อม rights predicates; หากยังไม่มี ingress/backend implementation ให้คง numeric path ปิดและระบุ dependency แทนการเชื่อม EC2 ข้าม private boundary.

## Hardening ตัวกรอง global release — 10 พฤศจิกายน 2569

- ตรวจต่อจาก worktree ปัจจุบันและพบว่า `scripts/build_rag_catalog.py` เดิมใช้เฉพาะสิทธิ์รายระเบียนกับ source registry ในการสร้าง public index จึงไม่ได้บังคับ manifest ระดับ global ว่าต้องอนุมัติ public release และผ่าน release gates ทั้งหมดก่อน
- ปรับตัวสร้าง catalog ให้ต้องผ่านสถานะ `APPROVED_FOR_PUBLIC_RELEASE`, `publicly_usable=true`, `public_release_allowed=true` และ release gates ที่กำหนดครบทุกข้อก่อนพิจารณาข้อมูลรายระเบียน เพิ่ม regression test จำลองกรณีทุก row/source ถูกตั้ง CLEARED แต่ global manifest ยังคง HOLD; public output ต้องว่าง
- ผลตรวจ: full Python suite `python -X utf8 -m unittest discover -s tests -v` ผ่าน 296 tests/ข้าม 10; CJS ทั้ง 17 ไฟล์ผ่าน; focused frontend/catalog 20 tests ผ่าน; `node tests/rag-vercel-api.cjs` ผ่าน; `node scripts/build_frontend.mjs` ได้ build แบบ RAG closed และไม่มี private research data; `python -X utf8 scripts/build_rag_catalog.py --check` พบ 20 private sources, 20 restricted evidence records, 0 public records. หลักฐาน: `evidence/rag-release-gate-hardening-2026-11-10.json`.
- ไม่เปลี่ยน manifest/สิทธิ์, ไม่แตะฐานข้อมูลหรือบริการสด, ไม่ push/deploy. Authenticated fixed-query API สำหรับ numeric question ยังไม่มี; RAG สาธารณะจึงยังเปิดไม่ได้
- Formal Codex Security scan ยังไม่มีรายงานที่สำเร็จ: เครื่องมือปฏิเสธการ finalize โดยแจ้งว่า draft ล่าสุดยัง incomplete และเครื่องมืออ่าน completed scan ยืนยันว่า scan ยังไม่สำเร็จ; ไม่อ้างว่าการตรวจ source แบบเฉพาะจุดนี้แทนการสแกน repository ทั้งหมดได้
- Automation `tamsoodbase-hourly-project-review` ยังมีสถานะ ACTIVE ตามไฟล์ automation ปัจจุบัน; หนึ่งรอบต่อชั่วโมงและมีขอบเขตห้ามเปลี่ยนสิทธิ์/ข้อมูล/Production หรือ push/deploy
- ขั้นถัดไป: ทำ fixed-query API ที่มี server-to-server authentication และ rights predicate หลังตรวจ schema/runtime ที่ใช้อยู่จริง; ปิด public index จนสิทธิ์ global/source-level ผ่าน และเก็บผลทดสอบแบบ reproducible.

## ตรวจสิทธิ์ระดับ schema ก่อนทำ numeric API — 10 พฤศจิกายน 2569

- อ่าน DDL จริงใน `sql/mysql/full-schema.sql`, `sql/mysql/supplemental-schema.sql`, `sql/mysql/eppo-schema.sql` และ `sql/mysql/reusable-schema.sql`. พบว่า DMF/NSO/research/EPPO ไม่มี normalized per-source `CLEARED` field สำหรับ route aggregate; สถานะ `PENDING`, `STAGED_SOURCE_VERIFIED`, `SOURCE_REPORTED_PRODUCT_INVENTORY` เป็นสถานะข้อมูล ไม่ใช่สิทธิ์เผยแพร่. Company มี `document.rights_status` แต่ `ACCEPTED_REFERENCE` ก็ไม่เท่ากับ redistribution clearance.
- ปรับ `docs/rag/dataset-catalog-map.json` ให้บอกฟิลด์สิทธิ์/สถานะที่มีจริงต่อ schema และระบุว่า numeric API ยังไม่พร้อมเพราะ rights predicates ไม่ครอบคลุมทุก layer; เพิ่ม regression assertion ไม่ให้ schema map อ้างว่าชุดใด queryable-as-cleared ได้แล้ว; สร้าง ignored catalog ใหม่จาก map ปัจจุบัน พบ 20 private sources, 20 restricted records, 0 public records.
- ผล test หลังเพิ่ม assertion: `python -X utf8 -m unittest tests.test_rag_catalog -v` ผ่าน 6 tests, JSON parse ผ่าน และรัน full suite ซ้ำ `python -X utf8 -m unittest discover -s tests -v` ผ่าน 296/ข้าม 10. สรุป schema review: `evidence/rag-rights-schema-audit-2026-11-10.json`.
- ไม่เพิ่ม endpoint ที่จะต้องเดา/ข้ามสิทธิ์ และไม่เปลี่ยน DDL, ข้อมูล, Vercel, EC2 หรือ Production; ขั้นถัดไปคือตัดสินแบบจำลอง rights registry/migration และทดสอบกับ schema snapshot ที่ทีมใช้ ก่อนเริ่ม fixed-query route.

## สร้าง private full-text index จาก database snapshots — 10 พฤศจิกายน 2569

- เพิ่ม `scripts/build_rag_database_index.py` เพื่อประกอบ snapshot ที่มีอยู่ในเครื่องเป็น SQLite FTS5 index สำหรับค้นภายใน โดยมี 41,015 เอกสาร: DMF 34,675, company 103, NSO 278, EPPO 5,937, research 18 และ supporting 4. เก็บ stable source/record IDs, status/rights ตามหลักฐาน, ปีเผยแพร่แยกจากปี/ช่วงข้อมูล, หน่วย, scope, URL และ locator; metadata ที่ไม่มีหลักฐานคงเป็น null และ DMF เก็บตำแหน่ง/hash อ้างกลับแทนสำเนา raw_json.
- ดัชนีทุกระเบียนบังคับ `release_allowed=0` และ `external_llm_allowed=0` ด้วย CHECK constraints; ไฟล์ output อยู่ใน `build/` ที่ถูก ignore. ดัชนีไม่ต่อ live MySQL, เว็บ, EC2 หรือ Gemini. Snapshot มีอายุคละกัน: DMF 22 ต.ค.; NSO/EPPO/product inventory 23 ต.ค.; reusable/company snapshot 9 พ.ย. 2569 จึงไม่ใช่สถานะสดหรือข้อมูลปัจจุบันสม่ำเสมอ.
- เพิ่ม 6 tests สำหรับการจับคู่ชั้นข้อมูล, provenance/status, การไม่ทำสำเนา raw DMF payload, Thai search, read-only query และ release flags. Full Python suite ผ่าน 302 tests / ข้าม 10. `--check` ผ่าน 20 sources/41,015 records; SQLite integrity `ok`, FTS 41,015 records, release/external flags ทั้งหมด 0. หลักฐาน: `evidence/rag-private-database-index-2026-11-10.json`.
- `node scripts/build_frontend.mjs` ผ่านและยังปิด RAG; `node scripts/package_vercel.mjs` ผ่าน 22 allowlisted files; private index ไม่อยู่ใน frontend build หรือ Vercel source package; CJS behavior/contract tests ทั้ง 17 ผ่าน (ครอบคลุมปุ่ม/คีย์บอร์ด, navigation, filters, API proxy fault cases และ RAG UI/API guards). ไม่มี deployment, DB update, rights change หรือ public release.
- Automation `tamsoodbase-hourly-project-review` ถูกปรับใน Codex app ให้ ACTIVE ทุก 1 ชั่วโมงและครอบคลุม project-wide readiness/security/UX; ทำหนึ่งงานที่มีขอบเขตต่อรอบ, ทดสอบตามการแก้, ถ้างานปลอดภัยหมดจึงไป UX และตรวจปุ่ม/keyboard/mobile. คงข้อห้ามอ่าน secrets, เปลี่ยน rights, push/deploy/Production และห้ามอ้าง final โดยไม่มีหลักฐานครบ.
- ข้อค้าง: refresh/ยืนยันความสดของ snapshot จากฐานจริง, rights registry/source-by-source approvals, backend authenticated fixed-query SQL API พร้อม read-only principal, external Gemini/privacy/cost controls, independent answer UAT และ Production release gates. ระบบยังไม่พร้อม final/public จากหลักฐานรอบนี้.

## ปรับรายงาน freshness ของ local index ให้ไม่ชวนเข้าใจว่าเป็นข้อมูลสด — 10 พฤศจิกายน 2569

- `--check` เดิมระบุเพียง `status=valid` กับ mtime ล่าสุด ซึ่งอาจถูกเข้าใจว่า fresh แม้เป็นเพียงไฟล์ snapshot. เพิ่ม metadata `basis=LOCAL_FILE_MTIME_ONLY`, `live_database_read=false`, `freshness_attested=false`, ช่วงเวลาเก่า/ใหม่ และคำเตือนว่า mtime ไม่ยืนยันความสด/สถานะฐานจริง ทั้งในรายงานตรวจและ metadata ภายใน SQLite.
- เพิ่ม regression test รวมกรณีไม่มี input snapshot; test รอบแรกพบทั้งกรณี `min([])` และไฟล์ SQLite temp ค้างบน Windows เมื่อ exception เกิดก่อน close. แก้ให้ค่าเวลาที่ไม่มีเป็น null และปิด connection ก่อน cleanup.
- ผลตรวจหลังแก้: targeted index tests 7 ผ่าน; full Python suite 303 ผ่าน/10 skipped; `--check` และการสร้าง index ผ่าน, SQLite integrity `ok`, FTS 41,015 ระเบียน, release/external flags รวมเป็นศูนย์. Evidence/hash ล่าสุดอัปเดตใน `evidence/rag-private-database-index-2026-11-10.json`.
- Security workflow repository-wide ที่เริ่มผ่าน Codex desktop คืน error จาก `workbench_db.py start-prompt-only-scan` โดยไม่มี scan ID/context; จึงยังไม่มี formal repository scan หรือ coverage claim. ไม่เริ่ม scan ซ้ำและไม่อ้างว่า security audit สำเร็จ.

## ปิด private search เป็นค่าเริ่มต้น — 10 พฤศจิกายน 2569

- ตรวจ helper `search_records()` พบว่าถ้าอนาคตมีผู้เรียกจาก route ผิดโดยตรง ฟังก์ชันเดิมคืน private rows ได้เพราะแม้ทุก record ถูกล็อกไม่ให้ปล่อย แต่ search helper ยังไม่ได้ใช้สิทธิ์เป็น predicate.
- เปลี่ยนค่าเริ่มต้นเป็น audience `public` ที่บังคับ `release_allowed=1`; `external_llm` ต้องผ่านทั้ง release และ external-LLM flags; private review ต้องระบุ `audience="internal"`. รายการ audience มาจาก allowlist ในโค้ด ไม่ต่อ string จาก input user; query ยังใช้ SQLite parameter binding.
- เพิ่ม tests ยืนยันว่า default และ external-LLM audience ไม่คืน private records, internal review ค้นได้, audience ที่ไม่รู้จักถูกปฏิเสธ. Targeted tests 8 ผ่าน; full Python suite 304 ผ่าน/10 skipped. Smoke test กับ index จริงใช้คำค้นภาษาไทย ได้ 0 public / 0 external-LLM / 50 explicit internal hits (ตาม limit ที่ขอ). การปรับนี้ยังไม่ทำให้มี record ที่ release ได้ และยังไม่เชื่อม route/web/EC2/Gemini.
- ข้อค้างไม่เปลี่ยน: refresh ข้อมูลด้วยหลักฐาน source timestamp/ฐานจริง, rights approvals, authenticated fixed-query backend, separate external-model approvals/privacy controls และ full independent UAT. Evidence index ปัจจุบันยังคงมีทุก flags เป็น 0.

## บันทึกเวลาของแหล่งตามความหมายจริง — 10 พฤศจิกายน 2569

- `file mtime` ของ reusable SQLite เป็น 9 พ.ย. แต่ข้อมูลเอกสารภายในระบุ `document.accessed_at` 22 ต.ค.; การสร้าง release ใหม่ 9 พ.ย. ไม่ได้ยืนยันว่า source ถูกดึงใหม่. ปรับ index builder ให้อ่าน timestamps จาก metadata ต้นทางที่มีและบอกประเภทเวลาแยกกัน.
- ตรวจพบ source acquisition: DMF `resource.acquired_at` 22 ต.ค.; NSO `source_manifest.resources[].acquired_at` 23 ต.ค.; EPPO `source_snapshot.payload.acquired_at` 23 ต.ค. (เพิ่ม hash/mtime ของ `build/eppo/eppo.sqlite` ใน input manifest); company source access 22 ต.ค.; research `checked_at` 23 ต.ค. เป็นเวลาตรวจ ไม่ใช่ acquisition; supporting ยังไม่มี timestamp มาตรฐาน.
- ผลตรวจ: index targeted tests 9 ผ่าน, full Python suite 305 ผ่าน/10 skipped; `--check` และ rebuild มี 41,015 FTS docs, SQLite integrity `ok`, public/external flags 0. Evidence เพิ่ม source-activity dates และ artifact hash ล่าสุดใน `evidence/rag-private-database-index-2026-11-10.json`.
- ไม่ได้ refresh จากเว็บหรือฐานสด; หลักฐาน timestamp เหล่านี้ช่วยระบุความเก่าของ snapshot แต่ไม่ได้ยืนยันว่าตรงกับข้อมูลต้นทางปัจจุบัน. Web/EC2/Gemini ยังไม่ได้เชื่อมกับ private index.
- ตรวจซ้ำหลังเพิ่ม timestamp metadata: frontend build 16 assets, `publicRagEnabled=false`, `ragMode=closed`, `containsPrivateResearchData=false`; Vercel package 22 files, ไม่มี private data/credentials; `tests/rag-vercel-api.cjs` ผ่าน; index ไม่ถูกคัดเข้า frontend และยังถูก Git ignore. ไม่มี deploy.


## 10 พฤศจิกายน 2569 — คัดกรองหลักฐานมีเทนโรงสกัดปาล์ม
คัดกรองบทความปฐมภูมิ Saswattecha et al. (2015), DOI 10.1080/1943815X.2015.1110184: Table 2 รายงาน non-CO2 GHG ต่อ ton CPO สำหรับกลุ่มโรงงานใน Tapi basin โดยประมาณ CH4 จากกิจกรรม COD removal และระบุ mass allocation CPO:PK ตามแต่ละกลุ่ม. ใช้เป็น HOLD_CONTEXT เท่านั้น: ข้อมูลปี 2012/ภูมิภาคและกลุ่มสถานการณ์ไม่จับคู่ provider ปัจจุบัน, ไม่ใช่มวล CH4 วัดจริง, ไม่ใช่ full CO2e; เว็บขวางการดาวน์โหลด PDF จึงยังไม่มี visual cell audit/hash/สิทธิแจกจ่าย. ไม่มีการ import/คำนวณหรือเปลี่ยน `CO2e_total`. รายละเอียด: `docs/scientific-source-check-2026-11-10.md`, `evidence/scientific-source-check-2026-11-10.json`.


## 10 พฤศจิกายน 2569 — ตรวจความสอดคล้องของ candidate ปัจจุบันแบบอ่านอย่างเดียว
- ตรวจ candidate ใน working tree ด้วย `scripts.audit_release_consistency.inspect()` โดยไม่เรียกส่วนที่เขียนทับ manifest; ผ่าน 46/46 checks, candidate ID `6672e264aa724fd60df014061434f7717f5b01387c3a28fb5ef4e55483a2fdcb`, ไม่มี check ตก.
- ครอบคลุม hash/source/build/manifest ของ inventory, frontend package และ SRS artifacts; counts ที่รายงานโดย audit: upstream 42 observations, conversion 16 observations.
- นี่ไม่ใช่การตรวจ live Vercel/EC2; ค่าการ deploy ในรายงานเป็นบันทึกเดิม และ readiness snapshot ยังคง `submission_ready=false`. ไม่มี tests/build, network, database write, rights change หรือ deploy รอบนี้.
- หลักฐาน: `evidence/release-consistency-review-2026-11-10.json`. T24 คง `IN_PROGRESS`; ข้อค้างทางมนุษย์/สิทธิ์/ความพร้อมส่งยังต้องปิดแยกต่างหาก.


## 10 พฤศจิกายน 2569 — รีเฟรช release readiness จาก working tree ปัจจุบัน
- รัน `python -m scripts.check_release` โดยไม่ใช้ `--tests`/`--package`; audit ตรวจ 68 checks: technical True, reusable reference release True, แต่ submission ยัง `false`.
- ข้อค้างที่ audit ยืนยัน: official requirements, source rights, domain/time-basis, team contribution/defense และ consent forms. นี่เป็น local evidence audit ไม่ใช่การยืนยันสถานะเว็บ/EC2 สด และไม่ได้ตรวจ gate ของ RAG Production แทนการทบทวนสิทธิ/ความเป็นส่วนตัว/UAT.
- ไม่มี test/package, network, DB mutation, rights change, push หรือ deploy. หลักฐาน: `evidence/current-release-readiness-2026-11-10.json`; เก็บ `T24` และ `T145` ไว้สถานะเดิม.
## 10 พฤศจิกายน 2569 — ตรวจ readiness/build/test ซ้ำหลังแก้ environment ทดสอบ

รัน Python full suite ใน report virtualenv ที่ตรวจ `pip check` ผ่าน: 305 tests, ผ่าน 295, ข้าม 10, ไม่มี failure (9 optional RAG tests ตรวจแยกใน RAG environment; 1 test ต้องใช้ restored review store ที่ไม่มีใน working tree). ชุด RAG database/catalog/scope ใน RAG virtualenv ผ่านครบ 24 tests และ `pip check` ผ่าน. JavaScript `tests/*.cjs` ผ่านครบ 17 ไฟล์. แยก environment รายงาน PDF กับ RAG เพราะ requirements ที่ pin ไว้มีช่วง Pillow ขัดกัน; ไม่เปลี่ยน dependency manifests.

Frontend build และ Vercel allowlist package ผ่าน: public snapshot 42 rows, `publicRagEnabled=false`, `ragMode=closed`, ไม่มี private research data/credentials. Catalog/index check ผ่านที่ 22 sources/41,017 records; public/external-LLM release ยัง 0. Private SQLite SHA-256 ตรงกับ evidence และ `integrity_check=ok`; เป็น snapshot local ไม่ใช่ live DB. `git diff --check` ผ่านโดยมีเฉพาะคำเตือน line endings. หลักฐาน `evidence/project-final-review-2026-11-10.json`.

สถานะยังไม่ใช่ final: ยังไม่มีสิทธิปล่อย corpus หรือส่ง Gemini, numeric fixed-query API, production privacy/cost controls, independent Thai user acceptance และ production capacity/monitoring/rollback evidence. ไม่เปลี่ยนข้อมูล canonical/DB, rights, secret, production, push หรือ deploy. ขั้นถัดไปคือทำ authenticated fixed-query API โดยต้องผูกสิทธิ source/record ให้ตรวจได้ก่อน หรือเดินส่วน retrieval ภายในต่อโดยไม่เผยข้อมูล.


## 10 พฤศจิกายน 2569 — เพิ่ม RAG timeout regression check
- เพิ่มเฉพาะ regression test ใน `tests/rag-vercel-api.cjs`: จำลองคำขอ Gemini ที่ค้างและยืนยันว่า AbortSignal ถูกยกเลิกที่ deadline 18 วินาที พร้อมเคลียร์ timer; `node tests/rag-vercel-api.cjs` ผ่าน.
- ใช้ fake fetch; ไม่มีการเรียก Gemini สดและไม่มีการแก้ production handler หรือ deployment. การทดสอบนี้ไม่แก้ข้อจำกัด global rate/cost budget.
- หลักฐาน: `evidence/rag-timeout-regression-2026-11-10.json`. RAG Production ยังคง HOLD ตาม release gates.


## 10 พฤศจิกายน 2569 — ระบุ trust boundary ในคำกำกับ Gemini
- ปรับคำกำกับให้ใช้ภาษาไทยตรงคำถามและเข้าใจง่าย; ใช้เฉพาะหลักฐานแนบ; ถือคำถาม/ฟิลด์หลักฐานเป็นข้อมูลที่ไม่น่าเชื่อถือ ไม่ใช่คำสั่ง; ปฏิเสธคำสั่งฝังในเนื้อหาและห้ามเดาหรือรวมตัวเลขที่ qualifiers ไม่ตรง.
- เพิ่ม assertion ใน `tests/rag-vercel-api.cjs`; ผล `node tests/rag-vercel-api.cjs` ผ่าน. เป็น fake-fetch contract test ไม่ใช่การยืนยันพฤติกรรม Gemini สดหรือการรับรองความปลอดภัยของ prompt.
- ไม่มี Gemini สดหรือ production deploy. ยังต้องทดสอบคำตอบ adversarial โดยผู้ตรวจอิสระ และปิด global rate/cost, rights และ privacy gates. หลักฐาน: `evidence/rag-prompt-injection-contract-2026-11-10.json`.


## ปรับแผน Final ให้ตรงกับสถานะ RAG ปัจจุบัน — 10 พฤศจิกายน 2569
- แก้ข้อความเก่าที่ระบุว่า RAG พัก/ไม่มี public route ให้แยกชัด: มี limited Vercel-authenticated Preview พร้อมหลักฐาน smoke test 9 พ.ย.; Production RAG ยังปิดและยังไม่มี independent Thai UAT.
- เพิ่มผล readiness local ล่าสุด 68/68 technical checks ผ่าน, reference release พร้อม, แต่ submission ยังไม่พร้อม; คง 5 human/official gates ตามหลักฐาน.
- ไม่เปลี่ยน SRS, สิทธิ์, deployment หรือ RAG config. อ้างอิง `docs/submission/FINAL_DELIVERY_PLAN.md` และ `evidence/current-release-readiness-2026-11-10.json`.
## 10 พฤศจิกายน 2569 — พบ anonymous Production API ส่งข้อมูลที่สิทธิ์ยังไม่เคลียร์

ตรวจ GET แบบไม่ส่ง Authorization ที่ `https://tamsoodbase.vercel.app`: `/api/eppo` ส่ง 40 แถวพร้อม `SPECIFIC_TERMS_NOT_YET_VERIFIED`; `/api/nso` ส่ง 273 แถว `PUBLIC_DOWNLOAD_REUSE_SCOPE_UNCONFIRMED`; `/api/records` ส่ง 30 แถว `PENDING`; `/api/reference` ส่ง 30 metadata rows `NOT_CLEARED` (ค่าปริมาณถูกซ่อน); `/api/product-inventory` ส่ง 16 rows และ `/api/summary` ตอบ 200. ทุก route ไม่มี `WWW-Authenticate`. บันทึกเฉพาะ counts/status ไม่บันทึกค่าระเบียน: `evidence/production-anonymous-api-exposure-2026-11-10.json`.

แก้ `api/[route].js` ให้ทุก dataset/login route ตอบ 403 ก่อนเรียก backend; เหลือ model/release metadata กับ readiness/health. หน้าเว็บแยกสถานะ restricted จาก network error และแจ้งผู้ใช้อย่างชัดเจน. เพิ่ม CJS coverage ให้ 15 routes ที่ถูกปิดและยืนยันว่าไม่มี upstream request. หลังแก้: Python suite 306 tests (ผ่าน 296, ข้าม 10, failure 0); CJS ทั้ง 17 ไฟล์ผ่าน; frontend build/package ผ่าน, public snapshot 42 แถว, ไม่มี private research data และ RAG closed; `git diff --check` ผ่าน. Production ยังไม่ได้ deploy mitigation และจึงยังเสี่ยงเปิดข้อมูลจนกว่าจะเผยแพร่ hotfix ที่ตรวจแล้ว. งาน T149 อยู่ IN_PROGRESS; ต้องยืนยัน Production API ทุกเส้นหลัง deployment ที่ได้รับอนุมัติ และวางเส้นทาง user authentication/สิทธิ์สำหรับข้อมูลที่เคลียร์แล้ว.



## บันทึกและทดสอบเพดานทรัพยากรต่อคำขอของ RAG — 10 พฤศจิกายน 2569
- ทบทวนตาราง readiness ที่มีข้อความเก่าว่าไม่เคยมี Gemini Preview; แก้ให้แยกการทดลอง Preview ที่ผู้ใช้ยินยอม 9 พ.ย. ออกจาก Production ซึ่งยังไม่ผ่าน privacy/right gates และยังไม่ยืนยันค่า secret ปัจจุบัน.
- บันทึกเพดานต่อคำขอที่มีในโค้ด: body 2 KiB, question 500 ตัวอักษร, context ไม่เกิน 4 cards, output 700 tokens, response 48 KiB, deadline 18 วินาที. เพิ่ม regression assertions สำหรับ oversized input/output, context/output caps; `node tests/rag-vercel-api.cjs` ผ่าน.
- อ้างแนวทางความปลอดภัย Gemini เรื่องจำกัดปริมาณคำถามและ prompt injection; ไม่มีการเปลี่ยน Vercel/Production. เพดานเหล่านี้ไม่ใช่ global spend budget หรือ distributed limiter; ยังเป็น release blocker. หลักฐาน: `evidence/rag-per-request-cost-bounds-2026-11-10.json`.


## Final readiness consistency retry — 10 November 2569
- หลังปรับเอกสาร readiness มี audit หนึ่งครั้งที่ `task_board_sync` ไม่ผ่าน; ตรวจไฟล์ปัจจุบันแล้วเนื้อหา board เท่ากับผล render จาก tasks.json และรันซ้ำทันทีผ่าน 68/68 checks. ยังไม่ทราบสาเหตุของ mismatch ชั่วคราว จึงเก็บทั้งสองผลตามจริง.
- ผล readiness ล่าสุดยัง `technical_pass=true`, `reference_release_ready=true`, `submission_ready=false`; ไม่มี source manifest mismatch. RAG per-request caps ผ่าน targeted contract test แต่ durable/global rate-and-spend controls ยังไม่ผ่าน.
- หลักฐาน: `evidence/current-release-readiness-2026-11-10.json`, `evidence/rag-per-request-cost-bounds-2026-11-10.json`.


## Current readiness recheck after volatile working-tree changes — 10 พฤศจิกายน 2569
- พบ hash ของ `tests/frontend-api-behavior.cjs`, `tests/test_frontend.py`, `web/api.js`, `web/app.js` เปลี่ยนหลังรายงาน readiness ก่อนหน้า; ไม่ได้แก้ไฟล์เหล่านี้ในรอบนี้. รัน audit และตรวจ hash manifest ทันทีต่อเนื่อง ผลล่าสุด technical 68/68 ผ่านและ mismatch 0.
- Task-board synchronization เคยไม่ผ่านหนึ่งครั้งในรอบก่อน แต่ตรวจซ้ำและ audit ล่าสุดผ่าน; ยังไม่ทราบสาเหตุของผลชั่วคราว.
- readiness ปัจจุบันยัง `submission_ready=false` ด้วยห้า gate เดิม; ไม่ได้ตรวจ live services หรือเปิด Production. หลักฐาน: `evidence/current-release-readiness-2026-11-10.json`.


## ตรวจซ้ำ local mitigation ของ anonymous Production API — 10 พฤศจิกายน 2569
- รัน `node tests/vercel-proxy-behavior.cjs` กับโค้ดล่าสุด; 15 dataset/login routes ถูกปฏิเสธ 403 ก่อนเรียก upstream mock, ส่วน health/readiness ตรวจแยกและผ่าน.
- Hash ของ `api/[route].js`: `2decbcd69ea0e7b2fb12b745468ee785f5db48408558c1b42da2a228002de522`. นี่ตรวจ local mitigation เท่านั้น; Production ยังไม่ได้ deploy/recheck และหลักฐาน exposure ก่อนแก้ยังคงเป็นความเสี่ยง live จนกว่าจะ deploy hotfix ที่ได้รับอนุมัติและตรวจหลัง deploy.
- ไม่มีการเรียก Production, เปลี่ยนสิทธิ์, credential หรือบริการ. หลักฐาน: `evidence/production-anonymous-api-mitigation-local-2026-11-10.json`.


## เพิ่ม numeric token guard ให้คำตอบ Gemini ของ RAG — 10 พฤศจิกายน 2569
- parser ตรวจเลขอารบิก/เลขไทยในคำตอบกับเฉพาะ hit ที่ source_ids อ้าง; ถ้าไม่พบค่าในแหล่งที่อ้างจะปฏิเสธคำตอบ. Normalize comma grouping เช่น 1,000 เพื่อเทียบกับ source 1000.
- `node tests/rag-vercel-api.cjs` ผ่าน: กรณีเลข ๑,๐๐๐ ที่รองรับรับได้ และค่าปี 2024 ที่ไม่มีในแหล่งถูกปฏิเสธ; contract อื่นในไฟล์เดียวกันผ่านด้วย.
- นี่เป็น lexical check ไม่ใช่ semantic entailment/การยืนยัน metric-unit-period-scope และไม่ครอบคลุมจำนวนที่เขียนเป็นคำ. ไม่มี live Gemini/deployment; RAG Production คง HOLD. หลักฐาน: `evidence/rag-numeric-token-guard-2026-11-10.json`.

## RAG data scope, Production proxy, and hourly review recheck — 10 พฤศจิกายน 2569

- ตรวจ scripts/build_rag_catalog.py --check: source registry 22 รายการ, curated narrative/fact 20 ระเบียน; public-cleared output 0 รายการ. scripts/build_rag_database_index.py --check ยืนยัน private FTS snapshot 41,017 records (DMF 34,677; company 103; NSO 278; EPPO 5,937; research 18; supporting 4). Index ทุกระเบียนบังคับ release_allowed=0, external_llm_allowed=0; เวลา mtime เป็นเพียงข้อมูลไฟล์ ไม่ใช่ live DB freshness.
- ตรวจ Production แบบไม่อ่าน row values: 6 dataset routes (/api/eppo, /api/nso, /api/records, /api/reference, /api/product-inventory, /api/summary) ตอบ 403; /api/healthz และ /api/release ตอบ 200; POST /api/rag/ask ตอบ 503 ใน probe ที่ไม่ให้ Gemini consent. ผลนี้ยืนยันการปิด anonymous data routes; ไม่ใช่ end-user authentication หรือการเชื่อมฐานข้อมูลเข้ากับเว็บ.
- รัน targeted tests 28 ผ่าน, 9 skipped; git diff --check ผ่านโดยมีเฉพาะคำเตือน CRLF ของ working tree. หลักฐาน: evidence/rag-system-recheck-2026-11-10.json.
- สถานะงาน: local inventory/search prototype มีข้อมูลครบตาม snapshots ที่มีในเครื่อง แต่ยังไม่มี live DB indexing, Vercel-to-EC2 HTTPS RAG/search service, user authentication, หรือ fixed SQL API. สิทธิ์ปัจจุบันทำให้ external/public index มี 0 records; RAG Production คง HOLD. T145 ยัง IN_PROGRESS และ T147 ยัง TODO จนมี release-cleared records, read-only principal, service authentication/HTTPS และ end-to-end tests.
- พบข้อกำหนด CN230 ในผลค้นทางการไม่เพียงพอที่จะยืนยัน deadline หรือช่องทางส่งงานปัจจุบัน; ไม่เปลี่ยน gate official_requirements.
- Automation tamsoodbase-hourly-project-review ตรวจยืนยันสถานะ ACTIVE ทุก 1 ชั่วโมงอยู่แล้ว จึงไม่สร้างซ้ำ. คำสั่งของ automation จำกัดหนึ่งรอบต่อครั้งและห้ามเปิดสิทธิ์/secret/public route หรือ deploy Production โดยอัตโนมัติ.
- รายการนี้เป็นผลล่าสุดและมีผลเหนือข้อความสถานะเก่าที่ระบุว่าไม่ได้ตรวจ live Production หลัง hotfix.

## 10 พฤศจิกายน 2569 — ตรวจเงื่อนไข Gemini และปรับคำแจ้งความเป็นส่วนตัว
- เทียบหน้า Terms/Billing/Usage Policies ทางการของ Google AI for Developers กับข้อความหน้า RAG; แยกการใช้ข้อมูลของโควตาไม่มีค่าใช้จ่ายออกจาก API ที่ผูกกับ Cloud Project ซึ่งเปิด Billing อยู่ และระบุว่าทีมยังไม่ตรวจ Billing ของ key ที่ตั้งค่าไว้.
- ปรับคำแจ้งภาษาไทยใน `web/ask.html` ให้บอกว่าคำถามและหลักฐานที่ค้นพบจะส่งไป Gemini หลังยินยอม, ผู้ตรวจอาจเข้าถึงข้อมูลในกรณีบริการไม่มีค่าใช้จ่าย และกรณี Billing active ไม่ควรถูกตีความว่าไม่มี abuse monitoring; เพิ่มลิงก์เงื่อนไข Billing. เพิ่ม `T153` และหลักฐาน `evidence/rag-gemini-terms-review-2026-11-10.json`.
- ตรวจพบเงื่อนไขผู้ให้บริการเพิ่มเติมเรื่องประเทศ/ภูมิภาคที่ให้บริการและอายุ 18 ปีขึ้นไป; กลุ่มผู้ใช้เป้าหมายยังไม่ยืนยัน จึงบันทึก `T154 WAITING` และคง Production RAG เป็น HOLD.
- ทดสอบคำแจ้ง privacy และ isolated frontend build 2 ผ่าน; สร้าง task board ใหม่. Local release audit รอบนี้ technical 68/68, reference ready, submission not ready (765 files); ข้อค้างทางการ/สิทธิ/หน่วย/ทีม/consent ยังคงเดิม.
- ไม่มีการส่ง prompt หรือข้อมูลโครงการไป Google, ไม่ตรวจหรือบันทึก API key/Billing จริง, ไม่เปลี่ยนบริการหรือ deploy. ข้อจำกัด: หน้า Terms/Billing โดยตรง redirect ไปหน้า AI Studio ที่ตัวอ่านเว็บเข้าถึงไม่ได้ จึงอ้างอิงเฉพาะข้อความผลค้นของหน้า official docs; ไม่ใช่การอนุมัติทางกฎหมายหรือยืนยันสถานะบัญชี.

## 10 พฤศจิกายน 2569 — เพิ่ม release gate ตรวจความเหมาะสมของกลุ่มผู้ใช้ Gemini
- ตรวจเส้นทางเปิดใช้งานจาก API, public catalog และ frontend build พบว่า Terms มีข้อจำกัดอายุ/ภูมิภาค แต่ไม่มี gate แยกที่บังคับยืนยันข้อนี้.
- เพิ่ม `provider_audience_eligibility_confirmed=false` ใน manifest และทำให้ public catalog generation, public frontend build และ runtime Preview/Production ปฏิเสธการเปิด RAG จนกว่าจะมีการยืนยันจากเจ้าของ. Preview ต้องมี `TAMSOOD_GEMINI_AUDIENCE_ELIGIBILITY_CONFIRMED=true` เพิ่มจาก flags เดิม.
- ทดสอบ targeted Python 2 รายการผ่าน (catalog predicate และ public build ในโฟลเดอร์ทดสอบแยก); `node tests/rag-vercel-api.cjs` ผ่าน รวม mocked Production predicate; `scripts/build_rag_catalog.py --check` ยืนยัน 22 แหล่ง private, 20 ระเบียนจำกัดสิทธิ และ public-cleared 0. หลักฐาน: `evidence/rag-provider-eligibility-gate-2026-11-10.json`.
- Gate นี้เป็น owner attestation เท่านั้น ไม่ตรวจอายุหรือปิดกั้นตามภูมิภาคจริง; `T154` ยัง WAITING จนกำหนด audience จริง. ไม่มีข้อมูลส่งไป Gemini, ไม่มี key อ่าน/แก้, ไม่มี Preview/Production deployment หรือการเปลี่ยนบริการ.
- หลังแก้ รัน local release audit ที่ 2026-11-10 07:39 UTC: technical 68/68, reference release ready, submission ยังไม่พร้อม, 766 files ใน manifest. ตรวจ `git diff --check` ผ่าน โดยมีเพียงข้อความเตือนเรื่อง CRLF ในไฟล์เดิม.
- ตรวจการค้นจริงในไฟล์ private FTS local (ขนาด 152,690,688 bytes): query ตัวอย่าง “ก๊าซธรรมชาติ” พบ 20 ระเบียนเมื่อ audience=internal และ 0 เมื่อ audience=public หรือ external_llm; บันทึกเฉพาะจำนวนผล ไม่บันทึก payload. นี่พิสูจน์ local index search/filter เท่านั้น ไม่ใช่เว็บหรือ live DB. เพิ่มใน evidence/rag-system-recheck-2026-11-10.json.

## สร้าง catalog outputs และตรวจขอบเขต Vercel bundle — 10 พฤศจิกายน 2569
- สร้าง local private-source-catalog.json และ public-source-index.json: private มี 22 sources, 20 restricted evidence records, 6 limited Preview cards; public index ยังเป็น 0 source/0 evidence และกัก 22 sources ไว้ตาม release gate.
- สร้าง source-only Vercel upload package 22 ไฟล์; ตรวจได้ว่าไม่มี private research data หรือ credentials ใน bundle. ไม่ได้ deploy หรือเปิด RAG.
- Python catalog/database-index/scope tests 24 tests (15 ผ่าน, 9 skipped); Vercel proxy และ RAG contract tests ผ่าน. Release audit 07:34 UTC: technical_pass=true, reference_release_ready=true, submission_ready=false, manifest_file_count=765.
- หลักฐานรวม: evidence/rag-system-recheck-2026-11-10.json. ข้อค้างยังเป็น live DB/HTTPS backend และ authenticated fixed-query numeric API; public rights remain closed.

## ปรับ SRS ระบบให้ตรงสถาปัตยกรรม RAG ล่าสุด — 10 พฤศจิกายน 2569
- ปรับ SRS Markdown เป็นรุ่น 0.7.2: แยก dataset API ออกจาก Vercel-native RAG, ระบุสถานะ 403/503 ตามหลักฐาน, เพิ่ม FR/NFR/use case/acceptance และข้อจำกัด privacy/provider eligibility พร้อมระบุว่า gate กลุ่มผู้ใช้เป็น owner attestation.
- สร้าง PDF 29 หน้า; ตรวจภาพ contact sheets ครบทุกหน้าและดูภาพเต็มหน้า 2, 13, 14, 23, 24. ตรวจข้อความ/หน้า/ขอบเขต PDF และ source hash ตรงกัน. เก็บ PDF 0.7.1 ไว้ใน archive.
- หลักฐาน: `evidence/srs-current-review.json`. ยังเป็น draft รอสมาชิกตรวจ; slides ไม่ได้ rebuild; ไม่มี live service check หรือ deployment รอบนี้.
- ขั้นถัดไป: ให้ทีมยืนยันเนื้อหา/ข้อมูลระบุตัวตนและ requirements ก่อนนำไปใช้ส่ง; แยกตรวจ release gates อื่นต่อ.

## Local release audit หลังอัปเดต SRS — 10 พฤศจิกายน 2569
- python -X utf8 -m scripts.check_release ผ่าน technical checks 68/68 และ reference release ready; submission_ready=false, manifest 767 ไฟล์. ข้อค้าง 5 กลุ่มเดิม: official requirements, source rights, domain/units, team/defense และ consent.
- หลักฐาน: `evidence/current-release-readiness-2026-11-10-0751.json`. เป็น local-only audit ไม่มี live service probes; ไม่ใช่การยืนยัน MTEC acceptance.

## ปรับป้ายสถานะแชตที่ยังปิด — 10 พฤศจิกายน 2569
- แก้ป้ายหัวหน้าแชตจากข้อความชวนเข้าใจว่ากำลังจะเปิดเป็นสถานะปิดชัดเจน และเปลี่ยนจุดสถานะสีเขียวเป็นสีอำพันเมื่อยังปิด; หาก config เปิดในอนาคต โค้ดจะเอารูปแบบปิดออก.
- Frontend suite ผ่าน 17 tests รวม regression เฉพาะกรณีนี้; git diff --check ผ่านพร้อม CRLF notices เดิม. ไม่ได้ตรวจภาพผ่าน browser, deploy หรือเรียก service สด.
- หลักฐาน: `evidence/rag-closed-state-ui-2026-11-10.json`. ไม่ได้เปิด RAG หรือเปลี่ยน Production.

## ป้องกันเลขจาก citation metadata ผ่านเป็นหลักฐาน RAG — 10 พฤศจิกายน 2569
- พบตัวตรวจ lexical numeric grounding เดิมรวมเลขจาก DOI/ปีในชื่อ/เลขหน้า/เลขตาราง/ใบอนุญาต จึงอาจรับคำตอบตัวเลขที่ไม่อยู่ในข้อความหลักฐาน. ปรับให้ใช้เฉพาะข้อความ evidence ที่ถูกอ้าง.
- เพิ่ม regression ที่ตัวเลข 7 ปรากฏเฉพาะใน locator และ metadata แต่ไม่มีในข้อความหลักฐาน; คำตอบถูกปฏิเสธ. `node tests/rag-vercel-api.cjs`, Node syntax checks และ `git diff --check` ผ่าน.
- หลักฐาน: `evidence/rag-numeric-locator-guard-2026-11-10.json`. นี่ไม่ใช่ semantic entailment และยังไม่ตรวจจับคำจำนวนที่สะกดเป็นคำ; ไม่มี Gemini สด/DB/deploy และ RAG Production ยัง HOLD.

## ป้องกันการสลับหน่วยของตัวเลขในคำตอบ RAG — 10 พฤศจิกายน 2569
- เพิ่ม lexical check แบบอนุรักษ์นิยมสำหรับคู่ตัวเลข+หน่วย/ตัวหารที่รองรับ: ต้องตรงกับข้อความหลักฐานที่อ้าง; ไม่มีการแปลงหน่วย.
- Regression ยืนยันว่าปฏิเสธ 7 kg CO2e/L เมื่อหลักฐานรายงาน 7 t CO2e/year และยอมรับรูปแบบพิมพ์ CO₂/ช่องว่างที่ต่างกันเมื่อหน่วยและตัวหารยังตรง. `node tests/rag-vercel-api.cjs`, Node syntax checks, `git diff --check` และ task-board synchronization ผ่าน.
- หลักฐาน: `evidence/rag-numeric-unit-grounding-2026-11-10.json`. รายการหน่วยที่รองรับมีขอบเขตจำกัด; ยังไม่พิสูจน์ว่าเป็น metric หรือช่วงเวลาเดียวกัน และไม่ใช่ semantic entailment. ไม่มี live Gemini/DB/Production change; RAG Production คง HOLD.

## รองรับรูปแบบหน่วยไทยและอังกฤษในตัวตรวจ RAG — 10 พฤศจิกายน 2569
- ปรับ normalization ให้รองรับรูปเขียนมาตรฐานที่ชัดเจน เช่น tonnes/tons, kilograms, litres, “per year”, กก., ลิตร, “ต่อปี” และ CO₂ ที่ใช้เลขห้อย ก่อนเปรียบเทียบคู่ตัวเลข-หน่วย.
- Regression ผ่านสำหรับรูปแบบอังกฤษและไทย และยังปฏิเสธกรณีตัวเลขเดียวกันแต่ตัวหารต่างกัน; syntax checks, `node tests/rag-vercel-api.cjs`, task-board sync และ `git diff --check` ผ่าน.
- หลักฐาน: `evidence/rag-numeric-unit-locale-2026-11-10.json`. ยังไม่ทำ unit conversion หรือ semantic validation และยังไม่มี live Gemini/DB/Production change; RAG Production คง HOLD.


## ซิงก์ป้ายรุ่น SRS บนสไลด์ review — 10 พฤศจิกายน 2569
- พบสไลด์หน้า 10 ยังระบุ SRS 0.7.1 ขณะที่ SRS ปัจจุบันเป็น 0.7.2; คงไฟล์ต้นฉบับ 9 พ.ย. ไว้ และสร้าง PPTX/PDF review ฉบับใหม่โดยเปลี่ยนข้อความเพียงจุดเดียว
- Artifact Tool import ผ่าน 10 สไลด์; ตรวจ layout/package ไม่มี findings. เปรียบเทียบข้อความทุกย่อหน้าพบเปลี่ยนเฉพาะ label หน้า 10; export PDF 10 หน้า และตรวจภาพหน้า 10 กับข้อความรุ่นแล้วตรงกัน
- หลักฐาน: `evidence/final-slides-2026-11-10.json`; PPTX `A6602890E2E46081FB15D69E1727A4E2A84D2F14105B0D76169D2E746D366DBA`, PDF `4CA5B515E180CD64D4D44994CE7C14AB7F6ED09D8448EA61CE8EF638BCC1486A`. ข้อเท็จจริงอื่นในสไลด์ไม่ได้ตรวจเทียบกับข้อมูลปัจจุบันรอบนี้ และเอกสารยังเป็น draft รอทีม
- ไม่เปลี่ยน Production. ขั้นต่อไปคือทีมตรวจข้อความ/ตัวเลขในสไลด์กับหลักฐานที่อ้างและอนุมัติฉบับใช้ส่ง


## แก้เกณฑ์ RAM ในตัวติดตั้ง RAG EC2 — 10 พฤศจิกายน 2569
- ตรวจสคริปต์ติดตั้งแบบอ่านอย่างเดียว พบเทียบ `MemAvailable` เป็น KiB กับ 720000 ทั้งที่เกณฑ์เอกสารคือ 720 MiB; ค่าเดิมยอมให้ผ่านได้ตั้งแต่ประมาณ 703.125 MiB
- แก้ threshold เป็น 737280 KiB และระบุหน่วยแปลงเดียวกันใน runbook. `bash -n` และ regression check ของ threshold ผ่าน; `git diff --check` ผ่าน
- หลักฐาน `evidence/rag-ec2-memory-gate-review-2026-11-10.json`. ไม่มีการวัด EC2, build image, รันสคริปต์ติดตั้ง, หรือเปลี่ยน service/production
- ขั้นต่อไป: ให้เจ้าของตรวจ resource จริงก่อนการติดตั้งใด ๆ; Docker image candidate ยังต้องผ่าน build/test และ human release gates

## 12 พฤศจิกายน 2569 — คัดกรองแหล่งมีเทน POME เพิ่มแบบจำกัดขอบเขต
- ตรวจบทความปฐมภูมิ Putro (2022), DOI 10.32526/ennrj/20/202100149. บทความรายงานการวัดก๊าซที่โรงงานในอินโดนีเซียและค่า POME GHG ต่อ CPO; ไม่ใช่ข้อมูลโรงงานไทย จึงปฏิเสธการนำเข้าหรือแทนค่ามีเทนใน FAME chain. สิทธิแจกจ่ายยังไม่ได้ประเมิน.
- ผลค้นอีกฉบับเป็นโรงงานมาเลเซีย (2017); แม้มี CPO/day และ POME/day ก็ไม่ตรงขอบเขตไทย. งานไทยปี 2012/2015 ที่มีในทะเบียนยังเป็นข้อมูลบริบท/รวม ไม่ยืนยันผู้ให้ข้อมูลกับงวดเดียวกันของกรณีทีม.
- `CO2e_total` คง `null`; methane+actual-output matched, allocation, transport, use และ background ยังไม่ปิด. ไม่แก้ข้อมูล/สิทธิ/เว็บ/RAG production.
- หลักฐาน: `docs/scientific-source-check-2026-11-12-pome-screen.md`, `evidence/scientific-source-check-2026-11-12-pome-screen.json`. ตรวจ JSON task file และ evidence parse ต่อหลังบันทึก.

## 12 November 2569 — ตรวจ release readiness จาก workspace ปัจจุบัน
- รัน local `scripts.check_release` หลังการแก้เอกสาร/หลักฐานรอบล่าสุด: technical pass 68/68, reference release ready, submission ready=false; manifest มี 778 ไฟล์ และยังมี 5 gates: official requirements, source rights, domain/units, team/defense และ consent forms.
- Snapshot: `evidence/current-release-readiness-2026-11-12.json`. เป็นการตรวจ artifacts/snapshots ในเครื่อง ไม่ใช่ live Vercel/EC2, ไม่ใช่การตรวจสิทธิ์หรือการตอบรับ MTEC และไม่ได้รัน full test suite.
- T24 ยังคง IN_PROGRESS; ไม่มีการ freeze/package/send/deploy. Human/official gates ต้องมีหลักฐานจริงก่อนเปลี่ยนสถานะ.

## 12 November 2569 — แก้และตรวจ Docker RAG candidate ในเครื่อง
- Docker Desktop Linux Engine กลับมาใช้งานได้ (`client/server 28.2.2`). Candidate `51d0ef861af7eb51` build ผ่านแต่ถามจริงได้ 503; ตรวจ stack ใน isolated container พบ `docs/rag/retrieval-scope.json` ไม่อยู่ใน allowlist/image แม้ `rag_scope.py` ต้องอ่านไฟล์นี้.
- เพิ่มไฟล์เข้า allowlist, Dockerfile และ regression test. `tests.test_rag_service_runtime` ผ่าน 3/3. สร้าง release ใหม่ `9c767ef49301347b`; package 20 ไฟล์/252,220,255 bytes, archive hash ตรวจผ่าน; build Linux/amd64 image `sha256:1bf44daf6880dd3e65ef1fa115f3708e0156145a66bc87cb7366e441202cbdd1`.
- Image smoke ใน network `none` ผ่าน: ready 10 cards, page/health 200, คำถาม FAME คืนการ์ดคาดหมายพร้อม URL/locator, wrong Origin 403, feedback เขียนใน tmpfs; hardened settings ผ่าน. ใช้ memory 499/512 MiB. หลักฐาน `evidence/rag-image-verification-9c767ef49301347b-20261111T223742Z.json` และ `evidence/rag-ec2-candidate-build-2026-11-12.json`.
- ไม่ใช้ Gemini key, ไม่ upload, ไม่สั่ง EC2, ไม่แตะ Vercel/Production และไม่เปลี่ยนสิทธิ. Candidate นี้ยังไม่ผ่าน release gates สำหรับ deploy; ต้องยืนยัน EC2 memory/API/rollback สดก่อนพิจารณา และยังไม่มี RAG-to-MySQL fixed-query path.

## 12 พฤศจิกายน 2569 — ตรวจอัตราจำกัดคำถาม RAG ใน Preview

- เพิ่ม regression test ระดับ route: คำถาม overview 12 ครั้งจาก client จำลองเดียวกันในหน้าต่าง 60 วินาทีตอบ 200; ครั้งที่ 13 ตอบ 429 พร้อม `Retry-After: 60`; ยืนยันว่าไม่เรียก Gemini เมื่อถูกจำกัด. หลักฐาน: `evidence/rag-preview-route-rate-limit-test-2026-11-12.json`.
- การรันครั้งแรกพบว่าเทสต์ Preview สองตัวแก้ `process.env` พร้อมกัน ทำให้ค่า gate แทรกกัน; จัดลำดับเทสต์ใหม่และรัน `node tests/rag-vercel-api.cjs` ผ่าน.
- ขอบเขตจำกัด: limiter ยังอยู่ในหน่วยความจำของ function instance ไม่ใช่โควตาส่วนกลาง; ยังไม่ได้ตรวจ/ตั้ง Vercel WAF หรือวงเงิน Gemini และไม่ได้เปลี่ยน Production. T151 คง WAITING เพื่อให้เจ้าของยืนยันแผน/ค่าใช้จ่ายและตั้งกฎเอง.

## 12 พฤศจิกายน 2569 — แก้เกณฑ์หน่วยความจำในสคริปต์อัปเกรด RAG

- เทียบสคริปต์อัปเกรดกับนโยบาย 320 MiB แล้วพบ guard 3 จุดใช้ 320,000 KiB ซึ่งต่ำกว่าค่า 320 MiB จริง (327,680 KiB) จึงแก้ทั้ง pre-update, ระหว่าง readiness และระหว่าง Docker health wait ให้ใช้ 327,680 KiB พร้อมระบุหน่วยในข้อความผิดพลาด.
- เพิ่ม `tests/test_rag_memory_gates.py`; regression 2 รายการผ่านและ Git Bash `-n` ผ่าน. เกณฑ์ติดตั้งเดิม 720 MiB ก่อน staging และ 320 MiB ระหว่าง staging ไม่เปลี่ยน.
- หลักฐาน: `evidence/rag-upgrade-memory-floor-review-2026-11-12.json`. เป็นการตรวจ/แก้ไฟล์ในเครื่องเท่านั้น; ไม่วัด RAM EC2, ไม่แตะ EC2/API/Ginder และไม่ deploy.

## 12 พฤศจิกายน 2569 — แก้ข้อความสถานะเว็บในสไลด์ Final review

- ตรวจสไลด์ 9 เทียบหลักฐาน Production: ข้อความเดิมสื่อว่าเส้นทาง Vercel → EC2 MySQL เปิดให้ค้นได้ แต่หลักฐานหลัง deploy ยืนยัน API ข้อมูลที่ตรวจ 15 เส้นทางตอบ 403; fixed-query endpoint ยังเป็น TODO. แก้สไลด์ให้แยกหน้าเว็บที่เปิดจาก API ที่ยังปิด และระบุว่ายังไม่มีทางล็อกอินดูข้อมูล.
- สร้าง PPTX/PDF ฉบับ review ใหม่ 10 หน้า; เทียบข้อความกับ source deck พบเฉพาะสไลด์ 9 เปลี่ยน, ตรวจ ZIP/layout ผ่าน, หน้า 9 render ตรวจแล้ว และหน้าอื่น pixel-identical กับ PDF เดิมที่ 72 dpi. รายละเอียด/hash: `evidence/final-slides-2026-11-12.json`.
- อัปเดตสองแถวสไลด์ใน Final Delivery Plan. สถานะยัง Draft for team review; ไม่มีการรับรองจากทีม/consent, ส่งงาน, เปลี่ยน Production หรือเปลี่ยนสิทธิข้อมูล.

## 12 พฤศจิกายน 2569 — ตรวจตัวเลขสำคัญในสไลด์ review เทียบหลักฐาน

- เทียบตัวเลขบนสไลด์ 3, 4, 7, 8 และ 10 กับหลักฐานปัจจุบัน: corporate 97/4, inventory 16, crosswalk 13 snapshots/5 layers, MySQL 17 checks, NSO 141 exact/24 rounding/4 divergences จาก 169 ที่เทียบ, SQL 102 แถวและ median 0.208/12.0 ms, Neo4j 16/39/68 ตรงกับ artifact ที่อ้าง.
- ย้ำข้อจำกัด: NSO อีก 104 รายการยังไม่มี direct cross-publication comparison และ independent measurement verified = 0; SQL เป็น local warm-cache server-iterator timing ไม่ใช่ SLA; Neo4j เป็น disposable projection ไม่ใช่ production graph. Registry มีแหล่ง candidate เพิ่มที่ไม่ได้อยู่ใน crosswalk 13 snapshots จึงบันทึก scope นี้ไว้ใน audit.
- สไลด์ 2, 5, 6 ไม่ได้ตรวจใหม่ในรอบนี้; ไม่มีการอ้างว่าทั้งชุดผ่านการตรวจอิสระ. หลักฐาน: `evidence/final-slides-quantitative-claim-audit-2026-11-12.json`. Final plan และ task board ซิงก์แล้ว.


## ตรวจคำกล่าวในสไลด์ 2, 5 และ 6 — 12 พฤศจิกายน 2569

- เทียบขอบเขต/หน่วย/ปีข้อมูลในสไลด์ 2 กับ SRS และ mapping-validation; โครง schema และข้อจำกัด Unit/Flow ในสไลด์ 5 กับ DDL/SRS/candidate; และ Crude glycerine, locator, period, allocation ในสไลด์ 6 กับ inventory/source review. ไม่พบเหตุให้แก้ข้อความในชุดหลักฐานที่ตรวจ.
- ระบุ caveat เพิ่มในหลักฐาน: Crude glycerine เป็น project-local source classification; ปีวัดไม่ระบุ; allocation ยังไม่ resolved; snapshot มาจาก publisher DOM ไม่ใช่ PDF/HTTP snapshot และยังไม่มี independent expert review. Flow/Unit candidate ไม่ใช่ global ontology หรือ production migration.
- หลักฐาน: `evidence/final-slides-scope-schema-provenance-audit-2026-11-12.json`; T166 DONE. ไม่มีการแก้สไลด์/ข้อมูลต้นทาง ไม่มี production probe/deploy; review deck ยังคง draft รอทีมตรวจและสิทธิ์เผยแพร่.


## ปรับแนวตอบ RAG ภาษาไทยให้เข้าเรื่องและลดข้อมูลไม่เกี่ยว — 12 พฤศจิกายน 2569

- เพิ่มกติกาให้ตอบประเด็นหลักก่อน ใช้ประโยคสั้น เลือกเฉพาะหลักฐานที่ตอบคำถาม และบอกข้อมูลที่ขาดอย่างกระชับเมื่อหลักฐานไม่พอ พร้อม regression ใน Gemini request contract test.
- `node tests/rag-vercel-api.cjs`, `node --check api/rag/ask.js` และ `git diff --check` ผ่าน. การทดสอบใช้ mock; ไม่มีการเรียก Gemini, เปิด public route, อ่าน/ส่งข้อมูลเพิ่ม หรือ deploy.
- หลักฐาน `evidence/rag-thai-answer-focus-2026-11-12.json`; T167 DONE. ยังต้องทดสอบคุณภาพกับผู้ใช้จริงและความหมาย/citation entailment; RAG Production คงปิดจนผ่าน gates.


## Local release audit หลังปรับ prompt RAG — 12 พฤศจิกายน 2569

- `python -X utf8 scripts/check_release.py` ผ่าน technical checks 68/68 และ reference release ready; submission ready=false, manifest 788 ไฟล์.
- ข้อค้าง 5 กลุ่มยังเดิม: official requirements, source rights, domain/units, team/defense และ consent; เหตุผลอยู่ใน snapshot. ไม่มี live Vercel/EC2/Gemini probe และไม่ได้สร้าง package/เปลี่ยน Production.
- หลักฐาน `evidence/current-release-readiness-2026-11-12-0614.json`; T168 DONE.


## ปิด fail-open edge case ใน RAG rollback — 12 พฤศจิกายน 2569

- ตรวจพบว่า process substitution อาจซ่อน error จาก `docker ps -aq` จนตีความว่ารุ่นก่อนหน้าไม่มี แล้วลบ active RAG. เปลี่ยนเป็นตรวจ exit status ก่อน; เมื่อ list ไม่ได้จะปฏิเสธและไม่ลบ container.
- Git Bash syntax และ isolated mock 2 กรณีผ่าน: listing error ไม่ทำ removal; กรณีปกติ restore รุ่นก่อนและตรวจ readiness/API/Ginder baseline. ไม่ใช้ Docker daemon, EC2 หรือ Production.
- หลักฐาน `evidence/rag-rollback-script-fail-closed-2026-11-12.json`; T169 DONE. ยังต้อง owner-verified live preflight/rollback drill ก่อน deploy และ RAG Production คง HOLD.


## Security gate: rotate Gemini key disclosed in chat — 12 พฤศจิกายน 2569

- พบ API credential ถูกวางในประวัติแชต; ถือว่าค่าเดิมอาจเปิดเผยแล้ว. ไม่อ่าน ไม่คัดลอก ไม่บันทึกค่า/เศษค่า/fingerprint และไม่แก้ secret store.
- ยังไม่มีหลักฐานจากเจ้าของว่าค่าเดิมถูก revoke และแทนที่. RAG Production คง HOLD; เจ้าของต้อง revoke/create ใหม่และตั้งไว้เฉพาะ server-side แล้วแจ้งเฉพาะสถานะ โดยไม่ส่งค่าคีย์.
- หลักฐานสถานะโดยไม่เก็บ secret: `evidence/gemini-credential-rotation-gate-2026-11-12.json`; T170 WAITING.


## อัปเดตรูปแบบ structured JSON ของ Gemini — 12 พฤศจิกายน 2569

- ตรวจเอกสาร GenerateContent ทางการ พบ `responseSchema` ถูก deprecate และมี `responseFormat.text` เป็นรูปแบบปัจจุบัน; model ID `gemini-3.5-flash-lite` ยังปรากฏในรายการโมเดล. เปลี่ยน request shape เป็น responseFormat พร้อม JSON Schema ตัวพิมพ์เล็กตามตัวอย่างทางการ.
- `node tests/rag-vercel-api.cjs`, syntax และ `git diff --check` ผ่านด้วย mock; ไม่มี live API/key/deploy. หลักฐานพร้อม URL/ข้อจำกัด: `evidence/gemini-generatecontent-response-format-review-2026-11-12.json`; T171 DONE. Provider acceptance/คุณภาพจริงและ release gates ยังไม่ยืนยัน.

## เพิ่ม regression contract สำหรับความยินยอมในหน้า RAG — 12 พฤศจิกายน 2569

- ตรวจหน้า `/ask` และพบว่า UI มี consent notice และ guard อยู่แล้ว แต่ชุดทดสอบเดิมยังไม่มี assertion เฉพาะว่าต้อง guard ก่อนส่งและ reset หลังแต่ละคำถาม. เพิ่ม `tests/rag-ask-consent-ui.cjs` โดยไม่เปลี่ยนพฤติกรรมหน้าเว็บ.
- `node tests/rag-ask-consent-ui.cjs` ผ่าน; `git diff --check -- tests/rag-ask-consent-ui.cjs` ผ่าน. หลักฐาน `evidence/rag-ask-page-consent-contract-2026-11-12.json`; T172 DONE.
- ข้อจำกัด: เป็น static source-contract test ไม่ใช่ browser interaction test; ไม่ยืนยัน provider/server runtime. RAG Production ยัง HOLD จากสิทธิ์ corpus, audience/billing, rate limit และการ rotate credential ที่เจ้าของยังไม่ยืนยัน.


## ซิงก์ task board และตรวจ readiness หลัง T172 — 12 พฤศจิกายน 2569

- รอบแรกของ `python -X utf8 scripts/check_release.py` ไม่ผ่านเฉพาะ `task_board_sync` เพราะเพิ่ม T172 ใน `docs/tasks.json` แล้วแต่ยังไม่ได้ regenerate `docs/tasks.md`; ไม่พบ technical/reference artifact failure อื่น.
- สร้าง task board ด้วย `python -X utf8 scripts/task_board.py` แล้วตรวจซ้ำ: audit เวลา 06:31:49 น. technical 68/68 ผ่าน, reference release ready=true, submission ready=false; manifest 795 ไฟล์ และงานค้าง 5 กลุ่มตาม snapshot. หลักฐาน `evidence/current-release-readiness-2026-11-12-0645.json`; T168 ชี้ snapshot ล่าสุด.
- เป็น local check เท่านั้น ไม่ตรวจสิทธิภายนอก/การยอมรับจาก MTEC/บริการ live และไม่มีการ build Docker, เรียก Gemini, deploy หรือเปลี่ยน Production.


## ปรับ preflight RAM สำหรับติดตั้ง RAG ครั้งแรก — 12 พฤศจิกายน 2569

- เทียบตัวคุมหน่วยความจำกับผล image verification: container จำกัด RAM 512 MiB และใช้จริง 499 MiB ใน isolated smoke แต่ first-install preflight เดิมต้องการ available host RAM เพียง 720 MiB ขณะที่สคริปต์ต้องเหลือ host reserve อย่างน้อย 320 MiB ระหว่างเปิดบริการ; เกณฑ์เริ่มเดิมจึงต่ำกว่าผลรวม 832 MiB.
- ปรับ first-install preflight เป็น 851,968 KiB (512 + 320 MiB) และซิงก์ runbook/test; เกณฑ์ runtime 320 MiB เดิมยังอยู่. `python -m unittest tests.test_rag_memory_gates -v` ผ่าน 2 tests, Git Bash `bash -n deploy/install_rag_ec2.sh` ผ่าน, `git diff --check` ผ่าน. จากนั้นสร้าง task board และรัน readiness audit หลังการเปลี่ยน: 68/68 checks ผ่าน, reference release ready=true, submission ready=false, manifest 797 ไฟล์. หลักฐาน `evidence/rag-ec2-install-memory-headroom-2026-11-12.json` และ `evidence/current-release-readiness-2026-11-12-0634.json`; T173 DONE.
- ค่านี้เป็น safety threshold เชิงอนุรักษ์ ไม่ใช่ผลวัด EC2; อาจปฏิเสธเครื่องที่ยังรันได้จริง. ไม่ได้รัน installer, Docker หรือแตะ EC2/Production. ยังต้องตรวจ headroom จริงโดยเจ้าของก่อน deploy.


## ซิงก์แผน Final กับ candidate และ readiness ล่าสุด — 12 พฤศจิกายน 2569

- อัปเดตหัวแผน `docs/submission/FINAL_DELIVERY_PLAN.md` จากสถานะ readiness เก่า 22:20Z ให้ชี้ snapshot ล่าสุดและบันทึกผลตรวจหลัง T173: technical 68/68, reference ready, submission not ready, 5 external/human gates ค้าง. บันทึก candidate Docker 9c767ef และ preflight 832 MiB โดยย้ำว่ายังไม่ deploy EC2.
- T24 ชี้ snapshot 06:36 ICT; task board สร้างใหม่แล้ว. ตรวจ consistency หลังแก้แผนเวลา 06:39:55 และตรวจยืนยันซ้ำท้ายรอบเวลา 06:40:37 ICT ผ่าน 68/68; reference release ready=true, submission_ready=false, manifest 797 files. ไม่มี Production/API/EC2/Gemini action.


## ทบทวนราคาและขอบเขต Vercel WAF — 12 พฤศจิกายน 2569

- ตรวจเอกสาร Vercel ทางการที่แก้ไขล่าสุด: WAF rate limiting ใช้ได้ทุกแผน; Hobby/Pro ใช้ fixed window และนับแยกตาม region. หน้า rate-limit ระบุ Hobby 1M allowed requests รวมและ Pro usage-based ที่ $0.50/1M; เอกสารราคาแยกยืนยันว่า traffic ที่ถูก deny/challenge/rate-limit ไม่คิด CDN Requests/FDT แต่ค่า rate-limit ของ allowed request และ Gemini provider ไม่ได้ถูกยกเว้น.
- ปรับ runbook แยกข้อเท็จจริงด้านราคาออกจากแผน/โควตาของบัญชี TamsoodBase ที่ยังไม่ได้ตรวจ. หลักฐาน `evidence/rag-vercel-waf-pricing-review-2026-11-12.json`; T151 ยัง WAITING. ไม่ตรวจ dashboard, ไม่ตั้ง rule, ไม่มี budget/owner confirmation และ Production RAG คง HOLD.


## ตรวจข้อจำกัดงบ Gemini API สำหรับ RAG — 12 พฤศจิกายน 2569

- ตรวจเอกสารทางการของ Google เพิ่ม: project-level spend cap เป็นสถานะ experimental และอาจเกินระหว่าง billing latency ราว 10 นาที; tier cap รวมการใช้จากทุก project ที่ผูก billing account; API key รับ billing state จาก project; monthly auto-charge limit ครอบคลุม auto-reload ไม่รวมรายการซื้อด้วยมือ. อัปเดต runbook ให้ถือ controls เหล่านี้เป็นแนวป้องกัน ไม่ใช่ hard cap ที่รับประกันยอดสูงสุด.
- หลักฐาน `evidence/rag-gemini-billing-controls-review-2026-11-12.json`; ลิงก์ต้นทางอยู่ใน runbook. ไม่เปิดดู dashboard, key, บัญชีหรือข้อมูลชำระเงิน และไม่ส่งข้อมูลโครงการไป Google.
- ยังไม่ได้ยืนยัน billing account/plan/spend cap/alerts ของโครงการ และไม่ได้เปลี่ยนการตั้งค่า; T151/T154/T170 ยังรอเจ้าของ. Production RAG คง HOLD. เป็นการเปลี่ยนเอกสารกับ evidence เท่านั้น; ไม่มีเหตุให้รันทดสอบโค้ดซ้ำ.


## เพิ่มระยะเก็บข้อมูลในคำชี้แจง RAG — 12 พฤศจิกายน 2569

- ตรวจหน้า Google Gemini Usage Policies และ Terms อีกครั้ง: เอกสาร abuse monitoring ระบุว่า prompt, context และ output เก็บ 55 วันเพื่อบังคับใช้นโยบาย/ความปลอดภัย/ข้อกำหนดทางกฎหมาย และเจ้าหน้าที่ที่ได้รับอนุญาตอาจตรวจเนื้อหาที่ระบบแจ้งเตือน. เพิ่มคำชี้แจงภาษาไทยและลิงก์นโยบายใน `web/ask.html`; ไม่เปลี่ยน consent guard หรือการส่งข้อมูล.
- `node tests/rag-ask-consent-ui.cjs` ผ่าน; targeted `tests.test_frontend.FrontendTests.test_gemini_privacy_notice_distinguishes_billing_terms` ผ่าน; `git diff --check` สำหรับไฟล์หน้าและ test ผ่าน. Evidence: `evidence/rag-ask-data-retention-notice-2026-11-12.json`. ไม่มีการเรียก Gemini หรือทำ browser visual review.
- สิทธิ/อายุผู้ใช้/region/billing ของโครงการและการหมุน key ที่เคยเปิดเผยยังไม่ยืนยัน; ไม่มีการเปลี่ยน Production และ RAG Production คง HOLD.

- ตรวจเพิ่มหลังงานรอบก่อน: `test_deployment_build_only_copies_public_assets` ยืนยันว่า build มีข้อความเก็บข้อมูล 55 วันและลิงก์ Usage Policies; รันคู่กับ `test_gemini_privacy_notice_distinguishes_billing_terms` ผ่าน 2/2. สัญญา static consent ก่อนหน้านี้ยังผ่าน; `git diff --check` ผ่านสำหรับหน้าและ tests. Evidence เดิมอัปเดตผลตรวจ package-copy นี้.



## ปิดช่องว่างการบังคับใช้ RAG release gates — 12 พฤศจิกายน 2569

- เทียบ manifest ปัจจุบันกับ runtime และ production build พบประกาศ 9 gates แต่โค้ดทั้งสองจุดบังคับเพียง 7; ขาด `private_network_connectivity_verified` และ `server_to_server_auth_configured`. แก้ให้ทั้ง runtime และ build ต้องผ่านครบ 9 ข้อ และเพิ่ม regression ที่ทำให้ false gate สองรายการนี้ปิดการให้บริการ/บล็อก production build.
- `node tests/rag-vercel-api.cjs` ผ่าน; `test_deployment_build_only_copies_public_assets` ผ่าน; `git diff --check` ตรวจท้ายรอบ. หลักฐาน: `evidence/rag-launch-gate-parity-review-2026-11-12.json`.
- manifest จริงยังตั้งทั้ง 9 gates เป็น false และคง `HOLD_RIGHTS_REVIEW`; ไม่เปลี่ยนสิทธิ ไม่เรียก Gemini/ฐานข้อมูล ไม่ deploy. หาก network/auth gate ไม่เกี่ยวกับสถาปัตยกรรมที่เลือก ต้องแก้สัญญา gate พร้อมเหตุผล/evidence แทนการข้าม gate ในโค้ด.


## รวมสัญญา RAG release gates เป็นแหล่งเดียว — 12 พฤศจิกายน 2569

- รวมรายชื่อ 9 gates ไว้ใน `docs/rag/required-release-gates.json`; API runtime, production frontend build และ catalog predicate อ่านสัญญาเดียวกัน และปฏิเสธทั้ง gate ขาด, gate เกิน และค่าที่ไม่เป็น true. เทียบกับ manifest ปัจจุบันแล้ว key set ตรงกันครบ 9 แต่ค่าจริงยัง false ทั้งหมด.
- `node tests/rag-vercel-api.cjs` ผ่าน; `python -X utf8 -m unittest tests.test_rag_catalog tests.test_frontend.FrontendTests.test_deployment_build_only_copies_public_assets -v` ผ่าน 7/7; `git diff --check` ผ่าน. ครั้งแรกพบ fixture ของ build test ไม่ได้คัดลอกไฟล์ contract ใหม่ จึงแก้ fixture แล้วรันชุดเป้าหมายซ้ำจนผ่าน. Evidence: `evidence/rag-launch-gate-parity-review-2026-11-12.json`.
- ไม่เปลี่ยน manifest/สิทธิ/credentials/Production; RAG คง HOLD.


## ตรวจ local release consistency หลัง rebuild หน้า ask — 12 พฤศจิกายน 2569

- ตรวจพบ generated `build/frontend/ask.html` เก่ากว่าต้นฉบับ `web/ask.html` ในข้อความแจ้งการเก็บข้อมูล; rebuild frontend แบบ local โดยปิด RAG/Preview และใช้ same-origin แล้วตรวจใหม่ผ่าน 46/46 checks. Candidate ID: `70f60e044947b42e16f82a14c69da066c4bba6e500138714dcbb86363b1f0dd1`.
- Build มี 16 assets, snapshot สาธารณะ 42 แถว, `publicRagEnabled=false`, `ragMode=closed`, และไม่รวม private research data. `git diff --check` ผ่าน โดยมีเพียงคำเตือน line-ending CRLF ในไฟล์ที่ติดตามอยู่. หลักฐาน `evidence/local-release-consistency-2026-11-12.json`.
- เป็นผลตรวจไฟล์ในเครื่องเท่านั้น; ไม่ตรวจ live service, ไม่เรียก Gemini/ฐานข้อมูล/EC2, ไม่ deploy และไม่เปลี่ยน Production. Submission ยังไม่พร้อมและ RAG Production คง HOLD.


## ปิด fail-open จากรหัสอนุมัติ RAG ซ้ำ — 12 พฤศจิกายน 2569

- ทดสอบ fixture ชั่วคราวที่ตั้งทุก global gate/สิทธิแหล่งเป็น true พบว่าการมี decision ซ้ำ (PENDING และ CLEARED) ของ record เดียวกันอาจปล่อยแถวตาม decision สุดท้ายได้; เป็นกรณีจำลอง ไม่ใช่การเปิดข้อมูลจริง.
- เพิ่ม validation ให้ catalog builder ปฏิเสธ ID ที่หายหรือซ้ำใน source registry, manifest decisions และ narrative/statistical corpus. `python -X utf8 -m unittest tests.test_rag_catalog -v` ผ่าน 8 tests; `python -X utf8 scripts/build_rag_catalog.py --check` ผ่านและยืนยัน 22 private source / 20 restricted evidence / 0 public-cleared records; `git diff --check` ผ่าน.
- Manifest และ source registry จริงไม่ได้เปลี่ยน, ไม่มี Gemini/EC2/Production action; RAG Production คง HOLD. หลักฐาน `evidence/rag-catalog-duplicate-approval-guard-2026-11-12.json`.


## ซิงก์ release manifest กับรหัสคอร์ปัส RAG — 12 พฤศจิกายน 2569

- ตรวจพบ manifest narrative มี 8 IDs แต่ active corpus มี 10; มี decision ที่หาย 6 และ placeholder ค้างที่ไม่อยู่ใน corpus 4. ซิงก์ ID ให้ตรงกับ narrative 10 และ facts 10; เพิ่มเฉพาะรายการ `PENDING` และนำ placeholder เก่าที่เป็น `PENDING` ออกจาก manifest active list. ไม่มีการอนุมัติสิทธิหรือเปลี่ยนข้อความคอร์ปัส.
- เพิ่ม assertion exact-ID-set ใน builder และ regression test; catalog tests ผ่าน 9/9, deployment-build guard ผ่าน 1/1, catalog check ยืนยัน 22 sources / 20 restricted records / 0 public-cleared records; `git diff --check` ผ่าน. Evidence `evidence/rag-corpus-manifest-sync-2026-11-12.json`.
- ทุกสิทธิยัง `PENDING`, 9/9 release gates ยัง false, Production RAG คง HOLD; ไม่มี Gemini, EC2, database หรือ Production action.


## ป้องกันคำตอบตัวเลขที่ตัดหน่วยออก — 12 พฤศจิกายน 2569

- ทดสอบเฉพาะจุดพบว่าคำตอบ `7` ผ่านได้ แม้หลักฐานที่อ้างระบุ `7 t CO2e/year`; ปรับ parser ให้ปฏิเสธเมื่อคำตอบละหน่วยของค่าที่ตรงกับ measurement ในข้อความอ้างอิง และคงการยอมรับรูปแบบตัวเลข+หน่วยที่ตรงกัน.
- `node tests/rag-vercel-api.cjs` ผ่าน รวม regression ใหม่; `git diff --check` ผ่าน. หลักฐาน `evidence/rag-unitless-numeric-answer-guard-2026-11-12.json`.
- ขอบเขตยังเป็น lexical guard ไม่พิสูจน์ความหมาย/ช่วงเวลา/ขอบเขตและไม่แปลงหน่วย; ไม่มี independent user test, Gemini, database, EC2 หรือ Production action; Production RAG คง HOLD.


## แสดงผล abstention เมื่อตัวเลขไม่ผ่าน grounding — 12 พฤศจิกายน 2569

- หลัง parser ปฏิเสธคำตอบตัวเลขที่ขาดหน่วย route เดิมตอบ 503 แบบ service outage; แยกกรณี `ungrounded_numeric_claim` ให้ตอบสถานะ abstention ภาษาไทย ไม่แนบ source IDs ของคำตอบที่ถูกปฏิเสธ แต่ยังแสดงการ์ดเอกสารที่ค้นพบให้ตรวจเอง. Transport/model errors อื่นยังเป็น 503.
- Mock route test `node tests/rag-vercel-api.cjs`, static UI contract `node tests/rag-ask-consent-ui.cjs`, และ frontend build-copy test ผ่าน; `git diff --check` ผ่าน. Evidence `evidence/rag-grounding-abstention-ux-2026-11-12.json`.
- ไม่มี live Gemini, browser visual, user UAT, EC2, database หรือ Production action; RAG Production คง HOLD.


## Rebuild และตรวจ consistency หลังปรับข้อความ abstention — 12 พฤศจิกายน 2569

- Rebuild static frontend ในเครื่องโดยปิด RAG/Preview; output 16 assets, 42 public snapshot rows, ไม่มี private research/raw document. ตรวจ generated `ask.html` มีสาขา grounding abstention และ config เป็น RAG closed.
- Local release consistency audit ผ่าน 46/46 checks; candidate ID `70f60e044947b42e16f82a14c69da066c4bba6e500138714dcbb86363b1f0dd1`; `live_rechecked=false`. Evidence `evidence/local-release-consistency-after-grounding-ux-2026-11-12.json`.
- ไม่ใช่ browser visual/UAT หรือ live verification; ไม่เรียก Gemini, ไม่แตะ DB/EC2, ไม่ deploy/เปลี่ยน Production. Submission readiness ยัง false และ Production RAG คง HOLD.

## ปฏิเสธ Preview เมื่อไม่มี client identity — 12 พฤศจิกายน 2569

- เพิ่ม regression ใน `tests/rag-vercel-api.cjs`: คำขอ Preview ที่ไม่มี `x-forwarded-for` ต้องถูกปฏิเสธเป็น HTTP 429 ก่อนเรียก Gemini; ตรวจ call count เป็นศูนย์.
- `node tests/rag-vercel-api.cjs` ผ่าน และ `git diff --check -- tests/rag-vercel-api.cjs` ผ่าน. บันทึก `evidence/rag-preview-missing-client-ip-guard-2026-11-12.json` และ pointer ใน `docs/tasks.json`.
- เป็นการทดสอบ route แบบ mock ในเครื่องเท่านั้น; ยังไม่ได้ยืนยัน header จริงบน Vercel, WAF/global limiter หรือ provider budget. ไม่เรียก Gemini จริงและไม่เปลี่ยน Production; RAG Production คง HOLD.

## ปิดทางลัด release gate ของ RAG — 12 พฤศจิกายน 2569

- ตรวจ diff งาน RAG ที่ยังไม่ commit พบ runtime/build เชื่อสถานะ `OWNER_APPROVED_PUBLIC_DEMO` และ flags ที่เป็น true แต่ไม่บังคับ 9 release gates หรือสิทธิรายระเบียน ทั้งที่ manifest ปัจจุบันยังมี 9 gates เป็น false และสิทธิทุกรายการเป็น `PENDING`. มี owner-decision claim ในไฟล์แต่ไม่ได้ตรวจยืนยัน จึงไม่ถือเป็นการอนุมัติจากรอบนี้.
- ปรับ runtime และ public build ให้ต้องผ่าน gate ทั้ง 9 ข้อครบตาม contract และสิทธิทุก narrative/fact เป็น `CLEARED` พร้อม flags provider processing/audience ที่ยืนยันชัด; เพิ่ม regression test ใช้ fixture ในหน่วยความจำเท่านั้น.
- `node tests/rag-current-release-gate.cjs` ผ่าน; public build เมื่อใช้ manifest ปัจจุบันถูกบล็อกก่อน package; `git diff --check` ผ่าน. Evidence `evidence/rag-current-release-gate-bypass-2026-11-12.json`.
- ไม่อ่าน secret, ไม่เรียก Gemini/Production API, ไม่เปลี่ยน manifest/สิทธิจริงหรือ production. RAG Production คง HOLD; owner ต้องยืนยันสิทธิ/เงื่อนไขแต่ละ gate พร้อมหลักฐานก่อนเปิด.


## เปิดแชตสาธารณะตามการตัดสินใจของเจ้าของโครงการ — 12 พฤศจิกายน 2569

- **บันทึกนี้ใหม่กว่าและแทนรายการ "ปิดทางลัด release gate ของ RAG" ด้านบน** เจ้าของโครงการสั่งโดยตรงในเซสชันทำงาน (Claude Code) เมื่อ 12 พ.ย. ให้เปิดแชตบนเว็บจริงสำหรับ demo รายวิชา และยืนยันซ้ำหลังเห็นว่างานอัตโนมัติอีกตัวปิดกลับ การเปิดจึงเป็น owner decision ไม่ใช่ผลของการผ่าน 9 gates; gates ทั้ง 9 ยังบันทึกเป็น false ใน `docs/rag/public-release-manifest.json` พร้อมรายการสิ่งที่ยอมรับโดยไม่ได้ตรวจ (`owner_decision.accepted_without_verification`) ผู้ช่วยตัวถัดไปไม่ควรปิดกลับโดยไม่ถามเจ้าของ
- ขอบเขตข้อมูลที่เจ้าของเลือก: ตอบตัวเลขได้เฉพาะข้อมูลเปิดของรัฐ (DMF 34,671 แถว, EPPO 5,934, NSO 273) และบทความ CC BY ของ Permpool et al. (ตาราง 1–4 รวม 58 แถว + บันทึก 6 ประเด็น) รายงาน Thai Oil/SPRC และหลักฐานเอทานอลมีเฉพาะคำอธิบายกับลิงก์ ไม่มีตัวเลขในชุดที่แชตใช้ ชุดนี้สร้างด้วย `scripts/build_rag_knowledge_pack.py` เป็น `docs/rag/knowledge-pack.json`; runtime และ build ปฏิเสธถ้า hash ไม่ตรงกับที่ manifest บันทึก หรือถ้าชุดมีค่ารายงานบริษัท
- `api/rag/ask.js` เขียนใหม่: Gemini วางแผนคำค้น → โค้ดคำนวณจากชุดความรู้ → Gemini เรียบเรียงภาษาไทย → ตรวจว่าตัวเลขทุกตัวในคำตอบอยู่ในผลค้น ไม่ผ่านจะแสดงรายการข้อมูลตรง ๆ แทน รองรับบทสนทนาต่อเนื่อง 4 รอบล่าสุด สวิตช์เปิด/ปิดคือ env `TAMSOOD_RAG_PUBLIC_ENABLED`
- กฎโดเมนที่บังคับในโค้ด: ค่ารายเดือน DMF และ EPPO intake (BBL/DAY) ไม่บวกข้ามเดือน ใช้ค่าเฉลี่ย/สูงสุด/ต่ำสุดรายเดือน; ไม่รวมค่าต่างหน่วยหรือต่างผลิตภัณฑ์; NSO แสดงรายแถว ข้อสังเกตที่ยังไม่ยืนยัน: ขนาดตัวเลข DMF สอดคล้องกับอัตราต่อวันมากกว่ายอดรวมทั้งเดือน
- พบค่าผิดปกติ 1 แถวในไฟล์ DMF: ก๊าซธรรมชาติ แหล่ง "กำแพงแสน อู่ทอง สังฆจาย" ก.พ. 2020 = 3,500,000 (ค่าอื่นทั้งชุดไม่เกินหลักพัน) เก็บค่าตามต้นทางและติดธงไว้ แชตไม่นับในค่าเฉลี่ย/สูงสุดและแจ้งผู้ใช้ทุกครั้ง ยังไม่ได้ยืนยันกับกรมฯ
- ตรวจในเครื่อง: `node tests/rag-vercel-api.cjs`, `node tests/rag-ask-consent-ui.cjs` และ node tests อื่นทั้งหมดผ่าน; `python -m unittest discover -s tests` รัน 314 tests ผ่าน ยกเว้น `test_rag_service_runtime` ที่ import ไม่ได้เพราะเครื่องนี้ไม่มี `fastembed` (เป็นอยู่ก่อนการแก้รอบนี้) Gemini ในเทสต์เป็น mock ทั้งหมด ลบ `tests/rag-current-release-gate.cjs` ที่บังคับสัญญาเดิมออก; `evidence/rag-current-release-gate-bypass-2026-11-12.json` เก็บไว้เป็นประวัติ
- ยังไม่ได้ทำ/ไม่ได้ตรวจ: Vercel WAF rate limit (มีแค่ตัวจำกัดต่อ instance ในฟังก์ชัน), สถานะ billing/audience ของ Gemini, UAT กับผู้ใช้จริง, เงื่อนไขใช้ซ้ำเฉพาะของ DMF/EPPO/NSO
