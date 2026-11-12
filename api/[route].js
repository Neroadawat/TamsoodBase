// Vercel same-origin read proxy. Upstream credentials stay in server-only env.
const https = require('node:https');
const routes = new Set(['model','release','summary','source-crosswalk','reports','report-pilot','nso','product-inventory','nso-comparison','reference','reference.json','reference.csv','records','record','eppo','export','login','readyz','healthz']);
// Public deployments must not proxy dataset rows until source and record rights
// are normalized and cleared. Service-to-service Basic Auth is not user auth.
const publicSafeRoutes = new Set(['model','release','readyz','healthz']);
const MAX_BUFFER_BYTES=4*1024*1024,MAX_EXPORT_BYTES=32*1024*1024;
function compactNso(data){
  if(!Array.isArray(data.rows))throw Error('Invalid statistics payload');
  const keys=['notes','status','data_kind','geography','publisher','source_url','rights_status','source_sha256','publication_year','originating_agency','is_normalized_lci_exchange'];
  const contexts=[],seen=new Map();
  const rows=data.rows.map(row=>{
    if(Object.hasOwn(row,'_context'))throw Error('Reserved context key');
    const context=Object.fromEntries(keys.filter(k=>Object.hasOwn(row,k)).map(k=>[k,row[k]]));
    const key=JSON.stringify(context);if(!seen.has(key)){seen.set(key,contexts.length);contexts.push(context);}
    return {...Object.fromEntries(Object.entries(row).filter(([k])=>!keys.includes(k))),_context:seen.get(key)};
  });
  return {...data,transport_profile:'NSO_DEDUP_V1',contexts,rows};
}
function publicReference(data){
  if(!Array.isArray(data.rows))throw Error('Invalid reference projection');
  const fields=['observation_id','label','publisher','data_kind','aggregation_role','reference_year','unit_code','decision','source_url','pdf_page','printed_page','source_page','source_table','source_column','source_metric_id','pdf_sha256','source_sha256','redistribution_status'];
  return {total:data.total,page:data.page,page_size:data.page_size,distribution_profile:'PUBLIC_REFERENCE_METADATA_V1',quantities_withheld:true,
    manifest:Object.fromEntries(['release_id','accepted_reference','held_context','reextracted_pdf_records'].map(k=>[k,data.manifest?.[k]??null])),
    fields:[...fields,'scaled_amount'],rows:data.rows.map(row=>({...Object.fromEntries(fields.filter(k=>Object.hasOwn(row,k)).map(k=>[k,row[k]])),scaled_amount:'ไม่เปิดเผยปริมาณ · ดูต้นฉบับ',redistribution_status:row.redistribution_status||'NOT_CLEARED'}))};
}

function origin() {
  const u = new URL(process.env.TAMSOOD_BACKEND_ORIGIN || '');
  const valid=v=>v.protocol==='https:'&&!v.username&&!v.password&&v.pathname==='/'&&!v.search&&!v.hash&&!v.port
    &&!require('node:net').isIP(v.hostname)&&!v.hostname.startsWith('[')&&v.hostname!=='localhost'
    &&!v.hostname.endsWith('.localhost')&&!v.hostname.endsWith('.local')&&!v.hostname.endsWith('.internal')&&!v.hostname.includes('*');
  if(!valid(u))throw Error('Invalid protected backend origin');
  const configured=process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS;
  if(configured){
    const allowed=JSON.parse(configured);
    if(!Array.isArray(allowed)||!allowed.length||allowed.length>8||allowed.some(value=>typeof value!=='string'||!valid(new URL(value))||new URL(value).origin!==value)||!allowed.includes(u.origin))throw Error('Backend origin is not explicitly allowed');
  }else if(!u.hostname.endsWith('.trycloudflare.com'))throw Error('Permanent backend needs an explicit origin allowlist');
  return u.origin;
}
function handler(req,res) {
  res.setHeader('Cache-Control','private, no-store');
  res.setHeader('X-Content-Type-Options','nosniff');
  let failed=false, deadline;
  const fail=(code,message)=>{if(failed||res.writableEnded)return;failed=true;clearTimeout(deadline);if(res.headersSent){res.destroy();return;}res.statusCode=code;res.setHeader('Content-Type','application/json');res.end(JSON.stringify({error:message}));};
  const url=new URL(req.url,'https://local.invalid');
  const route=['/readyz','/healthz'].includes(url.pathname)?url.pathname.slice(1):url.pathname.replace(/^\/api\//,'');
  if(!routes.has(route))return fail(404,'Unknown API route');
  if(!['GET','HEAD'].includes(req.method))return fail(405,'Read-only API');
  if(req.url.length>8192)return fail(414,'Request URL too long');
  if(!publicSafeRoutes.has(route))return fail(403,'ข้อมูลชุดนี้ยังไม่เปิดผ่านเว็บไซต์ระหว่างตรวจสอบสิทธิ์เผยแพร่');
  if(route==='model'||route==='release'){
    const metadata=require('../web/case-study.json');
    if(metadata.private_inventory_included!==false||metadata.full_lifecycle_inventory!==false)return fail(503,'Unreviewed model projection');
    const body=route==='model'?metadata:{scope:'FRONTEND_MODEL_IDENTITY_NOT_BACKEND_READINESS',model_release_id:metadata.model_release_id,metadata_snapshot_id:metadata.metadata_snapshot_id};
    res.statusCode=200;res.setHeader('Content-Type','application/json; charset=utf-8');return res.end(req.method==='HEAD'?undefined:JSON.stringify(body));
  }
  if(['reports','report-pilot','reference.csv'].includes(route))return fail(403,'Research quantities are not cleared for public distribution. Use source links and reference metadata JSON.');
  const authorization=process.env.TAMSOOD_BACKEND_AUTH||'';
  if(!authorization.startsWith('Basic ') || authorization.length>4096){
    return fail(503,'Backend connection not configured');
  }
  let base;try{base=origin();}catch{return fail(503,'Backend not configured');}
  const target=new URL(route==='login'?'/healthz':['healthz','readyz'].includes(route)?'/'+route:'/api/'+route,base);
  target.search=url.search;
  if(route==='nso')target.searchParams.delete('profile');
  const upstream=https.request(target,{method:req.method,headers:{Authorization:authorization,Accept:req.headers.accept||'application/json'},timeout:30000},response=>{
    if(failed||res.writableEnded){response.destroy();return;}
    if(response.statusCode>=300 && response.statusCode<400){response.resume();return fail(502,'Unexpected backend redirect');}
    if(response.statusCode===401){response.resume();return fail(503,'Backend connection needs updating');}
    if(route==='login'){
      response.resume();
      if(response.statusCode!==200)return fail(503,'Backend unavailable');
      res.statusCode=303;res.setHeader('Location','/');return res.end();
    }
    if(route==='export'){
      const advertised=Number(response.headers['content-length']);
      if(Number.isFinite(advertised)&&advertised>MAX_EXPORT_BYTES){response.resume();return fail(502,'Export too large; narrow the filters');}
      res.statusCode=response.statusCode;
      for(const key of ['content-type','content-disposition'])if(response.headers[key])res.setHeader(key,response.headers[key]);
      if(req.method==='HEAD'){response.resume();return res.end();}
      let bytes=0;
      response.on('data',chunk=>{bytes+=chunk.length;if(bytes>MAX_EXPORT_BYTES){response.unpipe(res);response.destroy();fail(502,'Export too large; narrow the filters');}});
      response.on('error',()=>fail(502,'Backend connection interrupted'));
      response.pipe(res);return;
    }
    const chunks=[];let size=0;
    response.on('data',chunk=>{if(failed)return;size+=chunk.length;if(size>MAX_BUFFER_BYTES){response.destroy();return fail(502,'Response too large; narrow the filters');}chunks.push(chunk);});
    response.on('end',()=>{
      if(failed||res.writableEnded)return;
      res.statusCode=response.statusCode;
      for(const key of ['content-type','content-disposition'])if(response.headers[key])res.setHeader(key,response.headers[key]);
      let body=Buffer.concat(chunks);
      if(route==='nso'&&url.searchParams.get('profile')==='explorer-v1'&&response.statusCode===200){
        try{body=Buffer.from(JSON.stringify(compactNso(JSON.parse(body.toString('utf8')))));}
        catch{return fail(502,'Invalid statistics projection');}
      }
      if(['reference','reference.json'].includes(route)&&response.statusCode===200){
        try{body=Buffer.from(JSON.stringify(publicReference(JSON.parse(body.toString('utf8')))));}
        catch{return fail(502,'Invalid public reference projection');}
      }
      res.end(req.method==='HEAD'?undefined:body);
    });
    response.on('error',()=>{if(!res.writableEnded)fail(502,'Backend connection interrupted');});
  });
  const stopUpstream=()=>{
    fail(504,'Backend response deadline exceeded');
    upstream.destroy();
  };
  deadline=setTimeout(stopUpstream,28000);
  deadline.unref?.();
  res.once('finish',()=>clearTimeout(deadline));
  res.once('close',()=>{
    clearTimeout(deadline);
    if(!res.writableEnded){failed=true;upstream.destroy();}
  });
  upstream.on('timeout',stopUpstream);
  upstream.on('error',()=>{if(!res.writableEnded)fail(502,'Backend unavailable');});
  upstream.end();
}
module.exports=handler;
module.exports.origin=origin;
module.exports.publicReference=publicReference;
module.exports.compactNso=compactNso;
module.exports.limits={MAX_BUFFER_BYTES,MAX_EXPORT_BYTES};
module.exports.publicSafeRoutes=publicSafeRoutes;
