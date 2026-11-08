"""Publish only explicitly licensed, reviewed article facts; never copy raw source files."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=('observation_id','process','reference_amount','reference_unit','reference_flow','flow','raw_value','amount','unit','direction','role','status','pdf_page','table_id','table_data_row','source_url','source_sha256','doi','publication_year','data_period')

def process_profiles(rows):
    profiles={}
    for process in ('FFB','CPO','RBDPO'):
        selected=[r for r in rows if r['process']==process]
        products=[r for r in selected if r['role']=='REFERENCE_PRODUCT']
        if len(products)!=1:raise ValueError('Reference product ambiguous')
        reasons=['ช่วงปีที่วัดไม่ระบุ','ยังไม่มี background processes ที่เชื่อมครบ','ยังไม่ยืนยันการปันส่วนที่ใช้กับปริมาณในตาราง']
        held=sum(r['status']=='HOLD_MISSING_UNIT' for r in selected)
        if held:reasons.insert(0,'Land seeding ไม่ระบุหน่วย จึงพักไว้')
        if process=='CPO' and not any(r['direction']=='INPUT' and r['flow']=='FFB' for r in selected):reasons.insert(0,'ตารางไม่ระบุปริมาณ FFB ที่ป้อนเข้า จึงยังเชื่อมกับการปลูกไม่ได้')
        profiles[process]={'reference_amount':products[0]['amount'],'reference_unit':products[0]['unit'],'reference_product':process,'source_cells_verified':True,'unit_present_rows':len(selected)-held,'held_rows':held,'measurement_period':None,'model_ready':False,'full_lifecycle_inventory':False,'open_issues':reasons,'quality_score':None,
            'boundary':{'included':'รายการสิ่งเข้าและสิ่งออกตามตาราง '+selected[0]['table_id']+' ของกระบวนการ '+process,
                        'excluded_from_imported_model':['การผลิตไฟฟ้าและสารเคมีที่ใช้','การขนส่ง','การใช้เชื้อเพลิงในรถ'],
                        'interpretation':'รายการที่ยังไม่นำเข้า ไม่ได้แปลว่างานวิจัยต้นฉบับไม่มีข้อมูลส่วนนั้น'},
            'quality_dimensions':{'source_verification':'ค่าที่เลือกตรวจตรงต้นฉบับ','measurement_period':'ต้นฉบับไม่ระบุช่วงปีที่วัด','geography':'บริบทการศึกษาในไทย ไม่ใช่ค่าเฉลี่ยประเทศไทย','model_completeness':'ยังขาดการเชื่อมกระบวนการและ background','independent_measurement':'ไม่ได้ตรวจวัดใหม่โดยโครงงาน','redistribution':'CC BY 4.0 พร้อมอ้างอิงผู้เขียน'},
            'usable_for':['อ่านค่าตามตารางและตรวจย้อนต้นฉบับ','ใช้ประกอบการทบทวนและเตรียมแบบจำลอง'],
            'not_ready_for':['รวมผลกระทบตลอดวงจรชีวิต','เปรียบเทียบผลิตภัณฑ์โดยไม่ตรวจฐานและวิธีจัดสรร']}
    return profiles

def public_snapshot(report):
    if report['source']['rights_status']!='ARTICLE_CC_BY_4_0':raise ValueError('Public redistribution not supported by selected source license')
    rows=report['rows']
    if len(rows)!=42 or len({r['observation_id'] for r in rows})!=42:raise ValueError('Unexpected source identities')
    for row in rows:
        if row['doi']!='10.3390/su12229415' or row['source_sha256']!=report['source']['sha256']:raise ValueError('Unreviewed source')
        if row['process'] not in ('FFB','CPO','RBDPO') or row['is_full_lci_dataset'] is not False:raise ValueError('Unsupported scope')
        if (row['unit'] is None)!=(row['status']=='HOLD_MISSING_UNIT'):raise ValueError('Missing unit/status inconsistency')
    if len(report['cross_engine_checks'])!=42 or not all(c['amount_unit_direction_match'] and c['normalized_label_match'] for c in report['cross_engine_checks']):raise ValueError('Source checks incomplete')
    result={'version':1,'scope':'LICENSED_PUBLIC_SOURCE_REPORTED_UPSTREAM_CANDIDATES','licence':'CC BY 4.0','attribution':'Permpool, N.; Ghani, H.U.; Gheewala, S.H. (2020). Sustainability 12(22), 9415. DOI:10.3390/su12229415. Tables1–3; extracted and annotated by TamsoodBase.','publisher_url':'https://www.mdpi.com/2071-1050/12/22/9415','source_pdf_url':report['source']['url'],'source_sha256':report['source']['sha256'],'counts':report['counts'],'process_profiles':process_profiles(rows),'rows':[{k:r[k] for k in FIELDS} for r in rows],'full_lifecycle_inventory':False,'allocation_applied':False,'provider_links_applied':0,'model_ready':False,'raw_document_included':False}
    result['public_snapshot_id']=hashlib.sha256(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result

def main():
    path=ROOT/'build/upstream-inventory/report.json';report=json.loads(path.read_text(encoding='utf8'))
    checked=json.loads((ROOT/'evidence/upstream-inventory-review.json').read_text(encoding='utf8'))
    if report!=checked:raise ValueError('Candidate report differs from reviewed evidence')
    pdf=ROOT/'data/raw/mdpi-9415/pdf-v3/source.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=report['source']['sha256']:raise ValueError('Retained source changed')
    result=public_snapshot(report);target=ROOT/'web/upstream-inventory.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Public CC BY reference snapshot:42rows;1hold;no raw PDF;no corporate data')
if __name__=='__main__':main()
