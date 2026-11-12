"""Extend the team's M3 SRS (.docx) into the M4 volume, keeping its formatting.

Reads the M3 file, inserts Chapter 5, the ERD figures, an updated serving-layer
section, Chapters 7-8 and a full table of contents, and writes a new file.
The source document is never modified.

    python build_m4.py <m3.docx> <out.docx> <diagram_dir> [toc_pages.json]
"""
import html
import json
import re
import sys
import zipfile
from PIL import Image

SRC, OUT, DIAGRAMS = sys.argv[1], sys.argv[2], sys.argv[3]
TOC_PAGES = json.load(open(sys.argv[4], encoding="utf-8")) if len(sys.argv) > 4 else {}
FONT = '<w:rFonts w:ascii="TH SarabunPSK" w:hAnsi="TH SarabunPSK" w:cs="TH SarabunPSK"/>'


def esc(text):
    return html.escape(str(text), quote=False)


def rpr(size=28, bold=False):
    return f'<w:rPr>{FONT}{"<w:b/><w:bCs/>" if bold else ""}<w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'


def para(text, size=28, bold=False, keep=False, page_break=False, align=None):
    ppr = ("<w:keepNext/>" if keep else "") + (f'<w:jc w:val="{align}"/>' if align else "")
    brk = '<w:r><w:br w:type="page"/></w:r>' if page_break else ""
    return (f'<w:p><w:pPr>{ppr}{rpr(size, bold)}</w:pPr>{brk}'
            f'<w:r>{rpr(size, bold)}<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>')


def h1(text):
    return para(text, 36, True, keep=True, page_break=True)


def h2(text):
    return para(text, 32, True, keep=True)


def h3(text):
    return para(text, 28, True, keep=True)


def body(text):
    return para(text)


def bullet(text):
    return para("- " + text)


def cell(text, width, bold=False):
    run = f'<w:rPr>{FONT}{"<w:b/><w:bCs/>" if bold else ""}</w:rPr>'
    paragraphs = "".join(f'<w:p><w:pPr>{run}</w:pPr><w:r>{run}<w:t xml:space="preserve">{esc(line)}</w:t></w:r></w:p>'
                         for line in str(text).split("\n"))
    margin = "".join(f'<w:{side} w:w="100" w:type="dxa"/>' for side in ("top", "left", "bottom", "right"))
    return f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:tcMar>{margin}</w:tcMar></w:tcPr>{paragraphs}</w:tc>'


def table(headers, rows, widths):
    assert sum(widths) == 9360 and all(len(row) == len(widths) for row in rows), headers
    borders = "".join(f'<w:{side} w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
                      for side in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    head = "<w:tr><w:trPr><w:tblHeader/></w:trPr>" + "".join(cell(h, w, True) for h, w in zip(headers, widths)) + "</w:tr>"
    lines = "".join("<w:tr>" + "".join(cell(v, w) for v, w in zip(row, widths)) + "</w:tr>" for row in rows)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
            '<w:tblLayout w:type="fixed"/><w:tblLook w:val="0600" w:firstRow="0" w:lastRow="0" w:firstColumn="0" '
            f'w:lastColumn="0" w:noHBand="1" w:noVBand="1"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{head}{lines}</w:tbl>'
            + para("", 16))


IMAGES = []


def figure(filename, caption, max_width_in=5.6, max_height_in=7.6):
    width, height = Image.open(f"{DIAGRAMS}/{filename}").size
    scale = min(max_width_in / width, max_height_in / height)
    cx, cy = int(width * scale * 914400), int(height * scale * 914400)
    index = len(IMAGES) + 1
    rid = f"rIdM4img{index}"
    IMAGES.append((rid, filename))
    drawing = (
        f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:docPr id="{9000 + index}" name="Figure {index}" descr="{esc(caption)}"/>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:nvPicPr><pic:cNvPr id="{9000 + index}" name="{esc(filename)}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
        '</wp:inline></w:drawing>')
    return (f'<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r>{drawing}</w:r></w:p>'
            + para(caption, 24, False, align="center"))


def text_of(xml):
    return html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)))


def clone_row(row_xml, texts):
    """Reuse a row's own cell and run formatting, replacing only the text."""
    cells = re.findall(r"<w:tc>.*?</w:tc>", row_xml, flags=re.S)
    assert len(cells) == len(texts), (len(cells), texts)
    rebuilt = []
    for cell_xml, value in zip(cells, texts):
        tcpr = re.search(r"<w:tcPr>.*?</w:tcPr>", cell_xml, flags=re.S).group(0)
        paragraph = re.search(r"<w:p[ >].*?</w:p>", cell_xml, flags=re.S).group(0)
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", paragraph, flags=re.S)
        run_pr = re.search(r"<w:r[ >](?:(?!</w:r>).)*?(<w:rPr>.*?</w:rPr>)", paragraph, flags=re.S)
        run_pr = re.sub(r"<w:cs/>", "", run_pr.group(1)) if run_pr else f"<w:rPr>{FONT}</w:rPr>"
        if "w:cs=" not in run_pr:
            run_pr = run_pr.replace("<w:rPr>", f"<w:rPr>{FONT}", 1) if "w:rFonts" not in run_pr else run_pr
        rebuilt.append(f'<w:tc>{tcpr}<w:p>{ppr.group(0) if ppr else ""}<w:r>{run_pr}'
                       f'<w:t xml:space="preserve">{esc(value)}</w:t></w:r></w:p></w:tc>')
    opening = re.match(r"<w:tr[^>]*>(?:<w:trPr>.*?</w:trPr>)?", row_xml, flags=re.S).group(0)
    opening = re.sub(r' w14:paraId="[^"]*"| w14:textId="[^"]*"', "", opening)
    return opening + "".join(rebuilt) + "</w:tr>"


# ───────────────────────────────────────────────────────────── new content

CH4_ERD = "".join([
    body("แผนภาพด้านล่างสร้างจากไฟล์ DDL ของแต่ละ schema โดยตรง (sql/mysql/*.sql) เส้นเชื่อมแสดง foreign key และ cardinality ตามข้อบังคับที่ประกาศจริงในฐานข้อมูล"),
    figure("dmf-erd.png", "รูปที่ 4-1 ERD ของ tamsood_research (ข้อมูลการผลิตของ DMF)", 4.6, 6.2),
    table(["ความสัมพันธ์", "Cardinality", "ข้อบังคับที่ใช้"], [
        ["resource_snapshot → source_record", "1 : N", "PK (snapshot_id, source_line); FK snapshot_id"],
        ["source_record → observation", "1 : 0..1", "observation ใช้ PK เดียวกับแถวดิบและเป็น FK ไปยังแถวดิบ"],
        ["source_record → rejected_record", "1 : 0..1", "แถวที่ไม่ผ่านรูปแบบเก็บเหตุผลเป็น JSON ไม่ลบทิ้ง"],
        ["production_context → observation", "1 : N", "FK context_id; area ต้องเป็น บนบก หรือ ในทะเล"],
        ["observation → duplicate_disposition", "1 : 1", "สถานะ SINGLETON / EXACT_REPRESENTATIVE / EXCLUDE_EXACT_COPY / HOLD_CONFLICT"],
    ], [3300, 1400, 4660]),
    figure("corporate-erd.png", "รูปที่ 4-2 ERD ของ tamsood_reusable (ตัวชี้วัดจากรายงานบริษัท)", 4.4, 6.0),
    table(["ความสัมพันธ์", "Cardinality", "ข้อบังคับที่ใช้"], [
        ["document → context → metric", "1 : N : N", "composite FK (context_id, document_id) กันการอ้างขอบเขตข้ามเอกสาร"],
        ["metric → observation", "1 : N", "UNIQUE (metric_key, reference_year)"],
        ["observation → review", "1 : N", "PK (observation_id, policy_version) เก็บผลทบทวนแยกตามรุ่นของกฎ"],
        ["data_release ↔ observation", "M : N", "ตารางเชื่อม release_observation"],
    ], [3300, 1400, 4660]),
    figure("supplemental-erd.png", "รูปที่ 4-3 ERD ของ tamsood_supplemental (สถิติประเทศและบัญชีรายการจากงานวิจัย)", 5.2, 4.2),
    figure("eppo-erd.png", "รูปที่ 4-4 ERD ของ tamsood_eppo (สถิติโรงกลั่นรายเดือน)", 4.6, 2.4),
])

CH5 = "".join([
    h1("5. Implementation"),
    body("บทนี้อธิบายสิ่งที่ทีมสร้างขึ้นจริงในช่วง BUILD ได้แก่ ขั้นตอนดึงข้อมูล คำสั่ง SQL การตรวจสอบพร้อมจำนวนแถวก่อนและหลังตรวจ และการเก็บที่มาของข้อมูล ตัวเลขทั้งหมดในบทนี้มาจากการรันบนชุดข้อมูลในเครื่องของทีม รอบข้อมูล DMF วันที่ 22 ตุลาคม 2569 และตรวจซ้ำล่าสุดวันที่ 13 พฤศจิกายน 2569"),
    h2("5.1 Extraction Pipeline · ขั้นตอนดึงข้อมูล"),
    body("ทุกแหล่งใช้ลำดับเดียวกัน คือ ดาวน์โหลดไฟล์ บันทึกสำเนาพร้อมรหัส SHA-256 เก็บแถวดิบตามต้นฉบับ แล้วจึงแปลงชนิดข้อมูล การรันซ้ำกับไฟล์เดิมจะได้รหัสเดิม จึงใช้พิสูจน์ได้ว่าข้อมูลไม่ถูกแก้ระหว่างทาง"),
    table(["ชุดข้อมูล (SRC)", "สคริปต์", "สิ่งที่อ่าน", "สิ่งที่ได้"], [
        ["DMF การผลิตปิโตรเลียม", "src/acquire_dmf.py\nsrc/process_dmf.py\nsrc/review_dmf.py", "CSV 3 ไฟล์จาก catalog.dmf.go.th", "34,905 แถวดิบ; ตาราง staging, candidate, rejected และ duplicate_disposition"],
        ["EPPO สถิติโรงกลั่น", "scripts/import_eppo.py\nscripts/load_eppo_mysql.py", "CSV ชุด 11_13 และ 11_14", "5,934 ค่า แยกวัตถุดิบเข้ารายบริษัทกับผลผลิตรวมประเทศ"],
        ["NSO สถิติพลังงาน", "scripts/import_nso.py\nscripts/review_nso.py", "CSV ตาราง 13.5–13.8 และ 13.10", "273 ค่า พร้อมเลขบรรทัดและคอลัมน์ต้นทาง"],
        ["รายงานบริษัท", "src/report_pilot.py\nsrc/sprc_report.py\nscripts/run_reference.py", "PDF รายงานความยั่งยืนปี 2024 ของ Thai Oil และ SPRC", "101 ค่า พร้อมเลขหน้า PDF และเลขหน้าที่พิมพ์"],
        ["งานวิจัยไบโอดีเซล", "scripts/build_product_inventory.py\nscripts/extract_upstream_inventory.py", "ตาราง 1–4 ของบทความ (CC BY 4.0)", "รายการเข้า–ออก 16 + 42 รายการ"],
        ["ผล LCA ที่บทความรายงาน", "scripts/build_rag_knowledge_pack.py", "ตาราง 5–6 ของบทความเดียวกัน", "ผลกระทบ 44 ค่า เก็บรูปที่พิมพ์คู่กับค่าทศนิยม"],
    ], [1900, 2500, 2400, 2560]),
    figure("pipeline.png", "รูปที่ 5-1 ลำดับการไหลของข้อมูลจากไฟล์ต้นทางถึงฐานข้อมูลและเว็บ", 5.6, 4.6),
    h2("5.2 SQL · ฐานข้อมูลและคำสั่งที่ใช้"),
    body("ระบบใช้ MySQL 8.4 แบ่งเป็น 4 schema ตามความหมายของข้อมูล และมี schema สำหรับ API อีกหนึ่งชุด ไฟล์ DDL อยู่ในโฟลเดอร์ sql/mysql ของ repository"),
    table(["ไฟล์", "Schema", "จำนวนตาราง", "ใช้ทำอะไร"], [
        ["full-schema.sql", "tamsood_research", "9", "แถวดิบและค่าที่แปลงของ DMF พร้อม view traceable_observations และ deduplicated_pending"],
        ["reusable-schema.sql", "tamsood_reusable", "11", "เอกสาร ขอบเขต ตัวชี้วัด ค่า ผลทบทวน และรุ่นเผยแพร่"],
        ["supplemental-schema.sql", "tamsood_supplemental", "5", "สถิติประเทศ กระบวนการ และรายการเข้า–ออก"],
        ["eppo-schema.sql", "tamsood_eppo", "2", "สถิติโรงกลั่นรายเดือน"],
        ["api-schema.sql", "tamsood_api", "6", "มุมมองสำหรับ API แบบอ่านอย่างเดียว"],
    ], [2200, 2300, 1300, 3560]),
    body("ตัวอย่างคำสั่งที่ตอบ use case \"เดือนมีนาคม 2026 แหล่งใดผลิตน้ำมันดิบมากที่สุด\" โดยผลแต่ละแถวมีเลขบรรทัดของไฟล์ต้นฉบับติดมาด้วย:"),
    body("SELECT source_group, area, raw_value, metadata_unit, source_line, csv_sha256 FROM deduplicated_pending WHERE product_code = 'crude_oil' AND period_start = '2026-03-01' ORDER BY amount DESC LIMIT 4;"),
    table(["แหล่งผลิต", "พื้นที่", "ค่าต้นฉบับ (บาร์เรล)", "บรรทัดในไฟล์"], [
        ["เบญจมาศ", "ในทะเล", "19337.54839", "11399"],
        ["Sirikit และอื่นๆใน S1", "บนบก", "18557", "11425"],
        ["ปลาทอง", "ในทะเล", "11760.67294", "11407"],
        ["นงเยาว์", "ในทะเล", "9703.50129", "11402"],
    ], [3200, 1600, 2600, 1960]),
    body("ผลข้างต้นเป็น 4 จาก 34 แหล่งที่มีข้อมูลในเดือนนั้น ค่าเป็นตัวเลขรายเดือนตามที่ไฟล์รายงาน ทีมยังไม่ได้ยืนยันกับกรมเชื้อเพลิงธรรมชาติว่าเป็นยอดรวมทั้งเดือนหรืออัตราต่อวัน จึงไม่นำมาบวกข้ามเดือน"),
    body("ผลทดลองด้าน transaction และ index: ชุดตรวจ 17 รายการบน MySQL ครอบคลุม rollback ระดับ isolation READ COMMITTED และ REPEATABLE READ และ row lock ส่วนการค้นตามช่วงเวลาของ DMF ให้ผล 102 แถวเท่ากันทั้งแบบใช้และไม่ใช้ index โดยค่ากลางของเวลา 0.208 มิลลิวินาทีเมื่อใช้ index เทียบกับ 12.0 มิลลิวินาทีเมื่อสั่ง IGNORE INDEX เป็นผลทดลองในเครื่อง ไม่ใช่การรับประกันความเร็วของระบบจริง"),
    h2("5.3 Validation · จำนวนแถวก่อนและหลังตรวจ"),
    body("การตรวจแบ่งเป็นสามชั้น คือ ตรวจรูปแบบ ตรวจซ้ำ และทบทวนความหมาย แถวที่ไม่ผ่านจะไม่ถูกลบ แต่ย้ายไปเก็บพร้อมเหตุผล"),
    table(["ชุดข้อมูล", "ก่อนตรวจ", "หลังตรวจ", "ที่ตัดออกหรือพักไว้ และเหตุผล"], [
        ["DMF", "34,905 แถว", "34,671 แถว", "ปฏิเสธ 6 แถว (ค่าว่าง ไม่ระบุพื้นที่หรือแหล่ง) · ตัดสำเนาซ้ำ 42 แถว (ค่าเท่ากันทุกช่อง) · พัก 186 แถว (ช่วงเวลาและแหล่งเดียวกันแต่ค่าต่างกัน)"],
        ["รายงานบริษัท", "101 ค่า", "97 ค่า", "พัก 4 ค่า เพราะชื่อและบริบทของตารางน้ำในรายงานไม่ตรงกัน เก็บทั้งคู่ไว้ ไม่เลือกฝ่ายใด"],
        ["NSO", "273 ค่า", "273 ค่า", "เทียบข้ามแหล่งได้ 169 ค่า: ตรงกัน 141, ต่างเพราะการปัดเศษ 24, ไม่ตรง 4 · อีก 104 ค่ายังไม่มีแหล่งให้เทียบ"],
        ["EPPO", "5,934 ค่า", "5,934 ค่า", "ไม่มีค่าซ้ำตาม (ชุดข้อมูล, ปี, เดือน, รายการ) · บางบริษัทมีเดือนที่ต้นทางไม่รายงาน"],
        ["งานวิจัย", "58 รายการ", "57 รายการ", "พัก 1 รายการ (Land seeding) เพราะบทความไม่ระบุหน่วย ทีมไม่เดาหน่วยให้"],
    ], [1500, 1400, 1400, 5060]),
    body("สถานะที่ต้องอ่านให้ถูก: 34,671 แถวของ DMF และค่าของ EPPO กับ NSO ผ่านการตรวจรูปแบบ ไม่ซ้ำ และย้อนถึงต้นทางได้แล้ว แต่ในฐานข้อมูลยังมีสถานะ PENDING เพราะทีมยังไม่ได้ยืนยันกฎรับข้อมูลสำหรับสถิติของรัฐ รายการที่ทีมรับเป็นข้อมูลอ้างอิงแล้วในตอนนี้จึงมี 97 รายการจากรายงานบริษัท"),
    body("ข้อสังเกตจากการตรวจข้อมูลรอบ 13 พฤศจิกายน 2569: (1) ชื่อแหล่งผลิตของ DMF เปลี่ยนตามช่วงปี และ 12 จาก 136 ชื่อเป็นชื่อกลุ่มที่รวมหลายแหล่ง จึงเทียบข้ามปีโดยตรงไม่ได้ (2) พบค่าก๊าซธรรมชาติของแหล่ง กำแพงแสน อู่ทอง สังฆจาย เดือนกุมภาพันธ์ 2020 เท่ากับ 3,500,000 ซึ่งสูงกว่าค่าอื่นของชุดเดียวกันเกินร้อยเท่า ทีมเก็บค่าตามต้นทางและติดธงไว้ ไม่นำไปคำนวณค่าเฉลี่ย"),
    h2("5.4 Provenance · การเก็บที่มาของข้อมูล"),
    body("ทุกแถวในฐานข้อมูลตอบได้ว่ามาจากไฟล์ใด บรรทัดหรือหน้าใด และไฟล์นั้นมีรหัส SHA-256 อะไร ช่องที่ใช้เก็บที่มาของแต่ละชุดมีดังนี้"),
    table(["ชุดข้อมูล", "ช่องที่ใช้ระบุที่มา", "ระดับที่ย้อนได้"], [
        ["DMF", "csv_url, csv_sha256, metadata_sha256, source_line, raw_json", "แถวของไฟล์ CSV"],
        ["รายงานบริษัท", "source_url, document_id (SHA-256 ของ PDF), pdf_page, printed_page, extracted_text_line", "หน้าและบรรทัดของ PDF"],
        ["NSO", "source_sha256, source_line, source_column", "ช่องของตาราง CSV"],
        ["EPPO", "snapshot_id, source_url, source_line", "แถวของไฟล์ CSV"],
        ["งานวิจัย", "DOI, table_id, source_row, source_column, source_snapshot_sha256", "ช่องของตารางในบทความ"],
    ], [1700, 5200, 2460]),
    body("ตัวอย่างการย้อนหนึ่งค่า: แหล่งไพลินเหนือ ผลิตคอนเดนเสทเดือนมีนาคม 2026 ค่า 5876.859677 บาร์เรล มาจากไฟล์ production_condensate.csv บรรทัดที่ 11394 ไฟล์มีรหัส SHA-256 ขึ้นต้นด้วย 79f5ac2a ดึงจาก catalog.dmf.go.th เมื่อวันที่ 22 ตุลาคม 2569 บนเว็บเปิดดูได้จากหน้า \"แหล่งผลิตน้ำมันและก๊าซ\" โดยกด \"ดูที่มา\" ที่แถวนั้น"),
])

CH6_STATUS = "".join([
    h2("6.8 สถานะ Serving Layer ล่าสุด และข้อแตกต่างของแต่ละแบบ"),
    body("ข้อมูลในหัวข้อ 6.5 และ 6.7 เป็นสถานะ ณ วันที่ 9 พฤศจิกายน 2569 หัวข้อนี้บันทึกสถานะที่เปลี่ยนไปถึงวันที่ 13 พฤศจิกายน 2569 ตามการตัดสินใจของเจ้าของโครงการที่ให้เปิดใช้สำหรับการนำเสนอรายวิชา"),
    table(["ส่วน", "สถานะ ณ 13 พ.ย. 2569", "หลักฐานและข้อจำกัด"], [
        ["เว็บค้นข้อมูล", "เปิดใช้ที่ tamsoodbase.vercel.app ข้อมูล DMF, NSO, EPPO และบัญชีรายการจากงานวิจัยเปิดดูได้ทุกแถวพร้อมที่มา", "ตรวจในเบราว์เซอร์ทั้งจอปกติและจอมือถือ · ปริมาณของรายงานบริษัทไม่แสดง เพราะยังไม่ยืนยันสิทธิ์เผยแพร่"],
        ["ผู้ช่วยตอบคำถาม (RAG)", "เปิดใช้ที่ /ask.html ตอบจากชุดความรู้ 41,906 ค่า และบันทึกอธิบาย 10 เรื่อง", "ทดสอบกับคำถามจริงบนระบบที่เปิดใช้ · ความเร็วขึ้นกับผู้ให้บริการโมเดล 3–17 วินาที · ยังไม่มีการทดสอบกับผู้ใช้ภายนอกทีม"],
        ["ผล LCA ของไบโอดีเซล", "แสดงบนหน้ากรณีศึกษา B100 และถามผ่านผู้ช่วยได้", "เป็นผลที่บทความรายงาน (ตาราง 5–6) ไม่ใช่ผลที่ทีมคำนวณเอง"],
        ["กราฟ Neo4j และ Qdrant", "ยังเป็นต้นแบบในเครื่องตามหัวข้อ 6.7", "ไม่ได้เปิดใช้บนเว็บ"],
    ], [1900, 3700, 3760]),
    body("วิธีทำงานของผู้ช่วยตอบคำถาม: (1) โมเดลภาษาแปลคำถามเป็นแผนการค้น (2) โปรแกรมคำนวณตัวเลขจากชุดข้อมูลโดยตรง (3) โมเดลภาษาเรียบเรียงคำตอบเป็นภาษาไทย (4) ระบบตรวจว่าตัวเลขและหน่วยทุกตัวในคำตอบตรงกับผลค้น หากไม่ตรงจะทิ้งคำตอบนั้นและแสดงรายการข้อมูลแทน ตัวเลขจึงไม่ได้มาจากการคาดเดาของโมเดล"),
    body("ข้อแตกต่างของสามแบบที่ทีมทดลอง:"),
    table(["แบบ", "เหมาะกับคำถามแบบใด", "ตัวอย่าง", "ข้อจำกัด"], [
        ["Graph (Neo4j)", "ความเชื่อมโยงหลายทอดระหว่างกระบวนการ รายการ และแหล่ง", "FAME มีสิ่งเข้าอะไรบ้าง และแต่ละรายการมาจากตารางใด", "ต้องออกแบบโหนดและความสัมพันธ์ก่อน และยังมีข้อมูลเพียง 16 รายการ"],
        ["Semantic Search (Qdrant)", "หาเอกสารที่ความหมายใกล้กับคำถาม แม้ใช้คำต่างกัน", "คำถามเรื่องการสตาร์ตเย็นของรถ E10", "ได้เอกสารที่เกี่ยวข้อง ไม่ได้คำนวณหรือรวมตัวเลข"],
        ["RAG", "ถามเป็นภาษาพูดแล้วได้คำตอบพร้อมตัวเลขและที่มา", "ปี 2567 ไทยใช้น้ำมันดีเซลหมุนเร็วเท่าไร", "ต้องมีการตรวจตัวเลขกำกับ และขึ้นกับบริการโมเดลภายนอก"],
    ], [1800, 2700, 2600, 2260]),
    body("ผลตรวจอัตโนมัติล่าสุด: ชุดทดสอบ 315 รายการผ่านทั้งหมด ยกเว้น 1 ชุดที่รันไม่ได้บนเครื่องที่ไม่ได้ติดตั้งไลบรารี fastembed และ 10 รายการที่ข้ามเพราะต้องใช้บริการภายนอก"),
])

CH7 = "".join([
    h1("7. Evidence"),
    body("บทนี้รวบรวมลิงก์ผลงานและหลักฐานที่เปิดตรวจได้ พร้อมสัดส่วนการมีส่วนร่วมของสมาชิก"),
    h2("7.1 ลิงก์ผลงาน"),
    table(["ผลงาน", "ที่อยู่", "หมายเหตุ"], [
        ["เว็บไซต์", "https://tamsoodbase.vercel.app", "เปิดดูข้อมูลและกด \"ดูที่มา\" ได้โดยไม่ต้องเข้าสู่ระบบ"],
        ["ผู้ช่วยตอบคำถาม", "https://tamsoodbase.vercel.app/ask.html", "ต้องยินยอมให้ส่งคำถามไปยังบริการโมเดลภาษาก่อนใช้"],
        ["กรณีศึกษา B100", "https://tamsoodbase.vercel.app/#case-study", "ผล LCA ตามที่งานวิจัยรายงาน และโมเดลของทีม"],
        ["Repository", "https://github.com/Neroadawat/TamsoodBase", "โค้ด DDL ชุดทดสอบ และเอกสาร"],
        ["สไลด์นำเสนอ", "S2-G05_M4_Slides.pdf", "10 หน้า ตามลำดับการนำเสนอ 8 ขั้น"],
        ["โปสเตอร์", "S2-G05_M4_Poster_A4.pdf", "A4 แนวตั้ง 1 หน้า"],
    ], [2000, 4100, 3260]),
    h2("7.2 หลักฐานใน repository"),
    table(["หลักฐาน", "ตำแหน่ง", "ใช้ยืนยันอะไร"], [
        ["ทะเบียนแหล่งข้อมูล", "docs/source-registry.csv", "22 แหล่ง พร้อมลิงก์ ชนิดไฟล์ และสถานะสิทธิ์"],
        ["ไฟล์ DDL", "sql/mysql/*.sql", "ตาราง คีย์ และข้อบังคับของทุก schema"],
        ["ชุดทดสอบ", "tests/", "315 รายการ ครอบคลุม pipeline ฐานข้อมูล เว็บ และผู้ช่วยตอบคำถาม"],
        ["ผลตรวจแต่ละรอบ", "evidence/", "ผลตรวจที่บันทึกพร้อมวันเวลาและขอบเขต"],
        ["บันทึกสถานะโครงการ", "PROJECT_STATE.md", "ลำดับการเปลี่ยนแปลงและข้อค้างตามวันที่"],
        ["เอกสารเตรียมนำเสนอ", "docs/submission/W15_PREP_TH.md", "ลำดับเดโม 8 ขั้นและคำตอบสำหรับคำถามตัวอย่าง"],
    ], [2300, 3000, 4060]),
    h2("7.3 Team Contribution"),
    body("สัดส่วนด้านล่างต้องเป็นค่าที่สมาชิกทุกคนตกลงร่วมกัน และแต่ละคนต้องชี้หลักฐานของงานตนเองได้ในวันนำเสนอ"),
    table(["สมาชิก", "บทบาท", "งานที่รับผิดชอบและหลักฐาน", "สัดส่วน (%)"], [
        ["ตฤณเดช พิตติรวิภาส / 6710742088", "PM/BA", "[ทีมกรอกตามจริง]", "[ทีมกรอก]"],
        ["เอดาวัต เอื้ออารยมนตรี / 6710742294", "Schema Lead", "[ทีมกรอกตามจริง]", "[ทีมกรอก]"],
        ["สิริเดช บุราคร / 6710742260", "Data Lead", "[ทีมกรอกตามจริง]", "[ทีมกรอก]"],
        ["พีรภัทร แสงศรี / 6610742501", "SQL Lead", "[ทีมกรอกตามจริง]", "[ทีมกรอก]"],
        ["ณวตา พุฒพินิจ / 6710742468", "QA Lead", "[ทีมกรอกตามจริง]", "[ทีมกรอก]"],
    ], [3000, 1400, 3560, 1400]),
    h2("7.4 การใช้ AI และการตรวจสอบ"),
    body("ทีมใช้ผู้ช่วย AI ในการเขียนสคริปต์ดึงข้อมูล ไฟล์ DDL ชุดทดสอบ หน้าเว็บ และผู้ช่วยตอบคำถาม รวมถึงการร่างเอกสารฉบับนี้ การตรวจสอบทำสามทาง คือ (1) ชุดทดสอบอัตโนมัติที่ต้องผ่านก่อนเผยแพร่ (2) การเทียบค่ากับไฟล์ต้นทางด้วยรหัส SHA-256 และเลขบรรทัด (3) การให้โปรแกรมคำนวณตัวเลขแทนโมเดลภาษา และปฏิเสธคำตอบที่ตัวเลขหรือหน่วยไม่ตรงกับข้อมูล สมาชิกแต่ละคนรับผิดชอบทบทวนส่วนของตนเองและต้องอธิบายได้ด้วยตนเอง"),
])

CH8 = "".join([
    h1("8. Appendix · Meeting Memo"),
    body("บันทึกการประชุมทุกฉบับแนบต่อจากหน้านี้ตามลำดับ Milestone"),
    table(["ครั้งที่", "Milestone", "วันที่ประชุม", "ผู้จดบันทึก", "สถานะ"], [
        ["1", "M1 UNDERSTAND", "[ทีมกรอก]", "[ทีมกรอก]", "[ทีมตรวจว่าแนบแล้ว]"],
        ["2", "M2 DESIGN", "3 พฤศจิกายน 2569", "ณวตา พุฒพินิจ", "แนบท้ายเล่ม"],
        ["3", "M3 BUILD", "[ทีมกรอก]", "[ทีมกรอก]", "มีเฉพาะร่างเตรียมประชุม ต้องประชุมจริงและบันทึกก่อนแนบ"],
        ["4", "M4 DEFEND", "[ทีมกรอก]", "[ทีมกรอก]", "ยังไม่มี"],
    ], [1000, 2000, 2100, 2000, 2260]),
])

TOC_ENTRIES = [
    ("Front", "ปก · Revision History · สารบัญ", "front"),
    ("1", "Introduction", "1. Introduction"), ("1.1", "Purpose", "1.1 Purpose"), ("1.2", "Scope", "1.2 Scope"),
    ("1.3", "Definitions", "1.3 Definitions"), ("1.4", "References (SRC-xx)", "1.4 References"),
    ("2", "Overall Description", "2. Overall Description"), ("2.1", "Product Perspective", "2.1 Product Perspective"),
    ("2.2", "Source Analysis", "2.2 Source Analysis"), ("2.3", "Users & Stakeholders", "2.3 Users"),
    ("2.4", "Constraints", "2.4 Constraints"), ("2.5", "Assumptions", "2.5 Assumptions"),
    ("3", "Requirements", "3. Requirements"), ("3.1", "Data Requirements (DR-xx)", "3.1 Data Requirements"),
    ("3.2", "Business Rules (BR-xx)", "3.2 Business Rules"), ("3.3", "Functional Requirements (FR-xx)", "3.3 Functional Requirements"),
    ("3.4", "Non-functional Requirements", "3.4 Non-functional"), ("3.5", "Use Cases", "3.5 Use Cases"),
    ("4", "Database Design", "4. Database Design"), ("4.1", "ERD + Cardinality", "4.1 ERD + Cardinality"),
    ("4.2", "Relational Schema (PK, FK)", "4.2 Relational Schema"), ("4.3", "Data Dictionary", "4.3 Data Dictionary"),
    ("4.4", "Source-to-DB Mapping", "4.4 Source-to-DB Mapping"),
    ("5", "Implementation", "5. Implementation"), ("5.1", "Extraction Pipeline", "5.1 Extraction Pipeline"),
    ("5.2", "SQL", "5.2 SQL"), ("5.3", "Validation", "5.3 Validation"), ("5.4", "Provenance", "5.4 Provenance"),
    ("6", "Verification", "6 Verification"), ("6.1", "Traceability", "6.1 Traceability"),
    ("6.2", "Thailand Relevance Check", "6.2 Thailand Relevance"), ("6.3", "Unit Consistency / Validated-only Counts", "6.3 Unit Consistency"),
    ("6.4", "SRC-xx Coverage Check", "6.4 SRC-xx Coverage"), ("6.5", "Serving Layer: Graph + Semantic Search (สรุป)", "6.5 Serving Layer"),
    ("6.6", "Acceptance and Evidence Rules", "6.6 Acceptance"), ("6.7", "Serving Layer: รายละเอียด Graph + Semantic Search", "6.7 Serving Layer"),
    ("6.8", "สถานะ Serving Layer ล่าสุด", "6.8 สถานะ Serving Layer"),
    ("7", "Evidence", "7. Evidence"), ("7.1", "ลิงก์ผลงาน", "7.1 ลิงก์ผลงาน"), ("7.2", "หลักฐานใน repository", "7.2 หลักฐานใน repository"),
    ("7.3", "Team Contribution", "7.3 Team Contribution"), ("7.4", "การใช้ AI และการตรวจสอบ", "7.4 การใช้ AI"),
    ("8", "Appendix · Meeting Memo", "8. Appendix"),
]

# ──────────────────────────────────────────────────────────────── assembly

source = zipfile.ZipFile(SRC)
xml = source.read("word/document.xml").decode("utf-8")
PARA = re.compile(r"<w:p[ >](?:(?!<w:p[ >]).)*?</w:p>", flags=re.S)


def find_paragraph(prefix, occurrence=0):
    hits = [m for m in PARA.finditer(xml) if text_of(m.group(0)).strip().startswith(prefix)]
    if len(hits) <= occurrence:
        raise SystemExit(f"paragraph not found: {prefix}")
    return hits[occurrence]


def replace_paragraph_text(prefix, new_text):
    """Keep the paragraph's first run formatting, replace all its text."""
    global xml
    match = find_paragraph(prefix)
    paragraph = match.group(0)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", paragraph, flags=re.S)
    run_pr = re.search(r"<w:r[ >](?:(?!</w:r>).)*?(<w:rPr>.*?</w:rPr>)", paragraph, flags=re.S).group(1)
    run_pr = run_pr.replace("<w:cs/>", "")
    opening = re.match(r"<w:p[^>]*>", paragraph).group(0)
    rebuilt = f'{opening}{ppr.group(0) if ppr else ""}<w:r>{run_pr}<w:t xml:space="preserve">{esc(new_text)}</w:t></w:r></w:p>'
    xml = xml[:match.start()] + rebuilt + xml[match.end():]


# cover and table-of-contents title
replace_paragraph_text("CN230 Database Systems Final Project", "CN230 Database Systems Final Project — M4 DEFEND")
replace_paragraph_text("สารบัญ (Table of Contents)", "สารบัญ (Table of Contents) – M4")

tables = list(re.finditer(r"<w:tbl>.*?</w:tbl>", xml, flags=re.S))

# revision history: add rows in the table's own format
revision = next(t for t in tables if text_of(t.group(0)).startswith("Rev"))
rows = re.findall(r"<w:tr[ >].*?</w:tr>", revision.group(0), flags=re.S)
new_rows = clone_row(rows[-1], ["0.3", "9 พฤศจิกายน 2569", "-", "เพิ่มบทที่ 4 Database Design และบทที่ 6 Verification รวมหัวข้อ Serving Layer (ส่ง M3)"]) \
    + clone_row(rows[-1], ["0.4", "13 พฤศจิกายน 2569", "-", "ฉบับ M4: เพิ่มภาพ ERD ในบทที่ 4, บทที่ 5 Implementation, หัวข้อ 6.8, บทที่ 7 Evidence และบทที่ 8 Appendix; ปรับสารบัญให้ครบทั้งเล่ม"])
revised = revision.group(0).replace("</w:tbl>", new_rows + "</w:tbl>")
xml = xml[:revision.start()] + revised + xml[revision.end():]

# table of contents: rebuild every data row from the existing row formats
tables = list(re.finditer(r"<w:tbl>.*?</w:tbl>", xml, flags=re.S))
toc = next(t for t in tables if text_of(t.group(0)).startswith("ส่วนหัวข้อหน้า"))
rows = re.findall(r"<w:tr[ >].*?</w:tr>", toc.group(0), flags=re.S)
chapter_row = next(r for r in rows if text_of(r).startswith("1Introduction"))
section_row = next(r for r in rows if text_of(r).startswith("1.1Purpose"))
front_row = next(r for r in rows if text_of(r).startswith("Front"))
toc_rows = ""
for number, title, key in TOC_ENTRIES:
    template = front_row if number == "Front" else chapter_row if "." not in number else section_row
    toc_rows += clone_row(template, [number, title, str(TOC_PAGES.get(key, ""))])
header_end = toc.group(0).index(rows[0]) + len(rows[0])
rebuilt_toc = toc.group(0)[:header_end] + toc_rows + "</w:tbl>"
xml = xml[:toc.start()] + rebuilt_toc + xml[toc.end():]

# chapter 4: figures under the empty "4.1 ERD + Cardinality" heading
anchor = find_paragraph("4.1 ERD + Cardinality")
xml = xml[:anchor.end()] + CH4_ERD + xml[anchor.end():]

# chapter 5 goes before chapter 6
anchor = find_paragraph("6 Verification")
xml = xml[:anchor.start()] + CH5 + xml[anchor.start():]

# 6.8, chapter 7 and 8 at the end of the body
end = xml.rindex("<w:sectPr")
xml = xml[:end] + CH6_STATUS + CH7 + CH8 + xml[end:]

for namespace, uri in (("wp", "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"),
                       ("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")):
    if f"xmlns:{namespace}=" not in xml[:6000]:
        xml = xml.replace("<w:document ", f'<w:document xmlns:{namespace}="{uri}" ', 1)

rels = source.read("word/_rels/document.xml.rels").decode("utf-8")
rels = rels.replace("</Relationships>", "".join(
    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
    f'Target="media/m4-{name}"/>' for rid, name in IMAGES) + "</Relationships>")
types = source.read("[Content_Types].xml").decode("utf-8")
if 'Extension="png"' not in types:
    types = types.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as out:
    for item in source.infolist():
        if item.filename.endswith("/"):
            continue
        data = source.read(item.filename)
        if item.filename == "word/document.xml":
            data = xml.encode("utf-8")
        elif item.filename == "word/_rels/document.xml.rels":
            data = rels.encode("utf-8")
        elif item.filename == "[Content_Types].xml":
            data = types.encode("utf-8")
        out.writestr(item, data)
    for rid, name in IMAGES:
        out.write(f"{DIAGRAMS}/{name}", f"word/media/m4-{name}")
print(json.dumps({"out": OUT, "images": len(IMAGES), "toc_rows": len(TOC_ENTRIES), "toc_keys": [k for _, _, k in TOC_ENTRIES]}, ensure_ascii=False)[:300])
