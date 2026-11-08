const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../web/app.js'),'utf8');
function el(tag,text,cls){return {tag,text,cls,children:[],append(...nodes){this.children.push(...nodes);}};}
const ctx={URL,el};vm.runInNewContext(source.slice(source.indexOf('function evidenceDestinations('),source.indexOf('async function openDetail(')),ctx);
const row={table_id:'13.6',source_url:'https://www.nso.go.th/table.csv',source_row:['ดีเซล','',0,'123'],source_column:3,source_line:8,source_header:'2567 (2024)'};
let links=ctx.evidenceDestinations('nso',row);assert.equal(links.length,2);assert.ok(links[0][1].includes('Page_SYB_TH.html'));assert.equal(links[1][1],row.source_url);
const preview=ctx.sourceRowPreview(row),cells=preview.children.at(-1).children.at(-1).children;
assert.equal(cells[2].cls,'source-cell selected');assert.equal(cells[2].children[1].text,'0','Numeric zero must remain visible');assert.equal(cells[1].children[1].text,'(ว่าง)');
assert.equal(ctx.evidenceDestinations('eppo',{dataset_id:'11_13',source_url:'https://catalog.eppo.go.th/data.csv'})[0][1],'https://catalog.eppo.go.th/th/dataset/dataset_11_13');
assert.equal(ctx.evidenceDestinations('dmf',{package:'production-oil',url:'https://catalog.dmf.go.th/data.csv'}).length,2);
for(const url of ['javascript:alert(1)','https://user:pass@example.com/data.csv','http://example.com/file.csv'])assert.equal(ctx.evidenceDestinations('unknown',{source_url:url}).length,0);
assert.equal(ctx.evidenceDestinations('eppo',{dataset_id:'../../unknown'}).length,0,'Unknown identifiers must not generate invented source links');
const nodes=new Map();let rendered=0;const $=key=>{if(!nodes.has(key))nodes.set(key,{value:'',addEventListener(name,fn){this[name]=fn;}});return nodes.get(key);};
vm.runInNewContext(source.slice(source.indexOf("$('#nso-demo-example').addEventListener"),source.indexOf('// Plain-language help')),{$,renderNso(){rendered++;}});

$('#nso-demo-example').click();assert.equal($('#nso-table').value,'13.6');assert.equal($('#nso-year').value,'2024');assert.equal($('#nso-search').value,'ดีเซล');assert.equal(rendered,1);
console.log('PASS: website + CSV links, locator highlight/zero preservation, safe URLs and example filter');
