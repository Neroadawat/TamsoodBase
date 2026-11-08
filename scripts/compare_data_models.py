"""Compare document and graph projections with read-only relational queries.

Local projection experiment only; does not run MongoDB or Neo4j.
"""
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def project(rows):
    nodes={};edges=set();seen=set()
    for row in rows:
        oid=row['observation_id']
        if oid in seen:raise ValueError('Duplicate observation identity')
        seen.add(oid)
        if row['decision']!='ACCEPTED_REFERENCE' or row['is_normalized_lci_exchange']:
            raise ValueError('Projection expects accepted reference only')
        document='document:'+row['pdf_sha256'];publisher='publisher:'+row['publisher'];observation='observation:'+oid
        for key,value in [(document,{'type':'Document','sha256':row['pdf_sha256'],'source_url':row['source_url']}),
                          (publisher,{'type':'Publisher','name':row['publisher']}),
                          (observation,{'type':'Observation','properties':row})]:
            if key in nodes and nodes[key]!=value:raise ValueError('Conflicting node identity')
            nodes[key]=value
        edges.add((observation,'REPORTED_IN',document));edges.add((document,'PUBLISHED_BY',publisher))
    return {'nodes':nodes,'edges':[list(edge) for edge in sorted(edges)]}


def graph_query(graph,publisher,year):
    documents={start for start,kind,end in graph['edges'] if kind=='PUBLISHED_BY' and end=='publisher:'+publisher}
    observations={start for start,kind,end in graph['edges'] if kind=='REPORTED_IN' and end in documents}
    return sorted(graph['nodes'][key]['properties']['observation_id'] for key in observations
                  if graph['nodes'][key]['properties']['reference_year']==year)


def project_inventory(rows):
    """Preserve exchange identity, source-local flow names and reported basis.

    Exchange nodes retain exact decimal strings and source locators. No emission
    compartment, upstream process or global canonical flow identity is inferred.
    """
    nodes={};edges=set();seen=set()
    def add(key,value):
        if key in nodes and nodes[key]!=value:raise ValueError('Conflicting inventory node identity')
        nodes[key]=value
    for row in rows:
        oid=row['observation_id']
        if oid in seen:raise ValueError('Duplicate exchange identity')
        seen.add(oid)
        if row['status']!='SOURCE_REPORTED_PRODUCT_INVENTORY' or row['direction'] not in ('INPUT','OUTPUT'):raise ValueError('Unexpected inventory status/direction')
        source='source:'+row['source_snapshot_sha256']
        process=source+':process:'+row['process'];exchange='exchange:'+oid
        flow=source+':flow:'+hashlib.sha256(json.dumps([row['flow'],row['unit']],ensure_ascii=False).encode()).hexdigest()
        unit='unit:'+row['unit'];location='location:'+row['geography']
        add(source,{'type':'Source','source_url':row['source_url'],'doi':row['doi'],'licence':row['licence']})
        add(process,{'type':'Process','name':row['process'],'reference_amount':row['reference_amount'],'reference_unit':row['reference_unit'],'boundary':row['boundary'],'geography':row['geography'],'allocation':row['allocation'],'data_period':row['data_period']})
        add(exchange,{'type':'Exchange','properties':row})
        add(flow,{'type':'Flow','name':row['flow'],'identity_scope':'SOURCE_LOCAL_LABEL_AND_UNIT'})
        add(unit,{'type':'Unit','label':row['unit']});add(location,{'type':'Location','name':row['geography']})
        edges.update([(process,'HAS_EXCHANGE',exchange),(exchange,'OF_FLOW',flow),(exchange,'IN_UNIT',unit),(exchange,'FROM_SOURCE',source),(process,'FROM_SOURCE',source),(process,'LOCATED_IN',location)])
    return {'nodes':nodes,'edges':[list(edge) for edge in sorted(edges)]}


def inventory_query(graph,process_name,direction):
    processes={key for key,node in graph['nodes'].items() if node['type']=='Process' and node['name']==process_name}
    exchanges={end for start,kind,end in graph['edges'] if kind=='HAS_EXCHANGE' and start in processes}
    return sorted(graph['nodes'][key]['properties']['observation_id'] for key in exchanges if graph['nodes'][key]['properties']['direction']==direction)


def main():
    folder=ROOT/'build/reusable';source=folder/'accepted-reference.json'
    rows=json.loads(source.read_text(encoding='utf-8'))
    if not rows:raise ValueError('Empty reference release')
    releases={row['release_id'] for row in rows}
    if len(releases)!=1:raise ValueError('Mixed releases')
    graph=project(rows);checks=[]
    with closing(sqlite3.connect((folder/'reference.sqlite').as_uri()+'?mode=ro',uri=True)) as con:
        for publisher,year in sorted({(r['publisher'],r['reference_year']) for r in rows}):
            document_ids=sorted(r['observation_id'] for r in rows if r['publisher']==publisher and r['reference_year']==year)
            relational=sorted(r[0] for r in con.execute('SELECT observation_id FROM accepted_reference WHERE release_id=? AND publisher=? AND reference_year=?',(next(iter(releases)),publisher,year)))
            graph_ids=graph_query(graph,publisher,year)
            checks.append({'publisher':publisher,'year':year,'records':len(relational),'equal':relational==document_ids==graph_ids})
    if not all(c['equal'] for c in checks):raise ValueError('Model query mismatch')
    out=ROOT/'build/model-comparison';out.mkdir(parents=True,exist_ok=True)
    (out/'graph.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    inventory_source=ROOT/'build/product-inventory/report.json'
    inventory_rows=json.loads(inventory_source.read_text(encoding='utf-8'))['rows']
    inventory_graph=project_inventory(inventory_rows);inventory_checks=[]
    with closing(sqlite3.connect((ROOT/'build/product-inventory/inventory.sqlite').as_uri()+'?mode=ro',uri=True)) as con:
        for process in sorted({r['process'] for r in inventory_rows}):
            for direction in ['INPUT','OUTPUT']:
                expected=sorted(r['observation_id'] for r in inventory_rows if r['process']==process and r['direction']==direction)
                actual=sorted(r[0] for r in con.execute('SELECT observation_id FROM exchange WHERE process_id=? AND direction=?',(process,direction)))
                inventory_checks.append({'process':process,'direction':direction,'records':len(expected),'equal':expected==actual==inventory_query(inventory_graph,process,direction)})
    if not all(c['equal'] for c in inventory_checks):raise ValueError('Inventory graph query mismatch')
    (out/'inventory-graph.json').write_text(json.dumps(inventory_graph,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    evidence={'passed':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'release_id':next(iter(releases)),'observations':len(rows),'nodes':len(graph['nodes']),'edges':len(graph['edges']),
              'checks':checks,'rights_preserved_in_each_observation':True,
              'scope':'Local JSON document and Python graph traversal compared with SQLite; no MongoDB/Neo4j engine or performance claim; no new observations; no public redistribution'}
    evidence['product_inventory']={'source_sha256':hashlib.sha256(inventory_source.read_bytes()).hexdigest(),'observations':len(inventory_rows),'processes':len({r['process'] for r in inventory_rows}),'checks':inventory_checks,'nodes':len(inventory_graph['nodes']),'edges':len(inventory_graph['edges']),'full_row_properties_preserved':True,'flow_identity':'Source-local label and unit; no inferred elementary/product classification or upstream links'}
    (ROOT/'evidence/model-comparison.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'reference_observations':len(rows),'reference_query_cases':len(checks),'inventory_observations':len(inventory_rows),'inventory_query_cases':len(inventory_checks)}))


if __name__=='__main__':main()
