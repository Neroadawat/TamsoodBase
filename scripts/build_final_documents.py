"""Render review SRS PDF and editable 10-slide deck from actual documented results.

Outputs are drafts: no signatures, team contributions or submission receipt invented.
Run with bundled Python (reportlab, python-pptx, pypdfium2, Pillow).
"""
import hashlib
import html
import json
import re
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,KeepTogether
from reportlab.pdfgen import canvas
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
import pypdfium2 as pdfium
from PIL import Image as PILImage,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'
GREEN='#1d3c32';GOLD='#9b772c';INK='#203b32'


def plain(s):
    s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1',s)
    return s.replace('**','').replace('`','')


def render(srs_only=False, source_path=None, evidence_name='srs-current-review.json', footer_date=None):
    OUT.mkdir(parents=True,exist_ok=True)
    pdfmetrics.registerFont(TTFont('Thai','C:/Windows/Fonts/tahoma.ttf'))
    pdfmetrics.registerFont(TTFont('ThaiBold','C:/Windows/Fonts/tahomabd.ttf'))
    pdfmetrics.registerFontFamily('Thai',normal='Thai',bold='ThaiBold',italic='Thai',boldItalic='ThaiBold')
    body=ParagraphStyle('Body',fontName='Thai',fontSize=10.3,leading=16,spaceAfter=8,wordWrap='CJK',textColor=colors.HexColor(INK))
    h1=ParagraphStyle('H1',parent=body,fontName='ThaiBold',fontSize=21,leading=30,spaceBefore=12,spaceAfter=14)
    h2=ParagraphStyle('H2',parent=h1,fontSize=16,leading=24,spaceBefore=18)
    h3=ParagraphStyle('H3',parent=h2,fontSize=12,leading=20)
    rowstyle=ParagraphStyle('Row',parent=body,fontSize=9.4,leading=15,leftIndent=10,borderColor=colors.HexColor('#d7e1d9'),borderWidth=.4,borderPadding=7,spaceAfter=10)
    story=[];table_header=None;in_code=False
    source_path=source_path or ROOT/'docs/submission/SRS.md'
    source_bytes=source_path.read_bytes()
    text=source_bytes.decode('utf-8')
    if footer_date is None:
        date_match=re.search(r'Version\s+[^·\n]+·\s*([^\n]+)',text)
        footer_date=date_match.group(1).strip() if date_match else 'Date not specified in source'
    for line in text.splitlines():
        line=line.strip()
        if line.startswith('```'):in_code=not in_code;continue
        if in_code:continue # actual rendered pipeline included below
        if not line:table_header=None;continue
        if line.startswith('|'):
            fields=[plain(x.strip()) for x in line.strip('|').split('|')]
            if all(re.fullmatch(r'[-: ]+',x) for x in fields):continue
            if table_header is None:table_header=fields;continue
            entry='<br/>'.join('<b>'+html.escape(k)+':</b> '+html.escape(v) for k,v in zip(table_header,fields))
            story.append(Paragraph(entry,rowstyle));continue
        level=len(line)-len(line.lstrip('#'))
        if level:
            content=plain(line[level:].strip())
            if level==2 and story:story.append(PageBreak())
            story.append(Paragraph(html.escape(content),h1 if level==1 else h2 if level==2 else h3))
        else:story.append(Paragraph(html.escape(plain(line)),body))
    story.extend([PageBreak(),Paragraph('Appendix: domain DDL diagrams',h1),Paragraph('Four domain schemas. The tamsood_api runtime views and representation tables are described separately in the SRS; these diagrams do not claim to include that fifth schema.',body)])
    for name in ['pipeline','corporate-erd','dmf-erd','supplemental-erd','eppo-erd','activity-model-erd']:
        path=ROOT/'build/submission-evidence/diagrams'/(name+'.png')
        story.append(Paragraph(name,h2))
        with PILImage.open(path) as im:w,h=im.size
        scale=min(480/w,630/h)
        story.append(Image(str(path),width=w*scale,height=h*scale))
        story.append(PageBreak())
    def footer(c,doc):
        c.setFont('Thai',8);c.setFillColor(colors.HexColor('#60746a'))
        c.drawString(42,25,'TamsoodBase · DRAFT FOR TEAM REVIEW · '+footer_date)
        c.drawRightString(553,25,str(doc.page))
    SimpleDocTemplate(str(OUT/'TamsoodBase-SRS-review.pdf'),pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=45,title='TamsoodBase SRS — review draft',author='TamsoodBase AI-assisted draft; team review pending').build(story,onFirstPage=footer,onLaterPages=footer)
    if srs_only:
        target=OUT/'TamsoodBase-SRS-review.pdf';doc=pdfium.PdfDocument(target)
        qa=ROOT/'build'/('srs-current-qa' if evidence_name=='srs-current-review.json' else Path(evidence_name).stem+'-qa');qa.mkdir(parents=True,exist_ok=True);thumbs=[]
        for i,page in enumerate(doc):
            im=page.render(scale=1.2).to_pil().convert('RGB');im.save(qa/f'page-{i+1:02}.png');im.thumbnail((250,355))
            thumb=PILImage.new('RGB',(270,385),'white');thumb.paste(im,(10,20));ImageDraw.Draw(thumb).text((10,3),str(i+1),fill='black');thumbs.append(thumb)
        for start in range(0,len(thumbs),12):
            sheet=PILImage.new('RGB',(1080,1155),'#d9ded9')
            for j,im in enumerate(thumbs[start:start+12]):sheet.paste(im,((j%4)*270,(j//4)*385))
            sheet.save(qa/f'contact-{start//12+1}.jpg')
        if source_path.read_bytes()!=source_bytes:raise RuntimeError('SRS changed during render; do not attest a mixed version')
        result={'artifact':str(target.relative_to(ROOT)),'pages':len(doc),'rendered_pages':len(thumbs),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source_bytes).hexdigest(),'status':'DRAFT_TEAM_REVIEW_PENDING','slides_rebuilt':False,'source_path':str(source_path.relative_to(ROOT))}
        (ROOT/'evidence'/evidence_name).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return

    slides=[
      ('TamsoodBase','ฐานข้อมูลเชื้อเพลิงไทยที่ตรวจย้อนกลับได้',[
       'CN230 × MTEC · Petroleum, Natural Gas & Fuels',
       'ข้อมูล 5 ระดับ · คงหน่วย ขอบเขต สถานะ และหลักฐาน',
       'ฉบับซ้อมนำเสนอ — รอทีมเติมชื่อและรับรองเนื้อหา'], 'อธิบายปัญหาและขอบเขต ไม่อ้างว่าเป็นฐาน LCI ประเทศไทยครบวงจร'),
      ('ปัญหา: ตัวเลขเหมือนกันอาจเทียบกันไม่ได้','ต้องรู้หน่วย เวลา ขอบเขต และต้นทางก่อนใช้',[
       'ยอดใช้พลังงานบริษัท ไม่ใช่ค่าต่อผลิตภัณฑ์โดยอัตโนมัติ',
       'BBL/DAY ของโรงกลั่น ต่างจาก Million Litres รวมประเทศ',
       'ปีเผยแพร่ไม่จำเป็นต้องเป็นปีที่วัดข้อมูล'], 'ชี้ตัวอย่างขอบเขตจริงจาก EPPO และงานวิจัย ไม่สร้างอัตรา yield'),
      ('ข้อมูลแยก 5 ชั้น','ไม่รวมจำนวนแถวทุกชุดเป็น accepted LCI',[
       'DMF: production context · NSO/EPPO: national/company statistics',
       'Corporate: 97 reference / 4 hold จาก 101 selected observations',
       'FAME/H-FAME: 16 source-reported foreground exchanges ต่อ 1000 MJ fuel'], 'ตัวเลขตาม snapshot; corporate rights ยังไม่ cleared สำหรับแจกจ่าย'),
      ('จากต้นฉบับสู่ข้อมูลที่เปิดตรวจได้','Acquisition → Staging → Mapping → Validation',[
       'เก็บ snapshot/hash และตำแหน่งต้นฉบับก่อน transform',
       'เก็บ rejected/hold พร้อมเหตุผล ไม่ลบหลักฐานที่ไม่ผ่าน',
       'Source ID crosswalk 13 source snapshots เชื่อม 5 ชั้น'], 'เปิด source-contract.json และตัวอย่างหนึ่งแถว ไม่อ้าง acquisition อัตโนมัติครบทุกแหล่ง'),
      ('Schema ออกแบบตามความหมายข้อมูล','4 domain schemas + tamsood_api runtime',[
       'Corporate: document/context/metric/review/release',
       'DMF: snapshot/source record/observation/duplicate disposition',
       'Inventory: process/exchange + basis/direction/role; Unit/Flow master ยังไม่ครบทุกชั้น'], 'เปิด ERD SVG ขยายอ่านระหว่าง Q&A;ไม่อ้าง 5NF;normalized candidate แยกจาก production;ไม่อ้าง5NFทุกตาราง'),
      ('ค่าหนึ่งต้องตามกลับต้นทางได้','Identity + Decimal + Source locator',[
       'เปิด Crude glycerine: co-product ไม่ใช่ emission',
       'อ่าน basis/boundary/allocation และปีที่ต้นฉบับไม่ระบุ',
       'ย้อนถึง Table 4 / row 24 / column 3 พร้อม source hash'], 'เปิดหน้า inventory→FAME→OUTPUT→Crude glycerine ไม่คำนวณ allocation เพิ่ม'),
      ('Validation และ Transaction มีผลทดลองจริง','แยกความถูกต้องเชิงโครงสร้างจาก semantics',[
       'MySQL lab: 17 checks รวม rollback, RC/RR และ row lock',
       'SQL error ไม่ได้ย้อนทั้ง transaction เอง ต้องจัดการ rollback',
       'NSO เทียบ 169/273: 141ตรง / 24ปัดเศษ / 4ขัดกัน'], 'อ่าน mysql-transaction-audit.json และ nso-review-ledger.json;104ยังไม่มีdirectcomparison;18derivedตรวจสูตรผ่าน;ไม่ใช่production crash experiment'),
      ('SQL และ Index ต้องตอบ use case','ค้นช่วงเวลา โดยไม่รวมหน่วยผิด',[
       'DMF period lookup: ผล 102 แถวเท่ากันทั้งสองแผน',
       'หลักฐานเดิม median iterator 0.208 ms กับ 12.0 ms เมื่อ IGNORE INDEX',
       'เป็น local warm-cache experiment ไม่ใช่ API SLA'], 'เปิด evidence/sql-performance.json;แผน controlled baseline ไม่ใช่สร้าง/ลบ index สด'),
      ('เว็บและการใช้งานต่อ','เลือกงาน → อ่านบริบท → ค้น → เปิดหลักฐาน',[
       'มีทางลัด inventory / reference / sources และตัวกรองตามระดับ',
       'Vercel → HTTPS proxy → EC2 MySQL; มี S3 backup/restore',
       'Quick Tunnel ยังชั่วคราว; สิทธิ raw ที่ไม่ชัดยังไม่อนุญาตแจก'], 'สาธิต error/retry ตามคู่มือ;ตรวจ release EC2 ก่อนเดโม Vercelเปิดอ่านโดยไม่loginตามเจ้าของ;upstreamเก็บsecretฝั่งserver;QuickTunnelยังชั่วคราว'),
      ('ข้อจำกัดและการส่งมอบ','ระบบตรวจได้ พร้อมให้ทีมทบทวน',[
       'ยังไม่ใช่ full refinery LCI; Flow/Unit master และ source semantics ต้องพัฒนาต่อ',
       'SRS0.4 และสไลด์พร้อมทบทวน;ทีมเติม contribution/memo/consent',
       'Neo4jจริง: 16 inventory records / 39 nodes / 68 relationships'], 'Neo4j5.26.32 local internalnetwork lab;4CypherqueriesตรงSQL ไม่ใช่productiongraph;ไม่แต่งชื่อสมาชิก/ผลซ้อม/การรับรอง')]
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    pdf=canvas.Canvas(str(OUT/'TamsoodBase-final-slides-review.pdf'),pagesize=(960,540))
    def ppt_text(slide,x,y,w,h,text,size,bold=False,color=INK):
        box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame;tf.word_wrap=True
        p=tf.paragraphs[0];p.text=text;p.font.name='Tahoma';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color.lstrip('#'))
    def pdftext(text,x,y,w,size,bold=False,color=INK):
        style=ParagraphStyle('slide',fontName='ThaiBold' if bold else 'Thai',fontSize=size,leading=size*1.6,wordWrap='CJK',textColor=colors.HexColor(color))
        p=Paragraph(html.escape(text),style);_,h=p.wrap(w,450);p.drawOn(pdf,x,y-h)
    for i,(title,subtitle,points,notes) in enumerate(slides,1):
        slide=prs.slides.add_slide(prs.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=RGBColor.from_string('F7F9F6')
        ppt_text(slide,.65,.6,12,1.1,title,30,True,GREEN);ppt_text(slide,.68,1.65,12,.6,subtitle,18,False,GOLD)
        pdf.setFillColor(colors.HexColor('#f7f9f6'));pdf.rect(0,0,960,540,fill=1,stroke=0)
        pdftext(title,47,493,866,29,True,GREEN);pdftext(subtitle,49,420,866,17,False,GOLD)
        for j,point in enumerate(points):
            ppt_text(slide,.8,2.65+j*1.12,11.8,1.05,point,21)
            pdftext(point,58,351-j*81,844,20)
        ppt_text(slide,.68,7,12,.3,f'DRAFT · Team review pending                                      {i}/10',10,False,'60746A')
        pdftext(f'DRAFT · Team review pending    |    {i}/10',49,30,866,9,False,'#60746a')
        slide.notes_slide.notes_text_frame.text=notes+'\nSources: docs/submission/SRS.md; evidence/*.json; docs/final-walkthrough.md'
        pdf.showPage()
    pdf.save();deck=ROOT/'output/presentations';deck.mkdir(parents=True,exist_ok=True);prs.save(str(deck/'TamsoodBase-final-review.pptx'))
    evidence={'draft':True,'team_review_pending':True,'submitted':False,'artifacts':[]}
    qa=ROOT/'build/final-document-qa';qa.mkdir(parents=True,exist_ok=True)
    for name in ['TamsoodBase-SRS-review.pdf','TamsoodBase-final-slides-review.pdf']:
        doc=pdfium.PdfDocument(OUT/name);thumbs=[]
        for i,page in enumerate(doc):
            image=page.render(scale=1.2).to_pil().convert('RGB');image.save(qa/(name+f'-{i+1:02}.png'))
            image.thumbnail((250,355));thumb=PILImage.new('RGB',(270,385),'white');thumb.paste(image,(10,20));ImageDraw.Draw(thumb).text((10,3),str(i+1),fill='black');thumbs.append(thumb)
        cols=4;rows=(len(thumbs)+cols-1)//cols;sheet=PILImage.new('RGB',(cols*270,rows*385),'#d9ded9')
        for i,im in enumerate(thumbs):sheet.paste(im,((i%cols)*270,(i//cols)*385))
        sheet.save(qa/(name+'-contact.jpg'))
        evidence['artifacts'].append({'path':(OUT/name).relative_to(ROOT).as_posix(),'pages':len(doc),'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest(),'rendered_pages':len(thumbs)})
    (ROOT/'evidence/final-document-draft.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--srs-only',action='store_true');args=parser.parse_args();render(args.srs_only)
