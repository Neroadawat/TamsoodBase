# ตัวคำนวณ CO₂e และการตรวจซ้ำกับแหล่ง — 6 พฤศจิกายน 2026

## สิ่งที่ทำได้จริง
เพิ่มsrc/carbon_calculator.py:แปลงมวลก๊าซkg×GWP100เป็นkgCO2e พร้อมsourcehash/locator/method/basis/coverage ไม่อนุมานความครบจากการบวก ตัวคำนวณกิจกรรม×characterizedEFมีอยู่แล้วในsrc/thai_carbon.py;ไม่คูณGWPซ้ำกับEFหน่วยkgCO2e

partial_sumปฏิเสธต่างmethod/ต่างFU/coverageซ้ำและaggregateที่ระบุoverlap ไม่ได้ตรวจsemanticทุกboundaryอัตโนมัติ ผู้จัดข้อมูลยังต้องreviewoverlapจริง แม้ใช้คนละID

## ตัวอย่างจากกากน้ำตาลไทยในเอกสาร
ใช้Figure1(PDF2)น้ำเสีย106.8Lต่ออ้อย1tonne/BODประมาณ40gL;Table1(PDF3)88%เข้าบ่อ;Table3(PDF5)default0.22kgCH4/kgBOD ตรวจภาพTable3เพิ่มและสองtextparsersสำหรับfactorแล้ว ไม่อ้างเป็นThai-siteCH4measurement

- BODรวม =106.8×40÷1000 =4.272kgBOD
- BODไปบ่อ =4.272×0.88 =3.75936kgBOD
- CH4ประมาณ =3.75936×0.22 =0.8270592kgCH4
- ใช้GWP100=23ตามIPCC2001ที่COMPETEรายงาน(Table7footnote/PDF20) ได้19.0223616kgCO2eสำหรับส่วนมีเทนจากบ่อบนฐานดังกล่าว
- หารเอทานอล10.17Lต่อbatch ได้ประมาณ1870.44gCO2e/Lethanol สอดคล้องค่ารายงาน1870ที่ปัดเป็นจำนวนเต็ม ภายใน0.5gCO2e/L

นี่คือsource-methodreplayจากงานกลุ่มเดียวกัน ไม่ใช่independentvalidationหรือการวัดการปล่อยจริง ไม่ใช่wholeCFPและไม่ใช่EFปัจจุบันของTGO ไม่สลับAR6เข้าผลเก่าโดยไม่เปลี่ยนmethodlabel

## ผูกกับหน่วยการใช้งาน
ตามpartialforegroundที่ทำไว้ ระยะ13.46km/E10ประมาณ1.011269722L ต้องมีethanolfeedประมาณ0.101126972L ส่วนมีเทนจากบ่อที่คำนวณได้จึงประมาณ0.18915kgCO2eต่อการเดินทางนี้เท่านั้น ต้องรายงานคำว่าpond-onlyกำกับเสมอ ไม่เรียกว่าการปล่อยของรถหรือE10ทั้งหมด

## ส่วนที่ไม่เติมเป็นศูนย์
สวน/soilN2O/ปุ๋ย,โรงน้ำตาลและallocation,พลังงานผลิตเอทานอล,การรั่วและเผาไหม้ก๊าซที่กู้ได้,ขนส่งทุกขา,การผลิตgasolineและการใช้E10ในรถ ยังต้องมีข้อมูลก่อนรวม ตัวเลือกกู้ก๊าซ100%ไม่แปลว่าไม่มีGHGทั้งระบบ ต้องเพิ่มdigesterleakage/combustion/energyและจัดcreditsไม่ซ้ำก่อน

## ใช้และตรวจ
`python -m scripts.build_ethanol_carbon_demo` → build/ethanol-carbon-demo/report.json และevidence/ethanol-carbon-calculator.json

`python -m unittest tests.test_carbon_calculator tests.test_ethanol_demo -v` ผ่าน7tests รวมการปฏิเสธkgCO2eเข้าทางgascharacterization,gasoriginกำกวม,missingprovenance,nonfinite,mixedmethod/FU,duplicate/overlap และไม่ตัดphysicalmassด้วยeconomicallocation

ผลprivate/researchเท่านั้น rightsNOT_CLEARED ข้อมูลapprox/defaultมีสมมติฐานครบ ไม่แก้เว็บ/EC2/productionbaseline และCO2e_totalยังnullจนกว่าครบขอบเขต
