# แหล่งบำบัดน้ำเสียปาล์มไทย: Lamthap — 6 พฤศจิกายน 2026

## ผลที่นำไปใช้ได้ตอนนี้
พบโครงการ Univanich Lamthap POME Biogas หมายเลข CDM2076 ที่กระบี่ แหล่งผู้ดำเนินโครงการอธิบายระบบบ่อปิด CIGAR เก็บก๊าซไปผลิตไฟฟ้าและใช้ตะกอนในแปลง เหมาะกับการศึกษาช่วงจัดการน้ำเสียของสายปาล์ม→B100 แต่ไม่ใช่หลักฐานว่าครอบคลุมวัฏจักรชีวิตทั้งหมด และไม่ใช่ข้อมูลระดับประเทศ

- ทะเบียนโครงการ: https://cdm.unfccc.int/Projects/DB/TUEV-SUED1218475905.14/view
- เอกสาร monitoring2013: https://cdm.unfccc.int/UserManagement/FileStorage/02MGH4OW7TB9I8P6QSRDKCAULFEVX3
- ผู้เกี่ยวข้อง: https://www.myclimate.org/en/get-active/climate-protection-projects/detail-climate-protection-projects/thailand-biogas-7140-7170/

## การตรวจและการตัดสินใจ
Web reader เคยอ่านเนื้อหา27หน้าได้ แต่ดาวน์โหลดโดยตรงได้HTML212bytesแทนPDF และการเปิดซ้ำภายหลังล้มเหลว จึงยังไม่มี rawPDF/hash/dual-parser/visualverification ห้ามใช้ข้อความที่อ่านได้เป็น source-cell verified หลักฐานตัวเลขทั้งหมดในJSONเป็น candidate ที่ยังไม่เข้า inventory

พบข้อสงสัยจากข้อความที่สกัด: baseline38041−project8652−leakage0=29389 แต่ reductionรายงาน21131 ต่าง8258tCO2e ยังแยกไม่ได้ว่าเป็นข้อผิดพลาดต้นฉบับ เวอร์ชัน หรือการสกัดข้อความ จึงไม่แก้ค่าให้ตรงเอง พบหน่วยไฟฟ้าMWhกับค่าขนาด7279537และคำอธิบายkWhที่ต้องเปิดภาพตรวจเช่นกัน

## กฎใช้ข้อมูลที่ต้องรักษา
1. รายงานผลลดก๊าซ/CER ไม่ใช่ elementary emission และไม่ใช่ผลCO2eของผลิตภัณฑ์
2. GWPมีเทน21ในวิธีเก่าต้องรักษา method/version ไม่รวมกับวิธีปัจจุบันโดยอัตโนมัติ
3. ก๊าซที่เกิด เก็บได้ เผาทำลาย และรั่ว เป็นคนละ flow; pipeline loss0% ไม่เท่ากับทุกการรั่วเป็นศูนย์
4. ต้องได้CPOoutputและขอบเขตเดียวกันก่อนแปลงต่อkgCPO และต้องมี compatibility bridge ก่อนเชื่อมโรงงาน/ปีอื่น
5. annual meanCOD×annualflowเป็นประมาณการได้เมื่อระบุสมมติฐาน ไม่ใช่ integratedloadที่วัดตรงโดยอัตโนมัติ
6. ไม่ใช้โครงการนี้แทน end-of-life ของเชื้อเพลิงโดยตรง: เป็นน้ำเสียจากการผลิตปาล์ม ส่วนการเผาไหม้B100/น้ำมันหล่อลื่น/การกำจัดอื่นต้องแยกขอบเขต

## สิ่งที่ยังต้องทำ
หาฉบับรายงานที่ดาวน์โหลดเป็นPDFจริงหรือฉบับแก้ไขจากเจ้าของโครงการ แล้วตรวจทุกช่องที่เลือก/หน่วย/locator/ยอดสรุป ก่อนรับตัวเลข หากไม่ได้ให้คงHOLD ไม่วนURLเดิมโดยไม่มีเบาะแสใหม่ ไม่เปลี่ยนbaseline ไม่เผยแพร่raw ไม่อ้างfullLCI

หลักฐาน: evidence/thai-lamthap-candidate-review.json ไม่มีการแก้productionหรือคำนวณCO2eรวมในรอบนี้

## ตรวจประวัติฉบับแก้ไขเพิ่มเติม — 6 พฤศจิกายน 2026
ตรวจหน้าประวัติการออกเครดิต (issuance request SIRIM1402397031.65) พบสถานะIssuedวันที่22May2015 ยอด40326CER และเอกสารเพิ่มเติมชื่อ **UNV MR Lamthap FormV.4 Jan15** พร้อม **UNV Lamthap ER V4 (Jan2013–Dec2013)11Feb15** และverification report

จึงแก้ข้อสรุปให้แม่นยำขึ้น: ตัวเลข21131มาจากVersion01 completion1/5/2014 ส่วนทะเบียนมีหลักฐานว่ามีฉบับแก้ไขภายหลัง แต่ยังไม่ทราบว่าแก้ค่าใดบ้าง ความต่างของยอดจึงเป็น **ข้อสงสัยที่ต้องเทียบเวอร์ชัน** ไม่ใช่ข้อยืนยันว่ารายงานฉบับสุดท้ายผิด ไม่แทน21131ด้วย40326เอง

ลองดาวน์โหลดลิงก์ใหม่ของV4และverificationจากทะเบียนโดยตรง ได้HTTP200แต่เป็นHTML850/844bytes ไม่ใช่PDF;webreaderเปิดเอกสารใหม่ไม่สำเร็จ ไม่บันทึกHTMLเป็นPDFหรือสร้างhashPDFขึ้นเอง ไม่ฝ่าระบบป้องกันของเว็บ

แหล่งประวัติ: https://cdm.unfccc.int/Projects/DB/TUEV-SUED1218475905.14/iProcess/SIRIM1402397031.65/view

### ข้อกำหนดรับข้อมูลที่เพิ่มจากสิ่งที่พบจริง
- ระบุตัวตนเอกสารด้วยproject+monitoringperiod+version+completiondate+hash ไม่ใช้เพียงชื่อโครงการ/ปี
- ทุกค่าต้องผูกกับเวอร์ชันของตัวเองจนกว่าจะทำfield-by-fielddiffกับฉบับแก้ไข
- สถานะIssuedของโครงการไม่ใช่การรับรองว่าแถวLCIของเราถูกต้อง และไม่เปลี่ยนสิทธิแจกจ่าย
- ลำดับถัดไปคือrawV4+verification+calculations แล้วตรวจทุกfieldที่เลือก/ฐานCPO ไม่ค้นหรือโหลดลิงก์เดิมวนจนมีวิธีเข้าถึงปกติหรือเอกสารใหม่

ผลรอบนี้: **ไม่เพิ่มแถวตัวเลขในinventory** แต่ค้นพบrevisionที่จำเป็นและป้องกันการใช้ฉบับเก่าข้ามเวอร์ชัน ไม่แก้เว็บ/EC2/ค่าbaseline

## ตรวจแหล่งตัวหารโรงงานเดียวกัน: RSPO2015
พบรายงานผู้ตรวจRSPOของLamthap ประเมิน29–31มกราคม2015 จาก https://rspo.org/wp-content/uploads/Univanich_Lamthap_Mill_RSPO_audit_report_final_report_22_07.pdf

Webreaderอ่าน62หน้าได้ แต่rawdownload403และscreenshotcachemiss จึงยังไม่ยกระดับเป็นตรวจต้นฉบับครบหรือimportตัวเลข

ข้อค้นพบจากข้อความPDF5–6: ตารางSection1.4จำกัดผลผลิตส่วนรับรองจากestate/divisions ไม่รวมindependentgrowers;CPO/PKคำนวณจากอัตราสกัด ไม่ใช่ผลผลิตทั้งโรงงานที่วัดตรง จึงไม่ใช้หารน้ำเสียทั้งโรงงานปี2013แม้ชื่อLamthapตรงกัน

PDF34Indicator4.4.4กล่าวถึงFFBทั้งโรงงานปี2014และน้ำใช้ แต่ยอดในข้อความ310100m3/196145tได้ประมาณ1.581m3/t ต่างจากratio0.63ที่รายงาน ต้องเปิดภาพตรวจ ไม่กลับเศษส่วนหรือแก้เลขให้ตรงเอง ปี2014ยังไม่ตรงmonitoring2013

รายงานอธิบายreuse/irrigationของน้ำบำบัด ไม่ตีความzero-dischargeเป็นzeroCH4หรือไม่มีwateruse และไม่ใช้ค่าเกณฑ์BODแทนemissionload

ทำสคริปต์diagnostic `python scripts/review_lamthap_denominator.py` สร้างevidence/thai-lamthap-denominator-review.json รักษาค่าreportedคู่derivedและ5เหตุผลปฏิเสธการเชื่อม ไม่เป็นตัวคำนวณinventory ไม่มีnormalizedvalueหรือCO2total

### ข้อค้างที่เจาะจงหลังค้นรอบนี้
1. ต้องได้rawฉบับแก้ไขV4/verification/calculationของ2013
2. ต้องได้whole-millCPOoutputปี2013 ไม่ใช้certifiedsubsetหรือปี2014แทน
3. ต้องมีallocation/วิธีเฉลี่ยCOD/ขอบเขตน้ำเสียและก๊าซตรงกัน
4. แหล่งusephaseไทยที่มีCH4/N2Oเชิงมวลและfuelbasisตรงกันยังไม่มีหลักฐานใหม่ที่ผ่านเกณฑ์

หยุดเส้นทางดาวน์โหลดที่ติดข้อจำกัดนี้จนมีเบาะแสใหม่ ไม่วนเรียกURLเดิม ไม่ใช้sourceholdingปิดfullLCI
