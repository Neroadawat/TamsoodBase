# แผนปิดช่องว่างก่อนส่ง Final — 27 ตุลาคม 2569

**สถานะใหม่กว่า 8 พฤศจิกายน:** รายการ F01–F12 ด้านล่างเป็น baseline เก่า ไม่ใช่รายการที่ยังไม่ได้ทำทุกข้อ ดู [คู่มือรับช่วง](TEAMMATE_NEXT_STEPS_TH.md) และ [ผลแก้ล่าสุด](explorer-performance-fix-2026-11-08.md) ก่อน Neo4j/MySQL lab มีผลจริงแล้วและ SRS0.7.1 PDFสร้างใหม่27หน้าตรงsource;finalfreezeยังรอhuman/rights/scientific/release gates ไม่ใช้คำว่าไม่มีNeo4jในประวัติด้านล่างแทนสถานะปัจจุบัน

ยังเหลือ **12 กลุ่มงาน** ไม่ใช่12บั๊กหรือเปอร์เซ็นต์สำเร็จ: 8กลุ่มที่ผู้ช่วยทำต่อได้,1กลุ่มdeployที่ทำได้บางส่วนและต้องมีปลายทางจริง,3กลุ่มต้องใช้หลักฐาน/การลงมือจากทีมด้วย รายการนี้เป็นbaselineก่อนรอบล่าสุด;ผลใหม่ดูสถานะด้านล่าง ไม่ใช้การมีไฟล์แทนteamreview

| ID | ลำดับ | งานค้างและเกณฑ์จบ | ผู้ดำเนินการ/สถานะ |
|---|---|---|---|
| F01 | P0 | ยืนยันขอบเขตนำเสนอและLCI:ใช้16foregroundexchangesอย่างตรงไปตรงมา;ถ้าจะอ้างrefineryLCIต้องมีFU/boundary/allocationจริง | ผู้ช่วยทำdomainreviewได้;ห้ามแต่งข้อมูล |
| F02 | P0 | Source-IDcrosswalk:registry→snapshot/hash→CSV/API;ตรวจidentityไม่ชน/ไม่มีorphan | ผู้ช่วย;ยังไม่ทำครบ |
| F03 | P0 | Schema:ตรวจdependencies,Flow/Unitcandidateและconstraintmigration;queryroundtripก่อนเปลี่ยนฐานจริง | ผู้ช่วย;direction/roleDDLใหม่ผ่าน แต่ฐานเดิมยังไม่migrate |
| F04 | P0 | Requirement→SQL→ผลจริง:queryทุกusecase/traceabilityรวมtransaction/index/engineที่ใช้สาธิต | ผู้ช่วย;Neo4jยังprojectionไม่ใช่engine |
| F05 | P0 | SRS:ร่าง1–8→เติมภาพ/dictionary→ตรวจความตรงrelease→PDFตรวจทุกหน้า | ผู้ช่วยร่างได้;ข้อมูลทีม/reviewต้องจริง |
| F06 | P0 | Dataset/SQL/ERD/pipelinepack:source_id/rights/hashตรงrelease ไม่มีsecret/rawสิทธิไม่ชัด | ผู้ช่วย;packเดิมยังไม่freezeตามDDLล่าสุด |
| F07 | P1 | Slides≤10หน้า+speaker/demo script:ภาพอ่านได้และไม่อ้างผลเกินจริง | ผู้ช่วย;มีoutline ยังไม่มีdeckPDFตรวจแล้ว |
| F08 | P1 | WebsiteUX:task-firstnavigation,metadataก่อนreuse,filter/empty/error/mobile/keyboard QA | ผู้ช่วย;เริ่มรอบนี้ เพิ่มทางลัดตามงานที่ต้องทำ |
| F09 | P0 | Deploy/revieweraccess:latestprivateimage→HTTPS/auth/CORS→ตรวจจากreviewerdevice→backup/rollback | ร่วม;ไม่มีdomain ไม่เปิดpublicdataหรือแตะGinder/Caddy |
| F10 | P0 | Memo/consent/contribution/peerassessment:สมาชิกประชุมและรับรองจริงครบ | ทีม;ผู้ช่วยเตรียมแบบฟอร์มได้แต่กรอกผลแทนไม่ได้ |
| F11 | P0 | PeerreviewMP4≤5นาที+ซ้อมdefense:สมาชิกอธิบายและรับfeedbackจริง | ทีม;ผู้ช่วยมีstoryboardและคำถามซ้อม |
| F12 | P0 | ยืนยันวัน/ช่องทาง/สิทธิผู้รับ→finalfreeze→ownerส่งและเก็บreceipt | ทีมร่วมผู้ช่วยQA;Teams/Formและเวลาบางส่วนยังไม่ชัด |

## ลำดับทำงาน

F02→F03→F04ควบคู่F01 แล้วF05/F06/F07;F08ปรับเป็นชิ้นเล็กที่ตรวจได้;F09ทำprivateต่อได้ก่อนpublicendpoint;F10/F11เริ่มโดยสมาชิกได้เลย ไม่ต้องรอเว็บเสร็จ F12หลังเอกสารกับreleaseตรงกัน ห้ามปิดงานเพียงเพราะมีไฟล์

ใช้tasks.jsonบันทึกการทำงานจริง รายการ12นี้เป็นfinalacceptanceworkstreams ไม่ใช่ผลรวมtaskเก่า ไม่รับประกันคะแนนหรืออันดับ เมื่อไม่มีหลักฐานใหม่ไม่วนreextract/build/testเดิม

## UX reference ที่เลือก

ใช้แนวทางค้นพบข้อมูลและอ่านmetadataก่อนreuseจาก [European Data Portal search guide](https://dataeuropa.gitlab.io/data-provider-manual/how-to-search/search-for-datasets/) และ [Eurostat dataset information](https://ec.europa.eu/eurostat/web/user-guides/data-browser/introduction-navigation-data/dataset-information) ไม่คัดลอกasset/codeหรือclaimuserstudy นำมาใช้เป็นtaskentryที่อธิบายระดับข้อมูลและชวนเปิดหลักฐานก่อนexport

## ผลดำเนินการรอบล่าสุด

- F01: ขอบเขตส่งร่างใช้reference/statisticsแยก16source-reportedforegroundexchanges ไม่อ้างfullrefineryLCI;ข้อจำกัดต้นทางยังคง
- F02: ปิดtechnicalcrosswalkแล้ว 13source snapshots/5layers;API+internalCSV/JSONL;IDเดิมไม่เปลี่ยน
- F03: candidateFlow15/Unit4/Process2/Exchange16ตรวจroundtrip+4queries+3negativechecksผ่าน;productionmigrationยังไม่ทำและไม่จำเป็นต้องอ้างเพื่อส่งcandidateanalysis
- F04: MySQL17checksและSQL/indexมีหลักฐาน;Neo4jengineเริ่มไม่สำเร็จ2รอบ จึงยังไม่ครบactualengineexperiment
- F05/F07: มีPDFรายงาน16หน้า/สไลด์10หน้าและPPTXพร้อมnotes;ตรวจrenderPDFแล้ว รอข้อมูลทีม/รับรอง ไม่ถือfinalsigned
- F06: rebuildERD/pipelineจากDDLล่าสุดและแพ็กเอกสาร/deriveddataภายในแยกกัน พร้อมmanifestตรวจhash ไม่แจกpublic
- F08: หน้าSourceIDครบ13snapshotsและสิทธิ;browsermobile390x844ไม่มีoverflow375/375;taskentryและinventoryผ่าน
- F09: privateEC2อัปเกรดc2d8db16b10a2fad,stage/active17routes,S3backup39membersและrollbackpreflightผ่าน;publicHTTPS/auth/domainยังค้าง
- F10/F11/F12: เตรียมMEMBER_INPUTSและstoryboardแล้ว แต่ยังต้องประชุม/consent/contribution/MP4/defense/ช่องทางและreceiptจริง

ไม่มีข้ออ้างว่าNeo4jผ่าน,ได้5NFทั้งระบบ,เปิดpublicหรือส่งงานแล้ว
