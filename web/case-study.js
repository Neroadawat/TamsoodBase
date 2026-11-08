(function(root){
 'use strict';
 const labels={FFB:'ผลปาล์มสด',CPO:'น้ำมันปาล์มดิบ',RBDPO:'น้ำมันปาล์มกลั่น',FAME:'ไบโอดีเซล'};
 function formatActivity(value){if(typeof value!=='string'||value.length>40||!/^\d+(\.\d+)?$/.test(value))throw Error('ปริมาณไม่ถูกต้อง');const n=Number(value);if(!Number.isFinite(n)||n<0)throw Error('ปริมาณไม่ถูกต้อง');return '≈ '+new Intl.NumberFormat('th-TH',{maximumSignificantDigits:3}).format(n)+' kg';}
 function validate(data){
  if(data.scope!=='PUBLIC_CASE_STUDY_METADATA_NO_RESTRICTED_INVENTORY'||data.full_lifecycle_inventory!==false||data.CO2e_total!==null||data.private_inventory_included!==false||data.cases?.length!==6||data.components?.length!==4)throw Error('ชุดข้อมูลกรณีศึกษายังไม่ผ่านเงื่อนไขแสดงผล');
  if(Object.keys(data.public_activity_kg).sort().join(',')!=='CPO,RBDPO'||data.rows||data.observations)throw Error('พบข้อมูลที่ไม่อยู่ในขอบเขตเผยแพร่');
  data.components.forEach(c=>{const u=new URL(c.source_url);if(u.protocol!=='https:'||u.username||u.password)throw Error('ลิงก์ต้นทางไม่ถูกต้อง');});return data;
 }
 const api={formatActivity,validate};
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(!root.document)return;
 const $=s=>document.querySelector(s),make=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
 let data=null,pending=null,selected='FAME';
 function render(){
  if(!data)return;
  const chosen=data.cases.find(c=>c.id===$('#case-choice').value)||data.cases[0];
  $('#case-selected').textContent=chosen.label+' · เลือกบริบทโรงสกัดเท่านั้น ตัวเลข CPO/RBDPO ด้านล่างใช้ฐานปลายทางปี 2020 เดียวกันทุกกรณี จึงยังไม่ใช่การเปรียบเทียบคาร์บอนหรือปริมาณรายโรงงาน · '+data.selection_note;
  $('#case-run').textContent='รุ่นโมเดล '+data.model_release_id.slice(0,12)+' · metadata '+data.metadata_snapshot_id.slice(0,12);
  const flow=$('#case-processes');flow.replaceChildren();
  data.components.forEach(component=>{
   const b=make('button',undefined,'case-process');b.type='button';b.dataset.component=component.id;b.setAttribute('aria-pressed',String(selected===component.id));
   b.append(make('strong',component.label),make('span',component.id),make('small','ยังมีประเด็นรอตรวจ'));
   b.addEventListener('click',()=>{selected=component.id;render();$('#case-processes [aria-pressed="true"]').focus();});flow.append(b);
  });
  const component=data.components.find(c=>c.id===selected),panel=$('#case-component');panel.replaceChildren();
  panel.append(make('h3',component.label+' ('+component.id+')'),make('p',component.status),make('p','ฐานต้นฉบับ: '+component.basis+' · ปีเผยแพร่ '+component.source_year),make('p','สิทธิ: '+component.rights,'muted'));
  const link=make('a','เปิดเว็บไซต์ / ตารางต้นฉบับ ↗','button secondary');link.href=component.source_url;link.target='_blank';link.rel='noopener noreferrer';panel.append(link);
  if(data.public_activity_kg[selected]){
   const value=data.public_activity_kg[selected];const strong=make('strong',formatActivity(value),'case-quantity');strong.title='ค่าคำนวณเต็ม '+value+' kg';
   panel.append(make('p','ปริมาณกิจกรรมต่อเชื้อเพลิง 1,000 MJ'),strong,make('p',data.activity_source,'muted'));
   const quantitySources=make('p',undefined,'muted');quantitySources.append(make('span','หลักฐานตัวเลขปี 2020: '));
   ['RBDPO','FAME'].forEach((id,i)=>{if(i)quantitySources.append(document.createTextNode(' · '));const a=make('a',id==='RBDPO'?'ตารางกลั่นน้ำมันปาล์ม':'ตารางผลิตไบโอดีเซล');a.href=data.components.find(c=>c.id===id).source_url;a.target='_blank';a.rel='noopener noreferrer';quantitySources.append(a);});panel.append(quantitySources);
   const detail=make('details');detail.append(make('summary','ดูค่าคำนวณเต็มและวิธีอ่านผล'),make('p','ค่าเต็ม '+value+' kg · ตัวเลขด้านบนปัดเพื่อไม่สื่อความแม่นเกินข้อมูลต้นทาง · ยังไม่ใช่ภาระที่แบ่งให้ผลิตภัณฑ์แล้ว'));panel.append(detail);
  }else if(selected==='FAME'){
   const original=make('a','ดูรายการเข้า–ออกขั้นผลิตไบโอดีเซล','button secondary');original.href='#inventory';panel.append(original);
  }else panel.append(make('p','ปริมาณของช่วงนี้ที่เชื่อมตามกรณีโรงสกัดยังไม่เผยแพร่ในหน้านี้ โปรดอ่านขอบเขตและลิงก์ต้นฉบับ','case-note'));
  const decisions=$('#case-decisions');decisions.replaceChildren();data.open_decisions.forEach(d=>{const box=make('article',undefined,'case-gap');box.append(make('strong',d.label),make('span','ยังไม่ปิดประเด็น','case-open'),make('p',d.reason));decisions.append(box);});
  $('#case-disclosure').textContent=data.disclosure;$('#case-verification').textContent=data.verification.meaning;
  $('#case-load-status').textContent='โหลดบริบทกรณีศึกษาแล้ว · ผล CO₂e ทั้งระบบยังคำนวณไม่ได้';$('#case-retry').hidden=true;$('#case-download').disabled=false;
 }
 api.load=function(){
  if(data)return Promise.resolve(true);if(pending)return pending;
  $('#case-load-status').textContent='กำลังโหลดกรณีศึกษา…';
  pending=fetch('/case-study.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('โหลดกรณีศึกษาไม่ได้ ('+r.status+')');return r.json();}).then(value=>{
   data=validate(value);const select=$('#case-choice');select.replaceChildren();data.cases.forEach(c=>{const o=make('option',c.label);o.value=c.id;select.append(o);});render();return true;
  }).catch(error=>{data=null;$('#case-load-status').textContent=error.message;$('#case-retry').hidden=false;return false;}).finally(()=>{pending=null;});return pending;
 };
 $('#case-choice').addEventListener('change',render);$('#case-retry').addEventListener('click',api.load);
 $('#case-download').addEventListener('click',()=>{if(!data)return;const blob=new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=make('a');a.href=url;a.download='tamsood-case-metadata-'+data.metadata_snapshot_id.slice(0,12)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 root.TamsoodCaseStudy=api;
})(typeof window==='undefined'?globalThis:window);
