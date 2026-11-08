const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../web/app.js'),'utf8');
const start=source.indexOf('function inventorySelection('),end=source.indexOf('\nfunction renderInventory()',start);
const context={};vm.runInNewContext(source.slice(start,end)+'\nthis.select=inventorySelection;this.makeExport=inventoryExport;',context);
const rows=[{process:'FAME',direction:'INPUT',amount:'0.0012300',data_period:null,reference_amount:'1000',reference_unit:'MJ fuel'}, {process:'FAME',direction:'OUTPUT',role:'CO_PRODUCT',data_period:null,reference_amount:'1000',reference_unit:'MJ fuel'}, {process:'H-FAME',direction:'INPUT'}];
const data={rows};
assert.equal(context.select(data,'FAME','').rows.length,2);
assert.equal(context.select(data,'FAME','OUTPUT').rows[0].role,'CO_PRODUCT');
const input=context.select(data,'FAME','INPUT');assert.equal(input.rows[0].amount,'0.0012300');assert.equal(input.context.data_period,null);assert.equal(input.context.reference_amount,'1000');
assert.equal(context.select(data,'missing','').context,null);
assert.equal(context.select(data,'H-FAME','OUTPUT').rows.length,0);
const mixed={rows:[rows[0],{...rows[1],reference_unit:'kg'}]};assert.equal(context.select(mixed,'FAME','').context,null);assert.equal(context.select(mixed,'FAME','').rows.length,0);assert.ok(context.select(mixed,'FAME','').error);
assert.equal(data.rows.length,3,'Filtering must not change source rows');
const actual=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../build/product-inventory/report.json'),'utf8'));
for(const process of ['FAME','H-FAME']){
 const exported=JSON.parse(JSON.stringify(context.makeExport(actual,process,'')));
 assert.deepEqual(exported.rows,actual.rows.filter(r=>r.process===process));
 assert.equal(exported.model_ready,false);assert.equal(exported.allocation_applied,false);assert.equal(exported.licence,'CC BY 4.0');
 assert.equal(exported.measurement_period,null);
}
for(const mutate of [x=>x.rows[0].amount='',x=>x.rows[0].licence='NOT_CLEARED',x=>x.rows[0].is_newly_allocated=true,x=>x.rows[0].reference_unit='kg',x=>x.rows[0].role='CO_PRODUCT']){
 const bad=JSON.parse(JSON.stringify(actual));mutate(bad);assert.throws(()=>context.makeExport(bad,'FAME',''));
}
console.log('PASS: process/direction selection preserves source basis, decimal strings, missing period and co-product role');
