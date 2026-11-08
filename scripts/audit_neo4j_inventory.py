"""Actual isolated Neo4j/Cypher experiment; no production engine change."""
import hashlib
import json
from pathlib import Path
import re
import secrets
import sqlite3
import subprocess
import time
from datetime import datetime,timezone
from scripts.compare_data_models import project_inventory

ROOT=Path(__file__).resolve().parents[1]


def literal(value):
    if isinstance(value,dict):
        if not all(re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*',k) for k in value):raise ValueError('Unsafe property')
        return '{'+','.join(k+':'+literal(v) for k,v in value.items())+'}'
    if isinstance(value,list):return '['+','.join(map(literal,value))+']'
    return json.dumps(value,ensure_ascii=False)


def audit():
    name='tamsood-neo4j-lab-'+secrets.token_hex(6);owner='TamsoodBase-Neo4j-Lab';network=name+'-private'
    def docker(*args,check=True):
        r=subprocess.run(['docker',*args],capture_output=True,timeout=120)
        if check and r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[:900])
        return r
    def query(sql,check=True):
        r=subprocess.run(['docker','exec','-i','-e','JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=2 -Xmx128m',name,'cypher-shell','--format','plain','--non-interactive'],input=sql.encode(),capture_output=True,timeout=60)
        if check and r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[:900])
        return r
    source=ROOT/'build/product-inventory/report.json';rows=json.loads(source.read_text(encoding='utf-8'))['rows'];graph=project_inventory(rows)
    docker('image','inspect','neo4j:5-community')
    docker('network','create','--internal','--label','org.tamsood.lab='+owner,network)
    try:
        docker('run','-d','--name',name,'--label','org.tamsood.lab='+owner,'--network',network,'--memory','1536m','--cpus','1','--pids-limit','512','-e','NEO4J_AUTH=none','-e','NEO4J_server_jvm_additional=-XX:ActiveProcessorCount=2','-e','NEO4J_server_memory_heap_initial__size=256m','-e','NEO4J_server_memory_heap_max__size=512m','-e','NEO4J_server_memory_pagecache_size=128m','neo4j:5-community')
        deadline=time.monotonic()+100
        while docker('exec',name,'wget','-q','-O','/dev/null','http://127.0.0.1:7474',check=False).returncode:
            state=json.loads(docker('inspect',name).stdout)[0]['State']
            if not state['Running']:raise RuntimeError('Neo4j stopped before HTTP readiness')
            if time.monotonic()>deadline:raise RuntimeError('Neo4j readiness timeout')
            time.sleep(1)
        version=query('CALL dbms.components() YIELD versions RETURN versions[0] AS version;').stdout.decode().strip()
        query('CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;')
        statements=[]
        for key,node in graph['nodes'].items():
            kind=node['type'];props={k:v for k,v in node.items() if k not in ('type','properties')}
            if 'properties' in node:
                row=node['properties'];props.update(observation_id=row['observation_id'],direction=row['direction'],amount=row['amount'],unit=row['unit'],raw_json=json.dumps(row,ensure_ascii=False,sort_keys=True))
            statements.append('CREATE (n:Entity:'+kind+' '+literal(dict(id=key,**props))+');')
        for start,kind,end in graph['edges']:
            statements.append('MATCH (a:Entity {id:'+literal(start)+'}), (b:Entity {id:'+literal(end)+'}) CREATE (a)-[:'+kind+']->(b);')
        # One explicit transaction, not hundreds of independently committed imports.
        import_sql=':begin\n'+'\n'.join(statements)+'\n:commit\n'
        query(import_sql)
        checks=[];queries=[]
        with sqlite3.connect((ROOT/'build/product-inventory/inventory.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as con:
            for process in ['FAME','H-FAME']:
                for direction in ['INPUT','OUTPUT']:
                    expected=sorted(r[0] for r in con.execute('SELECT observation_id FROM exchange WHERE process_id=? AND direction=?',(process,direction)))
                    cypher='MATCH (p:Process)-[:HAS_EXCHANGE]->(e:Exchange) WHERE p.name='+literal(process)+' AND e.direction='+literal(direction)+' WITH e ORDER BY e.observation_id RETURN collect(e.observation_id)='+literal(expected)+' AS equal;'
                    result=query(cypher).stdout.decode().strip().splitlines()
                    equal=result[-1].lower()=='true';checks.append({'process':process,'direction':direction,'records':len(expected),'equal_to_sqlite':equal});queries.append(cypher)
        full=[{'id':r['observation_id'],'payload':json.dumps(r,ensure_ascii=False,sort_keys=True),'amount':r['amount']} for r in rows]
        full_query='UNWIND '+literal(full)+' AS expected MATCH (e:Exchange {observation_id:expected.id}) WHERE e.raw_json=expected.payload AND e.amount=expected.amount RETURN count(e) AS matched;'
        matched=int(query(full_query).stdout.decode().strip().splitlines()[-1])
        duplicate=query('CREATE (:Entity {id:'+literal(next(iter(graph['nodes'])))+'});',False)
        if duplicate.returncode==0:raise ValueError('Unique constraint failed')
        if not all(c['equal_to_sqlite'] for c in checks) or matched!=len(rows):raise ValueError('Neo4j roundtrip mismatch')
        out=ROOT/'build/neo4j-lab';out.mkdir(parents=True,exist_ok=True)
        (out/'import.cypher').write_text(import_sql,encoding='utf-8')
        (out/'queries.cypher').write_text('\n'.join(queries)+'\n',encoding='utf-8')
        result={'checked_at':datetime.now(timezone.utc).isoformat(),'passed':True,'engine':'Neo4j Community','version_output':version,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'observations':len(rows),'nodes':len(graph['nodes']),'relationships':len(graph['edges']),'checks':checks,'full_original_payload_matches':matched,'unique_entity_id_enforced':True,'scope':'Network-isolated disposable container; source-local flow identity; no upstream links or inferred compartments; decimal amounts stored as strings; no performance claim; production unchanged'}
    except Exception as error:
        result={'passed':False,'status':'EXPERIMENT_FAILED','engine':'Neo4j Community','error':str(error),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'production_changed':False}
        logs=docker('logs',name,check=False)
        out=ROOT/'build/neo4j-lab';out.mkdir(parents=True,exist_ok=True)
        (out/'startup-diagnostic.log').write_bytes(logs.stdout+logs.stderr)
        state=docker('inspect',name,check=False)
        if state.returncode==0:
            state=json.loads(state.stdout)[0]['State']
            result['startup_state']={key:state.get(key) for key in ('Status','ExitCode','OOMKilled','Error')}
        result['diagnostic_log']='build/neo4j-lab/startup-diagnostic.log'
    finally:
        info=docker('inspect',name,check=False)
        if info.returncode==0:
            if (json.loads(info.stdout)[0]['Config']['Labels'] or {}).get('org.tamsood.lab')!=owner:raise RuntimeError('Lab ownership mismatch')
            docker('rm','-f','-v',name)
        net=docker('network','inspect',network,check=False)
        if net.returncode==0 and (json.loads(net.stdout)[0].get('Labels') or {}).get('org.tamsood.lab')==owner:docker('network','rm',network)
    result['temporary_container_removed']=True
    (ROOT/'evidence/neo4j-inventory-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':raise SystemExit(0 if audit()['passed'] else 1)
