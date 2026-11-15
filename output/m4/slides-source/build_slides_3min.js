// TamsoodBase: 3-minute talk deck (talk 3 min + 5 min demo video = 8 min).
// 8 main slides + 2 backup slides for Q&A (10 total = course limit). Covers ERD + SQL (W15 demo steps 5-6).
// Run: NODE_PATH=<runtime>/node_modules node build_slides_3min.js
const pptxgen = require('pptxgenjs');
const path = require('path');
const A = (f) => path.join(__dirname, 'assets', f);
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.title = 'TamsoodBase - Data to Net Zero Day (3 min talk)';
pres.author = 'S2-G05';
const FONT = 'Leelawadee UI';
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

const C = { pine: '143A30', pine2: '1F5245', leaf: '2F7D62', mint: 'DFEAE4', rust: 'C2572D', rust2: 'E8683A',
  sand: 'F4ECDC', cream: 'F0C9A0', ink: '1D2A25', mute: '5B6A63', line: 'DCD5C5', white: 'FFFFFF', pale: 'F7F5EF', amber: 'FFF1D6' };

const T = (s, v, o) => s.addText(v, { fontFace: FONT, color: C.ink, margin: 0, isTextBox: true, valign: 'top', ...o });
const box = (s, x, y, w, h, fill, o = {}) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: o.r ?? 0.14,
  fill: { color: fill, transparency: o.tr ?? 0 }, line: o.line ? { color: o.line, width: o.lw ?? 1 } : { color: fill, width: 0 } });
const pill = (s, x, y, w, h, fill, label, o = {}) => {
  box(s, x, y, w, h, fill, { r: h / 2, line: o.line, lw: o.lw });
  T(s, label, { x, y, w, h, fontSize: o.fs ?? 13, bold: o.bold ?? true, color: o.color ?? C.white, align: 'center', valign: 'middle' });
};
function light(tag, title, notes) {
  const s = pres.addSlide();
  s.background = { path: A('bg_light.png') };
  if (tag) pill(s, 0.7, 0.5, 1.9, 0.38, C.rust, tag, { fs: 12 });
  T(s, title, { x: 0.7, y: 1.0, w: 11.9, h: 0.95, fontSize: 31, bold: true, color: C.pine, lineSpacingMultiple: 1.0 });
  T(s, 'TamsoodBase · S2-G05', { x: 0.7, y: 7.02, w: 5, h: 0.3, fontSize: 10, color: C.mute });
  s.slideNumber = { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 10, color: C.mute, align: 'right' };
  if (notes) s.addNotes(notes);
  return s;
}
function dark(notes) {
  const s = pres.addSlide();
  s.background = { path: A('bg_dark.png') };
  if (notes) s.addNotes(notes);
  return s;
}

// ───────── 1 · Title (≈10 s)
{
  const s = dark('[0:00–0:10 · 10 วินาที] เปิด: เราคือทีม S2-G05 รับโดเมนปิโตรเลียม ก๊าซธรรมชาติ และเชื้อเพลิงจาก MTEC ' +
    'สิ่งที่ทีมสร้างคือ TamsoodBase ฐานข้อมูลที่ทุกตัวเลขเปิดย้อนกลับไปถึงไฟล์ต้นทางได้ ยืนข้างจอ ไม่บังสไลด์ และชี้ลูกโซ่ทางขวา 1 ครั้ง');
  T(s, 'CN230 × MTEC  ·  DATA TO NET ZERO DAY', { x: 0.8, y: 0.75, w: 9, h: 0.4, fontSize: 14, bold: true, color: C.cream, charSpacing: 4 });
  s.addText([{ text: 'Tamsood', options: { color: C.white } }, { text: 'Base', options: { color: C.cream } }],
    { x: 0.8, y: 1.35, w: 7.6, h: 1.5, fontFace: FONT, fontSize: 70, bold: true, margin: 0, isTextBox: true, fit: 'none', wrap: false });
  T(s, 'ข้อมูลเชื้อเพลิงของไทย\nที่ทุกตัวเลขย้อนกลับถึงไฟล์ต้นทางได้', { x: 0.8, y: 3.1, w: 7.2, h: 1.3, fontSize: 27, color: C.mint, lineSpacingMultiple: 1.15 });
  ['Petroleum', 'Natural Gas', 'Fuels'].forEach((t, i) => pill(s, 0.8 + i * 1.75, 4.75, 1.6, 0.42, C.pine, t, { line: C.cream, lw: 1.25, fs: 13, color: C.cream }));
  T(s, 'ทีม S2-G05 · Section 2', { x: 0.8, y: 5.75, w: 5, h: 0.3, fontSize: 14, bold: true, color: C.white });
  T(s, 'ตฤณเดช · เอดาวัต · สิริเดช · พีรภัทร · ณวตา', { x: 0.8, y: 6.1, w: 7.2, h: 0.3, fontSize: 13, color: C.mint });
  T(s, 'tamsoodbase.vercel.app', { x: 0.8, y: 6.6, w: 5, h: 0.35, fontSize: 15, bold: true, color: C.cream });
  // right: trace chain
  T(s, 'ตามหนึ่งค่า กลับไปถึงต้นทาง', { x: 8.55, y: 0.78, w: 4.3, h: 0.35, fontSize: 14, bold: true, color: C.cream });
  const chain = [
    ['1  ค่าบนเว็บ', 'ไพลินเหนือ · คอนเดนเสท · มี.ค. 2026', '5,876.859677 บาร์เรล'],
    ['2  แถวต้นฉบับ', 'production_condensate.csv', 'บรรทัดที่ 11394'],
    ['3  ไฟล์ที่ดึงมา', 'ดึงเมื่อ 22 ต.ค. 2569', 'SHA-256 79f5ac2a…ae678d1c'],
    ['4  หน่วยงานเจ้าของ', 'กรมเชื้อเพลิงธรรมชาติ', 'catalog.dmf.go.th'],
  ];
  chain.forEach(([h, a, b], i) => {
    const y = 1.3 + i * 1.32;
    box(s, 8.55, y, 4.2, 1.08, C.white, { tr: 90, line: C.cream, lw: 1 });
    T(s, h, { x: 8.78, y: y + 0.12, w: 3.8, h: 0.3, fontSize: 12, bold: true, color: C.cream });
    T(s, a, { x: 8.78, y: y + 0.42, w: 3.8, h: 0.28, fontSize: 12.5, color: C.white });
    T(s, b, { x: 8.78, y: y + 0.7, w: 3.8, h: 0.3, fontSize: 13.5, bold: true, color: C.white });
    if (i < 3) s.addShape(pres.ShapeType.downArrow, { x: 10.45, y: y + 1.08, w: 0.3, h: 0.24, fill: { color: C.rust2 }, line: { color: C.rust2, width: 0 } });
  });
}

// ───────── 2 · MTEC's 3 questions (≈25 s)
{
  const s = light('โจทย์ของ MTEC', 'MTEC ถาม 3 ข้อ · เราตอบด้วยระบบที่ตรวจย้อนกลับได้',
    '[0:10–0:35 · 25 วินาที แล้วพูดว่า ต่อไปดูของจริง 5 นาที] MTEC ถามสามข้อ: ข้อมูลไทยอยู่ที่ไหน เชื่อได้ไหม และใช้ซ้ำได้ไหม ' +
    'เราตอบข้อแรกด้วยทะเบียนแหล่งข้อมูล 22 แหล่ง ข้อสองด้วยบรรทัดต้นฉบับและรหัส SHA-256 ของทุกไฟล์ ข้อสามด้วยฐานข้อมูล เว็บ API ส่งออก CSV และผู้ช่วยตอบคำถาม ' +
    'ย้ำว่า More Data ไม่เท่ากับ Better Data ตัวเลขที่นับต้องผ่านเกณฑ์');
  const cols = [
    ['01', 'Findable', 'ข้อมูลไทยอยู่ที่ไหน?', ['ทะเบียนแหล่งข้อมูล 22 แหล่ง', '5 ชุดข้อมูลบนเว็บ ค้นได้ในที่เดียว', 'ปีครอบคลุม 1986–2026'], C.leaf],
    ['02', 'Verifiable', 'เชื่อถือค่านี้ได้ไหม?', ['ทุกแถวเก็บบรรทัดต้นฉบับ', 'ทุกไฟล์มีรหัส SHA-256 และวันที่ดึง', 'เกณฑ์รับ AR-2 อธิบายเหตุผลทุกแถว'], C.rust],
    ['03', 'Reusable', 'ใช้ซ้ำได้ไหม?', ['ฐานข้อมูล MySQL + เว็บ + API', 'ส่งออก CSV / JSON พร้อมหน่วยและที่มา', 'ผู้ช่วยตอบคำถาม ถามเป็นภาษาพูดได้'], C.pine2],
  ];
  cols.forEach(([n, en, q, items, col], i) => {
    const x = 0.7 + i * 4.1;
    box(s, x, 2.15, 3.85, 3.9, C.white, { line: C.line, lw: 1 });
    box(s, x, 2.15, 3.85, 0.12, col, { r: 0.05 });
    T(s, n, { x: x + 0.3, y: 2.5, w: 1.2, h: 0.7, fontSize: 40, bold: true, color: col });
    T(s, en, { x: x + 1.5, y: 2.62, w: 2.2, h: 0.4, fontSize: 18, bold: true, color: C.pine, align: 'right' });
    T(s, q, { x: x + 0.3, y: 3.3, w: 3.3, h: 0.45, fontSize: 21, bold: true, color: C.ink });
    s.addShape(pres.ShapeType.line, { x: x + 0.3, y: 3.88, w: 3.25, h: 0, line: { color: C.line, width: 1 } });
    items.forEach((it, j) => {
      s.addShape(pres.ShapeType.ellipse, { x: x + 0.32, y: 4.17 + j * 0.62, w: 0.14, h: 0.14, fill: { color: col }, line: { color: col, width: 0 } });
      T(s, it, { x: x + 0.6, y: 4.07 + j * 0.62, w: 3.05, h: 0.55, fontSize: 14, color: C.ink });
    });
  });
  box(s, 0.7, 6.28, 11.95, 0.55, C.pine, {});
  T(s, 'More Data ≠ Better Data  ·  ตัวเลขที่นับ = Accepted · Unique · Verified · Traceable', { x: 0.7, y: 6.28, w: 11.95, h: 0.55, fontSize: 16, bold: true, color: C.white, align: 'center', valign: 'middle' });
}

// ───────── 4 · Demo slide (shown while the 5-minute clip plays)
{
  const s = dark('[0:35 → เปิดคลิป 5 นาที] เล่นไฟล์ TamsoodBase-Website-Evidence-5min-TH-annotated.mp4 (มีเสียงบรรยายไทยและลูกศรชี้) ' +
    'ระหว่างคลิปไม่ต้องพูดทับ ยืนข้างจอ ชี้โปสเตอร์เมื่อคลิปถึงตอนย้อนดูแถวถึงต้นทาง ถ้าคลิปเปิดไม่ได้ ใช้ภาพสำรอง 10 ภาพในโฟลเดอร์ demo-backup');
  pill(s, 0.8, 0.6, 2.2, 0.4, C.rust, 'DEMO · 5 นาที', { fs: 13 });
  T(s, 'ดูของจริง: ตามค่าหนึ่งค่า\nกลับไปถึงไฟล์ต้นทาง', { x: 0.8, y: 1.2, w: 6.4, h: 1.6, fontSize: 34, bold: true, color: C.white, lineSpacingMultiple: 1.1 });
  T(s, 'ลูกศรและวงสีส้มในคลิป = จุดที่ให้ดู', { x: 0.8, y: 2.85, w: 6.4, h: 0.4, fontSize: 16, color: C.cream });
  const ch = [['01', 'ตั้งคำถาม', '0:00', 0.27, C.leaf], ['02', 'ตรวจที่มาและคัดรับ', '0:16', 1.93, C.rust], ['03', 'เลือกข้อมูลให้ตรงโจทย์', '2:12', 0.72, C.pine2], ['04', 'นำข้อมูลไปใช้', '2:55', 2.1, C.leaf]];
  ch.forEach(([n, t, tm, , col], i) => {
    const y = 3.6 + i * 0.78;
    box(s, 0.8, y, 6.4, 0.64, C.white, { tr: 90, line: C.cream, lw: 0.75 });
    s.addShape(pres.ShapeType.ellipse, { x: 0.95, y: y + 0.1, w: 0.44, h: 0.44, fill: { color: col }, line: { color: C.white, width: 1 } });
    T(s, n, { x: 0.95, y: y + 0.1, w: 0.44, h: 0.44, fontSize: 12, bold: true, color: C.white, align: 'center', valign: 'middle' });
    T(s, t, { x: 1.6, y, w: 4.2, h: 0.64, fontSize: 17, bold: true, color: C.white, valign: 'middle' });
    T(s, tm, { x: 5.8, y, w: 1.25, h: 0.64, fontSize: 15, color: C.cream, align: 'right', valign: 'middle' });
  });
  T(s, 'ไฟล์: output/prototype/TamsoodBase-Website-Evidence-5min-TH-annotated.mp4', { x: 0.8, y: 6.85, w: 8, h: 0.3, fontSize: 11, color: C.mint });
  box(s, 7.75, 0.95, 5.0, 2.95, C.white, { r: 0.12 });
  s.addImage({ path: A('f_trace.jpg'), x: 7.83, y: 1.03, w: 4.84, h: 2.72 });
  box(s, 7.75, 4.1, 5.0, 2.95, C.white, { r: 0.12 });
  s.addImage({ path: A('f_table.jpg'), x: 7.83, y: 4.18, w: 4.84, h: 2.72 });
}

// ───────── 5 · ERD + key design decisions (≈30 s)
{
  const s = light('ERD', 'ERD: แถวดิบแยกจากค่าที่แปลง · ที่มาฝังอยู่ในคีย์',
    '[หลังคลิป · 0:00–0:30 · 30 วินาที] ขั้น 5 ของเดโม: ERD และการตัดสินใจหลัก มี 9 ตารางใน MySQL schema tamsood_research (ภาพนี้ย่อ 7 ตาราง ไม่วาด publisher กับ product) ' +
    'จุดเด่นคือคีย์ของ observation คือ (snapshot_id, source_line) ซึ่งเป็นคีย์เดียวกับแถวดิบใน source_record ทุกค่าจึงชี้กลับแถวต้นฉบับได้โดยโครงสร้าง ' +
    'เก็บ raw_value คู่ amount แบบ DECIMAL เพื่อเทียบกลับไฟล์ แถวซ้ำและแถวที่ถูกปฏิเสธมีตารางของตัวเอง (duplicate_disposition, rejected_record) ไม่ลบทิ้ง ' +
    'และมี CHECK กันค่าติดลบกับวันผลิตเกินจำนวนวันของเดือน ถ้าถูกถามว่าทำไมไม่เก็บ flow เป็น string: เล่มบทที่ 4 มีรายละเอียดของตาราง LCI ส่วนชุด DMF ที่เห็นนี้เก็บค่าตามไฟล์ต้นทาง');
  const tb = (x, y, w, h, name, lines, hi) => {
    box(s, x, y, w, h, C.white, { line: hi ? C.rust : C.pine2, lw: hi ? 2.5 : 1.5, r: 0.1 });
    box(s, x, y, w, 0.36, hi ? C.rust : C.pine2, { r: 0.08 });
    T(s, name, { x: x + 0.12, y, w: w - 0.2, h: 0.36, fontSize: 13, bold: true, color: C.white, valign: 'middle' });
    T(s, lines.join('\n'), { x: x + 0.12, y: y + 0.42, w: w - 0.2, h: h - 0.46, fontSize: 11, color: C.ink, lineSpacingMultiple: 1.05 });
  };
  const arr = (x1, y1, x2, y2) => s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), line: { color: C.rust2, width: 2.25, endArrowType: 'triangle' } });
  tb(0.7, 2.05, 2.3, 1.2, 'source_resource', ['PK package', 'FK publisher, product']);
  tb(3.4, 2.05, 2.7, 1.2, 'resource_snapshot', ['PK snapshot_id', 'csv_url · csv_sha256', 'metadata_unit']);
  tb(6.5, 2.05, 2.5, 1.2, 'source_record', ['PK (snapshot_id, source_line)', 'raw_json', 'record_content_sha256']);
  tb(0.7, 3.85, 2.3, 1.25, 'production_context', ['PK context_id', 'area · block_label', 'source_group']);
  tb(3.4, 3.85, 2.7, 1.25, 'observation', ['PK = FK (snapshot_id, source_line)', 'FK context_id', 'raw_value + amount DECIMAL(30,12)', 'period_start · production_days'], true);
  tb(6.5, 3.85, 2.5, 1.25, 'duplicate_disposition', ['PK = FK (snapshot_id, source_line)', 'status · representative_line']);
  arr(3.0, 2.65, 3.4, 2.65); arr(6.1, 2.65, 6.5, 2.65);
  arr(4.75, 3.25, 4.75, 3.85); arr(3.0, 4.47, 3.4, 4.47); arr(6.1, 4.47, 6.5, 4.47);
  // composite FK: observation -> source_record (drawn from source_record down-left to observation)
  s.addShape(pres.ShapeType.line, { x: 5.9, y: 3.25, w: 1.0, h: 0.6, flipH: true, line: { color: C.rust, width: 2.25, dashType: 'dash', endArrowType: 'triangle' } });
  pill(s, 0.7, 5.4, 8.3, 0.42, C.amber, 'rejected_record (PK = FK → source_record · reasons_json) เก็บ 6 แถวที่ปฏิเสธพร้อมเหตุผล', { color: C.rust, fs: 12, line: C.cream });
  T(s, 'ภาพย่อ 7 จาก 9 ตาราง (ไม่วาด publisher, product) · เส้นประ = FK ประกอบ (snapshot_id, source_line) ระหว่าง observation กับ source_record (1 : 0..1) · ERD เต็มที่หัวข้อ 4.1 ในเล่ม', { x: 0.7, y: 6.0, w: 8.3, h: 0.6, fontSize: 11.5, color: C.mute });
  T(s, 'เหตุผลการออกแบบ', { x: 9.35, y: 2.0, w: 3.4, h: 0.35, fontSize: 15, bold: true, color: C.pine });
  const why = [['ที่มาอยู่ในคีย์', 'PK = (snapshot_id, source_line) ทุกค่าชี้กลับแถวต้นฉบับ'], ['ค่าดิบคู่ค่าแปลง', 'เก็บ raw_value คู่ amount เทียบกลับไฟล์ได้'], ['ไม่ลบทิ้ง', 'แถวซ้ำ/ถูกปฏิเสธมีตารางของตัวเอง'], ['กันค่าผิด', 'CHECK ค่าติดลบ · วันผลิตเกินวันในเดือน']];
  why.forEach(([h, d], i) => {
    const y = 2.4 + i * 1.08;
    box(s, 9.35, y, 3.4, 0.96, C.white, { line: C.line, lw: 1 });
    T(s, h, { x: 9.5, y: y + 0.08, w: 3.1, h: 0.3, fontSize: 13, bold: true, color: C.rust });
    T(s, d, { x: 9.5, y: y + 0.4, w: 3.1, h: 0.5, fontSize: 11.5, color: C.ink });
  });
}

// ───────── 6 · SQL that answers a use case (≈30 s)
{
  const s = light('SQL', 'SQL ตอบ use case: ได้ค่า พร้อมที่มา ในแถวเดียวกัน',
    '[หลังคลิป · 0:30–1:00 · 30 วินาที] ขั้น 6 ของเดโม: use case คือ "แหล่งไหนผลิตน้ำมันดิบมากที่สุดในเดือนมีนาคม 2026 และค่านี้มาจากบรรทัดไหนของไฟล์" ' +
    'query อ่านจาก view deduplicated_pending ซึ่ง JOIN 5 ตาราง และกรองเฉพาะแถวที่ไม่ใช่สำเนา ผลคือ 4 แหล่งแรกพร้อมค่าต้นฉบับ หน่วย และเลขบรรทัด ' +
    'เช่น เบญจมาศ 19,337.55 บาร์เรล บรรทัด 11399 ย้ำข้อจำกัด: ไฟล์ไม่ได้บอกว่าเป็นยอดรวมเดือนหรืออัตราต่อวัน ทีมจึงไม่บวกข้ามเดือน ' +
    'ผลทั้ง 4 แถวตรงกับ API จริง และรันซ้ำบน MySQL 8.4 ฐานทดลองแยกแล้ว (evidence/presentation-mysql-local-2026-11-15.json) แต่ไม่ใช่การรันบน EC2 โดยตรง จึงอย่าอ้างว่ารันสดบนฐาน production ตัวอย่างอื่นอยู่ใน sql/mysql/full-queries.sql ' +
    'ชื่อ view เป็นชื่อเดิม กรองแค่แถวที่ไม่ใช่สำเนา ไม่ได้กรองเฉพาะ Accepted (4 แถวนี้เป็น Accepted ตาม API) ถ้าพูดถึงการย้อนที่มาในคลิปคือแถวเอราวัณ 11202 คนละตัวอย่างกับ 11399 และไพลินเหนือ 11394 บนหน้าปก');
  box(s, 0.7, 2.05, 6.4, 3.0, C.pine, { r: 0.12 });
  s.addText([
    { text: 'SELECT ', options: { color: C.cream, bold: true } }, { text: 'source_group, area, raw_value,\n', options: { color: C.white } },
    { text: '       metadata_unit, source_line, csv_sha256\n', options: { color: C.white } },
    { text: 'FROM   ', options: { color: C.cream, bold: true } }, { text: 'deduplicated_pending\n', options: { color: C.white } },
    { text: 'WHERE  ', options: { color: C.cream, bold: true } }, { text: "product_code = 'crude_oil'\n", options: { color: C.white } },
    { text: '  AND  ', options: { color: C.cream, bold: true } }, { text: "period_start = '2026-03-01'\n", options: { color: C.white } },
    { text: 'ORDER  BY ', options: { color: C.cream, bold: true } }, { text: 'amount DESC\n', options: { color: C.white } },
    { text: 'LIMIT  ', options: { color: C.cream, bold: true } }, { text: '4;', options: { color: C.white } },
  ], { x: 0.95, y: 2.25, w: 5.9, h: 2.6, fontFace: 'Consolas', fontSize: 16, margin: 0, isTextBox: true, valign: 'top', lineSpacingMultiple: 1.1 });
  T(s, 'view JOIN 5 ตาราง: observation · production_context · resource_snapshot · source_resource · duplicate_disposition', { x: 0.7, y: 5.2, w: 6.4, h: 0.6, fontSize: 12.5, color: C.mute });
  T(s, 'กรองเฉพาะแถวที่ไม่ใช่สำเนา (SINGLETON · EXACT_REPRESENTATIVE) · ตัวอย่างอื่นอยู่ใน sql/mysql/full-queries.sql', { x: 0.7, y: 5.85, w: 6.4, h: 0.6, fontSize: 12.5, color: C.mute });
  const hdr = ['แหล่งผลิต', 'พื้นที่', 'ค่าต้นฉบับ (บาร์เรล)', 'บรรทัด'];
  const rows = [['เบญจมาศ', 'ในทะเล', '19337.54839', '11399'], ['Sirikit และอื่นๆ ใน S1', 'บนบก', '18557', '11425'], ['ปลาทอง', 'ในทะเล', '11760.67294', '11407'], ['นงเยาว์', 'ในทะเล', '9703.50129', '11402']];
  const cw = [2.25, 0.9, 1.55, 0.8]; const tx = 7.4;
  let x = tx; box(s, tx, 2.05, 5.5, 0.55, C.pine2, { r: 0.08 });
  hdr.forEach((h, j) => { T(s, h, { x: x + 0.1, y: 2.05, w: cw[j] - 0.12, h: 0.55, fontSize: 12, bold: true, color: C.white, valign: 'middle', align: j > 1 ? 'right' : 'left' }); x += cw[j]; });
  rows.forEach((r, i) => {
    const y = 2.7 + i * 0.62; box(s, tx, y, 5.5, 0.54, C.white, { r: 0.08, line: C.line, lw: 0.75 });
    let xx = tx; r.forEach((v, j) => { T(s, v, { x: xx + 0.1, y, w: cw[j] - 0.12, h: 0.54, fontSize: j === 3 ? 13 : 12.5, bold: j === 3, color: j === 3 ? C.rust : C.ink, valign: 'middle', align: j > 1 ? 'right' : 'left' }); xx += cw[j]; });
  });
  pill(s, tx, 5.3, 2.9, 0.4, C.amber, '4 จาก 34 แหล่งในเดือนนั้น', { color: C.rust, fs: 12, line: C.cream });
  T(s, 'ไฟล์ไม่ได้ระบุว่าเป็นยอดรวมเดือนหรืออัตราต่อวัน ทีมจึงไม่บวกข้ามเดือน', { x: tx, y: 5.85, w: 5.5, h: 0.4, fontSize: 12.5, color: C.mute });
  T(s, 'ตัวอย่าง trace ในคลิปใช้แถวเอราวัณ บรรทัด 11202 (หน้าปกใช้ไพลินเหนือ 11394)', { x: tx, y: 6.3, w: 5.5, h: 0.4, fontSize: 12.5, bold: true, color: C.pine });
}

// ───────── 5 · Results (≈40 s)
{
  const s = light('ผลลัพธ์', 'ทีมรับ 41,072 รายการ จาก 41,315 ที่พิจารณา',
    '[หลังคลิป · 1:00–1:25 · 25 วินาที] สรุปตัวเลข ทีมรับ 41,072 รายการตามกฎ AR-2 จาก 41,315 ที่พิจารณา ส่วนใหญ่มาจาก DMF 34,667 และ EPPO 5,934 ' +
    'อีก 243 รายการยังไม่รวมในยอดรับ (พักตรวจหรือแยกออก) ทุกแถวมีเหตุผลกำกับ คำว่า "รับ" หมายถึงผ่านเกณฑ์ของทีม ยังไม่ใช่การรับรองจากภายนอก ' +
    'ตัวอย่างที่ผู้ช่วยตอบ: FAME 10.7 เทียบกับดีเซลฟอสซิล 219 kg CO2e ต่อ 1,000 MJ เป็นผลที่ผู้วิจัยรายงานในตาราง 5 ไม่ใช่ผลคำนวณของทีม');
  T(s, '41,072', { x: 0.7, y: 2.0, w: 4.6, h: 1.4, fontSize: 82, bold: true, color: C.rust });
  T(s, 'รายการที่ทีมรับ (Accepted)\nตามเกณฑ์ AR-2 ของทีม', { x: 0.75, y: 3.45, w: 4.4, h: 0.8, fontSize: 17, color: C.mute, lineSpacingMultiple: 1.1 });
  pill(s, 0.75, 4.4, 4.6, 0.42, C.amber, '243 รายการยังไม่รวมในยอดรับ · มีเหตุผลทุกแถว', { color: C.rust, fs: 13, line: C.cream });
  const bars = [['DMF', 34667, '34,667', C.pine2], ['EPPO', 5934, '5,934', C.leaf], ['NSO', 273, '273', C.rust], ['งานวิจัย', 101, '101', C.rust], ['รายงานบริษัท', 97, '97', C.rust]];
  const maxW = 4.4;
  bars.forEach(([lab, v, txt, col], i) => {
    const y = 2.1 + i * 0.62;
    T(s, lab, { x: 5.7, y, w: 1.55, h: 0.44, fontSize: 15, bold: true, color: C.ink, valign: 'middle' });
    const w = Math.max(0.08, (v / 34667) * maxW);
    box(s, 7.3, y + 0.05, w, 0.34, col, { r: 0.08 });
    T(s, txt, { x: 7.3 + w + 0.12, y, w: 1.4, h: 0.44, fontSize: 15, bold: true, color: col, valign: 'middle' });
  });
  T(s, 'DMF = กรมเชื้อเพลิงธรรมชาติ · EPPO = สนพ. · NSO = สำนักงานสถิติแห่งชาติ', { x: 5.7, y: 5.25, w: 7, h: 0.3, fontSize: 11, color: C.mute });
  box(s, 0.7, 5.65, 5.7, 1.2, C.white, { line: C.line, lw: 1 });
  T(s, 'ทุกค่ากด “ดูที่มา” → เปิดบรรทัดต้นฉบับ', { x: 0.95, y: 5.78, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: C.pine });
  T(s, 'ค่าเดิม · หน่วย · ช่วงเวลา · บรรทัดในไฟล์ · รหัสไฟล์', { x: 0.95, y: 6.25, w: 5.3, h: 0.4, fontSize: 13, color: C.mute });
  box(s, 6.65, 5.65, 6.0, 1.2, C.pine, {});
  T(s, 'FAME 10.7  vs  ดีเซลฟอสซิล 219', { x: 6.9, y: 5.75, w: 5.6, h: 0.45, fontSize: 20, bold: true, color: C.white });
  T(s, 'kg CO₂e ต่อ 1,000 MJ · ผลที่ผู้วิจัยรายงาน (ตาราง 5) ไม่ใช่ผลคำนวณของทีม', { x: 6.9, y: 6.25, w: 5.6, h: 0.5, fontSize: 12.5, color: C.cream });
}

// ───────── 6 · Honest limits (≈40 s)
{
  const s = light('ข้อจำกัด', 'พูดได้เท่าที่มีหลักฐาน · ที่ยังไม่ปิด เราบอกตรง ๆ',
    '[หลังคลิป · 1:25–1:55 · 30 วินาที] เราแยกสิ่งที่ตอบได้กับสิ่งที่ยังตอบไม่ได้ ตอบได้: ตามค่าไปถึงบรรทัดต้นฉบับ มีกฎรับ-พักที่อธิบายได้ ผล LCA ของไบโอดีเซลตามที่ผู้วิจัยรายงานพร้อมหน้าและตารางต้นฉบับ และเว็บกับผู้ช่วยเปิดใช้จริง ' +
    'ยังไม่ปิด: บัญชี LCI ที่ทีมเชื่อมครบวงจรเอง เช่น ขนส่งและของเสีย จึงยังไม่คำนวณ CO2e รวมของทีม ฐานเวลาของ DMF รอยืนยัน สิทธิ์เผยแพร่ของบางแหล่ง และยังไม่มีการรับรองจาก MTEC ' +
    'ย้ำว่าเลือกพักข้อมูลที่ยังไม่เคลียร์ ดีกว่าปล่อยตัวเลขที่ยังไม่แน่ใจ');
  box(s, 0.7, 2.1, 5.85, 4.55, C.white, { line: C.leaf, lw: 2 });
  pill(s, 0.95, 2.3, 2.4, 0.4, C.leaf, '✓  ตอบได้ตอนนี้', { fs: 14 });
  const ok = ['ตามทุกค่าไปถึงบรรทัดต้นฉบับ + รหัสไฟล์', 'กฎรับ/พัก AR-2 อธิบายเหตุผลทุกแถว', 'ผล LCA ไบโอดีเซลที่ผู้วิจัยรายงาน พร้อมหน้า/ตารางต้นฉบับ', 'เว็บ + ผู้ช่วยตอบ (ยินยอมก่อนส่ง) เปิดใช้จริง'];
  ok.forEach((t, i) => T(s, '✓  ' + t, { x: 0.98, y: 2.98 + i * 0.88, w: 5.35, h: 0.8, fontSize: 15, color: C.ink }));
  box(s, 6.8, 2.1, 5.85, 4.55, C.white, { line: C.rust, lw: 2 });
  pill(s, 7.05, 2.3, 3.25, 0.4, C.rust, '!  ยังไม่ปิด · ต้องเติมหลักฐาน', { fs: 14 });
  const gap = ['บัญชี LCI ที่ทีมเชื่อมครบวงจรเอง (ขนส่ง ของเสีย ข้อมูลพื้นหลัง) → CO₂e รวมของทีมจึงยังไม่คำนวณ', 'ฐานเวลา DMF (ปริมาณหรืออัตราต่อวัน) รอยืนยันกับหน่วยงาน', 'สิทธิ์เผยแพร่ข้อมูลบางแหล่งและข้อมูลบริษัท ยังไม่ยืนยัน', '“รับ” = ผ่านเกณฑ์ของทีม ยังไม่มีการรับรองจาก MTEC'];
  gap.forEach((t, i) => T(s, '!  ' + t, { x: 7.08, y: 2.98 + i * 0.88, w: 5.35, h: 0.8, fontSize: 15, color: C.ink }));
}

// ───────── 7 · Next + close (≈35 s)
{
  const s = dark('[หลังคลิป · 1:55–2:10 · 15 วินาที] ก้าวต่อไปสามเรื่อง ยืนยันฐานเวลา DMF กับกรมเชื้อเพลิงธรรมชาติ หาข้อมูลขนส่งและการปันส่วนของไทยเพื่อปิดช่อง LCI และทำตารางชื่อแหล่งผลิตกลาง ' +
    'ปิดด้วยประโยค: Build data that someone else can trust. ขอบคุณครับ/ค่ะ พร้อมตอบคำถาม 4 นาที (สไลด์ถัดไปคือคำตอบสำรอง)');
  pill(s, 0.8, 0.6, 1.9, 0.4, C.rust, 'ก้าวต่อไป', { fs: 13 });
  const nx = [['1', 'ยืนยันฐานเวลาของ DMF', 'ถามกรมเชื้อเพลิงธรรมชาติว่าเป็นปริมาณหรืออัตราต่อวัน'], ['2', 'หาข้อมูลขนส่งและการปันส่วนของไทย', 'ปิดช่อง LCI ที่ยังขาด เพื่อคำนวณ CO₂e รวมได้เอง'], ['3', 'ทำตารางชื่อแหล่งผลิตกลาง', 'รวมชื่อแหล่งที่สะกดต่างกัน และแยก flow / unit ออกจากข้อความ']];
  nx.forEach(([n, h, d], i) => {
    const y = 1.35 + i * 1.5;
    box(s, 0.8, y, 6.7, 1.28, C.white, { tr: 90, line: C.cream, lw: 1 });
    s.addShape(pres.ShapeType.ellipse, { x: 1.05, y: y + 0.3, w: 0.66, h: 0.66, fill: { color: C.rust }, line: { color: C.white, width: 1.5 } });
    T(s, n, { x: 1.05, y: y + 0.3, w: 0.66, h: 0.66, fontSize: 22, bold: true, color: C.white, align: 'center', valign: 'middle' });
    T(s, h, { x: 1.95, y: y + 0.2, w: 5.4, h: 0.45, fontSize: 19, bold: true, color: C.white });
    T(s, d, { x: 1.95, y: y + 0.7, w: 5.4, h: 0.45, fontSize: 13.5, color: C.mint });
  });
  T(s, '“Build data that someone else can trust.”', { x: 7.9, y: 1.5, w: 4.9, h: 2.2, fontSize: 34, bold: true, color: C.white, lineSpacingMultiple: 1.1 });
  s.addShape(pres.ShapeType.line, { x: 7.95, y: 3.95, w: 1.6, h: 0, line: { color: C.rust2, width: 3 } });
  T(s, 'ขอบคุณครับ / ค่ะ  ·  พร้อมตอบคำถาม', { x: 7.9, y: 4.2, w: 4.9, h: 0.45, fontSize: 18, color: C.cream });
  T(s, 'tamsoodbase.vercel.app', { x: 7.9, y: 4.85, w: 4.9, h: 0.4, fontSize: 20, bold: true, color: C.white });
  T(s, 'ผู้ช่วยตอบคำถามอยู่ที่มุมจอทุกหน้า · /ask.html', { x: 7.9, y: 5.35, w: 4.9, h: 0.35, fontSize: 12.5, color: C.mint });
  T(s, 'ทีม S2-G05 · ตฤณเดช · เอดาวัต · สิริเดช · พีรภัทร · ณวตา', { x: 0.8, y: 6.85, w: 9, h: 0.3, fontSize: 12, color: C.mint });
}

// ───────── 8 · Backup: Q&A cheat sheet
{
  const s = light('สำรอง · ถาม-ตอบ', 'คำถามที่อาจถูกถาม · คำตอบสั้น',
    'สไลด์สำรองสำหรับช่วงถาม-ตอบ 4 นาที ไม่ต้องฉายตอนนำเสนอ 3 นาที ใช้เมื่อกรรมการถามตามหัวข้อบนหน้าวันงาน (Requirement, Mapping, Validation, Provenance, SQL, Team Contribution, AI Use) ' +
    'ช่อง "ทีมกรอก" ต้องเติมจากข้อมูลจริงของทีมก่อนวันงาน อย่าตอบเกินหลักฐาน');
  const qa = [
    ['Validation · duplicate rule?', 'ช่วงเวลา+แหล่งเดียวกัน ค่าเท่ากันทุกช่อง = สำเนาซ้ำ เก็บตัวแทน 1 แถว (42) · ค่าต่างกัน = พักรอหลักฐาน (186)'],
    ['Provenance · เปิด source ของ tuple?', 'เว็บ “ดูที่มา” → ไฟล์ production_oil.csv บรรทัด 11202 · SHA-256 ของไฟล์ · หน่วยเดิมของต้นฉบับ'],
    ['Mapping · field ต้นฉบับ → canonical?', 'เก็บ raw_value คู่กับ amount (DECIMAL) · ปี พ.ศ. → ค.ศ. · ตารางแถวดิบแยกจากค่าที่แปลงแล้ว'],
    ['SQL · ใช้ JOIN/constraint อย่างไร?', 'view deduplicated_pending JOIN observation · context · snapshot · source · disposition · PK/FK = (snapshot_id, source_line)'],
    ['Requirement · ทำไมต้องมีหน่วย/ฐานเวลา?', 'ค่าเดียวกันคนละหน่วย/ฐานเวลาเทียบกันไม่ได้ จึงพักค่าที่ยังไม่ยืนยัน และไม่บวกข้ามเดือน'],
    ['AI Use · AI ช่วยส่วนไหน?', 'ผู้ช่วยตอบคำถามเว็บ: ตัวเลขคำนวณด้วยโค้ด ไม่ให้ AI คิดเอง · ส่งข้อมูลให้โมเดลภายนอกต่อเมื่อผู้ใช้ยินยอม · [ทีมกรอก: AI ช่วยพัฒนาตรงไหน และตรวจอย่างไร]'],
    ['Team Contribution · ใครทำอะไร?', 'PM/BA ตฤณเดช · Schema เอดาวัต · Data สิริเดช · SQL พีรภัทร · QA ณวตา · [ทีมกรอก: หลักฐานของแต่ละคน]'],
    ['Modeling · ทำไม FLOW เป็นข้อความ ไม่แยกตาราง?', 'ชุดสินค้า 16 รายการเก็บ flow ตามชื่อ+หน่วยในบทความ (identity ระดับแหล่ง) เพราะยังไม่ยืนยันว่าชื่อข้ามแหล่งคือสิ่งเดียวกัน · ตาราง flow/unit กลางคือก้าวต่อไป · ใน Neo4j lab Flow เป็นโหนดแยก'],
  ];
  qa.forEach(([q, a], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.7 + col * 6.05, y = 2.0 + row * 1.2;
    box(s, x, y, 5.85, 1.07, C.white, { line: C.line, lw: 1 });
    T(s, q, { x: x + 0.2, y: y + 0.08, w: 5.5, h: 0.3, fontSize: 12.5, bold: true, color: C.rust });
    T(s, a, { x: x + 0.2, y: y + 0.4, w: 5.5, h: 0.64, fontSize: 11.5, color: C.ink, lineSpacingMultiple: 0.95 });
  });
}

// ───────── 9 · Backup: numbers by source
{
  const s = light('สำรอง · ตัวเลข', 'ยอดรับและยอดที่ยังไม่รวม แยกตามแหล่ง (กฎ AR-2)',
    'สไลด์สำรอง ตัวเลขทั้งหมดมาจาก docs/acceptance-ledger.json และ PROJECT_STATE ณ 13 พ.ย. 2569 ถ้ากรรมการถามที่มาของ 41,072 ให้เปิดตารางนี้ ' +
    'DMF 34,667 + EPPO 5,934 + NSO 273 + งานวิจัย 101 (57 บัญชีรายการ + 44 ผล LCA) + บริษัท 97 = 41,072');
  const rows = [
    ['ชุดข้อมูล', 'พิจารณา', 'รับ', 'ไม่รวม', 'เหตุผลที่ยังไม่รวมในยอดรับ'],
    ['DMF · กรมเชื้อเพลิงฯ', '34,905', '34,667', '238', 'โครงสร้างผิด 6 · พักหน่วย/ขนาด 4 · พักตรวจ 228 (สำเนา 42 + ขัดกัน 186)'],
    ['EPPO · สนพ.', '5,934', '5,934', '0', '—'],
    ['NSO · สำนักงานสถิติฯ', '273', '273', '0', '—'],
    ['งานวิจัย (บัญชี 57 + LCA 44)', '102', '101', '1', 'ขาดหน่วย 1 รายการ'],
    ['รายงานบริษัท (อ้างอิง)', '101', '97', '4', 'สำเนาซ้ำจากฉบับครบ 4 รายการ'],
    ['รวม', '41,315', '41,072', '243', 'ทุกแถวมีเหตุผลใน docs/acceptance-ledger.json'],
  ];
  const colW = [3.2, 1.3, 1.3, 1.1, 5.05];
  rows.forEach((r, i) => {
    const y = 2.05 + i * 0.63;
    const hdr = i === 0, tot = i === rows.length - 1;
    box(s, 0.7, y, 12.0, 0.56, hdr ? C.pine : tot ? C.amber : C.white, { r: 0.08, line: hdr ? C.pine : C.line, lw: 0.75 });
    let x = 0.7;
    r.forEach((v, j) => {
      T(s, v, { x: x + 0.18, y, w: colW[j] - 0.3, h: 0.56, fontSize: j === 4 ? 12 : 14, bold: hdr || tot || j === 2, color: hdr ? C.white : (tot ? C.rust : C.ink), valign: 'middle', align: j > 0 && j < 4 ? 'right' : 'left' });
      x += colW[j];
    });
  });
  T(s, '“รับ” = ผ่านเกณฑ์ของทีม (ค่าตรงต้นทาง · ไม่ซ้ำ · ย้อนตรวจได้ · เกี่ยวข้องกับไทย · ไม่มีข้อสงสัยหน่วย/ขนาด) ยังไม่ใช่การรับรองจาก MTEC', { x: 0.7, y: 6.55, w: 11.9, h: 0.3, fontSize: 11, color: C.mute });
}

pres.writeFile({ fileName: path.join(__dirname, '..', 'S2-G05_M4_Slides_3min.pptx') }).then((f) => console.log('wrote', f));
