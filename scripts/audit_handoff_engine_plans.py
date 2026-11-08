"""Read-only EXPLAIN in the owner-marked local MySQL and Neo4j labs."""
import json
import re
import sqlite3
from pathlib import Path
from verify_handoff_engines import docker, owned, cypher

ROOT=Path(__file__).resolve().parents[1]


def tables(value):
    if isinstance(value,dict):
        if 'table_name' in value: yield value
        for child in value.values():yield from tables(child)
    elif isinstance(value,list):
        for child in value:yield from tables(child)


def main():
    meta=json.loads((ROOT/'build/handoff/engines.json').read_bytes())
    store=json.loads((ROOT/'build/handoff/current.json').read_bytes())
    mysql=meta['mysql_container'];neo=meta['neo4j_container']
    if not owned(mysql) or not owned(neo):raise ValueError('Owned review labs unavailable')
    con=sqlite3.connect((ROOT/store['database']).resolve().as_uri()+'?mode=ro',uri=True)
    oid=con.execute('SELECT id FROM observation WHERE public=1 ORDER BY id LIMIT 1').fetchone()[0];con.close()
    if not re.fullmatch('[a-f0-9]{64}',oid):raise ValueError('Invalid observation ID')
    def explain(statement):
        output=docker('exec','-i',mysql,'mysql','-uroot','--batch','--raw','--skip-column-names',
                      body='EXPLAIN FORMAT=JSON '+statement).stdout.decode()
        return json.loads(output)
    lookup=explain("SELECT payload FROM handoff_review.observation WHERE id='"+oid+"';")
    period=explain("SELECT snapshot_id,source_line,amount FROM tamsood_research.observation WHERE period_start>='2024-01-01' AND period_start<'2025-01-01' ORDER BY period_start LIMIT 30;")
    lookup_tables=list(tables(lookup));period_tables=list(tables(period))
    graph=cypher(neo,'EXPLAIN MATCH (p:Process)-[:HAS_EXCHANGE]->(e:Exchange {observation_id:$observation_id}) RETURN p.name,e.amount;',{'observation_id':oid},verbose=True).stdout.decode()
    report={'scope':'LOCAL_LAB_EXPLAIN_NOT_PRODUCTION_QUERY_PLAN','mysql_lookup':lookup,
            'mysql_period_range':period,'neo4j_plan':graph,
            'primary_key_lookup':any(t.get('key')=='PRIMARY' for t in lookup_tables),
            'period_index_used':any(t.get('key')=='ix_period_context' for t in period_tables),
            'graph_index_seek': 'IndexSeek' in graph,'production_changed':False}
    report['passed']=all(report[k] for k in ('primary_key_lookup','period_index_used','graph_index_seek'))
    (ROOT/'evidence/local-engine-query-plans-2026-11-08.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('mysql_lookup','mysql_period_range','neo4j_plan')}))
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
