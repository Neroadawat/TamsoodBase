# Semantic retrieval ในผู้ช่วย TamsoodBase (15 พฤศจิกายน 2569)

## สถานะจริง

- **เปิดใช้บน production แล้วตั้งแต่ 15 พฤศจิกายน 2569** (Vercel env `TAMSOOD_SEMANTIC_ENABLED=true` บน Production, commit bcfcd9b) ปิดได้โดยลบ/แก้ flag ค่าเริ่มต้นเมื่อไม่ตั้ง = ผู้ช่วยทำงานเหมือนเดิมทุกประการ
- ผลวัดตัวเลข Recall และ latency ในส่วน "ผลที่วัดได้" เป็น **คุณภาพการค้นคืนบน corpus 21 ชิ้นเท่านั้น** ส่วนผลกับ Gemini จริงอยู่ในหัวข้อ "ผลตรวจจริง" ท้ายไฟล์
- ก่อนเปิดใช้ เคยเป็นโค้ดพร้อมที่ยังไม่ deploy เอกสารรุ่นก่อนหน้าที่เขียนแบบนั้นเป็นประวัติ ณ ตอนนั้น

## อัปเดต 15 พฤศจิกายน 2569 (หลังติดตั้งบน EC2)

- **บริการ semantic รันบน EC2 แล้ว** (`tamsoodbase-semantic`, 640 MiB, เครือข่ายภายใน `tamsoodbase-rag-private`, IP ตรึง 10.253.77.2, ไม่เปิดพอร์ตภายนอก) `tamsoodbase-rag` เดิมถูกหยุดไว้ (ไม่ลบ)
- **ทางเข้า:** `POST /semantic-search` บน gateway เดิม (`deploy/private_gateway.py`) ใช้ Basic Auth เดียวกับ API เดิม gateway เติม Bearer token ของบริการเอง token ไม่ไปถึง Vercel/เบราว์เซอร์ ตรวจบน EC2 แล้ว: 200 พร้อม corpus_version ตรง, ไม่มี auth → 401, body ผิด → 400, POST path อื่น → 405, `/healthz` เดิม 200
- **ฝั่ง Vercel (`ask.js`):** เมื่อไม่ได้ตั้ง `TAMSOOD_SEMANTIC_URL` และเปิด `TAMSOOD_SEMANTIC_ENABLED=true` จะใช้ `TAMSOOD_BACKEND_ORIGIN` + `TAMSOOD_BACKEND_AUTH` เดิมเรียก `/semantic-search` ไม่ต้องมี secret ใหม่
- **ข้อความยินยอม** ในหน้า `/ask.html` แจ้งแล้วว่าคำถามล่าสุดถูกส่งผ่านอุโมงค์ Cloudflare ไปบริการค้นของโครงการ ซึ่งไม่เก็บคำถาม
- **ย้อนกลับ:** ตั้ง flag เป็นอย่างอื่น (ไม่ต้อง deploy) | gateway: คืนไฟล์จาก `/home/ubuntu/tamsoodbase/backup-gateway-20261115T083220/` แล้ว `docker restart tamsoodbase-https-gateway` | บริการ: `docker stop tamsoodbase-semantic; docker start tamsoodbase-rag`
- ข้อควรระวัง: แรมเครื่องเหลือว่างราว 350 MB (ใช้ร่วมกับ ginder)

## เส้นทาง

`Browser → Vercel api/rag/ask.js → (flag) semantic service: FastEmbed + Qdrant → candidates (id, kind, score) → Gemini planner เลือก note_ids/queries → runQuery เดิมคำนวณตัวเลข → Gemini เรียบเรียง → ตรวจตัวเลข/หน่วย/ป้ายชื่อ → ตาราง + แหล่งอ้างอิงเดิม`

- Corpus = 10 บันทึกอธิบาย + 11 สรุปชุดข้อมูล จาก `knowledge-pack.json` ที่เจ้าของอนุมัติเท่านั้น (`scripts/build_semantic_corpus.py` → `docs/rag/semantic-corpus.json`, version = SHA-256 ของ chunks) **ไม่ฝังตารางตัวเลข** ตัวเลขทั้งหมดยังมาจาก `runQuery`
- Embedding: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (FastEmbed 0.7.3), 384 มิติ, cosine, Qdrant in-memory สร้างตอนเริ่มบริการ ชื่อ collection = `semantic_<corpus_version>`
- คะแนน = cosine + 0.5 × TF-IDF ของ bigram ตัวอักษร (hybrid; น้ำหนักตายตัว ไม่จูน) ข้อความที่ฝังมี `search_hint` (คำพ้อง/สำนวนพูด เขียนจากเนื้อหาชิ้นนั้น ใช้ค้นเท่านั้น ไม่แสดงผู้ใช้)
- top-k = 5 ส่งให้ planner พร้อม noise cut 0.4 (ไม่ใช่ข้ออ้างว่าเกี่ยวข้อง) planner ต้องเลือกเอง ระบบ **ไม่แนบ hit อัตโนมัติ**
- ผลวินิจฉัยใน response: `retrieval: {mode, corpus_version, evidence_ids, candidates, fallback_reason?}` โดย mode = `semantic` | `hybrid` | `structured` | `structured-fallback` (ไม่ส่ง field นี้เมื่อปิด flag)

## Fallback

หมดเวลา 2.5 วินาที, HTTP error, บริการล่ม, response ใหญ่/ผิดรูป, id ที่ไม่รู้จัก, corpus_version ไม่ตรง, ไม่มี hit เกิน 0.4 → ไม่ส่ง candidates ให้ planner ทำงานตามเส้นทาง structured เดิมและตอบ `structured-fallback` พร้อมเหตุผล Gemini ล่มยังได้ผลเหมือนเดิม (ไม่ถูกบดบัง) ผู้ใช้ไม่ยินยอมส่งข้อมูล → handler ตอบ 403 ก่อนถึงขั้นค้น

## เปิด/ปิด (ยังไม่ได้ทำใน production)

ตั้งใน Vercel (ค่าลับห้ามใส่ใน repo/frontend): `TAMSOOD_SEMANTIC_ENABLED=true`, `TAMSOOD_SEMANTIC_URL=https://…` (https เท่านั้น ยกเว้น loopback), `TAMSOOD_SEMANTIC_TOKEN` (≥32 ตัวอักษร) ย้อนกลับ = ลบ/ตั้ง `TAMSOOD_SEMANTIC_ENABLED` เป็นอย่างอื่น ไม่ต้อง deploy โค้ดใหม่

บริการ: `deploy/Dockerfile.semantic` (พอร์ต 8768, user 10001, ต้องส่ง `SEMANTIC_API_TOKEN` ตอนรัน, ไม่ดาวน์โหลดโมเดลตอนรัน) ต้องมี TLS/reverse proxy และไม่เปิดพอร์ตให้ browser ก่อนเปิด flag ต้องอัปเดตข้อความยินยอมให้ตรงเส้นทางข้อมูลจริง (คำถามถูกส่งไปบริการของระบบเอง)

## คำสั่งทำซ้ำ

```powershell
python scripts/build_semantic_corpus.py
python -m venv build/rag-verified-venv; build/rag-verified-venv/Scripts/python.exe -m pip install -r requirements-rag.txt
build/rag-verified-venv/Scripts/python.exe -X utf8 scripts/evaluate_semantic.py --output evidence/semantic-retrieval-eval-2026-11-15.json
node tests/rag-semantic-contract.cjs
node tests/rag-semantic-live-local.cjs build/rag-verified-venv/Scripts/python.exe evidence/semantic-pipeline-local-2026-11-15.json
python -X utf8 -m unittest tests.test_semantic_corpus
$env:SEMANTIC_API_TOKEN='<32+ chars>'; build/rag-verified-venv/Scripts/python.exe scripts/semantic_service.py --port 8768   # ตรวจ: GET /readyz
```

## ผลที่วัดได้ (evidence/semantic-retrieval-eval-2026-11-15.json)

ชุด held-out ใหม่ 14 คำถามเชิงสำนวน + 9 คำถามกวนใจ (เขียนก่อนรันรอบ hybrid ไม่ใช้จูน; relevant IDs กำหนดล่วงหน้า) corpus `f590197f715ddb17`

| วิธี | Recall@1 | Recall@3 | Recall@5 |
|---|---|---|---|
| keyword (bigram TF-IDF) | 0.786 | 0.857 | 0.929 |
| semantic (vector อย่างเดียว) | 0.571 | 0.929 | 1.000 |
| hybrid (ที่ใช้) | 0.786 | 0.929 | 0.929 |

ข้อสังเกตตามจริง: บน corpus เล็ก (21 ชิ้น) ตัวค้นคำธรรมดาแข็งมาก semantic ไม่ได้ชนะชัดเจน hybrid ดีเท่าหรือดีกว่าที่ top-3 รอบแรก (ก่อนเพิ่ม hint, held-out 14 ข้อ) semantic ล้วน Recall@3 = 0.714 เทียบ keyword 0.643 — เก็บไว้ที่ `evidence/semantic-retrieval-eval-round1-no-hints-2026-11-15.json` ชุดนั้นถูกดูผลแล้วจึงไม่ใช่ชุดสะอาดอีกต่อไป
คะแนนความคล้าย **แยกคำถามที่ไม่มีข้อมูล (ปีอนาคต หน่วยผิด บริษัทที่ไม่มี) ออกไม่ได้**: ไม่มี threshold ที่ให้ Recall สูงและไม่ดึงหลักฐานผิดพร้อมกัน (ดู threshold_sweep_dev) จึงออกแบบให้ planner กรอง และตัวเลขไม่พึ่ง vector เลย
Latency ในโปรเซส (ค้น 5 อันดับ) median 7.2 ms / p95 9.1 ms (n=69); ผ่าน HTTP loopback บริการจริง median 27.6 ms / p95 35.7 ms (n=23, timeout 0) — ไม่ใช่ latency บน EC2/Vercel จริง

## ทดสอบ pipeline (Gemini เป็น mock)

- `tests/rag-semantic-contract.cjs`: ปิด flag ไม่เปลี่ยนรูปแบบคำตอบ; ตาราง/ข้อมูลที่ส่งให้โมเดลเหมือนเดิมเมื่อเปิด flag; ตัวตรวจตัวเลขยังตีกลับตัวเลขที่ไม่มีในข้อมูล; fallback 4 แบบ + timeout + token/URL ไม่ปลอดภัย + id ปลอม + Gemini ล่ม + คำสั่งแฝงในประวัติ
- `tests/rag-semantic-live-local.cjs`: บริการ Python จริง + ask.js จริง + Gemini mock ที่แนบ **ทุก** โน้ตที่เสนอ (กรณีแย่สุดของการแนบเกิน) ผล: โน้ตที่เกี่ยวข้องถูกแนบ 7/9 คำถามที่มีโน้ตเป็นคำตอบ; คำถามกวนใจ 3/9 ถูกแนบโน้ตนอกรายการที่ยอมรับ ผลนี้ **ไม่ใช่พฤติกรรมของ planner Gemini จริง** (ยังไม่ได้วัด) เป็นเหตุผลที่ห้ามแนบ hit อัตโนมัติ และต้องวัดซ้ำด้วย Gemini จริงก่อนเปิด flag

## ยังไม่ได้ทำ

deploy บริการ semantic, ตั้งค่า flag บน Vercel, วัดคำตอบจริง/latency Gemini ก่อน–หลังบน production, ทดสอบ browser→production, แก้ข้อความยินยอมให้ตรงเส้นทางเมื่อเปิดใช้

## ผลตรวจจริงกับ Gemini (15 พฤศจิกายน 2569)

- ชุดเดียวกัน 29 ข้อบน preview (เปิด) เทียบ production เดิม (ปิด): เชิงสำนวน 14 ข้อแสดงต้นทางที่เกี่ยวข้อง 13/14 ทั้งสองฝั่ง ตัวเลข 6 ข้อถูกจากข้อมูลทั้งสองฝั่ง กวนใจ 9 ข้อไม่แต่งตัวเลขทั้งสองฝั่ง (evidence/semantic-preview-live-2026-11-15.json)
- หลังเปิดบน production ถามชุดใหม่ (docs/rag/semantic-eval-questions-v3-live.json กำหนดคำตอบก่อนถาม): เชิงสำนวน 12 ข้อแสดงต้นทางที่เกี่ยวข้อง 11/12, กวนใจ 6 ข้อไม่มีต้นทางนอกรายการที่ยอมรับ, ตัวเลข 6 ข้อตรงค่าเดิม (evidence/semantic-production-live-2026-11-15.json)
- สรุปตามจริง: ทำงานครบเส้นทางและไม่ทำให้ตัวเลข/ต้นทางเสีย แต่ยังไม่พบข้อดีด้านความแม่นยำเหนือ planner เดิม; มัธยฐานเวลาตอบรอบหลังเปิดราว 4.8 วินาที เทียบราว 2.3 วินาทีก่อนเปิด (รันครั้งเดียว ยังไม่แยกสาเหตุ: อุโมงค์/swap บน EC2/ความผันผวนของ Gemini)
- รายการ `project_scope` และ `acceptance` ไม่มีลิงก์ต้นทางหรือชุดข้อมูลให้แสดงการ์ด จึงไม่ใช่ข้อบกพร่องของการค้น