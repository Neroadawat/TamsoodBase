# ตรวจความครบ LCI สองเล่มเอทานอลและสร้างตัวอย่างเชื่อมฐาน — 6 พฤศจิกายน 2026

## สิ่งที่ทำเสร็จ
อ่านเนื้อหาทั้ง11หน้าเล่มกากน้ำตาลและ8หน้าเล่มมันสำปะหลังเพื่อหาเส้นทาง/ตาราง/ข้อมูลที่ยังไม่มี ไม่อ้างว่าตรวจทุกตัวเลขทุกภาพครบแล้ว ตรวจภาพFigure1/PDF2ของทั้งสองเล่มเพิ่มเติม สร้างตัวอย่างวัสดุจากกากน้ำตาลในเล่มเดียว ผูกกับFUการเดินทาง ไม่ต่อค่าB100หรือคนละเล่ม

คำสั่ง `python -m scripts.build_ethanol_demo` ผลprivateที่build/ethanol-demo/report.json และevidence/ethanol-demo-completion.json;โค้ดsrc/ethanol_demo.py ผ่าน3testsเฉพาะการคำนวณฐาน ไม่ใช่การรับรองความครบทางวิทยาศาสตร์

## ตัวอย่างที่คำนวณได้จริงในขอบเขตจำกัด
ตั้งระยะ13.46kmเท่ากับการใช้gasoline1Lตามรถทดสอบของงาน:ใช้E10ประมาณ1.011269722L;ส่วนเอทานอลผสมประมาณ0.101126972Lและgasolineประมาณ0.910142750L ภายใต้สมมติฐานผสมโดยปริมาตรและlinearbatchที่เปิดเผย

Figure1ของกากน้ำตาลให้ฐานอ้อย1tonne→เอทานอล99.5%10.17L พร้อมน้ำตาล103.6kg/กากน้ำตาล45.2kg/ชานอ้อย247kg/ใบอ้อย200kg/น้ำเสีย106.8L จึงscalephysicalbatchได้ แต่ intermediate/co-product/internalfuel ไม่ใช่flowอิสระที่นำมาบวกเป็นtotalmassหรือGHGทุกตัว

Economicallocation10.4%ของกากน้ำตาลใช้กับภาระupstreamที่เหมาะสม ไม่ตัดปริมาณอ้อยจริงเหลือ10.4% โค้ดแยกเรื่องนี้และทดสอบแล้ว ไม่มีการทำmassbalanceclosureจากข้อมูลไม่ครบ

ค่ารูปFigure1บางส่วนเป็นraster จึงระบุVISUAL_TRANSCRIPTIONชัด ไม่อ้างสองtextparsersอ่านตัวเลขในภาพได้ ข้อมูลstudyเก่าและสมมติฐาน99.5%fuel-blendingfeedไม่ใช่pureethanolconversion ไม่มีการเดาความหนาแน่น/volumecontraction

## ติดอะไรในเล่มกากน้ำตาล
- Table2เป็นprocedure/data-source ไม่ใช่ตัวเลขทุกinput/output
- มีปุ๋ยบางตัวต่อhectareในSection3.4 แต่ยังไม่มีyield/ปริมาณทุกinputที่ผูกFUเดียวกันครบ
- milling/conversionยังขาดรายการเชื้อเพลิง ไฟฟ้า สารเคมี น้ำ และการปล่อยรายprocessครบชุด
- transportมีscopeและแหล่งสัมภาษณ์ แต่ไม่ได้แจกทุกleg/payload/consumptionเป็นตัวเลขครบในเล่ม
- มีสัดส่วนน้ำเสีย/BOD/defaultCH4แต่ไม่ใช่ผลวัดก๊าซครบทุกระบบบำบัด
- Table5เป็นLCIA ไม่ย้อนแก้หาCO2/CH4/N2Oที่ไม่ตีพิมพ์จากค่าkgCO2eqรวม
- Section3.2/PDF8ระบุข้อมูลneatethanolcombustionส่วนใหญ่ไม่พร้อม;Figure6จึงเปรียบเทียบproductionphase อย่าอ่านเป็นE100fullcycle

## ลองเล่มมันสำปะหลังแล้ว
มีtransport3เส้นทางที่ตรวจแล้ว แต่ยังต้องมีมวลที่ขน/เชื้อเพลิง/ขากลับต่อFU Figure1แสดงเส้นทางstillage/sludgeโดยไม่มีquantitiesครบ Section1.2/PDF2ระบุชัดว่าข้อมูลsettledportionยังขาดและพิจารณาเฉพาะbiogasเป็นco-product Table2ใช้GREETประเมินE85ไม่ใช่fleetmeasurementไทย ข้อมูลTable4เป็นLCIAเช่นกัน และมีacidificationissueที่พักไว้เดิม

ดังนั้นเปลี่ยนไปเล่มนี้ยังไม่ทำให้unitprocessinventoryครบโดยอัตโนมัติ

## พบเล่มที่ควรตามต่ออย่างมีเหตุผล
**Fuel ethanol from cane molasses in Thailand: Environmental and cost performance** DOI10.1016/j.enpol.2008.01.008
https://www.sciencedirect.com/science/article/abs/pii/S0301421508000049

หน้าผู้พิมพ์ระบุTable7เป็นLCIresultsของE10a/b/cและCG มีรายการCO2/CH4/N2O/CO/NOx/SO2/VOC/PM10 เหมาะตรวจต่อเพราะอาจให้aggregateelementaryinventoryจริง ขอผู้ใช้ดาวน์โหลดผ่านห้องสมุดแล้ว ยังไม่importจากsnippet ไม่รับรองว่าunitprocessLCIครบจากคำบรรยาย

อีกแหล่งที่ตามreferenceได้คือ Full chain energy analysis of fuel ethanol from cane molasses in Thailand DOI10.1016/j.apenergy.2008.02.002 มีข้อมูลenergyรายsegmentตามหน้าผู้พิมพ์ แต่ยังไม่ได้fulltext จึงไม่copyค่ามาปิดgapและไม่วนค้นชื่อเดิมโดยไม่มีเบาะแสใหม่

## สถานะใช้งาน
โชว์เป็นpartialsame-studyforeground/ตัวอย่างFUและallocationได้ภายใน;ยังไม่ใช่completeLCIหรือผลCO2eรวม ไม่เปลี่ยนแบบจำลองเดิม ไม่deployข้อมูลraw ไม่ปิดstrictThai-backgroundgate ไม่มีการรอMTECapproval แต่ข้อจำกัดคือปริมาณที่เอกสารสองเล่มไม่เผยครบจริง

## เปลี่ยนทางหลังผู้ใช้ยืนยันว่า มธ. ไม่บอกรับเล่ม Energy Policy
ผู้ใช้รายงานไม่มีสิทธิ์ScienceDirect จึงไม่รอให้ซื้อและไม่ขอcredential ค้นพบและดาวน์โหลดรายงานCOMPETE/JGSEE มจธ. March2009ฉบับ61หน้าจากเว็บโครงการโดยตรง เก็บrawprivate/hashที่data/raw/thai-compete-report

Table7/PDF20printed16ตรวจภาพแล้วเป็นgCO2eq/Lethanol ใช้GWP100IPCC2001 ไม่ใช่ตาราง7รายก๊าซของEnergyPolicyแม้เลขตารางตรงกัน จึงใช้ตรวจบริบทmethod/boundaryได้ แต่ไม่แปลงmixedCO2eกลับเป็นมวลก๊าซหรือใช้Table13ต้นทุนย้อนหามลสารจากตัวเลขปัดเศษ

หลักฐานevidence/ethanol-open-access-followup.json;ไม่มีการimportnumericหรือแก้production ขั้นถัดไปคือหาauthoracceptedmanuscript/วิทยานิพนธ์ต้นทางที่มีphysicalLCIจริง หรือขอผ่านบริการจัดหาเอกสารของห้องสมุดโดยผู้ใช้เลือกดำเนินการเอง ไม่ส่งข้อความแทนผู้ใช้
