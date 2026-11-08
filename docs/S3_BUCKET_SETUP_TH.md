# วิธีสร้าง S3 bucket สำหรับ TamsoodBase

คู่มือสำหรับเจ้าของ AWS account ทำผ่านหน้าเว็บ AWS Console ตรวจอ้างอิง 24 ตุลาคม 2569

**ทำส่วนที่ 1 ให้เสร็จแล้วส่งชื่อ bucket กับ Region กลับมาก่อนได้** ส่วน IAM/EC2 ให้เจ้าของ server ทำต่อภายหลัง คู่มือนี้ยังไม่ได้สร้างหรือเปลี่ยนทรัพยากร AWS ให้

## เราจะใช้ bucket ทำอะไร

เก็บไฟล์ของ backend แบบ **private** โดยแยกไว้ใต้ `tamsoodbase/` เว็บไซต์จะไม่เปิด bucket ให้คนทั่วไปเข้าโดยตรง S3 เป็นที่เก็บไฟล์ ไม่ได้แทนฐาน MySQL และยังไม่มีการ sync ฐานข้อมูลอัตโนมัติ

สิ่งที่ต้องมี: AWS account ที่มีสิทธิสร้าง S3 bucket และรู้ว่า EC2 ของเพื่อนอยู่ Region ไหน แนะนำให้ใช้ account เดียวกับ EC2 สำหรับวิธีเชื่อมต่อในคู่มือนี้

## ส่วนที่ 1 — สร้าง bucket ผ่านหน้าเว็บ

### 1. ดู Region ของ EC2 ก่อน

1. เข้า [AWS Console](https://console.aws.amazon.com/)
2. ค้นบริการ **EC2** แล้วเข้า **Instances**
3. เลือกเครื่องที่จะใช้กับ TamsoodBase
4. จด Region ที่เลือกอยู่มุมขวาบน เช่น **Asia Pacific (Sydney)** รหัส `ap-southeast-2`

ตัวอย่างในคู่มือนี้ใช้ `ap-southeast-2` ตามค่าเริ่มต้นใน backend แต่ **ต้องดูของเครื่องจริงก่อน** ถ้าเป็น Region อื่นให้ใช้ค่าจริงนั้น

### 2. เปิดหน้าสร้าง bucket

1. ช่องค้นหาด้านบน พิมพ์ **S3** แล้วเลือกบริการ **S3**
2. เข้า **General purpose buckets** หรือ **Buckets**
3. กด **Create bucket**

### 3. กรอกค่าตามนี้

| ช่องในหน้า AWS | ค่าที่เลือก |
|---|---|
| AWS Region | Region เดียวกับ EC2 ที่จดไว้ |
| Bucket type | **General purpose** |
| Bucket name | ตั้งชื่อของทีม เช่น `tamsoodbase-team-fuel-2026-a7k9` |
| Object Ownership | **ACLs disabled / Bucket owner enforced** |
| Block Public Access | เปิด **Block all public access** ไว้ทั้งหมด |
| Bucket Versioning | **Disable** สำหรับเริ่มต้น; ถ้าทีมต้องการเก็บรุ่นเก่า ค่อยเปิดโดยเข้าใจว่ามีพื้นที่เก็บเพิ่ม |
| Tags | ใส่ `Project = TamsoodBase` ได้ เป็นตัวช่วยจัดหมวด ไม่ใช่เงื่อนไขให้ระบบทำงาน |
| Default encryption | **Server-side encryption with Amazon S3 managed keys (SSE-S3)** |
| Object Lock | ไม่ต้องเปิดสำหรับงานนี้ |

ข้อควรรู้เรื่องชื่อ:

- ใช้ตัวพิมพ์เล็ก ตัวเลข และขีดกลาง เช่นตัวอย่างด้านบน
- ชื่อตัวอย่างอาจมีคนใช้แล้ว ถ้าแจ้งชื่อซ้ำ ให้เปลี่ยนท้ายชื่อ
- ไม่ต้องใส่ `s3://` หรือ `/tamsoodbase` ในช่อง Bucket name
- ไม่ใส่ชื่อบุคคล รหัสนักศึกษา หรือข้อมูลลับในชื่อ bucket

เลือก SSE-S3 ให้ตรงกับ backend ปัจจุบัน ซึ่งส่งค่า encryption เป็น `AES256` เมื่อ upload อย่าเลือก SSE-KMS ตามตัวอย่างของระบบอื่นโดยยังไม่ได้ตั้งค่า KMS ให้ตรงกัน

### 4. กดสร้างและตรวจผล

1. กด **Create bucket** ด้านล่าง
2. เมื่อสร้างสำเร็จ คลิกชื่อ bucket
3. แท็บ **Permissions**: ตรวจว่า **Block all public access = On** และ Object Ownership เป็น **Bucket owner enforced**
4. แท็บ **Properties**: ตรวจ **AWS Region** และ **Default encryption = SSE-S3**

**ไม่ต้อง** เปิด Static website hosting, ใส่ Public bucket policy หรือเพิ่ม CORS สำหรับ backend ชุดนี้ เพราะ browser จะคุยกับ backend และ backend จึงคุยกับ S3

AWS อธิบายค่าการสร้างและ Object Ownership ไว้ใน [Creating a general purpose bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) และการคง bucket เป็น private ใน [Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)

### 5. ทดลองเก็บไฟล์ธรรมดาใน Console — ทำเพิ่มได้

หาก account ของเจ้าของมีสิทธิ upload:

1. เข้า bucket → แท็บ **Objects** → **Create folder** ชื่อ `tamsoodbase`
2. เข้าโฟลเดอร์นั้น → สร้างโฟลเดอร์ `health`
3. สร้างไฟล์ข้อความในเครื่องชื่อ `s3-check.txt` มีแค่ข้อความ `TamsoodBase storage check`
4. ในโฟลเดอร์ `tamsoodbase/health/` กด **Upload → Add files** เลือกไฟล์นี้ แล้วกด **Upload**
5. กลับมาดูว่ามี object `tamsoodbase/health/s3-check.txt` แล้ว

การ upload ผ่าน Console สำเร็จพิสูจน์ว่า account ที่ล็อกอินทำได้ ยังไม่ได้พิสูจน์ว่า backend บน EC2 มีสิทธิแล้ว การเปิด Object URL แล้วเจอ AccessDenied ขณะไม่ได้ยืนยันสิทธิ ไม่ใช่เหตุให้เปิด bucket เป็น public

ใช้เฉพาะไฟล์ทดลองนี้ก่อน ไม่ upload `.pem`, `.env`, password, ไฟล์ lecture หรือ raw PDF/CSV ที่สิทธิแจกจ่ายยังไม่ชัด

## ส่งอะไรกลับมาให้ทีม

คัดลอกแบบนี้แล้วเติมข้อมูลจริง:

```text
Bucket name: <ชื่อ bucket ที่สร้างจริง>
AWS Region: <เช่น ap-southeast-2>
Prefix: tamsoodbase/
AWS account เดียวกับ EC2: ใช่ / ไม่ใช่ / ยังไม่แน่ใจ
Block all public access: On
Default encryption: SSE-S3
IAM role ที่ EC2 ใช้อยู่: <ชื่อ role หรือ ยังไม่มี / ยังไม่ได้ตรวจ>
```

**ไม่ต้องส่ง Access Key, Secret Key, session token หรือ private key** ชื่อ bucket กับ Region ไม่ใช่รหัสผ่าน

ถ้าสร้างได้แค่ bucket ให้ส่งข้อมูลส่วนนี้ก่อน ถือว่าส่วนสร้าง bucket เสร็จแล้ว ไม่ต้องเดาการตั้งค่า server ต่อเอง

## ส่วนที่ 2 — ให้ EC2 เข้าถึง bucket (สำหรับเจ้าของ server)

### 6. ตรวจ IAM role เดิมก่อน

เข้า **EC2 → Instances → เลือกเครื่อง → Security → IAM role**

- **มี role เดิม:** จดชื่อไว้ ไม่เปลี่ยนทับ เพราะเครื่องนี้มีบริการอื่นของเพื่อนอยู่แล้ว ให้เจ้าของตรวจแล้วเพิ่มเฉพาะ policy ของ TamsoodBase หากเหมาะสม
- **ยังไม่มี role:** เจ้าของสามารถสร้าง role สำหรับ EC2 ตามขั้นถัดไปได้

EC2 ผูกได้ครั้งละหนึ่ง IAM role การแทนที่ role เดิมอาจกระทบบริการอื่น และ instance role ไม่ได้แยกสิทธิให้ Docker แต่ละตัวโดยอัตโนมัติ ดู [Attach an IAM role to an instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/attach-iam-role.html)

### 7. สร้าง policy จำกัดสิทธิให้ bucket นี้

1. เข้า **IAM → Policies → Create policy**
2. เลือกตัวแก้ไข **JSON**
3. วาง JSON ด้านล่าง โดยแทน `REPLACE_BUCKET_NAME` **ทั้งสองตำแหน่ง** ด้วยชื่อจริง

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::REPLACE_BUCKET_NAME",
      "Condition": {
        "StringLike": {
          "s3:prefix": ["tamsoodbase/*"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::REPLACE_BUCKET_NAME/tamsoodbase/*"
    }
  ]
}
```

4. กด **Next** ตั้งชื่อ เช่น `TamsoodBaseS3ArtifactsPolicy` แล้วกด **Create policy**

นี่คือ **IAM identity policy** ใส่ใน IAM ไม่ใช่ช่อง **S3 Bucket policy** ตรงกับ template ใน repo `deploy/s3-policy.template.json` ให้สิทธิอ่าน/เขียนเฉพาะ prefix นี้ ไม่มี DeleteObject หรือสิทธิทุก bucket

ตัวอย่างนี้ใช้ bucket กับ role ใน account เดียวกัน หากอยู่คนละ account ให้แจ้งทีมก่อน เพราะต้องจัดสิทธิข้าม account เพิ่ม ไม่ใช่เปิด public

### 8. ผูก policy กับ role

**ถ้ามี role เดิมและเจ้าของอนุญาตให้ใช้:** เข้า **IAM → Roles → ชื่อ role เดิม → Add permissions → Attach policies** เลือก policy ที่สร้างเมื่อกี้ แล้วกดเพิ่ม โดยรักษา permissions เดิมของบริการอื่นไว้

**ถ้ายังไม่มี role:**

1. เข้า **IAM → Roles → Create role**
2. Trusted entity เลือก **AWS service**
3. Use case เลือก **EC2**
4. เลือก policy `TamsoodBaseS3ArtifactsPolicy`
5. ตั้งชื่อ เช่น `TamsoodBaseEc2Role` แล้วสร้าง
6. กลับ **EC2 → Instances → เลือกเครื่อง → Actions → Security → Modify IAM role**
7. เลือก role ที่เพิ่งสร้าง แล้วกด **Update IAM role**

ไม่ต้องสร้าง IAM user พร้อม access key เพื่อใส่ลง Git หรือแชต

## ส่วนที่ 3 — สิ่งที่ทีม backend จะทำต่อ

หลังทราบชื่อจริง ทีมจะตั้งค่าในไฟล์ของ backend บน EC2:

```dotenv
TAMSOOD_S3_BUCKET=REPLACE_BUCKET_NAME
TAMSOOD_S3_PREFIX=tamsoodbase
AWS_REGION=ap-southeast-2
```

เปลี่ยน Region ให้ตรงของจริงด้วย ไฟล์ runtime อยู่ `/home/ubuntu/tamsoodbase/backend.env` ไม่ commit ไฟล์ที่เติม secrets แล้ว

Docker ที่สร้างไว้แล้วจะไม่รับ environment ใหม่เพียงเพราะแก้ไฟล์นี้ ต้องส่งค่าผ่านขั้นสร้าง container รุ่นถัดไปและมีแผน rollback ไม่ใช่ restart บริการอื่นทั้งหมด

จากนั้นทีมจะตรวจ:

1. backend ใช้ instance role ได้จริงโดยไม่ฝัง access key
2. upload/download ไฟล์ทดลองที่ไม่มีข้อมูลจำกัดสิทธิผ่าน prefix `tamsoodbase/` ได้
3. ชื่อ bucket/Region/encryption ตรงกับค่าที่ตั้งไว้ และไม่เปิด public
4. บริการเดิมของเพื่อนยังทำงานตามเดิม

หาก host ใช้ role ได้แต่ Docker หา credentials ไม่เจอ ให้ส่งข้อความ error ที่ปิดบังข้อมูลลับมาให้ทีมตรวจ IMDS/network ของ container ก่อน ไม่ปิด IMDSv2 หรือเปลี่ยน role เดิมเพื่อแก้เอง AWS อธิบายกรณี container กับ metadata hop limit ใน [Instance metadata access considerations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html)

## ปัญหาที่พบบ่อย

| อาการ | วิธีเริ่มตรวจ |
|---|---|
| ชื่อ bucket ซ้ำ | เปลี่ยนท้ายชื่อเป็นตัวอักษร/ตัวเลขของทีม แล้วลองสร้างใหม่ |
| ไม่มีสิทธิ Create bucket / IAM | ให้เจ้าของ account หรือผู้ดูแลที่มีสิทธิดำเนินการ |
| Console upload ได้ แต่ backend AccessDenied | ตรวจ role ที่ backend ใช้จริงและ ARN/prefix ใน policy ไม่ใช่เปิด public |
| List bucket root ไม่ได้ | policy จำกัด prefix ต้อง list ใต้ `tamsoodbase/` ไม่ใช่ทุก object ใน bucket |
| NoCredentialsError | ตรวจการผูก role และการเข้าถึง metadata จาก container |
| PermanentRedirect / Region ไม่ตรง | ตรวจ Region ใน Properties และ `AWS_REGION` |
| ใช้ SSE-KMS แล้ว AccessDenied | กลับมาทบทวน encryption กับทีม; backend ปัจจุบันออกแบบให้ใช้ SSE-S3 |

S3 มีค่าใช้จ่ายตามการใช้งานพื้นที่และคำขอ ไม่ถือว่าใช้ฟรีตลอด ใช้ไฟล์ทดลองเล็กก่อน และตรวจหน้า Billing ของ account ตามปกติ
