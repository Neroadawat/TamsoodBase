# Mapping และ validation สำหรับเปิดตรวจ

ทุกแถวด้านล่างเป็นกฎของระบบจริงตามชั้นข้อมูล ไม่ใช่การบังคับsourceทั้งหมดเข้าLCI_EXCHANGEเดียวกัน

| ชั้น / ต้นทาง | เป้าหมาย | Transform | Validation / ผลไม่ผ่าน | Evidence |
|---|---|---|---|---|
| DMF YEAR/MONTH | period_start / year_ce,month | ปีพ.ศ.ลบ543;parseเดือน | Gregorian1900–2100/เดือนถูกต้อง;rejectพร้อมเหตุผล | source_record snapshot+line, raw_json, hashes |
| DMF OIL/CONDENSATE/GAS | amount / decimal_value | Decimalคงความละเอียด;เก็บraw_value | finite/nonnegative,production_daysและcalendar;structuralreject | CSVpackage/line/column |
| DMF BLOCK_TYPE/BLOCK/FIELD | production_context | คงกลุ่มแหล่ง/พื้นที่;blankblockเป็นNULL | ไม่แตกกลุ่ม/ไม่แต่งจังหวัด;duplicateconflictพักทั้งกลุ่ม | metadataและrawfields |
| corporate label/year-column/value | metric / observation | คงsource metric ID;parseDecimal;raw×factor=scaled | page/year/column/hashตรง,scope/unitครบ;issuecontext→HOLD | document hash,pdf_page,printed_page,textline |
| corporate scope/unit | context/unit | รักษาboundaryและm3/year;MillionGJ→GJเฉพาะscale | ไม่หารreferenceproductหรือallocateเอง | mappingในreusable-model.md |
| NSO table/row/yearcolumn | national_statistic | parseperiod/Decimal;เก็บfootnotesและunit | headers/identity/additivechecks;ไม่promoteเป็นacceptedLCI | sourcehash/line/column,source_manifest |
| EPPO Year/Month/CompanyหรือProduct | observation | mapชื่อเดือน;คงsubjectและrate/quantitybasis | unit11_13=BBL/DAY,11_14=MillionLitres;unique(snapshot,year,month,subject) | sourcehash/CSVline/source_row |
| EPPO reimport | snapshot+typed+payload | INSERT OR IGNOREแล้วตรวจทุกtypedfieldและmetadataก่อนcommit | mismatch→rollback;ไม่เขียนreportสำเร็จ | import_eppo.py / system-integrity-followup.json |
| งานวิจัยTable4 | process / inventory_exchange | คงฐาน1000MJfuel,process/direction/unit/role | FAME/H-FAME16;BHD8แยกไม่ใช่บริบทไทย;ไม่เดาปีวัด | sourceDOMhash,row,column,articlecontext |

## กฎและสถานะที่ต้องแยกตอนตอบ

| Gate | ตรวจอะไร | หลักฐานจริง |
|---|---|---|
| Schema/completeness | datatype/required/PK/FK/CHECK | DDL, negative checks, pipeline audit |
| Provenance | source bytes/hash/locator/batchตามแหล่ง | acquisitionmanifest,source_report_replay,PDFtraceเดิม |
| Duplicate | identity/context/สำเนาเหมือนกัน/กลุ่มค่าขัดกัน | DMFreview;ไม่ใช้คนละURLแปลว่าไม่ซ้ำโดยอัตโนมัติ |
| Numerical | exactDecimal/scaling/typed/payloadตรงต้นทาง | MySQLroundtrip/replay;ไม่อ้างว่าต้นทางถูกต้องทางวิทยาศาสตร์ทุกค่า |
| Semantic | unit/time/geography/boundary/referencebasis | team-data-policy/context/issues;ไม่รวมคนละscope |
| Rights | ใช้ภายใน/แจกจ่ายได้หรือไม่ | rights_statusและredistribution_status ไม่เปลี่ยนตามqualitypass |

acceptedreferenceไม่เท่ากับnormalizedproductLCI;rejectไม่เท่ากับhold และstaged/pendingไม่เท่ากับaccepted คู่มือหน้า10–11ให้เก็บเหตุผลไม่ผ่าน ไม่ใช้จำนวนparserrowsเป็นverifiedvolume

เอกสารmappingละเอียด: ../mapping.md (DMFpilotพร้อมข้อจำกัด), ../mysql-full.md (fullDMF), ../reusable-model.md, ../nso-source.md, ../eppo-source.md, ../product-inventory.md
