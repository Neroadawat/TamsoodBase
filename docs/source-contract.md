# Source ID contract — SOURCE_ID_V1

สร้างด้วย `python -X utf8 scripts/build_source_contract.py` จาก registryและartifactsจริง ไม่เปลี่ยนPK/release/ค่าหรือacceptanceเดิม

ผลปัจจุบัน: corporate101,NSO273,inventory16,EPPO5934,DMFcandidate34899 เชื่อม13source snapshots Registrycandidateที่ยังไม่acquireไม่ถูกรวมเป็นแถวข้อมูล

- `build/source-contract/crosswalk.json`: source_id/hash/registryURL/rights/countsและinputhash;เปิดผ่าน `/api/source-crosswalk`
- `observations-internal.jsonl` และ `.csv`: additive source_id/layer/observation_key/hash/locator/usage_profile/originalpayload
- `original`คงทุกfieldและdecimalstring ไม่renameค่าหรือเรียกทั้งหมดว่าaccepted
- identityของDMFเป็นpackage:source_lineภายในsnapshotที่hashระบุ;ชุดอื่นคงobservation_id
- corporate decision/redistribution_statusเดิมอยู่ในoriginalpayload;registry_rights_statusเป็นmetadataทะเบียน ไม่แทนrecord-levelrights

ไฟล์ทั้งชุดใช้ **INTERNAL_REVIEW_ONLY** ห้ามอัปโหลดpublicหรือแนบผู้รับที่ไม่มีสิทธิอัตโนมัติ SourceIDไม่ใช่licenseและไม่ใช่MTECapproval การมี34899candidateไม่ทำให้เป็น34899verifiedLCI

APIเดิมยังคงfieldและidentityเดิมเพื่อcompatibility crosswalkAPIกับnewinternalexportเพิ่มcontractต่างหาก ไม่อ้างว่าทุกAPIrowถูกrenameเป็นsource_idแล้ว ห้ามลบhashเพราะมีreadableID
