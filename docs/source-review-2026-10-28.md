# ตรวจแหล่งข้อมูลและข้อขัดกัน — 28 ตุลาคม 2569

ตรวจบัญชีNSOครบ273รายการว่ามีหลักฐานdirect-sourceจากsnapshotเดิมและมีสถานะcross-sourceใด ดู `evidence/nso-review-ledger.json` ไม่อ้างว่าทั้ง273ผ่านการเทียบอีกแหล่งแล้ว

ผลปัจจุบัน: เทียบอีกสิ่งพิมพ์ได้145/273 แบ่ง118ค่าตรงตัวเลขพิมพ์,23ค่าอยู่ในช่วงการปัดเศษของExcel,4ค่าต่างเกินช่วงและต้องทบทวน อีก128ยังไม่มีcomparisonที่ยอมรับได้ รายงานNSOและตัวเลขเดิมไม่เปลี่ยน

## หลักฐานเพิ่ม

- DEDE Energy Balance2023 ตาราง2/25/30/31 PDFหน้า27/50/54 เทียบใหม่100ค่าในปี2022/2023 ทั้ง100ตรงกัน ตรวจภาพตารางร่วมกับหัวตาราง หน่วย ปี และfootnotes โดยเฉพาะconsumptionไม่รวมHSD/fueloilผลิตไฟฟ้า รักษาค่าลบของprimarysupply ไม่รวมrenewableที่aggregateต่างกัน
- DOEBขยายเฉพาะชื่อdiesel9ชนิดที่ระบุชัด ใช้ลบช่องว่าง/casefold ไม่เทียบชื่อแทนกันหรือรวมB7กับธรรมดา ไม่เทียบvolumeกับmass รวม27ค่า23อยู่ในdisplayrounding

## สี่รายการที่ต้องทบทวน

| NSOปี2024 | NSOพันลิตร | DOEBพันลิตร | สถานะ |
|---|---:|---:|---|
| น้ำมันดีเซลหมุนเร็ว บี7 | 0 | 24,102,658.000000003 | SOURCE_DIVERGENCE_REVIEW_REQUIRED |
| บี7 ชนิดพิเศษ | 0 | 194,743 | SOURCE_DIVERGENCE_REVIEW_REQUIRED |
| บี7 ชนิดพิเศษ ยูโร5 | 0 | 38,435 | SOURCE_DIVERGENCE_REVIEW_REQUIRED |
| ดีเซลพื้นฐาน50PPM | 0 | 246 | SOURCE_DIVERGENCE_REVIEW_REQUIRED |

CSVต้นฉบับNSOเป็น0จริง ไม่ใช่parserเปลี่ยนช่องว่างเป็น0 ยังไม่ทราบว่าผู้เผยแพร่เปลี่ยนclassification/revisionอย่างไร จึงไม่ย้ายDOEBมาแทนNSO ไม่รวมseriesจากชื่อคล้ายกัน และไม่ใช้4รายการนี้เป็นหลักฐานcross-sourceผ่าน ตัวเลขfloatingpointของExcelเก็บตรงตามเดิม ไม่อ้างความแม่นยำเพิ่มจากdigitทศนิยม

## อีก128รายการ

- 50: ตารางภายนอกปี2024ยังไม่ได้สกัดเทียบครบ
- 3: renewableมีขอบเขตaggregateต่างกัน
- 27: fuelclassificationยังไม่มีmappingที่รับรองด้วยเอกสาร
- 21: NSOปี2025แต่DOEBsnapshotสิ้นสุด2024
- 9: NSOเป็นมวลแต่Excelภายนอกหัวตารางvolume
- 18: percentไม่มีcellภายนอกที่นำมาเทียบตรง ไม่สร้างpercentจากdivisionแล้วนับเป็นverificationอีกแหล่ง

## สิ่งที่แก้ในเครื่องมือ

เพิ่มguardDOEBในcoverage:ตรวจsourcehash/ปี/หน่วย/label/NSOidentity/การแปลงล้าน→พัน/ส่วนต่าง/roundingtolerance ปฏิเสธเมื่อบริบทเปลี่ยน และเพิ่มregressiontestsไม่ให้normalizeชื่อจน10ppmกลายเป็น50ppmหรือB7กลายเป็นธรรมดา

ผลรอบนี้เป็นหลักฐานในrepository ไม่ได้เปลี่ยนrelease/artifactบนEC2หรือSRSและไม่ได้แก้sourcevalue ประวัติsource-cell-audit41,223รายการยังเป็นผลจากsnapshotเดิม ไม่ใช่การรับรองความใหม่ของเว็บต้นทาง และmatchingสิ่งพิมพ์NSOกับหน่วยงานต้นทางไม่ใช่การวัดอิสระ
