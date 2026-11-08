const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../web/api.js'),'utf8');
function setup(base='',fetcher=async()=>({ok:true,headers:{get:()=> 'application/json'},json:async()=>({ok:true})}),extra={}){
 const events=[];
 const window={TAMSOOD_CONFIG:{apiBaseUrl:base,...extra},location:{origin:'http://127.0.0.1:8765'},dispatchEvent:e=>events.push(e.detail.state)};
 vm.runInNewContext(source,{window,URL,AbortController,setTimeout,clearTimeout,TypeError,
   CustomEvent:class{constructor(name,options){this.detail=options.detail;}},fetch:fetcher});
 return {api:window.TamsoodAPI,events};
}
(async()=>{
 const remote=setup('https://api.example.com');
 assert.equal(remote.api.url('/api/reference.csv?q=water'),'https://api.example.com/api/reference.csv?q=water');
 assert.equal((await remote.api.get('/api/reference')).ok,true);
 assert.deepEqual(remote.events,['loading','connected']);
 assert.equal(setup().api.url('/api/nso'),'http://127.0.0.1:8765/api/nso');
 for(const base of ['http://example.com','https://user:secret@example.com','https://example.com/api','https://example.com/?key=secret']){
  const value=setup(base);assert(value.api.configurationError);await assert.rejects(value.api.get('/api/nso'));
 }
 for(const target of ['https://evil.example/api/data','/api/../.local/secret'])assert.throws(()=>remote.api.url(target));
 const html=setup('',async()=>({ok:true,headers:{get:()=> 'text/html'},json:()=>{throw Error('must not parse HTML');}}));
 await assert.rejects(html.api.get('/api/reference'),/ปลายทางไม่ใช่ API/);
 const timeout=setup('',(url,{signal})=>new Promise((resolve,reject)=>signal.addEventListener('abort',()=>{const error=Error('aborted');error.name='AbortError';reject(error);})));
 await assert.rejects(timeout.api.get('/api/nso',5),/ตอบช้าเกินไป/);
 const offline=setup('',async()=>{throw TypeError('Network failed');});
 await assert.rejects(offline.api.get('/api/nso'),/เชื่อมต่อ backend ไม่ได้/);
 const login=setup('',async()=>({status:401}),{loginUrl:'/api/login'});
 await assert.rejects(login.api.get('/api/reference'),/เข้าสู่ระบบ/);
 assert.deepEqual(login.events,['loading','unauthorized']);
 console.log('PASS: API origin/export URLs, unsafe configuration, HTML fallback, timeout and network errors');
})().catch(error=>{console.error(error);process.exitCode=1;});
