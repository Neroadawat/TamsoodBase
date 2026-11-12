// TamsoodBase final deck: 10 slides following the instructor's 8-step flow.
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5 in
pres.title = 'TamsoodBase — Data to Net Zero Day';
pres.author = 'S2-G05';
const FONT = 'Leelawadee UI'; // ships with Windows; Thai-capable
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

const C = { pine: '143A30', pine2: '1F5245', leaf: '2F7D62', rust: 'C2572D', sand: 'F4ECDC',
  cream: 'F0C9A0', ink: '1D2A25', mute: '5B6A63', line: 'DCD5C5', white: 'FFFFFF', pale: 'F7F5EF' };
const W = 13.33;

function text(slide, value, o) {
  slide.addText(value, { fontFace: FONT, color: C.ink, margin: 0, isTextBox: true, valign: 'top', ...o });
}
function card(slide, x, y, w, h, fill = C.white, name) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill },
    line: { color: fill === C.white ? C.line : fill, width: 0.75 }, objectName: name });
}
function content(stepLabel, title, notes) {
  const slide = pres.addSlide();
  slide.background = { color: C.white };
  if (stepLabel) {
    slide.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 0.5, w: 1.55, h: 0.36, rectRadius: 0.18, fill: { color: C.rust }, line: { color: C.rust } });
    text(slide, stepLabel, { x: 0.6, y: 0.5, w: 1.55, h: 0.36, fontSize: 12, bold: true, color: C.white, align: 'center', valign: 'middle' });
  }
  text(slide, title, { x: 0.6, y: 0.98, w: 12.1, h: 0.8, fontSize: 32, bold: true, color: C.pine });
  text(slide, 'TamsoodBase · S2-G05', { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: C.mute });
  slide.addText('', { x: 12.2, y: 7.0, w: 0.6, h: 0.3 });
  slide.slideNumber = { x: 12.3, y: 6.98, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 10, color: C.mute, align: 'right' };
  if (notes) slide.addNotes(notes);
  return slide;
}

// 1 ─ Title
{
  const s = pres.addSlide();
  s.background = { color: C.pine };
  text(s, 'CN230 × MTEC · DATA TO NET ZERO DAY', { x: 0.8, y: 0.9, w: 9, h: 0.4, fontSize: 14, bold: true, color: C.cream, charSpacing: 3 });
  s.addText([{ text: 'Tamsood', options: { color: C.white } }, { text: 'Base', options: { color: C.cream } }],
    { x: 0.8, y: 1.6, w: 9, h: 1.3, fontFace: FONT, fontSize: 72, bold: true, margin: 0, isTextBox: true });
  text(s, 'ฐานข้อมูลเชื้อเพลิงของไทย\nที่ทุกตัวเลขเปิดย้อนกลับไปถึงไฟล์ต้นทางได้', { x: 0.8, y: 3.2, w: 8.6, h: 1.3, fontSize: 26, color: 'DFEAE4', lineSpacingMultiple: 1.15 });
  text(s, 'Petroleum, Natural Gas & Fuels', { x: 0.8, y: 4.9, w: 8, h: 0.4, fontSize: 16, color: C.cream });
  card(s, 9.5, 1.6, 3.1, 3.9, C.pine2, 'team card');
  text(s, 'ทีม S2-G05 · Section 2', { x: 9.75, y: 1.82, w: 2.7, h: 0.4, fontSize: 15, bold: true, color: C.white });
  const team = [['ตฤณเดช พิตติรวิภาส', 'PM/BA'], ['เอดาวัต เอื้ออารยมนตรี', 'Schema Lead'], ['สิริเดช บุราคร', 'Data Lead'], ['พีรภัทร แสงศรี', 'SQL Lead'], ['ณวตา พุฒพินิจ', 'QA Lead']];
  team.forEach(([name, role], i) => {
    text(s, name, { x: 9.75, y: 2.36 + i * 0.6, w: 2.7, h: 0.3, fontSize: 13, color: C.white });
    text(s, role, { x: 9.75, y: 2.64 + i * 0.6, w: 2.7, h: 0.26, fontSize: 10.5, color: C.cream });
  });
  text(s, 'tamsoodbase.vercel.app', { x: 0.8, y: 6.6, w: 6, h: 0.35, fontSize: 14, color: 'CFE0D8' });
  s.addNotes('เปิด: เราคือทีม S2-G05 รับโจทย์ Petroleum, Natural Gas & Fuels จาก MTEC ใช้ 8 นาทีพาเดินตามหลักฐานตั้งแต่แหล่งข้อมูลจนถึงค่าหนึ่งค่าที่ย้อนถึงต้นทางได้ (ประมาณ 20 วินาที)');
}

// 2 ─ Step 1: domain and sources
{
  const s = content('ขั้นที่ 1', 'ข้อมูลเชื้อเพลิงไทย 5 ชั้น จาก 22 แหล่ง',
    'ขั้น 1 แนะนำ Domain และแหล่งข้อมูล (45 วินาที): โดเมนของเราคือปิโตรเลียม ก๊าซธรรมชาติ และเชื้อเพลิง ข้อมูลมี 5 ชั้นที่ความหมายต่างกัน เราไม่รวมเป็นตัวเลขเดียว เพราะสถิติการผลิต สถิติบริษัท และบัญชีรายการต่อผลิตภัณฑ์ เป็นคนละเรื่อง');
  const layers = [
    ['DMF', 'กรมเชื้อเพลิงธรรมชาติ', 'ผลิตน้ำมันดิบ คอนเดนเสท ก๊าซ รายเดือน แยกแหล่ง', '34,671', 'แถว'],
    ['EPPO', 'สนพ. / กรมธุรกิจพลังงาน', 'น้ำมันเข้าโรงกลั่นรายบริษัท และผลผลิตน้ำมันสำเร็จรูป', '5,934', 'แถว'],
    ['NSO', 'สำนักงานสถิติแห่งชาติ', 'สถิติพลังงานของประเทศ 5 ตาราง', '273', 'ค่า'],
    ['รายงานบริษัท', 'Thai Oil · SPRC', 'ตัวชี้วัดพลังงานและน้ำระดับองค์กร', '101', 'รายการ'],
    ['งานวิจัย', 'Permpool et al. 2020 · CC BY', 'บัญชีรายการปาล์ม–ไบโอดีเซล และผล LCA ที่ตีพิมพ์', '102', 'ค่า'],
  ];
  layers.forEach(([code, owner, what, count, unit], i) => {
    const x = 0.6 + i * 2.45;
    card(s, x, 2.15, 2.3, 3.6, i === 4 ? C.sand : C.pale, `layer ${code}`);
    text(s, code, { x: x + 0.2, y: 2.35, w: 1.9, h: 0.4, fontSize: 17, bold: true, color: C.rust });
    text(s, owner, { x: x + 0.2, y: 2.78, w: 1.95, h: 0.5, fontSize: 12, color: C.mute });
    text(s, count, { x: x + 0.2, y: 3.45, w: 1.9, h: 0.65, fontSize: 34, bold: true, color: C.pine });
    text(s, unit, { x: x + 0.2, y: 4.12, w: 1.9, h: 0.3, fontSize: 12, color: C.mute });
    text(s, what, { x: x + 0.2, y: 4.55, w: 1.95, h: 1.1, fontSize: 13, color: C.ink, lineSpacingMultiple: 1.1 });
  });
  text(s, 'ครอบคลุมปี 1986–2026 · ทุกแหล่งเป็นข้อมูลของประเทศไทย', { x: 0.6, y: 6.1, w: 12, h: 0.4, fontSize: 15, color: C.pine, bold: true });
}

// 3 ─ Step 2: source registry
{
  const s = content('ขั้นที่ 2', 'ทะเบียนแหล่งข้อมูล: รู้ว่าแต่ละค่ามาจากไหน และใช้ได้แค่ไหน',
    'ขั้น 2 เปิด Source Registry (45 วินาที): เปิดไฟล์ docs/source-registry.csv หรือหน้า Source ID บนเว็บ ชี้หนึ่งแหล่งให้เห็น ลิงก์ ชนิดไฟล์ สถานะการนำเข้า และสถานะสิทธิ์ เน้นว่าสิทธิ์เผยแพร่ถูกบันทึกแยกจากการรับข้อมูล');
  const rows = [
    [{ text: 'รหัสแหล่ง', options: { bold: true, color: C.white, fill: { color: C.pine } } }, { text: 'หน่วยงาน', options: { bold: true, color: C.white, fill: { color: C.pine } } }, { text: 'ชนิด', options: { bold: true, color: C.white, fill: { color: C.pine } } }, { text: 'สถานะสิทธิ์ที่บันทึก', options: { bold: true, color: C.white, fill: { color: C.pine } } }],
    ['DMF-CKAN-OIL', 'กรมเชื้อเพลิงธรรมชาติ', 'CSV', 'แนวทางของรัฐรองรับการใช้ซ้ำ'],
    ['EPPO-11_14', 'สนพ. / กรมธุรกิจพลังงาน', 'CSV', 'ป้าย Open Data Common'],
    ['NSO-SYB2026-13.6', 'สำนักงานสถิติแห่งชาติ', 'CSV', 'ดาวน์โหลดสาธารณะ'],
    ['MDPI-SU12229415-T4', 'Permpool; Ghani; Gheewala', 'HTML', 'CC BY 4.0'],
    ['SPRC-REPORT-2024', 'Star Petroleum Refining', 'PDF', 'อ่านได้สาธารณะ ยังไม่ยืนยันการใช้ซ้ำ'],
  ];
  s.addTable(rows, { x: 0.6, y: 2.15, w: 8.2, colW: [2.3, 2.5, 0.8, 2.6], fontFace: FONT, fontSize: 12.5, color: C.ink,
    border: { type: 'solid', color: C.line, pt: 0.75 }, rowH: 0.52, valign: 'middle', margin: [0.03, 0.1, 0.03, 0.1] });
  card(s, 9.2, 2.15, 3.5, 3.15, C.pine, 'evidence card');
  text(s, 'หลักฐานของหนึ่งแหล่ง', { x: 9.45, y: 2.35, w: 3, h: 0.35, fontSize: 14, bold: true, color: C.cream });
  const ev = [['ไฟล์', 'production_oil.csv (catalog.dmf.go.th)'], ['รหัส SHA-256', '841a7db1…c7bb70d3'], ['ดึงเมื่อ', '22 ต.ค. 2569'], ['หน่วยจาก metadata', 'บาร์เรล']];
  ev.forEach(([k, v], i) => {
    text(s, k, { x: 9.45, y: 2.85 + i * 0.58, w: 3, h: 0.24, fontSize: 10.5, color: 'CFE0D8' });
    text(s, v, { x: 9.45, y: 3.08 + i * 0.58, w: 3.15, h: 0.3, fontSize: 11.5, bold: true, color: C.white });
  });
  text(s, '22 แหล่งในทะเบียน · บางแหล่งเป็นเอกสารอ้างอิงเท่านั้น ยังไม่มีแถวข้อมูลในฐาน', { x: 0.6, y: 5.75, w: 12, h: 0.4, fontSize: 14, color: C.mute });
}

// 4 ─ Step 3: acquisition pipeline
{
  const s = content('ขั้นที่ 3', 'ดึงข้อมูลแบบรันซ้ำได้ และเก็บสำเนาก่อนแตะข้อมูลเสมอ',
    'ขั้น 3 อธิบาย Acquisition Pipeline (1 นาที): สคริปต์ src/process_dmf.py ดาวน์โหลดไฟล์ บันทึกสำเนาพร้อมรหัส SHA-256 เก็บทุกแถวดิบเป็น JSON แล้วจึงแปลงชนิดข้อมูล ถ้ารันซ้ำกับไฟล์เดิมจะได้รหัสเดิม จึงพิสูจน์ได้ว่าข้อมูลไม่ถูกแก้');
  const steps = [['1', 'ดาวน์โหลด', 'ไฟล์ CSV / PDF / HTML จากเว็บหน่วยงาน'], ['2', 'เก็บสำเนา', 'บันทึกไฟล์ต้นฉบับ พร้อมรหัส SHA-256 และวันเวลา'], ['3', 'เก็บแถวดิบ', 'ทุกแถวเป็น JSON ตามต้นฉบับ มีเลขบรรทัดกำกับ'], ['4', 'แปลงชนิดข้อมูล', 'ปี พ.ศ. → ค.ศ. · ตัวเลขเป็น DECIMAL · เก็บค่าดิบไว้คู่กัน']];
  steps.forEach(([n, title, body], i) => {
    const x = 0.6 + i * 3.15;
    card(s, x, 2.3, 2.85, 2.5, C.pale, `pipeline ${n}`);
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.25, y: 2.5, w: 0.55, h: 0.55, fill: { color: C.pine }, line: { color: C.pine } });
    text(s, n, { x: x + 0.25, y: 2.5, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: C.white, align: 'center', valign: 'middle' });
    text(s, title, { x: x + 0.25, y: 3.25, w: 2.4, h: 0.4, fontSize: 19, bold: true, color: C.pine });
    text(s, body, { x: x + 0.25, y: 3.72, w: 2.4, h: 1, fontSize: 13, color: C.ink, lineSpacingMultiple: 1.1 });
    if (i < 3) text(s, '→', { x: x + 2.85, y: 3.25, w: 0.3, h: 0.5, fontSize: 24, bold: true, color: C.rust, align: 'center' });
  });
  card(s, 0.6, 5.15, 12.15, 1.35, C.sand, 'pipeline numbers');
  text(s, 'DMF รอบ 22 ต.ค. 2569', { x: 0.85, y: 5.3, w: 3, h: 0.3, fontSize: 12, bold: true, color: C.rust });
  text(s, '3 ไฟล์ · 34,905 แถวดิบ · ทุกแถวอ่านกลับได้ตรงกับไฟล์ต้นฉบับ', { x: 0.85, y: 5.62, w: 11.6, h: 0.45, fontSize: 20, bold: true, color: C.pine });
  text(s, 'คำสั่ง: python -X utf8 src/process_dmf.py', { x: 0.85, y: 6.08, w: 11, h: 0.3, fontFace: 'Consolas', fontSize: 12, color: C.mute });
}

// 5 ─ Step 4: staging → validation
{
  const s = content('ขั้นที่ 4', 'ตรวจทีละชั้น และเก็บเหตุผลของทุกแถวที่ไม่ผ่าน',
    'ขั้น 4 Staging → Mapping → Validation → Accepted/Rejected (1 นาที 15 วินาที): จาก 34,905 แถวดิบ 6 แถวถูกปฏิเสธเพราะค่าหรือแหล่งว่าง 42 แถวเป็นสำเนาซ้ำที่ค่าเท่ากัน 186 แถวค่าขัดกันจึงพักไว้ทั้งหมดไม่เลือกเอง เหลือ 34,671 แถว พูดตรง ๆ ว่าชุดนี้ยังรอทีมยืนยันกฎรับข้อมูล ส่วนรายงานบริษัททีมรับแล้ว 97 จาก 101');
  const funnel = [['34,905', 'แถวดิบจากไฟล์', C.pine, 4.2], ['34,899', 'ผ่านการตรวจรูปแบบ', C.pine2, 3.9], ['34,671', 'ไม่ซ้ำ ไม่ขัดกัน', C.leaf, 3.6]];
  funnel.forEach(([n, label, fill, w], i) => {
    const y = 2.15 + i * 1.3;
    card(s, 0.6, y, w, 1.1, fill, `funnel ${i + 1}`);
    text(s, n, { x: 0.85, y: y + 0.12, w: w - 0.4, h: 0.55, fontSize: 30, bold: true, color: C.white });
    text(s, label, { x: 0.85, y: y + 0.68, w: w - 0.4, h: 0.3, fontSize: 13, color: 'DFEAE4' });
  });
  const out = [['6', 'ถูกปฏิเสธ', 'ค่าว่าง ไม่ระบุพื้นที่หรือแหล่ง'], ['42', 'สำเนาซ้ำ', 'ค่าเท่ากันทุกช่อง เก็บตัวแทน 1 แถว'], ['186', 'พักไว้', 'ช่วงเวลาและแหล่งเดียวกัน แต่ค่าต่างกัน']];
  out.forEach(([n, label, why], i) => {
    const y = 2.15 + i * 1.3;
    card(s, 5.2, y, 3.5, 1.1, C.pale, `out ${i + 1}`);
    text(s, n, { x: 5.4, y: y + 0.18, w: 1, h: 0.6, fontSize: 28, bold: true, color: C.rust });
    text(s, label, { x: 6.45, y: y + 0.16, w: 2.1, h: 0.35, fontSize: 15, bold: true, color: C.pine });
    text(s, why, { x: 6.45, y: y + 0.52, w: 2.15, h: 0.5, fontSize: 12, color: C.mute });
  });
  card(s, 9.1, 2.15, 3.65, 3.7, C.sand, 'corporate card');
  text(s, 'รายงานบริษัท', { x: 9.35, y: 2.35, w: 3.2, h: 0.35, fontSize: 14, bold: true, color: C.rust });
  text(s, '97', { x: 9.35, y: 2.8, w: 3.2, h: 0.9, fontSize: 54, bold: true, color: C.pine });
  text(s, 'รายการที่ทีมรับเป็นข้อมูลอ้างอิง', { x: 9.35, y: 3.75, w: 3.2, h: 0.35, fontSize: 13, color: C.ink });
  text(s, '4', { x: 9.35, y: 4.3, w: 1, h: 0.6, fontSize: 30, bold: true, color: C.rust });
  text(s, 'พักไว้เพราะบริบท\nของตารางไม่ตรงกัน', { x: 10.2, y: 4.36, w: 2.4, h: 0.7, fontSize: 12, color: C.ink });
  text(s, 'จาก 101 ค่าที่สกัดจาก PDF', { x: 9.35, y: 5.3, w: 3.2, h: 0.3, fontSize: 11, color: C.mute });
  text(s, 'สถิติรัฐทั้งหมดยังมีสถานะ "รอตรวจ" จนกว่าทีมจะยืนยันกฎรับข้อมูล', { x: 0.6, y: 6.25, w: 12, h: 0.4, fontSize: 14, color: C.mute });
}

// 6 ─ Step 5: schema
{
  const s = content('ขั้นที่ 5', 'ออกแบบตาราง ให้แถวดิบแยกจากค่าที่แปลงแล้ว',
    'ขั้น 5 เปิด ERD/Schema (1 นาที 15 วินาที): ชี้สายตาราง resource_snapshot → source_record → observation คีย์หลักของ observation คือ (snapshot_id, source_line) ซึ่งเป็น FK ไปยังแถวดิบด้วย จึงไม่มีค่าใดอยู่ได้โดยไม่มีแถวต้นทาง ถ้าถูกถามเรื่อง FLOW: ตาราง inventory_exchange ที่ใช้อยู่ยังเก็บ flow เป็นข้อความ เราออกแบบตาราง flow/unit แยกแล้วแต่ยังไม่ได้ย้ายข้อมูล');
  const boxes = [
    ['resource_snapshot', 'PK snapshot_id\ncsv_sha256 · csv_url\nmetadata_unit', 0.6, 2.2],
    ['source_record', 'PK (snapshot_id, source_line)\nraw_json\nrecord_content_sha256', 3.55, 2.2],
    ['observation', 'PK = FK (snapshot_id, source_line)\nFK context_id\nraw_value · amount DECIMAL(30,12)', 6.5, 2.2],
    ['production_context', 'PK context_id\narea · block_label\nsource_group', 6.5, 4.45],
    ['duplicate_disposition', 'PK = FK (snapshot_id, source_line)\nstatus · representative_line', 3.55, 4.45],
    ['rejected_record', 'PK = FK (snapshot_id, source_line)\nreasons_json', 0.6, 4.45],
  ];
  boxes.forEach(([name, cols, x, y]) => {
    card(s, x, y, 2.7, 1.75, C.pale, `table ${name}`);
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 2.7, h: 0.42, rectRadius: 0.08, fill: { color: C.pine }, line: { color: C.pine } });
    text(s, name, { x: x + 0.12, y, w: 2.5, h: 0.42, fontFace: 'Consolas', fontSize: 12, bold: true, color: C.white, valign: 'middle' });
    text(s, cols, { x: x + 0.12, y: y + 0.52, w: 2.5, h: 1.15, fontFace: 'Consolas', fontSize: 10, color: C.ink, lineSpacingMultiple: 1.15 });
  });
  [[3.3, 3.05], [6.25, 3.05]].forEach(([x, y]) => text(s, '→', { x, y: y - 0.25, w: 0.25, h: 0.5, fontSize: 20, bold: true, color: C.rust, align: 'center' }));
  text(s, 'tamsood_research', { x: 0.6, y: 6.32, w: 4, h: 0.3, fontFace: 'Consolas', fontSize: 11, color: C.mute });
  card(s, 9.55, 2.2, 3.2, 4.0, C.sand, 'design decisions');
  text(s, 'เหตุผลที่ออกแบบแบบนี้', { x: 9.75, y: 2.36, w: 2.9, h: 0.35, fontSize: 14, bold: true, color: C.rust });
  const why = ['ค่าทุกค่าต้องมีแถวต้นทาง จึงใช้คีย์เดียวกับแถวดิบ', 'เก็บ raw_value คู่กับ amount เพื่อเทียบกลับได้', 'แถวซ้ำและแถวที่ปฏิเสธ มีตารางของตัวเอง ไม่ลบทิ้ง', 'CHECK กันค่าติดลบและวันผลิตเกินจำนวนวันในเดือน'];
  s.addText(why.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < why.length - 1 } })),
    { x: 9.75, y: 2.8, w: 2.85, h: 3.2, fontFace: FONT, fontSize: 12.5, color: C.ink, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 8 });
}

// 7 ─ Step 6: SQL
{
  const s = content('ขั้นที่ 6', 'ถามด้วย SQL แล้วได้คำตอบพร้อมที่มาในแถวเดียวกัน',
    'ขั้น 6 รัน SQL Query (1 นาที): use case คือ "เดือนมีนาคม 2026 แหล่งไหนผลิตน้ำมันดิบมากที่สุด" รัน query นี้ให้ดู ผลแต่ละแถวมีเลขบรรทัดของไฟล์ต้นฉบับติดมาด้วย view deduplicated_pending JOIN 5 ตารางและคัดเฉพาะแถวที่ไม่ซ้ำ ผลที่แสดงมาจากฐานในเครื่องรอบข้อมูล 22 ต.ค. 2569');
  card(s, 0.6, 2.15, 6.6, 4.3, C.pine, 'sql card');
  const sql = "SELECT source_group, area, raw_value,\n       metadata_unit, source_line, csv_sha256\nFROM   deduplicated_pending\nWHERE  product_code = 'crude_oil'\n  AND  period_start = '2026-03-01'\nORDER  BY amount DESC\nLIMIT  4;";
  text(s, sql, { x: 0.85, y: 2.4, w: 6.1, h: 2.9, fontFace: 'Consolas', fontSize: 14, color: 'E8F1EC', lineSpacingMultiple: 1.2 });
  text(s, 'view นี้ JOIN observation · production_context · resource_snapshot · source_resource · duplicate_disposition', { x: 0.85, y: 5.5, w: 6.1, h: 0.75, fontSize: 11.5, color: C.cream });
  const head = o => ({ bold: true, color: C.white, fill: { color: C.rust }, ...o });
  s.addTable([
    [{ text: 'แหล่งผลิต', options: head() }, { text: 'พื้นที่', options: head() }, { text: 'ค่าต้นฉบับ (บาร์เรล)', options: head({ align: 'right' }) }, { text: 'บรรทัด', options: head({ align: 'right' }) }],
    ['เบญจมาศ', 'ในทะเล', { text: '19337.54839', options: { align: 'right' } }, { text: '11399', options: { align: 'right' } }],
    ['Sirikit และอื่นๆใน S1', 'บนบก', { text: '18557', options: { align: 'right' } }, { text: '11425', options: { align: 'right' } }],
    ['ปลาทอง', 'ในทะเล', { text: '11760.67294', options: { align: 'right' } }, { text: '11407', options: { align: 'right' } }],
    ['นงเยาว์', 'ในทะเล', { text: '9703.50129', options: { align: 'right' } }, { text: '11402', options: { align: 'right' } }],
  ], { x: 7.5, y: 2.15, w: 5.25, colW: [2.0, 0.9, 1.5, 0.85], fontFace: FONT, fontSize: 12, color: C.ink, border: { type: 'solid', color: C.line, pt: 0.75 }, rowH: 0.5, valign: 'middle', margin: [0.03, 0.08, 0.03, 0.08] });
  text(s, '4 จาก 34 แหล่งในเดือนนั้น', { x: 7.5, y: 4.8, w: 5.2, h: 0.35, fontSize: 13, bold: true, color: C.pine });
  text(s, 'ค่าเป็นตัวเลขรายเดือนตามที่ไฟล์รายงาน ทีมยังไม่ยืนยันว่าเป็นยอดรวมทั้งเดือนหรืออัตราต่อวัน จึงไม่บวกข้ามเดือน', { x: 7.5, y: 5.2, w: 5.2, h: 0.9, fontSize: 12, color: C.mute, lineSpacingMultiple: 1.1 });
}

// 8 ─ Step 7: trace one tuple
{
  const s = content('ขั้นที่ 7', 'ตามหนึ่งค่ากลับไปถึงไฟล์ของหน่วยงานได้ใน 4 ก้าว',
    'ขั้น 7 เปิด tuple หนึ่งรายการแล้วย้อนถึงต้นทาง (1 นาที 15 วินาที): ชี้โปสเตอร์ไปพร้อมกัน บนเว็บ เปิดหน้าแหล่งผลิตน้ำมันและก๊าซ กด "ดูที่มา" ที่แถวไพลินเหนือ จะเห็นค่า เลขบรรทัด และลิงก์ไฟล์ของกรมเชื้อเพลิงธรรมชาติ ทุกคนในทีมต้องทำขั้นนี้ได้');
  const hops = [['1', 'ค่าในฐานข้อมูล', 'ไพลินเหนือ · คอนเดนเสท\nมีนาคม 2026', '5,876.859677 บาร์เรล'], ['2', 'แถวต้นฉบับ', 'production_condensate.csv', 'บรรทัดที่ 11394'], ['3', 'ไฟล์ที่ดึงมา', 'ดึงเมื่อ 22 ต.ค. 2569', 'SHA-256 79f5ac2a…ae678d1c'], ['4', 'หน่วยงานเจ้าของ', 'กรมเชื้อเพลิงธรรมชาติ', 'catalog.dmf.go.th']];
  hops.forEach(([n, title, a, b], i) => {
    const x = 0.6 + i * 3.15;
    card(s, x, 2.3, 2.85, 3.0, i === 0 ? C.pine : C.pale, `hop ${n}`);
    const dark = i === 0;
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.25, y: 2.5, w: 0.5, h: 0.5, fill: { color: dark ? C.cream : C.rust }, line: { color: dark ? C.cream : C.rust } });
    text(s, n, { x: x + 0.25, y: 2.5, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: dark ? C.pine : C.white, align: 'center', valign: 'middle' });
    text(s, title, { x: x + 0.25, y: 3.15, w: 2.4, h: 0.4, fontSize: 18, bold: true, color: dark ? C.white : C.pine });
    text(s, a, { x: x + 0.25, y: 3.6, w: 2.4, h: 0.7, fontSize: 12.5, color: dark ? 'CFE0D8' : C.mute, lineSpacingMultiple: 1.1 });
    text(s, b, { x: x + 0.25, y: 4.4, w: 2.45, h: 0.7, fontSize: i === 0 ? 17 : 14, bold: true, color: dark ? C.cream : C.ink, fontFace: i === 2 ? 'Consolas' : FONT });
    if (i < 3) text(s, '→', { x: x + 2.85, y: 3.5, w: 0.3, h: 0.5, fontSize: 24, bold: true, color: C.rust, align: 'center' });
  });
  text(s, 'บนเว็บ: หน้า "แหล่งผลิตน้ำมันและก๊าซ" → กด "ดูที่มา" ที่แถวใดก็ได้', { x: 0.6, y: 5.7, w: 12, h: 0.4, fontSize: 16, bold: true, color: C.pine });
  text(s, 'ไม่มีที่มา = ไม่นับเป็นข้อมูลที่เชื่อถือได้', { x: 0.6, y: 6.15, w: 12, h: 0.4, fontSize: 14, color: C.mute });
}

// 9 ─ Beyond the minimum
{
  const s = content('ต่อยอด', 'เกินขั้นต่ำ: เว็บค้นข้อมูล กราฟ และผู้ช่วยตอบคำถาม',
    'ต่อยอด (40 วินาที): Level 2 คือเว็บที่กดดูที่มาได้ทุกแถว Level 3 เราลองสามแบบและใช้ต่างกัน กราฟตอบคำถามเรื่องความเชื่อมโยง Semantic Search หาเอกสารที่ความหมายใกล้ ส่วนผู้ช่วยบนเว็บให้ AI เข้าใจคำถาม แต่ตัวเลขคำนวณด้วยโค้ดจากฐานข้อมูล และปฏิเสธคำตอบที่ตัวเลขหรือหน่วยไม่ตรง ถ้าถูกถามเรื่อง AI ให้ตอบตามที่ทำจริง');
  const cols = [
    ['กราฟ (Neo4j)', 'ถามเรื่องความเชื่อมโยง', 'เช่น FAME มีสิ่งเข้าอะไรบ้าง', '39 โหนด · 68 ความสัมพันธ์', 'ทดลองกับ 16 รายการ ผลตรงกับ SQL 4 คำถาม'],
    ['Semantic Search', 'หาเอกสารที่ความหมายใกล้', 'เช่น คำถามเรื่องสตาร์ตเย็นของรถ E10', 'เวกเตอร์ 384 มิติ', 'ต้นแบบในเครื่อง บนการ์ดหลักฐาน 10 ใบ'],
    ['ผู้ช่วยตอบคำถาม (RAG)', 'ถามเป็นภาษาพูด ได้ตัวเลขพร้อมที่มา', 'เช่น ปี 2567 ไทยใช้ดีเซลเท่าไหร่', 'เปิดใช้จริงบนเว็บ', 'ตัวเลขคำนวณด้วยโค้ด ไม่ให้ AI คิดเลขเอง'],
  ];
  cols.forEach(([name, use, ex, stat, note], i) => {
    const x = 0.6 + i * 4.12;
    card(s, x, 2.15, 3.9, 3.55, i === 2 ? C.pine : C.pale, `approach ${i + 1}`);
    const dark = i === 2;
    text(s, name, { x: x + 0.25, y: 2.35, w: 3.4, h: 0.4, fontSize: 18, bold: true, color: dark ? C.cream : C.rust });
    text(s, use, { x: x + 0.25, y: 2.85, w: 3.4, h: 0.4, fontSize: 14, bold: true, color: dark ? C.white : C.pine });
    text(s, ex, { x: x + 0.25, y: 3.3, w: 3.4, h: 0.5, fontSize: 12, color: dark ? 'CFE0D8' : C.mute });
    text(s, stat, { x: x + 0.25, y: 4.0, w: 3.4, h: 0.5, fontSize: 20, bold: true, color: dark ? C.white : C.pine });
    text(s, note, { x: x + 0.25, y: 4.65, w: 3.4, h: 0.85, fontSize: 12, color: dark ? 'CFE0D8' : C.ink, lineSpacingMultiple: 1.1 });
  });
  card(s, 0.6, 5.95, 12.15, 0.75, C.sand, 'lca result');
  s.addText([{ text: 'ตัวอย่างที่ถามได้: ', options: { bold: true, color: C.rust } },
    { text: 'ภาวะโลกร้อนตลอดวงจรต่อ 1,000 MJ — FAME 10.7 เทียบกับดีเซลฟอสซิล 219 kg CO₂ eq (ผลที่งานวิจัยรายงาน ตาราง 5)', options: { color: C.ink } }],
    { x: 0.85, y: 5.95, w: 11.7, h: 0.75, fontFace: FONT, fontSize: 13.5, margin: 0, isTextBox: true, valign: 'middle' });
}

// 10 ─ Step 8: coverage, limits, next
{
  const s = pres.addSlide();
  s.background = { color: C.pine };
  s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 0.5, w: 1.55, h: 0.36, rectRadius: 0.18, fill: { color: C.cream }, line: { color: C.cream } });
  text(s, 'ขั้นที่ 8', { x: 0.6, y: 0.5, w: 1.55, h: 0.36, fontSize: 12, bold: true, color: C.pine, align: 'center', valign: 'middle' });
  text(s, 'สิ่งที่ทำได้ สิ่งที่ยังไม่ได้ และก้าวต่อไป', { x: 0.6, y: 0.98, w: 12.1, h: 0.8, fontSize: 32, bold: true, color: C.white });
  const cols = [
    ['ครอบคลุมแล้ว', C.cream, ['ข้อมูล 5 ชั้น จาก 22 แหล่ง ปี 1986–2026', 'ทุกแถวย้อนถึงไฟล์ต้นทางได้', 'เว็บและผู้ช่วยตอบคำถามเปิดใช้จริง', 'ผล LCA ของไบโอดีเซลตามที่งานวิจัยรายงาน']],
    ['ข้อจำกัด', 'F6B79A', ['ยังไม่ใช่บัญชี LCI ที่ทีมเชื่อมครบวงจรเอง', 'สถิติรัฐยังรอยืนยันกฎรับข้อมูล', 'ชื่อแหล่งผลิต DMF ยังไม่เป็นมาตรฐานเดียว', 'ตัวเลขรายงานบริษัทยังไม่เผยแพร่ต่อ']],
    ['ก้าวต่อไป', 'BFE3D2', ['ยืนยันกฎรับข้อมูลและฐานเวลากับกรมเชื้อเพลิงธรรมชาติ', 'แยกตาราง flow และ unit ออกจากข้อความ', 'ทำตารางชื่อแหล่งผลิตกลาง', 'หาข้อมูลขนส่งและการปันส่วนของไทย']],
  ];
  cols.forEach(([title, color, items], i) => {
    const x = 0.6 + i * 4.12;
    card(s, x, 2.15, 3.9, 4.1, C.pine2, `closing ${i + 1}`);
    text(s, title, { x: x + 0.28, y: 2.38, w: 3.4, h: 0.45, fontSize: 20, bold: true, color });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.28, y: 3.0, w: 3.4, h: 3.1, fontFace: FONT, fontSize: 14, color: C.white, margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 10 });
  });
  text(s, '“Build data that someone else can trust.”', { x: 0.6, y: 6.55, w: 8, h: 0.4, fontSize: 15, italic: true, color: C.cream });
  text(s, 'tamsoodbase.vercel.app', { x: 8.7, y: 6.55, w: 4.05, h: 0.4, fontSize: 15, color: 'CFE0D8', align: 'right' });
  s.addNotes('ขั้น 8 สรุป Coverage, Limitation และสิ่งที่จะปรับต่อ (45 วินาที): ย้ำว่าเราเลือกบอกข้อจำกัดตรง ๆ เพราะเป้าหมายคือข้อมูลที่คนอื่นเชื่อถือได้ แล้วเชิญคำถาม แต่ละคนเตรียมตอบส่วนของตัวเองและชี้หลักฐานได้');
}

pres.writeFile({ fileName: process.argv[2] }).then(f => console.log('wrote', f));
