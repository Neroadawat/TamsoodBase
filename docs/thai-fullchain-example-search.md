# คัดเลือกตัวอย่าง LCI เชื้อเพลิงไทยสำหรับเดโม — 6 พฤศจิกายน 2026

## ผลตัดสินใจ
พบงานศึกษาทั้งสายจริง โดยแนะนำเอทานอลมันสำปะหลัง/E10 และเอทานอลกากน้ำตาล/E10 ปี2008สำหรับขอฉบับเต็ม ไม่ได้ยืนยันว่ามีไฟล์LCIครบทุกflowที่นำเข้าฐานเราได้แล้ว งานเปิดWTWปี2025ใช้เล่าขอบเขต/วิธีวิเคราะห์ได้ทันทีในฐานะงานอ้างอิง แต่ไม่เรียกfullLCIdatasetของเรา

## แหล่งที่คัดกรอง
| กรณี | สถานะ | ข้อจำกัด |
|---|---|---|
| [เอทานอลมันสำปะหลังไทย / E10](https://link.springer.com/article/10.1065/lca2007.06.343) | WTW_STUDY_CONFIRMED_FULLTEXT_PENDING | Subscription;ThaiScience link returns lander HTML;no verified full inventory |
| [เอทานอลกากน้ำตาลไทย / E10](https://link.springer.com/article/10.1007/s11367-008-0011-2) | FULL_CHAIN_STUDY_CONFIRMED_FULLTEXT_PENDING | Publisher subscription;university mirror TLS EOF/reader timeout;upstream CH4/waste discussed but selected inventory not verified |
| [เส้นทางเชื้อเพลิงรถยนต์ไทย](https://www.iieta.org/journals/ijsdp/paper/10.18280/ijsdp.200306) | OPEN_METHOD_DEMO_NOT_COMPLETE_LCI | Full PDF11pages;CCBY4.0;method references and results not downloadable complete elementary inventory;imported electricity excluded in source |
| [จัดการน้ำมันทอดใช้แล้วในบริบทไทย](https://doi.org/10.1016/j.jenvman.2022.114810) | INVENTORY_TABLES_AVAILABLE_BOUNDARY_INCOMPLETE | PDF33pages;upstream generation/collection/transport excluded;foreign literature+ecoinvent;notThai-only background;repositoryCCBYNCND;public redistribution not cleared |
| [เอทานอลกากมันสำปะหลังไทย](https://doi.org/10.1016/j.jclepro.2020.124741) | PROMISING_PRODUCTION_AND_USE_STUDY_ACCESS_PENDING | Publisher403;do not import numerical abstracts asLCI |
| [เชื้อเพลิงทางเลือกไทย WTW](https://www.scientific.net/AMR.524-527.2538) | WTW_MODEL_CANDIDATE_INVENTORY_UNAVAILABLE | Publisher abstract;Thailand adaptedTsinghuaCA3EM;not allThai underlyingparameters verified |
| [CNGไทย รถขนส่งเทียบท่อ](https://ilcaj.org/EcoBalance2014/program/files/EcoBalance2014_abstract.pdf) | ABSTRACT_ONLY_BOUNDARY_CONFLICT | WTW introduction but WTT methods;ThaiLCI+ecoinvent background;not complete machine readable inventory |
| [ไบโอดีเซลปาล์มไทย2013](https://doi.org/10.1007/978-3-642-34519-7_2) | EXISTING_FULL_CHAIN_CANDIDATE_BASIS_CONFLICT | Already reviewed;do not repeat extraction;selected use/waste data internal only |
| [ไบโอดีเซลไทย2020](https://doi.org/10.3390/su12229415) | EXISTING_PRODUCTION_INVENTORY_NOT_FULL_LIFECYCLE | Existing52foreground observations;do not promote tofull bypaper title |
| [โรงงานไบโอดีเซลไทย5แห่ง](https://digital.car.chula.ac.th/chulaetd/18075/) | PRODUCTION_WASTE_ONLY_NOT_FULL_CHAIN | Institutional abstract;not transport/use complete;CCBYNCND stated |

## ตัวอย่างที่เล่าได้โดยไม่แต่งข้อมูล
เส้นทางเอทานอลไทย:ปลูกวัตถุดิบ→ผลิต/สกัด→แปรรูปเอทานอล→ขนส่ง/ผสมE10→ใช้ในรถ พร้อมแขนงบำบัดของเสียระหว่างการผลิต ภาพนี้เป็นแผนการเล่าขอบเขต ไม่ใช่processnetworkที่มีปริมาณครบแล้ว
การเผาไหม้เป็นการใช้และสิ้นสุดตัวเชื้อเพลิง ไม่จำเป็นต้องสร้างขั้นรีไซเคิลเชื้อเพลิงหลังเผาให้ครบ5กล่อง;ของเสียระหว่างผลิตต้องระบุที่เกิดและการบำบัด ส่วนการผลิต/ซากรถเป็นอีกขอบเขตหนึ่ง
ควรโชว์FU,systemboundary,processchain,แหล่งแต่ละขั้น,ข้อที่ตัดออก,ตารางLCI,วิธีallocation,ผลLCIAแยกจากphysicalflow และลิงก์ต้นฉบับ ไม่ใช้เปอร์เซ็นต์ลดGHGแทนLCI

## หลักฐานใหม่ที่ได้จริง
ดาวน์โหลดUCO2022และWTW2025เก็บprivate;hashในevidence ตรวจหน้าขอบเขตPDF5ของแต่ละไฟล์ด้วยpdfplumber+pypdfและภาพrenderแล้ว ไม่อ้างว่าตรวจครบทุกช่องของTable1–2
UCO2022ตัดcollection/transport/upstreamออกและใช้literatureต่างประเทศ จึงไม่เหมาะเป็นfullThai-onlyexample;WTW2025มีข้อยกเว้นไฟฟ้านำเข้า ไม่ถือว่าผลเป็นค่าเฉลี่ยประเทศที่ครอบคลุมทุกแหล่งโดยไม่มีข้อจำกัด

## สิ่งที่ต้องได้ก่อนนำเข้าเป็นกรณีคำนวณจริง
ขอPDFสองงานเอทานอลผ่านสิทธิห้องสมุดมหาวิทยาลัยโดยผู้ใช้ล็อกอินเอง ไม่ซื้อหรือส่งรหัสผ่าน แล้วตรวจทุกfield/หน่วย/locator/ปี/ขอบเขต/ผลพลอยได้/ของเสีย/CH4N2O/backgroundและสิทธิ ก่อนทำตัวอย่างเชื่อมครบตามขอบเขตที่เลือก
ไม่พบหลักฐานเพียงพอในรอบนี้ให้รับรองdownloadableครบทุกflow+Thai-onlyทั้งbackground จึงไม่มีnumericimportและไม่แก้fullLCIflag การค้นครอบคลุมหลายกลุ่มเชื้อเพลิงแต่ไม่อ้างค้นหมดอินเทอร์เน็ต

หลักฐาน: evidence/thai-fullchain-example-search.json
