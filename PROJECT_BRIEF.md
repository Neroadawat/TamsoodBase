# TamsoodBase — CN230 × MTEC

เป้าหมาย: ระบบข้อมูล Petroleum, Natural Gas & Fuels ที่ตรวจสอบกลับไปยังแหล่งต้นทางได้ พร้อมงานส่งรายวิชาและการอธิบายข้อจำกัด

## แหล่งหลัก
- docs/CHATGPT_HANDOFF_PROMPT.md และ docs/TEAM_HANDOFF.md: วิธีส่งต่อ ข้อจำกัดและการทำงานร่วมทีม
- docs/team-data-policy.md และ docs/acceptance-rules.md: นโยบายรับข้อมูล
- docs/dataset-model-index.md และ docs/source-contract.md: ชั้นข้อมูลและสัญญาข้อมูล
- docs/next-work-plan.md และ docs/final-gap-plan.md: ลำดับงานปัจจุบัน ตรวจข้อความที่ supersede กัน
- docs/submission/FINAL_DELIVERY_PLAN.md และ docs/submission/SRS.md: งานส่ง
- docs/tasks.md: งานและเกณฑ์จบ ไม่ใช้จำนวน task เป็นคะแนนความพร้อม

## กฎโดเมน
ACCEPTED_REFERENCE ไม่เท่ากับ normalized product LCI; ไม่รวม source statistics เป็นจำนวน accepted เดียว EPPO intake BBL/DAY กับ output MillionLitres ไม่ใช้หารเป็น refinery yield ห้ามเดา time basis, allocation หรือ gas volume-to-mass ตรวจสถานะ สิทธิ หน่วย ปี scope และต้นทางจริง ไม่แต่ง approval ผลทดสอบ contribution memo consent หรือหลักฐาน

## วิธีตรวจ
เลือกคำสั่งและ tests จาก README และเอกสารส่วนที่แก้ ตรวจว่ามี snapshot/runtime จริงก่อนรัน pipeline; raw/build/.local/Docker volume อาจไม่ตาม Git ห้ามสร้างข้อมูลเพื่อให้ผลตรวจผ่าน

