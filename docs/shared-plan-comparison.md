# เทียบแผนในแชตที่แชร์กับงานจริง

ตรวจ 23 ตุลาคม 2569 จากบทสนทนา “วางแผนโปรเจ็กต์ Petroleum”:
https://chatgpt.com/share/6ad5c9a4-07e4-83ec-9fee-6f2e501a01eb

อ่านเนื้อหาคำตอบใน rendered browser ครบ แชตนี้เป็นคำแนะนำประกอบ ไม่ใช่ข้อกำหนดทางการเพิ่มจากผู้สอน ไม่ใช้ตัวอย่าง Diesel 125 Million Litres ปี2025 ที่แชตระบุว่าสมมติเป็นข้อมูลจริง

## ผลเทียบ

| แผนในแชต | งานจริงและหลักฐาน | ผล |
|---|---|---|
| เข้าใจ domain/requirements/business rules ก่อน model | docs/requirements.md, team-data-policy.md, source-registry.csv | ตรงหลักการ; requirements เดิมยังเน้น DMF ต้องอัปเดตให้ครอบคลุมชุดใหม่ |
| เริ่ม EPPO 3–5 sources โดยเฉพาะ refinery input/output และ gas | เริ่ม DMF, Thai Oil/SPRC, NSO และงานวิจัย; EPPO เพิ่งตรวจ catalog จริง evidence/eppo-catalog-review.json | ต่างเส้นทาง; ยังไม่มี EPPO values ในฐาน ต้องตรวจ CSV/XLSX ก่อนทำ extractor |
| Raw → staging → mapping → validation → DB | src/acquire_dmf.py, process_dmf.py, scripts/import_nso.py, build_product_inventory.py และ SQL | มีจริง; การ rebuild offline จาก snapshot รองรับแล้ว แต่บาง raw ได้ผ่าน browser/manual acquisition ไม่ใช่ automated download end-to-end ทุกแหล่ง |
| Canonical model PROCESS/FLOW/LCI_EXCHANGE/UNIT ฯลฯ | tamsood_research สำหรับ DMF, tamsood_reusable สำหรับองค์กร, tamsood_supplemental สำหรับ NSO/งานวิจัย | มี relational models แต่ยังไม่ใช่ common canonical catalog ครบทุกแหล่ง; inventory ใช้ process/exchange และ flow string, ไม่ใช่ global FLOW master |
| PK/FK/normalization/SQL/constraints | sql/mysql/*, docs/reusable-model.md, sql-performance.md, supplemental-mysql.md | มีใช้งานจริง; supplemental ยังใช้ unit string และ payload metadata จึงยังไม่ได้ normalize unit/location/source ร่วมกันทั้งหมด |
| Accepted ต้องผ่าน semantic/หน่วย/duplicate/ที่มา | corporate97 ACCEPTED_REFERENCE,4hold; NSO273 staged; inventory16 source-reported; DMFยังpending | ตรงเรื่องไม่เหมารวม แต่97ไม่เท่ากับ97accepted LCI exchanges; ต้องคงหลายสถานะชัดเจน |
| Numerical verification และ provenance | corporateสกัดซ้ำ101; NSO18additivechecks; cross-source7/273; hash/locatorรายแถว | มีหลักฐาน แต่ยังตรวจข้ามแหล่งไม่ครบและDEDEต่าง1ยอด; hashไม่ใช่การรับรองการวัดต้นทาง |
| MySQL/PostgreSQL + Docker | DockerMySQL ใช้จริง; supplementary289ค่าอ่านกลับและFK/CHECKผ่าน evidence/supplemental-mysql.json | ตรงเป้าหมาย; ใช้ Docker CLI แทน Compose เป็นทางเลือก implementation ไม่ใช่ข้อบังคับที่ขาด |
| Repository/history/contributionของสมาชิก5คน | docs/team-contribution.md เปิดเผย AI-assisted; gitยังไม่มีcommitที่ยืนยันเป็นงานสมาชิก | ยังไม่ครบ; ห้ามปลอมauthor/historyและห้ามให้AIอ้างทำแทนcontributionมนุษย์ |
| Demo, individual defense, reproducibility | docs/demo-and-defense.md, reference package restore, tests | เครื่องมือและscriptพร้อมบางส่วน แต่ยังไม่มีหลักฐานทุกคนรันและdefendจริง |
| เว็บไซต์เป็นส่วนช่วยสาธิต | เว็บค้น/กรอง/หลักฐาน/exportและcatalogใหม่ | เพิ่มความสะดวกตามคำขอผู้ใช้ ไม่แทน SQL/schema/validation ที่ต้องส่ง |

## สิ่งที่ควรจัดลำดับต่อ

1. ตรวจคู่ข้อมูล EPPO refinery input/output และ gas จริงเป็น candidate โดยดูเวลา หน่วย boundary สิทธิ และ originating agency ไม่เชื่อมยอดประเทศคนละขอบเขตเป็น process โรงงาน
2. ทำ documentation/dictionary/mapping กลางและ unit/source vocabulary โดยรักษาความต่าง national statistic, organization reference และ product inventory ไม่บังคับทุกแถวเป็น LCI exchange
3. อัปเดต requirements และ release readiness ให้ครอบคลุม NSO/inventory ไม่ใช้ผลตรวจ corporate release ไปอ้างครอบคลุมทั้งโครงการ
4. ตรวจ cross-source mismatch และรายงาน denominator ของ coverage ตามจริง
5. ให้สมาชิกทำ review/run/contributionจริงและซ้อม defense แล้วจึง freeze submission

ชื่อentity10ตัว, pandas, pytest, Compose และการเริ่มEPPOเป็นแนวทางที่เสนอในแชต ไม่ใช่เหตุผลให้เปลี่ยนระบบที่ทำงานแล้วโดยไม่มีประโยชน์ สิ่งที่ต้องเทียบคือ semantics, integrity, reproducibility และหลักฐาน ไม่ใช่ชื่อเครื่องมือเหมือนกันทุกตัว
