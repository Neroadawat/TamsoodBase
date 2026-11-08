"""Publish only model metadata and CC-BY 2020 quantities, never restricted mill rows."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def project(artifact,store):
    cases=[artifact['baseline']]+artifact['alternatives']
    if len(cases)!=6 or store['calculation_runs']!=6 or not store['sealed']:
        raise ValueError('Six sealed reviewed scenarios required')
    components=[
        {'id':'FFB','label':'เพาะปลูกปาล์ม','status':'ยังขาดหน่วยบางรายการและการปล่อยจากแปลง',
         'basis':'ผลปาล์มสด 1,000 kg','source_year':'2020','rights':'CC BY 4.0',
         'source_url':'https://www.mdpi.com/2071-1050/12/22/9415#sustainability-12-09415-t001'},
        {'id':'CPO','label':'สกัดน้ำมันปาล์มดิบ','status':'ข้อมูลโรงงานไทย 6 กรณี · ความเข้ากันยังรอตรวจ',
         'basis':'น้ำมันปาล์มดิบ 1,000 kg','source_year':'2019','rights':'สิทธิแจกจ่ายยังไม่ยืนยัน · ไม่แนบข้อมูลรายแถว',
         'source_url':'https://www.jseejournal.com/media/219/attachment/Life%20cycle%20assessment%20pp.%2065-73.pdf#page=11'},
        {'id':'RBDPO','label':'กลั่นน้ำมันปาล์ม','status':'คำนวณกิจกรรมได้ · ยังไม่แบ่งภาระสิ่งแวดล้อม',
         'basis':'น้ำมันปาล์มกลั่น 1,000 kg','source_year':'2020','rights':'CC BY 4.0',
         'source_url':'https://www.mdpi.com/2071-1050/12/22/9415#sustainability-12-09415-t003'},
        {'id':'FAME','label':'ผลิตไบโอดีเซล B100','status':'มีข้อมูลขั้นผลิต · ยังไม่รวมการใช้เชื้อเพลิง',
         'basis':'เชื้อเพลิง 1,000 MJ','source_year':'2020','rights':'CC BY 4.0',
         'source_url':'https://www.mdpi.com/2071-1050/12/22/9415#sustainability-12-09415-t004'}]
    decisions=[('compatibility','ความเข้ากันของแหล่งข้อมูล','ต่างปีและต่างกลุ่มโรงงาน ยังไม่ยืนยันว่าเป็นห่วงโซ่อุปทานจริงเดียวกัน'),
        ('allocation','การแบ่งภาระให้ผลผลิตร่วม','ยังไม่ทราบว่าค่าในตารางผ่าน allocation แล้วหรือไม่ จึงไม่คูณซ้ำ'),
        ('transport','ขนส่งและจำหน่าย','มีระยะประมาณของขาผลปาล์มบางส่วน แต่รถ เที่ยวกลับ และขาอื่นยังไม่ครบ'),
        ('use','การใช้เชื้อเพลิง','ข้อมูลมลพิษต่อ litre ยังไม่เชื่อมกับฐานพลังงานและเชื้อเพลิงรุ่นนี้'),
        ('waste','ของเสียและน้ำเสีย','น้ำเสียที่บำบัดแล้วไม่ใช่น้ำเสียดิบ และปริมาณก๊าซที่ผลิตไม่ใช่การรั่ว'),
        ('background','ไฟฟ้า สารเคมี และเชื้อเพลิงเบื้องหลัง','ยังขาดรายการปล่อยและข้อมูลผู้ผลิตที่เข้ากันพร้อมสิทธิใช้')]
    result={'scope':'PUBLIC_CASE_STUDY_METADATA_NO_RESTRICTED_INVENTORY','schema_version':1,
        'model_release_id':store['release_id'],'review_date':'2026-11-05',
        'functional_unit':'การใช้เชื้อเพลิง 1,000 MJ','calculated_scope':'กิจกรรมการผลิตเท่านั้น ยังไม่ครบช่วงการใช้และปลายทาง',
        'full_lifecycle_inventory':False,'CO2e_total':None,'private_inventory_included':False,
        'calculation_type':'กรณีทดลองเชื่อมข้อมูลต่างปี ไม่ใช่ผลวัดของห่วงโซ่จริง',
        'selection_note':'โรงสกัด 1 เป็นตัวอย่างเริ่มต้นตามลำดับต้นฉบับ ไม่ใช่ค่าเฉลี่ยประเทศหรือกรณีคาร์บอนต่ำที่สุด',
        'cases':[{'id':c['scenario_id'],'label':'โรงสกัด '+str(i)+' · กรณีทดลอง',
                  'mill':c['selection']['mill'],'baseline':i==1} for i,c in enumerate(cases,1)],
        'components':components,'open_decisions':[{'id':k,'label':label,'reason':reason,'state':'OPEN'} for k,label,reason in decisions],
        'public_activity_kg':{'RBDPO':'24.6','CPO':'27.0600'},
        'activity_source':'Table 3–4 ปี2020 · CC BY 4.0 · เป็นปริมาณกิจกรรม ไม่ใช่ CO₂e',
        'verification':{'result_rows_replayed':store['result_rows_replayed'],
            'meaning':'ทวนสูตรปรับฐานและ foreign key ภายในแล้ว ไม่ใช่การรับรองสมดุลมวล/พลังงานครบระบบหรือการวัดใหม่'},
        'disclosure':'รายละเอียดปริมาณจากโรงสกัดปี2019ยังเก็บในฐานวิจัยภายใน สิทธิแจกจ่ายยังไม่ยืนยัน จึงเผยแพร่เฉพาะบริบทและลิงก์ต้นฉบับ'}
    # Source-specific hard stop: quantities in this projection must come from licensed 2020 data only.
    if result['public_activity_kg']!={k:cases[0]['physical_demand_kg'][k] for k in ('RBDPO','CPO')}:
        raise ValueError('Licensed activity quantities changed')
    result['metadata_snapshot_id']=hashlib.sha256(json.dumps(result,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    return result


def main():
    artifact=json.loads((ROOT/'build/thai-fame-activity-chain/scenarios.json').read_text(encoding='utf8'))
    store=json.loads((ROOT/'evidence/activity-model-store.json').read_text(encoding='utf8'))
    body=(ROOT/'build/thai-fame-activity-chain/scenarios.json').read_bytes()
    if hashlib.sha256(body).hexdigest()!=store['input_manifest']['input_artifact_sha256']:
        raise ValueError('Model store does not match current activity file')
    result=project(artifact,store)
    (ROOT/'web/case-study.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'metadata_snapshot_id':result['metadata_snapshot_id'],'private_inventory_included':False,'cases':6}))


if __name__=='__main__':main()
