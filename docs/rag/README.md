# ต้นแบบค้นหลักฐานด้วย Qdrant

ต้นแบบใช้ FastEmbed สร้างเวกเตอร์จากการ์ดสาธารณะ 4 ใบใน `public-evidence.json` แล้วค้นด้วย cosine similarity บน Qdrant Local เก็บดัชนีใน `build/rag/qdrant` และเก็บโมเดลภาษาใน `build/rag/models` แต่ละผลมี ID ข้อความ คะแนน และตำแหน่งอ้างอิง คะแนนวัดความใกล้ของข้อความ ไม่ใช่ระดับความถูกต้องของคำตอบ

จากโฟลเดอร์โปรเจกต์ ใช้ PowerShell ดังนี้ การสร้างดัชนีครั้งแรกต้องดาวน์โหลดโมเดลและมีพื้นที่ดิสก์สำหรับ dependencies, cache และโมเดล

```powershell
python -m venv build/rag-verified-venv
& build/rag-verified-venv/Scripts/python.exe -m pip install --no-cache-dir -r requirements-rag.txt
& build/rag-verified-venv/Scripts/python.exe scripts/rag_retrieve.py index
$env:PYTHONIOENCODING = 'utf-8'
& build/rag-verified-venv/Scripts/python.exe scripts/rag_retrieve.py search "ทำไมเอทานอลยังไม่มี CO₂e ทั้งวงจร"
```

ทดสอบคำถามเรื่อง CO₂e ทั้งวงจร สตาร์ตเย็นของรถ E10 และการจัดสรรไอน้ำ โดยตรวจว่า ID ของการ์ดเป้าหมายอยู่ในผลค้นและเปิดหลักฐานได้ ก่อนนำไปต่อโมเดลตอบคำถาม ต้องเพิ่มชุดทดสอบคำถามที่ไม่มีหลักฐาน และกำหนดวิธีปฏิเสธคำตอบที่ตรวจจากการ์ดไม่ได้

`inventory-lineage.cypher` เป็นตัวอย่างอ่าน Neo4j inventory lab ด้วยพารามิเตอร์ `$observation_id` ใช้เมื่อผลค้นหรือ API ให้รหัส observation ที่ตรวจแล้ว การ์ด FAQ ในต้นแบบยังไม่มีการจับคู่กับ ID ของ graph จึงแยกการค้นสองส่วนไว้ โมเดลตอบคำถามในอนาคตควรเรียก query ที่กำหนดไว้ล่วงหน้า

ทดสอบจริงวันที่ 8 พฤศจิกายน 2569 ด้วย FastEmbed 0.7.3 และ Qdrant Client 1.15.1 สร้างเวกเตอร์ 384 มิติครบ 4 การ์ดใน collection `public_evidence_7d05fcf2f1cf876be1ff` แล้วค้นในโหมดออฟไลน์จากโมเดลที่แคชไว้

| คำถามทดสอบ | ผลอันดับแรก | คะแนน cosine |
| --- | --- | --- |
| เอทานอลขาดข้อมูลอะไรถึงยังสรุปคาร์บอนตลอดวงจรไม่ได้ | ethanol-total-gap | 0.6579 |
| รถ E10 ตอนสตาร์ตเครื่องเย็นกินน้ำมันเท่าไหร่ | e10-cold-start | 0.6701 |
| โรงงานอ้อยผลิตไอน้ำกับไฟฟ้าจากอะไร | bagasse-steam | 0.7513 |
| สถิติอุตสาหกรรมต่างจากแบบจำลองวัฏจักรชีวิตยังไง | reference-vs-model | 0.7135 |
| วิธีปลูกกล้วยไม้ในกระถาง | ไม่มีผล | ก่อนกรอง 0.1889 |

ตั้งเกณฑ์ทดลอง 0.45 จากชุดนี้ ผลต่ำกว่าเกณฑ์จะคืน `[]` ควรปรับเกณฑ์ด้วยชุดคำถามอิสระก่อนเปิดใช้จริง Qdrant Local เปิดดัชนีได้ทีละโปรเซส Docker Engine ยังไม่พร้อมสำหรับทดสอบ Neo4j รอบนี้ ต้นแบบยังอยู่ในเครื่องและค้นหลักฐานได้โดยตรง

## เปิดหน้าถามข้อมูลในเครื่อง

```powershell
& build/rag-verified-venv/Scripts/python.exe scripts/rag_retrieve.py serve
```

เปิด http://127.0.0.1:8767/ แล้วเลือกตัวอย่างหรือพิมพ์คำถาม ระบบแสดงข้อความจากการ์ดพร้อมลิงก์ต้นทาง และแสดงสถานะเมื่อไม่พบหลักฐาน ทดสอบ HTTP ด้วยคำถามภาษาไทยแบบเปลี่ยนสำนวนสองข้อ พบการ์ดเป้าหมายอันดับ 1 และ 2 ตามลำดับ คำถามนอกเรื่องคืนรายการว่าง ส่วนคำถามว่าง ชนิดข้อมูลผิด และคำขอข้าม origin ถูกปฏิเสธ รุ่นนี้แสดงข้อความจากหลักฐานโดยตรง ยังไม่มี LLM เรียบเรียงคำตอบ

## ตั้งค่า Qdrant Cloud เมื่อมีคลัสเตอร์

ตั้ง `TAMSOOD_QDRANT_URL` และ `TAMSOOD_QDRANT_API_KEY` ใน environment ฝั่งเซิร์ฟเวอร์ ใช้คีย์ที่เขียนได้เฉพาะขั้นสร้างดัชนี และใช้คีย์อ่านในขั้นเปิดบริการ หากเปิดหน้าเดโมจากเครื่องให้ใช้คำสั่งต่อไปนี้หลังตั้งค่า

```powershell
& build/rag-verified-venv/Scripts/python.exe scripts/rag_retrieve.py --cloud index
& build/rag-verified-venv/Scripts/python.exe scripts/rag_retrieve.py --cloud serve
```

Cloud เก็บเวกเตอร์และหมายเลขรายการ ส่วน backend เก็บการ์ดและสร้าง embedding สำหรับคำถามด้วยโมเดลเดียวกัน รุ่นนี้ยังไม่ได้ทดสอบกับคลัสเตอร์จริง ตัวเซิร์ฟเวอร์เดโม bind เฉพาะ loopback สำหรับใช้งานในเครื่อง

## ทดลองเรียบเรียงคำตอบด้วย Gemini

หยุดเซิร์ฟเวอร์เดโมเดิมก่อน เพราะ Qdrant Local เปิดดัชนีได้ทีละโปรเซส สร้างคีย์ใน [Google AI Studio](https://aistudio.google.com/apikey) แล้วใช้ PowerShell 7 ในโฟลเดอร์โปรเจกต์

```powershell
$env:GEMINI_API_KEY = Read-Host 'Gemini API key' -MaskInput
& build/rag-verified-venv/Scripts/python.exe scripts/rag_retrieve.py serve --gemini
```

เปิด http://127.0.0.1:8767/ ระบบจะส่งคำถามและข้อความจากการ์ดสาธารณะที่ค้นพบไปยัง Gemini 2.5 Flash-Lite ลิงก์อ้างอิงมาจากการ์ดในเครื่องตามรหัสที่โมเดลส่งกลับ ถ้าค้นไม่พบ จะไม่เรียก Gemini หากโมเดลตอบผิดรูปแบบ อ้างรหัสที่ไม่มี หรือเรียกไม่สำเร็จ หน้าเว็บจะแสดงการ์ดเดิม เกณฑ์ตรวจรหัสอ้างอิงช่วยให้ลิงก์ย้อนกลับได้ ยังต้องทวนความถูกต้องของข้อความที่โมเดลเรียบเรียง

ทดสอบ HTTP กับ Qdrant Local จริงในโหมดค้นหลักฐาน และทดสอบการตรวจคำตอบ Gemini ด้วย response จำลองสำหรับกรณีอ้างอิงถูก อ้างอิงนอกชุด ขาดอ้างอิง โควตา และ timeout ยังไม่มีคีย์ใน environment ที่ใช้ทดสอบ จึงยังไม่มีผลเรียก Gemini จริง [เอกสาร Gemini API](https://ai.google.dev/api/generate-content)
