# Schema normalization audit — 24 October 2026

## ข้อสรุปสำหรับทีม

Backend ใช้งานได้ไม่เท่ากับพิสูจน์ Normal Form แล้ว ฐานที่ใช้งานจริงยังไม่ควรเรียกว่า “ทั้งระบบเป็น 3NF/BCNF/5NF” พบ dependency ซ้ำใน corporate metric และมีค่าคำนวณ/หลักฐานต้นทางเก็บคู่กันโดยตั้งใจ งานนี้สร้าง candidate SQLite แยกและตรวจผล ไม่ migrate EC2 หรือเปลี่ยน API เดิม

## Key และ dependency ที่ใช้วิเคราะห์

FD คือกฎที่ต้องจริงในทุกสถานะข้อมูลที่อนุญาต ไม่ใช่เพียงค่าที่บังเอิญไม่ซ้ำใน snapshot นี้ PK แบบ hash ไม่ทำให้ dependency อื่นหายไป และ FK ไม่ใช่หลักฐานว่าเป็น 3NF

| Relation / key | FD / กฎที่เกี่ยวข้อง | ผลประเมิน |
|---|---|---|
| publisher / publisher_id | publisher_id → name | BCNF ภายใต้ FD นี้เท่านั้น; ไม่สมมติว่าชื่อ unique |
| document / document_id | document_id → publisher_id,title,report_year,source_url,accessed_at,rights_status | เก็บเอกสารพร้อม acquisition metadata หนึ่งค่า; ถ้ารองรับหลาย URL/หลายการเข้าถึง ควรแยก document_location/access_event ไม่ overwrite ประวัติ |
| unit / unit_code | unit_code → dimension | BCNF ภายใต้กฎ master นี้; dimension ไม่เป็น key |
| context / context_id | context_id → document_id,source_scope,description,geography_status | BCNF ภายใต้ FD ที่ระบุ; UNIQUE(context_id,document_id) เป็น superkey ไม่ใช่ candidate key ขั้นต่ำ |
| metric รุ่นเดิม / metric_key | metric_key → ทุก field; context_id → document_id | **ผิด 3NF**: context_id ไม่เป็น superkey ของ metric และ document_id ไม่ใช่ prime attribute ตาม key ที่ประกาศ; มีหลาย metric ต่อ context |
| metric candidate / metric_key | metric_key → source_metric_id,label,context_id,unit_code,data_kind,aggregation_role | เอา document_id ออก; BCNF เมื่อไม่มี FD เพิ่มนอกเหนือจาก key นี้ ไม่รับรอง source_metric_id unique ข้ามเอกสาร |
| observation / observation_id; alternate(metric_key,reference_year) | key → raw/amount/locator; parse(raw_value) × scale_factor → scaled_amount | มี derived redundancy โดยตั้งใจเพื่อ audit; ไม่รับรองทั้ง relation เป็น 3NF/BCNF จาก PK อย่างเดียว ต้องกำหนด parse/precision semantics ก่อนแยกค่าคำนวณเป็น view |
| quality_issue / issue_id | issue_id → document_id,source_issue_id,reason | key FD; ไม่สมมติ source_issue_id unique ทั่วระบบ |
| review / (observation_id,policy_version) | key → decision,review_actor,trace_verification | ไม่สมมติว่า policy_version → review_actor เพราะอนาคตมีผู้ตรวจหลายคนได้ |
| data_release / release_id | release_id → policy_version,usage_profile,created_at | ถ้ากำหนด policy_version → usage_profile เป็น business rule ต้องแยก policy master; ปัจจุบันไม่ถือค่าคงที่ใน snapshot เป็นข้อพิสูจน์ |
| issue_observation; release_observation / คู่ FK | relation ประกอบด้วย binary association และ composite key | ไม่มี non-key attribute ให้เกิด partial/transitive FD; ไม่ใช้แถวที่มีจริงอนุมานกฎ independent association |

## ชุดข้อมูลอื่นที่ตรวจจาก DDL

| Schema | Key / จุดสำคัญ | ผลและข้อจำกัด |
|---|---|---|
| tamsood_research (DMF) | source_record/observation/duplicate_disposition/rejected_record ใช้(snapshot_id,source_line); production_context ใช้ context_id | มีชั้น raw และ audit ตาม source; ต้องแยกการประเมิน payload ออกจาก typed relations ไม่ประกาศ NF รวมทั้งฐาน ต้องตรวจความสอดคล้อง package ของ context กับ snapshot เพิ่มหากขยาย loader |
| tamsood_supplemental | observation ใช้(snapshot_id,observation_id); process ใช้(snapshot_id,process_id); subtype ใช้ key parent | process basis แยกจาก exchange แล้ว; source hash/locator และ payload ยังเป็น source snapshot มีความซ้ำ ไม่รับรอง BCNF ทั้งฐาน ต้องกำหนดว่าไฟล์/ตารางหนึ่งผูก source hash อย่างไรก่อน decomposition |
| tamsood_eppo | observation_id และ alternate(snapshot_id,reference_year,month,subject) | ชุดปัจจุบันกำหนดหน่วยต่อ dataset/snapshot จึงมี snapshot_id → unit_code ซ้ำใน observation; หากคงกฎนี้ควรย้ายหน่วยไป snapshot/master ใน migration ถัดไป ไม่เดาว่าทุก snapshot ในอนาคตมีหน่วยเดียว |

JSON ไม่ได้ทำให้ SQL relation ผิด 1NF โดยอัตโนมัติ แต่การมี JSON ต้นทางไม่ได้พิสูจน์ว่าเนื้อหาภายในได้รับ normalization แล้ว ตัวเลขที่เหมือนกันในไฟล์เดียวไม่ใช่ FD โดยอัตโนมัติ

## การแก้ที่ลงมือและขอบเขตการพิสูจน์

รัน `python scripts/audit_normalization.py` สร้าง `build/normalization/reference-candidate.sqlite` จากฐานเดิมแบบ read-only และเขียน `evidence/normalization-audit.json` เปลี่ยนเฉพาะ metric โดยเอา document_id ออก อ้าง context ด้วย FK และปรับ view ให้หา document ผ่าน context ตารางอื่นคง schema/ค่าตามเดิม จึงยังมี observation audit redundancy ตามที่ระบุข้างบน

การแยก metric เดิม R เป็น metric ใหม่ M และ context/document mapping C สามารถ join กลับแบบ lossless เพราะ intersection คือ context_id และ context_id → document_id; context_id เป็น key ของ C ที่ใช้อ้างอิง FK บังคับทุก metric ต้องมี context ส่วน document ถูกบังคับโดย context อยู่แล้ว ไม่มีอิสระให้ metric เลือก document ขัดกับ context การพิสูจน์นี้ครอบคลุม dependency นี้ ไม่ใช่ 5NF ทุก relation

ตรวจจริง: reconstruct metric เดิมทุก field ตรง; reference_catalog ทุก column ตรง 101 แถว; accepted_reference ทุก column ตรง 97 แถว (อีก 4 ยัง hold); FK check ผ่าน และทดสอบ update ไป missing context ถูกปฏิเสธ SHA256 ฐานต้นทางไม่เปลี่ยน

ผลรัน `python -m unittest discover -s tests`: 72 tests ผ่าน รวม 3 tests ใหม่สำหรับ lossless/constraints, การห้ามเขียนทับ source และการปฏิเสธ source ที่ context/document ขัดกัน ระหว่างพัฒนาพบ SQLite connection ไม่ปิดเมื่อออกจาก context manager บน Windows และแก้ด้วย explicit closing แล้ว

ไม่มีการเปลี่ยน acceptance, rights, normalized-LCI status หรือจำนวนข้อมูล ต่อมาในรอบตรวจทั้งกระบวนการได้โหลด candidate เข้า MySQL แยกชื่อ `tamsood_nf_c4a3f824c950` ด้วย `python scripts/verify_normalization_mysql.py` แล้ว เทียบ catalog ทุกช่อง101แถว/accepted97แถวตรง SQLite และตรวจ4กรณี invalid context/kind/amount/decision ถูกปฏิเสธ หลักฐาน `evidence/normalization-mysql.json`; generated schema/load SQL อยู่ `build/normalization/` ไม่ได้แก้ `tamsood_reusable` หรือ EC2 การสลับฐานใช้งานจริงยังต้องมี migration/rollback และตรวจ consumer เพิ่มก่อน

## 4NF และ 5NF

4NF ต้องตรวจ nontrivial multivalued dependencies; 5NF ต้องตรวจ nontrivial join dependencies ว่าถูกบังคับโดย candidate keys หรือไม่ การมีตารางเล็กหลายตารางหรือ JOIN ผ่านไม่เพียงพอ ต้องมี business rule ที่ระบุว่า facts หลายชุดเป็นอิสระและ recombine กันได้จริง ห้ามแยก process/flow/source เป็นคู่แล้วสร้าง combinations ที่ต้นฉบับไม่เคยรายงาน

ปัจจุบันยังไม่มี JD/MVD specification ครบทุก relation จึง **ไม่รับรอง 4NF/5NF ทั้งระบบ** เป้าหมาย Defense ที่ตรงหลักฐานคือ “ตรวจ FD ของ typed model พบและแก้ความซ้ำ context/document ใน candidate พร้อม lossless roundtrip; raw/audit และข้อค้างระบุแยกชัดเจน”

อ้างอิงแนวคิด: [UNSW Relational Design Theory](https://cgi.cse.unsw.edu.au/~cs3311/22T3/notes/D/notes.html) และ [SJSU: dependencies beyond BCNF](https://www.cs.sjsu.edu/~pollett/157a.34.05f/Lec30112005.pdf) เอกสารนี้เป็นการวิเคราะห์ของทีม ไม่ใช่การรับรองโดยอาจารย์/MTEC
