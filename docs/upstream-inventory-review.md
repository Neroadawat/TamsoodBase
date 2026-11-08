# ตรวจข้อมูลต้นน้ำ FFB / CPO / RBDPO

ได้ไฟล์PDFฉบับเต็มจากURLสาธารณะที่พบใหม่บนเซิร์ฟเวอร์ไฟล์ทางการของผู้ตีพิมพ์ ไม่ได้วนเรียกหน้าHTMLที่ตอบ429

แหล่ง: Permpool, Ghani & Gheewala (2020), DOI10.3390/su12229415, Tables1–3, PDFหน้า5–6 ฉบับv3 ท้ายPDFระบุCCBY4.0 เก็บraw/manifest/hashในdata/raw/mdpi-9415/pdf-v3 โดยไม่ได้เผยแพร่rawต่อ

## ผลตรวจ

| Process | ฐานอ้างอิง | รายการมีหน่วย | พักเพราะหน่วยไม่ระบุ |
|---|---|---:|---:|
| FFB | 1000kgFFB |18|1|
| CPO | 1000kgCPO |12|0|
| RBDPO | 1000kgRBDPO |11|0|

รวม42observedcells:41unit-presentและ1HOLD ไม่ใช่41acceptedLCIdatasets ทุกค่าตรวจเทียบpypdfกับpdfplumber:amount/unit/directionตรง;labelsเทียบแบบnormalizeช่องว่าง/ligature/subscriptsพร้อมคงlabelจากpypdfไว้ ตรวจภาพหน้า5–6แล้ว ไม่ใช่independentmeasurements

ผูกidentityกับPDFhash/table/data-row เก็บrawline/decimal/unit/ทิศทาง/หน้า/table-row/DOI/ปีเผยแพร่/ช่วงปีวัดnull/role เฉพาะreferenceproductมีroleชัดเจน ผลพลอยได้/ของเสียอื่นคงOUTPUTโดยไม่เดาการจัดประเภท

## ประเด็นที่ต้องคงไว้

- Land seeding0.48ไม่มีหน่วย จึงHOLD ไม่เติมm2หรือha
- Table2ไม่ระบุFFBinputamount จึงยังเชื่อมFFB→CPOหรืออ้างmassbalanceครบไม่ได้
- Table3Water0.11มีหน่วยkgตามต้นฉบับ ไม่แก้เป็นm3
- Table4Potassium hydroxideขัดกับเนื้อความที่พูดถึงNaOH ไม่แก้ชื่อตามการเดา
- CPOมีreportedallocation92/6/2และFAME70/30ในเนื้อความ แต่ยังไม่ยืนยันการapplyกับตัวเลขตาราง จึงไม่คูณซ้ำ
- ปี2020เป็นpublicationyear ไม่ใช้แทนmeasurementyear

## ฐานทดลองและการเชื่อม

build/upstream-inventory/candidate.sqlite มีprocess3/exchange42และviewunit-present41 ตรวจroundtripครบ42/FKไม่มีปัญหา ทดสอบmissingprocessและการเปลี่ยนHOLDที่ไม่มีหน่วยเป็นcandidateถูกปฏิเสธ ไม่migrateMySQL/EC2และไม่เปลี่ยนAPIเดิม

evidence/upstream-provider-review.jsonมีcandidate3คู่: CPO→RBDPO, RBDPO→FAME, FAME→H-FAME ทั้งหมดCANDIDATE_NOT_APPLIED ไม่คำนวณscaling/LCItotal และคงmissingFFB→CPOไว้ชัด

## ทำซ้ำ

ใช้Pythonที่มีpypdf/pdfplumber:

```powershell
python scripts/extract_upstream_inventory.py
python scripts/review_upstream_links.py
python -m unittest discover -s tests -p "test_*.py"
```

ผลล่าสุด140testsผ่าน พร้อมevidence/upstream-inventory-review.json การที่unit-presentไม่ใช่เกณฑ์ครบทุกด้าน ยังต้องallocation/background/transport/emissions/method/rightsตามการใช้ก่อนmodelready

ขั้นต่อไป:ทบทวนข้อมูลสนับสนุนวิธีallocationและupstreamfeedstockที่ยังขาด แล้วจึงเปิดprofile/ชุดcandidateในUIแบบแยกจากinventoryที่ให้บริการอยู่ ไม่เพิ่มยอดproduction16รายการโดยเงียบ ๆ
