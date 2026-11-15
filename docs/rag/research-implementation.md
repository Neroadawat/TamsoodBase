# Research notes: improving statistical answers in TamsoodBase RAG

วันที่ทบทวนหลักการวิจัย: 8 พฤศจิกายน 2569 · สถานะ implementation ตรวจซ้ำ: 10 พฤศจิกายน 2569

## งานที่อ่านและข้อค้นพบที่นำมาใช้

1. **Yu, Jian & Chen, “TableRAG: A Retrieval Augmented Generation Framework for Heterogeneous Document Reasoning,” EMNLP 2025.** ผู้เขียนชี้ว่าการ flatten ตารางและตัดเป็น chunks อาจทำให้ความสัมพันธ์ระหว่างแถว/คอลัมน์และภาพรวมตารางเสียหาย งานเสนอ workflow ที่แยก text retrieval, schema-aware table retrieval, SQL execution และการประกอบคำตอบหลายขั้น [บทความ ACL Anthology](https://aclanthology.org/2025.emnlp-main.710.pdf).
2. **Strich et al., “T²-RAGBench: Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation,” accepted EACL 2026.** ชุดทดสอบแยกความท้าทายการหา context ที่ถูกต้องออกจากการ reasoning ตัวเลข และรายงานว่า Hybrid BM25 ซึ่งผสม dense กับ sparse retrieval เป็นวิธีที่ทำได้ดีที่สุดในการประเมินของงานนั้น; benchmark มี 23,088 QA/context triples [บทความ arXiv](https://arxiv.org/abs/2506.12071).
3. **Herzig et al., “Open Domain Question Answering over Tables via Dense Retrieval,” NAACL 2021.** งานเสนอการฝึก retriever ให้รับรู้บริบทแบบตารางและรายงาน retrieval/QA ดีขึ้นเมื่อเทียบ baseline ของงานนั้น [หน้า Google Research พร้อม abstract/citation](https://research.google/pubs/open-domain-question-answering-over-tables-via-dense-retrieval/).

ตัวเลขผลทดลองในบทความเป็นผลของ corpus/benchmark/วิธีทดลองของผู้เขียน ไม่ใช่ผลที่รับประกันว่าจะเกิดกับ TamsoodBase.

## การประยุกต์ในโครงการ

| หลักการจากงาน | การนำมาใช้ | ข้อจำกัดปัจจุบัน |
|---|---|---|
| Dense + sparse retrieval ก่อนตอบ | รวม multilingual FastEmbed/Qdrant กับ BM25 และ Reciprocal Rank Fusion (RRF); token ภาษาไทยใช้ trigram และ sparse candidate ต้องผ่านทั้ง score และ query coverage | Local index ปัจจุบันใช้ 10 narrative cards กับ 10 fact records; หน้า Vercel Preview เป็นอีก corpus ที่จำกัด 6 narrative cards. BM25 threshold ยังต้อง recalibrate เมื่อขยาย corpus |
| รักษาโครงสร้างตัวเลขและที่มา | แยก fact records ออกจาก narrative: value, unit, period, basis, geography, status, qualifier, source locator, source URL และ flag การส่งออก | JSON ไม่ใช่ schema relational ที่ query ข้าม observation ได้; ยังต้อง reconcile full data model |
| ป้องกันการคำนวณจาก chunk/context ที่ปนกัน | สถิติเลือกคำตอบจาก metric/title/unit/aliases ของ fact ไม่เลือกตัวเลขจากบริบทคำอธิบาย; คำถาม “ค่าจริง” ต้องใช้ระเบียน null/status ที่ตรง metric แทนค่าการออกแบบ | การ matching ด้วย aliases/rules ไม่เข้าใจทุก paraphrase; ยังไม่มี coverage ของคำถามผู้ใช้จริง |
| แยก retrieval evaluation จาก answer evaluation | มี target evidence Recall@3/MRR@3, OOD abstention และ exact fact-ID selection ใน suite เดียว | Exact ID ไม่รับรองข้อความภาษาไทย entailment หรือความครบถ้วนของ citation ในทุกกรณี |
| SQL สำหรับ global aggregation (แนวทาง TableRAG) | บันทึกเป็นงานต่อไป ห้ามใช้ LLM คำนวณยอดรวมหรือสร้าง query อิสระตอนนี้ | ยังไม่ได้ต่อ SQL/allowlisted query catalog และยังไม่รองรับหลายตาราง/joins ใน RAG |

## ผลประเมินเฉพาะระบบนี้

มีผลประเมินสองชุดที่ห้ามปนกัน:

1. **ผลของ local narrative retrieval ที่รันใหม่ 10 พ.ย.** `scripts/evaluate_rag.py` ใช้ `docs/rag/evaluation-questions.json` จำนวน 24 ข้อกับ `docs/rag/public-evidence.json` ปัจจุบัน 10 cards. ผ่าน top-1 12/12 positive cases และปฏิเสธ 8/8 negative cases; อีก 4 ambiguous cases ไม่มีคะแนนผ่าน/ตก. หลักฐานและ hashes อยู่ใน `evidence/rag-current-retrieval-eval-2026-11-10.json`. นี่ประเมินการค้นการ์ด ไม่ได้ประเมินความถูกต้องของคำตอบที่ Gemini สร้าง.
2. **ผล hybrid/mixed-fact ย้อนหลัง 8 พ.ย.** `docs/rag/retrieval-eval.json` มี 18 cases (15 relevant, 3 negative); `evidence/rag-hybrid-eval.json` บันทึกการทดลอง 18 documents (8 narrative + 10 facts) ด้วย model `paraphrase-multilingual-MiniLM-L12-v2` และ Qdrant in-memory. ผลที่บันทึกจริงคือ:

- Dense-only: Recall@3 0.9333, MRR@3 0.7667, OOD abstention 1.0.
- Hybrid BM25+dense/RRF: Recall@3 1.0, MRR@3 0.8667, OOD abstention 1.0.
- สถิติ: exact fact ID 11/11; OOD query ไม่ได้ source ID ของ fact.
- คำขอเทียบ PDD avoidance `tCO₂e/year` กับ whole-life `kg CO₂e/L` ถูกปฏิเสธการคำนวณผลต่าง/ผลรวม เพราะหน่วย ช่วงเวลา และฐาน/ขอบเขตไม่ตรง.
- UI answer panel แสดงเฉพาะ fact ที่อ้างโดยคำตอบและ narrative parent; ใน evaluation ไม่มี uncited fact ปรากฏใน panel. รายการ retrieved อื่นไม่ถูกนำมาแสดงปะปนเป็นหลักฐานของคำตอบ.
- Regression ที่พบก่อนแก้: Thai overlapping bigrams ทำให้ orchid query ได้ BM25 score สูง; แก้เป็น trigram+coverage gating. คำถาม actual methane เคยเลือก null ของ ethanol output เพราะ qualifier แชร์คำ; แก้ให้ actual query จำกัดตาม metric/alias ที่ผู้ใช้ถามและไม่ยกหลาย metric มาปน.

**ข้อจำกัดของการเทียบรุ่น:** ผล hybrid ข้างต้นใช้ narrative corpus SHA-256 `5427ae467a78e1dcc122974fef7a8a178f45ade5a5f4def6fddb4b234fd6ee6e` ซึ่งต่างจาก current `public-evidence.json` SHA-256 `9b131dba2938161841cd3b51eb192c6d97f5f90e2ede3ac580c17dffc3ae0605`; จึงเป็นผลย้อนหลัง ไม่ใช่ผลของ corpus ปัจจุบัน. ผล 10 พ.ย. ใช้ corpus ปัจจุบันแต่ทดสอบเฉพาะ narrative retrieval. ทั้งสองชุดเป็น targeted regression จากคำถามที่ทีมเขียน ไม่ใช่ independent benchmark, user study, confidence interval หรือหลักฐานว่า RAG ตอบทุกคำถามได้ดีขึ้น. ยังไม่มี independent Thai reviewer และไม่มีการประเมินคำตอบ Gemini รอบนี้. FastEmbed เตือนเรื่อง pooling configuration; ควร pin และประเมิน embedding configuration พร้อม curated set ที่ใหญ่ขึ้นก่อนใช้เทียบผลรุ่นต่อรุ่น.

## การคุ้มครองข้อมูลและข้อห้ามด้านการคำนวณ

- Numeric fact answers deterministic และตอบจากระเบียนที่เก็บในเครื่อง; ไม่มี live Gemini/API call ในการประเมิน.
- Gemini ยังเป็น optional สำหรับ narrative cards ที่ตั้ง `external_llm_allowed: true`; คำถามและการ์ดที่เลือกจะถูกส่งออกเมื่อเปิดใช้ จึงต้องไม่ใช้ข้อมูลลับ/ส่วนบุคคล.
- ค่าปี 2009 ใน UNFCCC PDD ยังเป็น design/ex-ante values; current installed capacity ไม่ใช่ output จริง; null แปลว่าไม่พบใน reviewed corpus ไม่ได้แปลว่าไม่มีข้อมูลที่ใดเลย.
- RAG นี้ยังไม่ใช่เครื่องคำนวณ full lifecycle CO₂e และไม่อนุญาตให้รวมตัวเลขคนละ functional unit, boundary, year, site หรือ reporting period.
