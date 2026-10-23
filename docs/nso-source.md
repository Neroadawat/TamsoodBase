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
