# สร้างเว็บสาธารณะจากชุดส่งต่อที่แยกแล้ว

Node.jsเป็นdependencyของfrontend ไม่ต้องมีPython/MySQL/rawPDFเพื่อสร้างหน้าเว็บ:

1. ใช้รายการไฟล์ใน scripts/verify_frontend_cleanroom.py หรือแพ็กเกจ build/vercel-upload
2. ตั้ง TAMSOOD_DEPLOY_MODE=proxy และ TAMSOOD_API_BASE_URL เป็นค่าว่าง
3. รัน node scripts/build_frontend.mjs ได้ output build/frontend
4. เมื่อเปิดแบบstatic หน้าB100โหลดmetadataได้เอง ส่วนdataset APIต้องเชื่อมVercelproxy/backendที่ตั้งค่าแล้ว
5. รัน python -m scripts.verify_frontend_cleanroom จากworkspaceเพื่อพิสูจน์buildในtemporarydirectoryที่ไม่มีraw/private inputs;ผล evidence/frontend-cleanroom.json

การตรวจนี้รับรองเฉพาะpublicfrontend ไม่ใช่clean-room rebuildฐานวิจัยทั้งหมด ซึ่งต้องมีsourceacquisitionที่ได้รับสิทธิและenvironmentตามREADME ไม่ควรแนบrawสิทธิไม่ชัดเพื่อทำให้เพื่อนรันผ่าน ห้ามแนบ .local, .env, PEM หรือbackups

ก่อนส่งGitต้องreviewdiff/untrackedfilesและmanifestจริง งานนี้ไม่commit/pushแทนผู้ใช้ และไม่ถือโฟลเดอร์buildบนเครื่องนี้เป็นสิ่งที่cloneจะได้มาเอง
