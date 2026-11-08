"""Process-level consistency; a study FU does not imply complete lifecycle data."""
from decimal import Decimal,InvalidOperation
import hashlib

CONTEXT_FIELDS=('reference_amount','reference_unit','boundary','geography','technology_level',
                'publication_year','data_period','allocation','doi','source_snapshot_sha256')

def positive_number(value):
    if not isinstance(value,str):raise ValueError('Amounts must preserve source decimal strings')
    try:number=Decimal(value)
    except InvalidOperation:raise ValueError('Invalid amount') from None
    if not number.is_finite() or number<=0:raise ValueError('Reference quantity must be positive and finite')
    return number

def validate_process_context(rows):
    if not rows:raise ValueError('Inventory is empty')
    ids=set();groups={}
    for row in rows:
        if not isinstance(row.get('process'),str) or not row['process'].strip():raise ValueError('Process identity missing')
        oid=row['observation_id']
        if not oid or oid in ids:raise ValueError('Duplicate or empty observation identity')
        ids.add(oid);groups.setdefault(row['process'],[]).append(row)
    profiles=[]
    for process,group in sorted(groups.items()):
        first=group[0]
        for key in CONTEXT_FIELDS:
            if any(key not in r or r[key]!=first[key] for r in group):raise ValueError('Mixed process context: '+process+'/'+key)
        positive_number(first['reference_amount'])
        for key in ('reference_unit','boundary','geography','technology_level','allocation','doi','source_snapshot_sha256'):
            if not isinstance(first[key],str) or not first[key].strip():raise ValueError('Missing context: '+key)
        products=[r for r in group if r['role']=='REFERENCE_PRODUCT']
        if len(products)!=1:raise ValueError('Expected exactly one reference product per reviewed process')
        positive_number(products[0]['amount'])
        for row in group:
            if not isinstance(row.get('amount'),str):raise ValueError('Exchange amount must be a decimal string')
            try:amount=Decimal(row['amount'])
            except InvalidOperation:raise ValueError('Invalid exchange amount') from None
            if not amount.is_finite() or amount<0:raise ValueError('Exchange amount must be finite and nonnegative')
            if row['direction'] not in ('INPUT','OUTPUT'):raise ValueError('Unknown exchange direction')
            if row['role'] not in ('INPUT','OUTPUT','REFERENCE_PRODUCT','CO_PRODUCT'):raise ValueError('Unknown exchange role')
            if (row['role']=='INPUT')!=(row['direction']=='INPUT'):raise ValueError('Role/direction mismatch')
            if row.get('is_full_lci_dataset') is not False:raise ValueError('Full lifecycle claim unsupported by foreground contract')
        profiles.append({'process':process,'reference_basis':{'amount':first['reference_amount'],'unit':first['reference_unit']},
            'reference_product':{'flow':products[0]['flow'],'amount':products[0]['amount'],'unit':products[0]['unit']},
            'dataset_boundary':first['boundary'],'data_period':first['data_period'],
            'allocation_status':'SOURCE_METHOD_REPORTED_TABLE_ALLOCATION_BASIS_NOT_RESOLVED',
            'full_lifecycle_inventory':False,'exchanges':len(group)})
    return profiles

def study_scope(rows,context):
    profiles=validate_process_context(rows)
    required=('The functional unit was defined as the use of 1000 MJ fuel.',
              'cultivation and harvesting of oil palm fresh fruit bunch',
              'the use of biofuel in pick-up trucks','Life cycle inventory')
    for phrase in required:
        if phrase not in context:raise ValueError('Study scope evidence changed: '+phrase)
    if any(r['doi']!='10.3390/su12229415' or r['reference_amount']!='1000' or r['reference_unit']!='MJ fuel' for r in rows):raise ValueError('Scope applies only to the reviewed article basis')
    return {'version':1,'source_doi':'10.3390/su12229415','article_context_sha256':hashlib.sha256(context.encode('utf8')).hexdigest(),
        'study_functional_unit':{'function':'Use of fuel','amount':'1000','unit':'MJ fuel','use_context':'Biofuel in pick-up trucks','source_section':'2.1 Goal and Scope'},
        'study_boundary':'Oil palm cultivation and harvesting through biofuel use, as described by the article',
        'imported_boundary':'Selected Table 4 foreground biofuel conversion exchanges only',
        'coverage_status':'PARTIAL_FOREGROUND_INVENTORY',
        'not_imported_as_linked_unit_processes':['Oil palm cultivation and harvesting','Palm oil milling and refining','Transport chain','Background electricity and chemical production','Fuel distribution and vehicle use'],
        'open_issues':['Measurement period not specified in selected table','Confirm allocation already applied before any further allocation','Background process datasets and elementary flow mapping are incomplete'],
        'processes':profiles,'source_values_changed':False,'full_lifecycle_inventory':False}
