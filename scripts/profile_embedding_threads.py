"""Compare short/long local embedding CPU cost in separate processes, no downloads."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--child',choices=('default','2'));args=parser.parse_args()
    if args.child:
        from rag_retrieve import TextEmbedding, MODEL, STORE
        encoder=TextEmbedding(MODEL,cache_dir=str(STORE/'models'),local_files_only=True,
                              threads=None if args.child=='default' else 2)
        questions=['หน่วยหน้าที่ของ FAME คืออะไร','E10 ตอนเครื่องเย็นปล่อย CO2 เท่าไร',
                   'การจัดสรรภาระระหว่างกระบวนการผลิตเชื้อเพลิงและการตรวจสอบหลักฐานต้นทาง '*6]
        for _ in range(2):list(encoder.embed(questions))
        cpu=time.process_time();start=time.perf_counter()
        for _ in range(10):vectors=list(encoder.embed(questions))
        result={'threads':args.child,'batches':10,'questions_per_batch':3,
                'elapsed_ms':round((time.perf_counter()-start)*1000,3),
                'cpu_ms':round((time.process_time()-cpu)*1000,3),
                'vectors':[v.tolist() for v in vectors]}
        (ROOT/'build/handoff'/('embedding-'+args.child+'.json')).write_text(json.dumps(result),encoding='utf-8')
        return
    reports=[]
    for value in ('default','2'):
        subprocess.run([sys.executable,'-X','utf8',__file__,'--child',value],check=True,timeout=60)
        reports.append(json.loads((ROOT/'build/handoff'/('embedding-'+value+'.json')).read_bytes()))
    difference=max(abs(a-b) for v,w in zip(reports[0]['vectors'],reports[1]['vectors']) for a,b in zip(v,w))
    report={'scope':'LOCAL_EMBEDDING_THREAD_COMPARISON_NOT_GENERAL_BENCHMARK',
            'cases':[{k:v for k,v in r.items() if k!='vectors'} for r in reports],
            'max_vector_component_difference':difference,'equivalent_within_1e_minus_5':difference<=1e-5}
    (ROOT/'evidence/local-embedding-threads-2026-11-08.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
