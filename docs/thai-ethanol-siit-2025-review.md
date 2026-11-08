# แหล่งใหม่ที่มีปริมาณ LCI: เอทานอลไทย SIIT2025

## แหล่งและผลที่ได้
Potential of Using Ethanol as Fuel in the Transportation Sector, Sittimont & Chinda, Science & Technology Asia30(3),174–188, DOI10.14456/scitechasia.2025.60
https://ph02.tci-thaijo.org/index.php/SciTechAsia/article/view/261544

ดาวน์โหลดPDF15หน้าจริง383076bytes SHA2564a3d9dc62e670069302bf27ab85caa93fb604258db1c8f40bb73e71a6d49addd เก็บprivateในdata/raw/thai-ethanol-siit-2025;หน้าเว็บระบุCCBYNCND ไม่เปลี่ยนredistributionเป็นCLEARED

Table8/PDF14printed187มีปริมาณ18แถวบนฐาน1tonethanol เช่นfresh/burntcane,น้ำ,สารเคมี,กากน้ำตาลและintermediateprocessstreams ตรวจตัวเลขทุกค่าของsubsetนี้ด้วยpypdf+pdfplumberและภาพเต็มหน้า14;ชื่อ/หน่วย/ตำแหน่งแถวเทียบภาพ ไม่อ้างว่าตรวจทุกfieldทั้งบทความแล้ว

ผลที่ใช้ต่อได้: **อีกกรณีศึกษาของactivityinventoryฝั่งacquisition** ไม่ใช่ข้อมูลmissingที่นำไปใส่ชุด2008ได้ทันที intermediateเช่นdilutedmolasses/alcoholต้องเป็นlinkระหว่างprocess ไม่บวกเป็นexternalinputsซ้ำ

## ตรวจคุณภาพก่อนใช้แล้วพบ6ประเด็น
- Table9แถวlime:2.61×1.0215×100%ได้2.666115 แต่รายงาน0.2866 เกินกว่าการปัดทศนิยมธรรมดา อาจเกี่ยวallocationที่ไม่ตรงคอลัมน์ แต่ไม่เปลี่ยน100%เป็น10.73%ให้เอง
- FreshcaneEFTable6=0.0157แต่Table9=0.0151 ยังไม่รู้ว่าเวอร์ชันหรือพิมพ์ผิด
- BurntcaneEFTable6=0.0249แต่Table9=0.0242 คงทั้งสองไว้
- ROwaterคูณEFที่แสดง0.0005ไม่ตรงผลที่แสดง อาจมาจากprecisionภายในมากกว่า ไม่กล่าวหาว่าผิดจนได้หลักฐาน
- ขอบเขตศึกษาจริงเป็นacquisition ไม่ครอบคลุมenergy/use/wasteทั้งวงจร แม้ชื่อเรื่องกล่าวถึงtransportationsector
- ตารางอ้างEcoinvent/แหล่งต่างประเทศด้วย ไม่อ้างThai-onlybackground

อ่านภาพTable9/PDF15ยืนยันว่าคอลัมน์allocationและค่าขัดกันปรากฏจริง ไม่ใช่แค่parserเลื่อนบรรทัด

## การตัดสินใจ
เก็บ18quantitiesเป็นsource-reportedcandidateภายใน พร้อม6issuesและsourcehash ไม่importเข้าproductionหรือปิดfullLCIflag ไม่รวมGWPต่างรุ่น/ฐานมวล1tonethanolกับฐาน1gasoline-equivalentlitreปี2008โดยไม่มีdensity/FU/technologybridge

คำสั่ง `python -m scripts.review_ethanol_siit_2025`;ผลbuild/ethanol-siit-review/review.json และevidence/thai-ethanol-siit-2025-review.json

## เส้นทางค้นอื่นที่ตรวจในรอบนี้
พบเพียงbibliographicreferencesของวิทยานิพนธ์Nguyen2007ยังไม่มีfulltextที่เข้าถึงได้จริง;KU2011articlewebreaderอ่านได้แต่directdownload404 ไม่สร้างPDF/hashเท็จ ไม่ใช้snippetแก้ค่าที่ขาด ไม่วนURLเดิมโดยไม่มีเบาะแสใหม่

จึงเพิ่มหลักฐานได้จริงฝั่งวัตถุดิบของกรณีใหม่ แต่ยังไม่ใช่fullreconstructableLCIทุกprocess วิธีปิดช่องว่างต่อคือตรวจฐานข้อมูลต้นทางDEDE/ThaiEnvironmentFoundation2007ที่บทความอ้างหรือได้inventoryexportของกรณีเดียวกัน ไม่รอMTECapprovalและไม่เติมmissingเป็นzero
