// Construct a source-only deployment folder; do not upload the research repo.
import {readFile,writeFile,mkdir,copyFile,lstat,readdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'build/vercel-upload');
const files=['vercel.json','scripts/build_frontend.mjs','api/[route].js','api/rag/ask.js',
 'docs/rag/public-release-manifest.json','docs/rag/knowledge-pack.json',
 'web/index.html','web/ask.html','web/style.css','web/design-refresh.css','web/app.js','web/api.js','web/config.js','web/favicon.svg','web/upstream-inventory.json','web/case-study.js','web/case-study.json','web/discovery.js','web/story.js','web/theme.css','web/noto-sans-thai-06310198b08f.woff2','web/FONT-LICENSE.txt'];
await mkdir(out,{recursive:true});
for(const name of files){
 const source=path.join(root,name),target=path.join(out,name);
 if(!(await lstat(source)).isFile() || (await lstat(source)).isSymbolicLink())throw Error('Unsafe source file');
 await mkdir(path.dirname(target),{recursive:true});await copyFile(source,target);
}
await writeFile(path.join(out,'.vercelignore'),'.vercel/\n.env*\nbuild/\n.git/\n');
await mkdir(path.join(out,'.vercel'),{recursive:true});
const link=JSON.parse(await readFile(path.join(root,'.vercel/project.json'),'utf8'));
await writeFile(path.join(out,'.vercel/project.json'),JSON.stringify({projectId:link.projectId,orgId:link.orgId,projectName:link.projectName})+'\n');
const allowed=new Set([...files,'.vercelignore','.vercel/project.json']);
async function inspect(folder,prefix=''){
 for(const entry of await readdir(folder,{withFileTypes:true})){
  const name=prefix+entry.name;
  if(entry.isSymbolicLink())throw Error('Unexpected symlink');
  if(entry.isDirectory())await inspect(path.join(folder,entry.name),name+'/');
  else if(!allowed.has(name))throw Error('Unexpected deployment file: '+name);
 }
}
await inspect(out);console.log(JSON.stringify({directory:out,sourceFiles:files.length,licensedPublicReferenceSnapshot:true,containsPrivateResearchData:false,containsCredentials:false}));
