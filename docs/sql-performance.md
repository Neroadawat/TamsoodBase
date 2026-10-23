# SQL use cases และผลวัดจริง

## Query ที่ตอบ requirement

sql/mysql/full-queries.sql ใช้ค้นผลิตภัณฑ์/เดือนของ DMF พร้อม provenance, ตรวจ coverage ตามปี/พื้นที่ และ LEFT JOIN หา resource ที่ยังไม่มี observations

sql/mysql/reusable-queries.sql ใช้ดูจำนวนตาม decision/kind/aggregation role, ค้น reported intensity เฉพาะแหล่ง/ปี, แสดง organizational inputs พร้อมขอบเขต และเปิดทุกสมาชิกของ unresolved issues โดยกรอง release_id เสมอ

ไม่มี query รวมพลังงานทุกแถวหรือแปลง production rate ที่ยังไม่ทราบฐานเวลาเป็นยอดปี

## การวัด 23 ตุลาคม 2569 ตามเวลาประเทศไทย

คำสั่ง `python -X utf8 scripts/benchmark_sql.py` ใช้ SELECT และ EXPLAIN ANALYZE เท่านั้น ไม่สร้าง/ลบ index และไม่เปลี่ยนข้อมูล ผลละเอียดอยู่ evidence/sql-performance.json

สภาพแวดล้อม: MySQL 8.1.0 ใน Docker บนเครื่องนี้ ข้อมูล DMF 34,899 observations ค้น period_start=2026-01-01 ได้ 102 แถว ทั้งสอง query ให้ผลตรงกันหลัง sort และตรวจ checksum

| Query variant | Plan ที่พบ | Median root completion time |
|---|---|---:|
| ให้ optimizer เลือกตามปกติ | Index lookup: ix_period_context | 0.208 ms |
| IGNORE INDEX(ix_period_context) | Table scan 34,899 แถว แล้ว filter | 12.0 ms |

วอร์มแต่ละแบบหนึ่งครั้ง จากนั้นวัด 5 รอบ สลับลำดับแบบละรอบ ใช้เวลาจบของ root iterator จาก EXPLAIN ANALYZE ไม่บวกเวลาของโหนดซ้อนกันและไม่รวม latency ของ Docker CLI/client

นี่เป็น controlled baseline ที่ละเว้น period index ไม่ใช่การอ้างว่าเคยลบ index หรือ deploy ก่อน–หลังจริง ผลแสดงว่า index นี้รองรับ workload ที่เลือก แต่ไม่ใช่ production SLA หรือความเร็วเว็บทั้งระบบ ค่าที่วัดอาจเปลี่ยนตาม cache, load และเครื่อง

## ตารางเล็กไม่ได้ต้องใช้ index ทุกครั้ง

query reported intensity ปี 2024 ของ release ปัจจุบันให้ผล 2 แถวจากสองบริษัท แผนมี scan ตาราง metric ขนาดเล็ก ซึ่งเป็นทางเลือกของ optimizer ที่สมเหตุสมผล ไม่สร้าง index เพิ่มทุก column เพื่อบังคับให้แผนดูสวย และไม่ตีความว่าตัวเลขสองบริษัทเทียบกันได้โดยข้าม boundary

อ้างอิงพฤติกรรมและข้อจำกัดเครื่องมือ: [MySQL EXPLAIN / EXPLAIN ANALYZE](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
