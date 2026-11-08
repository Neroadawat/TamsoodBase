"""Render an explicit local-review relation map; not a production MySQL diagram."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]


def main():
    im=Image.new('RGB',(1500,1160),'#f7f9f6');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28)
    d.text((35,25),'B100 activity model - local sealed review store',font=title,fill='#1d3c32')
    d.text((35,70),'Solid arrows: selected FK dependencies (child -> parent). See SQL for all composite FKs.',font=font,fill='#50645c')
    nodes={
      'release_manifest':(0,0,'PK release_id'), 'release_seal':(1,0,'PK/FK release_id'),
      'product_system_version':(2,0,'PK model_id; FK release_id'), 'scenario_case':(3,0,'PK scenario_id; FK model_id'),
      'source_observation':(0,1,'PK observation_id; JSON + typed'), 'process_dataset_version':(1,1,'PK version_id; process, count'),
      'dataset_exchange':(2,1,'PK version_id + observation_id'), 'process_instance':(3,1,'PK scenario_id + process_name'),
      'allocation_decision':(0,2,'PK/FK scenario_id; unresolved'), 'required_decision':(1,2,'PK scenario_id + decision_key'),
      'scenario_assumption':(2,2,'PK scenario_id + assumption_key'), 'provider_link_candidate':(3,2,'PK scenario_id + provider + consumer'),
      'calculation_run':(2,3,'PK run_id; input/code hashes'), 'result_exchange':(3,3,'PK run_id + observation_id')}
    def box(name):
        col,row,_=nodes[name];return (35+col*365,140+row*210,380+col*365,255+row*210)
    edges=[('release_seal','release_manifest'),('product_system_version','release_manifest'),('scenario_case','product_system_version'),
      ('dataset_exchange','source_observation'),('dataset_exchange','process_dataset_version'),('process_instance','scenario_case'),
      ('process_instance','process_dataset_version'),('provider_link_candidate','process_instance'),('provider_link_candidate','dataset_exchange'),
      ('calculation_run','scenario_case'),('result_exchange','calculation_run'),('result_exchange','process_instance'),('result_exchange','dataset_exchange')]
    for child,parent in edges:
        a=box(child);b=box(parent);start=((a[0]+a[2])//2,a[1]);end=((b[0]+b[2])//2,b[3])
        if a[1]==b[1]:start=(a[0],(a[1]+a[3])//2);end=(b[2],(b[1]+b[3])//2)
        d.line([start,end],fill='#a4b4aa',width=2);x,y=end;d.ellipse((x-4,y-4,x+4,y+4),fill='#1d3c32')
    for name,(_,_,key) in nodes.items():
        a=box(name);d.rounded_rectangle(a,radius=9,fill='white',outline='#698376',width=2)
        d.text((a[0]+12,a[1]+15),name,font=font,fill='#1d3c32')
        d.text((a[0]+12,a[1]+53),key,font=small,fill='#394e43')
    d.text((35,1005),'allocation_decision, required_decision and scenario_assumption reference scenario_case (omitted arrows).',font=font,fill='#394e43')
    d.text((35,1040),'All tables: append-only. Seal blocks later inserts. Release acceptance checks sources, runs, results and endpoints.',font=font,fill='#394e43')
    d.text((35,1075),'This schema stores activity scenarios; unresolved allocation and missing emissions prevent full LCI / CO2e claims.',font=font,fill='#394e43')
    target=ROOT/'build/submission-evidence/diagrams/activity-model-erd.png';target.parent.mkdir(parents=True,exist_ok=True);im.save(target)
    print(target)


if __name__=='__main__':main()
