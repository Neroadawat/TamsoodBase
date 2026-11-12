const assert=require('node:assert/strict');
const {EventEmitter}=require('node:events');
const {Readable}=require('node:stream');
const https=require('node:https');
const handler=require('../api/[route].js');
process.env.TAMSOOD_BACKEND_ORIGIN='https://test.trycloudflare.com';
process.env.TAMSOOD_BACKEND_AUTH='Basic c2VydmVyOnNlY3JldA==';
delete process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS;
let seen,upstreamStatus=200,upstreamBody='{"total":97,"rows":[],"manifest":{}}',advertisedLength;
https.request=(url,options,callback)=>{
 seen={url,options};const request=new EventEmitter();request.destroy=()=>request.emit('error',Error('timeout'));
 request.end=()=>queueMicrotask(()=>{
  const response=Readable.from([Buffer.from(upstreamBody)]);response.statusCode=upstreamStatus;response.headers={'content-type':'application/json',...(advertisedLength?{'content-length':advertisedLength}:{})};callback(response);
 });return request;
};
function call(path,auth='Basic dGVhbTpwYXNz',method='GET'){
 seen=null;return new Promise(resolve=>{
  let streamed='';const response=Object.assign(new EventEmitter(),{headers:{},write(body){this.headersSent=true;streamed+=body.toString();return true;},destroy(){this.writableEnded=true;resolve({status:this.statusCode,headers:this.headers,body:streamed,destroyed:true,seen});},setHeader(k,v){assert.ok(!this.headersSent,'No header writes after streaming begins');this.headers[k.toLowerCase()]=v;},end(body){this.writableEnded=true;resolve({status:this.statusCode,headers:this.headers,body:body?.toString()||streamed,seen});}});
  handler({url:path,method,headers:auth?{authorization:auth}:{}},response);
 });
}
(async()=>{
 const projected=handler.publicReference({manifest:{release_id:'fixture',secret:'do-not-copy'},total:1,page:1,page_size:30,private:'do-not-copy',rows:[{label:'Water',scaled_amount:'123',raw_value:'123',payload:{secret:'do-not-copy'},redistribution_status:'NOT_CLEARED',source_url:'https://example.org/report.pdf'}]});
 assert.equal(projected.quantities_withheld,true);assert.equal(projected.rows[0].raw_value,undefined);assert.equal(projected.rows[0].payload,undefined);assert.equal(projected.private,undefined);assert.equal(projected.manifest.secret,undefined);assert.ok(!JSON.stringify(projected).includes('123'));
 const modelResponse=await call('/api/model',null);assert.equal(modelResponse.status,200);assert.equal(JSON.parse(modelResponse.body).private_inventory_included,false);
 const blockedRoutes=['summary','source-crosswalk','reports','report-pilot','nso','product-inventory','nso-comparison','reference','reference.json','reference.csv','records','record','eppo','export','login'];
 for(const route of blockedRoutes){const blocked=await call('/api/'+route);assert.equal(blocked.status,403,route);assert.match(blocked.body,/ยังไม่เปิดผ่านเว็บไซต์ระหว่างตรวจสอบสิทธิ์เผยแพร่/);assert.equal(blocked.seen,null,route);}
 let r=await call('/api/readyz',null);assert.equal(r.status,200);assert.equal(r.seen.options.headers.Authorization,process.env.TAMSOOD_BACKEND_AUTH);assert.ok(!r.headers['www-authenticate']);
 r=await call('/api/readyz','Basic x','POST');assert.equal(r.status,405);assert.equal(r.seen,null);
 r=await call('/api/secret');assert.equal(r.status,404);
 r=await call('/readyz');assert.equal(r.status,200);assert.equal(r.seen.url.pathname,'/readyz');
 r=await call('/api/readyz?probe=1');assert.equal(r.status,200);assert.equal(r.seen.url.href,'https://test.trycloudflare.com/readyz?probe=1');assert.equal(r.seen.options.headers.Authorization,process.env.TAMSOOD_BACKEND_AUTH);assert.equal(r.headers['cache-control'],'private, no-store');
 upstreamStatus=401;r=await call('/api/readyz');assert.equal(r.status,503);assert.ok(!r.headers['www-authenticate']);
 upstreamStatus=200;r=await call('/api/login?return=https://evil.example');assert.equal(r.status,403);assert.equal(r.headers.location,undefined);assert.equal(r.seen,null);
 upstreamStatus=302;r=await call('/api/readyz');assert.equal(r.status,502);
 upstreamBody='x'.repeat(handler.limits.MAX_BUFFER_BYTES+1);r=await call('/api/readyz');assert.equal(r.status,502);
 upstreamStatus=200;upstreamBody='{"total":97,"rows":[],"manifest":{}}';
 delete process.env.TAMSOOD_BACKEND_AUTH;r=await call('/api/readyz');assert.equal(r.status,503);assert.equal(r.seen,null);
 process.env.TAMSOOD_BACKEND_AUTH='Basic c2VydmVyOnNlY3JldA==';
 process.env.TAMSOOD_BACKEND_ORIGIN='http://127.0.0.1:22';r=await call('/api/readyz');assert.equal(r.status,503);assert.equal(r.seen,null);
 process.env.TAMSOOD_BACKEND_ORIGIN='https://api.example.com';r=await call('/api/readyz');assert.equal(r.status,503);assert.equal(r.seen,null);
 process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS='["https://api.example.com"]';r=await call('/api/readyz');assert.equal(r.status,200);assert.equal(r.seen.url.hostname,'api.example.com');
 process.env.TAMSOOD_BACKEND_ORIGIN='https://api.example.com.attacker.example';r=await call('/api/readyz');assert.equal(r.status,503);assert.equal(r.seen,null);
 for(const address of ['https://127.0.0.1','https://[::1]','https://backend.local','https://api.example.com:8443','https://user:secret@api.example.com']){
  process.env.TAMSOOD_BACKEND_ORIGIN=address;process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS=JSON.stringify([address]);
  r=await call('/api/readyz');assert.equal(r.status,503);assert.equal(r.seen,null);
 }
 process.env.TAMSOOD_BACKEND_ORIGIN='https://api.example.com';process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS='not-json';
 r=await call('/api/readyz');assert.equal(r.status,503);assert.equal(r.seen,null);
 // Exercise whole-request deadline and disconnect without waiting 28 seconds.
 process.env.TAMSOOD_BACKEND_ORIGIN='https://test.trycloudflare.com';
 delete process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS;
 let destroyed=0, expire;
 const originalTimeout=global.setTimeout;
 global.setTimeout=(fn,delay,...args)=>{
  if(delay===28000){expire=fn;return originalTimeout(()=>{},delay);}
  return originalTimeout(fn,delay,...args);
 };
 https.request=()=>{
  const request=new EventEmitter();
  request.end=()=>{};
  request.destroy=()=>{destroyed++;request.emit('error',Error('cancelled'));};
  return request;
 };
 const request={url:'/api/readyz',method:'GET',headers:{}};
 const mockResponse=()=>Object.assign(new EventEmitter(),{
  setHeader(){},end(){this.writableEnded=true;this.emit('finish');}
 });
 try{
  const timed=mockResponse();
  handler(request,timed);
  assert.equal(typeof expire,'function');
  expire();
  assert.equal(timed.statusCode,504);
  assert.equal(destroyed,1);
  const disconnected=mockResponse();
  handler(request,disconnected);
  disconnected.emit('close');
  assert.equal(destroyed,2);
  assert.equal(disconnected.writableEnded,undefined);
 }finally{global.setTimeout=originalTimeout;}
 console.log('Vercel proxy: restricted dataset APIs fail closed, safe health proxy is authenticated, origin allowlist and read-only checks passed');
})().catch(e=>{console.error(e);process.exitCode=1;});
