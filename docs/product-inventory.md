# Inventory ต่อฐานผลิตภัณฑ์จากบทความ

แหล่ง: Permpool, N.; Ghani, H.U.; Gheewala, S.H. (2020). [An In-Depth Environmental Sustainability Analysis of Conventional and Advanced Bio-Based Diesels in Thailand](https://www.mdpi.com/2071-1050/12/22/9415), Sustainability12(22)9415, DOI10.3390/su12229415, Table4. ผู้ตีพิมพ์ระบุ CC BY4.0 ที่ท้ายบทความ จัดเก็บ attribution ไว้ทุกrecord

## ผล

ได้ source-reported inventory16ค่า: FAME10 / H-FAME6 บนฐานเดิม1000MJfuel; แยกBHD8ค่าเพราะต้นแบบข้อมูลจากฟินแลนด์ที่ปรับบริบท ไม่กล่าวว่าเป็นการวัดโรงงานไทย

FAME อ้างข้อมูล5โรงงานในไทย; H-FAMEอ้างnational pilot plant (Section2.2) ไม่เรียกทั้งสองเทคโนโลยีว่า commercial national average กระบวนการใน Table4 เป็น foreground conversion; ขอบเขตการศึกษาทั้งฉบับ WTWไม่ทำให้ตารางเดียวกลายเป็นฐานLCIครบวงจร

ปี2020คือpublication year ไม่ทราบmeasurement periodจากตารางที่เลือก เก็บdata_period=nullอย่างเปิดเผย คงฐาน1000MJ ไม่หารเปลี่ยนเป็นkgเอง ค่าผลผลิตFAMEในตาราง26.3kgคงเดิม แม้บทนำมี26.27kg ไม่แก้ด้วยข้อความอีกตำแหน่ง

Economic allocation FAME70%/glycerine30%เป็นคำอธิบายการศึกษาจากSection3.1.4 เก็บไว้เป็นmetadata ไม่คูณ0.70ซ้ำเพราะยังต้องตรวจว่าค่าในตารางถูกจัดสรรที่ขั้นใดแล้ว ช่องว่างไม่ใช่0; superscript aของไฟฟ้าH-FAME0.08kWhระบุ calculated powerของsemi-batch reactor เก็บannotation

สถานะ SOURCE_REPORTED_PRODUCT_INVENTORY แยกจาก ACCEPTED_REFERENCE97เดิมและจากการรับรองfull normalized productLCI ไม่รวมตารางimpactCO2eหรือenvironmental damagesเป็นinventory flows

## หลักฐานและการทำซ้ำ

เก็บ rendered DOM tableพร้อมtext/colspan/rowspan และ visible article textใน data/raw/mdpi-9415/ ไม่อ้างว่าเป็นoriginal HTTP responseหรือPDFbytes เว็บไซต์ HTTPตรงให้403/429 แต่ browserเปิดบทความและTable4ได้ตามปกติ ไม่มีการbypassaccess control

`python -X utf8 scripts/build_product_inventory.py` ตรวจsnapshot/headers/ตัวเลข/blank/footnote/geography แล้วสร้าง build/product-inventory/inventory.sqlite (process1:Nexchange พร้อมFK),report.json และ evidence/product-inventory.json ตรวจpayloadroundtripทุก16record

evidenceใช้SHA256ของsnapshotที่บันทึกจากDOM ไม่ใช่hashเอกสารตีพิมพ์ต้นฉบับ การอ้างอิงมีTable4/row/columnและDOIทุกค่า UIเมนู “LCI จากงานวิจัย” เปิดรายละเอียดได้

## ผลเทียบ NSO–DEDE

`scripts/compare_nso_dede.py` ใช้Pythonที่มีpypdf ตรวจPDFhashและre-extractpage8เชิงอรรถ3 เปรียบ manufacturing2024ที่30350ktoeในNSO13.10 กับ28987ktoeในDEDEเบื้องต้น ต่าง1363ktoe ผล DIFFERENT_PUBLICATIONS_REVIEW_REQUIRED ไม่สรุปสาเหตุrevisionหรือว่าแหล่งใดผิด

ไม่เปรียบmanufacturingกับindustrial total29261ซึ่งรวมเหมือง134และก่อสร้าง140ktoe ภาพpage8ถูกrenderตรวจแล้ว หลักฐานURL/hash/lineอยู่ evidence/nso-dede-comparison.json

การเทียบนี้ครอบคลุม1จาก273ค่าเท่านั้น อีก272ค่ายังไม่อ้างว่าเทียบDEDEแล้ว และNSOอ้างข้อมูลDEDEจึงเป็นการเทียบการเผยแพร่ ไม่ใช่independent measurements เก็บทั้งสองค่าและข้อจำกัดไว้ ไม่overwriteNSO การตรวจDOEBและDEDEฉบับrevisedยังเป็นงานต่อ

## เทียบกรมธุรกิจพลังงานเพิ่ม

พบ CKAN package963c2ffc-6899-4a59-8ea0-27d617a1a403 ที่ data.doeb.go.th และเก็บ XLSยอดขายรายปีพร้อมmetadata/hashในdata/raw/doeb/ ใช้xlrd2.0.2อ่านsheet sale_y ไม่แก้workbook

python -X utf8 scripts/compare_nso_doeb.py จับคู่ชื่อไทยตรงหลังtrimเฉพาะน้ำมันเบนซินออกเทน91และน้ำมันเตา ในปี2022–2024 รวม6ค่า แปลงmillionlitre→thousandlitreด้วย1000แบบDecimal คงstoredExcelfloatเป็นstring ทุกค่าต่างจากNSO แต่6/6อยู่ในครึ่งขั้นการแสดงผล0.0millionlitre (=50thousandlitre) ผลนี้ไม่เท่ากับexactmatchหรือindependentvalidation ดูevidence/nso-doeb-comparison.json

ไม่จับคู่ดีเซลที่การจัดประเภทต่างกัน และไม่เทียบLPGที่NSOใช้มวลกับหัวตารางทั่วไปของDOEBที่ระบุปริมาตร ปี2025ไม่มีในXLSฉบับที่ได้ ไม่อ้างว่าตรวจแล้ว รวมสองแหล่งเทียบได้7distinctNSOobservations ยังไม่เทียบ266ค่า งานT30ยังIN_PROGRESS

ติดตั้งdependencyสำหรับอ่านXLSเฉพาะในเครื่อง: python -m pip install --target .local/xls-deps xlrd==2.0.2 (ไม่ต้องใช้Excelหรือเปลี่ยนแปลงไฟล์ต้นทาง)
