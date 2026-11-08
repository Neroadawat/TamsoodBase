# ตรวจสิทธิ S3 หลังสร้าง bucket

**ปิดปัญหาแล้ว26ตุลาคม2569:** ภาพJSONจากเจ้าของพบspaceหลังชื่อbucketในResourceทั้งสองARN เจ้าของแก้และแจ้งบันทึกแล้ว ทดสอบซ้ำจากcontainerจริงผ่านlist/put/get,79bytesตรงhash,AES256 ดูevidence/s3-connectivity.json ไม่ต้องเพิ่มสิทธิหรือเปิดpublicตามวิธีอื่น ด้านล่างคงผลล้มเหลวเดิมและแนวตรวจไว้เป็นประวัติ ไม่ใช่สถานะค้างปัจจุบัน

ผลตรวจ26ตุลาคม2569 จากEC2ของทีม: Region `ap-southeast-2`, instance role `TamsoodBaseEc2Role` และPythonในcontainer `tamsoodbase-api` หาcredentialsได้ด้วยวิธี `iam-role` แล้ว แต่ `ListObjectsV2` ใน `tamsoodbase/health/` และ `PutObject` พร้อมSSE-S3ยังได้ `AccessDenied` HTTP403

ไม่มีobjectทดสอบถูกสร้าง ไม่เปลี่ยนcontainer/environmentถาวร ไม่แก้IAM/securitygroup/Caddy/Ginder และยังไม่ยืนยันว่าbackendเชื่อมS3สำเร็จ

## ให้เจ้าของบัญชีตรวจเฉพาะส่วนนี้

1. เข้าIAM → Roles → **TamsoodBaseEc2Role** → Permissions
2. ตรวจว่าpolicyของTamsoodBaseแนบกับroleนี้จริง ไม่ใช่แค่สร้างpolicyไว้เฉยๆ
3. เปิดpolicy versionที่ใช้งานอยู่ ตรวจชื่อbucketให้ตรง **tamsoodbase-team-fuel-2026-a7k9** ไม่มี `REPLACE_BUCKET_NAME` ค้างอยู่ และresourceของobjectลงท้าย `/tamsoodbase/*`
4. ไฟล์policyที่เติมชื่อจริงให้แล้วอยู่ `deploy/s3-policy.tamsoodbase.json` เป็นIAM identity policy ไม่ใช่S3 Bucket policy อย่าเปลี่ยนpermissionsอื่นของบริการเพื่อนหรือแทนที่roleเดิม
5. หากidentitypolicyตรงแล้ว ให้เจ้าของตรวจexplicit Denyในbucket policy/permissions boundary/องค์กรหรือVPC endpoint policy และยืนยันว่าbucketกับEC2อยู่accountเดียวกันตามคู่มือ การตรวจครั้งนี้ยังแยกสาเหตุเหล่านี้ไม่ได้
6. คงBlock all public accessและSSE-S3ไว้ ไม่แก้ด้วยการเปิดpublicหรือส่งAccessKeyให้ทีม

เมื่อเจ้าของแก้แล้วบอกว่าแก้ส่วนไหน ผู้ช่วยจะทดสอบซ้ำด้วยไฟล์ข้อความเล็กใน `tamsoodbase/health/` เท่านั้น หากต้องเพิ่มสิทธิผ่านbrowser จะให้เจ้าของยืนยันpolicyที่เจาะจงก่อนกดใช้ ไม่เพิ่มสิทธิทุกbucketหรือDeleteObject

ชื่อbucketและRegionไม่ใช่credentials ไม่ต้องส่งรหัสผ่าน, OTP, AccessKey, SecretKey หรือsessiontoken
