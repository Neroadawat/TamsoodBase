# ตรวจความพร้อม LCI และค้นส่วนขนส่ง — 4 พฤศจิกายน 2569

## ผลที่ได้จริง

แก้ตัวตรวจ local FAME candidate ให้การลบพารามิเตอร์ที่ยังขาดไม่ช่วยให้ผ่าน, ปฏิเสธ parameter ID ซ้ำ, แสดงแถว HOLD/ขาดหน่วย/ขาด URL หรือ hash เป็น blocker และไม่รับ gate VERIFIED ที่ไม่มี evidence reference รองรับ รองรับทั้ง source_sha256 ของ PDF และ source_snapshot_sha256 ของ HTML โดยคง source payload เดิม

คำสั่ง `python -m unittest tests.test_lifecycle_model tests.test_thai_carbon` ผ่าน14tests (รวม4testsใหม่ในรอบนี้) และสร้าง candidate ใหม่สำเร็จ52รายการ ไม่มีการแก้จำนวน/หน่วย/ปี/locator จากต้นฉบับ ขณะนี้พบหนึ่งแถวขาดหน่วยและ HOLD อยู่ในแถวเดียวกัน จึงแสดงสองเหตุผล ไม่ใช่สองรายการเสีย ตัวตรวจนี้เป็นเงื่อนไขจำเป็น ไม่ใช่เครื่องรับรองความครบถ้วนทางวิทยาศาสตร์จากการตั้ง status

## สิ่งที่ค้นและตรวจเพิ่ม

1. **Malakul et al., Life-cycle Energy and Environmental Analysis of Biofuels Production in Thailand (2011)** — [ต้นฉบับในคลังมหาวิทยาลัยเกษตรศาสตร์](https://kukr.lib.ku.ac.th/kukr_es/BKN/search_detail/dowload_digital_file/203067/58789): อ่านเนื้อหา section2.1–2.3 พบขอบเขตเพาะปลูก–ผลิต–ขนส่งจนได้เชื้อเพลิง ไม่ได้เป็นหลักฐานว่าครบการใช้และปลายทางทั้งหมด Section2.2 ระบุ background บางรายการจาก ecoinvent จึงยังปิดข้อกำหนดไทยล้วนไม่ได้ ไม่มีการนำตัวเลขเข้าโมเดล
2. **Pleanjai/Gheewala (2009), DOI10.1016/j.apenergy.2009.05.013** — web reader อ่านเนื้อหาฉบับเต็มได้ รวม section2.3.4 ขนส่ง แต่ local PDF ติด certificate expired, HTTP redirect ไปHTTPSเดิม และ screenshot cache miss จึงยังไม่ยกระดับตัวเลขเป็น fully reviewed local source ไม่มีการปิดตรวจ certificate หรือคัดตัวเลขจาก snippet เข้าโมเดล
3. **Chotanapund et al. (2025), Spatially differentiated life cycle assessment of Thailand's transport**, DOI10.1016/j.spc.2025.04.023 — [คลังผู้เขียน](https://researchers.mq.edu.au/en/publications/spatially-differentiated-life-cycle-assessment-of-thailands-trans/) ยืนยันตัวตนบทความ การขนส่งไทยทั้ง freight/passenger และมีลิงก์ publisher PDF ที่ระบุ CC BY; Crossref ยืนยัน DOI/ผู้เขียน/license metadata เก็บ metadata/hash แล้ว อย่างไรก็ตาม PDF ในลิงก์ที่เผยแพร่จริงตอบ403 จึงยังไม่ได้ตรวจ inventory/supplement/reference product/ช่วงปี/สิทธิ background และยังไม่รับตัวเลข งานนี้เป็น candidate ใหม่ที่ตรงช่องว่างการขนส่ง ไม่อ้างว่าได้ชุดข้อมูลแล้ว
4. ThaiScience paper2004 URLที่ค้นพบคืนเนื้อหาที่ไม่ใช่PDF จึงไม่บันทึกเป็นต้นฉบับสำเร็จและไม่รับข้อมูล

## ช่องว่างที่ยังปิดไม่ได้จากหลักฐานรอบนี้

| ส่วน | สิ่งที่มี | เงื่อนไขก่อนเชื่อมเป็นผลทั้งระบบ |
|---|---|---|
| วัตถุดิบ/การผลิต FAME2020 | source payload52รายการ | หน่วยแถวHOLD, FFB input, allocation, reference-flow scaling, providers |
| ขนส่ง/จำหน่าย | ข้อมูลอ้างอิง2009อ่านได้ทางweb; candidate2025ใหม่ | ตรวจต้นฉบับ/ตารางครบ, ขาเดินทาง, โหลด/เที่ยวกลับ, เชื้อเพลิง, หน่วยและช่วงปีตรงระบบ |
| การใช้ | Thai2013รายงาน4pollutants ต่อlitre | ตรวจรายงานวัดต้นทาง, fuel properties สำหรับฐานMJ, ความเข้ากันกับรุ่นเชื้อเพลิง/เครื่องยนต์, CH4/N2O และชนิดPM |
| การจัดการของเสีย | POMEไทย2011มีoperating pointsและbiogas generation | ปริมาณน้ำเสียต่อreference product, fugitive emissions, auxiliary inputs, net export; ห้ามใช้CH4ที่ผลิตเป็นCH4ที่รั่ว |
| ข้อมูลเบื้องหลัง | พบThaiNationalLCIและTGOcharacterized factors | ต้องได้ exchanges/provider/version/สิทธิที่ใช้ได้; CO2e factorไม่แทนelementary inventory |

GSP2007เป็นอีกเส้นทางผลิตภัณฑ์และgate-to-gate ไม่ต่อเข้ากับFAMEเพื่อเติมจำนวนช่วง ไม่รวมตัวเลขข้ามปี/โรงงาน/ฐานallocationโดยไม่มี compatibility justification

## สถานะส่งมอบ

หลักฐาน `evidence/lifecycle-readiness-review-2026-11-04.json` และ `evidence/lifecycle-candidate.json`; T104ปิดเฉพาะการแก้ตัวตรวจและค้นแบบมีขอบเขต T97ยังIN_PROGRESS ไม่มีการเปลี่ยนเว็บไซต์/API/EC2/สิทธิแจกจ่าย และยังไม่ใช่ complete Thai-only full lifecycle LCI ไม่มีข้อมูลที่หาไม่พบถูกเติมเป็นศูนย์

ขั้นถัดไปที่มีประโยชน์คือได้ fulltext/supplement ของ transport2025 จากช่องทางทางการที่เข้าถึงได้ หรือไฟล์ThaiLCIที่มีสิทธิและprovider metadata แล้วตรวจทุกแถว/หน่วย/ปี/ขอบเขตก่อนประกอบโมเดล ไม่วนดาวน์โหลด URLที่ล้มเหลวโดยไม่มีหลักฐานใหม่
