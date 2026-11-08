const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../web/app.js'),'utf8');
const start=source.indexOf('function ensureLoaded(view){'),end=source.indexOf('\nactivateView(location.hash',start);
const cache=new Map(),nodes=new Map();let calls=0,answer=false;
const context={loadedViews:cache,viewLoaders:{reference:async()=>{calls++;return answer;},nso:async()=>[{},false],reports:async()=>{throw Error('offline');}},$:id=>{if(!nodes.has(id))nodes.set(id,{});return nodes.get(id);}};
vm.runInNewContext(source.slice(start,end)+'\nthis.run=ensureLoaded;',context);
(async()=>{
 const one=context.run('reference'),two=context.run('reference');
 assert.equal(one,two,'Concurrent navigation must share one pending load');
 await one;assert.equal(calls,1);assert.equal(cache.has('reference'),false,'Failure must not be cached as loaded');
 answer={};await context.run('reference');await context.run('reference');
 assert.equal(calls,2,'Success should stay cached');
 await context.run('nso');assert.equal(cache.has('nso'),false,'A failed parallel section must allow retry');
 await context.run('reports');assert.equal(cache.has('reports'),false);assert.equal(nodes.get('#report-status').textContent,'offline');
 console.log('PASS: lazy views retry failures, cache success and deduplicate pending navigation');
})().catch(error=>{console.error(error);process.exitCode=1;});
