# ชุดตรวจรับและซ้อมก่อนส่ง

นี่คือscriptซ้อม ไม่ใช่ผลการซ้อมของสมาชิก และไม่ใช่การยืนยันกำหนดส่ง ใช้ร่วมกับdemo-and-defense.mdและtasks.json

## เจ้าของเครื่องเตรียม

เปิดlocalserverตามREADMEเพียงหนึ่งตัว หากเปิดอยู่แล้วไม่เปิดซ้ำ ใช้ข้อมูลreleaseที่manifestระบุ อย่าเปลี่ยนexpectednumbersเพื่อให้ผ่านเมื่อข้อมูลไม่ตรง ให้ตรวจreleaseก่อน

| สิ่งที่เปิด | ผลที่คาดจากreleaseปัจจุบัน | ต้องอธิบาย |
|---|---|---|
| พร้อมใช้ต่อ / accepted | 97reference | ไม่ใช่97normalizedproductLCIหรือ97flowsอิสระ |
| พร้อมใช้ต่อ / hold | 4รายการ | contextไม่ชัดจึงแยกจากdefaultexportแต่รักษาหลักฐาน |
| ข้อมูลรายงาน / ไทยออยล์2024 | 12รายการจาก48selectedsourceobservations | total/componentsและboundaryต่างกัน ห้ามรวมทุกแถว |
| EPPO / intake / SPRC2024 | 12เดือนBBL/DAY | เป็นrateของบริษัท ไม่หารnationalMillionLitresเพื่อสร้างyield |
| NSO | 273observations | cross-sourceเทียบ15distinctเท่านั้น อีก258ยังไม่ได้เทียบ |
| งานวิจัย | 16source-reportedinventory | basis1000MJfuel,ปีวัดไม่ระบุ;BHD8พักแยก |
| DMF | raw34905/reject6/deduplicatedpending34671 | pendingไม่เท่ากับacceptedและtimebasisยังมีข้อจำกัด |

## ลำดับตรวจที่ต้องทำจริง

1. เลือกreferenceหนึ่งรายการ เปิดหน่วย/ปี/scope/sourcepage/hash แล้วเทียบต้นฉบับlocalที่มีสิทธิเปิด
2. ส่งออกตามตัวกรอง เปิดJSON/CSV ตรวจdecision/rights/usageprofileยังอยู่ ไม่สาธิตการเผยแพร่ไฟล์ที่ยังไม่clearrights
3. เปิดholdหนึ่งรายการ อธิบายissueและเหตุที่ไม่ปรับเลขเอง เปิดrejectlogเพื่ออธิบายstructuralfailureแยกจากsemanticuncertainty
4. เปิดschema/dictionary/mappingที่ตรงชุดข้อมูล รันSELECTตามsql/mysql/reusable-queries.sqlบนlocalworkspaceที่ตรวจowner อธิบายPK/FK/JOINและreleasefilter
5. เปิดevidence/pipeline-audit.jsonเพื่ออธิบายreplayที่เกิดจริง และtransaction-audit.jsonเพื่ออธิบายrollback/isolationของSQLiteสำเนาทดลอง ไม่ใช้UPDATEกับฐานจริงเพื่อโชว์
6. เปิดdata-model-selection.mdและmodel-comparison.json อธิบายว่าผลprojection/traversalไม่เท่ากับทดลองNeo4j/MongoDBengine
7. ทุกคนตอบหนึ่งคำถามเรื่องงานตนเองและชี้artifactจริง แล้วจึงกรอกcontribution/peerreview/reflectionตามที่ทำจริง
8. ตรวจประกาศAssignmentล่าสุดเรื่องเวลา/รูปแบบ/ช่องทางส่ง เจ้าของตรวจไฟล์ก่อนpushและตรวจTurned inด้วยตนเอง ไม่ถือว่าการมีแพ็กเกจคือส่งแล้ว

## หากเกิดปัญหาระหว่างเดโม

- โหลดข้อมูลไม่สำเร็จ: เปลี่ยนกลับหน้าเลือกชุดแล้วเข้าหน้าเดิม หรือปุ่มลองใหม่ ตรวจAPIปลายทางและอย่านำตารางเก่ามาอ้างว่าโหลดสำเร็จ
- อินเทอร์เน็ตล่ม: ใช้snapshot/evidenceที่เก็บไว้ในเครื่องตามสิทธิ ไม่อ้างว่าเรียกต้นทางสด
- Dockerไม่ได้เปิด: แสดงschema/query/evidenceที่บันทึกโดยระบุว่าไม่ใช่livequery แล้วแก้เครื่องก่อนซ้อมใหม่ ไม่แต่งผลสด
- คำถามเรื่อง5NF/coverage/สิทธิ: ใช้ข้อจำกัดที่บันทึกไว้ ไม่รับรองมากกว่าหลักฐาน

## ขอบเขตส่งต่อ

ส่งโค้ด/schema/docs/evidenceที่reviewแล้วได้ตามนโยบายทีม แพ็กเกจbackendมีderiveddataภายในจึงไม่ควรอัปโหลดpublicอัตโนมัติ `.local/`, PEM, secrets และrawสิทธิไม่ชัดไม่เข้าGitหรือเอกสารให้เพื่อน
