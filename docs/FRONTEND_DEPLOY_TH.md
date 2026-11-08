# Deploy หน้าเว็บ TamsoodBase

**อัปเดตชุดต้นน้ำ:** มีpublicsnapshotเฉพาะTables1–3จากบทความCCBY4.0จำนวน42รายการพร้อมattributionที่Vercelผ่าน/upstream-inventory.json ไม่มีrawPDF/ข้อมูลบริษัทเพิ่มในstaticassets ข้อมูลเดิมยังอยู่EC2/MySQL นี่เป็นข้อยกเว้นที่ตรวจสิทธิแล้วจากแผนcode-onlyเดิม ดูevidence/upstream-web-release.json ผู้ใช้ให้browserไม่loginแล้ว ข้อความloginด้านล่างเป็นประวัติ

**สถานะล่าสุด28ตุลาคม: ขึ้น Vercel แล้วที่ https://tamsoodbase.vercel.app** อ่าน [VERCEL_LIVE_TH.md](VERCEL_LIVE_TH.md) สำหรับวิธีล็อกอินและdeployครั้งถัดไป ข้อความด้านล่างเป็นแผน/ประวัติก่อนdeploy ไม่ใช้แทนสถานะล่าสุด Backendยังใช้HTTPS Quick Tunnel และต้องอัปเดตoriginเมื่อURLเปลี่ยน

อัปเดต28ตุลาคม2569: MySQL EC2ใช้งานแล้ว และมี HTTPS test URL พร้อมBasic authenticationทุกrouteตาม docs/HTTPS_TEST_TH.md นี่เป็นsame-origin previewจากEC2 ยังไม่ใช่Vercel deployment และห้ามถือURLชั่วคราวเป็นproduction API origin การเชื่อมVercelข้ามoriginยังต้องออกแบบlogin/CORS/โดเมนถาวร

อัปเดต26ตุลาคม2569: backendบนEC2อัปเกรดเป็นcdc51c36b5356c41และS3configถาวรแล้ว ดูPRIVATE_BACKEND_OPERATIONS_TH.md เว็บรุ่นใหม่จึงใช้ผ่านSSHtunnelได้ แต่ยังไม่มีpublicHTTPSAPI/domain/accesscontrolและยังไม่ได้deployVercel ผล88tests/imageเก่าด้านล่างเป็นประวัติรุ่น24ตุลาคม ไม่ใช่สถานะactiveล่าสุด

อัปเดต24ตุลาคม2569 เว็บเป็น HTML/CSS/JavaScript ไม่ต้องติดตั้ง frontend framework และไม่ต้องมี S3 ก่อนจึงจะ build ได้ มีสองรูปแบบที่เตรียมไว้:

| รูปแบบ | วิธีเรียกข้อมูล | สถานะ |
|---|---|---|
| เว็บและ backend อยู่ด้วยกันบน EC2 | `/api/...` ที่ origin เดียวกัน | รองรับใน Docker backend;รุ่นเว็บใหม่นี้ยังไม่สลับขึ้นEC2 |
| เว็บบน Vercel และ backend แยกที่อยู่ | HTTPS API origin จาก `TAMSOOD_API_BASE_URL` | build/configพร้อม;ยังไม่ได้สร้างdeploymentบนVercel |

## ดูเว็บในเครื่อง

```powershell
python -X utf8 src/explorer.py
```

เปิด `http://127.0.0.1:8765/` ใช้ `web/config.js` ที่ค่า apiBaseUrl ว่าง จึงเรียก API เครื่องเดียวกัน เปลี่ยนเมนูแล้ว URL มี `#reference`/`#eppo` เป็นต้น เมื่อ reload จะกลับหน้าที่เลือก

## Build frontend สำหรับตรวจ/ส่งต่อ

ต้องมี Node.js คำสั่งนี้ไม่มี npm dependencies:

```powershell
node scripts/build_frontend.mjs
```

ได้ `build/frontend/` มีแค่ index.html,style.css,app.js,api.js,config.js,favicon.svg และbuild-manifest.json ไม่คัดลอก raw/SQLite/MySQL/credentials ไปด้วย

เมื่อไม่ตั้ง API origin จะได้แบบ same-origin สำหรับใช้หลัง backend/reverse proxy เดียวกัน ถ้าเปิดด้วย static server อย่างเดียวจะไม่มี `/api` ให้ จึงไม่ควรถือว่าโหลดข้อมูลพร้อมแล้ว

ตัวอย่าง build เพื่อเชื่อม backend แยก:

```powershell
$env:TAMSOOD_API_BASE_URL = 'https://api.your-domain.example'
node scripts/build_frontend.mjs
Remove-Item Env:TAMSOOD_API_BASE_URL
```

แทน URL ด้วยที่อยู่จริงของทีม ระบุแค่ origin **ไม่ต่อ `/api`**,ไม่มีusername/password/query/fragment ต้องเป็นHTTPSยกเว้นlocalhostสำหรับทดสอบในเครื่อง

ไฟล์ config ในbuildเป็นข้อมูลสาธารณะที่browserอ่านได้ ห้ามใส่AWS keys,private key,passwordหรือtokenไว้ในตัวแปรนี้

## ตั้งค่า Vercel

1. เตรียม HTTPS backend ที่ browser ของสมาชิกเข้าถึงได้จริงก่อน
2. ใน Vercel สร้าง project จาก repository ที่เจ้าของพร้อมนำขึ้น โดย Root Directory ใช้rootrepo
3. Framework Preset เลือก **Other**
4. repoมี `vercel.json` กำหนด Build Command = `node scripts/build_frontend.mjs` และ Output Directory = `build/frontend` แล้ว
5. ใน Environment Variables ตั้ง `TAMSOOD_API_BASE_URL` เป็น HTTPS backend origin จริง ทั้งPreview/Productionที่จะใช้
6. ตรวจการจำกัดผู้เข้าถึง deployment ตามความสามารถของ account และนโยบายทีมก่อนใช้กับข้อมูลอ้างอิงภายใน
7. สร้างdeploymentแล้วจดfrontendURLจริง เพื่อนำไปตั้งCORSด้านbackend

BuildบนVercelจะปฏิเสธเมื่อไม่ได้ตั้งAPI origin หรือใช้HTTP/localhost ป้องกันbuildผ่านแต่frontendเรียกAPIที่ไม่มีอยู่เอง

`public:false` ในvercel.jsonจำกัดการเปิดsource/logsตามความหมายของVercel **ไม่ใช่การใส่รหัสผ่านให้เว็บไซต์** การจำกัดผู้เข้าถึงต้องตั้งแยกในprojectตามสิทธิaccount

`.vercelignore` จำกัดไฟล์ต้นทางสำหรับdeploymentไว้เฉพาะwebassets/builder/config และstaticoutputก็มีallowlistอีกชั้น ดู [Vercel configuration](https://vercel.com/docs/project-configuration/vercel-json), [Build configuration](https://vercel.com/docs/builds/configure-a-build) และ [Deployment file allowlist](https://vercel.com/docs/deployments/vercel-ignore)

## ให้ backend ยอมรับ origin ของหน้าเว็บ

backend WSGI รองรับตัวแปรนี้:

```dotenv
TAMSOOD_ALLOWED_ORIGINS=https://your-project.vercel.app
```

ถ้ามีหลายoriginที่ทีมใช้จริง ให้คั่นด้วยcomma ใช้ชื่อเต็มตรงกับbrowser ไม่ใส่pathท้ายชื่อ ไม่ใช้ wildcardเพื่อเปิดทุกpreview และต้องนำenvironmentผ่านขั้นสร้างcontainerรุ่นถัดไป การแก้envfileแล้วrestartเฉย ๆ ไม่เปลี่ยนenvironmentของcontainerเดิม

Export CSV/JSON จะชี้ไปAPI originเดียวกับที่ดึงข้อมูลโดยอัตโนมัติ

**CORS ไม่ใช่ authentication** BackendบนEC2ปัจจุบันผูกloopbackและเข้าผ่านSSH tunnel จึงยังไม่ใช่ปลายทางHTTPSสำหรับVercel และ `127.0.0.1` ของผู้เปิดเว็บหมายถึงเครื่องของผู้เปิด ไม่ใช่EC2 ต้องเตรียมHTTPS/access controlที่เหมาะกับการใช้ภายในก่อน การเปิดfrontendไม่ควรเปิดข้อมูลที่สิทธิแจกจ่ายยังไม่ชัดตามไปด้วย

ขั้นตั้งdomain/HTTPSหรือปรับreverse proxyต้องให้เจ้าของserverตรวจ เพราะเครื่องนี้มีGinder/Caddyเดิมอยู่ ห้ามทับพอร์ต80/443หรือแทนIAM roleเพื่อให้เว็บนี้deployได้

## ตรวจหลังนำขึ้นจริง

- หน้าแรกแสดง5ชุดข้อมูลและสถานะเชื่อมต่อ ไม่ใช่HTMLของหน้า404แทนJSON
- ชุดอ้างอิงโหลด97รายการ/พัก4ตามsnapshotปัจจุบัน และเปิดหลักฐานได้
- EPPOค้นSPRCปี2024ได้12เดือน หน่วยBBL/DAY
- ลิงก์exportชี้ไปbackendจริง ไม่มีlocalhostค้าง
- เปิดจากมือถือ เมนูเปิด/ปิดได้ เลือกหน้าแล้วเมนูยุบ และreloadยังอยู่หน้าเดิม
- backendล่มหรือAPIURLผิด ต้องแสดงerrorและไม่คงตาราง/exportเก่า
- ถ้าข้อมูลหรือsnapshotเปลี่ยน ให้ใช้ยอดจริงในmanifest ไม่ยึดตัวเลขตัวอย่างตลอดไป

การตรวจในเครื่องสำเร็จไม่เท่ากับdeployบนVercelสำเร็จ คู่มือนี้เตรียมconfig/ขั้นตอน ยังไม่ได้push,เผยแพร่หรือเปลี่ยนบริการEC2ให้

ผลตรวจรอบนี้:88testsผ่าน;Dockerimageรุ่นbca514e1c2552315ผ่าน16routes;browserdesktop/mobileและแยกoriginผ่าน ดูevidence/frontend-deployment.jsonและbackend-image-audit.json แพ็กเกจเฉพาะfrontendอยู่build/frontend-static.zipเป็นแบบsame-origin ไม่ใช่URLเว็บที่เผยแพร่แล้ว
