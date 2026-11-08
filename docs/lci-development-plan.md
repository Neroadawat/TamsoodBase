# แผนพัฒนาจากข้อมูลอ้างอิงสู่ LCI ที่ใช้ต่อได้

เลือก **FAME ขั้นแปรรูปเชื้อเพลิงในไทยตาม Table4 ของ DOI10.3390/su12229415** เป็นกรณีหลักก่อน เพราะมีreferenceproduct/ฐาน1000MJ/input-output/source locatorsอยู่แล้ว ไม่ใช้แทนดีเซลปิโตรเลียมหรือค่าเฉลี่ยประเทศ H-FAMEยังเป็นกระบวนการแยกจากpilotplant

เป้าหมายแรกคือforegroundinventoryที่นำไปทบทวนต่อได้ ไม่ประกาศfull lifecycle ก่อนมีข้อมูลครบตามขอบเขต

## ทำแล้ว

- docs/inventory-flow-registry.json:15source-localflowsจับคู่16observationsด้วยlabel/unitตรง ไม่เดาCAS/globalontology/compartment
- scripts/build_inventory_model_review.py:2processprofilesแยกstudyFU/referencebasis/referenceproduct/boundary/readiness
- build/inventory-model-review/review.json และ evidence/inventory-model-review.json:ผลสร้างซ้ำได้ ไม่ใช่16observationsใหม่อีกชุด
- FAMEoutput→H-FAMEinputมี1candidate เก็บidentityทั้งสอง ไม่applyscaling/link/allocation
- 136testsผ่าน รวมnegativecasesของlabel/unit/DOI/mappingซ้ำ/compartmentที่เดาเอง

## งานต่อ

| ลำดับ | งาน | เกณฑ์จบ |
|---|---|---|
| P0 | เก็บTable1–3ฉบับเต็ม | snapshot/hash/tablecells/units/footnotes และตรวจทุกค่าที่เลือก ไม่ใช้searchsnippetเป็นrawverified |
| P0 | ทบทวนallocation | ระบุแต่ละตารางก่อน/หลังallocation;sourceและวิธีใช้ปัจจัย;ไม่คูณ70%ซ้ำ |
| P0 | เพิ่มupstreamprocessแยก | FFB/CPO/RBDPOมีbasisตัวเอง ไม่เปลี่ยน1000kgเป็น1000MJโดยตรง |
| P1 | เชื่อมprovider | product/unit/context/methodเข้ากัน มีversion/เหตุผลเลือก;ยังไม่พร้อมคงNOT_LINKED |
| P1 | Quality review | เวลา/พื้นที่/เทคโนโลยี/ความครบถ้วนพร้อมหลักฐาน ไม่แต่งDQRหรือuncertainty |
| P1 | Export/roundtrip | metadata/source/decimal/boundaryไม่หาย สิทธิชัด ไม่อ้างopenLCAcompatibleจนทดสอบจริง |
| P1 | หน้าprocessprofile | อ่านง่าย แสดงสิ่งที่มีและขาด ไม่คืนแถบเดโมที่ผู้ใช้ไม่รับ |

## ผลค้นเพิ่ม 30ตุลาคม2569

ผลค้นพบTable1:1000kgFFB/Table2:1000kgCPO/Table3:1000kgRBDPOในบทความเดิม แต่เปิดผู้ตีพิมพ์ครั้งนี้ได้HTTP429จึงหยุดเรียก ไม่เปลี่ยนendpointเพื่อหลบข้อจำกัด ยังไม่ใช้ตัวเลขจากผลค้นมานับเป็นverifiedobservations

พบรายงานCOMPETEประเทศไทยที่ผลค้นระบุinventoryต่อ1tonbiodiesel แต่webtoolเปิดPDFไม่สำเร็จ เป็นcandidateเท่านั้น ยังไม่ยืนยันปี/เทคโนโลยี/สิทธิหรือใช้เชื่อมกับข้อมูล2020

- Publisher: https://www.mdpi.com/2071-1050/12/22/9415
- Candidate report: https://www.compete-bioafrica.net/publications/publ/2nd_Report/Annex4-2-5-COMPETE-032448-2ndReport-D4.1-Thailand-Final.pdf

## ข้อจำกัด

16mappedexchangesไม่เท่ากับ16completeLCIdatasets;modelreadyยัง0/fullLCIfalse;measurementperiodและallocationapplicationไม่resolved;ไม่มีglobalflowmapping;ยังไม่deployreviewartifactนี้ไปAPIหรือmigrateMySQL การตรวจเป็นAI-assistedไม่ใช่independentexpertreview

## อัปเดต: ได้PDFทางการฉบับเต็มแล้ว
พบURLไฟล์PDFสาธารณะใหม่และดาวน์โหลดสำเร็จ ตรวจTable1–3ครบ42รายการด้วย2extractorsและภาพหน้า5–6:41มีหน่วย/1HOLD สร้างcandidateSQLiteแยกและprovidercandidates3คู่แต่ไม่apply มีFFBinputขาดในTable2 ดูdocs/upstream-inventory-review.md และevidence/upstream-inventory-review.json;140testsผ่าน ข้อความเข้าถึงไม่ได้ด้านบนเป็นประวัติรอบก่อน ไม่ใช่blockerปัจจุบัน

## ขึ้นเว็บชุดต้นน้ำแล้ว
เพิ่มแท็บข้อมูลต้นน้ำแยกจากTable4เดิมที่#inventory;publicsnapshotเฉพาะCCBY4.0พร้อมattribution ไม่มีrawPDFหรือข้อมูลบริษัทเพิ่ม ตรวจlive42rowsทุกfieldตรงreviewedreport;143testsและAPI27routesผ่าน มีbrowserก่อน/หลังdeployรวม390px/filter/hold/detail/pdfpage ตรวจจริงแล้ว ดูevidence/upstream-web-release.json ยังไม่applyprovider/allocationหรืออ้างfullLCI

## Allocation/readiness/exportต่อแล้ว
ตรวจreportedsharesCPO92/6/2และFAME70/30ตรงPDF แต่applicationกับtableยังunresolved;ขึ้น3processreadinessprofilesแยกsourceverifiedจากmodelreadyพร้อมreviewJSONdownloadตามfilter (ไม่ใช่openLCAformat) 146testsผ่าน browserดาวน์โหลด/parseCPO12ก่อนและFFB18หลังdeployตรงทุกfield ดูdocs/allocation-and-review-export.md/evidence/upstream-export-review.json สิ่งที่ยังต้องหาคือcalculationbasis,FFBinput,backgroundprocesses/transport/useและflowmapping ไม่วนตรวจแถวเดิมเพื่อเพิ่มยอด
