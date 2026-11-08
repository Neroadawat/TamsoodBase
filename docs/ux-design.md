# UX pass — 23 October 2026

เป้าหมาย: ค้นง่าย อ่านง่าย เปิดต้นทางสะดวก บนคอมและมือถือ ใช้เว็บในเครื่องเดิม ไม่เผยแพร่ dataset หรือ deploy

## Reference ที่อ่าน

- [Our World in Data: redesign](https://ourworldindata.org/redesigning-our-interactive-data-visualizations): ใช้แนวคิด contrast ของตาราง, การจัดแนวตัวเลข, ที่มาที่เปิดดูได้ และ download ที่อยู่ใกล้ข้อมูล
- [World Bank Open Data](https://data.worldbank.org/indicator/index): ใช้แนวคิดค้นจากชื่อข้อมูลและเลือกเงื่อนไข พร้อม download ใกล้ผลลัพธ์

เป็นการประยุกต์ interaction และลำดับข้อมูล ไม่คัดลอก code, artwork หรือ branding และไม่อ้างว่าเว็บเราเป็นขององค์กรเหล่านั้น

## ปรับจริง

- หน้าแรกเริ่มที่ reference ที่รับตามนโยบายทีม แยกจาก DMF pending research
- แสดงสถิติ DMF เฉพาะเมนูสำรวจ/คุณภาพ เพื่อไม่ดันตัวค้นหาของ reference ลง
- ปรับตัวอักษร controls/table หลักเป็น 14px พร้อม line-height และ contrast มากขึ้น
- ปุ่มหลักสูงอย่างน้อย44px, focus ring, skip link, dialog accessible name และ aria-current สำหรับเมนู
- ตารางแถวสลับสี/hover, sticky header, เลขและหน่วยอยู่ด้วยกัน
- ข้อจำกัดยาวอยู่ใน details ที่เปิดอ่านได้ ไม่ลบคำอธิบายสิทธิหรือความหมายข้อมูล
- reference มีปุ่มล้างทั้งหมดและ empty state พร้อมคำแนะนำ
- เมนูมือถือ wrap ให้ทุกเมนูเห็นได้ แทนการให้ปุ่มแต่ละอันกว้างเต็มจอในแถบเลื่อน

## ตรวจ

JavaScript syntax ผ่าน Node; explorer tests5ผ่าน ตรวจ browser จริงที่ขนาดปกติและ390×844: หน้า reference โหลด97, ค้นข้อความที่ไม่มีผลแสดง0พร้อมคำแนะนำ, reset กลับ97; บันทึกภาพ build/explorer/ux-desktop.png และ ux-mobile.png การตรวจนี้ยังไม่ใช่ usability study กับคนจริงหรือการรับรอง WCAG ทุกข้อ


## ปรับจาก EPPO — 23 ตุลาคม 2569

ตรวจ https://data.eppo.go.th/Oil ใน browser พบการแบ่งหมวดและ topic พร้อมไฟล์ Current/Month/Quarter/Year; static web reader เดิมแสดง No data จึงไม่ใช้ผลนั้นสรุปว่าไม่มีรายงาน หลักฐาน candidate อยู่ evidence/eppo-catalog-review.json ยังไม่ import ค่าจาก Excel

หน้าเริ่มต้นใหม่เป็น catalog 4 กลุ่ม: DMF, NSO, องค์กร และงานวิจัย ค้นชื่อหรือคำเกี่ยวข้องและกรองระดับได้ แต่ละการ์ดบอกขอบเขต/เวลา/ข้อจำกัดและมีปุ่มไปหน้าเดิม ไม่รวมจำนวนต่างชนิดให้ดูเหมือน accepted เดียวกัน เพิ่มลิงก์ EPPO ในรายละเอียดแหล่งเพิ่มเติมพร้อมป้ายยังไม่ได้นำเข้า

ตรวจจริงใน browser: เริ่ม4ชุด, ค้นดีเซลพบ2ชุด (รวมไบโอดีเซล), เลือกระดับ product พบ1, คำไม่พบแสดงempty state, resetคืน4; ปุ่มNSOเปิดตาราง13.6จำนวน69ค่า/ทั้งชุด273ได้ ตรวจmobile390pxเป็นคอลัมน์เดียวไม่มีhorizontal overflow คืนviewportเดิมแล้ว JS syntaxผ่านและ explorer tests5ผ่าน ไม่อ้างuser study


## รุ่นเตรียม deploy — 24 ตุลาคม 2569

Catalog ปัจจุบันมี5ชุดรวมEPPO (ข้อความ4ชุดในผลทดสอบเดิมเป็นประวัติรุ่นก่อน) รอบนี้เพิ่มปุ่มเริ่มค้นจากหน้าแรก,เมนูมือถือเปิด/ปิดและยุบหลังเลือก,URLhashจำหน้าและรองรับreload/back,ย้ายคำอธิบายheroให้อยู่เฉพาะหน้าแรก และแก้โลโก้/overflowในsidebarเมื่อdesktopแคบ

เพิ่มAPItransportตั้งoriginแยกได้,timeout15วินาที,ข้อความเครือข่าย/HTMLfallbackที่อ่านได้ และexportชี้backendเดียวกัน หน้าแรกโหลดhealthzเป็นคำขอข้อมูลเดียว ชุดใหญ่โหลดเมื่อเลือกหน้าและเก็บผลระหว่างเปลี่ยนเมนูในรอบหน้าเว็บนั้น ไม่อ้างbenchmarkความเร็วเครือข่าย

ตรวจbrowser: desktopcatalog5ชุด,reference97,NSO13.6แสดง69/ทั้ง273,inventory16,ThaiOil48/ปี2024แสดง12,DMF34671pending,EPPOค้นSPRC2024ได้12;mobileviewport390x844 (content375ไม่ล้น),เมนูยุบและreloadจำ#reference

ตรวจแยกoriginจริง: frontendstatic8770เรียกWSGI8766ที่อนุญาตoriginตรง;reference97และexportURLไป8766 เมื่อหยุดAPIแล้วค้นใหม่ ข้อความerrorแสดง,rowsว่าง,exportไม่มีhref จากนั้นปิดแท็บ/เซิร์ฟเวอร์ทดสอบทั้งสอง คืนviewportเดิม คงเว็บlocal8765ให้ผู้ใช้ดู

ดูdocs/FRONTEND_DEPLOY_TH.mdสำหรับVercel/same-origin;ยังไม่ได้publishหรือสลับEC2 ภาพbuild/frontend-ux-desktop.jpgและfrontend-ux-mobile.jpg ไม่อ้างhumanusabilitystudyหรือWCAGcertification

## Catalog ใช้ง่ายขึ้น — 25 ตุลาคม 2569

- กรองระดับด้วยปุ่มที่เห็นตัวเลือกครบพร้อมจำนวนชุดที่ตรงคำค้น แทนdropdownซ้ำกับปุ่ม; countsคือจำนวนdataset ไม่ใช่จำนวนacceptedrecords
- สลับการ์ด/รายการเพื่อเลือกการอ่านที่ถนัด จำเฉพาะlayoutในlocalStorage ไม่เก็บคำค้น; storageถูกบล็อกก็ยังใช้เว็บได้
- เพิ่มคำอธิบายการเลือกระดับประเทศ/องค์กร/ต่อหน่วย พร้อมเตือนเรื่องขอบเขตและการรวมค่า
- สีlabelแยกระดับแต่ยังมีข้อความ ไม่ใช้สีเป็นข้อมูลเพียงอย่างเดียว; aria-pressed/focus/44pxcontrols; ล้างตัวกรองปิดเมื่อไม่มีเงื่อนไข
- ใช้HTML/CSS/JSเดิมเพราะinteractionนี้ไม่ต้องเพิ่มframeworkหรือexternalCDN ยังรองรับstaticbuildและbackendimageเดิม

ตรวจbrowser desktop/mobile390x844: กรององค์กร1ชุด,product1ชุด,referenceเปิด97;listจำหลังreload;mobilecontent375pxไม่ล้น375px;ภาพbuild/catalog-ux-desktop.jpgและcatalog-ux-mobile.jpg เพิ่มdeterministictestของfilter/count/reset/layoutและstorageblocked ผลนี้ไม่ใช่userstudyหรือการรับรองWCAGครบทุกข้อ

## Inventory process context — 27 October 2026
เลือก process/direction ได้ แสดง source basis, geography, publication year แยก data period, boundary/allocation และ product/co-product role ก่อนอ่านค่า ตรวจมือถือ390x844ไม่ล้น; evidence/final-project-recheck.json ไม่มีการคำนวณ allocation เพิ่ม

## Friendly statistics — 5 November 2026
ความชอบที่ผู้ใช้ยืนยันสำหรับเว็บนี้:อีโมจิช่วยสแกนหัวข้อและทำให้การอ่านสถิติไม่น่าเบื่อ ใช้คู่ข้อความเสมอและซ่อนภาพตกแต่งจากscreenreader สีพาสเทลรองรับหมวดแต่ไม่แทนlabel. อ้างแนวทาง ONS icons/colours และโครงสร้างหัวข้อ Our World in Data energy mix (URLsในevidence/friendly-statistics-ux.json). ไม่คัดลอกแบรนด์หรือข้อมูลเพิ่ม;summaryนับrecords/ปี/หน่วยจากrowsจริง EPPOระบุcurrentpage ไม่รวมquantities ไม่มีframework/CDNใหม่. Browserและtest evidenceไม่ใช่userstudy.

## Fuel story — 5 November 2026
ผู้ใช้ระบุอยากได้ภาพเล่าเรื่องที่เลื่อนแล้วเห็นเส้นทางทีละช่วง แทนเพียงhover/press. ใช้originalSVG+sticky+IntersectionObserverตามแนวคิดThePudding/Scrollama ไม่เพิ่มlibraryในproductionเพราะ5ฉากทำด้วยbrowserAPIได้. แยกภาพconceptualpetroleumจากกรณีB100 ไม่วาดให้ดูเหมือนlinkedLCIพร้อมคำนวณ. บทอ่านและลิงก์ยังใช้ได้ถ้าobserverไม่มี;เลขช่วงเป็นnativebuttonใช้keyboardได้;reducedmotionเปลี่ยนทันที. Local/liveheadlessChromeภาพและผลอยู่evidence/fuel-story-ux.json.

## Thai readability and coverage map — 5 November 2026
NotoSansThaiฝังWOFF2จากgoogle/fontsพร้อมOFL1.1ในCSS ลดความต่างของThai glyphsระหว่างเครื่อง ไม่เรียกthirdpartyfontตอนรัน. Body16px/story18px ใช้สีเข้ม. Categorymap5หมวดและcoveragecaptionบอกสิ่งเปิดดูได้จริง ไม่สร้างข้อมูลหรือclaimครบวงจร. Scrolltruck/progressใช้passivescroll+1queuedrAFพร้อมhidden/reducedmotionguard. Samplecontrast/local-live320/390และภาพอยู่evidence/story-readability-ux.json.
