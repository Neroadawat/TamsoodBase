import json,sys,re,pymupdf
sys.stdout.reconfigure(encoding='utf-8')
keys=json.loads(open('toc_keys.json',encoding='utf-8').read())
d=pymupdf.open(sys.argv[1])
toc_last=max(i for i in range(6) if 'Functional Requirements (FR-xx)' in d[i].get_text() or 'Appendix' in d[i].get_text() and i<5)
pages={}
start=toc_last+1
for k in keys:
    if k=='front': pages[k]=f'1-{toc_last+1}'; continue
    found=None
    for i in range(start-1 if start>toc_last+1 else start,len(d)):
        lines=[re.sub(r'\s+',' ',l).strip() for l in d[i].get_text().split('\n')]
        if any(l.startswith(k) for l in lines): found=i; break
    if found is None:
        for i in range(toc_last+1,len(d)):
            if d[i].search_for(k): found=i; break
    pages[k]=found+1 if found is not None else ''
    if found is not None: start=found+1
json.dump(pages,open('toc_pages.json','w',encoding='utf-8'),ensure_ascii=False)
print('toc ends on page',toc_last+1,'| missing:',[k for k,v in pages.items() if v==''])
print(pages)
