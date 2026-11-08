# ผลทำงานต่อทั้ง 6 ส่วน — 8 พฤศจิกายน 2569

**อัปเดตวิธีรับช่วง 9 พฤศจิกายน:** สถานะปัจจุบันและรายการค้างอยู่ [ที่นี่](TEAMMATE_NEXT_STEPS_TH.md) Corporate กู้และตรวจ 101 รายการแล้ว และ HTTP ข้อมูลจริง 144 checks ผ่าน ตารางผลด้านล่างเป็นประวัติรอบวันที่ 8 ไม่ใช่สถานะล่าสุด วิธีเตรียมเครื่องในเอกสารนี้ปรับตามตัวช่วยปัจจุบันแล้ว

## ผลในรอบวันที่ 8 พฤศจิกายน

| งาน | ทำแล้วและหลักฐาน | สิ่งที่ยังค้าง |
|---|---|---|
| 1 คำถามจากคนใช้ | เพิ่มแบบประเมินบนหน้าค้น ผูกคำถาม/การ์ด/รุ่นกับผลจริง เก็บเฉพาะในเครื่องและไม่อ้างตัวตน; ตรวจ UI ผ่าน IAB เห็นผลค้น ลิงก์รายการและแบบประเมิน | ยังไม่มีผลประเมินจริง ไม่แต่งคำถามหรือผลแทนสมาชิก; วิธีใช้ `docs/rag/member-validation.md` |
| 2 กู้ระบบข้อมูล | NSO 5 CSV ตรง hash เดิมครบ → 273 รายการ; FAME/H-FAME 16 รายการจาก API ผ่าน metadata+process contract; DMF ดาวน์โหลด snapshot ใหม่และ pipeline ผ่าน 34,905 raw/34,899 observations/6 rejects/34,671 pending | Corporate reference ยังขาดไฟล์; EPPO 2 URL ดาวน์โหลดไม่สำเร็จ จึงไม่สร้างข้อมูลแทน; DOM ต้นฉบับ Table 4 ยังไม่ได้กู้ |
| 3 เชื่อมข้อมูลจริง | Review SQLite 331 records อ่านกลับตรงทุก payload; MySQL 331 records+DMF 34,899 observations/34,905 raw payloads ตรง; Neo4j 58 article observations และ 97 card links ตรง SQL; HTTP ค้น→รายการ→graph ผ่าน | เป็นฐานทดลองเฉพาะเครื่อง ไม่ใช่การย้าย production หรือ provider links ของ full LCI |
| 4 เรียบเรียงด้วย Gemini | เพิ่ม guard ตัวเลข/อัตราส่วนหน่วย/เชื้อเพลิง/สาร/ช่วงทดสอบและ cited IDs; ใช้เฉพาะข้อความจากการ์ดที่อ้างจริง; กรณี connection error/429/ข้อมูลผิดคืนหลักฐานเดิม | ไม่พบ GEMINI_API_KEY ใน environment ที่ใช้ จึงยังไม่มี live call; guard ไม่พิสูจน์ความถูกต้องทางความหมายทุกประโยค |
| 5 ข้อมูล LCI | เปิดอ่าน PDD TSM ฉบับจริงทางเว็บได้แล้ว บันทึก version/locators/ความต่างของบริบทและแยก ex-ante กับแผน monitoring | ดาวน์โหลดตรงได้ non-PDF จึงไม่มี local PDF/hash; PDD ไม่ใช่ผลเดินระบบจริง มวล CH₄ คู่ยอดผลิตยังขาด จึงคง CO₂e/L เป็น null |
| 6 สถิติและซ้อมระบบ | ตรวจ NSO restored identities/contextครบ273 ทวนเลขเทียบเดิม169, totals18, percentages18; ทดลองเปิด/ค้น/ส่งออกข้อมูลจริงและขอบเขตผิดผ่าน | ยังเหลือ104รายการและ4divergences ไม่มี direct external comparisons ใหม่; สมาชิกต้องลองใช้และซ้อมอธิบายเอง |

## ขอบเขตฐานทดลอง

`build/handoff/current.json` ชี้ไป SQLite รุ่นตาม content hash มี foreground16 + upstream42 + NSO273 แยก layer และต้นทาง คง payload และ decimal strings เดิม เก็บ null และ HOLD ตามต้นฉบับ API หลักฐานของ RAG เปิดเฉพาะ 58 observations จากบทความที่ตรวจสิทธิ CC BY 4.0; NSO ที่ reuse scope ยังไม่ยืนยันถูกปฏิเสธจากเส้นทาง public evidence นี้

การผูกการ์ดกับแถวเป็น supporting source lineage สำหรับเปิดหลักฐาน ไม่ได้พิสูจน์ provider compatibility หรือสร้างผลรวม LCI กราฟยังเป็นสำเนาทดลอง ไม่แทน relational source of truth

MySQL ใช้ owner-marked container เครือข่าย none; Neo4j ใช้ owner-marked internal network เพราะ network none ทำให้การเริ่มระบบรอบนี้หยุดก่อนพร้อม ไม่มี published ports ไม่เปลี่ยน EC2/Vercel/Ginder/Caddy ฐานทดลองคงเปิดไว้ให้เดโมและตรวจต่อ ชื่ออยู่ `build/handoff/engines.json` การหยุด/ลบต้องตรวจ owner label ก่อนเสมอ MySQL review lab ใช้พื้นที่ชั่วคราวจึงควรสร้างซ้ำจากไฟล์ที่ตรวจแล้ว ไม่ใช้แทน backup production

FAME/H-FAME ที่กู้เป็นสำเนา API ที่ตรวจ metadata ตรง evidence เดิมและตรวจ process contract แล้ว ไม่ใช่การรัน extractor จาก DOM ต้นฉบับ รายงาน NSO สร้างใหม่จาก CSV bytes เดิมและ manifest การกู้ครั้งนี้ จึงมี report hash ใหม่ ไม่อ้างว่าเป็น report bytes เดิมทั้งหมด

## เปิดใช้งาน

หน้าเว็บข้อมูลเดิม: `http://127.0.0.1:8765/`

```powershell
python -X utf8 src/explorer.py
```

หน้าค้นพร้อมลิงก์ข้อมูลจริงและแบบประเมิน: `http://127.0.0.1:8767/`

```powershell
& build/rag-verified-venv/Scripts/python.exe -X utf8 scripts/rag_retrieve.py serve --lineage
```

หยุดบริการเก่าก่อนรันใหม่ และหยุด RAG ก่อนสร้างดัชนีหรือประเมินออฟไลน์เพราะ Qdrant Local เปิดดัชนีได้ทีละโปรเซส

## เตรียมซ้ำบนเครื่องใหม่

เตรียม Python/dependencies ตาม README รวม `pypdf` และเปิด Docker Desktop Linux engine ก่อน; RAG/index ใช้ environment แยกตาม `docs/rag/README.md` สำหรับข้อมูลและฐานทดลองใช้คำสั่ง:

```powershell
python -X utf8 scripts/prepare_handoff_runtime.py --restore-corporate --acquire-dmf-if-missing --verify-labs
python -X utf8 scripts/verify_restored_nso.py
```

ใช้ MySQL image `mysql:8.1` และ Neo4j `neo4j:5.26.32-community` หากมีข้อมูลและ images ครบ เพิ่ม `--offline` เพื่อไม่ดึงข้อมูลหรือ images ใหม่ DMF จะ acquire เฉพาะเมื่อไม่มี snapshot ในเครื่อง และได้รุ่น ณ เวลารัน ไม่รับประกัน bytes/จำนวนตรงรอบผู้ส่ง หากข้อมูลเปลี่ยนต้องตรวจ source/context ใหม่ Corporate/NSO รับเฉพาะ hash ที่บันทึกไว้ ส่วน FAME API ต้องตรง metadata และ process contract ที่กำหนด

ดู `requested_steps_passed` และผลแต่ละขั้น ไม่ใช้ค่านี้แทน `full_runtime_restored` ซึ่งยัง false ได้เพราะขาด EPPO/DOM คำสั่งนี้ตรวจ Corporate ใน owned MySQL lab เพิ่มแล้ว ไม่เปลี่ยน production

คำสั่งทดลองกู้ EPPO `python -X utf8 scripts/restore_eppo_snapshot.py` จะสร้าง report เฉพาะเมื่อ CSV ตรง hash เดิมและเก็บ evidence ใหม่แยกจากประวัติ รอบนี้ยังไม่สำเร็จ ไม่รันวนโดยไม่มีสัญญาณใหม่

หากไม่มี snapshot จริงหรือ API ใช้ไม่ได้ คำสั่งขั้นถัดไปที่ต้องพึ่งข้อมูลจะหยุดตามจริง ห้ามสร้างข้อมูลสมมติเพื่อข้าม preflight

## ตรวจซ้ำ

```powershell
python -X utf8 -m unittest discover -s tests -p test_rag_runtime.py -v
& build/rag-verified-venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -p test_rag_scope.py -v
python -X utf8 -m unittest discover -s tests -p test_frontend.py -v
python -X utf8 -m unittest discover -s tests -p test_eppo.py -v
```

ผลในรอบแรกวันที่ 8: runtime8, scope6, frontend13 ผ่าน; EPPO parser4 ผ่าน อีก1 integrationข้ามเพราะไม่มี snapshot ไม่ใช้เป็นผลผ่าน จำนวน tests ปัจจุบันอาจเพิ่มแล้ว ให้รายงานผลที่รันจริง เมื่อเปิดทั้งสองบริการแล้ว:

```powershell
python -X utf8 scripts/check_handoff_integration.py
python -X utf8 scripts/check_restored_explorer.py
python -X utf8 scripts/check_rag_local_http.py
python -X utf8 scripts/check_restored_data_end_to_end.py
```

ผล HTTP ในรอบแรก: source→graph 9 checks และ RAG19 checks ผ่าน Explorerตรวจ9เส้นทางได้ตามคาด โดย reference/EPPO ยัง503ในขณะนั้น ต่อมากู้ Corporate แล้ว reference ตอบ200 เหลือ EPPO unavailable; broad export400เพราะเกิน5000แถวยังคงเป็นพฤติกรรมที่กำหนด ผลปัจจุบันดู `evidence/handoff-data-http-2026-11-09.json` และผลที่รันใหม่ใน `build/handoff/end-to-end-data-verification.json`

หน้าค้นตรวจด้วย IAB จริง: กดตัวอย่าง Land seeding ค้นพบการ์ดแสดงข้อจำกัด หน่วยว่าง ลิงก์ source row และแบบประเมิน ไม่กดส่งผลแทนคน ไม่ได้อ้างตรวจ responsive ทุกขนาด

หลักฐานอยู่ใน `evidence/`: `handoff-runtime-2026-11-08.json`, `handoff-store-2026-11-08.json`, `handoff-engines-2026-11-08.json`, `handoff-dmf-mysql-2026-11-08.json`, `handoff-integration-2026-11-08.json`, `handoff-explorer-2026-11-08.json`, `nso-restored-review-2026-11-08.json`, `tsm-pdd-review-2026-11-08.json` และ `eppo-restoration-2026-11-08.json` บางไฟล์เป็นผลล่าสุดของตัวตรวจที่รันซ้ำ ให้ดู timestamp/scope ภายใน ไม่ถือว่าชื่อวันที่ยืนยันว่าเป็นผลรอบแรกเสมอ

## ขั้นต่อไปที่ต้องพึ่งข้อมูลภายนอก

- คำถาม/ผลประเมินจากสมาชิกจริงก่อนสรุปความแม่นยำต่อคนใช้
- คีย์ Gemini ตั้งฝั่งเครื่อง/เซิร์ฟเวอร์ก่อนทดสอบ live; ไม่ใส่คีย์ในแชต ไฟล์บริบท หรือ frontend
- EPPO และ DOM ต้นฉบับ Table 4/article-visible จริงหรือช่องทางดาวน์โหลดใหม่ที่ใช้ได้; Corporate กู้และตรวจแล้ว แต่ยังต้องเคลียร์สิทธิแจกจ่าย
- หลักฐานปี/หน่วย/การจัดกลุ่มสำหรับ NSO และข้อมูลเดินระบบจริงสำหรับ LCI ไม่ใช้หลักฐานซ้ำหรือประมาณการแทนข้อมูลที่ขาด
