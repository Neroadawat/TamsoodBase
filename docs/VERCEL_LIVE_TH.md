## สถานะล่าสุด — 10 พฤศจิกายน 2569

- ก่อน hotfix การ probe anonymous พบ `/api/eppo` (40 rows), `/api/nso` (273), `/api/product-inventory` (16), `/api/records` (30 `PENDING`), `/api/reference` (30 `NOT_CLEARED` metadata) และ `/api/summary` ตอบ 200. หลักฐานก่อนแก้ไม่เก็บค่าระเบียน: `evidence/production-anonymous-api-exposure-2026-11-10.json`
- สาเหตุ: Vercel Function ใส่ service Basic Auth ไป backend เอง; สิ่งนี้ไม่ยืนยันตัวตนผู้เยี่ยมชมเว็บ
- ทดลอง Preview ก่อน แล้ว deploy hotfix ไป `https://tamsoodbase.vercel.app`: 15 dataset/login endpoints ตอบ 403 ก่อนออก upstream และคืน 0 rows; `/`, `/ask.html`, `/api/healthz`, `/api/release` ยังใช้ได้. RAG POST ตอบ 503 ก่อนเรียก Gemini. หลักฐาน: `evidence/production-dataset-api-hotfix-2026-11-10.json`
- การเปิดให้ผู้ใช้เข้าข้อมูลหรือ RAG ยัง HOLD จนสิทธิ์, end-user authentication, privacy, global rate/cost, quality, monitoring และ rollback ผ่าน; ห้ามเปิด dataset routes กลับก่อนผ่าน gate

## สถานะก่อนหน้า — 9 พฤศจิกายน 2569 (ประวัติ)

- Vercel เชื่อมกับ GitHub repo `Neroadawat/TamsoodBase` แล้ว; push branch ที่ไม่ใช่ production branch สร้าง Preview ได้
- Preview จาก commit `b5b53cf` พร้อมที่ [tamsoodbase-fg26o95bz-neroadawats-projects.vercel.app](https://tamsoodbase-fg26o95bz-neroadawats-projects.vercel.app/); หน้าแรกมีลิงก์ไป `/ask.html` และทดสอบ Gemini ผ่าน Preview ได้หนึ่งคำถาม
- Preview ยังใช้ Vercel Authentication; การ deploy Preview ไม่ได้ทำให้คนทั่วไปเข้าถึงได้
- Production ยังเป็น `main` รุ่นเก่า (`aff41e1` ตามการตรวจล่าสุด), ไม่มี RAG entry point รุ่นใหม่ และ Production RAG ต้องคงปิดจนผ่าน release gates ใน `docs/rag/PUBLIC_WEB_READINESS.md`
- ตั้งแต่เชื่อม Git แล้ว push เข้า `main` อาจสร้าง Production deployment อัตโนมัติ ห้าม merge/promote branch นี้จนตรวจ source, Preview, release gates และแผน rollback ก่อน

เนื้อหาและคำสั่งด้านล่างที่ระบุสถานะก่อน 9 พ.ย. เป็นประวัติ อย่าใช้เป็นหลักฐานสถานะ runtime ปัจจุบัน

## ประวัติสถานะ ณ 30 ตุลาคม 2569

เว็บเปิดอ่านโดยไม่ล็อกอินตามผู้ใช้ Vercelเก็บเฉพาะstaticcodeและupstream42observationsที่ตรวจสิทธิCCBY4.0พร้อมattribution;ข้อมูลAPIอื่นอยู่EC2MySQL ไม่มีrawPDF/ข้อมูลบริษัทเพิ่มในstaticbuild Export FAME/H-FAMEเป็นreviewJSONแยกจากต้นน้ำ รหัสupstreamอยู่serverเท่านั้น ข้อความด้านล่างที่ให้login/บอกว่าVercelไม่มีข้อมูลเลยเป็นประวัติที่ถูกแทนแล้ว ดู evidence/current-frontend-release.json และ docs/expert-review-action-plan.md

# Vercel ใช้งานจริง — 28 ตุลาคม 2569

ลิงก์หลัก: **https://tamsoodbase.vercel.app**

**อัปเดตล่าสุด28ต.ค.: ผู้ใช้ยืนยันเอาหน้า username/password ออกสำหรับการตรวจงาน จึงเปิดอ่านข้อมูลผ่าน Vercel ได้โดยไม่ล็อกอินแล้ว** ใครที่เข้าถึง URL นี้ได้อ่านข้อมูลได้ ไม่ใช่ network ภายใน Vercelเก็บ `TAMSOOD_BACKEND_AUTH` เป็น secret ฝั่งfunctionเพื่อเรียกgatewayเดิม ไม่ฝังลงassets ไม่เปลี่ยนสิทธิ/redistribution_statusของข้อมูลเป็นCLEARED ข้อความวิธีล็อกอินด้านล่างเป็นประวัติรุ่นก่อนการเปลี่ยนนี้

Export DMF เปลี่ยนเป็นstreamผ่านfunction จึงไม่redirectผู้ใช้ไปหน้าถามรหัสของgatewayโดยตรง การอัปเดตรหัสbackendให้เปลี่ยนserver-onlyenvironmentและredeploy ไม่ส่งรหัสลงfrontend

หน้าเว็บเป็น static assets บน Vercel ส่วนข้อมูลยังอยู่ MySQL/EC2 ไม่มีการย้ายข้อมูลวิจัยเข้า Vercel ไม่มีการ push Git

## เข้าใช้งาน

เปิดลิงก์ กด **เข้าสู่ระบบ** ในแถบการเชื่อมต่อ แล้วใช้ username/password เดิมจาก `.local/HTTPS-ACCESS.md` เบราว์เซอร์จะถามบัญชีผ่าน Basic authentication เมื่อสำเร็จกลับหน้าแรกและโหลดข้อมูลได้

หน้า UI/โค้ด static เปิดได้ทั่วไป แต่ข้อมูล API/export ต้องมีรหัส ไม่ได้ฝัง shared password, AWS credential, SQLite, raw PDF/CSV หรือ SQL dump ใน assets

## เส้นทางข้อมูล

Vercel frontend → `/api/...` บน Vercel function → HTTPS gateway แบบต้องล็อกอินบน EC2 → API/MySQL ภายใน

Function ส่งต่อ credential ที่ผู้ใช้ป้อนเฉพาะไปยัง origin ที่กำหนดบนเซิร์ฟเวอร์ ไม่ใส่ credential ใน URL หรือ public config และไม่ follow redirect จาก upstream หน้าเว็บกับ API เป็น origin เดียวจึงไม่ต้องเปิด CORS สาธารณะ

`/api/export` ของ DMF redirect ไป gateway ที่ต้องล็อกอินโดยตรง เพื่อไม่ติดขนาด response ของ Vercel Functions ซึ่งอาจต้องใส่รหัสเดิมอีกครั้งที่ origin นั้น export ชุด reference ขนาดเล็กผ่าน proxy ได้ตามปกติ ดู [Vercel payload limits](https://vercel.com/docs/functions/limitations)

## ความคงที่ของลิงก์

Production alias ของ project คือ `tamsoodbase.vercel.app`; deployment ใหม่จะใช้ alias เดิม ส่วน backend ยังใช้ Quick Tunnel ชั่วคราว หาก tunnel restart และ URL เปลี่ยน ต้องอัปเดต environment `TAMSOOD_BACKEND_ORIGIN` ของ Production แล้ว deploy ใหม่ ลิงก์ frontend ไม่เปลี่ยน แต่ข้อมูลจะยังไม่ทำงานระหว่างปลายทางเก่าหยุดจนแก้ config

การทำให้ทั้งระบบถาวรยังต้องมี backend domain/named tunnel และระบบบัญชีสำหรับใช้งานระยะยาว ไม่อ้างว่า Quick Tunnel มี uptime guarantee

## ขั้นเผยแพร่รอบถัดไป

ให้ใช้ Git-connected flow ตามปกติ: push ไป feature branch เพื่อสร้าง Preview, ตรวจ deployment ที่ commit ตรงกับ branch และทดสอบหน้าแรก, `/ask.html`, API, citations และ error state ก่อน การสร้าง Preview ไม่ควรใช้ `--prod`

อย่ารันคำสั่งเก่า `npx vercel deploy --prod` จาก feature branch หรือ package ที่ยังไม่ได้ตรวจ คู่มือและ `scripts/package_vercel.mjs` เคยเป็น allowlist รุ่นก่อนและกำลังอัปเดตให้รวมหน้า RAG/API/corpus ปัจจุบัน การแพ็กเกจอย่างเดียวไม่ใช่เหตุผลให้ Production พร้อมปล่อย

ก่อน deploy Production ต้องตรวจ `docs/rag/PUBLIC_WEB_READINESS.md` และ `docs/rag/public-release-manifest.json` ใหม่ให้ผ่านทุก gate, ยืนยัน privacy/rights/user acceptance/rate-limit/monitoring/rollback, แล้ว deploy จากสายโค้ดที่ตรงกับ Production branch เท่านั้น หลังเชื่อม Git แล้ว push เข้า `main` สามารถเริ่ม Production deploy อัตโนมัติ

อย่าอัปโหลด `.env.local`, `.local/`, research data หรือ token ของ CLI ไป Git/Vercel source package; เก็บ `GEMINI_API_KEY` เป็น server-side Secret ใน Vercel environment ที่ตรงกับ deploy target เท่านั้น

## ตรวจจริงแล้ว

`evidence/vercel-deployment.json`: API27กรณีตรงกับ SQLite/MySQL baseline, ไม่ล็อกอิน401, static assets ไม่มีรหัส, config ใช้ same-origin และมี login link

`tests/vercel-proxy-behavior.cjs`: บล็อก write/unknown routes/unsafe origin, 401 challenge, ไม่ follow redirect, login กลับ `/` เสมอ ไม่รับ return URL จากผู้ใช้

แก้ readiness rewrite ให้รองรับ path เดิมที่ Vercel ส่งเข้า function แล้ว ตรวจ production ซ้ำผ่าน ไม่ถือผล local เป็นผล deploy
