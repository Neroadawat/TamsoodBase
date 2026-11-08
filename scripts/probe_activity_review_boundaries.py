"""Reproduce review findings in memory only. Never opens production databases."""
import copy
import json
import sqlite3
from decimal import Decimal,localcontext
from pathlib import Path
from src.activity_model_store import initialize,audit,validate_case

ROOT=Path(__file__).resolve().parents[1]


def probe():
    conn=sqlite3.connect(':memory:')
    initialize(conn,(ROOT/'sql/activity-model-review.sql').read_text(encoding='utf-8'))
    result={}
    try:
        try:
            conn.execute('INSERT INTO source_observation VALUES(?,?,?,?)',('fixture','12','kg','{"unit":"kg"}'))
            result['missing_json_amount_accepted']=True
        except sqlite3.IntegrityError:result['missing_json_amount_accepted']=False
        conn.rollback()
        try:
            result['empty_database_audit']=audit(conn)
            result['empty_release_accepted']=True
        except ValueError:
            result['empty_release_accepted']=False
        conn.execute('INSERT INTO source_observation VALUES(?,?,?,?)',('fixture','12','kg','{"amount":"12","unit":"kg","process":"FAME"}'))
        conn.execute('INSERT INTO process_dataset_version VALUES(?,?,?)',('cpo-version','CPO',1))
        try:
            conn.execute('INSERT INTO dataset_exchange VALUES(?,?)',('cpo-version','fixture'))
            result['wrong_process_source_membership_accepted']=True
        except sqlite3.IntegrityError:result['wrong_process_source_membership_accepted']=False
    finally:conn.close()
    source=ROOT/'build/thai-fame-activity-chain/scenarios.json'
    case=copy.deepcopy(json.loads(source.read_text(encoding='utf-8'))['baseline'])
    with localcontext() as context:
        context.prec=100
        factor=str(Decimal(case['component_scale_factors']['CPO'])*2)
        case['component_scale_factors']['CPO']=factor
        for row in case['rows']:
            if row['component']=='CPO':
                row['scale_factor']=factor
                if row['scaled_amount'] is not None:
                    row['scaled_amount']=str(Decimal(row['source']['amount'])*Decimal(factor))
    try:
        validate_case(case)
        result['changed_process_factor_with_stale_transfer_edges_accepted']=True
    except ValueError:result['changed_process_factor_with_stale_transfer_edges_accepted']=False
    result['stale_transfer_reproduction']='Only memory copy: CPO factor/results doubled; transfer edge fields unchanged; original file untouched'
    return {'scope':'ISOLATED_MEMORY_ONLY_NO_PRODUCTION_CHANGE','probes':result}


if __name__=='__main__':
    result=probe()
    (ROOT/'evidence/system-review-probes.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
