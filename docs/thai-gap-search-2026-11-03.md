# ตรวจแหล่งเติมช่องว่างไทยรอบถัดไป — 3 พฤศจิกายน 2569

ผู้ใช้ให้ค้นส่วนที่ขาดและตรวจต่อ เป็นงานT97 ไม่ใช่การปิดว่าfullLCIสำเร็จ

## พบแหล่งใหม่ที่ใช้ต่อได้ตามขอบเขต

รายงาน สวทช. ธันวาคม2564 ชื่อ “การศึกษาวัฏจักรชีวิตของการใช้พลังงานไปสู่ภาคขนส่ง และการคำนวณเปรียบเทียบรอยเท้าคาร์บอนในการใช้เชื้อเพลิงฟอสซิล เชื้อเพลิงยานยนต์ไฟฟ้า และเชื้อเพลิงชีวภาพ” 64หน้า

https://waa.inter.nstda.or.th/stks/pub/2022/20220110-life-cycle-energy-carbon-footprint.pdf

webreaderเปิดต้นฉบับได้และอ่านfootnote11 PDF45/print37:

| ค่า | จำนวน | หน่วย/บทบาท |
|---|---|---|
| B100FAME WtT | 1.7096 | kgCO2eq/litre, ผลcharacterizedที่รายงาน |
| B100 TtW | 0.1550 | kgCO2eq/litre, ผลcharacterizedที่รายงาน |
| B100FAME WtW | 1.8646 | kgCO2eq/litre, ผลรวมที่รายงาน |

Decimal arithmetic:1.7096+0.1550=1.8646ตรง ไม่ใช่independentvalidationของการวัด ไม่ใช่emissionfactorรับเข้าใช้ทันที ไม่ใช่3elementaryflows;scopeเป็นfuelWtWไม่รวมvehiclelifecycleตามexecutivesummary PDF2 ต้องตรวจunderlyingdata/methodเพิ่มเติมก่อนอ้างstrictThai-onlyทุกinput

ใช้เป็น **REPORTED_WTW_BENCHMARK_PENDING_SOURCE_SNAPSHOT** แยกจาก2020foregroundและTGO2026EF ห้ามบวกTGOproductionEFเข้ากับWtWtotal ห้ามใช้gCO2e/MJจนมีLHV/densityตรงcontext และห้ามใช้benchmarkปิดช่องtransport/treatmentinventory

ข้อจำกัดการตรวจ: downloadตรงถูกserverปิดconnection, screenshotผ่านwebtoolcachemiss จึงยังไม่มีlocalPDFhash/visualpageverificationของรายงานนี้ ไม่อ้างtwoextractors/ทุกcellverifiedหรือsource-readyimport ไม่มีretryวนURLเดิม ไม่มีการเผยraw

## แหล่งที่ไม่รับเติมโมเดลหลัก

1. รายงานมหาวิทยาลัยอุบลราชธานีเรื่องเครื่องผลิตไบโอดีเซลจากน้ำมันพืชใช้แล้ว: ผลค้นมีค่าความร้อน/ความถ่วงจำเพาะ แต่feedstockต่างจากpalmFAME และยังไม่ตรวจHHV/LHVชัด จึงไม่ใช้แปลงฐานของ2020/2013
   https://www.esanpedia.oar.ubu.ac.th/e-research/sites/default/files/Prachasanti_Triyasut_1.pdf
2. งานKMUTNBปี2018 “การผลิตกระแสไฟฟ้าและประสิทธิภาพการบำบัดจากของเสียกลีเซอรอล...” เป็นmicrobialfuelcellระดับทดลอง ไม่ใช่POMEfullscaleplantของกรณีหลัก จึงไม่ใช้แทนwastewaterprovider
   https://www.journal.sci.kmutnb.ac.th/JournalVol/JournalVol.17No.1/JAppSci_V17N1_P0064_to_P0074.pdf
3. Fullchain2009repositoryเดิมcertificateหมดอายุ รอบก่อนจึงไม่รับsnippet;ไม่วนเรียกหรือปิดSSL
4. IIETA2025WTWarticleเปิดได้ แต่เป็นgasoline-ethanol/EVpassengervehiclecomparison ไม่ใช่palmFAMEtransport/treatmentinventory จึงไม่ใช้ปิดgateนี้
   https://www.iieta.org/journals/ijsdp/paper/10.18280/ijsdp.200306

## งานที่ยังขาดจริง

transportแต่ละขา+distributionที่ตรวจต้นฉบับได้, LHV/densityของเชื้อเพลิงตรงstudy, quantitativePOME/EFBtreatmentและmethaneleakage, useCH4/N2O, allocationapplication/FFBinput/backgroundThaiorigin สิ่งที่ค้นเจอแต่contextไม่ตรงจะไม่รับเพื่อให้จำนวนครบ

รอบนี้ไม่มีข้อมูลรับเข้าmodel ไม่มีproductionchange ไม่รันทดสอบชุดเดิมซ้ำเพราะเป็นsource-screening/doc-only ค่าทั้งสามของbenchmarkเป็นreportedresultไม่ใช่modeloutputของเรา
