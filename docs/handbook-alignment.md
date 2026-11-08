# เทียบโครงงานกับคู่มือภาพถ่าย

ทบทวน 25 ตุลาคม 2569 จากภาพหน้า **3–20** ที่มองเห็นในแชตนี้ เลขหน้าเป็นเลขที่พิมพ์บนเอกสาร ไม่อ้างว่าได้ตรวจหน้า1–2หรือประกาศ Teams ล่าสุด เอกสารนี้เปรียบเทียบข้อกำหนดกับงานจริง ไม่ใช่คะแนนที่กรรมการให้หรือการรับรองโดย MTEC

## ข้อกำหนดกับหลักฐาน

| หน้า / บท | สิ่งที่คู่มือเน้น | งานที่มีจริง / สิ่งที่นำมาปรับใช้ |
|---|---|---|
| 3 / 1 | Database Engineering ตั้งแต่ requirements ถึง defense; ไม่นับ raw rows แทนข้อมูลผ่านตรวจ | tasks.json, requirements.md, pipeline-audit.md แยก DMF pending / reference / inventory; ไม่ใช้จำนวนรวมทุกชั้นเป็นคะแนนแข่งขัน |
| 4–5 / 2 | ค่าอย่างเดียวไม่พอ ต้องมี unit/time/geography/process/source; ไม่เดากฎโดเมน | dataset-model-index.md และเอกสารแต่ละแหล่งคง context; inventory16มีฐาน1000MJfuelแต่ปีวัดไม่ระบุ; DMF historical time basisยังไม่ยืนยัน |
| 5–6 / 3 | Source Registry รวม candidate/approved/rejected พร้อม rights และ access time | source-registry.csv, source-use-review และ acquisition manifests; สถานะรับข้อมูลไม่เท่ากับสิทธิแจกจ่าย |
| 6 / 4 | Canonical representation เป็น integration strategy ไม่บังคับ EER superclass/subclass | dataset-model-index.md เชื่อมความหมายหลาย schema; ไม่ยุบ national statistics กับ process inventory และไม่อ้างว่ามี physical schema เดียว |
| 7–8 / 5 | เริ่ม requirements; identity/cardinality/PK/FK ต้องอธิบายได้; proposed entities เป็น draft | requirements.md, database-design.md, reusable-model.md, supplemental-mysql.md, sql/mysql/*schema.sql; ชื่อตารางต่างจากตัวอย่างได้เมื่ออธิบาย semantics |
| 8–9 / 6 | API/CSV ก่อน HTML/browser; เก็บ raw evidence ก่อน transform | acquisition scripts และ raw snapshots ในเครื่อง; API/browser ไม่ใช่เป้าหมายการเรียนหลัก; ไม่สกัดต้นทางซ้ำเพียงเพื่อเดโมเมื่อไม่มีความเปลี่ยนแปลง |
| 9–10 / 7 | Raw → Staging → Mapping → Canonical; transform/validation/evidence ชัด | mapping.md, reusable-model.md, nso-source.md, eppo-source.md; pipeline replay ตรวจผลซ้ำแบบแยก workspace |
| 10–11 / 8 | Schema/completeness/reference/provenance/duplicate/numerical/semantic gates; rejectต้องมีเหตุผล | DMF reject6/pending34671; corporate101→reference97/hold4; typed/payload checks และ T42ตรวจแถวส่วนเกิน; ไม่อ้าง97เป็นnormalizedLCI |
| 11–12 / 9 | ทุกrecordต้องตอบว่ามาจากไหน; responsible data/AI | source locators/hash/batch, team-data-policy.md, source-use-notice.md; contributionและการตรวจโดยสมาชิกต้องเกิดจริง |
| 12–13 / 10 | DDL/DML/DQL/constraints, normalization, indexมีผลวัด, backup reproduce | sql/mysql/, sql-performance.json, normalization-audit.md, restore evidence; candidateฐานแยกยังไม่แทนproductionและไม่รับรอง5NF |
| 13–14 / 11 | Milestones/stage gates/repoแยกraw/staging/accepted/rejected | tasks.json→task_board.py, docs/,src/,sql/,data/,evidence/; W08–W15เป็นสัปดาห์เรียน ไม่ใช่กำหนดส่งจริง |
| 15–16 / 12 | UNDERSTAND/DESIGN/BUILD/DEFEND; gradeกับchallengeแยกกัน | ใช้ตาราง package ด้านล่าง; rubric20คะแนนดิบ ไม่ใช่20%รายวิชา; หน้า15ระบุbaseline15% ยังไม่ใช้แทนประกาศเปลี่ยนล่าสุด |
| 16–17 / 13 | Demo8ขั้นและindividual defense; แสดงend-to-end evidence | ปรับ demo-and-defense.md ให้มี pipeline/SQL/trace/limitationsครบ; ซ้อมรายคนยังต้องทำจริง |
| 17 / A | Registry/mapping/validation/reject/contribution templates | มีเอกสารและlogsจริงตามหน้าที่ ไม่จำเป็นต้องชื่อไฟล์เหมือนtemplate; ห้ามเติมcontributionของสมาชิกแทน |
| 18–19 / B,C | GlossaryและQAด้านdomain/database/data/engineering/professional/defense | ใช้dictionary, release audit, pipeline audit, README; QAอัตโนมัติผ่านไม่เท่ากับสมาชิกทุกคนdefenseได้ |
| 20 / Q | ข้อมูลมาจากไหน / ความหมายและหน่วย / พิสูจน์ย้อนกลับอย่างไร | ใช้สามคำถามนี้กับตัวอย่างรับ1รายการและพัก1รายการก่อนเดโม; source evidenceต้องเปิดได้ในเครื่อง |

## จัดงานส่งเป็นสี่ package

| Package | ทางเข้าที่ทีมใช้ตรวจได้ | สถานะที่ต้องพูดตรงกัน |
|---|---|---|
| UNDERSTAND | requirements.md, source-registry.csv, team-data-policy.md | มีbaseline; กำหนดส่ง/ช่องทางล่าสุดยังต้องดูประกาศจริง |
| DESIGN | dataset-model-index.md → schema/dictionary/mapping, normalization-audit.md, data-model-selection.md | หลายschemaมีเหตุผล; normalized candidateยังเป็นฐานทดลอง |
| BUILD | README.md, src/, sql/, pipeline-audit.md, evidence/ | ตรวจlocalและ26ตุลาคมอัปเกรดEC2private/S3ถาวรแล้ว; backuphashผ่าน; frontendยังไม่public ดูPRIVATE_BACKEND_OPERATIONS_TH.md |
| DEFEND | demo-and-defense.md, team-contribution.md, TEAM_HANDOFF.md | มีแนวสาธิต; contributionและซ้อมจริงของมนุษย์ยังไม่ครบ |

## ช่องว่างที่ไม่ควรซ่อน

- **CLO5:** เพิ่ม [การเลือกแบบจำลอง](data-model-selection.md) เปรียบเทียบ Raw/JSON/Relational/Graph จากงานนี้ Graphเป็นแนวทางวิเคราะห์ ไม่ได้ติดตั้ง graph database หรือ benchmark แล้ว
- **Challenge:** หน้า15ให้น้ำหนัก volume30/traceability25/accuracy25/coverage20 แต่ยังแปลงยอดreference/statisticsเป็นคะแนนแข่งขันไม่ได้ ไม่บวกtotalกับcomponentsหรือrepublicationเป็นแหล่งอิสระ
- **5NF:** คู่มือหน้า12–13เน้นnormalizationและintegrity ไม่ได้ระบุว่าทุกตารางต้อง5NF; ยังต้องพิสูจน์FD/JDก่อนกล่าวอ้าง
- **ความพร้อมส่ง:** ข้อจำกัดDMF/rights, contributionรายคน และประกาศส่งล่าสุดยังคงอยู่ แยกจากการเตรียมdeployซึ่งเป็นความต้องการเพิ่มเติมของผู้ใช้

ไม่ให้คะแนนตัวเองตามrubricและไม่สร้างหลักฐานที่ไม่มี เพื่อให้ทีมอธิบายสิ่งที่ทำจริงได้ตรงกับคู่มือ
