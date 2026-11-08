"""Create a review bundle of docs/DDL/evidence and diagrams, never raw data.

ER sources are parsed from the four current MySQL DDL files, not a proposed LCI
template. Pillow is required only for rendering PNGs, not for SQL parsing.
"""
import hashlib
import html
import json
import re
import textwrap
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={'corporate':'sql/mysql/reusable-schema.sql','dmf':'sql/mysql/full-schema.sql',
         'supplemental':'sql/mysql/supplemental-schema.sql','eppo':'sql/mysql/eppo-schema.sql'}


def split_definitions(body):
    depth=0;start=0;quote=None;parts=[]
    for i,c in enumerate(body):
        if quote:
            if c==quote:quote=None
        elif c in "'\"":quote=c
        elif c=='(':depth+=1
        elif c==')':depth-=1
        elif c==',' and depth==0:
            parts.append(body[start:i].strip());start=i+1
    return parts+[body[start:].strip()]


def parse_schema(sql):
    tables={};links=[]
    for name,body in re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*?)\) ENGINE=InnoDB;',sql,re.S):
        columns=[];primary=set();unique=[];foreign=[]
        for part in split_definitions(body):
            fk=re.match(r'FOREIGN KEY\(([^)]+)\) REFERENCES (\w+)\(([^)]+)\)',part)
            pk=re.match(r'PRIMARY KEY\(([^)]+)\)',part)
            uq=re.match(r'UNIQUE\(([^)]+)\)',part)
            if fk:
                foreign.append((tuple(x.strip() for x in fk[1].split(',')),fk[2],tuple(x.strip() for x in fk[3].split(','))))
            elif pk:primary.update(x.strip() for x in pk[1].split(','))
            elif uq:unique.append(set(x.strip() for x in uq[1].split(',')))
            elif not part.startswith(('CHECK','INDEX','CONSTRAINT')):
                col=re.match(r'(\w+)\s+(\w+(?:\([^)]*\))?)',part)
                if not col:raise ValueError('Unparsed column: '+part)
                columns.append({'name':col[1],'type':col[2],'required':'NOT NULL' in part or 'PRIMARY KEY' in part})
                if 'PRIMARY KEY' in part:primary.add(col[1])
        if not primary:raise ValueError('Missing primary key: '+name)
        tables[name]={'columns':columns,'primary':primary,'unique':unique,'foreign':foreign}
    if not tables:raise ValueError('No supported tables in schema')
    for child,table in tables.items():
        for local,parent,remote in table['foreign']:
            if parent not in tables:raise ValueError('Missing FK target')
            if not set(local)<={c['name'] for c in table['columns']} or not set(remote)<={c['name'] for c in tables[parent]['columns']}:raise ValueError('Missing FK column')
            required=all(c['required'] or c['name'] in table['primary'] for c in table['columns'] if c['name'] in local)
            single=any(key and key<=set(local) for key in [table['primary'],*table['unique']])
            links.append({'parent':parent,'child':child,'local':local,'remote':remote,'parent_end':'||' if required else 'o|','child_end':'o|' if single else 'o{'})
    return tables,links


def mermaid(tables,links):
    lines=['erDiagram']
    for link in links:
        lines.append(f"    {link['parent']} {link['parent_end']}--{link['child_end']} {link['child']} : { '_'.join(link['local']) }")
    for name,table in tables.items():
        fks={key for local,_,_ in table['foreign'] for key in local}
        lines.append('    '+name+' {')
        for col in table['columns']:
            flags=','.join(flag for flag,keys in [('PK',table['primary']),('FK',fks)] if col['name'] in keys)
            # Preserve exact SQL type separately in schema inventory; Mermaid types
            # cannot contain the DECIMAL comma in all supported renderers.
            datatype=re.sub(r'\(.*','',col['type']).lower()
            lines.append(f"        {datatype} {col['name']}"+(' '+flags if flags else ''))
        lines.append('    }')
    return '\n'.join(lines)+'\n'


class Canvas:
    def __init__(self,width,height):
        from PIL import Image,ImageDraw,ImageFont
        self.image=Image.new('RGB',(width,height),'#f7f9f6');self.draw=ImageDraw.Draw(self.image)
        font=Path('C:/Windows/Fonts/consola.ttf');self.font=ImageFont.truetype(str(font),15)
        self.titlefont=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#f7f9f6"/>']
    def text(self,x,y,value,title=False,color='#244737'):
        self.draw.text((x,y),value,font=self.titlefont if title else self.font,fill=color)
        self.svg.append(f'<text x="{x}" y="{y+ (25 if title else 16)}" fill="{color}" font-family="Consolas,monospace" font-size="{25 if title else 15}">{html.escape(value)}</text>')
    def box(self,x,y,w,h):
        self.draw.rounded_rectangle((x,y,x+w,y+h),radius=9,fill='white',outline='#a8bcae',width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="white" stroke="#a8bcae" stroke-width="2"/>')
    def line(self,x1,y1,x2,y2):
        self.draw.line((x1,y1,x2,y2),fill='#709a83',width=2)
        self.svg.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#709a83" stroke-width="2" fill="none"/>')
    def save(self,path):
        self.image.save(path.with_suffix('.png'));path.with_suffix('.svg').write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8')


def render_erd(path,title,tables,links):
    positions={};row_y=110;names=list(tables)
    for start in range(0,len(names),3):
        group=names[start:start+3];height=max(86+24*len(tables[n]['columns']) for n in group)
        for column,name in enumerate(group):positions[name]=(35+column*430,row_y,400,86+24*len(tables[name]['columns']))
        row_y+=height+65
    foot=row_y+24;c=Canvas(1320,foot+100+len(links)*25)
    c.text(35,22,title,True);c.text(35,65,'Current MySQL DDL | PK = primary key; FK = foreign key | candidate migration is separate')
    # Exact FK ledger below is authoritative where connector paths overlap.
    for link in links:
        a=positions[link['parent']];b=positions[link['child']]
        if link['parent']!=link['child']:c.line(a[0]+a[2]/2,a[1]+a[3],b[0]+b[2]/2,b[1])
    for name,(x,y,w,h) in positions.items():
        table=tables[name];fks={key for local,_,_ in table['foreign'] for key in local}
        c.box(x,y,w,h);c.text(x+14,y+10,name,True)
        for i,col in enumerate(table['columns']):
            flags=('P' if col['name'] in table['primary'] else '-')+('F' if col['name'] in fks else '-')
            c.text(x+14,y+52+i*24,f"{flags} {col['name']}  {col['type']}")
    c.text(35,foot,'Foreign keys / SQL cardinality (parent -> children)',True)
    for i,link in enumerate(links):
        parent='1' if link['parent_end']=='||' else '0..1';child='0..1' if link['child_end']=='o|' else '0..N'
        c.text(35,foot+45+i*25,f"{link['parent']} ({parent}) -> {link['child']} ({child}): {','.join(link['local'])} => {','.join(link['remote'])}")
    c.save(path)


def render_pipeline(path):
    audit=json.loads((ROOT/'evidence/pipeline-audit.json').read_text(encoding='utf-8'))
    if not audit['passed']:raise ValueError('Pipeline evidence is not passing')
    stages={item['stage']:item['detail'] for item in audit['stages']}
    dmf=stages['dmf_full_replay'];reference=stages['reference_api_and_pdf'];supplement=stages['source_report_replay']
    labels=[('1. SOURCE REGISTRY',['URL / owner / terms / accessed_at','Candidate sources are not accepted records']),
            ('2. ACQUIRE + RAW EVIDENCE',['Saved source bytes + SHA256 + manifest','API/CSV first; PDF table/page preserved']),
            ('3. PARSE / STAGING',['Source fields retained + raw decimal strings','Extraction batch and source locator retained']),
            ('4. MAP + VALIDATE',['Explicit mapping; typed + payload checks','Unit / time / boundary / duplicate / trace checks']),
            ('5. DISTINCT DATA PRODUCTS',[f"DMF: {dmf['pending_after_deduplication']} deduplicated PENDING; reject {dmf['table_counts']['rejected']}",f"Corporate: {reference['accepted_reference']} reference / {reference['held_context']} HOLD ({reference['source_observations']} source)",f"NSO: {supplement['nso']} staged; EPPO: {supplement['eppo']} staged",f"Product inventory: {supplement['inventory']} source-reported; BHD {supplement['excluded_inventory_cells']} excluded"]),
            ('6. SQL / API / EXPORT / DEMO',['SQLite/JSON serve web; local MySQL verified','Rights and usage profile remain attached'])]
    c=Canvas(1180,1200);c.text(40,24,'TamsoodBase | Source-to-evidence pipeline',True)
    c.text(40,65,'Five layers retain distinct scope, units, acceptance and redistribution status.')
    y=110
    for i,(title,lines) in enumerate(labels):
        height=75+24*len(lines)
        if i:c.line(590,y-25,590,y)
        c.box(75,y,1030,height);c.text(100,y+13,title,True)
        for j,line in enumerate(lines):c.text(100,y+53+24*j,line)
        y+=height+25
    c.text(45,y+5,'Offline replay / FK / roundtrip / negative tests -> evidence/*.json')
    c.text(45,y+30,'No MTEC approval claimed; reference != normalized LCI; no public deployment claimed.')
    c.save(path)


def build():
    out=ROOT/'build/submission-evidence';out.mkdir(parents=True,exist_ok=True)
    diagrams=out/'diagrams';diagrams.mkdir(exist_ok=True);inventory={}
    for name,source in SCHEMAS.items():
        sql=(ROOT/source).read_text(encoding='utf-8');tables,links=parse_schema(sql)
        (diagrams/(name+'-erd.mmd')).write_text(mermaid(tables,links),encoding='utf-8')
        render_erd(diagrams/(name+'-erd'),name.upper()+' | Actual relational schema',tables,links)
        inventory[name]={'source':source,'sha256':hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),
                         'tables':list(tables),'foreign_keys':links,'columns':{n:t['columns'] for n,t in tables.items()},
                         'primary_keys':{n:sorted(t['primary']) for n,t in tables.items()}}
    render_pipeline(diagrams/'pipeline')
    (diagrams/'pipeline.mmd').write_text('''flowchart TD
    Registry[Source registry / rights / scope] --> Raw[Acquire / raw bytes / hash / manifest]
    Raw --> Staging[Parse and preserve source fields]
    Staging --> Mapping[Explicit source-to-model mapping]
    Mapping --> Validation[Schema / unit / time / numerical / duplicate / provenance]
    Validation --> Rejected[Reject / hold with evidence and reason]
    Validation --> Products[Separate reference / statistics / reported inventory]
    Products --> Storage[Relational SQLite / local MySQL / JSON artifacts]
    Storage --> Read[Read-only API / export / demo / trace to source]
    Rejected --> Review[Recorded review; no automatic acceptance]
''',encoding='utf-8')
    selected=[]
    for directory,extensions in [('docs',{'.md','.csv','.json'}),('sql',{'.sql'}),('evidence',{'.json'})]:
        selected.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in extensions and not p.is_symlink() and p.resolve().is_relative_to(ROOT.resolve()) and p.name not in {'submission-evidence.json','final-review-bundles.json'})
    selected.append(ROOT/'README.md')
    archive=out/'tamsood-evidence-review.zip'
    members={str(p.relative_to(ROOT)).replace('\\','/'):p.read_bytes() for p in selected}
    for p in diagrams.iterdir():
        if p.suffix in {'.svg','.png','.mmd'}:members['diagrams/'+p.name]=p.read_bytes()
    members['schema-inventory.json']=(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n').encode()
    start=(ROOT/'docs/submission/README.md').read_text(encoding='utf-8').replace('](../','](docs/')
    for name in ['mapping-validation','status-and-limitations','human-final-checklist']:
        start=start.replace(']('+name+'.md)','](docs/submission/'+name+'.md)')
    members['START_HERE.md']=start.encode('utf-8')
    gallery='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TamsoodBase — หลักฐานเตรียมส่ง</title><style>body{font:16px/1.8 Tahoma,sans-serif;max-width:1100px;margin:auto;padding:28px;background:#f7f9f6;color:#244737}a{color:#245f50}nav{display:flex;flex-wrap:wrap;gap:16px}section{background:white;border:1px solid #cbd9cd;border-radius:12px;padding:22px;margin:24px 0}img{display:block;max-width:100%;height:auto}small{color:#52675a}h1{font-size:28px}</style><h1>ชุดหลักฐาน CN230 × MTEC</h1><p>ชุดเตรียมตรวจและนำเสนอ ยังไม่ใช่ final submission ไม่มี raw data, database หรือ credentials</p><nav><a href="START_HERE.md">ดัชนีงานส่ง</a><a href="docs/submission/human-final-checklist.md">สิ่งที่สมาชิกต้องเติม</a><a href="schema-inventory.json">schema inventory</a><a href="manifest.json">hash manifest</a></nav>'''
    for name,title in [('pipeline','Pipeline'),('corporate-erd','Corporate reference ERD'),('dmf-erd','DMF research ERD'),('supplemental-erd','NSO / product inventory ERD'),('eppo-erd','EPPO ERD')]:
        gallery+=f'<section><h2>{title}</h2><p><a href="diagrams/{name}.svg">เปิด SVG ขยายเต็ม</a> · <a href="diagrams/{name}.mmd">Mermaid source</a></p><a href="diagrams/{name}.png"><img loading="lazy" src="diagrams/{name}.png" alt="{title}"></a></section>'
    members['index.html']=(gallery+'</html>').encode('utf-8')
    # Materialize the same relative paths so the folder also works without unzip.
    for name,body in members.items():
        destination=out/name
        if not destination.resolve().is_relative_to(out.resolve()) or destination.is_symlink():raise ValueError('Unsafe output path')
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body)
    manifest={'scope':'REVIEW_EVIDENCE_NOT_FINAL_SUBMISSION','raw_data_included':False,
              'database_or_credentials_included':False,'source_ddl':inventory,
              'files':[{'path':n,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)} for n,b in sorted(members.items())]}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,body in sorted(members.items()):z.writestr(name,body)
        z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Archive CRC failure')
        for item in manifest['files']:
            if hashlib.sha256(z.read(item['path'])).hexdigest()!=item['sha256']:raise ValueError('Archive hash mismatch')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_bytes(members['index.html'])
    (out/'START_HERE.md').write_bytes(members['START_HERE.md'])
    (out/'schema-inventory.json').write_bytes(members['schema-inventory.json'])
    print(json.dumps({'archive':str(archive),'files':len(members)+1,'erd_tables':{k:len(v['tables']) for k,v in inventory.items()},'verified':True}))
    return archive


if __name__=='__main__':build()
