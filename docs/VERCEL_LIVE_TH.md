## สถานะปัจจุบัน 30 ตุลาคม 2569

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

## Deploy ครั้งถัดไป

ใช้บัญชีที่เชื่อม CLI แล้ว และ project `neroadawats-projects/tamsoodbase`

```powershell
node scripts/package_vercel.mjs
npx --yes vercel@65.5.0 deploy --cwd build/vercel-upload --prod --yes
```

ต้องใช้โฟลเดอร์ upload ที่คัดไฟล์แล้ว ไม่ deploy root repository โดยตรง เพราะรอบจริงพบ CLI อัปโหลดได้เฉพาะ vercel.json จาก pattern allowlist เดิม ทำให้ builder หาย โฟลเดอร์ upload มี source allowlist เพียง9ไฟล์ กับ metadata link project ที่ไม่ใช่ credential

Production environment:

- `TAMSOOD_DEPLOY_MODE=proxy` สำหรับ build same-origin UI
- `TAMSOOD_BACKEND_ORIGIN` เป็น HTTPS gateway origin เท่านั้น ไม่มี username/password

อย่าอัปโหลด `.env.local`, `.local/`, research data หรือ token ของ CLI ให้ Git/Vercel source package

## ตรวจจริงแล้ว

`evidence/vercel-deployment.json`: API27กรณีตรงกับ SQLite/MySQL baseline, ไม่ล็อกอิน401, static assets ไม่มีรหัส, config ใช้ same-origin และมี login link

`tests/vercel-proxy-behavior.cjs`: บล็อก write/unknown routes/unsafe origin, 401 challenge, ไม่ follow redirect, login กลับ `/` เสมอ ไม่รับ return URL จากผู้ใช้

แก้ readiness rewrite ให้รองรับ path เดิมที่ Vercel ส่งเข้า function แล้ว ตรวจ production ซ้ำผ่าน ไม่ถือผล local เป็นผล deploy
