const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const s=fs.readFileSync(require('node:path').join(__dirname,'../web/app.js'),'utf8');
function node(dataset={}){return {dataset,value:'',textContent:'',hidden:false,disabled:false,attributes:{},listeners:{},setAttribute(k,v){this.attributes[k]=v;},addEventListener(k,f){this.listeners[k]=f;}};}
const ids=new Map(['catalog-search','catalog-level','catalog-results','catalog-empty','catalog-reset','catalog-grid'].map(id=>['#'+id,node()]));
const cards=[node({level:'national',keywords:'oil'}),node({level:'organization',keywords:'water'}),node({level:'product',keywords:'biofuel'})];
const pills=['','national','organization','product'].map(level=>node({catalogLevel:level}));
const counts=['','national','organization','product'].map(level=>node({levelCount:level}));
const layouts=['grid','list'].map(layout=>node({catalogLayout:layout}));
const groups={'.dataset-card':cards,'[data-catalog-level]':pills,'[data-level-count]':counts,'[data-catalog-layout]':layouts};
const ctx={$:id=>ids.get(id),document:{querySelectorAll:key=>groups[key]},localStorage:{getItem:()=>{throw Error('blocked');},setItem:()=>{throw Error('blocked');}}};
vm.runInNewContext(s.slice(s.indexOf('function filterCatalog(){'),s.indexOf('const eppoState')),ctx);
assert.equal(ids.get('#catalog-grid').dataset.layout,'grid','Blocked localStorage must not break startup');
assert.equal(ids.get('#catalog-reset').disabled,true);
pills[2].listeners.click();assert.equal(ids.get('#catalog-level').value,'organization');assert.equal(cards.filter(c=>!c.hidden).length,1);assert.equal(pills[2].attributes['aria-pressed'],'true');
ids.get('#catalog-search').value='oil';ids.get('#catalog-search').listeners.input();
assert.equal(ids.get('#catalog-empty').hidden,false);assert.equal(counts[1].textContent,'1');assert.equal(counts[2].textContent,'0');
ids.get('#catalog-reset').listeners.click();assert.equal(cards.filter(c=>!c.hidden).length,3);assert.equal(ids.get('#catalog-reset').disabled,true);
layouts[1].listeners.click();assert.equal(ids.get('#catalog-grid').dataset.layout,'list');assert.equal(layouts[1].attributes['aria-pressed'],'true');
console.log('PASS: catalog filters/counts/layout/reset work even with storage blocked');
