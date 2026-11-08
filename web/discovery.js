/* Discovery contracts: shareable filters, lossless payload hydration and contextual comparison. */
(function(root){
 const TABLES=['13.5','13.6','13.7','13.8','13.10'];
 function route(value){const [view,query='']=String(value||'catalog').replace(/^#/,'').split('?');const p=new URLSearchParams(query);return {view,table:TABLES.includes(p.get('table'))?p.get('table'):'13.6',year:/^202[2-5]$/.test(p.get('year')||'')?p.get('year'):'',q:(p.get('q')||'').replace(/[\u0000-\u001f]/g,'').slice(0,160)};}
 function hash(filters){const p=new URLSearchParams();p.set('table',TABLES.includes(filters.table)?filters.table:'13.6');if(/^202[2-5]$/.test(filters.year))p.set('year',filters.year);if(filters.q)p.set('q',filters.q.slice(0,160));return '#nso?'+p;}
 function hydrate(data){if(data.transport_profile!=='NSO_DEDUP_V1')return data;if(!Array.isArray(data.contexts)||!Array.isArray(data.rows))throw Error('Invalid statistics payload');return {...data,rows:data.rows.map(row=>{if(!Number.isInteger(row._context)||!data.contexts[row._context])throw Error('Missing source context');const {_context,...fields}=row;return {...data.contexts[_context],...fields};})};}
 function compare(a,b){const fields=[['table_id','ตาราง'],['unit','หน่วย'],['measure','ประเภทค่า'],['geography','พื้นที่'],['reference_year','ปีข้อมูล'],['originating_agency','หน่วยงานต้นทาง']];const checks=fields.map(([key,label])=>({key,label,left:a[key]??'',right:b[key]??'',same:a[key]!=null&&b[key]!=null&&a[key]!==''&&String(a[key])===String(b[key])}));return {checks,contextAligned:checks.every(c=>c.same),calculationAllowed:false};}
 const api={route,hash,hydrate,compare};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.TamsoodDiscovery=api;
 const doc=root.document;if(!doc?.querySelector)return;
 const filterPanel=doc.querySelector('.nso-filter-panel');
 if(filterPanel&&root.matchMedia){const mobile=root.matchMedia('(max-width: 760px)');filterPanel.open=!mobile.matches;mobile.addEventListener?.('change',()=>{filterPanel.open=!mobile.matches;});}
 const selected=new Map();let current=[];
 function node(tag,text,cls){const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
 function renderComparison(){
  const box=doc.querySelector('#nso-compare-result'),count=doc.querySelector('#nso-compare-count');if(!box||!count)return;
  count.textContent=selected.size+' / 2 รายการ';box.replaceChildren();const rows=[...selected.values()];
  rows.forEach(row=>{const p=node('p',row.label+' · '+row.reference_year+' · '+row.raw_value+' '+row.unit);const remove=node('button','นำออก');remove.type='button';remove.addEventListener('click',()=>{selected.delete(row.observation_id);renderComparison();refreshChecks();});p.append(remove);box.append(p);});
  if(rows.length!==2){box.append(node('p','เลือกได้ 2 รายการจากตารางด้านล่างเพื่อดูหน่วย ปี และขอบเขตเทียบกัน ไม่บวกหรือหารให้อัตโนมัติ','muted'));return;}
  doc.querySelector('.nso-comparison-workspace').open=true;
  const result=compare(...rows),heading=node('p',result.contextAligned?'บริบทหลักตรงกัน · ยังต้องอ่านนิยามรายการและเชิงอรรถก่อนใช้':'มีบริบทต่างกันหรือยังไม่ระบุ · อ่านแยกกันก่อนนำไปใช้','comparison-verdict');box.append(heading);
  const table=node('table'),head=node('tr');['ตรวจบริบท','รายการแรก','รายการที่สอง','ผลตรวจ'].forEach(t=>head.append(node('th',t)));const thead=node('thead');thead.append(head);table.append(thead);const body=node('tbody');result.checks.forEach(c=>{const tr=node('tr');[c.label,c.left||'ไม่ระบุ',c.right||'ไม่ระบุ',c.same?'ตรงกัน':'ต่างกัน / ไม่ครบ'].forEach(t=>tr.append(node('td',String(t))));body.append(tr);});table.append(body);const wrap=node('div',undefined,'table-wrap');wrap.tabIndex=0;wrap.append(table);box.append(wrap,node('p','นี่เป็นการตรวจบริบทสถิติ ไม่ใช่การรับรองว่าเทียบผลกระทบ LCI ได้ และไม่ใช้แทนการตรวจเชิงอรรถ','muted'));
 }
 function refreshChecks(){doc.querySelectorAll('[data-compare-id]').forEach(input=>{input.checked=selected.has(input.dataset.compareId);input.disabled=selected.size===2&&!input.checked;});}
 api.renderNso=(rows)=>{
  current=rows;const filters={table:doc.querySelector('#nso-table').value,year:doc.querySelector('#nso-year').value,q:doc.querySelector('#nso-search').value.trim()};
  if(doc.body.dataset.activeView==='nso')root.history.replaceState(root.history.state,'',hash(filters));
  const active=doc.querySelector('#nso-active-filters');if(active)active.textContent='ตาราง '+filters.table+' · '+(filters.year||'ทุกปี')+' · '+(filters.q||'ทุกรายการ');
  doc.querySelectorAll('#nso-rows tr').forEach((tr,index)=>{const row=rows[index];if(!row)return;const label=node('label',undefined,'compare-select');const input=node('input');input.type='checkbox';input.dataset.compareId=row.observation_id;input.setAttribute('aria-label','เทียบ '+row.label+' '+row.measure+' '+row.reference_year);input.addEventListener('change',()=>{if(input.checked&&selected.size<2)selected.set(row.observation_id,row);else selected.delete(row.observation_id);renderComparison();refreshChecks();});label.append(input,node('span','เลือกเทียบ'));tr.cells[0].append(label);});refreshChecks();renderComparison();
 };
 doc.querySelector('#nso-clear-compare')?.addEventListener('click',()=>{selected.clear();refreshChecks();renderComparison();});
 doc.querySelector('#nso-copy-link')?.addEventListener('click',async event=>{try{await root.navigator.clipboard.writeText(root.location.href);event.target.textContent='คัดลอกลิงก์แล้ว';}catch{event.target.textContent='คัดลอกจากแถบที่อยู่ได้เลย';}});
})(typeof window==='undefined'?globalThis:window);
