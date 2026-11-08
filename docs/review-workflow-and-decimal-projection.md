# Local database evolution candidate — 6 November 2026

`src/decimal_projection.py`, `scripts/build_decimal_projection.py`: สร้าง numeric query projection แยกจาก sealedstore โดยคง raw_text/sourceidentity. DECIMAL(65,30) รับจำนวนเต็มไม่เกิน35และทศนิยมไม่เกิน30หลัก ต้อง finite;เกินต้องNULL/excluded ไม่roundหรือFLOAT. Unitขาด/HOLDถูกกันออก. Sumข้ามunit/contextยังห้ามแม้SQLทำได้.

ตรวจ MySQL8.4.13ใน owned container/networknone/noports ครบ460rows/453eligible/7excluded พร้อม ORDER BY numeric และ invalideligibleNULLได้3819. Source DB hashไม่เปลี่ยน. SQL/JSON projectionใน build/decimal-projection เป็นinternalไม่ส่งpublic.

`sql/review-workflow.sql`, `src/review_workflow.py`: draft/review/publish/retract contract; actor/role/reason/hash/expectedrevision,append-onlyevents,immutablecontentidentity,transactionrollback. INTERNAL_ACTIVITY_REVIEWห้ามpublish และ workflowนี้ไม่อนุมัติ science/fullLCI.

นี่เป็นlocalcontractภายใต้trustedDBwriter ไม่ใช่authenticationserviceหรือproofว่าสิทธิได้รับจริง. Productionต้องauthenticatedidentitybinding/DBgrants/rights evidence/signoffจริงก่อน. Testsใช้TEST_FIXTURE_ONLYไม่สร้างhumanreviewerจริง.

FD: review_release.id→hash,scope,state,revision; review_event.event_id→release,from,to,actor,role,evidence,reason,time. ไม่สมมติ actor→role หรือ hash uniqueness. Numeric(kind,identity)เป็นkeyแต่derived amount/rawเก็บซ้ำเพื่อaudit จึงไม่อ้างBCNF/5NFจากPKอย่างเดียว. Productioncorporateกับnormalizedcandidateเป็นคนละartifact;ดูdocs/normalization-audit.md. ไม่มีEC2migrationในรอบนี้.
