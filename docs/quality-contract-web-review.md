# โปรไฟล์คุณภาพและหลักฐานบนเว็บ — 30 ตุลาคม 2569

## ผลที่ขึ้นจริง

Vercel deployment `dpl_BSZ6yCPZUmiHXzJT7RBDcsqmdbCM` ที่ https://tamsoodbase.vercel.app/#inventory แท็บต้นน้ำแสดง:

- ขอบเขตที่มีข้อมูล และการใช้งานที่รองรับก่อนตาราง
- คุณภาพแยกต้นฉบับ/เวลา/พื้นที่/ความครบถ้วน/การตรวจวัดใหม่/สิทธิ
- ส่วนที่ยังไม่นำเข้า โดยระบุว่าไม่ใช่ข้อสรุปว่างานวิจัยต้นฉบับไม่มีส่วนนั้น
- source-public-snapshot identifier เดียวกันในหน้าเว็บและ JSON export;เป็นรุ่นข้อมูลต้นน้ำ ไม่ใช่รุ่น backend ทั้งระบบ
- modal ค่าดิบคู่ค่าที่ระบบเก็บ หน่วย null คงเดิม วิธีแปลงเลข และลิงก์เว็บไซต์/PDFหน้าตาราง พร้อมชี้ว่าไม่ได้เน้น cell อัตโนมัติ

ข้อมูลตัวเลข42รายการและสถานะ1HOLDคงเดิม ไม่มี provider/การปันส่วนที่นำมาใช้ ไม่มีข้อมูลบริษัท/rawPDFเพิ่มในstaticbuild ไม่ได้เปลี่ยนMySQLบนEC2

## การตรวจที่เกิดจริง

- 155 unit/behavior tests ผ่าน; browser local ตรวจ CPO12และdownloadครบทุกfield/profile/version
- browser production ตรวจFFB19/modalmissingunit/ค่าดิบคู่ค่าจัดเก็บ/ปิดด้วยEscape/downloadจริงอ่านกลับครบ19rows
- local390px:documentwidth375 ไม่มีการล้นหน้า;ปรับการ์ดคุณภาพเป็น1คอลัมน์เมื่อ≤600px
- HTTP app.js/style.css/publicJSONตรงbuild;API27routesเทียบbaselineผ่าน;exportยังเข้าถึงได้ตามนโยบายผู้ใช้โดยเก็บupstreamsecretเฉพาะserver
- หลักฐาน `evidence/current-frontend-release.json`, `evidence/vercel-deployment.json`, ภาพ `build/ux-verification/quality-contract-live.png`

## จุดแก้ proxy ที่พบจริง

`api/[route].js` เดิมไม่มีเพดาน streaming export เพิ่ม32MiBตามbytesจริงและadvertisedContentLength; JSONbufferเดิม4MiBคงไว้แต่เพิ่มการป้องกันตอบerrorซ้ำ;HEADไม่ส่งbody การส่งเกินเพดานระหว่างเริ่มstreamแล้วต้องตัดconnectionแทนเปลี่ยนHTTPheadersกลางstream ทดสอบ server-onlysecret/read-only/allowlist/HEAD/oversizeก่อนdeployแล้ว

เพดานนี้ไม่รับประกันเพดานresponseของแพลตฟอร์มVercelทุกแผนและไม่ใช่rate limiter;ไม่ป้องกันquerycostในupstreamหรือพิสูจน์loadcapacity ยังต้องวัดเมื่อมีworkloadและข้อกำหนดจริง ไม่ทดสอบloadบนserverเพื่อนโดยพลการ

## ตรวจย้อนกับคำวิจารณ์

ข้อ5/7/8/9 มีการปรับเว็บและexportจริง;ข้อ11/12มีresponseboundและnegativechecksเพิ่ม ไม่ถือว่าsecurityauditครบทุกจุด ส่วนsource-scientific/modelreadinessยังไม่ผ่านเพราะallocation/FFB/backgroundไม่ครบ

Release checker พบSRS.mdเปลี่ยนเป็น0.6ขณะทำงาน แต่PDF evidenceยัง0.5 จึงรายงาน `srs_markdown_matches_rendered_source=false` อย่างถูกต้อง ไม่เขียนทับงานเอกสารที่กำลังแก้ ไม่เปลี่ยนผลให้ผ่านเพื่อประกาศfinalfreeze

ต่อมาแก้ความคลาดเคลื่อนด้วยการrenderสำเนาSRS0.6แยก ตรวจcontactsheetครบ21หน้าและภาพreferencesหน้า4 แล้วตรวจhashว่าMarkdownต้นฉบับยังตรงสำเนาก่อนpromotePDFเท่านั้น ไม่แก้เนื้อหาMarkdown เก็บPDFเก่าในoutput/pdf/archive/ หลักฐานใหม่evidence/srs-current-review.json;releasecheckerกลับผ่าน แต่ยังเป็นDRAFT_TEAM_REVIEW_PENDING ไม่ใช่สมาชิกอนุมัติหรือส่งFinalแล้ว

## แหล่งใหม่ที่ตรวจเพิ่ม

พบ PDF20หน้าจากNRCTชื่อข้อเสนอเชิงนโยบายปาล์มน้ำมัน เก็บhashและตรวจภาพหน้า9(พิมพ์หน้า7) มี oil extraction yield ที่อ้างบริบทปี2013 แต่ไม่ยืนยันว่าเป็นinventoryชุดTables1–4หรือcalculationreportที่ใช้allocation จึง **ไม่ใช้ย้อนคำนวณFFBinput** และไม่เพิ่มobservations ดู `evidence/nrct-policy-review.json` rawเก็บprivate/สิทธิแจกจ่ายยังไม่ยืนยัน

แหล่ง: https://explore.nrct.go.th/file_upload/submitter/file_upload/6083b66b616de8ed195a79b0d6ca6251a46f42cb1173c9ac.pdf
