# ใช้ข้อมูลโรงสกัดไทยตามปริมาณ CPO ที่เลือก

4พฤศจิกายน2569 — ต่อจากTableS2ปี2019ที่ตรวจครบ90ช่อง ดูthai-mill-alternative-2019.md

## สิ่งที่เพิ่ม

`python -m scripts.scale_thai_mill --mill 1 --cpo-kg 500`

เลือกโรงงาน1–6เพียงแห่งเดียวและปริมาณCPOเป็นkg ใช้สูตร `scaled_amount = source_amount × requested_CPO_kg / 1000` ตามreferenceoutput1000kgCPOในต้นฉบับ คงraw/sourcepayloadทั้ง15แถวไว้ในผลลัพธ์ แยกscaled_amountจากsource_amount ไม่มีการหารด้วยallocationหรือคูณcredit

ตัวอย่าง500kgCPOสำหรับMill1:FFB3465kg,Water0.520m3,TreatedPOME1.55m3 เป็นตัวอย่างปรับฐานจากข้อมูลที่รายงาน ไม่ใช่การวัดการผลิต500kgจริง และtreatedPOMEไม่ใช่น้ำเสียก่อนบำบัดหรือemissionสู่น้ำ ไม่มีการนำไปคำนวณCO2e

ไฟล์ผลลัพธ์build/thai-mill-2019-scaling/mill-1.jsonมีrequest_class/result_type/rightsและfull_lifecycle_inventory=falseชัดเจน คำสั่งครั้งถัดไปสำหรับmillเดียวกันเขียนทับdemonstrationไฟล์นี้ จึงไม่ใช้เป็นimmutableversionarchive

CLIตรวจhash/extractorsของPDFก่อนคำนวณ ไม่อ่านbuildJSONที่อาจถูกแก้โดยไม่ตรวจต้นทาง ปฏิเสธmillสมมติ/ค่าเฉลี่ย,ค่าติดลบ/ศูนย์/NaN/Infinity,ข้อมูลเกินขอบเขตเลขทศนิยม,referenceproduct/unit/hashไม่ตรง หรือsourceแถวหาย ใช้Decimalprecision100สำหรับค่าที่จำกัดขนาดแล้ว

## ผลตรวจ

15testsผ่านจากtests.test_mill_inventory_scaling,tests.test_thai_mill_2019,tests.test_lifecycle_model รวม3testsใหม่ ตรวจทุกโรงงาน×15แถวว่าฐาน1000kgตรงต้นฉบับและฐาน1.25kgคำนวณย้อนกลับได้ทุกค่า เก็บsourcepayloadเท่าเดิม พร้อมทดสอบการปฏิเสธฐานผิด/ข้อมูลหาย/เลขไม่เหมาะสม ไม่มีการอ้างว่า15testsเป็นfullsuiteทั้งหมด

หลักฐานevidence/thai-mill-scaling.jsonบันทึกhashผลdemonstration500kg ไฟล์ต้นฉบับและสิทธิยังNOT_CLEARED ไม่เพิ่มpublicexport/API/deploy

## ค้นส่วนที่ขาดต่อ

- อ่าน[รายงานEFBสุราษฎร์ธานี2019จากผู้พิมพ์](https://www.jstage.jst.go.jp/article/jie/98/5/98_119/_pdf/-char/en) DOI10.3775/jie.98.119 แล้ว:physicalsampleเป็นไทย แต่Section2.3ใช้IDEAv2สำหรับขนส่ง/ผลิตไฟฟ้าและIPCCdefaultsสำหรับการสลายตัว จึงไม่รับเป็นค่าปล่อยที่วัดในไทย นอกจากนี้พบdensity0.118ในmethod/0.117ในresult และค่าCO2eในabstract/resultsแตกต่างกัน ต้องตรวจหากนำมาประเมินภายหลัง ไม่มีการนำตัวเลขจากรายงานนี้เข้าinventory
- พบวิทยานิพนธ์ผู้วิจัยปาล์มไทยที่WUR https://edepot.wur.nl/400393 แต่ดาวน์โหลดไม่สมบูรณ์ WindowscurlตรวจTLSได้แต่หมดเวลาก่อนครบ และserverไม่รองรับresume จึงเก็บชื่อsource.pdf.partialพร้อมmanifestINCOMPLETE_DO_NOT_USE ไม่อ้างว่าได้fulltextหรือhashของไฟล์สมบูรณ์
- บทความการผลิต/ใช้PME DOI10.1504/IJGW.2009.029213 ยังเปิดpublisherfulltextไม่ได้(403) ไม่รับตัวเลขจากabstractเข้าโมเดล

ตัวปรับฐานนี้ยังไม่ปิดcompatibilityระหว่าง2019CPOกับ2020FAME ไม่สร้างnationalaverageหรือcompleteLCIจากการปรับหน่วย ส่วนThaiNationalLCIยังพักตามผู้ใช้เพราะสมัครไม่ได้ ไม่รอการอนุมัติMTECเป็นblocker
