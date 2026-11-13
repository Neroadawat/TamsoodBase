const $=s=>document.querySelector(s), labels={'production-oil':'น้ำมันดิบ','production-condensate':'คอนเดนเสท','production-natural-gas':'ก๊าซธรรมชาติ'};
const state={page:1,total:0,summary:null,request:0};
const number=n=>Number(n).toLocaleString('en-US');
const flowThai={'RBDPO':'น้ำมันปาล์มกลั่น','CPO':'น้ำมันปาล์มดิบ','FFB':'ผลปาล์มสด','FAME':'ไบโอดีเซลเมทิลเอสเทอร์','Methanol':'เมทานอล','Steam':'ไอน้ำ','Electricity (grid)':'ไฟฟ้าจากโครงข่าย','Phosphoric acid':'กรดฟอสฟอริก','Potassium hydroxide':'โพแทสเซียมไฮดรอกไซด์','Tap water':'น้ำประปา','Cooling water':'น้ำหล่อเย็น','Crude glycerine':'กลีเซอรีนดิบ'};
const flowDisplay=label=>flowThai[label]?flowThai[label]+' ('+label+')':label;

const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;};
const statusLabel={SINGLETON:'ไม่พบซ้ำ',EXACT_REPRESENTATIVE:'ตัวแทนสำเนา',EXCLUDE_EXACT_COPY:'สำเนาที่แยกออก',HOLD_CONFLICT:'พัก: ข้อมูลขัดกัน'};
function badge(status){return el('span',statusLabel[status]||status,'tag '+(status==='HOLD_CONFLICT'?'hold':status==='EXCLUDE_EXACT_COPY'?'copy':''));}
function params(){return new URLSearchParams(new FormData($('#filters')));}
const get=(url,options)=>window.TamsoodAPI.get(url,35000,options);
const apiUrl=path=>window.TamsoodAPI.url(path);
async function load(){const request=++state.request;const p=params();p.set('page',state.page);$('#results').textContent='กำลังค้นหา…';$('#rows').replaceChildren();$('#previous').disabled=true;$('#next').disabled=true;$('#export').removeAttribute('href');try{const data=await get('/api/records?'+p);if(request!==state.request)return;state.total=data.total;$('#rows').replaceChildren();data.rows.forEach(row=>{const tr=el('tr');const name=el('td');name.append(el('strong',row.source_group),el('small',`${row.area} · ${row.block_label||'ไม่ระบุแปลง'}`));const amount=el('td',row.raw_value,'number');amount.append(el('small',`${row.unit_label} · ฐานเวลารอตรวจ`));const action=el('td'),button=el('button','ดูที่มา','evidence-btn');button.addEventListener('click',()=>openDetail(row));action.append(button);const status=el('td');status.append(badge(row.duplicate_status));tr.append(name,el('td',labels[row.package]),el('td',`${row.year_ce}-${String(row.month).padStart(2,'0')}`),amount,status,action);$('#rows').append(tr);});if(!data.rows.length){const tr=el('tr'),td=el('td','ไม่พบข้อมูลตามตัวกรอง ลองล้างตัวกรองหรือเปลี่ยนคำค้น','empty');td.colSpan=6;tr.append(td);$('#rows').append(tr);}$('#results').textContent=`พบ ${number(data.total)} รายการ · แถวที่ไม่ซ้ำและไม่ถูกพัก ทีมรับเป็นสถิติต้นทางแล้ว`;$('#page-label').textContent=`หน้า ${state.page} / ${Math.max(1,Math.ceil(data.total/30))}`;$('#previous').disabled=state.page<=1;$('#next').disabled=state.page*30>=data.total;const exportLink=$('#export');const limited=Number.isInteger(data.export_max_rows)&&data.total>data.export_max_rows;
if(limited){exportLink.removeAttribute('href');exportLink.setAttribute('aria-disabled','true');exportLink.textContent='กรองให้เหลือไม่เกิน '+number(data.export_max_rows)+' รายการเพื่อส่งออก';}
else{exportLink.href=apiUrl('/api/export?'+params());exportLink.removeAttribute('aria-disabled');exportLink.textContent='ดาวน์โหลด CSV';}}
catch(error){if(request!==state.request)return;$('#results').textContent=error.message;$('#rows').replaceChildren();$('#page-label').textContent='';return false;}}
function item(label,value){const box=el('div',undefined,'detail-item');box.append(el('span',label),el('div',value??'ไม่ระบุ'));return box;}
// Publication pages explain context; extraction files preserve the exact source bytes.
function evidenceDestinations(kind,row){
 const links=[];
 if(kind==='nso'&&['13.5','13.6','13.7','13.8','13.10'].includes(row.table_id))links.push(['เว็บไซต์รายงาน สสช.','https://www.nso.go.th/public/e-book/Statistical-Yearbook/SYB-2026_webPage/Page_SYB_TH.html','เลือกบท 13 และตาราง '+row.table_id+' · รายงานเผยแพร่ 2569 ไม่ใช่ปีข้อมูล']);
 if(kind==='eppo'&&['11_13','11_14'].includes(row.dataset_id))links.push(['หน้าเว็บไซต์ชุดข้อมูล EPPO','https://catalog.eppo.go.th/th/dataset/dataset_'+row.dataset_id,'อ่านคำอธิบาย หน่วย และแหล่งที่มาของชุดข้อมูล']);
 if(kind==='dmf'&&['production-oil','production-condensate','production-natural-gas'].includes(row.package))links.push(['หน้าเว็บไซต์ชุดข้อมูล DMF','https://catalog.dmf.go.th/dataset/'+row.package,'อ่าน metadata และข้อจำกัดของฐานเวลา']);
 const raw=row.source_url||row.url;
 try{const u=new URL(raw);if(u.protocol==='https:'&&!u.username&&!u.password)links.push(['ดาวน์โหลดไฟล์ข้อมูล CSV',u.href,'ไฟล์จากเจ้าของข้อมูล · อาจเปิดเป็นข้อความหรือดาวน์โหลด']);}catch{}
 return links;
}
function evidenceNavigation(kind,row){
 const section=el('section',undefined,'evidence-navigation');section.append(el('h3','เปิดต้นทาง'));
 for(const [title,url,note] of evidenceDestinations(kind,row)){
  const a=el('a',undefined,'evidence-destination');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.append(el('strong',title+' ↗'),el('small',note));section.append(a);
 }
 section.append(el('p','ลิงก์เปิดเว็บปัจจุบันของเจ้าของข้อมูล ส่วนค่าด้านล่างอ้างอิง snapshot ที่เก็บไว้ จึงอาจต่างจากไฟล์ที่เจ้าของปรับปรุงภายหลัง','muted'));
 return section;
}
function sourceRowPreview(row){
 const section=el('section',undefined,'source-preview');section.append(el('h3','จุดที่นำค่ามา'),el('p',`ตาราง ${row.table_id} · บรรทัด CSV ${row.source_line} · คอลัมน์ ${row.source_column} · หัวคอลัมน์ ${row.source_header||'ไม่ระบุ'}`));
 const list=el('ol',undefined,'source-cells');
 (row.source_row||[]).forEach((value,index)=>{const selected=index+1===Number(row.source_column),cell=el('li',undefined,selected?'source-cell selected':'source-cell');cell.append(el('small','คอลัมน์ '+(index+1)+(selected?' · ค่าที่เลือก':'')),el('strong',String(value??'')||'(ว่าง)'));list.append(cell);});const details=el('details',undefined,'raw-row-details');details.append(el('summary','ดูแถวต้นฉบับทั้งหมด'),list);section.append(details);return section;
}
async function openDetail(record){$('#detail-content').replaceChildren(el('p','กำลังโหลดหลักฐาน…'));if(!$('#detail').open)$('#detail').showModal();try{const data=await get(`/api/record?package=${encodeURIComponent(record.package)}&line=${record.source_line}`);const content=$('#detail-content');content.replaceChildren(el('h2',data.source_group,'detail-title'));content.append(badge(data.duplicate_status));const grid=el('div',undefined,'detail-grid');grid.append(item('ผลิตภัณฑ์',labels[data.package]),item('ค่าตามต้นฉบับ',data.raw_value),item('ช่วงเวลา',`${data.year_ce}-${String(data.month).padStart(2,'0')}`),item('พื้นที่ / แปลง',`${data.area} / ${data.block_label||'ไม่ระบุ'}`),item('หน่วยตาม metadata',data.unit_label),item('ตำแหน่งต้นฉบับ',`CSV บรรทัด ${data.source_line}`));content.append(grid,el('p',data.unit_status+' · แถวที่ไม่ซ้ำและไม่ถูกพัก ทีมรับเป็นสถิติต้นทางแล้ว (กฎ AR-2)','notice'));if(data.conflict_investigation){const note=data.conflict_investigation;content.append(el('h3','ประเด็นที่ต้องตรวจเพิ่ม'),el('p',`วันผลิตของกลุ่มรวม ${note.sum_days} วัน / ปฏิทิน ${note.calendar_days} วัน`),el('p',note.pattern==='POSSIBLE_SUBPERIOD'?'อาจเป็นข้อมูลแบ่งช่วงภายในเดือน แต่ยังไม่มีวันที่เริ่ม–สิ้นสุดยืนยัน จึงยังพักทั้งกลุ่มและไม่รวมค่าอัตโนมัติ':'จำนวนวันรวมยังอธิบายช่วงเวลาที่ไม่ซ้อนกันไม่ได้ จึงพักทั้งกลุ่มและไม่รวมค่าอัตโนมัติ','notice'));}content.append(evidenceNavigation('dmf',data),el('h3','ร่องรอยข้อมูล'),el('p',`Snapshot ${data.run_id}`,'muted'),el('div',data.csv_sha256,'hash'),el('p',`ดึงข้อมูล ${data.acquired_at} · ใบอนุญาตตาม metadata: ${data.license_label}`,'muted'));content.append(el('h3','แถวต้นฉบับ'),el('pre',JSON.stringify(data.raw_fields,null,2)));if(data.related.length>1){content.append(el('h3','รายการในกลุ่มตัวตนเดียวกัน'));data.related.forEach(row=>{const box=el('div',undefined,'source-card');box.append(el('p',`บรรทัด ${row.source_line} · ค่า ${row.raw_value}`),badge(row.status),el('pre',JSON.stringify(JSON.parse(row.raw_json),null,2)));content.append(box);});}const copy=el('button','คัดลอก metadata อ้างอิง','button primary');copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(JSON.stringify({package:data.package,source_url:data.url,source_line:data.source_line,snapshot:data.run_id,sha256:data.csv_sha256,accessed_at:data.acquired_at,status:'PENDING'},null,2));copy.textContent='คัดลอกแล้ว ✓';}catch{copy.textContent='เบราว์เซอร์ไม่อนุญาตให้คัดลอก';}});content.append(copy);}catch(error){$('#detail-content').replaceChildren(el('p',error.message));}}
function renderOverview(data){state.summary=data;$('#raw-count').textContent=number(data.quality.raw_rows);$('#pending-count').textContent=number(data.report.deduplicated_candidates_pending_review);$('#hold-count').textContent=number(data.report.total_row_dispositions.HOLD_CONFLICT);/* AR-2 (docs/acceptance-ledger.json): unique, source-verified rows minus the 4 held for unit or magnitude doubts. */$('#accepted-count').textContent=number(data.report.deduplicated_candidates_pending_review-4);$('#snapshot').textContent='DMF snapshot '+data.run_id;data.years.forEach(year=>{const opt=el('option',String(year));opt.value=year;$('#year').append(opt);});const quality=el('div',undefined,'quality-grid');[['แยกสำเนาที่เหมือนกันทุกช่อง',data.report.total_row_dispositions.EXCLUDE_EXACT_COPY,'คง raw และแถวตัวแทนไว้ ไม่ลบหลักฐาน'],['ไม่ผ่านรูปแบบ',data.quality.rejected,'แยกเหตุผลตรวจสอบได้ใน rejected log'],['ตัวเลข spot-check',`${data.report.unit_review.numeric_sample_matches} / ${data.report.unit_review.checks}`,'ตัวอย่างเลือกเอง ไม่ใช่อัตราความถูกต้องทั้งชุด'],['บริบทแปลงตรงแบบ exact',`${data.report.unit_review.exact_block_matches} / ${data.report.unit_review.checks}`,'ค่าตรงไม่ได้แปลว่าขอบเขตข้อมูลตรงกันทั้งหมด']].forEach(([title,value,note])=>{const box=el('div',undefined,'quality-card');box.append(el('p',title),el('strong',typeof value==='number'?number(value):value),el('p',note));quality.append(box);});$('#quality-content').append(quality);const patterns=data.report.conflict_patterns||{};$('#quality-content').append(el('h3','ทบทวนกลุ่มที่ต้องพักตรวจ'),el('p',`${patterns.POSSIBLE_SUBPERIOD||0} กลุ่มมีวันผลิตรวมเท่ากับวันในเดือน และ ${patterns.DAYS_EXCEED_MONTH||0} กลุ่มมีวันรวมเกินเดือน`),el('p','รูปแบบนี้ใช้จัดลำดับการตรวจเท่านั้น ยังพิสูจน์ไม่ได้ว่าช่วงวันไม่ซ้อนกันหรือใช้ฐานอัตราเดียวกัน ทุกกลุ่มยังคง HOLD และไม่รวมค่า','notice'));const max=Math.max(...data.coverage.map(r=>r.n));data.coverage.forEach((row,index)=>{const bar=el('div',undefined,'bar');bar.style.height=`${row.n/max*120}px`;bar.title=`${row.year_ce}: ${number(row.n)} candidates`;if(index%3===0||index===data.coverage.length-1)bar.append(el('span',String(row.year_ce)));$('#coverage').append(bar);});data.sources.forEach(source=>{const box=el('article',undefined,'source-card');box.append(el('h3',labels[source.package]),el('p','กรมเชื้อเพลิงธรรมชาติ · '+source.package),el('p',`หน่วย metadata: ${source.unit_label} · ${source.license_label}`));const link=el('a','เปิดข้อมูลต้นทาง ↗');link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';box.append(link,el('div',source.csv_sha256,'hash'),el('p',`ดึงข้อมูล: ${source.acquired_at}`,'muted'));$('#sources').append(box);});}
$('#filters').addEventListener('submit',event=>{event.preventDefault();state.page=1;load();});$('#reset').addEventListener('click',()=>{$('#filters').reset();state.page=1;load();});$('#previous').addEventListener('click',()=>{if(state.page>1){state.page--;load();}});$('#next').addEventListener('click',()=>{if(state.page*30<state.total){state.page++;load();}});$('#close-detail').addEventListener('click',()=>$('#detail').close());document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>activateView(button.dataset.view,true)));
let summaryPromise=null;function ensureSummary(){if(!summaryPromise)summaryPromise=get('/api/summary').then(data=>{renderOverview(data);return data;}).catch(error=>{summaryPromise=null;throw error;});return summaryPromise;}

let reportData=null,reportSources=[];
const metricNames={throughput:'วัตถุดิบป้อนโรงกลั่น',energy_total:'พลังงานใช้รวม',fuel_total:'เชื้อเพลิงใช้รวม',natural_gas:'ก๊าซธรรมชาติ',fuel_oil:'น้ำมันเตา',fuel_gas:'ก๊าซเชื้อเพลิง',coke:'โค้ก',diesel:'ดีเซล',electricity_consumption:'ไฟฟ้าใช้',electricity_purchased:'ไฟฟ้าซื้อจากภายนอก',electricity_sold:'ไฟฟ้าขาย',energy_intensity:'ความเข้มการใช้พลังงานตามรายงาน'};
const metricTitle=row=>row.metric_label_th||metricNames[row.metric_id]||row.source_label;
function boundaryTitle(row){return {REFINERY_FEEDSTOCK:'วัตถุดิบโรงกลั่น',REPORTED_INTENSITY_BOUNDARY_REVIEW:'ความเข้มที่รายงาน · รอตรวจขอบเขต',SPRC_REPORTED_OPERATIONS_SCOPE_REVIEW:'SPRC · ขอบเขตองค์กรรอตรวจ'}[row.boundary]||'TOP · TPX · TLB · LABIX · TOPSPP';}
function openReportDetail(row){
 const content=$('#detail-content');content.replaceChildren(el('h2',metricTitle(row),'detail-title'),el('p','รายละเอียดชั้นข้อมูลต้นทาง ดูผลรับข้อมูลตามนโยบายทีมที่เมนูพร้อมใช้ต่อ','notice'));
 const grid=el('div',undefined,'detail-grid');
 grid.append(item('ปีข้อมูล',row.year),item('ค่าต้นฉบับ',row.raw_value+' '+row.source_unit),item('ปรับเฉพาะตัวคูณหน่วย',row.normalized_value+' '+row.normalized_unit),item('ตำแหน่ง PDF',`หน้าไฟล์ ${row.pdf_page} / เลขพิมพ์ ${row.printed_page}`),item('เอกสารอธิบายขอบเขต',`หน้าไฟล์ ${row.footnotes_pdf_page} / เลขพิมพ์ ${row.footnotes_printed_page}`),item('ขอบเขต',boundaryTitle(row)));
 const link=el('a','เปิดรายงานต้นฉบับ ↗','button secondary');link.href=row.source_url+'#page='+row.pdf_page;link.target='_blank';link.rel='noopener noreferrer';
 content.append(grid,el('p','ปรับหน่วยด้วยตัวคูณตามต้นทางเท่านั้น ยังไม่หารด้วยปริมาณผลิตหรือทำ allocation','notice'),link,el('h3','SHA256 ของต้นฉบับ'),el('div',row.pdf_sha256,'hash'));
 const issues=(reportData.issues||[]).filter(i=>i.year===row.year&&i.metrics.includes(row.metric_id));
 issues.forEach(issue=>{content.append(el('h3','ประเด็นทบทวนบริบท'),el('p','ค่าระหว่างสองตารางต่างเกินช่วงการปัดเศษที่แสดง แต่ชื่อรายการยังต่างกัน จึงยังไม่สรุปว่าเป็นข้อมูลเดียวกันหรือเลือกค่าที่ถูก','notice'));issue.metrics.forEach(id=>{const related=reportData.rows.find(r=>r.metric_id===id&&r.year===issue.year);content.append(el('p',`${metricTitle(related)}: ${related.raw_value} ${related.source_unit} · PDF หน้า ${related.pdf_page}`));const evidenceLink=el('a',`เปิด PDF หน้า ${related.pdf_page} ↗`);evidenceLink.href=related.source_url+'#page='+related.pdf_page;evidenceLink.target='_blank';evidenceLink.rel='noopener noreferrer';content.append(evidenceLink);});});
 content.append(el('h3','Metadata และ mapping'),el('pre',JSON.stringify(row,null,2)));if(!$('#detail').open)$('#detail').showModal();
}
function renderReports(){
 const rows=reportData.rows.filter(r=>String(r.year)===$('#report-year').value);$('#report-rows').replaceChildren();
 $('#report-status').textContent=`${reportData.display_name} · ${reportData.row_count} รายการ / ${reportData.metric_count} ตัวชี้วัด · แสดงปี ${$('#report-year').value}: ${rows.length} รายการ · ชั้นข้อมูลต้นทาง`;
 $('#report-boundary').textContent=reportData.source==='SPRC_2024_REPORT'?'ขอบเขตรายงานรวมการดำเนินงาน การกระจายผลิตภัณฑ์ และธุรกิจตลาดเชื้อเพลิง จึงยังไม่ถือว่าทุกตัวเลขเป็นโรงกลั่นอย่างเดียว ข้อมูลสองตารางน้ำเก็บแยกกัน ไม่รวม total กับส่วนประกอบซ้ำ':'ข้อมูลพลังงานครอบคลุม 5 บริษัท ขณะที่ throughput เป็นข้อมูลโรงกลั่น จึงไม่หารเป็นค่าต่อหนึ่งตัน และไม่รวมยอด total กับส่วนประกอบซ้ำ ข้อมูลยังไม่ใช่ LCI ที่ผ่านการยอมรับ';
 const issues=$('#report-issues');issues.replaceChildren();
 if(reportData.arithmetic_checks){const passed=reportData.arithmetic_checks.filter(c=>c.result==='WITHIN_DISPLAY_ROUNDING').length;issues.append(el('p',`ตรวจยอดพลังงานกับส่วนประกอบ: ${passed}/${reportData.arithmetic_checks.length} กรณีอยู่ในช่วงที่การปัดเศษอธิบายได้ ไม่ใช่การยืนยันความถูกต้องทั้งชุด`,'muted'));}
 (reportData.issues||[]).filter(i=>String(i.year)===$('#report-year').value).forEach(issue=>{const box=el('article',undefined,'source-card');box.append(el('h3',`พักทบทวนบริบท · ${metricTitle(reportData.rows.find(r=>r.metric_id===issue.metrics[0]&&r.year===issue.year))} · ปี ${issue.year}`),el('p',`${issue.left_m3} ${issue.left_unit} กับ ${issue.right_m3} ${issue.right_unit} · PDF หน้า ${issue.source_pages.join(' / ')}`),el('p','ชื่อรายการอาจมีบริบทต่างกัน ช่วงปัดเศษไม่ทับกัน ไม่รวมค่าและไม่เลือกฝ่ายใด'));const button=el('button','ดูสองรายการประกอบกัน','evidence-btn');button.addEventListener('click',()=>openReportDetail(reportData.rows.find(r=>r.metric_id===issue.metrics[0]&&r.year===issue.year)));box.append(button);issues.append(box);});
 rows.forEach(row=>{const tr=el('tr'),amount=el('td',row.raw_value,'number'),evidence=el('td');amount.append(el('small',row.source_unit));const button=el('button','ดูที่มา','evidence-btn');button.addEventListener('click',()=>openReportDetail(row));evidence.append(button);tr.append(el('td',metricTitle(row)),el('td',row.direction==='CONTEXT'?'ตัวชี้วัดบริบท':row.direction==='INPUT'?'เข้า / ใช้':'ออก / รายงาน'),amount,el('td',boundaryTitle(row)),evidence);$('#report-rows').append(tr);});
}
$('#report-year').addEventListener('change',()=>{if(reportData)renderReports();});
$('#report-source').addEventListener('change',()=>{reportData=reportSources.find(r=>r.source===$('#report-source').value);if(reportData)renderReports();});
function loadReports(){return get('/api/reports').then(data=>{reportSources=data.sources;$('#report-source').replaceChildren();reportSources.forEach(source=>{const option=el('option',source.display_name);option.value=source.source;$('#report-source').append(option);});reportData=reportSources[0];if(reportData)renderReports();else $('#report-status').textContent='ยังไม่มีข้อมูลตัวอย่างรายงานในเครื่อง';}).catch(error=>{$('#report-status').textContent=error.message;return false;});}

const referenceState={page:1,request:0,total:0};
const kindLabels={ORGANIZATION_INPUT:'ข้อมูลเข้าองค์กร',ORGANIZATION_OUTPUT:'ข้อมูลออกองค์กร',REPORTED_INTENSITY:'ความเข้มตามรายงาน',CONTEXT_METRIC:'ข้อมูลบริบท'};
const referenceParams=()=>new URLSearchParams(new FormData($('#reference-filters')));
function openReference(row){const content=$('#detail-content');content.replaceChildren(el('h2',row.label,'detail-title'),el('p',row.decision==='ACCEPTED_REFERENCE'?'ทีมรับเป็นข้อมูลอ้างอิงภายในแล้ว':'พักทบทวนบริบท','notice'));const grid=el('div',undefined,'detail-grid');grid.append(item('ปีข้อมูล',row.reference_year),item('ค่าต้นฉบับ',row.quantities_withheld?'ไม่เปิดเผยปริมาณตามนโยบายสาธารณะ':row.raw_value+' '+row.raw_unit_label),item('ปรับตัวคูณหน่วย',row.scaled_amount+' '+row.unit_code),item('ประเภท / บทบาท',kindLabels[row.data_kind]+' / '+row.aggregation_role),item('ขอบเขตตามต้นทาง',row.boundary_note||'อ่านรายละเอียดในต้นฉบับ'),item('หน้า PDF / เลขพิมพ์',row.pdf_page+' / '+row.printed_page));content.append(grid,el('p','ไม่ได้จัดสรรต่อผลิตภัณฑ์ · สิทธิแจกจ่ายต่อยังไม่ยืนยัน','muted'));const link=el('a','เปิดหลักฐานต้นทาง ↗','button secondary');link.href=row.source_url+'#page='+row.pdf_page;link.target='_blank';link.rel='noopener noreferrer';content.append(link,el('h3','หลักฐานการตรวจ'),el('p',row.trace_verification),el('p','นโยบาย '+row.policy_version),el('div',row.pdf_sha256,'hash'),el('h3','ข้อมูลที่ส่งต่อให้ผู้ใช้'),el('pre',JSON.stringify(row,null,2)));if(!$('#detail').open)$('#detail').showModal();}
async function loadReference(){ensureReferenceChoices();const request=++referenceState.request;const p=referenceParams();p.set('page',referenceState.page);$('#reference-status').textContent='กำลังค้นหา…';$('#reference-rows').replaceChildren();$('#reference-previous').disabled=true;$('#reference-next').disabled=true;$('#reference-csv').removeAttribute('href');$('#reference-json').removeAttribute('href');try{const data=await get('/api/reference?'+p);if(request!==referenceState.request)return;referenceState.total=data.total;const m=data.manifest;if(data.quantities_withheld)data.rows.forEach(r=>r.quantities_withheld=true);$('#reference-status').textContent='';$('#reference-status').textContent=`ทีมรับ ${m.accepted_reference} รายการ · พัก ${m.held_context} รายการ · สกัดซ้ำจากต้นฉบับครบ ${m.reextracted_pdf_records} รายการ · ผลกรอง ${data.total} รายการ`;$('#reference-release').textContent='Release '+m.release_id.slice(0,12);$('#reference-page').textContent=`หน้า ${data.page} / ${Math.max(1,Math.ceil(data.total/30))}`;$('#reference-previous').disabled=data.page<=1;$('#reference-next').disabled=data.page*30>=data.total;$('#reference-rows').replaceChildren();data.rows.forEach(row=>{const tr=el('tr'),name=el('td',row.label),amount=el('td',row.scaled_amount,'number'),evidence=el('td');name.append(el('small',row.publisher));amount.append(el('small',row.unit_code));const button=el('button','ดูที่มา','evidence-btn');button.addEventListener('click',()=>openReference(row));evidence.append(button);tr.append(name,el('td',kindLabels[row.data_kind]+' / '+row.aggregation_role),el('td',String(row.reference_year)),amount,(()=>{const td=el('td');td.append(el('span',row.decision==='ACCEPTED_REFERENCE'?'✓ พร้อมอ้างอิง':'◷ พักทบทวน','tag '+(row.decision==='HOLD_CONTEXT'?'hold':'')));return td;})(),evidence);$('#reference-rows').append(tr);});if(!data.rows.length){const tr=el('tr'),td=el('td','ไม่พบข้อมูล ลองเปลี่ยนคำค้นหรือกดล้างตัวกรองทั้งหมด','empty');td.colSpan=6;tr.append(td);$('#reference-rows').append(tr);}if(!data.quantities_withheld)$('#reference-csv').href=apiUrl('/api/reference.csv?'+referenceParams());else $('#reference-status').append(' · แสดงเฉพาะ metadata ปริมาณยังไม่เปิดเผย');$('#reference-json').href=apiUrl('/api/reference.json?'+referenceParams());}catch(error){if(request!==referenceState.request)return;$('#reference-status').textContent=error.message;$('#reference-rows').replaceChildren();$('#reference-page').textContent='';return false;}}
$('#reference-filters').addEventListener('submit',event=>{event.preventDefault();referenceState.page=1;loadReference();});
$('#reference-previous').addEventListener('click',()=>{if(referenceState.page>1){referenceState.page--;loadReference();}});
$('#reference-next').addEventListener('click',()=>{if(referenceState.page*30<referenceState.total){referenceState.page++;loadReference();}});

$('#reference-reset').addEventListener('click',()=>{$('#reference-filters').reset();referenceState.page=1;loadReference();});

let nsoData=null;
function renderNso(){if(!nsoData)return;const selected=$('#nso-table').value;populateNsoChoices();const query=$('#nso-search').value.trim().toLocaleLowerCase();const year=$('#nso-year').value;const rows=nsoData.rows.filter(r=>r.table_id===selected&&(!year||String(r.reference_year)===year)&&(!query||(r.label+' '+r.measure+' '+r.source_row.join(' ')).toLocaleLowerCase().includes(query)));$('#nso-status').textContent=`ตาราง ${selected} · ${rows.length} ค่า · ทั้งชุด ${nsoData.row_count} ค่า · กดหลักฐานเพื่ออ่านเชิงอรรถ/หน่วยงานต้นทาง`;$('#nso-rows').replaceChildren();if(!rows.length){const tr=el('tr'),td=el('td','ไม่พบข้อมูลตามเงื่อนไข ลองเลือกทุกปีหรือล้างตัวกรอง','empty');td.colSpan=4;tr.append(td);$('#nso-rows').append(tr);}for(const row of rows){const tr=el('tr'),label=el('td',row.label),value=el('td',row.raw_value,'number'),action=el('td'),button=el('button','ดูที่มา','evidence-btn');label.append(el('small',row.measure));value.append(el('small',row.unit));button.addEventListener('click',()=>{const content=$('#detail-content');content.replaceChildren(el('h2',row.label,'detail-title'));const grid=el('div',undefined,'detail-grid');grid.append(item('ปีข้อมูล',row.reference_year),item('ค่า / หน่วย',row.raw_value+' '+row.unit),item('ตาราง / บรรทัด / คอลัมน์',row.table_id+' / '+row.source_line+' / '+row.source_column),item('หน่วยงานต้นทาง',row.originating_agency));content.append(grid,el('p','ข้อมูลสถิติระดับประเทศ · ยังไม่รวมในชุดอ้างอิงองค์กร 97 รายการ','notice'),evidenceNavigation('nso',row),sourceRowPreview(row),el('h3','หมายเหตุและเชิงอรรถ'),el('pre',row.notes.join('\n')),el('h3','SHA256 ต้นฉบับ'),el('div',row.source_sha256,'hash'));if(!$('#detail').open)$('#detail').showModal();});action.append(button);tr.append(label,el('td',String(row.reference_year)),value,action);$('#nso-rows').append(tr);}window.TamsoodDiscovery?.renderNso(rows);}
$('#nso-table').addEventListener('change',()=>{$('#nso-search').value='';renderNso();});
function loadNso(){return get('/api/nso?profile=explorer-v1').then(data=>{nsoData=window.TamsoodDiscovery?window.TamsoodDiscovery.hydrate(data):data;renderNso();}).catch(error=>{$('#nso-status').textContent=error.message;return false;});}

$('#nso-year').addEventListener('change',renderNso);$('#nso-search').addEventListener('input',renderNso);$('#nso-reset').addEventListener('click',()=>{$('#nso-year').value='';$('#nso-search').value='';renderNso();});

function loadNsoComparison(){return get('/api/nso-comparison').then(data=>{const box=$('#nso-comparison');box.hidden=false;
 const r=data.revised;
 box.textContent=r?`ผลเทียบอุตสาหกรรมการผลิตปี2024: สสช. ${data.nso_value} / DEDE revised ${r.dede_revised_value} ktoe · ${r.exact_displayed_value_match?'ค่าที่แสดงตรงกัน':'ค่าที่แสดงยังต่างกัน'} · รายงานเบื้องต้นเดิม ${data.dede_preliminary_value} ยังคงเก็บแยก · เทียบยอดนี้เท่านั้น ไม่ใช่ครบ273ค่า และไม่ใช่การวัดอิสระ `:`ผลเทียบที่ต้องทบทวน: อุตสาหกรรมการผลิตปี2024 สสช. ${data.nso_value} / DEDEเบื้องต้น ${data.dede_preliminary_value} ktoe ต่าง ${data.difference_nso_minus_dede} · ไม่แก้ค่าต้นฉบับ · ตรวจเฉพาะหนึ่งยอด ไม่ใช่ครบ273ค่า`;
 if(r){const link=el('a','เปิดรายงาน revised ↗');link.href=r.revised_source_url;link.target='_blank';link.rel='noopener noreferrer';box.append(link);}
}).catch(()=>false);}
let inventoryData=null;
function inventorySelection(data,process,direction){
 const rows=data.rows.filter(row=>row.process===process);
 const fields=['reference_amount','reference_unit','boundary','geography','technology_level','publication_year','data_period','allocation','doi','source_snapshot_sha256','licence','authors'];
 if(rows.length&&fields.some(key=>rows.some(row=>row[key]!==rows[0][key])))return {context:null,rows:[],error:'ข้อมูลกระบวนการนี้มีฐานอ้างอิงหรือขอบเขตไม่ตรงกัน จึงพักการแสดงรวมเพื่อทบทวน'};
 return {context:rows[0]||null,rows:rows.filter(row=>!direction||row.direction===direction)};
}
function inventoryExport(data,process,direction){
 if(!['FAME','H-FAME'].includes(process)||!['','INPUT','OUTPUT'].includes(direction))throw Error('ตัวกรองส่งออกไม่ถูกต้อง');
 const selected=inventorySelection(data,process,direction),all=inventorySelection(data,process,'');
 if(!selected.context||selected.error||!all.rows.length)throw Error('บริบทกระบวนการไม่สอดคล้องกัน');
 if(selected.context.reference_amount!=='1000'||selected.context.reference_unit!=='MJ fuel'||!/^[a-f0-9]{64}$/.test(selected.context.source_snapshot_sha256||''))throw Error('ฐานหรือรุ่นต้นฉบับไม่รองรับ export นี้');
 if(new Set(all.rows.map(r=>r.observation_id)).size!==all.rows.length||all.rows.filter(r=>r.role==='REFERENCE_PRODUCT').length!==1)throw Error('Identity หรือผลิตภัณฑ์อ้างอิงไม่ถูกต้อง');
 if(all.rows.some(r=>r.licence!=='CC BY 4.0'||r.is_full_lci_dataset!==false||r.is_newly_allocated!==false||typeof r.amount!=='string'||!/^\d+(?:\.\d+)?$/.test(r.amount)||!Number.isFinite(Number(r.amount))||!r.unit||!((r.direction==='INPUT'&&r.role==='INPUT')||(r.direction==='OUTPUT'&&['OUTPUT','REFERENCE_PRODUCT','CO_PRODUCT'].includes(r.role)))))throw Error('สถานะหรือสิทธิข้อมูลไม่รองรับ export นี้');
 return {scope:'SOURCE_REPORTED_CONVERSION_REVIEW_EXPORT',source_snapshot_sha256:selected.context.source_snapshot_sha256,
  doi:selected.context.doi,licence:'CC BY 4.0',attribution:selected.context.authors,
  reference_basis:{amount:selected.context.reference_amount,unit:selected.context.reference_unit},
  boundary:selected.context.boundary,measurement_period:selected.context.data_period,
  selection:{process,direction:direction||'ALL',exported_rows:selected.rows.length},
  rows:selected.rows.map(row=>({...row})),model_ready:false,allocation_applied:false,
  provider_links_applied:0,full_lifecycle_inventory:false,
  limitations:['Review export; not an interoperable LCA-tool dataset','Allocation application and background links remain unresolved']};
}
function renderInventory(){
 if(!inventoryData)return;
 const selection=inventorySelection(inventoryData,$('#inventory-process').value,$('#inventory-direction').value),context=selection.context,filtered=selection.rows;
 $('#inventory-rows').replaceChildren();$('#inventory-context').replaceChildren();
 $('#inventory-download').disabled=true;
 if(context){
  const box=$('#inventory-context');
  box.append(item('กระบวนการ / เทคโนโลยี',context.process+' · '+context.technology_level),item('ฐานอ้างอิงตามต้นฉบับ',context.reference_amount+' '+context.reference_unit),item('พื้นที่',context.geography),item('ปีเผยแพร่ / ช่วงปีวัด',context.publication_year+' / '+(context.data_period??'ต้นฉบับไม่ระบุ')));
  box.append(item('ความพร้อมใช้งาน','อ่านอ้างอิงได้ · ยังไม่พร้อมคำนวณ LCI ทั้งวงจร'));
  const quality=el('details',undefined,'readiness-issues');quality.append(el('summary','คุณภาพ สิทธิ และรุ่นต้นฉบับของ '+context.process));
  quality.append(el('p','ตรวจค่าตามตารางที่เลือกแล้ว · ไม่ได้ตรวจวัดใหม่หรือยืนยันเป็นค่าเฉลี่ยประเทศไทย'),el('p','ยังไม่ยืนยันการใช้ allocation และยังไม่เชื่อม background processes'),el('p','สิทธิข้อมูล: '+context.licence+' · '+context.authors),el('p','รุ่นต้นฉบับตาราง: '+context.source_snapshot_sha256.slice(0,12)),el('p','ดาวน์โหลดเพื่อทบทวนได้ แต่ยังไม่ใช่รูปแบบนำเข้า openLCA/ILCD ที่ทดสอบแล้ว'));box.append(quality);
  $('#inventory-boundary').textContent='ข้อมูลในเว็บนี้: เฉพาะวัตถุดิบ พลังงาน และผลผลิตในขั้นแปรรูปเชื้อเพลิงจาก Table 4 ไม่ครอบคลุมทั้งวงจรชีวิต';
  $('#inventory-allocation').textContent=context.allocation;
 }else{$('#inventory-boundary').textContent='ไม่พบกระบวนการ';$('#inventory-allocation').textContent='';}
 $('#inventory-status').textContent=`แสดง ${filtered.length} รายการของ ${$('#inventory-process').value} · ทั้งชุด ${inventoryData.source_reported_inventory_count} รายการ · พัก BHD ${inventoryData.excluded_count} รายการ · ไม่รวมค่าข้ามกระบวนการหรือหน่วย`;
 if(selection.error){$('#inventory-status').textContent=selection.error;return;}
 $('#inventory-download').disabled=!context||!filtered.length;
 for(const row of filtered){const tr=el('tr'),process=el('td',row.process),value=el('td',row.amount,'number'),action=el('td'),button=el('button','ดูที่มา','evidence-btn');process.append(el('small',row.technology_level));value.append(el('small',row.unit));button.addEventListener('click',()=>{const content=$('#detail-content');content.replaceChildren(el('h2',flowDisplay(row.flow),'detail-title'));const grid=el('div',undefined,'detail-grid');grid.append(item('Process / direction',row.process+' / '+row.direction),item('ค่าตามตาราง',row.raw_value+' '+row.unit),item('ฐานอ้างอิง',row.reference_amount+' '+row.reference_unit),item('บทบาท',row.role),item('ค่าที่ระบบจัดเก็บ',row.amount+' '+row.unit),item('ปีเผยแพร่ / ปีวัด',row.publication_year+' / '+(row.data_period??'ไม่ระบุ')),item('ตาราง / แถว / คอลัมน์',row.table_id+' / '+row.source_row+' / '+row.source_column));const link=el('a','เปิด Table 4 บนเว็บผู้ตีพิมพ์ ↗','button secondary');link.href=row.source_url;link.target='_blank';link.rel='noopener noreferrer';content.append(grid,el('p',row.boundary,'notice'),link,el('p',row.allocation),el('p',row.annotation||'ไม่มีการแปลงหน่วยหรือจัดสรรเพิ่ม'),el('p',row.authors+' · DOI '+row.doi+' · '+row.licence),el('div',row.source_snapshot_sha256,'hash'));if(!$('#detail').open)$('#detail').showModal();});action.append(button);const flow=el('td',row.direction+' · '+flowDisplay(row.flow));flow.append(el('small',({REFERENCE_PRODUCT:'ผลิตภัณฑ์อ้างอิง',CO_PRODUCT:'ผลิตภัณฑ์ร่วม',INPUT:'สิ่งเข้า',OUTPUT:'สิ่งออก'})[row.role]||row.role));tr.append(process,flow,value,el('td',row.reference_amount+' '+row.reference_unit),action);$('#inventory-rows').append(tr);}
 if(!filtered.length){const tr=el('tr'),td=el('td','ไม่พบรายการตามทิศทางที่เลือก','empty');td.colSpan=5;tr.append(td);$('#inventory-rows').append(tr);}
}
function loadInventory(){return get('/api/product-inventory').then(data=>{
 inventoryData=data;const selected=$('#inventory-process').value;$('#inventory-process').replaceChildren();
 const processes=[...new Set(data.rows.map(row=>row.process))];
 for(const process of processes){const option=el('option',process==='FAME'?'ไบโอดีเซล (FAME)':'ไบโอดีเซลเติมไฮโดรเจน (H-FAME)');option.value=process;$('#inventory-process').append(option);}
 $('#inventory-process').value=processes.includes(selected)?selected:(processes[0]||'');renderInventory();
}).catch(error=>{$('#inventory-status').textContent=error.message;return false;});}
$('#inventory-process').addEventListener('change',renderInventory);
$('#inventory-direction').addEventListener('change',renderInventory);
$('#inventory-download').addEventListener('click',()=>{
 if(!inventoryData)return;
 try{
  const process=$('#inventory-process').value,direction=$('#inventory-direction').value,payload=inventoryExport(inventoryData,process,direction);
  const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json;charset=utf-8'}),url=URL.createObjectURL(blob),link=el('a');
  link.href=url;link.download='TamsoodBase-'+process+'-'+(direction||'ALL')+'-review.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }catch(error){$('#inventory-status').textContent=error.message;}
});
let upstreamData=null,upstreamPending=null;
function validateUpstream(data){
 if(!data||data.scope!=='LICENSED_PUBLIC_SOURCE_REPORTED_UPSTREAM_CANDIDATES'||data.licence!=='CC BY 4.0'||!Array.isArray(data.rows)||data.rows.length!==42||data.full_lifecycle_inventory!==false||data.model_ready!==false||data.allocation_applied!==false||data.provider_links_applied!==0||!/^[a-f0-9]{64}$/.test(data.public_snapshot_id||''))throw Error('รูปแบบข้อมูลต้นน้ำไม่ตรงกับรุ่นที่ตรวจแล้ว');
 const ids=new Set();
 for(const row of data.rows){
  if(!['FFB','CPO','RBDPO'].includes(row.process)||!['INPUT','OUTPUT'].includes(row.direction)||row.reference_amount!=='1000'||row.reference_unit!=='kg'||typeof row.amount!=='string'||!/^\d+(?:\.\d+)?$/.test(row.amount)||!Number.isFinite(Number(row.amount))||row.source_sha256!==data.source_sha256||row.doi!=='10.3390/su12229415'||!/^[a-f0-9]{64}$/.test(row.observation_id||'')||ids.has(row.observation_id)||(row.unit===null)!==(row.status==='HOLD_MISSING_UNIT'))throw Error('บริบทหรือสถานะข้อมูลต้นน้ำไม่ถูกต้อง');
  ids.add(row.observation_id);
 }
 for(const process of ['FFB','CPO','RBDPO']){
  const p=data.process_profiles?.[process];
  if(!p||p.reference_amount!=='1000'||p.reference_unit!=='kg'||p.model_ready!==false||p.quality_score!==null||!p.boundary||!p.quality_dimensions||!Array.isArray(p.open_issues))throw Error('รายละเอียดกระบวนการไม่ครบ');
 }
 return data;
}
function upstreamSelection(data,process,direction){
 return data.rows.filter(row=>row.process===process&&(!direction||row.direction===direction));
}
function upstreamExport(data,process,direction){
 validateUpstream(data);
 if(!['FFB','CPO','RBDPO'].includes(process)||!['','INPUT','OUTPUT'].includes(direction))throw Error('ตัวกรองส่งออกไม่ถูกต้อง');
 const rows=upstreamSelection(data,process,direction).map(row=>({...row}));
 return {version:1,scope:'SOURCE_REPORTED_UPSTREAM_REVIEW_EXPORT',public_snapshot_id:data.public_snapshot_id,licence:data.licence,attribution:data.attribution,publisher_url:data.publisher_url,source_pdf_url:data.source_pdf_url,source_sha256:data.source_sha256,source_counts:data.counts,selection:{process,direction:direction||'ALL',exported_rows:rows.length},process_profile:data.process_profiles[process],rows,model_ready:false,full_lifecycle_inventory:false,allocation_applied:false,provider_links_applied:0};
}
function renderUpstream(){
 if(!upstreamData)return;
 const process=$('#upstream-process').value,rows=upstreamSelection(upstreamData,process,$('#upstream-direction').value);
 $('#upstream-basis').textContent='ฐานตามตาราง: ผลิต '+process+' 1,000 kg · ไม่ใช่ฐาน 1,000 MJ ของตารางผลิตเชื้อเพลิง';
 $('#upstream-status').textContent=`${rows.length} รายการ · พักเพราะไม่ระบุหน่วย ${rows.filter(r=>r.status==='HOLD_MISSING_UNIT').length} รายการ · ยังไม่พร้อมคำนวณแบบจำลอง`;
 $('#upstream-rows').replaceChildren();
 $('#upstream-download').disabled=!rows.length;
 const profile=upstreamData.process_profiles?.[process],readiness=$('#upstream-readiness');readiness.replaceChildren();
 if(profile){
  readiness.append(item('ตรวจค่าจากต้นฉบับ','ตรวจแล้ว '+(profile.unit_present_rows+profile.held_rows)+' รายการ'),item('พร้อมคำนวณ LCI','ยังไม่พร้อม · ต้องทบทวนแบบจำลอง'));
  readiness.append(item('ขอบเขตที่แสดง',profile.boundary.included),item('ใช้ข้อมูลนี้ทำอะไรได้',profile.usable_for.join(' · ')));
  const details=el('details',undefined,'readiness-issues');details.append(el('summary','ต้องตรวจอะไรเพิ่มสำหรับ '+process));const list=el('ul');profile.open_issues.forEach(reason=>list.append(el('li',reason)));details.append(list);readiness.append(details);
  const quality=el('details',undefined,'readiness-issues');quality.append(el('summary','ดูคุณภาพ สิทธิ และรุ่นข้อมูล'));const grid=el('div',undefined,'detail-grid');
  const labels={source_verification:'ค่าต้นฉบับ',measurement_period:'ช่วงเวลาวัด',geography:'พื้นที่',model_completeness:'ความครบถ้วน',independent_measurement:'การตรวจวัดใหม่',redistribution:'สิทธิแจกจ่าย'};
  for(const [key,label] of Object.entries(labels))grid.append(item(label,profile.quality_dimensions[key]));
  quality.append(grid,el('p','ยังไม่พร้อมสำหรับ: '+profile.not_ready_for.join(' · ')),el('p','ยังไม่นำเข้า: '+profile.boundary.excluded_from_imported_model.join(' · ')),el('p',profile.boundary.interpretation),el('small','รุ่นข้อมูล: '+upstreamData.public_snapshot_id.slice(0,12)));readiness.append(quality);
 }
 for(const row of rows){
  const tr=el('tr'),name=el('td',flowDisplay(row.flow)),value=el('td',row.raw_value,'number'),status=el('td'),action=el('td');
  name.append(el('small',row.direction==='INPUT'?'สิ่งเข้า':row.role==='REFERENCE_PRODUCT'?'ผลิตภัณฑ์อ้างอิง':'สิ่งออก · ยังไม่จัดประเภทเพิ่ม'));
  value.append(el('small',row.unit??'ต้นฉบับไม่ระบุหน่วย'));
  status.append(el('span',row.status==='HOLD_MISSING_UNIT'?'พัก · ไม่มีหน่วย':'ค่าตรงต้นฉบับ · รอตรวจแบบจำลอง','tag '+(row.status==='HOLD_MISSING_UNIT'?'hold':'')));
  const button=el('button','ดูที่มา','evidence-btn');button.addEventListener('click',()=>{
   const content=$('#detail-content');content.replaceChildren(el('h2',flowDisplay(row.flow),'detail-title'));
   const grid=el('div',undefined,'detail-grid');grid.append(item('กระบวนการ / ฐาน',row.process+' / '+row.reference_amount+' '+row.reference_unit+' '+row.reference_flow),item('ค่าตามต้นฉบับ',row.raw_value+' '+(row.unit??'(ไม่ระบุหน่วย)')),item('ตาราง / หน้า PDF / แถวข้อมูล',row.table_id+' / '+row.pdf_page+' / '+row.table_data_row),item('ปีเผยแพร่ / ช่วงปีวัด',row.publication_year+' / ไม่ระบุ'));
   grid.append(item('ค่าที่ระบบจัดเก็บ',row.amount+' '+(row.unit??'(ไม่ระบุหน่วย)')),item('การแปลงที่ทำ','อ่านเลขเป็นทศนิยม · ไม่เปลี่ยนหน่วยหรือปันส่วนเพิ่ม'));
   content.append(grid,el('p',row.status==='HOLD_MISSING_UNIT'?'รายการนี้พักไว้ ไม่เติมหน่วยและไม่นำไปคำนวณ':'ตรวจค่าจากต้นฉบับแล้ว แต่ยังไม่ยืนยัน allocation และความครบถ้วนของแบบจำลอง','notice'));
   const links=el('div',undefined,'evidence-navigation');
   for(const [label,url] of [['เปิด PDF ตรงหน้าตาราง',row.source_url],['เปิดเว็บไซต์บทความ',upstreamData.publisher_url]]){const a=el('a',label+' ↗','evidence-destination');a.href=url;a.target='_blank';a.rel='noopener noreferrer';links.append(a);}
   content.append(links,el('p','ลิงก์ PDF เปิดหน้าตาราง ไม่ได้เน้นช่องข้อมูลอัตโนมัติ · แถวข้อมูลนับเฉพาะรายการในตาราง'),el('p',upstreamData.attribution),el('p','CC BY 4.0 · ค่าดิบและหน่วยไม่เปลี่ยน; ไม่มีการปันส่วนเพิ่ม'),el('p','รุ่นชุดข้อมูล: '+upstreamData.public_snapshot_id.slice(0,12)),el('div',row.source_sha256,'hash'));
   if(!$('#detail').open)$('#detail').showModal();
  });action.append(button);tr.append(name,value,status,action);$('#upstream-rows').append(tr);
 }
 if(!rows.length){const tr=el('tr'),td=el('td','ไม่มีรายการตามตัวกรอง','empty');td.colSpan=4;tr.append(td);$('#upstream-rows').append(tr);}
}
function loadUpstream(){
 if(upstreamData){renderUpstream();return Promise.resolve(true);}
 if(upstreamPending)return upstreamPending;
 $('#upstream-status').textContent='กำลังโหลดข้อมูลต้นน้ำ…';$('#upstream-retry').hidden=true;
 upstreamPending=(async()=>{
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
  try{
   const response=await fetch('/upstream-inventory.json',{signal:controller.signal,headers:{Accept:'application/json'}});
   if(!response.ok||!(response.headers.get('content-type')||'').includes('application/json'))throw Error('โหลดข้อมูลต้นน้ำไม่สำเร็จ');
   const data=await response.json();
   validateUpstream(data);
   upstreamData=data;renderUpstream();return true;
  }catch(error){$('#upstream-status').textContent=error.name==='AbortError'?'โหลดนานเกินไป ลองใหม่ได้':error.message;$('#upstream-retry').hidden=false;return false;}
  finally{clearTimeout(timer);upstreamPending=null;}
 })();return upstreamPending;
}
document.querySelectorAll('[data-inventory-layer]').forEach(button=>button.addEventListener('click',()=>{
 const upstream=button.dataset.inventoryLayer==='upstream';$('#inventory-conversion').hidden=upstream;$('#inventory-upstream').hidden=!upstream;
 document.querySelectorAll('[data-inventory-layer]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
 if(upstream)loadUpstream();
}));
$('#upstream-process').addEventListener('change',renderUpstream);$('#upstream-direction').addEventListener('change',renderUpstream);$('#upstream-retry').addEventListener('click',loadUpstream);
$('#upstream-download').addEventListener('click',()=>{
 if(!upstreamData)return;
 const process=$('#upstream-process').value,direction=$('#upstream-direction').value,payload=upstreamExport(upstreamData,process,direction);
 const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json;charset=utf-8'}),url=URL.createObjectURL(blob),link=el('a');
 link.href=url;link.download='TamsoodBase-'+process+'-'+(direction||'ALL')+'-review.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
});

// Topic-first catalog: navigation uses the same controls as the sidebar.
document.querySelectorAll('[data-open]').forEach(button=>button.addEventListener('click',()=>{
 document.querySelector('.nav[data-view="'+button.dataset.open+'"]').click();
 const heading=document.querySelector('#view-'+button.dataset.open+' h2');
 heading.setAttribute('tabindex','-1');heading.focus();
}));
function filterCatalog(){
 const query=$('#catalog-search').value.trim().toLocaleLowerCase(),level=$('#catalog-level').value;
 let visible=0;const counts={'':0,national:0,organization:0,product:0};
 document.querySelectorAll('.dataset-card').forEach(card=>{
  const queryMatches=!query||(card.textContent+' '+card.dataset.keywords).toLocaleLowerCase().includes(query);
  if(queryMatches){counts['']++;counts[card.dataset.level]++;}
  const matches=(!level||card.dataset.level===level)&&queryMatches;
  card.hidden=!matches;if(matches)visible++;
 });
 $('#catalog-results').textContent=`พบ ${visible} ชุดข้อมูล · กดดูข้อมูลของแต่ละชุดได้เลย`;
 $('#catalog-empty').hidden=visible!==0;
 document.querySelectorAll('[data-catalog-level]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.catalogLevel===level)));
 document.querySelectorAll('[data-level-count]').forEach(label=>{label.textContent=String(counts[label.dataset.levelCount]||0);});
 $('#catalog-reset').disabled=!query&&!level;
}
document.querySelectorAll('[data-catalog-level]').forEach(button=>button.addEventListener('click',()=>{$('#catalog-level').value=button.dataset.catalogLevel;filterCatalog();}));
function setCatalogLayout(layout){
 if(!['grid','list'].includes(layout))layout='grid';
 $('#catalog-grid').dataset.layout=layout;
 document.querySelectorAll('[data-catalog-layout]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.catalogLayout===layout)));
 try{localStorage.setItem('tamsood.catalog-layout',layout);}catch{}
}
document.querySelectorAll('[data-catalog-layout]').forEach(button=>button.addEventListener('click',()=>setCatalogLayout(button.dataset.catalogLayout)));
setCatalogLayout('grid');
$('#catalog-search').addEventListener('input',filterCatalog);
$('#catalog-level').addEventListener('change',filterCatalog);
$('#catalog-reset').addEventListener('click',()=>{$('#catalog-search').value='';$('#catalog-level').value='';filterCatalog();});
filterCatalog();

const eppoState={page:1,total:0,request:0};
async function loadEppo(){
 eppoState.controller?.abort();eppoState.controller=new AbortController();
 const request=++eppoState.request,p=new URLSearchParams(new FormData($('#eppo-filters')));p.set('page',eppoState.page);
 $('#eppo-status').textContent='กำลังค้นหา…';$('#eppo-rows').replaceChildren();$('#eppo-prev').disabled=true;$('#eppo-next').disabled=true;
 try{const data=await get('/api/eppo?'+p,{signal:eppoState.controller.signal});if(request!==eppoState.request)return;eppoState.total=data.total;
 $('#eppo-status').textContent=`พบ ${data.total} ค่า · ข้อมูลต้นทาง DOEB ผ่าน EPPO · ปีอัปเดต metadata บางช่องล้าหลังค่าจริง`;
 $('#eppo-rows').replaceChildren();
 for(const row of data.rows){const tr=el('tr'),amount=el('td',row.raw_value,'number'),action=el('td'),button=el('button','ดูที่มา','evidence-btn');amount.append(el('small',row.unit));
 button.addEventListener('click',()=>{const content=$('#detail-content');content.replaceChildren(el('h2',row.subject,'detail-title'));const grid=el('div',undefined,'detail-grid');grid.append(item('ค่า / หน่วย',row.raw_value+' '+row.unit),item('เดือน',row.reference_year+'-'+String(row.month).padStart(2,'0')),item('ขอบเขต',row.scope),item('บรรทัด CSV',row.source_line));content.append(grid,el('p',row.temporal_basis,'notice'),evidenceNavigation('eppo',row),el('p',row.license_label+' · เงื่อนไขแจกจ่ายเฉพาะยังไม่ยืนยัน'),el('div',row.source_sha256,'hash'),el('pre',JSON.stringify(row.source_row,null,2)));if(!$('#detail').open)$('#detail').showModal();});action.append(button);tr.append(el('td',row.subject),el('td',row.reference_year+'-'+String(row.month).padStart(2,'0')),amount,action);$('#eppo-rows').append(tr);}
 if(!data.rows.length){const tr=el('tr'),td=el('td','ไม่พบข้อมูล ลองเปลี่ยนปีหรือคำค้น','empty');td.colSpan=4;tr.append(td);$('#eppo-rows').append(tr);}
 $('#eppo-page').textContent=`หน้า ${eppoState.page} / ${Math.max(1,Math.ceil(data.total/40))}`;$('#eppo-prev').disabled=eppoState.page===1;$('#eppo-next').disabled=eppoState.page*40>=data.total;
 }catch(error){if(request!==eppoState.request)return;$('#eppo-status').textContent=error.message;$('#eppo-rows').replaceChildren();$('#eppo-page').textContent='';return false;}
}
$('#eppo-filters').addEventListener('submit',event=>{event.preventDefault();eppoState.page=1;loadEppo();});
$('#eppo-reset').addEventListener('click',()=>{$('#eppo-filters').reset();eppoState.page=1;loadEppo();});
$('#eppo-prev').addEventListener('click',()=>{if(eppoState.page>1){eppoState.page--;loadEppo();}});
$('#eppo-next').addEventListener('click',()=>{if(eppoState.page*40<eppoState.total){eppoState.page++;loadEppo();}});

// Navigation is bookmarkable; the mobile menu closes after a selection.
const views=['catalog','explore','quality','reference','reports','inventory','case-study','ethanol','nso','eppo','sources'];
const viewScroll=new Map();
function closeNavigation(){document.body.classList.remove('menu-open');$('#nav-toggle').setAttribute('aria-expanded','false');}
function activateView(view,push=false,options={}){
 const requestedCase=new URLSearchParams(String(view).split('?')[1]).get('case');
 const route=window.TamsoodDiscovery?.route(view)||{view};view=route.view;
 if(!views.includes(view))view='catalog';
 const previous=document.body.dataset.activeView;if(previous!==view)viewScroll.set(previous,window.scrollY);
 if(view==='nso'&&window.TamsoodDiscovery){$('#nso-table').value=route.table;$('#nso-year').value=route.year;$('#nso-search').value=route.q;}

 document.body.dataset.activeView=view;
 document.querySelectorAll('[data-view]').forEach(button=>{
  const active=button.dataset.view===view;button.classList.toggle('active',active);
  if(active){button.setAttribute('aria-current','page');$('#page-context').textContent=button.querySelector('span').textContent;document.title=button.querySelector('span').textContent+' · TamsoodBase';}
  else button.removeAttribute('aria-current');
 });
 views.forEach(name=>{$('#view-'+name).hidden=name!==view;});
 const caseId=['dede','cmu','tsm','uasb','e10','bagasse'].includes(requestedCase)?requestedCase:'dede';
 const destination='#'+view+(view==='ethanol'&&requestedCase?'?case='+caseId:'');
 if(push&&location.hash!==destination)history.pushState(null,'',destination);
 closeNavigation();
 const activeButton=document.querySelector('[data-view="'+view+'"]');const group=activeButton?.closest('details');if(group)group.open=true;
 if(previous!==view){const title=options.restore?$('#view-'+view):$('#view-'+view).querySelector('h1,h2');if(title){title.tabIndex=-1;title.focus({preventScroll:true});}window.scrollTo({top:options.restore?(viewScroll.get(view)||0):0,behavior:'instant'});}
 if(view==='ethanol'){
  const selected=caseId;
  document.querySelectorAll('[data-ethanol-case]').forEach(panel=>{panel.hidden=panel.dataset.ethanolCase!==selected;});
  document.querySelectorAll('#view-ethanol .toolbar a').forEach(link=>{
   if(link.hash.endsWith('='+selected))link.setAttribute('aria-current','true');
   else link.removeAttribute('aria-current');
  });
 }
 if(view==='nso'&&nsoData)renderNso();
 ensureLoaded(view);
}
$('#nav-toggle').addEventListener('click',()=>{const open=document.body.classList.toggle('menu-open');$('#nav-toggle').setAttribute('aria-expanded',String(open));});
window.addEventListener('popstate',()=>activateView(location.hash.slice(1),false,{restore:true}));
window.addEventListener('hashchange',()=>activateView(location.hash.slice(1)));
window.addEventListener('tamsood:navigate',event=>activateView(event.detail.view,true));
document.addEventListener('click',event=>{const link=event.target.closest?.('a[href^="#"]');if(!link||event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;const target=link.getAttribute('href').slice(1);if(views.includes(target.split('?')[0])){event.preventDefault();activateView(target,true);}});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&document.body.classList.contains('menu-open')){closeNavigation();$('#nav-toggle').focus();}});
$('#connection-retry').addEventListener('click',()=>location.reload());
window.addEventListener('tamsood:connection',event=>{
 const mode=event.detail.state,banner=$('#connection-banner');banner.dataset.state=mode;
 const failed=(event.detail.failedDatasets||[]).map(path=>({'/api/nso':'สถิติประเทศ','/api/nso-comparison':'ผลเทียบแหล่งข้อมูล','/api/eppo':'โรงกลั่น','/api/reference':'ข้อมูลบริษัท'}[path]||'ข้อมูลบางชุด'));
 $('#connection-message').textContent=mode==='restricted'?'ปิดการโหลดข้อมูลจากฐานข้อมูลชั่วคราวระหว่างตรวจสอบสิทธิ์เผยแพร่':mode==='error'&&failed.length?'โหลดไม่สำเร็จ: '+[...new Set(failed)].join(', ')+' · ชุดอื่นยังเปิดดูได้':mode==='unauthorized'?'เข้าสู่ระบบด้วยบัญชีทดสอบของทีมเพื่อดูข้อมูล':mode==='error'?'บางรายการโหลดไม่ได้ ตรวจการเชื่อมต่อแล้วลองใหม่':mode==='connected'?'เชื่อมต่อระบบแล้ว · พร้อมใช้งาน':'กำลังโหลดข้อมูล…';
 $('#connection-login').hidden=mode!=='unauthorized';
 $('#connection-retry').hidden=mode!=='error';
});
$('#deployment-mode').textContent='CN230 · MTEC';$('#deployment-mode').dataset.mode=window.TamsoodAPI.base?'remote':'same-origin';
const SOURCE_REFERENCE_CODES=Object.freeze({
 'DMF-CKAN-OIL':'SRC-01',
 'DMF-CKAN-CONDENSATE':'SRC-02',
 'DMF-CKAN-GAS':'SRC-03',
 'THAIOIL-REPORT-2024':'SRC-04',
 'SPRC-REPORT-2024':'SRC-05',
 'NSO-SYB2026-13.5':'SRC-06','NSO-SYB2026-13.6':'SRC-06','NSO-SYB2026-13.7':'SRC-06','NSO-SYB2026-13.8':'SRC-06','NSO-SYB2026-13.10':'SRC-06',
 'EPPO-11_13':'SRC-07','EPPO-11_14':'SRC-08',
 'MDPI-SU12229415-T4':'SRC-09'
});
async function loadSourceCrosswalk(){
 const target=$('#crosswalk-sources');target.replaceChildren();
 try{const data=await get('/api/source-crosswalk');
 $('#crosswalk-status').textContent=`ทะเบียน ${data.sources.length} source snapshots · SRC-xx คือรหัสอ้างอิงใน SRS; source_id ใช้ตามรอยชุดข้อมูล · รหัสไม่ใช่สิทธิแจกจ่าย`;
 for(const source of data.sources){const card=el('article',undefined,'source-card'),code=SOURCE_REFERENCE_CODES[source.source_id];if(code)card.append(el('span',code,'source-reference-code'));card.append(el('h3',source.source_id),el('p',source.layers.join(' / ')+' · '+number(source.observations)+' observations'),el('p',source.registry_rights_status,'muted'),el('div',source.source_sha256,'hash'));const link=el('a','เปิดแหล่งในทะเบียน ↗');link.href=source.registry_url;link.target='_blank';link.rel='noopener noreferrer';card.append(link);target.append(card);}
 }catch(error){target.replaceChildren();$('#crosswalk-status').textContent=error.message;return false;}
}

const loadedViews=new Map();
const viewLoaders={explore:()=>ensureSummary().then(load),quality:ensureSummary,sources:()=>Promise.all([ensureSummary(),loadSourceCrosswalk()]),reference:loadReference,reports:loadReports,nso:()=>Promise.all([loadNso(),loadNsoComparison()]),inventory:loadInventory,'case-study':()=>window.TamsoodCaseStudy.load(),eppo:loadEppo};
function ensureLoaded(view){
 if(!viewLoaders[view])return Promise.resolve();
 if(loadedViews.has(view))return loadedViews.get(view);
 const pending=Promise.resolve().then(viewLoaders[view]).then(result=>{
  if(result===false||(Array.isArray(result)&&result.includes(false)))loadedViews.delete(view);
  return result;
 }).catch(error=>{
  loadedViews.delete(view);
  const targets={explore:'#results',quality:'#quality-content',sources:'#sources',reference:'#reference-status',reports:'#report-status',nso:'#nso-status',inventory:'#inventory-status','case-study':'#case-load-status',eppo:'#eppo-status'};
  $(targets[view]).textContent=error.message;
  return false;
 });
 loadedViews.set(view,pending);
 return pending;
}

activateView(location.hash.slice(1));
get('/healthz').catch(()=>{});


$('#nso-demo-example').addEventListener('click',()=>{$('#nso-table').value='13.6';$('#nso-year').value='2024';$('#nso-search').value='ดีเซล';renderNso();});

// Plain-language help and choices change queries only, never source observations.
const UX_TERMS=[
 ['LCI','บัญชีรายการสิ่งเข้า–ออก','Life Cycle Inventory','ข้อมูลวัตถุดิบ พลังงาน ผลผลิต และสิ่งที่ปล่อยออก ภายใต้ขอบเขตที่ระบุ ข้อมูลตรงเอกสารยังไม่แปลว่าเป็นบัญชีครบวงจร'],
 ['FAME','ไบโอดีเซลชนิดเมทิลเอสเทอร์','Fatty Acid Methyl Ester','ในชุดงานวิจัยนี้เป็นขั้นผลิตไบโอดีเซลจากน้ำมันปาล์ม มีข้อมูลวัตถุดิบ พลังงาน และผลผลิตตามตาราง'],
 ['H-FAME','ไบโอดีเซลที่เติมไฮโดรเจน','Hydrogenated FAME in this study','เชื้อเพลิงที่ได้จากการเติมไฮโดรเจนให้ FAME ตามงานวิจัยนี้ เป็นข้อมูลโรงงานนำร่อง ไม่ใช่ค่าเฉลี่ยประเทศไทย'],
 ['FFB','ทะลายปาล์มสด','Fresh Fruit Bunch','ผลปาล์มที่เก็บเกี่ยวพร้อมทะลาย ในชุดต้นน้ำใช้อ้างอิงการผลิต 1,000 กิโลกรัม'],
 ['CPO','น้ำมันปาล์มดิบ','Crude Palm Oil','น้ำมันที่สกัดจากผลปาล์ม ก่อนขั้นกลั่น ในหมวดเชื้อเพลิงชีวภาพนี้ไม่ได้หมายถึงชื่อผู้ประกอบการในชุดน้ำมันและก๊าซ'],
 ['RBDPO','น้ำมันปาล์มที่ผ่านการกลั่น ฟอกสี และกำจัดกลิ่น','Refined, Bleached and Deodorized Palm Oil','ผลิตภัณฑ์หลังปรับคุณภาพน้ำมันปาล์มดิบ เป็นวัตถุดิบของขั้นผลิตไบโอดีเซลในงานวิจัย'],
 ['FU','หน่วยหน้าที่ที่ใช้เปรียบเทียบ','Functional Unit','ระบุว่าศึกษาบริการอะไรและปริมาณเท่าไร งานวิจัยเชื้อเพลิงนี้ใช้การใช้เชื้อเพลิง 1,000 MJ ส่วนตารางต้นน้ำมีฐานผลิตภัณฑ์ของตัวเอง'],
 ['BOUNDARY','ขอบเขตระบบ','System Boundary','บอกว่ารวมขั้นตอนไหนและยังไม่รวมอะไร เช่น มีขั้นแปรรูป แต่ยังไม่ได้นำเข้าข้อมูลขนส่งหรือการใช้ในรถ'],
 ['ALLOCATION','การแบ่งภาระระหว่างผลิตร่วม','Allocation','เมื่อกระบวนการเดียวได้หลายผลิตภัณฑ์ ต้องระบุวิธีแบ่งวัตถุดิบ พลังงาน หรือภาระให้แต่ละผลิตภัณฑ์ ไม่คูณสัดส่วนซ้ำถ้าตารางจัดสรรมาแล้ว'],
 ['NSO','สำนักงานสถิติแห่งชาติ','National Statistical Office','เจ้าของรายงานสถิติรายปีที่เราใช้เป็นข้อมูลบริบทระดับประเทศ','สสช. สสช'],
 ['EPPO','สำนักงานนโยบายและแผนพลังงาน','Energy Policy and Planning Office','แหล่งเผยแพร่สถิติพลังงานและโรงกลั่น ในบางชุดหน่วยงานต้นทางเป็นกรมธุรกิจพลังงาน','สนพ. สนพ'],
 ['DOEB','กรมธุรกิจพลังงาน','Department of Energy Business','หน่วยงานต้นทางของสถิติน้ำมันบางชุดที่เผยแพร่ผ่านเว็บไซต์พลังงาน'],
 ['MTEC','ศูนย์เทคโนโลยีโลหะและวัสดุแห่งชาติ','National Metal and Materials Technology Center','หน่วยงานที่เกี่ยวข้องกับโจทย์โครงงานนี้ การนำข้อมูลมาใช้ในเว็บไม่ได้หมายถึงได้รับการรับรองจากหน่วยงาน','เอ็มเทค'],
 ['SPRC','บริษัทสตาร์ปิโตรเลียมรีไฟน์นิ่ง','Star Petroleum Refining Public Company Limited','บริษัทเจ้าของรายงานที่ใช้เป็นข้อมูลอ้างอิงระดับองค์กรในเว็บนี้ ไม่ใช่ชื่อชนิดเชื้อเพลิง'],
 ['THAIOIL','บริษัทไทยออยล์','Thai Oil Public Company Limited','บริษัทเจ้าของรายงานด้านพลังงานและน้ำที่เราใช้เป็นข้อมูลอ้างอิงระดับองค์กร'],
 ['DMF','กรมเชื้อเพลิงธรรมชาติ','Department of Mineral Fuels','แหล่งข้อมูลการผลิตน้ำมันดิบ คอนเดนเสท และก๊าซ แยกตามแหล่งผลิต'],
 ['LPG','ก๊าซปิโตรเลียมเหลว','Liquefied Petroleum Gas','เชื้อเพลิงกลุ่มโพรเพนและบิวเทน ต้องอ่านหน่วยที่แต่ละตารางรายงานก่อนนำค่าไปเปรียบเทียบ'],
 ['CONDENSATE','คอนเดนเสท','Condensate','ไฮโดรคาร์บอนเหลวที่แยกออกมาพร้อมก๊าซธรรมชาติ เป็นคนละผลิตภัณฑ์กับน้ำมันดิบในชุดข้อมูลนี้'],
 ['COKE','โค้กปิโตรเลียม','Petroleum coke','วัสดุเชื้อเพลิงคาร์บอนแข็งที่เกิดจากกระบวนการกลั่นน้ำมัน อ่านตามบริบทของรายงานโรงกลั่น'],
 ['MJ','เมกะจูล: หน่วยพลังงาน','Megajoule','ใช้บอกปริมาณพลังงาน ไม่ใช่น้ำหนักเชื้อเพลิง จึงไม่เปลี่ยนเป็นกิโลกรัมโดยไม่มีข้อมูลสมบัติเชื้อเพลิง'],
 ['GJ/t throughput','พลังงานต่อหนึ่งตันที่ผ่านกระบวนการ','Gigajoule per tonne throughput','ตัวหารเป็นปริมาณที่ผ่านกระบวนการโรงกลั่นตามรายงาน ไม่ใช่ผลิตภัณฑ์อ้างอิงของ LCI โดยอัตโนมัติ'],
 ['ktoe','พันตันเทียบเท่าน้ำมันดิบ','Thousand tonnes of oil equivalent','หน่วยเทียบปริมาณพลังงานในสถิติ ไม่ใช่น้ำหนักน้ำมันดิบที่ผลิตจริง'],
 ['m3','ลูกบาศก์เมตร: หน่วยปริมาตร','Cubic metre / m³','ใช้บอกปริมาตร เช่น น้ำหรือก๊าซ ต้องอ่านว่าตารางวัดอะไร ไม่เปลี่ยนเป็นกิโลกรัมโดยไม่มีสมบัติของสาร'],
 ['kWh','กิโลวัตต์ชั่วโมง: หน่วยพลังงานไฟฟ้า','Kilowatt-hour','ใช้บอกพลังงานไฟฟ้าที่ใช้หรือผลิต ต้องอ่านทิศทางเข้า–ออกของรายการด้วย'],
 ['CHP','การผลิตไฟฟ้าและความร้อนร่วม','Combined Heat and Power','ระบบที่ผลิตไฟฟ้าและนำความร้อนมาใช้ด้วย คำว่า biomass ในรายการหมายถึงชีวมวล ต้องอ่านหมายเหตุของค่าต้นฉบับประกอบ'],
 ['BBL/DAY','บาร์เรลต่อวัน','Barrels per day','เป็นอัตราปริมาณต่อเวลา ต่างจากปริมาณรวมล้านลิตรในอีกตาราง จึงห้ามนำสองชุดมาหารเป็นอัตราผลผลิตรายโรงกลั่นเอง'],
 ['HOLD','พักข้อมูลไว้ทบทวน','Hold / context review','ยังมีข้อจำกัด เช่น ไม่มีหน่วยหรือบริบทขัดกัน ไม่ได้แปลว่าค่าคือศูนย์ และไม่ควรนำไปคำนวณเหมือนข้อมูลพร้อมใช้'],
 ['CSV','ไฟล์ตารางสำหรับเปิดตรวจ','Comma-separated values','เปิดเป็นตารางได้ในโปรแกรมตารางคำนวณ แต่ต้องอ่านหน่วย ปี และหลักฐานประกอบก่อนใช้'],
 ['JSON','ไฟล์ข้อมูลมีโครงสร้าง','JavaScript Object Notation','เก็บค่าพร้อมชื่อช่องและข้อมูลอ้างอิง ใช้ส่งต่อให้โปรแกรมได้ ไฟล์ทบทวนของเรายังไม่ใช่รูปแบบนำเข้าเครื่องมือ LCA ที่ทดสอบแล้ว']
];
function matchingTerms(query){const q=query.trim().toLocaleLowerCase();return UX_TERMS.filter(term=>term.join(' ').toLocaleLowerCase().includes(q));}
function openTerms(query=''){
 const content=$('#detail-content');content.replaceChildren(el('h2','คำศัพท์และตัวย่อในเว็บ','detail-title'),el('p','อ่านความหมายก่อนใช้ข้อมูล · คำอธิบายนี้ใช้กับบริบทของชุดข้อมูลในเว็บ'));
 const label=el('label','ค้นหาความหมาย'),input=el('input');input.type='search';input.placeholder='เช่น FAME, โค้ก, หน่วยพลังงาน';input.value=query;label.append(input);
 const status=el('p',undefined,'muted');status.setAttribute('role','status');const list=el('div',undefined,'glossary-list');
 const render=()=>{const terms=matchingTerms(input.value);list.replaceChildren();status.textContent=terms.length?'พบ '+terms.length+' คำ':'ยังไม่มีคำนี้ ลองค้นชื่อเต็มหรือเปิดดูทุกคำ';for(const [code,title,english,meaning] of terms){const card=el('article',undefined,'glossary-entry');card.append(el('h3',title+' ('+code+')'),el('small',english),el('p',meaning));list.append(card);}};
 input.addEventListener('input',render);content.append(label,status,list);render();if(!$('#detail').open)$('#detail').showModal();input.focus();
}
$('#terms-open').addEventListener('click',()=>openTerms());
document.querySelectorAll('[data-term]').forEach(button=>button.addEventListener('click',()=>openTerms(button.dataset.term)));
function fillChoices(select,options,placeholder='ทุกรายการ / หรือพิมพ์เอง'){
 if(!select)return;const previous=select.value;select.replaceChildren();const first=el('option',placeholder);first.value='';select.append(first);
 const seen=new Set();for(const [value,label] of options){if(!value||seen.has(value))continue;seen.add(value);const option=el('option',label);option.value=value;select.append(option);}select.value=seen.has(previous)?previous:'';
}
function populateNsoChoices(){if(!nsoData)return;const rows=nsoData.rows.filter(r=>r.table_id===$('#nso-table').value);fillChoices($('#nso-topic'),[...new Set(rows.map(r=>r.label))].sort((a,b)=>a.localeCompare(b,'th')).map(label=>[label,label]));}
const refFriendly={'Coke':'โค้กปิโตรเลียม','Diesel':'น้ำมันดีเซล','Electricity consumption':'การใช้ไฟฟ้า','Electricity purchased from external source':'ไฟฟ้าซื้อจากภายนอก','Electricity sold (4)':'ไฟฟ้าที่ขายออก','Fuel gas':'ก๊าซเชื้อเพลิง','Fuel oil':'น้ำมันเตา','Natural gas':'ก๊าซธรรมชาติ','Refinery energy intensity':'พลังงานต่อปริมาณที่ผ่านโรงกลั่น','Refinery throughput (1)':'ปริมาณที่ผ่านกระบวนการโรงกลั่น','Total energy consumption  (2)':'การใช้พลังงานรวม','Total fuel consumption  (2)':'การใช้เชื้อเพลิงรวม'};
let referenceChoicesPending=null,referenceChoicesLoaded=false;
function ensureReferenceChoices(){
 if(referenceChoicesLoaded)return Promise.resolve(true);if(referenceChoicesPending)return referenceChoicesPending;
 referenceChoicesPending=get('/api/reference.json?decision=all').then(data=>{const options=[...new Set(data.rows.map(r=>r.label))].map(label=>[label,refFriendly[label]?refFriendly[label]+' ('+label+')':label]);fillChoices($('#reference-topic'),options);referenceChoicesLoaded=true;return true;}).catch(()=>{fillChoices($('#reference-topic'),[],'ตัวเลือกยังโหลดไม่ได้ · พิมพ์ค้นหาได้');return false;}).finally(()=>{referenceChoicesPending=null;});return referenceChoicesPending;
}
const eppoChoices={
 '11_13':[['THAI OIL','ไทยออยล์ (THAI OIL)'],['SPRC','สตาร์ปิโตรเลียมรีไฟน์นิ่ง (SPRC)'],['BANGCHAK','บางจาก (BANGCHAK)'],['ESSO','ESSO — ชื่อตามข้อมูลต้นฉบับ'],['FANG','โรงกลั่นฝาง (FANG)'],['RPC','RPC — ชื่อตามข้อมูลต้นฉบับ'],['RRC / PTTAR / PTTGC','RRC / PTTAR / PTTGC — กลุ่มชื่อในข้อมูล'],['TPI / IRPC','TPI / IRPC — กลุ่มชื่อในข้อมูล']],
 '11_14':[['DIESEL','น้ำมันดีเซล (DIESEL)'],['FUEL OIL','น้ำมันเตา (FUEL OIL)'],['GASOLINE','น้ำมันเบนซิน (GASOLINE)'],['JET PETROLEUM','เชื้อเพลิงอากาศยาน (JET PETROLEUM)'],['KEROSENE','น้ำมันก๊าด (KEROSENE)'],['LPG','ก๊าซปิโตรเลียมเหลว (LPG)']]
};
function populateEppoChoices(){fillChoices($('#eppo-topic'),eppoChoices[$('#eppo-filters [name="dataset"]').value]||[]);}
$('#catalog-topic').addEventListener('change',()=>{$('#catalog-search').value=$('#catalog-topic').value;$('#catalog-level').value='';filterCatalog();});
$('#catalog-search').addEventListener('input',()=>{$('#catalog-topic').value='';});
$('#catalog-reset').addEventListener('click',()=>{$('#catalog-topic').value='';});
$('#dmf-topic').addEventListener('change',()=>{$('#search').value=$('#dmf-topic').value;state.page=1;load();});
$('#search').addEventListener('input',()=>{$('#dmf-topic').value='';});
$('#reference-topic').addEventListener('change',()=>{$('#reference-filters [name="q"]').value=$('#reference-topic').value;referenceState.page=1;loadReference();});
$('#reference-filters [name="q"]').addEventListener('input',()=>{$('#reference-topic').value='';});
$('#reference-reset').addEventListener('click',()=>{$('#reference-topic').value='';});
$('#nso-topic').addEventListener('change',()=>{$('#nso-search').value=$('#nso-topic').value;renderNso();});

// Friendly statistics: visual cues support labels; source values are never rewritten.
(function(root){
 const categories=[
  {pattern:/ไบโอดีเซล|biodiesel|\bfame\b/i,emoji:'🌿',tone:'mint'},
  {pattern:/ไฟฟ้า|electricity/i,emoji:'⚡',tone:'amber'},
  {pattern:/แก๊สโซฮอล์|ก๊าซโซฮอล์|gasohol|เบนซิน|gasoline/i,emoji:'⛽',tone:'amber'},
  {pattern:/ก๊าซ|แก๊ส|\bgas\b|\blpg\b|\blng\b/i,emoji:'🔥',tone:'violet'},
  {pattern:/น้ำเสีย|น้ำจืด|น้ำดิบ|น้ำใช้|water/i,emoji:'💧',tone:'blue'},
  {pattern:/ถ่านหิน|โค้ก|coal|coke/i,emoji:'🪨',tone:'slate'},
  {pattern:/น้ำมันดิบ|crude/i,emoji:'🛢️',tone:'rose'},
  {pattern:/ดีเซล|เบนซิน|น้ำมันเตา|diesel|gasoline|fuel oil/i,emoji:'⛽',tone:'amber'}];
 function fuelCue(label){return categories.find(c=>c.pattern.test(label))||null;}
 function summaryFacts(rows){
  const years=[...new Set(rows.flatMap(r=>String(r.period).match(/(?:19|20)\d{2}/g)||[]))].sort();
  const units=[...new Set(rows.map(r=>r.unit).filter(Boolean))];
  return {count:rows.length,period:years.length?(years[0]===years.at(-1)?years[0]:years[0]+'–'+years.at(-1)):'—',units:units.length===1?units[0]:units.length?units.length+' หน่วย':'—',mixedUnits:units.length>1};
 }
 if(typeof module==='object'&&module.exports)module.exports={fuelCue,summaryFacts};
 if(!root.document||!root.MutationObserver)return;
 const doc=root.document;
 const node=(tag,text,cls)=>{const n=doc.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
 function syncChoices(){
  doc.querySelectorAll('[data-stat-table]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.statTable===doc.querySelector('#nso-table').value)));
  doc.querySelectorAll('[data-stat-eppo]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.statEppo===doc.querySelector('#eppo-filters [name="dataset"]').value)));
 }
 function update(which){
  const tbody=doc.querySelector('#'+which+'-rows'),container=doc.querySelector('#'+which+'-stat-summary');
  if(!tbody||!container)return;
  const rows=[];
  tbody.querySelectorAll('tr').forEach(tr=>{
   const cells=tr.querySelectorAll('td');if(cells.length!==4)return;
   const label=cells[0].textContent,unit=cells[2].querySelector('small')?.textContent||'';
   rows.push({period:cells[1].textContent,unit});
   if(!cells[0].querySelector('.fuel-symbol')){
    const cue=fuelCue(label);if(cue){const icon=node('span',cue.emoji,'fuel-symbol tone-'+cue.tone);icon.setAttribute('aria-hidden','true');cells[0].prepend(icon);}
   }
  });
  container.hidden=!rows.length;
  const facts=summaryFacts(rows);container.replaceChildren();
  const items=[['🔎',String(facts.count),which==='eppo'?'รายการในหน้านี้':'รายการที่ตรงตัวกรอง','เป็นจำนวนค่าที่แสดง ไม่ใช่ปริมาณเชื้อเพลิง'],['📅',facts.period,'ช่วงปีที่กำลังดู',which==='eppo'?'ช่วงของข้อมูลในหน้านี้':'ตามตัวกรองและตารางที่เลือก'],['📐',facts.units,'หน่วยตามต้นฉบับ',facts.mixedUnits?'มีหลายหน่วย อ่านแยกกัน ไม่บวกรวม':'ตัวเลขทุกค่าคงหน่วยเดิม']];
  items.forEach(([emoji,value,label,note],i)=>{
   const card=node('article',undefined,'stat-summary-card stat-accent-'+i),icon=node('span',emoji,'stat-summary-icon');icon.setAttribute('aria-hidden','true');
   const text=node('div');text.append(node('p',label,'stat-summary-label'),node('strong',value),node('small',note));card.append(icon,text);container.append(card);
  });syncChoices();
 }
 doc.querySelectorAll('[data-stat-table]').forEach(b=>b.addEventListener('click',()=>{
  const select=doc.querySelector('#nso-table');select.value=b.dataset.statTable;select.dispatchEvent(new Event('change',{bubbles:true}));syncChoices();
 }));
 doc.querySelectorAll('[data-stat-eppo]').forEach(b=>b.addEventListener('click',()=>{
  const select=doc.querySelector('#eppo-filters [name="dataset"]');select.value=b.dataset.statEppo;select.dispatchEvent(new Event('change',{bubbles:true}));doc.querySelector('#eppo-filters [name="q"]').value='';doc.querySelector('#eppo-filters').requestSubmit();syncChoices();
 }));
 ['nso','eppo'].forEach(which=>{
  const tbody=doc.querySelector('#'+which+'-rows');
  if(tbody){new root.MutationObserver(()=>update(which)).observe(tbody,{childList:true});update(which);}
 });syncChoices();
})(typeof window==='undefined'?globalThis:window);
$('#nso-search').addEventListener('input',()=>{$('#nso-topic').value='';});
$('#nso-reset').addEventListener('click',()=>{$('#nso-topic').value='';});
$('#nso-demo-example').addEventListener('click',()=>{$('#nso-topic').value='';});
$('#eppo-topic').addEventListener('change',()=>{$('#eppo-filters [name="q"]').value=$('#eppo-topic').value;eppoState.page=1;loadEppo();});
$('#eppo-filters [name="q"]').addEventListener('input',()=>{$('#eppo-topic').value='';});
$('#eppo-filters [name="dataset"]').addEventListener('change',()=>{$('#eppo-filters [name="q"]').value='';$('#eppo-topic').value='';populateEppoChoices();eppoState.page=1;loadEppo();});
$('#eppo-reset').addEventListener('click',()=>{populateEppoChoices();$('#eppo-topic').value='';});
populateEppoChoices();

// Finite motion responds to actions; values are never animated or rewritten.
(function(root){
 function play(element,frames,options){
  if(!element||typeof element.animate!=='function'||root.matchMedia?.('(prefers-reduced-motion: reduce)').matches)return false;
  element.getAnimations?.().forEach(animation=>animation.cancel());
  element.animate(frames,options);return true;
 }
 if(typeof module!=='undefined'&&module.exports)module.exports.motionPlay=play;
 const doc=root.document;if(!doc||!root.MutationObserver)return;
 const enter=element=>play(element,[{opacity:.35,transform:'translateY(9px)'},{opacity:1,transform:'translateY(0)'}],{duration:260,easing:'cubic-bezier(.2,.7,.2,1)'});
 doc.querySelectorAll('[id^="view-"]').forEach(view=>{
  new root.MutationObserver(()=>{if(!view.hidden)enter(view);}).observe(view,{attributes:true,attributeFilter:['hidden']});
 });
 doc.querySelectorAll('.stat-summary').forEach(summary=>{
  new root.MutationObserver(()=>{
   if(summary.hidden)return;
   summary.querySelectorAll('.stat-summary-card').forEach((card,index)=>play(card,[{opacity:.4,transform:'translateY(7px)'},{opacity:1,transform:'translateY(0)'}],{duration:220,delay:index*35,easing:'ease-out'}));
  }).observe(summary,{childList:true});
 });
 doc.addEventListener('click',event=>{
  const button=event.target.closest?.('.stat-topic-nav button,.case-process,#nso-demo-example');
  if(button&&!button.disabled)play(button,[{transform:'scale(1)'},{transform:'scale(.96)',offset:.3},{transform:'scale(1)'}],{duration:230,easing:'ease-out'});
 });
})(typeof window==='undefined'?globalThis:window);
