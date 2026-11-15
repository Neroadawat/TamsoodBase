# ไฟล์งานล่าสุดสำหรับตรวจและเตรียมส่ง M4

อัปเดต 15 พฤศจิกายน 2569 ชุดนี้ยังรอข้อมูลและการยืนยันของสมาชิก ไม่ใช่การรับรองว่าพร้อมส่งทุก Gate

| งาน | ไฟล์ |
|---|---|
| เล่มล่าสุด 71 หน้า ไอไลต์เหลืองและสารบัญตรวจครบ55รายการ | [Report REVIEW v2](../../output/m4/review-2026-11-15/S2-G05_M4_Report_REVIEW_2026-11-15_v2.docx) |
| สไลด์หลักของ Claude 10 หน้า รวมหน้าสำรอง | [PowerPoint](../../output/m4/S2-G05_M4_Slides_3min.pptx) · [PDF](../../output/m4/S2-G05_M4_Slides_3min.pdf) |
| สไลด์เสริมธีม Canva 2 หน้า แยกจากชุดหลัก | [PowerPoint 2 หน้า](../../output/m4/TamsoodBase_Canva_Additions_2slides_2026-11-15.pptx) |
| โปสเตอร์ A4 10 บล็อก | [PDF](../../output/m4/S2-G05_M4_Poster_A4_10blocks.pdf) · [HTML](../../output/m4/S2-G05_M4_Poster_A4_10blocks.html) |
| เดโม5นาทีพร้อมลูกศร | [MP4](../../output/prototype/TamsoodBase-Website-Evidence-5min-TH-annotated.mp4) |
| CSVชุดส่ง16แถว32คอลัมน์ | [product_inventory.csv](../../output/m4/dataset/product_inventory.csv) |
| SQLตรวจแบบอ่านอย่างเดียว | [presentation-verification.sql](../../sql/mysql/presentation-verification.sql) |

สไลด์ Canva เพิ่มใหม่2หน้าเตรียมไว้สำหรับชุด Canvaเดิม6หน้า จึงจะเป็น8หน้าหลังนำเข้า ไม่ใช่ให้นำไปรวมกับชุดหลัก10หน้าของClaude สไลด์เสริมยังไม่ถูกนำเข้าCanva เพราะติดสิทธิ์อัปโหลดของส่วนขยาย ไม่มีการแก้6หน้าต้นฉบับ

ก่อนส่ง: ทีมกรอกContribution, Consent, MemoM4และช่องทีมกรอก ตรวจไฮไลต์ แล้วออกReport/MemoPDFฉบับสุดท้าย ซ้อมรวมเปิดคลิปให้ไม่เกิน8นาที และตรวจเครื่องฉาย/โปสเตอร์พิมพ์จริง SQLบนMySQLฐานทดลองและผลAPIผ่านแล้ว แต่ยังไม่ได้รันบนEC2โดยตรง

ผลตรวจรอบรวมเข้าmain: [main-merge-review](../../evidence/main-merge-review-2026-11-15.json) เล่ม71หน้าและสารบัญ55รายการถูกบันทึกใหม่หลังเพิ่มแถวโปสเตอร์ ไม่ใช้จำนวนหน้า70จากผลเก่าเป็นสถานะล่าสุด
