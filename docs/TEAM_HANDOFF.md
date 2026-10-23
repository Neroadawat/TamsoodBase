# คู่มือรับช่วงงาน TamsoodBase

สถานะ ณ 23 ตุลาคม 2569 สำหรับเพื่อนและผู้ช่วย AI ของแต่ละคน อ่านคู่กับ tasks.md ซึ่งเป็นสถานะงานล่าสุด เอกสารนี้สรุปสิ่งที่ทำจริง ไม่ใช่คำรับรองจาก MTEC

## โปรเจกต์นี้ทำอะไร

รวมข้อมูลน้ำมัน ก๊าซ และเชื้อเพลิงของไทยจากเว็บ/CSV/PDF ให้อยู่ในฐานข้อมูลที่ค้นได้ เปิดหลักฐานต้นทางได้ และอธิบายการแปลง/ตรวจข้อมูลได้ เป้าหมายรายวิชาคือ UNDERSTAND → DESIGN → BUILD → DEFEND เว็บไซต์เป็นเครื่องมือสำรวจและสาธิต

## ทำมาแล้ว

| ข้อมูล | สิ่งที่ทำและผลปัจจุบัน | ยังห้ามอ้าง |
|---|---|---|
| DMF | 34905 raw;34899ผ่านรูปแบบ;6reject;42สำเนา;186แถวพักขัดกัน;34671pendingหลังแยกซ้ำ; MySQL/SQLiteและหลักฐานระดับแถว | ทุกแถวผ่านLCI; historicaltimebasisยืนยันแล้ว |
| Thai Oil/SPRC | 101 observationsสกัดซ้ำPDF;97ACCEPTED_REFERENCE/4HOLD_CONTEXT; relationalMySQL,CSV/JSON,restoreและSQLperformance | 97productLCI exchanges; สิทธิแจกจ่ายรายงานได้รับอนุญาตแล้ว |
| NSO | 5ตาราง273ค่า;18additivechecks;SQLite/MySQL;cross-sourceเทียบ7/273และยังมีข้อแตกต่าง | ทุกค่าตรงข้ามแหล่ง; NSOเป็นการวัดอิสระจากDEDE/DOEB |
| งานวิจัยFAME/H-FAME | 16ค่าต่อ1000MJfuelจากTable4;SQLและsourceattribution;แยกBHD8ค่าต่างบริบท | fullLCI dataset/ค่าเฉลี่ยประเทศ; publicationyearคือmeasurementyear |
| EPPO | intake3012และoutput2922รวม5934ค่าจากCSV;1986–2026-07;MySQLอ่านกลับครบ;เว็บค้นและหลักฐาน | inputรายบริษัทหารoutputรวมประเทศเป็นyield;2026เต็มปี |

ระบบมีPythonpipeline,SQLite,MySQL8.1ผ่านDocker,APIและHTML/CSS/JS ไม่มีfrontendbuild เว็บไซต์ยังอ่านSQLite/JSON ไม่ได้อ่านMySQLโดยตรง ฐานMySQLแยกtamsood_research,tamsood_reusable,tamsood_supplemental,tamsood_eppoเพราะข้อมูลมีsemanticsต่างกัน

ผู้ช่วย AI ช่วยเตรียมcode/docs/tests/reviewจำนวนมาก ทีมต้องตรวจและอธิบายงานเอง ไม่ใช้เอกสารนี้อ้างว่าเป็นcontributionของสมาชิกที่ยังไม่ได้ทำ

## อ่านตามลำดับนี้

1. README.md และ docs/tasks.md — ภาพรวมกับสถานะล่าสุด
2. docs/team-data-policy.md — acceptance/rights/ข้อห้ามรวมข้อมูลผิด
3. docs/dataset-model-index.md — ดัชนีschema/dictionary/mappingทั้ง5ชั้น
4. docs/reusable-model.md, supplemental-mysql.md, eppo-source.md — โครงสร้างจริง
5. docs/shared-plan-comparison.md — ช่องว่างจากแผน
6. docs/demo-and-defense.md และ team-contribution.md — หลักฐานมนุษย์ที่ยังต้องทำ

## Clone แล้วจะได้อะไร

ได้code,SQL,docs,tests,evidenceและweb ถ้าcommitไฟล์ใหม่ครบก่อนpush ข้อมูลต่อไปนี้ถูก.gitignoreและไม่ตามGit:

- `data/raw/`: CSV/PDF/DOMsnapshotsและmanifestต้นทาง
- `build/`: SQLite,JSONreports,SQLload,ZIPและscreenshots
- `.local/`: credentialsและruntimeส่วนตัว
- Docker named volume: ข้อมูลMySQLอยู่ในเครื่องเดิม ไม่ตามrepo

ดังนั้นcloneใหม่ยังเปิดเว็บพร้อมข้อมูลครบหรือรันreleaseauditผ่านทันทีไม่ได้ Evidenceในrepoเป็นผลจากเครื่องผู้พัฒนา ไม่ใช่หลักฐานว่าผู้cloneตรวจบนเครื่องตัวเองแล้ว

อย่าแก้ปัญหาด้วยการforce-add raw/.local/buildทั้งหมด ใช้การดาวน์โหลดจากpublisherหรือชุดข้อมูลส่งต่อที่ตรวจสิทธิแล้ว พร้อมตรวจhash ถ้าsourceเปลี่ยนอย่าเขียนทับsnapshotเก่าแล้วใช้evidenceเดิม

## เริ่มเครื่องใหม่

ติดตั้งPython3.12 และDockerDesktopจากผู้ผลิต ใช้Terminalที่rootrepo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-report.txt
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

บางintegrationtestsจะSKIPเมื่อไม่มีlocalsnapshots ต้องอ่านยอดskip ไม่ถือว่าทดสอบครบข้อมูลจริงแล้ว `compare_nso_doeb.py` ต้องการxlrdเพิ่มเติมหากทำงานนั้น; localfallbackเดิมไม่ตามGit

### สร้างข้อมูลใหม่จากต้นทาง

- DMF: `python -X utf8 scripts/run_pipeline.py --acquire` แล้วตรวจว่ารุ่นใหม่ตรงขอบเขตและผ่านchecks; ไม่รับประกันURLหรือค่าจะเหมือนsnapshotเดิม
- Thai Oil/SPRC: `scripts/acquire_thaioil.py --source thaioil` และ `--source sprc` ตามด้วย `scripts/run_reference.py` ต้องเข้าถึงPDFได้และตรวจhash หากHTTP403ให้ใช้ลิงก์ทางการในbrowser ไม่bypass
- NSO: ตามdocs/nso-source.md ดาวน์โหลดCSV5ไฟล์ผ่านbrowser แล้วใช้ `scripts/import_nso.py --download-dir <โฟลเดอร์ดาวน์โหลด>`; จากนั้น `scripts/review_nso.py`
- EPPO: ตามdocs/eppo-source.md ดาวน์โหลดCSV2ชุดพร้อมบันทึกmanifest/เวลา/hashก่อน `scripts/import_eppo.py`; manifestอยู่data/rawจึงต้องสร้างจากการรับข้อมูลจริง ห้ามคัดhashเดิมมาอ้างกับไฟล์ใหม่
- Inventory: ตามdocs/product-inventory.md ต้องมีDOMtableและcontextsnapshotที่ตรวจlayoutจริงก่อน `scripts/build_product_inventory.py`; PDFหรือHTMLrawแทนDOMtableไม่ได้โดยเปลี่ยนชื่อไฟล์เฉย ๆ

ขั้นตอนacquisitionยังไม่อัตโนมัติครบทุกแหล่ง เป็นงานที่ทำต่อได้ ห้ามสร้างrawสมมติเพื่อให้pipelineผ่าน

### เมื่อมีsnapshot/buildครบแล้ว

```powershell
python -X utf8 scripts/mysql_workspace.py --reports --reusable
python -X utf8 scripts/load_supplemental_mysql.py
python -X utf8 scripts/load_eppo_mysql.py
python -X utf8 src/explorer.py
```

เปิด http://127.0.0.1:8765/; ตรวจDockerให้พร้อมและอ่านdocs/mysql-full.mdก่อนรัน MySQL workspaceใช้volumeของแต่ละเครื่อง/networknone ไม่แชร์credentialsจาก.localของเพื่อน คำสั่งloadEPPOต้องมีcontainerที่เริ่มพร้อมแล้ว

```powershell
python -X utf8 scripts/check_release.py --tests
```

ผลtechnical_passไม่เท่ากับsubmission_ready และไม่ใช่MTECapproval; ผลล่าสุดหลังเพิ่มauditครอบคลุม5ชั้นมี60testsผ่านบนเครื่องเดิม ไม่ใช่การรับรองเครื่องใหม่

## เพื่อนต้องทำอะไรต่อ

เลือกหนึ่งงานที่ตนรับผิดชอบก่อน ไม่ให้AIหลายคนแก้ไฟล์เดียวกันพร้อมกัน ตัวอย่างแบ่ง5คนนี้เป็นข้อเสนอ ไม่ใช่ประวัติงานที่ทำไปแล้ว:

| บทบาท | งานเริ่มต้นที่ตรวจได้จริง | สิ่งส่งกลับ |
|---|---|---|
| Domain/requirements | อ่านขอบเขต5ชั้น ตรวจคำจำกัดความและข้อกำหนดส่งจริง | source-backedrule/issueและrequirementsdiff |
| Petroleum/EPPO | ตรวจCSVsampleกับpublisherและหน่วย;พัฒนาacquisitionmanifestที่reproduceได้ | extractor/testsและsampletraceที่ระบุlocator |
| Gas/DMF | สืบhistoricaltimebasisหรือsourcegasใหม่อย่างมีขอบเขต | หลักฐานนิยามเวลา หรือเหตุผลคงhold ไม่เดาหน่วย |
| Database | ตรวจERD/FK/identity;ทบทวนvocabularyกลางโดยไม่ยุบscope | schema/migration/queryพร้อมผลตรวจroundtrip |
| Quality/integration | สืบNSO–DEDEdifference1363ktoeและขยายเฉพาะmetricที่นิยามตรง | comparisonพร้อมdenominator/coverageและrejectionreason |

งานร่วมที่ต้องทำจริง: ทุกคนเปิดsourceของหนึ่งtuple,รันSQL,อธิบายmapping/constraint,reviewงานเพื่อน และกรอกteam-contribution.mdด้วยวันเวลา/commit/ผลตรวจจริง

## วิธีทำงานผ่านGitและแชต

เริ่มจากpullสถานะล่าสุด สร้างbranchของงานตัวเอง ทำงานขนาดเล็กและตรวจส่วนกระทบ เปิดPRให้เพื่อนreviewก่อนmerge ห้ามสร้างcommitย้อนหลังหรือปลอมauthor การมีinitialcommitไม่ได้พิสูจน์contributionของสมาชิกทุกคน

ใช้ [CHATGPT_HANDOFF_PROMPT.md](CHATGPT_HANDOFF_PROMPT.md) เป็นข้อความเริ่มคุย ผู้ช่วยในแชตใหม่ไม่เห็นไฟล์หรือเครื่องนี้อัตโนมัติ ต้องเชื่อมrepoหรือให้ไฟล์ตามรายการก่อน อย่าส่ง.env/password/.local/rawที่สิทธิไม่ชัดให้แชต

## ก่อนเจ้าของpush

ดู `git status --short` และ `git diff --stat` เพื่อแน่ใจว่ารวมhandoff/auditล่าสุดแล้ว ตรวจรายชื่อไฟล์ที่จะcommitโดยเฉพาะcredentials/raw/lecture ผู้ช่วยยังไม่ได้commit/pushในคำขอนี้; ให้เจ้าของเลือกไฟล์และpushเอง
