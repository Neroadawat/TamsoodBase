# คู่มือส่งต่อโปรเจกต์ TamsoodBase ให้ Codex

เอกสารนี้เป็นจุดเริ่มต้นให้ Codex ของสมาชิกทีมเข้าใจเป้าหมาย โครงสร้าง ข้อเท็จจริง และข้อจำกัดของโปรเจกต์ก่อนลงมือทำงาน ใช้คู่กับ repository ปัจจุบันและคำสั่งล่าสุดของผู้ใช้ ไม่ใช่หลักฐานอนุมัติหรือข้อมูลแทน source files

อัปเดตจากสถานะใน workspace ณ 9 พฤศจิกายน 2569

### ผลรับช่วงที่ใหม่กว่าตารางสถานะเดิม

เครื่องสมาชิกกู้ DMF/NSO/Corporate และเตรียม MySQL/Neo4j lab กับ RAG lineage ได้แล้ว Corporate มี 101 รายการ (97 ACCEPTED_REFERENCE / 4 HOLD_CONTEXT) ตรวจ MySQL เทียบ SQLite ครบทุกช่อง พร้อม constraint/rollback ผ่าน; ยังเป็นข้อมูลอ้างอิงภายใน สิทธิแจกจ่าย NOT_CLEARED และไม่ใช่ normalized LCI ส่วน EPPO และ DOM ต้นฉบับ Table 4/article-visible ยังขาด

ตรวจข้อมูลจริงผ่าน HTTP 144 ครั้ง ครอบคลุมค้น/กรอง/ส่งออก/ที่มา ดู `evidence/handoff-corporate-mysql-2026-11-09.json` และ `evidence/handoff-data-http-2026-11-09.json` ผลเป็นของเครื่องผู้ส่ง ไม่ใช่ผล replay ในเครื่องผู้รับหรือ production เริ่มรับช่วงจาก [รายการและคำสั่งปัจจุบัน](docs/TEAMMATE_NEXT_STEPS_TH.md) และท้าย `PROJECT_STATE.md`; รายงานวันที่ 8 พฤศจิกายนเป็นประวัติของแต่ละรอบ

แก้คอขวด export/metadata ของ Explorer โดย API/CSV ครบ34,899แถวตรงเดิม;ทดสอบHTTP localดีขึ้นแต่ยังไม่ใช่production capacity สร้างPDFจากSRS0.7.1เดิมใหม่27หน้าตรงsourcehash รอทีมตรวจและไม่ได้rebuildสไลด์ ผลค้นprimary sourcesเพิ่มเติมยังไม่ปิดallocationหรือCH₄คู่ยอดผลิตจริง ดู `docs/scientific-source-check-2026-11-08.md`

งานรับช่วงรอบนี้เตรียมส่งผ่าน branch `codex/teammate-runtime-handoff-2026-11-09` จากฐาน `67db1ad` ให้ตรวจ commit/remote จริงด้วย Git ก่อนรับงาน ไม่ใช้ข้อความว่า “ยังไม่ commit/push” ในประวัติรอบก่อนแทนสถานะปัจจุบัน ZIP เป็นทางเลือกสำหรับฐานเดิมและไม่รวม runtime/raw/secrets; รอบนี้ไม่ deploy หรือเปลี่ยน production

## 1. โปรเจกต์คืออะไร

**TamsoodBase** เป็นโปรเจกต์ CN230 × MTEC สำหรับจัดเก็บ ค้นหา และตรวจสอบย้อนกลับข้อมูลด้าน Petroleum, Natural Gas & Fuels ของไทย เป้าหมายคือทำให้ผู้ใช้เห็นค่าต้นฉบับ หน่วย ช่วงเวลา ขอบเขต ที่มา สิทธิ และสถานะการตรวจ โดยไม่รวมข้อมูลต่างชนิดหรือต่างขอบเขตเป็นค่าเดียวโดยไม่มีหลักฐาน

โปรเจกต์มีทั้งเว็บ ฐานข้อมูลเชิงสัมพันธ์ pipeline สำหรับข้อมูลหลายแหล่ง งานศึกษา LCI และเอกสารส่งรายวิชา การมีข้อมูลหรือแผนภาพหลายช่วงชีวิตไม่ได้แปลว่ามี full lifecycle LCI ที่เชื่อมครบแล้ว

## 2. อ่านเอกสารตามลำดับ

1. `AGENTS.md` — กติกาการทำงานของ repository
2. `PROJECT_BRIEF.md` — เป้าหมายและกฎโดเมนแบบย่อ
3. `PROJECT_STATE.md` — บันทึกสถานะตามวันที่ ให้อ่านรายการวันที่ล่าสุดและตรวจเอกสารต้นทางประกอบ
4. `README.md` — วิธีเริ่มใช้งานและข้อจำกัดการ clone
5. `docs/CURRENT_ARCHITECTURE.md` — สถาปัตยกรรมและสถานะที่ยืนยันได้
6. `docs/team-data-policy.md` และ `docs/source-contract.md` — กฎรับ/เก็บ/เผยแพร่ข้อมูล
7. `docs/dataset-model-index.md` — ดัชนีข้อมูลและโมเดล
8. `docs/tasks.md`, `docs/next-work-plan.md`, `docs/final-gap-plan.md` — งานค้างและลำดับต่อไป
9. ก่อนแก้ schema, LCI หรือ SRS ให้อ่านเอกสารเฉพาะทางที่เชื่อมจากไฟล์ข้างต้น และตรวจ DDL, source snapshot/manifest, code และ evidence ต้นทางจริง

เอกสารเก่าบางไฟล์มีสถานะก่อนหน้าและอาจขัดกับ snapshot ล่าสุด ให้ยึดคำสั่งผู้ใช้ล่าสุดและหลักฐานลงวันที่ใหม่กว่า อย่าคัดตัวเลขหรือสถานะจาก README เก่ามาใช้โดยไม่ตรวจ

## 3. สถานะข้อมูลและความหมาย

ตัวเลขด้านล่างเป็น snapshot ที่บันทึกไว้ ไม่ใช่จำนวนเป้าหมายถาวร ให้เปิด evidence ที่ระบุเพื่อยืนยันเมื่อใช้จริง:

| ชุดข้อมูล | สถานะที่บันทึกไว้ | ข้อจำกัดสำคัญ |
|---|---|---|
| DMF | 34,905 raw rows; 34,899 parse candidates; 6 rejected; 34,671 deduplicated pending | ฐานเวลา/ความหมายหน่วยบางส่วนยังไม่ยืนยัน; pending ไม่ใช่ accepted LCI |
| Corporate: Thai Oil/SPRC | 101 source observations; 97 `ACCEPTED_REFERENCE`; 4 `HOLD_CONTEXT` | เป็นสถานะอ้างอิงภายใน ไม่ใช่ normalized flows; สิทธิแจกจ่ายยังต้องตรวจ |
| NSO | 273 observations; cross-source comparison 169: 141 exact, 24 display-rounding compatible, 4 divergence; 104 ยังไม่เทียบ | ห้ามสรุปว่า 273 ค่าได้รับการตรวจข้ามแหล่งครบ |
| EPPO/DOEB | 5,934 staged observations แยก company intake กับ national output | ห้ามเอา BBL/DAY ของบริษัทไปหารกับ output ระดับประเทศเพื่อสร้าง yield; ปี 2026 เป็นข้อมูลบางช่วง |
| FAME/H-FAME | 16 source-reported exchanges จาก Table 4 ของงาน Permpool et al. (2020), basis การใช้เชื้อเพลิง 1,000 MJ | ปีตีพิมพ์ไม่ใช่ปีวัด; ไม่ใช่ full lifecycle inventory; BHD 8 รายการอยู่คนละบริบท |
| งานเอทานอลไทย | มีกรณีศึกษา/การตรวจหลักฐานเพิ่ม เช่น E10 vehicle, wastewater และ capture | เป็นหลักฐานคนละขอบเขตและคนละชุด; ยังไม่มีข้อมูลพอประกาศ total หรือ full lifecycle LCI |

หลักฐานและรายละเอียดล่าสุดอยู่ใน `PROJECT_STATE.md`, `docs/submission/status-and-limitations.md`, `docs/ethanol-whole-cycle-reference.md`, `docs/ethanol-tsm-wastewater.md` และ evidence ที่เอกสารเหล่านั้นอ้าง

## 4. กฎสำคัญของ LCI และหลักฐาน

- `ACCEPTED_REFERENCE` ไม่ได้แปลว่า normalized product LCI, ผ่านการรับรองจากผู้สอน หรือมีสิทธิแจกจ่ายต่อ
- แยกสถิติระดับองค์กร สถิติระดับประเทศ production statistics และ product inventory ออกจากกัน
- เก็บ raw/source-reported values, หน่วย, source ID, snapshot/hash, locator, boundary, basis, rights และ review status ให้ตรวจย้อนกลับได้
- ปีเผยแพร่ ปีรายงาน และปีวัดเป็นคนละค่า; ถ้าแหล่งไม่ระบุ ให้คงไม่ระบุ ไม่ใช้ปีตีพิมพ์แทน
- ไม่เดา allocation, time basis, mass conversion, provider link, unit conversion หรือ upstream/downstream connection
- อย่ารวม totals กับ components หรือ inventory คนละ process/basis; อย่านับ allocation, transport, combustion หรือ waste burden ซ้ำ
- ค่าที่ขาดยังเป็น null/unknown/hold ตามสัญญาข้อมูล ไม่แทนด้วยศูนย์
- FAME/H-FAME Table 4 เป็น foreground conversion inventory ไม่ได้พิสูจน์ว่ามีวัตถุดิบ ขนส่ง การใช้ และการจัดการของเสียเชื่อมครบ
- งานเอทานอลเป็นกรณีเพิ่มเติมที่ต้องคงแยกจาก FAME/B100 จนกว่าจะมีหลักฐานเชื่อมฐานและ scope ที่ตรงกัน
- อย่าเขียนว่าอนุมัติ ทดสอบ ประชุม ส่งงาน หรือสมาชิกทำส่วนใดแล้ว หากไม่มีหลักฐานจริง

## 5. สถาปัตยกรรมและโมเดล

- Frontend: `web/`; build/packaging และ configuration สำหรับ Vercel อยู่ใน repository
- API/proxy และงาน backend: ดู `api/`, `src/` และ `deploy/`; credentials/runtime secrets ต้องอยู่ใน environment ส่วนตัวเท่านั้น
- มี MySQL schemas แยกตาม semantics เช่น `tamsood_research`, `tamsood_reusable`, `tamsood_supplemental`, `tamsood_eppo`; ตรวจไฟล์ใน `sql/mysql/` ก่อนอ้าง schema ปัจจุบัน
- SQLite/JSON/build artifacts บางส่วนเป็น local review หรือ reproducibility artifacts ไม่ได้หมายความว่าข้อมูลเหล่านั้นอยู่ใน MySQL production
- กราฟ LCI ยังเป็น projection/lab สำหรับ subset ที่ตรวจแล้ว ไม่ใช่ graph production หรือ source of truth แทน relational DB
- โมเดล activity/version/release ใหม่และ Flow/Unit candidate เป็น candidate/local review แยกจาก production migration จนกว่าจะมีหลักฐาน migration จริง

### ขอบเขต Neo4j/RDB → Graph ที่ตรวจได้

การทดลองแปลง foreground FAME/H-FAME 16 exchanges เป็นกราฟ Neo4j Community 5.26.32 ใน isolated lab ได้ 39 nodes และ 68 relationships; Cypher 4 query ตรงกับ SQL; payload 16 แถวอ่านกลับตรงและ constraint ปฏิเสธ ID ซ้ำ การทดลองนี้ลบ container หลังจบ ไม่ได้เปลี่ยน production และไม่มี performance claim ดู `docs/neo4j-engine-experiment.md` และ `evidence/neo4j-inventory-audit.json`

Flow/Unit candidate มี `source`, `unit`, `process`, `flow`, `exchange`; ตรวจ 16-row roundtrip, typed joins และ negative checks แล้ว แต่ `production_migrated=false` และยังไม่ใช่ global flow ontology ดู `scripts/build_inventory_candidate.py` และ `evidence/inventory-candidate.json`

## 6. โครงสร้าง repository ที่ใช้บ่อย

| Path | ใช้ทำอะไร |
|---|---|
| `src/`, `scripts/` | pipeline, API/service logic, builders, audits และ utilities |
| `sql/mysql/`, `sql/` | schemas, queries และแบบจำลองฐานข้อมูล |
| `web/`, `api/` | frontend และ HTTP/API routes |
| `docs/` | design, policy, research reviews, SRS และ operating guides |
| `evidence/` | ผล audit/replay/verification ที่ควรอ่านพร้อม scope และ timestamp |
| `tests/` | automated checks; อ่าน README/คำสั่งเฉพาะก่อนรัน |
| `data/raw/`, `build/`, `.local/`, Docker volumes | แหล่งข้อมูลจริง, build/local state, secrets หรือ runtime data; ปกติไม่อยู่ใน Git |

## 7. การ clone และข้อจำกัดการตรวจ

การ clone repository จะไม่ได้ `data/raw/`, `build/`, `.local/` หรือ MySQL Docker volumes ตาม `README.md` และ `.gitignore` ดังนั้นบาง replay/integration checks ต้องมี snapshot ที่ได้มาอย่างถูกต้องก่อน หลักฐานใน `evidence/` เป็นหลักฐานของรอบที่บันทึกไว้ ไม่ได้พิสูจน์ว่าผู้ clone รันซ้ำแล้ว

ก่อนรันงาน:

1. ตรวจ `git status` และอย่าทับงานค้างของผู้ใช้
2. อ่านคำสั่งเฉพาะใน README/เอกสารงานก่อนติดตั้งหรือดึงข้อมูล
3. ตรวจ prerequisites และไฟล์ต้นทางที่ต้องมี; ห้ามสร้างข้อมูลสมมติเพื่อให้ pipeline ผ่าน
4. รันเฉพาะการตรวจที่ตรงกับการเปลี่ยนแปลงและผู้ใช้ร้องขอ
5. แยก “เคยผ่านใน evidence” จาก “รันผ่านในเครื่องปัจจุบัน” ให้ชัด

## 8. วิธีทำงานที่คาดหวังจาก Codex

- ตอบผู้ใช้เป็นภาษาไทย อ่านง่าย และทำงานต่อจากสถานะล่าสุด
- ตรวจ `AGENTS.md`, Git status และเอกสารที่เกี่ยวข้องก่อนแก้ไฟล์
- อ้างต้นฉบับและหลักฐานจริง; แยกข้อเท็จจริง สมมติฐาน และช่องว่าง
- แก้ให้ขอบเขตแคบที่สุดและเก็บ provenance/status/rights ตามเดิม
- อย่าเผยแพร่ raw data, keys, tokens, connection strings, environment files หรือข้อมูลที่สิทธิไม่ชัด
- อย่าทำ deploy, เปลี่ยน production DB, ซื้อข้อมูล, ติดต่อบุคคล/หน่วยงาน หรือรับรองงานแทนสมาชิก หากผู้ใช้ไม่ได้สั่งชัดเจน
- เมื่อแก้สถานะโครงการ ให้เพิ่มบันทึกสั้น ๆ ใน `PROJECT_STATE.md` พร้อมวันที่ หลักฐาน และข้อค้าง
- รายงานว่าทำอะไร ตรวจอะไร และมีข้อจำกัดอะไร โดยไม่กล่าวอ้างผลตรวจที่ไม่ได้รัน

## 9. จุดเริ่มงานต่อ

ให้ดูรายการวันที่ล่าสุดใน `PROJECT_STATE.md` และลำดับปัจจุบันใน `docs/next-work-plan.md` / `docs/final-gap-plan.md` ก่อนเลือกงาน อย่าถือว่าโครงการเสร็จเพียงเพราะมีเว็บหรือแผนภาพ งาน LCI หลักยังต้องปิด compatibility ของ process/basis, allocation, provider/background data, transport/use/treatment evidence, rights และ human review ตาม scope ที่ประกาศไว้

สำหรับงานรายวิชา เช่น W13 A4 ให้ยึดข้อกำหนดจากโจทย์ของอาจารย์ แต่แยกจากคำขอของผู้ใช้ และใช้ Functional Requirements, relational schema และ SQL ของรายงานทีมฉบับล่าสุด ไม่เอา candidate model มาอ้างว่าเป็น production schema
