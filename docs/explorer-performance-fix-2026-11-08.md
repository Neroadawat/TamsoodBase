# แก้คอขวด Explorer และตรวจชุดเอกสาร — 8 พฤศจิกายน 2569

**สถานะใหม่กว่า 9 พฤศจิกายน:** Corporate กู้และตรวจแล้ว ส่วน EPPO/DOM ต้นฉบับยังขาด ดู [คู่มือปัจจุบัน](TEAMMATE_NEXT_STEPS_TH.md) ข้อความ Corporate unavailable และจำนวน tests ในรายงานนี้เป็นประวัติรอบก่อนกู้ ไม่ใช้แทนผลล่าสุด

ต่อจากข้อค้างใน `docs/local-engineering-review-2026-11-08.md` พบคอขวดในเส้นทาง export และการอ่าน metadata ไม่ได้สรุปว่า Windows หรือ network เป็นสาเหตุโดยไม่มีหลักฐาน

## การแก้และความถูกต้องของข้อมูล

1. Export เดิมดึงรายละเอียด 5,001 แถวเป็น Python objects ก่อนปฏิเสธคำขอที่เกิน 5,000 แถว เปลี่ยนเป็น bounded COUNT จาก query ที่ใช้ joins/filters เดียวกันก่อนดึงรายละเอียด พร้อมคง LIMIT และ guard หลังดึงไว้
2. หน้ารายการเดิมอ่าน metadata ของ package เดียวกัน 30 ครั้ง เปลี่ยนเป็น cache เฉพาะภายในคำขอ อ่านครั้งเดียวต่อ package คำขอถัดไปยังอ่านใหม่ ไม่เก็บ cache ถาวรที่อาจค้างข้าม snapshot
3. เกณฑ์ส่งออกยัง 5,000 แถว: fixture ตรวจ 5,000 ผ่าน/5,001 ปฏิเสธ/visibility filters ตรงกัน/metadata เปลี่ยนแล้วคำขอใหม่เห็นค่าใหม่ เป็นข้อมูลทดสอบแยกจาก source จริง

เทียบ source ก่อนแก้ที่เก็บจาก ZIP รอบก่อนกับ source หลังแก้บนฐานเดียวกัน: **34,899 candidate rows ครบทั้งตาราง แบ่ง 72 product/year partitions** ผล API ทุก field และลำดับตรงกัน รวม CSV bytes ตรงกัน ตรวจหน้าเพิ่มเติม 7 กรณี รวม HOLD, copies และ literal search ข้อมูลใน resource/staging/candidate/rejected/duplicate_disposition มี fingerprint เดิม `f1be67906d36a4881f4e2e453b20d72ab225f767d83d20bd1ef861c3307ece6e`

## ผลเวลาในเครื่องนี้

เปรียบเทียบระดับฟังก์ชันที่ concurrency 8 จำนวน 24 คำขอต่อ operation:

| Operation | p95 ก่อน (ms) | p95 หลัง (ms) |
|---|---:|---:|
| หน้า records | 106.537 | 28.290 |
| Export กรองแล้ว | 328.772 | 339.932 |
| ปฏิเสธ export กว้าง | 3406.962 | 12.283 |

Export ที่ผ่านเกณฑ์ไม่ได้เร็วขึ้นในการวัดนี้ มี probe เพิ่มหนึ่ง query; การแก้มีเป้าหมายหลักที่คำขอเกินขีดจำกัดและ metadata ไม่อ้างว่าทุก operation เร็วขึ้น

ตรวจผ่าน HTTP แบบ workload ผสมเดิม บริการละ 24 คำขอที่ concurrency 1/4/8 รอบละ 144 คำขอรวม Explorer+RAG ผลทั้ง baseline/หลังแก้/ยืนยันอีกครั้งได้สถานะและผลตามคาดครบ:

| Explorer HTTP p95 | ก่อนแก้ (ms) | หลังแก้ (ms) | ยืนยันอีกครั้ง (ms) |
|---|---:|---:|---:|
| c1 | 79.23 | 48.96 | 34.91 |
| c4 | 921.72 | 68.45 | 111.56 |
| c8 | 2377.42 | 236.24 | 234.05 |

ตัวเลขยืนยันการปรับปรุงใน workload local นี้ ยังไม่ใช่ production capacity/SLA หรือผลทดลองสุ่มควบคุม มีการ restart Explorer ก่อนวัดหลังแก้และวัดตามลำดับ PeakWorkingSet ยังเป็น peak ตลอดอายุ process จึงไม่อ้างการลด memory จากการ restart

ตรวจ bounded-probe SQL shape แบบ read-only ใน MySQL lab ที่ตรวจ owner แล้วได้ 5,001 / 1,125 / 0 ตรง expected bounded count จากข้อมูลจริง 3 กรณี ไม่ใช่ production API/MySQL parity ของทุกเส้นทาง

ผล tests รอบนี้: boundary fixtures 4, Explorer 5, MySQL store 4, WSGI 6, schema diagrams 3 และ frontend 13 ผ่าน; HTTP Explorer 9 checks ผ่าน โดย Corporate/EPPO ยังตอบ unavailable ตาม snapshot ที่ขาด ผลชุดส่งต่อสะอาดดู `build/handoff-package/VERIFICATION.json`

## SRS ที่สร้างใหม่

พบ source hash ของ SRS 0.7.1 ใน Git ต่างจาก `evidence/srs-current-review.json` เดิม และเครื่องนี้ไม่มี PDF ฉบับที่อ้าง จึงสร้างใหม่จาก **Markdown เดิมโดยไม่แก้เนื้อหา** สร้างภาพ ERD จาก DDL เดิมและแผนภาพ local review ที่ระบุ scope ชัด

ปรับเฉพาะตัวสร้าง PDF ให้ตารางประวัติรุ่นกระชับลง ไม่เหลือหน้าที่มีแถวเดียว และใช้ hyphen ในข้อความแสดงผล ได้ PDF **27 หน้า** render ครบ ตรวจ contact sheets ทุกหน้าและภาพเต็มหน้าสำคัญ พร้อมตรวจ heading/draft labels/ขอบเขตตัวอักษร ไม่มีข้อความล้นหน้าที่ตรวจพบ เก็บบันทึก render เก่าแยกไว้ ไม่ใช้ hash เก่ารับรองไฟล์ใหม่

- ไฟล์: `output/pdf/TamsoodBase-SRS-review.pdf`
- source SHA256: `c2299cd48cad6bf7c4105be8f97a3d9f7317ee4482a13722b2b2b543a1cbd3a3`
- PDF SHA256: `647444a9ae5086e10b5328edf09a9ed84c4363860e4dbb9ab05c274d1c76c067`
- หลักฐาน: `evidence/srs-handoff-render-2026-11-08.json` และ `evidence/srs-current-review.json`

ยังเป็นร่างรอทีมตรวจ ไม่ได้ตรวจ production ใหม่ทุกคำกล่าวใน SRS, ไม่ได้ rebuild slides/PPTX และไม่ได้รับรอง contribution/consent หรือส่งงาน PDF อยู่แยกจาก source ZIP ที่ไม่รวม output/

## หลักฐานและข้อค้าง

- `evidence/explorer-performance-fix-2026-11-08.json`: all-row parity และ controlled function profile
- `evidence/local-load-performance-{baseline,fixed,confirmation}-2026-11-08.json`: HTTP ทั้งสามรอบ รวม RAG control
- `evidence/local-export-probe-mysql-2026-11-08.json`: read-only query-shape check
- `docs/scientific-source-check-2026-11-08.md`: ผลค้นหลักฐาน LCI เพิ่มและเหตุที่ยังไม่ปิด gate

T109/T114 ยัง IN_PROGRESS สำหรับ staging/production, permanent endpoint, independent human/screen-reader review และ scientific gates ส่วน T55/T58 ยังรอทีมตรวจและ final consistency ของ deliverables ทุกชิ้น งานใหม่ยังอยู่ใน working tree ไม่ได้ commit/push/deploy
