// Dependency-free static build. Only explicitly listed public web assets are copied.
import {readFile,writeFile,mkdir,copyFile,lstat,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'build','frontend');
const requested=(process.env.TAMSOOD_API_BASE_URL||'').trim();
const proxy=process.env.TAMSOOD_DEPLOY_MODE==='proxy';
if(process.env.VERCEL && !requested && !proxy)throw Error('Set TAMSOOD_API_BASE_URL or TAMSOOD_DEPLOY_MODE=proxy before building on Vercel.');
if(proxy && requested)throw Error('Proxy mode must use same-origin API routes.');
let apiBaseUrl='';
if(requested){
 const url=new URL(requested),local=['localhost','127.0.0.1','[::1]'].includes(url.hostname);
 if(url.username||url.password||url.search||url.hash||url.pathname!=='/'||!(url.protocol==='https:'||(local&&url.protocol==='http:'&&!process.env.VERCEL)))throw Error('Use an HTTPS API origin without credentials, path, query or fragment.');
 apiBaseUrl=url.origin;
}
const assets=['index.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt'];
const publicSnapshot=JSON.parse(await readFile(path.join(root,'web/upstream-inventory.json'),'utf8'));
if(publicSnapshot.scope!=='LICENSED_PUBLIC_SOURCE_REPORTED_UPSTREAM_CANDIDATES'||publicSnapshot.licence!=='CC BY 4.0'||publicSnapshot.rows.length!==42||publicSnapshot.raw_document_included!==false)throw Error('Unreviewed public snapshot');
const caseStudy=JSON.parse(await readFile(path.join(root,'web/case-study.json'),'utf8'));
const publicCaseKeys=new Set(['scope','schema_version','model_release_id','review_date','functional_unit','calculated_scope','full_lifecycle_inventory','CO2e_total','private_inventory_included','calculation_type','selection_note','cases','components','open_decisions','public_activity_kg','activity_source','verification','disclosure','metadata_snapshot_id']);
if(caseStudy.scope!=='PUBLIC_CASE_STUDY_METADATA_NO_RESTRICTED_INVENTORY'||caseStudy.private_inventory_included!==false||caseStudy.full_lifecycle_inventory!==false||caseStudy.CO2e_total!==null||Object.keys(caseStudy).some(k=>!publicCaseKeys.has(k))||Object.keys(caseStudy.public_activity_kg).sort().join(',')!=='CPO,RBDPO')throw Error('Unreviewed or restricted case-study projection');
function forbidPrivate(value){if(!value||typeof value!=='object')return;for(const [key,item] of Object.entries(value)){if(['rows','observations','raw_value','payload_json','scaled_amount','FFB'].includes(key))throw Error('Private case inventory must not enter public assets');forbidPrivate(item);}}
forbidPrivate(caseStudy);
try { if((await lstat(output)).isSymbolicLink())throw Error('Output cannot be a symlink'); }
catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(output,{recursive:true});
const expectedNames=new Set([...assets,'config.js','build-manifest.json']);
for(const entry of await readdir(output,{withFileTypes:true})){
 if(!entry.isFile()||entry.isSymbolicLink()||!expectedNames.has(entry.name))throw Error('Unexpected output file; use a clean build/frontend directory: '+entry.name);
}
for(const name of assets){
 const source=path.join(root,'web',name);
 if((await lstat(source)).isSymbolicLink())throw Error('Symlink assets are not allowed');
 await copyFile(source,path.join(output,name));
}
await writeFile(path.join(output,'config.js'),'window.TAMSOOD_CONFIG = '+JSON.stringify({apiBaseUrl})+';\n');
const files=[];
for(const name of [...assets,'config.js']){
 const body=await readFile(path.join(output,name));
 files.push({path:name,sha256:createHash('sha256').update(body).digest('hex'),bytes:body.length});
}
await writeFile(path.join(output,'build-manifest.json'),JSON.stringify({scope:'PUBLIC_FRONTEND_WITH_LICENSED_REFERENCE_SNAPSHOT',containsSourceData:true,publicSnapshotLicence:'CC BY 4.0',publicSnapshotRows:42,containsPrivateResearchData:false,containsRawDocuments:false,apiBaseUrl,files},null,2)+'\n');
console.log(JSON.stringify({output,assets:files.length,apiBaseUrl:apiBaseUrl||'same-origin',publicSnapshotRows:42,containsPrivateResearchData:false}));
