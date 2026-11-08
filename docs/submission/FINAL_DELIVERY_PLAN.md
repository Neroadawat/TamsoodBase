## สถานะล่าสุดสำหรับเตรียมส่ง — 8 พฤศจิกายน 2569

SRS Markdown0.7.1เดิมสร้างPDFใหม่27หน้าตรงsourcehashและตรวจภาพแล้ว ดู [ผลตรวจรับช่วง](../explorer-performance-fix-2026-11-08.md) กับ `evidence/srs-current-review.json` ยังเป็นร่างรอทีมรับรอง;slides/PPTXยังไม่ได้rebuildรอบนี้ คงงานข้อมูลสมาชิก/consent/peerreview/finalfreezeจริงไว้ ไม่มีการส่งงานหรือรับรองfullLCI ข้อความรุ่นเก่าในตารางถัดไปเป็นประวัติ

## สถานะเดิม 30 ตุลาคม 2569

SRS0.5/PDF21หน้าเป็นร่างรอทีมตรวจ;ข้อมูลต้นน้ำ42และconversion16แยกกัน เว็บเผยแพร่แล้ว ดู [แผน12ข้อ](../expert-review-action-plan.md) และ PROJECT_STATE.md ก่อนใช้ตัวเลข/รุ่นในประวัติด้านล่าง ไม่ได้ส่งFinalหรือรับรองfullLCIแล้ว

# แผนจากระบบปัจจุบันถึงส่ง Final

ผู้ใช้อนุญาต27ตุลาคมให้กลับมาทำ SRS และชุดส่งทุก milestone แล้ว ลำดับนี้แทนคำสั่งพักงานเอกสารก่อนหน้า การเตรียมไฟล์ไม่เท่ากับ upload/submit

| ลำดับ | ชิ้นงาน | ทำได้ตอนนี้ | ข้อค้างจริง |
|---|---|---|---|
| 1 | SRSเล่มต่อเนื่องบท1–8 | SRS0.4 PDF19หน้าและMDมีDR/BR/FR/NFR/traceability;renderตรวจแล้ว | ข้อมูลทีมและteamreviewจริง |
| 2 | Requirement→schema→query→evidence | matrixบท6และDDL4ชุด | source-IDcrosswalk/ตรวจdomainเพิ่มตามหลักฐาน |
| 3 | ERD/pipeline/dictionary | generatorและreviewbundleเดิม | freezeจากDDL/releaseที่ส่งจริงแล้วrenderตรวจใหม่ |
| 4 | Validated dataset CSV + SQL | เลือกexportตามชั้นและสิทธิ;ไม่ปน97referenceเป็นLCI | ตรวจsource_idทุกexportและสิทธิผู้รับก่อนแนบ |
| 5 | Memoอย่างน้อย1ต่อM | ใช้แบบฟอร์ม5วาระจากอาจารย์ | สมาชิกประชุมจริง:ประเด็น/ทางเลือก/มติ/เหตุผล/เจ้าของงาน |
| 6 | Peer review MP4≤5นาที | storyboardด้านล่าง | สมาชิกบันทึกจริง/รับpeerfeedbackจริง;ไม่สร้างผลreview |
| 7 | Slides PDF≤10หน้า | PDF10หน้าและPPTXupdatedถึง169/273และruntimeปัจจุบัน;renderPDFตรวจแล้ว | สมาชิกตรวจและซ้อมจริง;ไม่อ้างส่งแล้ว |
| 8 | Deployment/reviewer access | Vercelpublicfrontend/EC2MySQL/S3restoreพร้อมตามevidence | QuickTunnelยังชั่วคราว;ไม่มีdomain;ผู้ใช้ให้browserไม่loginโดยเก็บupstreamsecretฝั่งserver;ห้ามแตะGinder/Caddy |
| 9 | Final QA/freeze | ตรวจmanifest/hash/secrets/rights/links | teamreview/consent/deadline/channelยืนยันจริง |
| 10 | ส่งงาน | เตรียมreviewpackage | เจ้าของเลือกช่องทางและตรวจreceipt;ยังไม่ส่งแทน |

## โครงวิดีโอ Peer Review ไม่เกิน5นาที

0:00–0:35 ปัญหาและขอบเขตไทย; 0:35–1:20 requirements/แยกชั้นข้อมูล; 1:20–2:10 ERD/identity/keys; 2:10–3:15 demoหนึ่งค่า→sourceพร้อมunit/basis; 3:15–4:10 validation/hold/reject; 4:10–4:45 limitationและคำถามที่อยากให้peerช่วยตรวจ;4:45–5:00สรุป เก็บfeedbackที่เกิดจริงแยกจากscriptนี้

## โครงสไลด์10หน้า

1 Problem/Thai relevance · 2 Scopeและข้อมูล5ชั้น · 3 Requirements/usecases · 4 Architecture/pipeline · 5 ERD/keys/normalization · 6 Mapping/provenance · 7 Validationพร้อมactualresults · 8 Livequeryและtrace demo · 9 Value/limitations/rights · 10 Contributionsที่รับรองจริง/nextsteps

ทุกกราฟระบุหน่วย/ปี/scope ไม่บวกข้อมูลต่างชั้น ไม่ใช้คะแนนwidget100เป็นคะแนนทีม ไม่อ้างอันดับหรือชนะ

## เกณฑ์จบ

เอกสารกับschema/query/releaseตรงกัน,PDFอ่านได้,ลิงก์reviewerใช้ได้ตามสิทธิ,ไม่มีkey/rawที่สิทธิไม่ชัด,consentและmemoจริงครบ,ทุกคนอธิบายงานได้ แล้วจึงfreeze ไม่ทำเครื่องหมายเสร็จแทนสมาชิก
