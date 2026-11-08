## ล่าสุด 28 ตุลาคม T77
Cross-publication169/273 (141exact24round4divergence);104มีเหตุผลค้าง ดูdocs/source-completion-review.md พบปีDEDEพิมพ์2034จริง ไม่แก้เดา;SRS0.4PDF19หน้า/127testsผ่าน Productionไม่เปลี่ยน

ล่าสุด28ต.ค.:SRS0.3/PDF19หน้า;cross-source159/273=131exact24rounding4divergence;114ค้าง;124testsผ่าน อ่านPROJECT_STATE.md/primary-supply-2024-review.md ก่อนใช้ตัวเลขประวัติด้านล่าง

ตรวจข้อมูลล่าสุด28ต.ค.:NSO273identityมีreviewledgerครบ;เทียบอีกสิ่งพิมพ์145=118exact+23displayrounding+4divergence;128ยังต้องตรวจต่อ อ่านdocs/source-review-2026-10-28.md/evidence/nso-review-ledger.json ห้ามอ้างว่าผ่าน273cross-source เว็บEC2comparisonartifactยังไม่เปลี่ยน ผู้ใช้ให้ทำSRSต่อแล้ว:ร่าง0.2/PDF19หน้า ดูPROJECT_STATE.mdและevidence/srs-current-review.json

อัปเดต 28 ต.ค. 2569: ผู้ใช้ยืนยันให้Vercelไม่ต้องล็อกอินสำหรับตรวจงานแล้ว https://tamsoodbase.vercel.app ใช้server-only TAMSOOD_BACKEND_AUTHเรียกgateway;ใครมีURLอ่านข้อมูลได้ สิทธิข้อมูลไม่เปลี่ยนเป็นCLEARED อ่าน docs/VERCEL_LIVE_TH.md/evidence/vercel-deployment.json;ยังต้องอัปเดตTAMSOOD_BACKEND_ORIGINเมื่อQuickTunnelเปลี่ยน EC2ใช้MySQL8.4 backuprestore5ฐานผ่าน ไม่มีGitpush ไม่แก้Caddy/SG

# คู่มือรับช่วงงาน TamsoodBase

เว็บรุ่นเตรียมdeploy24ต.ค.: อ่านFRONTEND_DEPLOY_TH.md มีstaticbuild/configAPIorigin,เมนูมือถือ/hashnavigation/lazyload และไฟล์vercel.json/.vercelignore;ยังไม่ได้publishหรือเปิดbackendเป็นpublic

รอบตรวจทั้งกระบวนการ24ต.ค.: อ่าน [pipeline-audit.md](pipeline-audit.md) มี preflightDMF/typedSQLite/readiness/เว็บแก้staleผลและexportแล้ว โค้ดชุดนี้ยังไม่ขึ้นEC2; taskboardสร้างจากtasks.jsonและreleaseauditตรวจความตรงกัน

อัปเดต 24 ต.ค.: ตรวจ [normalization-audit.md](normalization-audit.md) ก่อนอ้าง 3NF/5NF พบ metric.document_id ซ้ำกับ context; มี candidate SQLite และ MySQLแยกtamsood_nf_c4a3f824c950ที่อ่านกลับตรง101/97แถว ยังไม่แทนฐานMySQLproduction/EC2 รัน `python scripts/audit_normalization.py` เพื่อสร้างSQLitecandidateใหม่จากฐานlocalปัจจุบัน

สถานะ ณ 23 ตุลาคม 2569 สำหรับเพื่อนและผู้ช่วย AI ของแต่ละคน อ่านคู่กับ tasks.md ซึ่งเป็นสถานะงานล่าสุด เอกสารนี้สรุปสิ่งที่ทำจริง ไม่ใช่คำรับรองจาก MTEC

## โปรเจกต์นี้ทำอะไร

รวมข้อมูลน้ำมัน ก๊าซ และเชื้อเพลิงของไทยจากเว็บ/CSV/PDF ให้อยู่ในฐานข้อมูลที่ค้นได้ เปิดหลักฐานต้นทางได้ และอธิบายการแปลง/ตรวจข้อมูลได้ เป้าหมายรายวิชาคือ UNDERSTAND → DESIGN → BUILD → DEFEND เว็บไซต์เป็นเครื่องมือสำรวจและสาธิต

## ทำมาแล้ว

| ข้อมูล | สิ่งที่ทำและผลปัจจุบัน | ยังห้ามอ้าง |
|---|---|---|
| DMF | 34905 raw;34899ผ่านรูปแบบ;6reject;42สำเนา;186แถวพักขัดกัน;34671pendingหลังแยกซ้ำ; MySQL/SQLiteและหลักฐานระดับแถว | ทุกแถวผ่านLCI; historicaltimebasisยืนยันแล้ว |
| Thai Oil/SPRC | 101 observationsสกัดซ้ำPDF;97ACCEPTED_REFERENCE/4HOLD_CONTEXT; relationalMySQL,CSV/JSON,restoreและSQLperformance | 97productLCI exchanges; สิทธิแจกจ่ายรายงานได้รับอนุญาตแล้ว |
| NSO | 5ตาราง273ค่า;18additivechecks;SQLite/MySQL;cross-source15distinctค่า;DEDErevised2024total30350และ5fuelsubtotalตรงโดยเก็บpreliminary28987แยก | ทุกค่าตรงข้ามแหล่ง; NSOเป็นการวัดอิสระจากDEDE/DOEB |
| งานวิจัยFAME/H-FAME | 16ค่าต่อ1000MJfuelจากTable4;SQLและsourceattribution;แยกBHD8ค่าต่างบริบท | fullLCI dataset/ค่าเฉลี่ยประเทศ; publicationyearคือmeasurementyear |
| EPPO | intake3012และoutput2922รวม5934ค่าจากCSV;1986–2026-07;MySQLอ่านกลับครบ;เว็บค้นและหลักฐาน | inputรายบริษัทหารoutputรวมประเทศเป็นyield;2026เต็มปี |

ระบบมีPythonpipeline,SQLite,MySQL8.1ผ่านDocker,APIและHTML/CSS/JS มีstatic frontend buildและVercelconfigแล้วแต่ยังไม่publish ดูFRONTEND_DEPLOY_TH.md เว็บไซต์ยังอ่านSQLite/JSON ไม่ได้อ่านMySQLโดยตรง ฐานMySQLแยกtamsood_research,tamsood_reusable,tamsood_supplemental,tamsood_eppoเพราะข้อมูลมีsemanticsต่างกัน

เทียบคู่มือภาพถ่ายหน้า3–20ล่าสุด: [handbook-alignment.md](handbook-alignment.md) รวม4packages/ช่องว่างจริง และ [data-model-selection.md](data-model-selection.md) ใช้ซ้อมCLO5โดยไม่อ้างว่าติดตั้งgraph databaseแล้ว

เทียบsyllabusที่ผู้ใช้ส่งใหม่: [syllabus-project-map.md](syllabus-project-map.md) รวมW01–W15/CLO เพิ่มscripts/audit_transactions.pyทดลอง6checksในสำเนาSQLiteทิ้งแล้ว ฐานต้นทางhashเดิม ดูevidence/transaction-audit.json ไม่ใช่ผลMySQLหรือpower-failure test

แผนล่าสุด [next-work-plan.md](next-work-plan.md): แก้lazyloadretryแล้ว มีevidence/frontend-retry.jsonและbackendimageรุ่นใหม่ตามbackend-image-audit.jsonแต่EC2ไม่เปลี่ยน เพิ่มlocalmodelprojection97records/8queriesตรงSQLไม่ใช่Neo4j/MongoDBrun พร้อม [final-walkthrough.md](final-walkthrough.md) สำหรับซ้อมจริง ไม่สร้างผลซ้อมหรือcontributionแทนสมาชิก

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

JavaScript request-behavior tests ใช้Node.js ถ้าไม่มีจะรายงานSKIP; Pythonwrapperเรียกไฟล์tests/web-request-behavior.cjsซึ่งต้องตามrepo/packageไปด้วย Normalization/replayintegrationtestsต้องมีlocalartifactsเช่นกัน

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

ผลtechnical_passไม่เท่ากับsubmission_ready และไม่ใช่MTECapproval; ผลล่าสุดหลังขยายcomparison15/273มี84testsผ่านบนเครื่องเดิม ไม่ใช่การรับรองเครื่องใหม่

## เพื่อนต้องทำอะไรต่อ

เลือกหนึ่งงานที่ตนรับผิดชอบก่อน ไม่ให้AIหลายคนแก้ไฟล์เดียวกันพร้อมกัน ตัวอย่างแบ่ง5คนนี้เป็นข้อเสนอ ไม่ใช่ประวัติงานที่ทำไปแล้ว:

| บทบาท | งานเริ่มต้นที่ตรวจได้จริง | สิ่งส่งกลับ |
|---|---|---|
| Domain/requirements | อ่านขอบเขต5ชั้น ตรวจคำจำกัดความและข้อกำหนดส่งจริง | source-backedrule/issueและrequirementsdiff |
| Petroleum/EPPO | ตรวจCSVsampleกับpublisherและหน่วย;พัฒนาacquisitionmanifestที่reproduceได้ | extractor/testsและsampletraceที่ระบุlocator |
| Gas/DMF | สืบhistoricaltimebasisหรือsourcegasใหม่อย่างมีขอบเขต | หลักฐานนิยามเวลา หรือเหตุผลคงhold ไม่เดาหน่วย |
| Database | ตรวจERD/FK/identity;ทบทวนvocabularyกลางโดยไม่ยุบscope | schema/migration/queryพร้อมผลตรวจroundtrip |
| Quality/integration | อ่านผลDEDErevisedที่อธิบายdifference1363ktoeแล้ว;ขยายcomparisonเฉพาะmetric/ปี/หน่วยตรงโดยไม่ทับpreliminary | comparisonพร้อมdenominator/coverageและrejectionreason |

งานร่วมที่ต้องทำจริง: ทุกคนเปิดsourceของหนึ่งtuple,รันSQL,อธิบายmapping/constraint,reviewงานเพื่อน และกรอกteam-contribution.mdด้วยวันเวลา/commit/ผลตรวจจริง

## วิธีทำงานผ่านGitและแชต

Repoกำหนดtextเป็นLFผ่าน.gitattributesเพื่อให้hashคงที่ข้ามเครื่อง ดู[ผลทบทวนportability](advice-review-portability.md) หากเห็นhashไม่ตรงให้ตรวจsnapshotและlineendingก่อน ห้ามแก้expectedhashหรือลบvalidationเพื่อให้ผ่าน หลังpullที่มีงานค้างอย่าใช้reset --hardเพื่อแก้ปัญหา

เริ่มจากpullสถานะล่าสุด สร้างbranchของงานตัวเอง ทำงานขนาดเล็กและตรวจส่วนกระทบ เปิดPRให้เพื่อนreviewก่อนmerge ห้ามสร้างcommitย้อนหลังหรือปลอมauthor การมีinitialcommitไม่ได้พิสูจน์contributionของสมาชิกทุกคน

ใช้ [CHATGPT_HANDOFF_PROMPT.md](CHATGPT_HANDOFF_PROMPT.md) เป็นข้อความเริ่มคุย ผู้ช่วยในแชตใหม่ไม่เห็นไฟล์หรือเครื่องนี้อัตโนมัติ ต้องเชื่อมrepoหรือให้ไฟล์ตามรายการก่อน อย่าส่ง.env/password/.local/rawที่สิทธิไม่ชัดให้แชต

## ก่อนเจ้าของpush

ดู `git status --short` และ `git diff --stat` เพื่อแน่ใจว่ารวมhandoff/auditล่าสุดแล้ว ตรวจรายชื่อไฟล์ที่จะcommitโดยเฉพาะcredentials/raw/lecture ผู้ช่วยยังไม่ได้commit/pushในคำขอนี้; ให้เจ้าของเลือกไฟล์และpushเอง

## Backend EC2ที่เพิ่มภายหลัง

26ตุลาคม: activeEC2รุ่นcdc51c36b5356c41,private127.0.0.1:8765,16routesผ่านทั้งstage/active,S3ถาวรiam-roleและbackup38membersผ่าน เก็บrollback-f2596ce38f984279ไว้ ไม่แตะGinder/Caddy ดูPRIVATE_BACKEND_OPERATIONS_TH.mdและevidence/ec2-upgrade.json/s3-backup.json/ec2-runtime-check.json S3ไม่ค้างbucket/roleแล้ว;publicdomain/HTTPS/accesscontrolยังค้างจริง

อัปเดตคืน24–25ตุลาคม: T42 ปิดช่องโหว่ audit แถวส่วนเกินและ EPPO verification หลัง commit แล้ว ตรวจ snapshot metadata/typed columns ก่อน commit พร้อม rollback เมื่อผิด ดู pipeline-audit.md และ evidence/system-integrity-followup.json ผล90testsผ่านและoffline pipeline replayผ่าน ข้อมูลจริงไม่พบ corruption จากสองกรณีนี้ ไม่ต้องรันชุดเดิมซ้ำหากไม่มีการเปลี่ยนแปลงหรือข้อกังวลใหม่ Runtimeเว็บ/image/EC2ไม่ได้เปลี่ยนในT42

มีprivatebackendบนEC2ของเพื่อนแล้ว ดูec2-backend.md ใช้SSHtunnellocal8876 ไม่ใช่publicURL และยังไม่ย้ายMySQLขึ้นEC2 S3moduleอยู่src/s3_storage.pyแต่ยังไม่มีbucket/role ห้ามนำprivatekeyไปใส่repoหรือแก้Caddy/Ginderที่ใช้80/443อยู่ หากต้องเปลี่ยนreleaseให้ตรวจownerก่อนเสมอ


## Final Project technical review — 27 ตุลาคม2569

ผู้ใช้ให้พักงานส่งแต่ละM/T55 เน้นระบบจริงตามfinal-project-system-review.md อ่าน12หน้าและเทียบ25ประเด็น เพิ่มinventorygraph16exchanges/4queriesตรงSQLโดยไม่อ้างNeo4jengine Tests101ผ่าน ชุดหลักฐานส่งเดิมไม่ได้regenerateในรอบนี้เพราะผู้ใช้ให้ยังไม่ยุ่งงานส่ง

## User resumed final deliverables — 27 October
คำสั่งล่าสุดให้ทำSRS/Finalต่อแล้ว แทนคำสั่งพักก่อนหน้า มีร่างdocs/submission/SRS.mdบท1–8และFINAL_DELIVERY_PLAN.mdพร้อมtraceability/storyboard/10slideoutline T55/T58IN_PROGRESS ยังไม่ใช่PDFfinalหรือส่งแล้ว สมาชิกต้องเติมข้อมูล/review/memo/consentจริง Localimage50d950acd1b6880dผ่าน16routes EC2ยังcdc51c36b5356c41 ไม่มีpublicdomain

## Latest autonomous delivery pass — 27 October
Sourcecontract13snapshots/5layers/APIและinternalCSV/JSONLเสร็จ;candidateFlow15/Unit4/process2/exchange16แยกproduction;104testsผ่าน;SRS16pages/slides10pages/PPTXdraftพร้อมnotes;Neo4jstartup2attemptsfailedexit3ไม่อ้างengineผ่าน;activeprivateEC2c2d8db16b10a2fad17routes,S3backup39membersและrollbackpreflightผ่าน Ginderunchanged Publicdomain/authและhumanmemo/consent/contribution/videoยังค้าง ใช้docs/final-gap-plan.mdผลล่าสุด อย่าวนอ้างภาพprojectionเป็นengineหรือทดสอบเดิมซ้ำโดยไม่มีchange

## Latest — 6 November 2026 expert review delivery
Read PROJECT_STATE T114–T117 and docs/review-implementation-2026-11-06.md before continuing. New discovery/story/theme/fontassets are required: explicit cleanroom now17sources/14assets. Vercel deployment and rollback are in evidence/current-frontend-release.json. 226tests+15finaltargeted/live browser/axe passed scoped;freshS3backup+localrestore5schemas passed. EC2APIimage unchanged. Workflow/numericprojection are isolated candidates, not production migrations or human approvals. Scientific/stableendpoint/human gates remain open. Drive C very low; do not run disk-heavyfulltests/builds without checking free space or delete unrelated files.
