# Backend บน EC2 ของทีม

## สถานะที่ตรวจจริง

**สถานะล่าสุด26ตุลาคม2569:** อัปเกรดจริงเป็น`cdc51c36b5356c41`แล้ว มีS3configถาวรและinstance-roleaccessผ่านในcontainerใหม่ Staging/activeผ่าน16routes,activehealthy,unrelatedcontainerIDs/statesตรงเดิม เก็บรุ่น`f2596ce38f984279`เป็นrollbackcontainer ตรวจpreflightแบบread-onlyแล้ว สำรองruntimearchiveเข้าS3และdownloadตรวจ38membersผ่าน ดู[คู่มือดูแลล่าสุด](PRIVATE_BACKEND_OPERATIONS_TH.md),evidence/ec2-upgrade.json,s3-backup.json,ec2-runtime-check.json ข้อความreleaseเดิมด้านล่างเป็นประวัติการติดตั้งครั้งแรก ไม่ใช่activeปัจจุบัน

อัปเดต26ตุลาคม2569: ทดสอบS3จากcontainerจริงสำเร็จแล้วหลังเจ้าของลบspaceในResourceARN ใช้instance role `TamsoodBaseEc2Role`, bucket `tamsoodbase-team-fuel-2026-a7k9`, Region `ap-southeast-2` ผ่านListObjectsV2/PutObject/GetObjectในtamsoodbase/health/ ไฟล์ทดสอบ79bytesอ่านกลับตรงhashและSSE-S3=AES256 ไม่มีstaticcredentials คงmarkerไว้ ดูevidence/s3-connectivity.json การทดสอบใช้configเฉพาะprocessที่รันตรวจ ยังไม่แก้environmentถาวรหรือสลับrelease/ตั้งsyncข้อมูล ข้อความS3ที่ยังไม่configureด้านล่างเป็นประวัติการติดตั้งเดิม

ติดตั้งบริการ `tamsoodbase-api` บน EC2 ที่ผู้ใช้ระบุ `ubuntu@54.206.67.32` โดยแยกจากระบบGinderที่มีอยู่ พอร์ต80/443ของเครื่องนี้ใช้โดยCaddyของGinder จึงไม่ได้แก้Caddy,securitygroup,IAMหรือบริการเดิม

- Release `f2596ce38f984279`; image `tamsoodbase-api:f2596ce38f984279`
- Working release `/home/ubuntu/tamsoodbase/releases/f2596ce38f984279`
- Gunicorn/WSGI,2workers×2threads ภายในDocker; non-root UID10001,read-only filesystem,384MiB,CPU0.5,pids128,logrotation
- Docker publishเฉพาะ `127.0.0.1:8765` ของEC2 ไม่เปิดพอร์ตนี้สู่อินเทอร์เน็ต
- `/healthz`และ`/readyz`ตอบ200; Dockerhealthhealthy; ตรวจ13routesพร้อมdata assertionsจริง
- EC2ใช้สำเนาderivedSQLite/JSONสำหรับAPI ยังไม่ได้ย้ายMySQLจากเครื่องพัฒนาไปEC2 ไม่มีการใช้PostgreSQLของGinderร่วม
- ไม่มีrawCSV/PDF,lecture,privatekeyหรือ.localในdeploymentarchive มีเฉพาะDMFmetadataที่APIจำเป็นต้องอ่าน และderivedreports/SQLiteสำหรับทีมprivateuse ข้อมูลบริษัทไม่ได้รับสิทธิpublicredistributionเพิ่ม
- S3moduleพร้อมแต่ยังไม่configurebucket/roleและยังไม่upload/สร้างbucket

## ทดสอบผ่าน SSH tunnel

บนเครื่องของผู้ใช้เปิดTerminal:

```powershell
ssh -i "C:\Users\HP\Downloads\ginder-ec2.pem" -N -L 127.0.0.1:8876:127.0.0.1:8765 ubuntu@54.206.67.32
```

ถ้าต้นฉบับkeyมีACLกว้างเกินไป ให้ใช้สำเนาที่จำกัดสิทธิใน `.local/ec2-deploy.pem` บนเครื่องพัฒนาปัจจุบัน อย่าcommitหรือส่งkeyในGit เครื่องเพื่อนใช้pathkeyของตนเอง

เปิด http://127.0.0.1:8876/ และ http://127.0.0.1:8876/healthz ข้อมูลนี้มาจากEC2ผ่านSSH ไม่ใช่localexplorerที่8765 ต้องเปิดtunnelค้างไว้ ไม่ใช่publicURLที่ส่งให้ใครแล้วเปิดได้ทันที

## ดูแลบริการ

เชื่อมSSHแล้วตรวจเฉพาะบริการเรา:

```sh
docker ps --filter name=tamsoodbase-api
docker logs --tail 100 tamsoodbase-api
curl -fsS http://127.0.0.1:8765/readyz
docker inspect --format '{{ index .Config.Labels "org.tamsood.project" }}' tamsoodbase-api
```

labelต้องเป็นTamsoodBaseก่อนดำเนินการกับcontainer ไม่ใช้dockercomposeของGinder ไม่รันdockerpruneหรือหยุดcontainerอื่น

`--restart unless-stopped`ทำให้บริการกลับมาเมื่อDockerเริ่มใหม่ ข้อมูลruntimeในimageเป็นsnapshot ต้องสร้างreleaseใหม่เมื่อข้อมูลเปลี่ยน ไม่รันpipelineเขียนทับภายในreadonlycontainer

## การสร้างรุ่นถัดไป

1. ตรวจcode/data/testsในเครื่องพัฒนา แล้ว `python -X utf8 scripts/package_backend.py`
2. ตรวจbuild/deploy/manifest.jsonกับpackage.json อย่าtarทั้งrepoหรือforce-addbuild/raw/.local
3. ส่งarchiveและmanifestด้วยSCPไปโฟลเดอร์releaseใหม่บนEC2 ตรวจSHAก่อนextract/build
4. deploy/install_private.pyตรวจchecksum/memberallowlistและrefuseหากcontainerชื่อเดิมมีอยู่ ต้องวางแผนupgradeโดยตรวจownerและสำรองcontainerเดิมก่อน ไม่ลบทิ้งอัตโนมัติ
5. ทดสอบimageใหม่ด้วยชื่อแยกและพอร์ตloopbackว่างก่อนสลับ แล้วตรวจ13routesและrightsprofile คงรุ่นก่อนสำหรับrollback

การติดตั้งรอบนี้ไม่ได้setupCI/CDหรือpushGit ไม่มีการเปลี่ยนpublicrouting บริการนี้เป็นprivatebackendที่รอdomain/HTTPSและแผนaccessก่อนเปิดสาธารณะ

## S3 เมื่อได้ชื่อbucket

อัปเดต local 24 ต.ค.: `/readyz` ตรวจการอ่านฐานจริงและหน้าเว็บล้างผล/export เก่าขณะโหลดแล้ว ดู pipeline-audit.md การแก้ชุดนี้ยังไม่ถูกนำไปแทน image/container EC2 รุ่นเดิม ต้องตรวจ image ใหม่แยกและเตรียม rollback ก่อนสลับ

แพ็กเกจlocalรุ่น57ad16e4a4e8f790ตรวจallowlist/hashและbuildเป็นimageทดสอบแล้ว;13routesผ่านในcontainernetworknone/ไม่มีport หลักฐานevidence/backend-image-audit.json รุ่นนี้ยังไม่ได้ส่งขึ้นหรือสลับบนEC2

- ผู้ใช้แจ้งbucketและregionภายหลัง; ห้ามส่งAccessKey/SecretKeyในแชต
- ตั้งbucketprivate,BlockPublicAccess,defaultencryption และใช้prefixเฉพาะtamsoodbase/ พร้อมleast-privilege role ดูdeploy/s3-policy.template.json (ยังมีplaceholder ไม่ใช่policyที่applyแล้ว)
- เติมTAMSOOD_S3_BUCKET/AWS_REGIONใน `/home/ubuntu/tamsoodbase/backend.env` ด้วยowner-onlypermissions; templateอยู่deploy/backend.env.example ไม่มีsecret
- AWScredentialsใช้defaultproviderchain/roleที่เจ้าของอนุญาต ไม่คัดcredentialsของบริการเพื่อนมาใช้
- ตรวจbucketaccessด้วยartifactทดลองที่ไม่มีข้อมูลจำกัดสิทธิก่อน ไม่มีAPIอัปโหลดสาธารณะ การเรียกsrc/s3_storage.pyต้องเลือกartifactที่ตรวจสิทธิแล้วชัดเจน
- moduleS3ไม่ได้syncฐานข้อมูลอัตโนมัติ และไม่ทำให้rawของบริษัทแจกจ่ายได้

## อ้างอิงการเลือกแนวทาง

Pythonระบุว่าhttp.serverไม่เหมาะกับproduction จึงใช้Gunicornด้านหน้าrouteเดิมในWSGI: https://docs.python.org/3/library/http.server.html

AWSแนะนำS3privateและBlockPublicAccess: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html

AWScredentialproviderchain: https://docs.aws.amazon.com/boto3/latest/guide/credentials.html
