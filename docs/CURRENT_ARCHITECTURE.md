# สถาปัตยกรรมปัจจุบันและขอบเขตการยืนยัน

อัปเดต 5 พฤศจิกายน 2569 สำหรับงานแก้รีวิว อ่านหน้านี้ก่อนใช้ข้อความประวัติในเอกสารออกแบบเดิม

| ส่วน | สถานะที่ตรวจได้ | ข้อจำกัด |
|---|---|---|
| เว็บที่เผยแพร่ | Vercel release ตาม evidence/current-frontend-release.json (6พฤศจิกายน: dpl_Wz7EhN4xyjaj2aUsuFp56wjyhLeB) | APIโมเดล/metadata/assetตรงรุ่น ตรวจ10ปลายทาง;EC2ไม่สลับimage |
| API/ฐานวิจัย production | MySQL บน EC2 ตามหลักฐานเดิม | ไม่ได้ย้ายฐานหรือเปลี่ยน service ในรอบนี้ |
| โมเดลกิจกรรม FAME ใหม่ | SQLite แยกใน build/activity-model-store/releases ตาม content hash | local review store ไม่ใช่ MySQL production และไม่ใช่ full LCI |
| หน้า B100 ใหม่ | https://tamsoodbase.vercel.app/#case-study และ /api/model,/api/release | เผยแพร่metadataที่ตรวจแล้ว ไม่เปิด330resultsภายใน |
| ข้อมูลโรงสกัด 2019 | เก็บต้นฉบับ/ปริมาณภายใน สิทธิแจกจ่าย NOT_CLEARED | เว็บแสดงบริบท ลิงก์ต้นฉบับ และตัวเลขกิจกรรมจากแหล่ง CC BY 2020 เท่านั้น |

## รุ่นโมเดลและการคำนวณ

source_observation → process_dataset_version → dataset_exchange → process_instance → calculation_run → result_exchange

product_system_version เก็บฐานศึกษา; scenario_case แยกโรงสกัด 6 กรณี; provider_link_candidate อ้างทั้ง consumer/provider instance และ exchange จริง; allocation_decision, scenario_assumption และ required_decision เก็บเหตุผลที่ยังไม่ปิด ไม่เชื่อมจากชื่ออย่างเดียว

แต่ละ release บันทึก input/code/runtime manifest, ใช้ transaction ทั้งชุด และ seal หลังตรวจ ค่า typed source ต้องตรง original JSON; foreign key ผูกผลกับสมาชิก dataset/run รุ่นเดียวกัน ห้าม UPDATE/DELETE และห้าม INSERT เพิ่มหลัง seal ผลเดิมไม่ถูกเขียนทับ รุ่นใหม่ต้องสร้างฐานใหม่

ดู schema: sql/activity-model-review.sql และหลักฐาน evidence/activity-model-store.json มี 130 source observations, 9 dataset versions, 6 runs, 330 result rows รวม 6 HOLD หน่วยไม่ครบ จำนวนผลนี้ไม่ใช่จำนวนการวัดอิสระ

SQL normalization เป็นเรื่อง keys/dependencies ส่วนการปรับปริมาณต่อฐาน LCI เป็นอีกเรื่อง ไม่มีการอ้างว่าทุก relation เป็น 5NF หรือว่าความถูกต้องของ FK พิสูจน์ความครบถ้วนทางสิ่งแวดล้อม

MySQL equivalent candidate: sql/mysql/activity-model-review.sql ผ่านengine8.4.13ในฐานทดลองowner-markedที่ลบแล้ว ตรวจ130sourcepayloads/330resultrowsทุกfieldและ5negativecasesโดยรหัสerrorตรงคาด APIพร้อมก่อนและหลัง ไม่มีproductiontablemigration ดูevidence/activity-model-mysql.json

ทะเบียนflowภายในครบ130sourcesแยกsource-localidentity/dimension/role;ยังไม่มีelementarymapping/CFที่ยอมรับ จึงeligibleLCIA=0 ไม่ยกinputวัสดุหรือstreamน้ำเสียเป็นemission ดูevidence/model-flow-contract.json

## เว็บและความปลอดภัย

หน้า B100 โหลด metadata สาธารณะจาก origin ของ frontend ได้โดยไม่ต้องรอ API แต่ไม่ได้ยืนยันว่า backend พร้อมใช้งาน ข้อมูลแต่ละ process แสดงฐาน ปี สิทธิ และลิงก์ต้นฉบับ ส่วนค่ากิจกรรม CPO/RBDPO มีลิงก์ตารางปี 2020 แยกจากเอกสารโรงสกัดปี 2019 ชัดเจน

Proxy ยังใช้ server-only upstream secret และค่าเริ่มต้นยอมรับเฉพาะ Quick Tunnel โค้ดใหม่เตรียม TAMSOOD_BACKEND_ALLOWED_ORIGINS เป็น JSON array ของ HTTPS origins แบบตรงตัว เช่น ["https://api.example.com"] ไม่มี path/credentials/port พิเศษ ไม่รับ IP, localhost, wildcard หรือ host ภายใน หากตั้งค่าผิดจะปฏิเสธ ไม่ได้ตั้ง env หรือสร้างโดเมนให้ในรอบนี้ และไม่ทำให้ Quick Tunnel กลายเป็นปลายทางถาวร

## ข้อค้างทางวิทยาศาสตร์

การทวนสูตร transfer เป็นการตรวจเลขจากแบบจำลอง ไม่ใช่ independent mass/energy balance ยังต้องยืนยัน compatibility ต่างปี, allocation ที่อาจอยู่ในตารางต้นฉบับ, รถ/ขนส่ง, การใช้เชื้อเพลิง, การปล่อยจริงจากการจัดการของเสีย และ Thai background providers ที่เข้ากันพร้อมสิทธิใช้ จึงเก็บ CO2e_total=null และ full_lifecycle_inventory=false

