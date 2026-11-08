# ผลดำเนินการตามรีวิว 15 ข้อ — 6 พฤศจิกายน 2569

งานวิศวกรรมที่ทำได้ถูกส่งมอบพร้อมหลักฐาน ส่วน science, stable hostname และ human review ไม่ได้ถูกปิดด้วย UI หรือ fixtures.

| ข้อ | สิ่งที่แก้และตรวจ | สถานะจริง |
|---|---|---|
|1 Route/focus|หน้าใหม่ focus H2/top0; back คืน filters และ scroll; story jump ยังใช้ได้|local/live browser ผ่าน|
|2 URL filters|NSO table/year/q validated ใน URL; reload/share/back คงดีเซล2024สองค่า|ส่งเว็บแล้ว;ยังไม่ขยาย URL contract ทุก dataset|
|3 Mobile hierarchy|แสดง count/activefilters ก่อน; filters ยุบมือถือ; summary รองท้ายตาราง; keyboard details|320x600/390ไม่ล้น;ไม่ใช่ UAT มนุษย์|
|4 Capabilities|5 cards บอกอ่านอะไร/metadata only/ปริมาณบริษัทไม่เปิดเผยก่อนกด|ส่งเว็บแล้ว ไม่สร้าง CSV ปริมาณที่ถูกปิด|
|5 Comparison|เลือก2 NSO records แม้เปลี่ยน filter;ตรวจ table/unit/measure/geography/year/agency|ส่งเว็บแล้ว ไม่มีการหาร/รวม/LCIA;ไม่รับรอง compatible LCI|
|6 Menu|quality/reports/sources รวมในเครื่องมือตรวจสอบ เปิดเองเมื่อ active|ส่งเว็บแล้ว โดยยังเข้าถึงหลักฐานได้|
|7 Maintainability|แยก discovery.js/story.js/theme.css และ tokens; explicit source allowlists/local static routes|incremental refactor ไม่อ้างย้าย framework หรือ rewrite core ทั้งหมด|
|8 Fonts/assets|hashed WOFF2/OFL/selfhost/preload; immutable cache เฉพาะ font; CSS แยกจาก base64|live hash/Cache-Control ตรวจจริง;private API ยัง no-store|
|9 A11y/UAT|axe WCAG tagged checks3หน้า/keyboard/reducedmotion/mobile;แก้ footer/side contrast และ role group หลัง dynamic render|automated ผ่าน;ยังมี incomplete manual checks/ไม่มี certification หรือ human UAT|
|10 LCI scope|อ่าน gate evidence/ค้นอย่างมีขอบเขต; API full=false/CO2e=null/eligible elementary0 คงเดิม|OPEN: table allocation basis, elementary/CF, independent balance|
|11 Compatibility|คง6 gates ไม่แทน missing ด้วย0/ไม่ใช้ old transport/use เชื่อม model2020เอง|OPEN: matched Thai use/transport/waste/background และ rights;0 new numeric imports|
|12 Workflow|local SQL/Python draft-review-publish-retract;actor/role/hash/reason/revision guard;append-only events|candidate/testsเท่านั้น ไม่ใช่ authenticated production multiuser service ไม่สร้างผู้ตรวจจริง|
|13 Numeric/schema|130 source+330 results→DECIMAL(65,30)แยก;453eligible/7excluded;MySQL8.4.13ครบ460/ORDER BY/negative3819|candidateไม่round ไม่แก้ sealedDB ไม่ migrate EC2 ไม่อ้าง5NFทั้งระบบ|
|14 Operations|owner check;fresh5schema S3 AES256;restore isolated MySQL;ordered logical rows56,887,016bytes/hashตรง live|backup/restoreผ่าน;QuickTunnelยังtemporary ไม่มีauto schedule/wholeEC2 DR/loadtest|
|15 API|NSO433169→146019bytes;hydrate273ทุกfieldตรง;client35s/proxy30s;staleEPPOabort;concurrent statusไม่ล้าง error ชุดอื่น|live/behavior tests ผ่าน ไม่อ้าง SLA/Core Web Vitals|

## ผลตรวจและหลักฐาน

Full suite226 testsผ่านไม่มีskip;หลังแก้ aria role เพิ่ม targeted15tests และ axe dynamic case-study ซ้ำ. Browser local/live route focus, filter reload/history, comparison, keyboard details, mobile320/390/reducedmotion ไม่มี pageerror.

- evidence/review-implementation-2026-11-06.json: manifest ผลส่งมอบ
- evidence/nso-compact-transport.json:273rowsทุกfield;default API เดิมคงสัญญา
- evidence/decimal-projection.json:460rows MySQL engineจริงในคอนเทนเนอร์ของงานนี้ ลบหลังตรวจowner ไม่มีsharedDBเปลี่ยน
- evidence/mysql-backup-2026-11-06.json และ mysql-restore-2026-11-06.json: backupใหม่จากprivateS3/hashตรง/liveครบ5ฐาน
- evidence/operational-readiness-2026-11-06.json: HTTPhealthy/backupfresh แต่ permanent endpointยังไม่ครบ;exit2เป็นข้อค้างจริง
- Public cleanroom17sourcefiles/14assets ไม่รวมraw/private/credentials;deployและrollbackอยู่evidence/current-frontend-release.json

## วิทยาศาสตร์: ตรวจเพิ่มอย่างมีขอบเขต
ค้นThai FAME allocation/useสองqueries พบ DOI10.1016/j.spc.2025.04.023และDEDE agricultural B100ที่เคยอยู่candidateแล้ว ไม่เพิ่มแหล่งซ้ำ/ไม่promote snippet. DOIทางการredirectเปิดไม่ได้;GDcatalogระบุโครงการ2559และCCNonCommercial(any) ไม่ใช่หลักฐานmatched2020หรือสิทธิแจกจ่ายใหม่. ไม่มี numeric imports/allocation/provider factor ใหม่. ยึดevidence/fame-gate-closure-review.jsonเป็นรายการหลักฐานที่ต้องมี.

## ข้อค้างที่ปิดเองไม่ได้

1. Table-specific gross/allocated basis; matched Thai use/transport/background/waste; elementary mapping/CF/independent balance.
2. Stable hostname ที่ทีมควบคุม;ไม่ซื้อdomain/แตะGinder/Caddy/SG/สร้างautomationเอง.
3. Independent human reviewer, UAT/screenreader/manual accessibility, ข้อมูลสมาชิก/contribution/consent/final approval.
4. Production workflow/migrationต้องสิทธิ/identity/grants/rollbackจริง;local fixtureไม่ใช่ผู้ใช้หรือการรับรองวิทยาศาสตร์.

## ข้อผิดพลาดระหว่างทำงาน

ชุดทดสอบพบ fixture allowlist และ AbortController stub เก่า แก้แล้ว full226ผ่าน. Live axe พบ aria-label บน div ไม่มี role หลัง B100โหลดครบ แก้ role=group และรอ dynamic content ก่อน audit. ไดรฟ์พื้นที่ต่ำทำให้เขียนรายงานครั้งแรกไม่ครบ จึงลบเฉพาะสำเนา archive ชั่วคราวของการ restore รอบนี้หลังยืนยันS3/hashแล้วและเขียนเอกสารใหม่ ไม่ลบงานอื่น. พื้นที่ไดรฟ์ยังต่ำ เป็นข้อจำกัดเครื่องพัฒนาไม่ใช่ข้อมูลproductionเสีย.
