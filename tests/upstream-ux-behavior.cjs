const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../web/app.js'),'utf8');
const nodes=new Map();let requests=0,renders=0;
const pub=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../web/upstream-inventory.json'),'utf8'));
const ctx={URL,AbortController,setTimeout,clearTimeout,$:id=>{if(!nodes.has(id))nodes.set(id,{});return nodes.get(id);},rendered:()=>renders++,fetch:async()=>{requests++;if(requests===1)return {ok:false,headers:{get:()=>''}};return {ok:true,headers:{get:()=> 'application/json'},json:async()=>pub};}};
const start=source.indexOf('let upstreamData=null'),end=source.indexOf("document.querySelectorAll('[data-inventory-layer]')",start);
vm.runInNewContext(source.slice(start,end)+'\nrenderUpstream=()=>rendered();this.load=loadUpstream;this.select=upstreamSelection;this.makeExport=upstreamExport;this.validate=validateUpstream;',ctx);
(async()=>{
 assert.equal(await ctx.load(),false);assert.equal(nodes.get('#upstream-retry').hidden,false);
 assert.equal(await ctx.load(),true);assert.equal(nodes.get('#upstream-retry').hidden,true);
 await ctx.load();assert.equal(requests,2,'Successful snapshot reused; failed snapshot must be retryable');assert.equal(renders,2);
 const rows=[{process:'FFB',direction:'INPUT',amount:'0.48',unit:null,status:'HOLD_MISSING_UNIT'},{process:'RBDPO',direction:'INPUT',amount:'0.11',unit:'kg'},{process:'FFB',direction:'OUTPUT',amount:'1000',unit:'kg'}];
 const filtered=ctx.select({rows},'FFB','INPUT');assert.equal(filtered.length,1);assert.equal(filtered[0].unit,null);assert.equal(filtered[0].amount,'0.48');assert.equal(rows.length,3);
 const exported=JSON.parse(JSON.stringify(ctx.makeExport(pub,'FFB','INPUT')));
 assert.equal(exported.selection.exported_rows,18);assert.equal(exported.rows[0].unit,null);assert.equal(exported.rows[0].status,'HOLD_MISSING_UNIT');assert.equal(exported.model_ready,false);assert.equal(exported.source_counts.observed_cells,42);assert.equal(exported.process_profile.reference_product,'FFB');assert.equal(exported.licence,'CC BY 4.0');
 assert.deepEqual(exported.rows,pub.rows.filter(r=>r.process==='FFB'&&r.direction==='INPUT'));
 assert.equal(exported.public_snapshot_id,pub.public_snapshot_id);
 assert.equal(exported.process_profile.quality_dimensions.independent_measurement,'ไม่ได้ตรวจวัดใหม่โดยโครงงาน');
 for(const mutate of [x=>x.rows[0].reference_unit='MJ fuel',x=>x.rows[0].status='ACCEPTED',x=>x.provider_links_applied=1,x=>x.process_profiles.CPO.model_ready=true,x=>x.rows[1].observation_id=x.rows[0].observation_id]){
  const bad=JSON.parse(JSON.stringify(pub));mutate(bad);assert.throws(()=>ctx.makeExport(bad,'FFB','INPUT'));
 }
 assert.throws(()=>ctx.makeExport(pub,'unknown',''));assert.throws(()=>ctx.makeExport(pub,'FFB','TOTAL'));
 console.log('PASS: upstream retry/cache/filter preserve held units and source decimal strings');
})().catch(error=>{console.error(error);process.exitCode=1;});
