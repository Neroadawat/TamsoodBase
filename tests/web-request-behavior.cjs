// Deterministic race/failure tests with a fake DOM; no browser or live service used.
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../web/app.js'),'utf8');
const specs=[
  {name:'DMF',start:'async function load(){',end:'\nfunction item(',fn:'load',state:'state',status:'#results',rows:'#rows',links:['#export'],prev:'#previous',next:'#next',
   response:{total:0,rows:[]}},
  {name:'reference',start:'async function loadReference(){',end:"\n$('#reference-filters').addEventListener",fn:'loadReference',state:'referenceState',status:'#reference-status',rows:'#reference-rows',links:['#reference-csv','#reference-json'],prev:'#reference-previous',next:'#reference-next',
   response:{total:0,page:1,rows:[],manifest:{accepted_reference:97,held_context:4,reextracted_pdf_records:101,release_id:'fixture-release'}}},
  {name:'EPPO',start:'async function loadEppo(){',end:"\n$('#eppo-filters').addEventListener",fn:'loadEppo',state:'eppoState',status:'#eppo-status',rows:'#eppo-rows',links:[],prev:'#eppo-prev',next:'#eppo-next',
   response:{total:0,page:1,rows:[]}},
];
function harness(spec){
 const nodes=new Map(), pending=[];
 function node(){return {textContent:'old',children:['stale'],href:'old-export',disabled:false,
   replaceChildren(...children){this.children=children;},append(child){this.children.push(child);},removeAttribute(name){delete this[name];}};}
 const context={AbortController,URLSearchParams,FormData:class {},number:String,el:()=>node(),apiUrl:path=>path,ensureReferenceChoices:()=>Promise.resolve(true),
   $:id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);},params:()=>new URLSearchParams(),referenceParams:()=>new URLSearchParams(),
   get:()=>new Promise((resolve,reject)=>pending.push({resolve,reject}))};
 context[spec.state]={request:0,page:1,total:40};
 const start=source.indexOf(spec.start),end=source.indexOf(spec.end,start);
 assert(start>=0&&end>start,'Request function boundaries missing');
 vm.runInNewContext(source.slice(start,end)+'\nthis.run='+spec.fn+';',context);
 return {context,nodes,pending};
}
(async()=>{
 for(const spec of specs){
  const {context:c,pending}=harness(spec);
  const first=c.run();
  assert.equal(c.$(spec.rows).children.length,0,spec.name+' must clear old data while loading');
  for(const link of spec.links)assert.equal(c.$(link).href,undefined,'Stale export must be disabled');
  assert.equal(c.$(spec.prev).disabled,true);assert.equal(c.$(spec.next).disabled,true);
  const second=c.run();
  pending[0].reject(Error('obsolete failure'));await first;
  assert.notEqual(c.$(spec.status).textContent,'obsolete failure',spec.name+' older failure must not overwrite new search');
  pending[1].resolve(spec.response);await second;
  assert.notEqual(c.$(spec.status).textContent,'obsolete failure');
  const third=c.run();pending[2].reject(Error('current failure'));await third;
  assert.equal(c.$(spec.status).textContent,'current failure');
  assert.equal(c.$(spec.rows).children.length,0);
  assert.equal(c.$(spec.prev).disabled,true);assert.equal(c.$(spec.next).disabled,true);
  for(const link of spec.links)assert.equal(c.$(link).href,undefined);
 }
 console.log('PASS: 3 search views clear stale data/exports and ignore superseded failures');
})().catch(error=>{console.error(error);process.exitCode=1;});
