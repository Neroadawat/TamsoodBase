# เว็บ HTTPS สำหรับทดสอบภายในทีม

28 ต.ค. 2569 ผู้ใช้เลือก HTTPS ชั่วคราวพร้อมรหัสเข้า โดยยังไม่มีโดเมนถาวร

URL ปัจจุบันดู `evidence/https-test.json` ข้อมูลเข้าใช้งานอยู่ในไฟล์ส่วนตัว `.local/HTTPS-ACCESS.md` ห้าม commit/แชร์ไฟล์รหัสต่อสาธารณะ เมื่อเปิด URL เบราว์เซอร์จะถาม username/password

## เส้นทางจริง

Browser → HTTPS ของ Cloudflare Quick Tunnel → authenticated gateway บน EC2 `127.0.0.1:18766` → API `127.0.0.1:8765` → MySQL ภายใน

- ทุกหน้า รวม health, API และ export ต้องใช้รหัส ไม่มี anonymous data endpoint
- เก็บ password hash แบบ PBKDF2-SHA256 600,000 รอบใน gateway และไม่ส่ง Authorization ต่อให้ API
- gateway และ tunnel เป็น container ใหม่ของโครงการ ไม่แก้ Ginder/Caddy, Security Group, IAM หรือพอร์ต 80/443
- พอร์ต MySQL และ origin API ไม่เปิดสาธารณะ S3 ยังเป็น private
- TLS certificate ถูกตรวจตามปกติ ไม่ใช้ตัวเลือกข้ามการตรวจ certificate

นี่เป็นการทดสอบเว็บและ API จาก EC2 origin เดียวกัน ยังไม่ใช่ frontend ที่ publish บน Vercel และไม่ควรใช้ URL นี้เป็น production API origin ของ Vercel

Quick Tunnel URL อาจเปลี่ยนหลัง restart และไม่มี uptime guarantee ตาม [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/) การใช้งานถาวรควรใช้โดเมนและระบบยืนยันตัวตนที่เหมาะกับผู้ใช้จริง

## ตรวจและหยุด

บน EC2 ตรวจเฉพาะ container ของเรา:

```sh
docker ps --filter name=tamsoodbase-https
```

หยุดลิงก์ทดสอบ:

```sh
docker stop tamsoodbase-https-tunnel tamsoodbase-https-gateway
```

ไม่ต้องหยุด API/MySQL และห้ามแตะ Caddy ของเพื่อน หากต้องเริ่มใหม่ ให้ตรวจ URL ใหม่จาก log ของ tunnel และตรวจ 401/200 อีกครั้ง รหัสใน browser ถูก cache ไว้; ถ้าต้องการทดสอบแบบไม่มีรหัส ให้ใช้หน้าต่างส่วนตัวใหม่

## หลักฐาน

`evidence/https-test.json`: ไม่ล็อกอิน/รหัสผิดได้ 401; ล็อกอินได้ 200 และ reference total 97; บริการอื่นไม่เปลี่ยน

`tests/test_private_gateway.py`: ทดสอบป้องกันทุก route, malformed/wrong credentials, ไม่ส่ง Authorization upstream, บล็อก write methods และ HEAD ไม่มี body
