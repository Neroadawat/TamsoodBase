"""Verify restored records in owned isolated MySQL and Neo4j labs; no production access."""
import csv
import io
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'TamsoodBase-Handoff-Review'
NETWORK = 'tamsood-handoff-isolated'


def cypher_literal(item):
    if isinstance(item, dict): return '{' + ','.join(k + ':' + cypher_literal(v) for k, v in item.items()) + '}'
    if isinstance(item, list): return '[' + ','.join(cypher_literal(v) for v in item) + ']'
    return json.dumps(item, ensure_ascii=False)


def docker(*args, body=None, timeout=60, check=True):
    result = subprocess.run(['docker', *args], input=body.encode() if body is not None else None,
                            capture_output=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace')[:1000])
    return result


def owned(name):
    result = docker('inspect', name, check=False)
    if result.returncode: return False
    info = json.loads(result.stdout)[0]
    if info['Config'].get('Labels', {}).get('org.tamsood.handoff') != OWNER:
        raise ValueError('Container ownership mismatch')
    network = info['HostConfig']['NetworkMode']
    if network not in ('none', NETWORK) or info['HostConfig'].get('PortBindings'):
        raise ValueError('Lab isolation mismatch')
    if network == NETWORK:
        net = json.loads(docker('network', 'inspect', NETWORK).stdout)[0]
        if not net['Internal'] or net.get('Labels', {}).get('org.tamsood.handoff') != OWNER:
            raise ValueError('Lab network ownership mismatch')
    return True


def cypher(name, statement, params=None, check=True, verbose=False):
    if not owned(name): raise LookupError('Graph lab unavailable')
    argv = ['exec', '-i', '-e', 'JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=2 -Xmx128m', name,
            'cypher-shell', '--non-interactive', '--format', 'verbose' if verbose else 'plain']
    if params:
        argv += ['--param', '{' + ','.join(k + ':' + json.dumps(v) for k, v in params.items()) + '}']
    return docker(*argv, body=statement, check=check)


def graph_observation(name, oid):
    # Caller validates public ID against the immutable SQLite store first.
    output = cypher(name,
        'MATCH (p:Process)-[:HAS_EXCHANGE]->(e:Exchange {observation_id:$observation_id}) '
        'RETURN p.name AS process,e.observation_id AS observation_id,e.amount AS amount,e.unit AS unit;',
        {'observation_id': oid}).stdout.decode('utf-8')
    rows = list(csv.reader(io.StringIO(output), escapechar='\\', skipinitialspace=True))
    records = [dict(zip(rows[0], row)) for row in rows[1:] if row]
    for record in records:
        if record.get('unit') == 'NULL': record['unit'] = None
    return records


def main():
    meta = json.loads((ROOT / 'build/handoff/current.json').read_bytes())
    with sqlite3.connect((ROOT / meta['database']).resolve().as_uri() + '?mode=ro', uri=True) as con:
        observations = list(con.execute('SELECT * FROM observation ORDER BY id'))
        processes = list(con.execute('SELECT * FROM process ORDER BY process_key'))
        sources = list(con.execute('SELECT * FROM source ORDER BY snapshot'))
        links = list(con.execute('SELECT card_id,observation_id FROM card_observation ORDER BY card_id,observation_id'))
    suffix = meta['release'][:12]; mysql = 'tamsood-handoff-mysql-' + suffix; neo = 'tamsood-handoff-neo4j-' + suffix
    if not owned(mysql):
        docker('run', '-d', '--name', mysql, '--label', 'org.tamsood.handoff=' + OWNER,
               '--network', 'none', '--memory', '768m', '--pids-limit', '256',
               '--tmpfs', '/var/lib/mysql:rw,size=512m', '-e', 'MYSQL_ALLOW_EMPTY_PASSWORD=yes',
               'mysql:8.1', '--skip-log-bin', '--innodb-buffer-pool-size=64M')
    deadline = time.monotonic() + 55
    # The image starts a temporary socket-only server during initialization.
    # TCP becomes available only after that server shuts down and the final one starts.
    while docker('exec', mysql, 'mysqladmin', '--protocol=TCP', '-h127.0.0.1', '-uroot', 'ping', check=False).returncode:
        if time.monotonic() > deadline: raise TimeoutError('MySQL lab startup')
        time.sleep(1)
    def sql(statement, check=True):
        return docker('exec', '-i', mysql, 'mysql', '-uroot', '--batch', '--skip-column-names', '--default-character-set=utf8mb4', body=statement, check=check)
    def value(item): return 'NULL' if item is None else 'CONVERT(0x' + str(item).encode().hex() + ' USING utf8mb4)'
    sql('CREATE DATABASE IF NOT EXISTS handoff_review; USE handoff_review; '
        'CREATE TABLE IF NOT EXISTS source(snapshot CHAR(64) PRIMARY KEY);'
        'CREATE TABLE IF NOT EXISTS process(process_key CHAR(64) PRIMARY KEY,snapshot CHAR(64) NOT NULL,name VARCHAR(40) NOT NULL,FOREIGN KEY(snapshot) REFERENCES source(snapshot));'
        'CREATE TABLE IF NOT EXISTS observation(id CHAR(64) PRIMARY KEY,layer VARCHAR(40),snapshot CHAR(64) NOT NULL,process_key CHAR(64),amount VARCHAR(120),unit VARCHAR(120),status VARCHAR(120),public INT CHECK(public IN(0,1)),payload LONGTEXT,FOREIGN KEY(snapshot) REFERENCES source(snapshot),FOREIGN KEY(process_key) REFERENCES process(process_key));')
    count = int(sql('SELECT COUNT(*) FROM handoff_review.observation;').stdout)
    if count == 0:
        statements = ['USE handoff_review; START TRANSACTION;']
        for table, rows in [('source', sources), ('process', processes), ('observation', observations)]:
            for row in rows: statements.append('INSERT INTO ' + table + ' VALUES(' + ','.join(value(v) for v in row) + ');')
        statements.append('COMMIT;'); sql('\n'.join(statements))
    returned = sql('SELECT id,HEX(payload) FROM handoff_review.observation ORDER BY id;').stdout.decode().splitlines()
    actual = {parts[0]: json.loads(bytes.fromhex(parts[1])) for parts in (line.split('\t') for line in returned)}
    expected = {r[0]: json.loads(r[-1]) for r in observations}
    if actual != expected: raise ValueError('MySQL payload mismatch')
    bad_fk = sql("INSERT INTO handoff_review.process VALUES('bad','missing','bad');", check=False)
    if bad_fk.returncode == 0 or b'ERROR 1452' not in bad_fk.stderr: raise ValueError('MySQL FK check failed')
    exists = docker('network', 'inspect', NETWORK, check=False)
    if exists.returncode:
        docker('network', 'create', '--internal', '--label', 'org.tamsood.handoff=' + OWNER, NETWORK)
    if owned(neo):
        state = json.loads(docker('inspect', neo).stdout)[0]['State']
        if not state['Running'] and state['ExitCode'] != 0:
            docker('rm', '-v', neo)  # Only this owner-marked failed lab, not any project database.
    if not owned(neo):
        docker('run', '-d', '--name', neo, '--label', 'org.tamsood.handoff=' + OWNER,
               '--network', NETWORK, '--memory', '1536m', '--pids-limit', '512',
               '-e', 'NEO4J_AUTH=none', '-e', 'NEO4J_server_jvm_additional=-XX:ActiveProcessorCount=2',
               '-e', 'NEO4J_server_memory_heap_initial__size=256m', '-e', 'NEO4J_server_memory_heap_max__size=512m',
               '-e', 'NEO4J_server_memory_pagecache_size=128m', 'neo4j:5.26.32-community')
    deadline = time.monotonic() + 70
    while docker('exec', neo, 'wget', '-q', '-O', '/dev/null', 'http://127.0.0.1:7474', check=False).returncode:
        if not json.loads(docker('inspect', neo).stdout)[0]['State']['Running']:
            raise RuntimeError('Neo4j stopped; inspect owned lab logs')
        if time.monotonic() > deadline: raise TimeoutError('Neo4j lab startup')
        time.sleep(1)
    cypher(neo, 'CREATE CONSTRAINT observation_id IF NOT EXISTS FOR (n:Exchange) REQUIRE n.observation_id IS UNIQUE;')
    rows = [r for r in observations if r[-2] == 1]
    graph_rows = [{'id': r[0], 'process_key': r[3], 'process': json.loads(r[-1])['process'],
                   'snapshot': r[2], 'amount': r[4], 'unit': r[5], 'payload': r[-1]} for r in rows]
    statement = ('UNWIND $rows AS row MERGE (p:Process {id:row.process_key}) SET p.name=row.process '
                 'MERGE (e:Exchange {observation_id:row.id}) SET e.amount=row.amount,e.unit=row.unit,e.payload=row.payload '
                 'MERGE (s:Snapshot {id:row.snapshot}) MERGE (p)-[:HAS_EXCHANGE]->(e) MERGE (e)-[:FROM_SNAPSHOT]->(s);')
    # Pass data as parameters via stdin; avoid OS command-line size limits.
    cypher(neo, ':param {rows:' + cypher_literal(graph_rows) + '}\n' + statement)
    cypher(neo, ':param {links:' + cypher_literal([{'card': c, 'oid': o} for c, o in links]) + '}\n'
            'UNWIND $links AS row MATCH (e:Exchange {observation_id:row.oid}) MERGE (c:EvidenceCard {id:row.card}) MERGE (c)-[:SUPPORTS]->(e);')
    lines = list(csv.reader(io.StringIO(cypher(neo, 'MATCH (e:Exchange) RETURN e.observation_id AS id,e.payload AS payload ORDER BY id;').stdout.decode('utf-8')), escapechar='\\', skipinitialspace=True))
    graph_actual = {r[0]: json.loads(r[1]) for r in lines[1:] if r}
    if graph_actual != {r[0]: json.loads(r[-1]) for r in rows}: raise ValueError('Neo4j payload mismatch')
    duplicate = cypher(neo, 'CREATE (:Exchange {observation_id:$id});', {'id': rows[0][0]}, check=False)
    if duplicate.returncode == 0: raise ValueError('Neo4j duplicate not rejected')
    sample = graph_observation(neo, rows[0][0])
    if len(sample) != 1 or sample[0]['amount'] != rows[0][4]: raise ValueError('Parameterized graph lookup mismatch')
    graph_links = list(csv.reader(io.StringIO(cypher(neo, 'MATCH (c:EvidenceCard)-[:SUPPORTS]->(e:Exchange) RETURN c.id AS card,e.observation_id AS id ORDER BY card,id;').stdout.decode('utf-8')), escapechar='\\', skipinitialspace=True))
    if [tuple(r) for r in graph_links[1:] if r] != links: raise ValueError('Graph card links differ from SQL')
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'release': meta['release'],
              'mysql_container': mysql, 'neo4j_container': neo, 'mysql_rows_equal': len(actual),
              'neo4j_rows_equal': len(graph_actual), 'card_links_equal': len(links),
              'mysql_fk_rejection': True, 'neo4j_duplicate_rejection': True, 'parameterized_graph_lookup': True,
              'mysql_network': 'none', 'neo4j_network': 'owner-marked internal network', 'published_ports': [], 'production_changed': False,
              'scope': 'OWNED_LOCAL_REVIEW_LABS_NOT_PRODUCTION_OR_FULL_LCI', 'passed': True}
    (ROOT / 'build/handoff/engines.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'evidence/handoff-engines-2026-11-08.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
