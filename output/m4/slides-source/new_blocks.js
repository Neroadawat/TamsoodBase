// ───────── 5 · ERD + key design decisions (≈30 s)
{
  const s = light('ERD', 'ERD: แถวดิบแยกจากค่าที่แปลง · ที่มาฝังอยู่ในคีย์',
    '[หลังคลิป · 0:00–0:30 · 30 วินาที] ขั้น 5 ของเดโม: ERD และการตัดสินใจหลัก มี 9 ตารางใน MySQL schema tamsood_research ' +
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
  pill(s, 0.7, 5.4, 8.3, 0.42, C.amber, 'rejected_record (PK = FK → source_record · reasons_json) เก็บ 6 แถวที่ปฏิเสธพร้อมเหตุผล', { color: C.rust, fs: 12, line: C.cream });
  T(s, '9 ตาราง · MySQL InnoDB · schema tamsood_research · ERD ฉบับเต็มอยู่ที่หัวข้อ 4.1 ในเล่ม', { x: 0.7, y: 6.0, w: 8.3, h: 0.35, fontSize: 12, color: C.mute });
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
    'ถ้าถูกขอให้รันสด ใช้ sql/mysql/full-queries.sql ได้ (ตรวจกับฐานจริงก่อนขึ้นเวที)');
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
  const cw = [2.35, 0.95, 1.6, 0.8]; const tx = 7.5;
  let x = tx; box(s, tx, 2.05, 5.7, 0.55, C.pine2, { r: 0.08 });
  hdr.forEach((h, j) => { T(s, h, { x: x + 0.1, y: 2.05, w: cw[j] - 0.12, h: 0.55, fontSize: 12, bold: true, color: C.white, valign: 'middle', align: j > 1 ? 'right' : 'left' }); x += cw[j]; });
  rows.forEach((r, i) => {
    const y = 2.7 + i * 0.62; box(s, tx, y, 5.7, 0.54, C.white, { r: 0.08, line: C.line, lw: 0.75 });
    let xx = tx; r.forEach((v, j) => { T(s, v, { x: xx + 0.1, y, w: cw[j] - 0.12, h: 0.54, fontSize: j === 3 ? 13 : 12.5, bold: j === 3, color: j === 3 ? C.rust : C.ink, valign: 'middle', align: j > 1 ? 'right' : 'left' }); xx += cw[j]; });
  });
  pill(s, tx, 5.3, 2.9, 0.4, C.amber, '4 จาก 34 แหล่งในเดือนนั้น', { color: C.rust, fs: 12, line: C.cream });
  T(s, 'ไฟล์ไม่ได้ระบุว่าเป็นยอดรวมเดือนหรืออัตราต่อวัน ทีมจึงไม่บวกข้ามเดือน', { x: tx, y: 5.85, w: 5.7, h: 0.4, fontSize: 12.5, color: C.mute });
  T(s, 'ต่อจากนี้: บรรทัด 11399 → ไฟล์ต้นฉบับ → หน่วยงาน (ดูในคลิปฉาก 4)', { x: tx, y: 6.3, w: 5.7, h: 0.4, fontSize: 12.5, bold: true, color: C.pine });
}

