# ทบทวนคำแนะนำเรื่องการส่งต่อและ hash

คำแนะนำจาก https://chatgpt.com/share/6adb4039-c29c-83ec-9019-b8fd61c40f37 อ่าน23ตุลาคม2569 (เวลาไทย) เป็นreviewจากอีกenvironment ไม่ใช่หลักฐานว่ารันระบบบนเครื่องนี้ซ้ำแล้ว

## ผลตรวจเครื่องผู้พัฒนา

- ก่อนปรับ `scripts/check_release.py` ยังtechnical_pass=true แต่ `git ls-files --eol` พบsrc/build_reusable.pyเป็นw/crlfและcore.autocrlf=true
- manifestที่มีอยู่ในเครื่องนี้ตรงbytesCRLFของimplementationสองไฟล์ จึงไม่สรุปว่าreleaseเครื่องนี้เสียเหมือนเครื่องผู้review แต่การเปลี่ยนlineendingตอนcheckoutทำให้cross-machinehashต่างได้จริง
- เพิ่ม.gitattributesให้textใช้LFและระบุbinaryสำหรับPDF/ภาพ/Excel/SQLite/ZIP ไม่เปลี่ยนrawsnapshot
- ปรับCRLF→LFเฉพาะtrackedtext53ไฟล์ รักษาการแก้ไขเชิงเนื้อหาที่มีอยู่ก่อน; ไม่stage/commit/pushหรือแก้globalGitconfig
- regressiontestใช้temporaryGitrepoตรวจว่าfixture.pyแบบCRLF/LFได้normalizedGitobjecthashเดียวกัน ขณะที่fixture.pdfแบบbinaryยังต่างกัน ไม่มีการสร้างcontribution/commitในrepoจริง
- rebuildreferenceและSQL/packageevidenceตามbytesใหม่แทนการแก้expectedhashให้ผ่านเฉย ๆ ผลสุดท้ายต้องอ่านevidence/git-portability-review.json

## สิ่งที่คำแนะนำตรงกับข้อค้างเดิม

Cloneไม่รวมraw/build/Dockervolume; Pythonไม่มีในเครื่องเพื่อนเป็นปัญหาenvironmentของเครื่องนั้น ไม่ใช่เหตุให้เปลี่ยนstackทั้งหมด วิธีsetup/รับsnapshotอยู่TEAM_HANDOFF.md ยังไม่มีone-commandacquisitionครบทุกแหล่ง; browsercaptureบางแหล่งต้องตรวจด้วยมนุษย์

Cross-sourcecoverageเก่า7/273ในreviewเป็นsnapshotก่อนหน้า ปัจจุบันอ่านevidence/cross-source-coverage.json; เมื่อเพิ่มexact-labelsulfur-diesel2022–24เป็น10/273ยังไม่เปลี่ยนindependentmeasurementsverifiedจาก0

คำว่าunitmasterหรือschemaกลางยังเป็นข้อจำกัดจริง: modelหลายชุดแยกกันและwebอ่านSQLite/JSON ไม่ใช่MySQLโดยตรง ต้องนำเสนอตามที่ทำจริง

## วิธีรับช่วงหลังpull

1. เก็บงานที่ตนกำลังแก้ด้วยวิธีปกติของทีมก่อนpull ไม่ใช้reset --hardเพื่อแก้lineending
2. ตรวจ `git check-attr text eol -- src/build_reusable.py` ควรได้text:set/eol:lf
3. ตรวจ `git ls-files --eol` เพื่อแยกindexกับworkingtree; .gitattributesไม่บังคับworkingtreeเดิมที่มีงานค้างให้เปลี่ยนทันที
4. ใช้pipelineสร้างreleaseจากsnapshotที่hashตรง และตรวจreleaseใหม่ ไม่ใช้evidenceของsnapshotเก่ามายืนยันข้อมูลใหม่
5. หากต้องrenormalizeindex ให้เจ้าของตรวจdiffและเลือกstageเอง ไม่force-addraw/.local/build

ไม่รับประกันว่าเครื่องอื่นพร้อมจนกว่าจะมีผลsetup/tests/pipelineจริงของเครื่องนั้น
