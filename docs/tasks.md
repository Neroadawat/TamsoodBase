# Task board — TamsoodBase

สถานะนี้นับเป็นหน่วยงาน ไม่ใช่เปอร์เซ็นต์ความสมบูรณ์หรือประมาณเวลา แต่ละงานมีขนาดต่างกัน

ทั้งหมด 34 งาน: DONE 30 · IN_PROGRESS 1 · TODO 2 · WAITING 1

DONE หมายถึงผ่านเกณฑ์เฉพาะงานนั้น ไม่ได้หมายความว่า dataset ผ่าน MTEC แล้ว
WAITING คือรอข้อมูล/การยืนยัน/การมีส่วนร่วมของมนุษย์ ทำงานอิสระส่วนอื่นต่อได้

| ID | ลำดับ | สถานะ | งาน / เกณฑ์จบ | หลักฐาน | ขึ้นกับ |
|---|---|---|---|---|---|
| T01 | P0 | DONE | สรุป domain และข้อกำหนดตั้งต้น<br>มี requirement/business rules และแยกข้อไม่ยืนยัน | [docs/requirements.md](../docs/requirements.md) | — |
| T02 | P0 | DONE | เก็บต้นฉบับ DMF พร้อม hash<br>สาม package มี raw/metadata/manifest ที่ตรวจ hash ได้ | [src/acquire_dmf.py](../src/acquire_dmf.py) | — |
| T03 | P0 | DONE | สร้าง staging และ candidate/reject<br>row accounting 34905=34899+6 และรันซ้ำได้ | [src/process_dmf.py](../src/process_dmf.py) | T02 |
| T04 | P0 | DONE | ทบทวน duplicate และหน่วยเบื้องต้น<br>เก็บ exact/conflict และข้อจำกัดฐานเวลา | [docs/dmf-review-results.md](../docs/dmf-review-results.md) | T03 |
| T05 | P0 | DONE | โหลดข้อมูลเต็มเข้า MySQL<br>Decimal/raw checks และ constraints ผ่าน | [docs/mysql-full.md](../docs/mysql-full.md) | T03 |
| T06 | P1 | DONE | เพิ่มตัวอย่างรายงานสองบริษัท<br>48+53 observations พร้อม numerical/metadata roundtrip | [docs/sprc-review.md](../docs/sprc-review.md) | — |
| T07 | P1 | DONE | สร้างเว็บสำรวจและเปิดหลักฐาน<br>ค้น/กรอง/detail/รายงาน/issue ใช้งานได้ | [docs/explorer.md](../docs/explorer.md) | T03, T06 |
| T08 | P0 | DONE | ตรวจ tests และตัวอย่าง trace<br>tests32 และ source re-extraction samples5 | [evidence/report-trace-checks-2026-10-22.json](../evidence/report-trace-checks-2026-10-22.json) | T05, T06 |
| T09 | P0 | DONE | เตรียมชุดคำถาม domain พร้อมตัวอย่าง<br>พร้อมให้ทีมใช้ถามโดยยังไม่ได้ส่ง | [docs/domain-review-packet.md](../docs/domain-review-packet.md) | T06 |
| T10 | P0 | DONE | เขียนกฎ acceptance และ final gate ฉบับร่าง<br>แยก technical pass/eligibility/rights ชัด | [docs/acceptance-rules.md](../docs/acceptance-rules.md) | T01 |
| T11 | P0 | DONE | ทำ release audit และ manifest ของหลักฐาน<br>ตรวจ artifacts, hash, counts, gates และรายงานผล | [docs/release-readiness.md](../docs/release-readiness.md) | T08, T10 |
| T12 | P0 | DONE | ทบทวนข้อกำหนดการส่งจากเอกสารที่มีโดยไม่รอคำรับรอง<br>แยกรายการส่ง/วันส่งที่ทราบจากสิ่งที่ยังไม่มีประกาศ ไม่บล็อกการใช้ข้อมูล | [docs/submission-checklist.md](../docs/submission-checklist.md) | — |
| T13 | P0 | DONE | ตรวจสิทธิใช้รายงานและรูปแบบ evidence ที่ส่งได้<br>ตรวจหลักฐานต่อแหล่งและจัดทำ notice/วิธีส่ง evidence แล้ว; สิทธิแจกจ่ายรายงานยัง NOT_CLEARED ไม่อ้างว่าอนุญาต | [docs/source-use-notice.md](../docs/source-use-notice.md) | — |
| T14 | P0 | DONE | หาหลักฐานฐานเวลาย้อนหลัง DMF<br>ทบทวนหลักฐานแล้วคง unresolved time basis และ hold ตามเหตุผล; ไม่อ้างว่าฐานเวลาย้อนหลังยืนยันแล้ว | [evidence/dmf-time-basis-review-2026-10-23.json](../evidence/dmf-time-basis-review-2026-10-23.json) | T04 |
| T15 | P0 | DONE | กำหนดประเภทข้อมูลและเกณฑ์รับระดับทีม<br>มีนโยบายและผล ACCEPTED_REFERENCE/HOLD_CONTEXT ตาม use case จริง | [docs/team-data-policy.md](../docs/team-data-policy.md) | T09 |
| T16 | P0 | DONE | สร้างแบบจำลองเชิงสัมพันธ์สำหรับข้อมูลหลายแหล่ง<br>schema/ERD/dictionary/mapping พร้อม typed database และ roundtrip checks | [docs/reusable-model.md](../docs/reusable-model.md) | T06, T10, T15 |
| T17 | P0 | DONE | ตรวจตัวเลข subset ทุกค่าพร้อมขอบเขตการตรวจ<br>สกัดซ้ำ PDF ครบ101 และแยก automated review จาก human review | [build/reusable/manifest.json](../build/reusable/manifest.json) | T10, T16 |
| T18 | P1 | DONE | เติม process/reference-product basis เมื่อมีข้อมูลครบจริง<br>พบTable4ต่อ1000MJและสร้าง16source-reported inventoryของFAME/H-FAMEพร้อมSQL/metadata; measurementperiodยังnull ไม่อ้างfull acceptedLCI | [docs/product-inventory.md](../docs/product-inventory.md) | T16 |
| T19 | P1 | DONE | ทำ SQL use cases และ performance evidence ชุด final<br>SQL use cases และผล EXPLAIN ANALYZE 5รอบ พร้อม equality/hash ของผลลัพธ์ | [docs/sql-performance.md](../docs/sql-performance.md) | T16 |
| T20 | P0 | DONE | ตรวจ reproducibility ในสภาพแวดล้อมสะอาด<br>แพ็กเกจรัน client แบบ -I ในโฟลเดอร์ใหม่และ restore ลง MySQL ว่าง 2ครั้ง ตรวจ97ค่าและ101source records; ไม่อ้างทดสอบOSใหม่ | [evidence/reference-package-verification.json](../evidence/reference-package-verification.json) | T16, T19 |
| T21 | P1 | DONE | ทำแพ็กเกจอ้างอิงภายในพร้อม manifest และวิธีใช้<br>CSV/JSON/schema/example/hash ตรวจครบและสิทธิแนบไปกับชุด | [build/reusable/reference-data-local.zip](../build/reusable/reference-data-local.zip) | T11, T16 |
| T22 | P0 | WAITING | เก็บ contribution จริงและ version history ของทีม<br>สมาชิกระบุงานจริงและซ้อมอธิบาย ไม่มีการสร้างย้อนหลังเท็จ | [docs/](../docs/) | — |
| T23 | P1 | DONE | ทำ demo script รายงาน และชุดซ้อม defense<br>มี demo script และคำถามซ้อมรายบุคคล; การซ้อมจริงของมนุษย์ยังไม่ถูกอ้างว่าเสร็จ | [docs/demo-and-defense.md](../docs/demo-and-defense.md) | T16, T19 |
| T24 | P0 | TODO | ตรวจ final gate และ freeze รุ่นส่ง<br>ตรวจความพร้อมการใช้ข้อมูลและส่งงานตามข้อกำหนดที่มี ไม่ต้องรอคำอนุมัติ MTEC | [docs/acceptance-rules.md](../docs/acceptance-rules.md) | T12, T13, T14, T15, T17, T18, T20, T21, T22, T23 |
| T25 | P0 | DONE | แก้และตรวจ export/filter/pagination<br>CSV ว่าง schema ครบ; pagination97ไม่ซ้ำ/ตก; literal filters และ invalid inputs ตรวจแล้ว | [tests/test_reusable.py](../tests/test_reusable.py) | T16 |
| T26 | P1 | DONE | สร้าง quality/coverage scorecard จาก release จริง<br>ผูก hash และตรวจ context/scaling/identity/counts; ไม่คาดคะแนนแข่งขัน | [evidence/reference-scorecard.json](../evidence/reference-scorecard.json) | T16 |
| T27 | P1 | DONE | คัดและทดลองแหล่งข้อมูลทางการใหม่ที่เพิ่มความครอบคลุมจริง<br>NSO5 CSV273ค่าพร้อมhash/units/notes/SQLite/เว็บและtests; ยังเป็นnational staging ไม่รวม97reference | [docs/nso-source.md](../docs/nso-source.md) | T16 |
| T28 | P1 | DONE | ปรับ UX เว็บจาก reference ต่างประเทศและตรวจบนมือถือ<br>ปรับอ่าน/ค้น/เมนู/reset/empty state และตรวจ browser ขนาดปกติ/390px; ยังไม่อ้าง user study | [docs/ux-design.md](../docs/ux-design.md) | T07 |
| T29 | P1 | DONE | ตรวจยอดรวม NSO และเพิ่มการค้นปี/รายการ<br>18 additive checksพร้อมDecimal tolerance; testsตรวจจับcomponentเสีย; UIกรองดีเซล2024ได้2ค่าตรงต้นฉบับ | [docs/nso-source.md](../docs/nso-source.md) | T27 |
| T30 | P0 | IN_PROGRESS | เทียบNSOกับDEDE/DOEBและทบทวนrevision<br>เทียบทุกmetricที่มีขอบเขตตรงกันและเก็บcoverage/mismatch; รอบนี้7distinctค่า:DEDE1ต่าง,DOEB6ต่างค่าดิบแต่อยู่displayrounding; อีก266ยังไม่เทียบ | [evidence/nso-dede-comparison.json](../evidence/nso-dede-comparison.json) | T27 |
| T31 | P0 | DONE | รวม NSO และ inventory งานวิจัยเข้า MySQL แบบแยกชนิดและ snapshot<br>โหลดNSO273และinventory16เข้าMySQLจริง; numeric/payload/typed fields/process basisตรงครบ; FKและdirection constraintsปฏิเสธข้อมูลผิดตามคาด ไม่เปลี่ยนacceptance | [evidence/supplemental-mysql.json](../evidence/supplemental-mysql.json) | T18, T27 |
| T32 | P1 | DONE | ปรับหน้าเลือกชุดข้อมูลจาก EPPO reference<br>catalog4กลุ่มค้น/กรองระดับ/reset/empty state/navigationตรวจbrowserจริง desktopและmobile390px; EPPOcandidateแยกไม่อ้างimport | [docs/ux-design.md](../docs/ux-design.md) | T28 |
| T33 | P0 | DONE | ตรวจและนำเข้า EPPO refinery intake/product output ตามแผน<br>CSV2ชุด5934ค่ามีhash/locator/SQLite/MySQLroundtripครบ; API/UIค้นSPRC2024และหลักฐานตรวจจริง; ไม่สร้างyieldหรือเพิ่มacceptedLCI | [docs/eppo-source.md](../docs/eppo-source.md) | T31, T32 |
| T34 | P0 | TODO | ทำ model documentation และ release audit กลางทุกชุดข้อมูล<br>dictionary/mapping/status/unit/source vocabulary และ audit ครอบคลุมDMF/corporate/NSO/inventory/EPPO โดยรักษาsemanticsต่างกัน | [docs/shared-plan-comparison.md](../docs/shared-plan-comparison.md) | T33 |

## วิธีทำต่อในแต่ละรอบ

อ่าน tasks.json และผลตรวจจริง เลือก P0 ที่ยังทำได้ก่อน P1 ทำให้จบพร้อมหลักฐานแล้วอัปเดตสถานะและรัน scripts/task_board.py ไม่ทดสอบซ้ำโดยไม่มีการเปลี่ยนแปลงหรือข้อกังวลใหม่
อย่ากำหนดชื่อสมาชิกหรือ contribution แทนมนุษย์ อย่าส่งคำถาม/เอกสารออกไปเอง และอย่าประกาศว่าได้รับอนุมัติโดยไม่มีต้นฉบับคำตอบ

เปิดรอบปรับปรุงต่อทุกชั่วโมงในแชตนี้ รหัส tamsoodbase ตามแผน competition-improvement-plan.md; งาน local ต้องเปิดเครื่องและแอปไว้
แจ้งเฉพาะความคืบหน้าสำคัญ งานเสร็จ ปัญหา หรือสิ่งที่ต้องให้ผู้ใช้ตัดสินใจ หากไม่มีอะไรเปลี่ยนให้ไม่รายงานซ้ำ
