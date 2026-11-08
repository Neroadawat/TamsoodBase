# ผลตรวจ CO₂e รายช่วงและส่วนที่ทำต่อได้ — 6 พฤศจิกายน 2026

## ผลงานรอบนี้
ตรวจภาพTable5–6(PDF18)และTable7(PDF20)ของรายงานCOMPETEเพิ่มเติม ทำtranscriptionเฉพาะTable7ส่วนcontribution17rows×2ปี=34cells พร้อมhierarchy/หน่วย/sourcehash/page/row/year ผลในevidence/ethanol-reported-stage-review.json และCSVprivateที่build/ethanol-reported-stages/contributions-private.csv

นี่เป็น**ผลCO2eที่แหล่งรายงาน** ไม่ใช่ผลคำนวณLCIครบของเรา หน่วยgCO2eq/Letohไม่ใช่kgก๊าซ ห้ามนำค่า1870ของpondมาบวกกับconversion3119.4ซึ่งรวมpondอยู่แล้ว

## ตรวจยอดแล้ว
แยกfarm/milling/conversionเป็นparentและรายการย่อยเป็นchildren:ยอดchildrenตรงparentทั้งสองปี เครดิตไฟฟ้าเก็บแยกและติดลบตามแหล่ง ผลรวมparent+creditต่างจากtotalที่รายงาน0.1gCO2eq/Lทั้งสองปี อยู่ในขอบเขตการปัดแสดง ไม่เปลี่ยนreportedtotal

โค้ดsrc/reported_balance.pyปฏิเสธparent+childและIDซ้ำ ตรวจส่วนต่างต่อdisplayrounding;3testsผ่าน ไม่ถือว่าการตรงสมการเป็นindependentreviewหรือแหล่งถูกทุกข้อ

## ข้อผิดพลาดที่เพิ่มในissue log
ปี2006Table7รายงานpercentincrease31.3 แต่net819.8/avoided2638.9ประมาณ31.1และข้อความประกอบรายงาน31.1 ต้องรักษาทั้งสองค่า ไม่แก้เป็นค่าเดียวหรือใช้percentนี้เป็นผลdemoที่ยืนยันแล้ว

## เหตุใดจึงยังไม่รวมกับE10ตัวอย่าง
1. Table7มีlabourในfarming แต่baselineของบทความ2008ที่เล่าเดโมแยกlabourออก ต้องแก้compatibilityก่อน
2. ตารางนี้เป็นethanolproductionaccounting มีgrossavoidedgasolineส่วนเปรียบเทียบ ไม่ใช่การปล่อยE10WTWทั้งหมด
3. พลังงานTable5–6เป็นprimaryenergyaccountingและมีinternalenergy/credit ไม่เอาMJไปคูณEFdirectcombustionเสมือนเป็นปริมาณเชื้อเพลิงที่เผาจริง
4. ไม่ย้อนCO2eqเป็นก๊าซรายชนิดจากยอดmixedcomponents และไม่ย้อนต้นทุนสิ่งแวดล้อมที่ปัดเศษกลับเป็นLCI

## สถานะหลังทำส่วนที่ข้อมูลรองรับ
- มีpartialphysicalbasis/FU/allocation;pondCH4คำนวณเองและreplayแหล่งได้
- มีชุดsource-reportedstageGHGที่ตรวจhierarchyและสมการแล้ว พร้อมexportprivate
- มีตัวคำนวณgas→CO2e/activity→CO2eที่แยกกันและป้องกันการนับซ้ำตามcoverageที่ระบุ
- ยังขาดปริมาณelementaryflows/providerinventoryที่สองPDFไม่ได้ให้ครบ และaggregateairLCIเล่มEnergyPolicyที่มธ.ไม่บอกรับ จึงไม่อ้างfullLCIหรือCFPรวม

ขั้นถัดไปที่ต้องมีหลักฐานใหม่:authoracceptedmanuscript/วิทยานิพนธ์/รายงานต้นทางที่มีrawLCI หรือเลือกทำscenarioที่เปิดเผยสมมติฐานเพิ่มอย่างชัดเจน ห้ามเรียกสมมติฐานใหม่เป็นdataวัดไทยหรือแก้fullflagเพื่อให้ดูครบ ไม่มีproductiondeployment/rawpublicในรอบนี้
