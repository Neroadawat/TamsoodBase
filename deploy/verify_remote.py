"""Read-only EC2 smoke test; outputs selected status fields, never environment secrets."""
import json
import subprocess
import urllib.request

checks=[]
for path in ['/healthz','/readyz','/api/summary','/api/records?product=production-oil&page=1',
             '/api/record?package=production-oil&line=2','/api/reference','/api/reference.csv',
             '/api/reports','/api/nso','/api/product-inventory',
             '/api/eppo?dataset=11_13&year=2024&q=SPRC','/api/nso-comparison','/']:
    with urllib.request.urlopen('http://127.0.0.1:8765'+path,timeout=20) as response:
        body=response.read();check=dict(path=path,status=response.status,bytes=len(body))
        if path=='/api/reference':
            assert json.loads(body)['manifest']['accepted_reference']==97;check['accepted_reference']=97
        if path=='/api/nso':assert json.loads(body)['row_count']==273;check['rows']=273
        if path=='/api/product-inventory':assert len(json.loads(body)['rows'])==16;check['rows']=16
        if path.startswith('/api/eppo'):assert json.loads(body)['total']==12;check['filtered_rows']=12
        checks.append(check)
info=json.loads(subprocess.check_output(['docker','inspect','tamsoodbase-api']))[0]
result=dict(result='passed',checks=checks,running=info['State']['Running'],
    health=info['State'].get('Health',{}).get('Status'),port_bindings=info['HostConfig']['PortBindings'],
    readonly=info['HostConfig']['ReadonlyRootfs'],user=info['Config']['User'],
    memory_limit=info['HostConfig']['Memory'],release=info['Config']['Labels']['org.tamsood.release'],
    s3_connected=False,public_route_configured=False,mysql_migrated=False)
assert result['running'] and result['health']=='healthy' and result['readonly']
assert all(binding['HostIp']=='127.0.0.1' for bindings in result['port_bindings'].values() for binding in bindings)
print(json.dumps(result,indent=2))
