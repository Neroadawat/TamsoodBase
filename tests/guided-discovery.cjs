const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../web/app.js'),'utf8');
const nodes=new Map(),pending=[];let requests=0,searches=0;
function node(text){return {textContent:text,value:'',children:[],listeners:{},append(...items){this.children.push(...items);},replaceChildren(...items){this.children=items;},addEventListener(event,fn){this.listeners[event]=fn;},setAttribute(){},focus(){},showModal(){this.open=true;}};}
const ctx={document:{querySelectorAll:()=>[]},$:key=>{if(!nodes.has(key))nodes.set(key,node());return nodes.get(key);},el:(tag,text)=>node(text),
 get:()=>{requests++;return new Promise((resolve,reject)=>pending.push({resolve,reject}));},filterCatalog:()=>searches++,load:()=>searches++,loadReference:()=>searches++,loadEppo:()=>searches++,renderNso:()=>searches++,state:{page:8},referenceState:{page:8},eppoState:{page:8},nsoData:null};
vm.runInNewContext(source.slice(source.indexOf('// Plain-language help'))+'\nthis.terms=matchingTerms;this.choices=eppoChoices;this.ensure=ensureReferenceChoices;this.fill=fillChoices;this.nso=populateNsoChoices;',ctx);
(async()=>{
 assert(ctx.terms('โค้ก').some(t=>t[0]==='COKE'));assert(ctx.terms('h-fame').some(t=>t[0]==='H-FAME'));assert.equal(ctx.terms('unknown-no-such-term').length,0);
 ctx.$('#eppo-filters [name="dataset"]').value='11_14';ctx.$('#eppo-filters [name="dataset"]').listeners.change();
 const actual=JSON.parse(fs.readFileSync(path.join(__dirname,'../build/eppo/report.json'),'utf8')).rows;
 for(const [dataset,options] of Object.entries(ctx.choices))for(const [value] of options)assert(actual.some(r=>r.dataset_id===dataset&&r.subject===value),'Choice must exist in retained source: '+value);
 assert.equal(ctx.$('#eppo-topic').children.length,7,'Six real product choices plus all');
 ctx.$('#eppo-topic').value='DIESEL';ctx.$('#eppo-topic').listeners.change();assert.equal(ctx.$('#eppo-filters [name="q"]').value,'DIESEL');assert.equal(ctx.eppoState.page,1);
 ctx.$('#eppo-filters [name="q"]').listeners.input();assert.equal(ctx.$('#eppo-topic').value,'','Typing must clear obsolete choice');
 const first=ctx.ensure();pending[0].reject(Error('metadata unavailable'));assert.equal(await first,false);
 const second=ctx.ensure(),same=ctx.ensure();assert.equal(requests,2,'Retry and deduplicate pending metadata');
 const references=JSON.parse(fs.readFileSync(path.join(__dirname,'../build/reusable/all-reference.json'),'utf8'));pending[1].resolve({rows:references});assert.equal(await second,true);assert.equal(await same,true);
 assert.equal(ctx.$('#reference-topic').children.length,new Set(references.map(r=>r.label)).size+1,'Include all source labels, not just first paginated response');
 await ctx.ensure();assert.equal(requests,2,'Successful metadata cached');
 const nso=JSON.parse(fs.readFileSync(path.join(__dirname,'../build/nso/report.json'),'utf8'));
 ctx.nsoData=nso;ctx.$('#nso-table').value='13.6';ctx.nso();assert.equal(ctx.$('#nso-topic').children.length,new Set(nso.rows.filter(r=>r.table_id==='13.6').map(r=>r.label)).size+1);
 ctx.$('#catalog-topic').value='FAME';ctx.$('#catalog-level').value='national';ctx.$('#catalog-topic').listeners.change();assert.equal(ctx.$('#catalog-search').value,'FAME');assert.equal(ctx.$('#catalog-level').value,'');
 console.log('PASS: understandable glossary; source-backed choices; typing/choice sync; metadata retry/cache; table-specific NSO topics');
})().catch(e=>{console.error(e);process.exitCode=1;});
