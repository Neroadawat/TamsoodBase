# SRS engineering addendum — 6 November 2026

ส่วนเสริมร่างเทคนิคSRS0.7.1 ไม่ใช่finalapproval;PDF27หน้าที่ render 9พ.ย. ยังไม่รวม addendum นี้.

FR-D01: NSO table/year/q<=160ต้องvalidatedในURLและreload/back/shareคงผลเดิม.
FR-D02: routeใหม่เห็นtitle/focus;backคืนตำแหน่งอ่าน;storyjumpไม่เสีย.
FR-D03: เลือก2observationsแสดงค่าดิบ/หน่วย/context6fields;different/missingเตือน;ไม่คำนวณratio/LCIA.
FR-D04: ชุดข้อมูลบอกcapabilities/metadataonly/rightsก่อนเปิด.
FR-T01: compacttransporthydrateครบ273rowsทุกfield;privateAPIยังno-store.
FR-T02: concurrentdatasetfailureไม่ถูกล้างด้วยsuccessอีกชุด;staleEPPOabort;client35s.
DB-Q01: exactfitDECIMAL(65,30),ไม่round/HOLDexcluded/sourceimmutable.
DB-W01: localworkflowactor/role/reason/hash/revision/audit;ไม่publishinternalหรือapprove science.
OPS-R01: consistent5schema/privateS3/checksumAES256;isolatedrestore/fullorderedfingerprintตรงlive;freshnessตรวจได้แต่ไม่ติดตั้งschedule.
NFR-A01: mobile320/390/keyboard/reducedmotion/automatedWCAG3หน้า;manualUAT/screenreaderยังค้าง.

Traceability:docs/review-implementation-2026-11-06.md และ evidence/review-implementation-2026-11-06.json. fullLCI=false/CO2e=null/humanapprovalยังไม่เปลี่ยน.
