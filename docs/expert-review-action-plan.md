# แผนแก้ตามคำวิจารณ์ LCI และเว็บฐานข้อมูล

เริ่ม 30 ตุลาคม 2569 ตามผู้ใช้ให้แก้ละเอียดและตรวจย้อนทุกข้อ ใช้ตารางนี้เป็น acceptance checklist ไม่ใช้จำนวน tests/tasks เป็นคะแนนคุณภาพหรือเปอร์เซ็นต์สำเร็จ

| ข้อวิจารณ์ | สิ่งที่ลงมือและตรวจแล้ว | สิ่งที่ยังปิดไม่ได้ |
|---|---|---|
| 1 Provenance | ตรวจ58payload/immutable source/parse audit/รุ่นข้อมูล | แหล่งใหม่ต้องผ่าน gate เดิมทุกครั้ง |
| 2 FU/Boundary | coverage5processes/แยก1000kgกับ1000MJ/หน้ากระบวนการ | ยังไม่ครบข้อมูลทั้งวงจร |
| 3 FAME case | foregroundพร้อมreviewJSONแบบกรองและsourceครบ | allocation/cutoff/backgroundขาดหลักฐาน |
| 4 Flow semantics | source-local51keys/15conversionlabels/provideridentityguards | global mapping/compartment/provider compatibilityยังไม่ยืนยัน |
| 5 Quality | ทั้ง5processesแสดงคุณภาพ สิทธิ เวลา และmodel readinessแยกกัน | ไม่มีmeasurementperiodหรือDQRที่พิสูจน์ได้ ห้ามเดา |
| 6 Schema | versioned candidate5process/58source/58parse audit;seal/immutability/rollbackจริง | ยังไม่migrateMySQL;ต้องทดสอบengine/parity/rollbackก่อนใช้จริง |
| 7 UX | browserlocal+production/มือถือ390/กรอง/Escape/downloadจริง | ยังไม่ใช่userstudyหรือสมาชิกตรวจรับ |
| 8 Evidence | rawคู่stored/footnote/locator/hash/website/PDFหน้าอ้างอิง | sourceURLปัจจุบันไม่รับรองsnapshotโดยตัวมันเอง |
| 9 Release | source/build/proxy/PDF/candidatehash audit;liveassetparity;exportsourceversion | finalfreezeและชุดส่งยังต้องเจ้าของรับรอง |
| 10 Resilience | APIhealth/retry/backuprestoreมีหลักฐาน/manualrecovery | QuickTunnelชั่วคราว โดเมนพัก;ไม่เปลี่ยนSG/Caddyเอง |
| 11 Security | อ่านparameterizedSQL/allowlists/read-only/rights/secret boundary;proxybounds/HEAD/errorchecks | ไม่ใช่pentest/loadtest และpublicURLไม่ใช่private |
| 12 Risk tests | 161testsรวมversion/process/rollback/parse/rights/allocation guards;browserdownloadroundtrip | testsไม่แทนscientificreviewหรือการซ้อมจริง |

## ลำดับลงมือที่ไม่ข้าม dependency

1. **T87 ทำแล้ว:** สร้าง release candidate manifest และ consistency checker ที่อ่านอย่างเดียว ไม่ deploy/migrate;ทดสอบการเปลี่ยนบริบทแม้ตัวเลขเดิมแล้วต้อง fail
2. **T88 ทำแล้วใน local:** Boundary coverage และ quality contract ของ5processes ผูกครบ58observation IDs/1HOLD แยก source extraction/cross-publication/independent measurement/time/model completeness ไม่สร้าง default zero หรือเปอร์เซ็นต์ความครบถ้วน; `evidence/boundary-coverage.json` ยังไม่เปลี่ยนเว็บ/API
3. ทบทวน source calculations ของ allocation/FFBinput อย่างมีขอบเขต;บันทึกพบ/ไม่พบและความเข้ากัน หยุดเมื่อไม่มีหลักฐานใหม่ ไม่วน URLเดิม
4. ปรับ UXหลักฐาน/หน้ากระบวนการตาม contract พร้อม browser ก่อน/หลัง deployเมื่อแก้หน้าเว็บจริง
5. ตรวจ schema/transformation/export/provider guards โดยไม่สลับฐาน productionจนมี tested package/ownercheck/rollback
6. ผูก SRS/diagram/dictionary/slides กับ candidate release แล้วตรวจ render;รายชื่อ/consent/contribution/peerreview ต้องสมาชิกจริง
7. ตรวจย้อนข้อ1–12 แล้วปิดเฉพาะเกณฑ์ที่ผ่านจริง ข้อที่ขาด sourceหรือสมาชิกยังเปิดอยู่ ไม่ใช้ไฟล์แผนแทนผลสำเร็จ

## Release candidate checker

`python -m scripts.audit_release_consistency`

อ่าน source snapshot hashes, upstream reviewed report, public projectionทุกfield, frontendmanifest/source/build และ SRS Markdown/PDF/render evidence สร้าง `build/release-candidate/manifest.json` กับ `evidence/release-consistency.json`

candidate_id เป็น hash ของไฟล์ที่ประกาศในmanifest ไม่ใช่Gitcommitหรือproductionreleaseid `recorded_deployments` อ้างหลักฐาน deployที่เก็บไว้เท่านั้น ค่า live_rechecked_this_run=false โดยตรง การตรวจผ่าน22จุดไม่รับรอง scientific completeness/สิทธิใหม่/สมาชิกอนุมัติ/สุขภาพproductionในเวลาปัจจุบัน

ไม่อัปโหลด manifest ภายในนี้ขึ้นเว็บโดยอัตโนมัติ ไม่มี env/credentials/raw content ในผลลัพธ์ หาก source/build/SRS เปลี่ยนให้ buildหรือrenderส่วนที่เปลี่ยนและรันตรวจใหม่ มีเหตุจากการเปลี่ยนแปลงจึงตรวจซ้ำได้

## ตรวจย้อนรอบแรก

T87–T88 เพิ่มการตรวจความสอดคล้องและ coverage contract ไม่ได้ปิดข้อ2–12ทั้งหมด: UIยังต้องนำ contractไปใช้และตรวจbrowser;allocation/FFBinput/backgroundยังขาด;productionไม่เปลี่ยน;quality_score=nullและmodel_ready=falseทั้ง5ตามหลักฐาน Tests154ผ่านรวมnegativecases stalebuild/stalePDF/เปลี่ยนcontextแต่คงamount/จับproviderผิดobservation/แอบapplyscaling ยังไม่อ้างindependentexpertreviewหรือLCAtoolcompatibility

## ตรวจย้อนรอบสอง: T89–T90

T89นำquality/boundary/usable-for/rightsเข้าupstreamUIจริง พร้อมsnapshotIDร่วมexport/modalraw-vs-storedและPDFpageclarification ตรวจbrowserก่อน/หลังdeployมือถือ/Escape/downloadroundtrip;T90เพิ่มstreamingexport32MiB/HEADnobody/erroronceguardsในVercelproxyและทดสอบผ่าน155tests/API27routes หลักฐาน docs/quality-contract-web-review.md ข้อ5/7/8/9/11/12พัฒนาเพิ่มแต่ไม่ปิดทุกacceptancegate

พบsourceใหม่NRCTpolicybrief20หน้า ตรวจyieldcontextแล้วไม่ตรงชุดที่ต้องใช้จึงไม่deriveFFBinput;allocationapplicationยังopen ไม่เพิ่มยอด ขณะเดียวกันSRS0.6มีการแก้จริงแต่PDFยัง0.5 releasecheckerจึงfaildocumenthash ไม่rewriteหรือรับรองfreezeจนrenderจากเนื้อหาที่นิ่งแล้ว

T91แก้documenthashด้วยsnapshotrender0.6แยก/21หน้าตรวจภาพ/hashก่อนpromote เก็บPDFเก่า ไม่แก้Markdown ผลกลับผ่านแต่teamreviewยังpending;T92ทบทวนNRCTpolicybriefและบันทึกไม่ใช้yieldต่างบริบทแทนmissingFFB จึงปิดเฉพาะงานตรวจcandidateไม่ปิดallocationgate

## T93–T94 และผลตรวจย้อนล่าสุด
เพิ่มversionedreview schemaพร้อมsourceimmutability/typed-payloadguards/sealedversions/parseauditครบ58รวมfootnotea และexportFAME/H-FAMEบนเว็บจริง ตรวจFAME10local/H-FAME6productionทุกfield/basis/null/footnoteพร้อมmobile390 มีdocs/versioned-inventory-design.mdและdocs/expert-review-checkback.mdเป็นผลตรวจ12ข้อ ไม่ทำเครื่องหมายว่าทั้ง12เสร็จสมบูรณ์เพราะscientific/externaldependenciesยังอยู่
