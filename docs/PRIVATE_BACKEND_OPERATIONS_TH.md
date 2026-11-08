## สถานะปัจจุบันที่บันทึกไว้ — 30 ตุลาคม 2569

หลักฐานล่าสุด `evidence/ec2-upgrade.json` ระบุ backend dea667bbd79dc1d9 และ production MySQL;Vercelเปิดใช้งานแล้วผ่านserver-onlyupstreamsecret/QuickTunnelชั่วคราว ข้อมูลreleaseเก่าด้านล่างเป็นประวัติ **อย่าใช้คำสั่งapplyที่อ้างรุ่นเก่ากับruntimeโดยไม่ตรวจowner/currentrelease/rollbackจริงก่อน** ดู PROJECT_STATE.md และ docs/expert-review-action-plan.md ผลนี้ไม่ใช่การตรวจEC2liveรอบใหม่

## สถานะล่าสุด27ตุลาคม (แทนreleaseในประวัติด้านล่าง)

Active c2d8db16b10a2fad;17routesผ่านstage/active;SourceIDAPI13snapshots;rollback-cdc51c36b5356c41เก็บไว้และpreflightผ่าน S3backup39membersผ่าน ดูevidence/ec2-upgrade.json,s3-backup-latest.json,ec2-rollback-preflight-latest.json ยังprivate127.0.0.1:8765และไม่แตะGinder/Caddy

# ดูแล backend และ S3 ที่ตั้งค่าแล้ว

อัปเดต26ตุลาคม2569: active release **cdc51c36b5356c41** บน EC2 เดิม สลับจาก **f2596ce38f984279** หลัง staging ที่127.0.0.1:18765ผ่าน16routes แล้วตรวจactiveที่127.0.0.1:8765อีก16routesพร้อมassertions97reference/273NSO/16inventory/12SPRC2024

## ตำแหน่งใช้งานจริง

| รายการ | ค่า |
|---|---|
| Active container | tamsoodbase-api |
| Active image | tamsoodbase-api:cdc51c36b5356c41 |
| Server bind | 127.0.0.1:8765 → container8000; ไม่เปิดpublic |
| Runtime env | /home/ubuntu/tamsoodbase/backend.env; mode0600 |
| S3 bucket / Region / prefix | tamsoodbase-team-fuel-2026-a7k9 / ap-southeast-2 / tamsoodbase/ |
| AWS credentials | Instance role TamsoodBaseEc2Role; ไม่ฝังAccessKey |
| Rollback container | tamsoodbase-rollback-f2596ce38f984279; หยุดไว้ไม่ลบทิ้ง |
| Previous environment | backend.env.before-cdc51c36b5356c41; mode0600 |
| Upgrade report | /home/ubuntu/tamsoodbase/active-upgrade.json |

ไฟล์backend.envมีค่าS3ถาวรแล้ว Containerใหม่รับค่าผ่าน--env-fileจริง ไม่ใช่แค่แก้ไฟล์แล้วrestart ส่วนCORSยังไม่เพิ่มpublicoriginและไม่มีการเปลี่ยนIAM/securitygroup/Caddy/Ginder

## เปิดจากเครื่องพัฒนา

```powershell
ssh -i .local/ec2-deploy.pem -N -L 127.0.0.1:8876:127.0.0.1:8765 ubuntu@54.206.67.32
```

เปิดhttp://127.0.0.1:8876/ ขณะtunnelทำงาน หาก8876มีtunnelเดิมอยู่ไม่ต้องเปิดซ้ำ URLนี้เป็นlocaltunnelไม่ใช่URLสาธารณะให้คนอื่นใช้

## สำรองและตรวจคืนจาก S3

ทำบนEC2:

```sh
python3 /home/ubuntu/tamsoodbase/backup_private.py --release cdc51c36b5356c41
```

ผลสำรองจริงอยู่ `evidence/s3-backup.json` เก็บarchive38files/4,353,650bytesที่:

```text
tamsoodbase/backups/cdc51c36b5356c41/ed04d0345c5f6546ba63bb0fa93aa39794712a8b92880a7ccc8da8d9ac3efb7a.tar.gz
```

SSE-S3=AES256, metadataSHA256, conditionalcreateไม่เขียนทับobjectเดิม ถ้ามีchecksumเดิมจะreuse แต่ต้องมีเหตุให้ตรวจซ้ำ ไม่ตั้งdailybackupของsnapshotเดิมให้วนโดยไม่มีข้อมูลเปลี่ยน

ขอบเขตคือallowlistedruntimearchive: code/web/derivedSQLite/JSON/source metadataที่จำเป็นตามprivateprofile ไม่มีrawCSV/PDF/lecture/privatekey/.env/logs และไม่ใช่backupMySQLทั้งเครื่อง ข้อมูลderivedภายในยังไม่รับสิทธิแจกจ่ายpublicใหม่

การตรวจrestoreรอบนี้ดาวน์โหลดarchiveกลับและอ่านสมาชิกทุกไฟล์เทียบmanifest/hashในmemory ไม่ได้แทนฐานproductionหรือทดสอบfreshEC2ทั้งเครื่อง หากต้องกู้เครื่องใหม่ให้ตรวจscope/สิทธิ/manifestแล้วสร้างimageและทดสอบloopbackก่อนswitchตามupgradeprocedure

## Rollback เมื่อจำเป็น

ตรวจแบบread-onlyก่อน (เป็นdefault ไม่มี--apply):

```sh
python3 /home/ubuntu/tamsoodbase/rollback_private.py --current cdc51c36b5356c41 --previous f2596ce38f984279
```

preflightผ่านจริงแล้ว26ตุลาคม ตรวจowner/release/loopback/envcheckpoint ห้ามใช้dockerpruneหรือลบrollbackcontainer

หากเจ้าของตัดสินใจย้อนจริงจึงเพิ่ม `--apply` คำสั่งจะหยุดเฉพาะบริการเรา เก็บcontainerใหม่เป็นretired แล้วเริ่มรุ่นเก่า หากเริ่มรุ่นเก่าไม่ได้พยายามคืนรุ่นใหม่ที่เก็บไว้:

```sh
python3 /home/ubuntu/tamsoodbase/rollback_private.py --current cdc51c36b5356c41 --previous f2596ce38f984279 --apply
```

**ยังไม่ได้รัน--applyในรอบนี้** การย้อนใช้environmentรุ่นก่อนซึ่งยังไม่มีS3config ต้องตรวจใหม่หลังrollback ไม่อ้างว่าเพียงมีscriptคือได้ทดสอบdisasterrecoveryครบ

## ข้อค้างก่อนเปิดผ่านโดเมน

- ชื่อdomain/subdomainและผู้ควบคุมDNS
- แผนHTTPS/accesscontrolสำหรับข้อมูลใช้ภายใน เจ้าของserverต้องreviewroutingเพราะ80/443มีGinder/Caddyใช้อยู่
- ถ้าแยกfrontendบนVercel ต้องระบุHTTPSAPIoriginและCORSที่ตรงจริง; CORSไม่ใช่authentication
- หากใช้frontendและAPIoriginเดียวกันบนEC2จะลดขั้นตอนข้ามorigin แต่ยังต้องมีHTTPS/accesscontrolที่เหมาะสมก่อนเปิด

ยังไม่สร้างpublicroute,เปลี่ยนDNS,ซื้อdomain,เปิดS3publicหรือdeployVercel ไม่มีการเปลี่ยนบริการของเพื่อนเพื่อให้ระบบนี้ขึ้นได้
