# ผลตรวจรายงาน สวทช. และการบำบัด POME ไทย — 3 พฤศจิกายน 2569

## ปิดข้อค้างการเก็บและตรวจต้นฉบับ

รายงาน สวทช.64หน้าที่ก่อนหน้านี้เก็บไฟล์ไม่ได้ ดาวน์โหลดสำเร็จด้วยcurlที่ตรวจTLSตามปกติ เก็บprivatePDF/hash/manifestที่data/raw/nstda-wtw-2021 ตรวจภาพPDF45/print37/footnote11และสองextractors(pypdf/pdfplumber) ค่าB100FAME WTT1.7096 + TTW0.1550 = WTW1.8646 kgCO2eq/litreตรงกัน

เป็นbenchmarkผลcharacterizedของรายงาน ไม่ใช่LCIรายสาร ไม่เอาไปบวกTGO2026productionfactorซ้ำ ไม่ใช้แทนrequiredtransport/treatmentprocess ไม่อ้างallbackgroundThaiverifiedหรือfullinventoryของเรา สถานะsourceverificationของสามค่านี้ดีขึ้นจากwebtextonlyเป็นlocalhash+สองextractors+ภาพจริงแล้ว

## แหล่งใหม่ตรงบริบทบำบัดไทย

Chotwattanasak & Puetpaiboon, **Full Scale Anaerobic Digester for Treating Palm Oil Mill Wastewater**, Journal of Sustainable Energy & Environment2(2011)133–136

- หน้าบทความ: https://so04.tci-thaijo.org/index.php/JSEE/article/view/9839
- PDFผู้พิมพ์: https://www.jseejournal.com/media/101/attachment/Full%20Scale%20Anaerobic_pp.%20133-136.pdf
- Site: Asian Palm Oil Co.,Ltd.,กระบี่ ไม่ใช่ค่าเฉลี่ยโรงงานไทยทั้งหมด
- ตรวจภาพTable2 PDF3/print135 ครบ4operatingpoints×5numericcellsเทียบสองextractors
- ตรวจอัตราที่รายงาน20m3biogas/m3wastewaterและ2.5kWh/m3biogas;ผลคูณ50kWh/m3เป็นderivedarithmeticpotentialตามอัตราที่รายงาน ไม่ใช่measurednetexport/avoidedgridcredit

ไม่ถือCH4content(%)หรือmethanegeneratedเป็นCH4ปล่อยสู่อากาศ:ยังไม่มีfugitiveleakage/flare/destructionefficiency/volumeconditionครบ ไม่เปลี่ยนm3เป็นkgโดยไม่มีtemperature/pressure/standardcondition และไม่หยิบค่าdefaultในสมการCDMของบทความมาใช้ให้กลายเป็นThai-onlymeasurement

ยังขาดwastewaterต่อFAMEbasis,pretreatmentboundary,auxiliaryenergy/reagents,sludge/post-treatment,netexportและallocation จึงเป็นquantitativetreatmentcandidateที่นำไปออกแบบscenarioได้ ไม่ใช่providerที่applyเชื่อมแล้ว

## ชิ้นงาน/ผลตรวจ

- scripts/review_thai_pome_benchmark.pyทำซ้ำการตรวจhash/tablecells/sourcephrasesและbenchmarksum
- build/thai-pome-benchmark-review/review.jsonและevidence/thai-pome-benchmark-review.json แยกtreatmentกับbenchmark
- testsใหม่3ข้อผ่าน:ทุกoperatingpoint,biogas≠fugitiveemissions/grosselectricity≠netcredit,benchmark≠fullLCI
- rightsNOT_CLEAREDคงเดิม เก็บprivate ไม่เปิดrawบนเว็บ ไม่เพิ่มยอดacceptedLCI ไม่เปลี่ยนEC2หรือproduction

## ข้อค้างที่ยังหาอยู่

transport/distributionที่ตรวจต้นฉบับได้,compatibleLHV/density,CH4/N2Ouse,FFBinput/allocation/referenceflow และThaioriginของbackground ข้อมูลใหม่รอบนี้ลดช่องว่างtreatmentcontextและปิดbenchmarkverification ไม่ได้ปิดscientificcompletenessทั้งหมด
