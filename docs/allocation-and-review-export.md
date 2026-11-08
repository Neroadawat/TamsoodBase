# Allocation review และไฟล์สำหรับทบทวนต่อ

ตรวจPDFv3ที่เก็บไว้ด้วยhashเดิมแล้วพบreported economic allocation:

| Process | ปัจจัยที่รายงาน | ตำแหน่ง |
|---|---|---|
| CPO | CPO92% / dry kernel6% / shell2% | PDFหน้า5 |
| FAME | FAME70% / crude glycerine30% | PDFหน้า7 |

ผลรวมแต่ละชุด100% ตรวจด้วยDecimal แต่ยังไม่ยืนยันว่าปริมาณในตารางเป็นก่อน/หลังallocation จึงไม่ใช้ปัจจัยนี้คูณค่าซ้ำ หลักฐานevidence/inventory-allocation-review.json และscripts/review_inventory_allocation.py ไม่เปลี่ยนmodelreadyให้true

สืบต่อreference18 (ARDA2017) พบระเบียนNRCTที่เกี่ยวข้องกับปาล์มและวัฏจักรชีวิต แต่ชื่อระเบียนยังไม่ยืนยันว่าเป็นรายงานอ้างอิงเดียวกัน และไม่มีcalculation sheetsที่เข้าถึงได้จากหน้าที่ตรวจ จึงไม่ใช้ยืนยันการปันส่วน:
https://explore.nrct.go.th/search_detail/result/3152

## บนเว็บ

แท็บข้อมูลต้นน้ำมีprofileของFFB/CPO/RBDPO แยกsourcecellverificationจากmodelreadiness มีเหตุผลค้างเฉพาะprocess ไม่ให้คะแนนDQRหรือuncertaintyขึ้นเอง ช่วงปีวัดยังnullอย่างเปิดเผย

ดาวน์โหลดJSONตามprocessและdirectionที่เลือกได้ โดยคงdecimalstrings/unit/sourceURL/hash/table/page/row/heldstatus/attribution/CCBY4.0 และแนบprocessprofile/ข้อจำกัด แยกsource_countsของชุดต้นฉบับจากselection.exported_rowsเพื่อไม่ทำให้จำนวนเข้าใจผิด

## ผลตรวจ

- 146testsผ่าน รวมallocationfinite/sum100,profilemissingfeedstock,exportselection/roundtrip/nullunit/hold
- Browserก่อนdeploy:ดาวน์โหลดCPOทั้งหมด12รายการและparseกลับเทียบทุกfieldกับpublicsnapshot/profile
- Browserหลังdeploy:ดาวน์โหลดFFBเฉพาะINPUT18รายการและparseกลับตรงทั้งหมด รายการLandseedingยังunitnullและHOLD ไม่หายไป
- HTTPหลังdeploy:publicsnapshot42rowsและprofilesตรงbuildทุกfield;HTML/JS/CSSตรงbuild;APIconversion16rowsทุกfieldยังตรงsavedreport
- production dpl_9ATkhNM3ybpM297dYszZ38iix1Si;ภาพbuild/ux-verification/readiness-live-proof.png

นี่คือreviewJSON ไม่อ้างว่าเป็นILCD/openLCA/SimaProformatหรือพร้อมคำนวณLCIA การexportไม่ได้เปลี่ยนระดับการยอมรับข้อมูล

## งานที่ยังเหลือ

1. ได้เอกสารหรือcalculation sheetsที่ยืนยันการใช้allocationกับแต่ละตาราง
2. ได้FFBinputamountและข้อมูลขาดอื่นพร้อมsourceและบริบทที่เข้ากัน
3. เชื่อมbackground/transport/use-phaseและelementaryflows พร้อมตรวจความครบถ้วน/qualityตามขอบเขตที่เลือก
4. สร้างและทดสอบinteroperableLCIexportเมื่อแบบจำลองพร้อม ไม่เปลี่ยนชื่อreviewJSONเพื่ออ้างว่ารองรับแล้ว
