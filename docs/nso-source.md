# สำนักงานสถิติแห่งชาติ: สถิติพลังงานรายปี

ค้นและเก็บ 23 ตุลาคม 2569 จาก [รายงานสถิติรายปีประเทศไทย 2569](https://www.nso.go.th/public/e-book/Statistical-Yearbook/SYB-2026_webPage/Page_SYB_TH.html) เปิดบท13และดาวน์โหลด CSV ทางลิงก์จริงใน browser เนื่องจาก direct HTTP ตอบ418 ไม่ bypass CAPTCHA/authentication

| ตาราง | เรื่อง | ปีข้อมูล ค.ศ. | จำนวนค่า |
|---|---|---|---:|
| 13.5 | การจัดหาพลังงานขั้นต้น | 2022–2024 | 48 |
| 13.6 | การผลิต/ใช้น้ำมันสำเร็จรูป | 2022–2024 | 69 |
| 13.7 | ปริมาณ/มูลค่านำเข้าน้ำมันสำเร็จรูป | 2022–2024 | 36 |
| 13.8 | การจำหน่ายเชื้อเพลิง | 2022–2025 | 84 |
| 13.10 | การใช้พลังงานในอุตสาหกรรม | 2022–2024 | 36 |

รวม273 source observations ไม่ใช่273 LCI exchanges หรือ273 flows อิสระ มีทั้งยอดรวม รายการย่อย มูลค่า และร้อยละ เก็บแยกจาก reference97รายการเดิมใน build/nso/nso.sqlite และ report.json

## จุดสำคัญของความหมาย

- NSO เป็นผู้เผยแพร่/รวบรวม; ต้นทางตามท้ายตารางคือกรมพัฒนาพลังงานทดแทนและอนุรักษ์พลังงาน (13.5/6/7/10) และกรมธุรกิจพลังงาน (13.8) ไม่ถือการเผยแพร่ซ้ำเป็น independent verification
- 13.5 นิยาม supply = domestic production + imports − exports ± stock change มี6ค่าติดลบ เก็บเครื่องหมายเดิม ไม่ reject หรือทำ absolute
- 13.8 เชิงอรรถ(1)เปลี่ยนหน่วย LPG/propane/butane เป็นพันกิโลกรัม รวม12ค่า ไม่ใช้หน่วยพันลิตรจากหัวตารางกับทุกแถว
- 13.7 มูลค่าหน่วยล้านบาทและ13.10ร้อยละเป็น context แยกจากปริมาณจริง
- 13.6 ระบุไม่รวม HSD/fuel oil ที่ใช้ผลิตไฟฟ้าตามเชิงอรรถ เก็บหมายเหตุทุกแถว; ไม่เทียบตรงกับยอดขายคนละขอบเขต
- publication2026 แยกจาก reference_year2022–2025 ไม่มีการเพิ่มข้อมูลปี2026ขึ้นเอง

## หลักฐานและการตรวจ

raw CSV bytes และ manifest SHA256/URL/เวลาเก็บอยู่ data/raw/nso/yearbook-2026/ ซึ่งถูก gitignore ข้อมูลแต่ละค่ามี table, CSV physical line end-of-record, column1-based, header, raw row, raw value, unit, notes และ agency

รัน offline: `python -X utf8 scripts/import_nso.py` ตรวจ hash, headerปี,จำนวนคอลัมน์,ตัวเลข,duplicate identity,SQLite integrity และ JSON roundtrip ทุก273ค่า; `--download-dir C:/Users/HP/Downloads` ใช้ import ไฟล์ที่ดาวน์โหลดใหม่ครั้งแรก snapshotต่างbytesไม่ overwrite

tests/test_nso.py ตรวจหน่วยตามเชิงอรรถ,negative supply,จำนวนและidentity,locator และปฏิเสธcellเสีย ผล reparse ไม่ใช่การตรวจข้ามแหล่งอิสระ ยังไม่ได้เทียบ PDF ทุกค่า (PDF download รอบนี้ไม่สำเร็จ)

สถานะ STAGED_SOURCE_VERIFIED = parse/locator จาก CSV ต้นฉบับได้ ยังไม่ promote เป็น ACCEPTED_REFERENCE หรือ normalized product LCI และยังไม่ยืนยัน redistribution licence เว็บไซต์อธิบายจุดประสงค์ research/reuse พร้อม footerสงวนลิขสิทธิ์ จึงเก็บ raw local ไม่เผยแพร่ต่อ

เปิดเว็บเมนู “สถิติแห่งชาติ” เลือกตารางแล้วเปิดหลักฐานได้ ภาพตรวจจริง build/explorer/nso-statistics.png

## เพิ่มความทนทานของ parser

ตรวจกรณีทั้งแถวเป็น n.a. แล้วต้องแจ้ง error ไม่ปล่อยให้แถวหายเงียบ พร้อมตรวจ พ.ศ.−543=ค.ศ. และปีไม่ซ้ำ ผล tests และ import273ค่าเดิมอยู่ evidence/nso-parser-hardening.json ไม่มีการเปลี่ยนค่าต้นฉบับหรือเลื่อนสถานะ accepted

## ตรวจยอดรวมและการค้น

รัน python -X utf8 scripts/review_nso.py ได้ evidence/nso-total-checks.json ตรวจ18กลุ่มของตาราง13.6/13.7/13.10 ทุกกลุ่มอยู่ใน tolerance จากครึ่งหลักสุดท้ายของตัวเลขแต่ละค่า ไม่แก้ตัวเลข ไม่รวม13.5ที่มีsubtotalซ้อน หรือ13.8ที่มีต่างมิติ ไม่อ้างว่าเป็น independent verification

เพิ่มตัวกรองปี/คำค้นและreset ในเมนูสถิติแห่งชาติ ตรวจbrowserค้นดีเซล2024ได้2ค่า: ผลิต27664และใช้25120 ล้านลิตร แยกตามmeasureพร้อมหลักฐาน ภาพอยู่ build/explorer/nso-filtered.png

## ทบทวน local comparison เพิ่ม 23 ตุลาคม 2569

เพิ่มexactlabelน้ำมันดีเซลกำมะถันสูง2022–2024จากDOEB XLSเดิม3ค่า หน่วยvolumeตรงกัน แต่storedvaluesไม่เท่ากัน (รวมDOEB9ค่าอยู่displayroundingทั้งหมด ไม่ใช่exactmatch) coverageสร้างจากNSOidentityและตรวจreporthashด้วยscripts/cross_source_coverage.py: เทียบรวมDEDE10/273 อีก263ยังไม่เทียบ independentmeasurementsverifiedยัง0 ไม่แก้sourcevalueและไม่เปลี่ยนacceptance ปี2025ไม่มีDOEBในsnapshotนี้ ส่วนdieselชนิดอื่นไม่รวมโดยอนุมานclassification


## พบรายงาน DEDE revised ที่ตรง NSO — 24 ตุลาคม 2569

หน้า https://www.dede.go.th/articles?id=452&menu_id=1 ระบุannual2024เป็นrevised และลิงก์Excelชื่อ25May2026 ตารางsheet `ktoe` แถวMANUFACTURING คอลัมน์GRAND TOTAL cellDT52ระบุ30350 ตรงNSO13.10ปี2024ทุกหลักที่แสดง ต่าง0 ใช้ scripts/compare_nso_dede_revised.py ตรวจhash/ปี/หน่วย/ชื่อแถว/คอลัมน์ก่อนเทียบ

หลักฐาน evidence/nso-dede-revised-comparison.json รายงานเบื้องต้น28987และส่วนต่าง1363ยังคงอยู่ในหลักฐานเดิม ไม่แก้ตัวเลขย้อนหลัง ไม่สรุปว่าNSOผิด หรือระบุสาเหตุcalculationchangesที่ต้นทางไม่ได้อธิบาย การพบrevisedที่ตรงกันไม่ได้พิสูจน์ว่าทุกmetricตรง และไม่เพิ่มindependentmeasurementsverified/acceptedLCI การเทียบนี้ใช้NSOidentityเดิมจึงcoverageยัง10/273 อีก263ยังไม่เทียบ

snapshotExcel/manifestอยู่data/raw/dede/revised-2024ไม่ตามGit; ต้องมีopenpyxlในenvironmentที่รันscript (เครื่องเดิมใช้bundledPython) อัปเดตเว็บแล้วให้แสดงrevised30350ตรงกับNSOและpreliminary28987แยกกัน พร้อมลิงก์ต้นฉบับ ตรวจbrowserจริงและAPIidentity/arithmetic; evidence/nso-revised-ui.json

## ขยาย comparison จาก workbook เดิม — 24 ตุลาคม 2569 เวลา 11:27 UTC

ตรวจ read-only เฉพาะ manufacturing ปี2024ใน workbook DEDE revised ที่เก็บไว้แล้ว ไม่ดาวน์โหลด URL เดิมซ้ำ พบ quantity subtotal ที่เทียบเพิ่มได้5ค่า ทุกค่าตรง NSO13.10ตามจำนวนเต็มที่แสดง:

| NSO label | ค่า (ktoe) | DEDE sheet / cell |
|---|---:|---|
| ถ่านหิน | 6970 | ktoe / W52 |
| น้ำมันสำเร็จรูป | 3186 | ktoe / BO52 |
| ก๊าซธรรมชาติ | 6631 | ktoe / AG52 |
| ไฟฟ้า | 7163 | ktoe / BR52 |
| พลังงานหมุนเวียน | 6400 | ktoe / DC52 |

ใช้ `scripts/compare_nso_dede_components.py` ตรวจsourcehash,year,unit,MANUFACTURING row,แต่ละcolumnheaderและcachednumericก่อนเทียบ ผลรวม5subtotalตรงgrandtotal30350 เก็บlocatorของทั้งNSO/DEDEใน `evidence/nso-dede-components.json` เปอร์เซ็นต์และปีอื่นไม่นับเป็นcomparisonเพิ่ม

Coverageล่าสุด `evidence/cross-source-coverage.json`: **15/273 distinct NSO observations;อีก258ยังไม่เทียบ** ประกอบด้วยDEDErevised6ค่า (totalเดิม1+subtotalใหม่5) และDOEB9ค่าที่อยู่displayrounding ไม่เพิ่มsourceobservations,acceptedLCIหรือindependentmeasurementsverified(ยัง0) ไม่แก้ตัวเลขหรือสิทธิเดิม

Regressionใหม่3testsตรวจwrongheader/year/unit/cacheและกรณีค่าต่างโดยไม่แก้source;ชุดทดสอบรวมล่าสุด84testsผ่าน และreleaseaudit technical_pass=true โดยsubmission_readyยังfalse
