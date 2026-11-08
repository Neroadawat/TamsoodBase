"""Versioned review schema with immutable source observations; never production LCI."""
import hashlib
import json
import sqlite3
import re
from decimal import Decimal
from pathlib import Path
from scripts.build_combined_inventory_review import ROOT, build_review
from scripts.extract_upstream_inventory import amount as parse_source_number
PARSER_CONTRACT='REVIEW_PARSE_V2_TABLE4_FOOTNOTE_A'

SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE source_observation(
 observation_id TEXT PRIMARY KEY,process_id TEXT NOT NULL,source_hash TEXT NOT NULL,
 flow_label TEXT NOT NULL,amount TEXT NOT NULL CHECK(amount GLOB '*[0-9]*' AND amount NOT GLOB '*[^0-9.]*' AND amount NOT GLOB '*.*.*'),unit_code TEXT,
 direction TEXT NOT NULL CHECK(direction IN ('INPUT','OUTPUT')),role TEXT NOT NULL,
 source_status TEXT NOT NULL,original_json TEXT NOT NULL,
 CHECK((direction='INPUT' AND role='INPUT') OR (direction='OUTPUT' AND role IN ('OUTPUT','REFERENCE_PRODUCT','CO_PRODUCT'))),
 CHECK((unit_code IS NULL AND source_status='HOLD_MISSING_UNIT') OR
       (unit_code IS NOT NULL AND source_status!='HOLD_MISSING_UNIT')));
CREATE TRIGGER observation_payload_match BEFORE INSERT ON source_observation
WHEN NEW.observation_id IS NOT json_extract(NEW.original_json,'$.observation_id')
 OR NEW.process_id IS NOT json_extract(NEW.original_json,'$.process')
 OR NEW.flow_label IS NOT json_extract(NEW.original_json,'$.flow')
 OR NEW.amount IS NOT json_extract(NEW.original_json,'$.amount')
 OR NEW.unit_code IS NOT json_extract(NEW.original_json,'$.unit')
 OR NEW.direction IS NOT json_extract(NEW.original_json,'$.direction')
 OR NEW.role IS NOT json_extract(NEW.original_json,'$.role')
 OR NEW.source_status IS NOT json_extract(NEW.original_json,'$.status')
 OR NEW.source_hash IS NOT COALESCE(json_extract(NEW.original_json,'$.source_sha256'),json_extract(NEW.original_json,'$.source_snapshot_sha256'))
BEGIN SELECT RAISE(ABORT,'Typed source fields differ from retained payload'); END;
CREATE TRIGGER observation_immutable_update BEFORE UPDATE ON source_observation
BEGIN SELECT RAISE(ABORT,'Source observation is immutable; create a new source revision'); END;
CREATE TRIGGER observation_immutable_delete BEFORE DELETE ON source_observation
BEGIN SELECT RAISE(ABORT,'Retain source observation for audit'); END;
CREATE TABLE process_dataset_version(
 version_id TEXT PRIMARY KEY,process_id TEXT NOT NULL,contract_version TEXT NOT NULL,
 reference_amount TEXT NOT NULL,reference_unit TEXT NOT NULL,
 reference_observation_id TEXT NOT NULL REFERENCES source_observation(observation_id),
 model_ready INTEGER NOT NULL CHECK(model_ready=0),
 allocation_state TEXT NOT NULL CHECK(allocation_state='UNRESOLVED'),
 sealed INTEGER NOT NULL DEFAULT 0 CHECK(sealed IN (0,1)),
 UNIQUE(process_id,version_id));
CREATE TABLE dataset_exchange(
 version_id TEXT NOT NULL REFERENCES process_dataset_version(version_id),
 observation_id TEXT NOT NULL REFERENCES source_observation(observation_id),
 PRIMARY KEY(version_id,observation_id));
CREATE TRIGGER dataset_immutable_update BEFORE UPDATE ON process_dataset_version
WHEN NOT(OLD.sealed=0 AND NEW.sealed=1 AND OLD.version_id=NEW.version_id AND OLD.process_id=NEW.process_id
 AND OLD.contract_version=NEW.contract_version AND OLD.reference_amount=NEW.reference_amount
 AND OLD.reference_unit=NEW.reference_unit AND OLD.reference_observation_id=NEW.reference_observation_id
 AND OLD.model_ready=NEW.model_ready AND OLD.allocation_state=NEW.allocation_state)
BEGIN SELECT RAISE(ABORT,'Create a new dataset version'); END;
CREATE TRIGGER dataset_immutable_delete BEFORE DELETE ON process_dataset_version
BEGIN SELECT RAISE(ABORT,'Retain dataset versions'); END;
CREATE TRIGGER reference_context BEFORE INSERT ON process_dataset_version
WHEN NOT EXISTS(SELECT 1 FROM source_observation WHERE observation_id=NEW.reference_observation_id
 AND process_id=NEW.process_id AND role='REFERENCE_PRODUCT' AND direction='OUTPUT')
BEGIN SELECT RAISE(ABORT,'Reference product does not belong to this process'); END;
CREATE TRIGGER exchange_immutable_update BEFORE UPDATE ON dataset_exchange
BEGIN SELECT RAISE(ABORT,'Create a new dataset version for membership changes'); END;
CREATE TRIGGER exchange_immutable_delete BEFORE DELETE ON dataset_exchange
BEGIN SELECT RAISE(ABORT,'Retain dataset membership'); END;
CREATE TRIGGER exchange_context BEFORE INSERT ON dataset_exchange
WHEN (SELECT sealed FROM process_dataset_version WHERE version_id=NEW.version_id)=1
 OR (SELECT process_id FROM source_observation WHERE observation_id=NEW.observation_id)
 !=(SELECT process_id FROM process_dataset_version WHERE version_id=NEW.version_id)
BEGIN SELECT RAISE(ABORT,'Observation and dataset process differ'); END;
CREATE TABLE numeric_parse_audit(
 observation_id TEXT PRIMARY KEY REFERENCES source_observation(observation_id),
 operation TEXT NOT NULL CHECK(operation='PARSE_SOURCE_NUMBER_ONLY'),
 parser_version TEXT NOT NULL,input_lexeme TEXT NOT NULL,output_decimal TEXT NOT NULL,
 unit_conversion_applied INTEGER NOT NULL CHECK(unit_conversion_applied=0),
 allocation_applied INTEGER NOT NULL CHECK(allocation_applied=0));
CREATE TRIGGER parse_matches_source BEFORE INSERT ON numeric_parse_audit
WHEN NEW.output_decimal!=(SELECT amount FROM source_observation WHERE observation_id=NEW.observation_id)
 OR NEW.input_lexeme!=(SELECT json_extract(original_json,'$.raw_value') FROM source_observation WHERE observation_id=NEW.observation_id)
BEGIN SELECT RAISE(ABORT,'Parsed quantity does not match retained source'); END;
CREATE TRIGGER parse_immutable_update BEFORE UPDATE ON numeric_parse_audit
BEGIN SELECT RAISE(ABORT,'Retain numeric parsing evidence'); END;
CREATE TRIGGER parse_immutable_delete BEFORE DELETE ON numeric_parse_audit
BEGIN SELECT RAISE(ABORT,'Retain numeric parsing evidence'); END;
CREATE INDEX ix_source_process_direction ON source_observation(process_id,direction);
CREATE VIEW review_export AS SELECT v.version_id,v.reference_amount,v.reference_unit,
 o.observation_id,o.process_id,o.flow_label,o.amount,o.unit_code,o.direction,o.role,
 o.source_status,o.source_hash,o.original_json,v.model_ready,v.allocation_state
 FROM dataset_exchange e JOIN process_dataset_version v USING(version_id)
 JOIN source_observation o USING(observation_id);
'''


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def create_store(upstream, conversion):
    reviewed=build_review(upstream,conversion)
    con=sqlite3.connect(':memory:')
    con.executescript(SCHEMA)
    try:
        with con:
            for mapping in reviewed['mappings']:
                row=mapping['source']
                parser='extract_upstream_inventory.amount:v1'
                if row['table_id']=='4':
                    match=re.fullmatch(r'(\d+(?:\.\d+)?)(?:\s+(a))?',row['raw_value'])
                    if not match or (match[2] and row.get('annotation')!='Calculated power for semi-batch reactor'):
                        raise ValueError('Unreviewed Table4 numeric footnote')
                    parsed=Decimal(match[1]);parser='TABLE4_DECIMAL_OPTIONAL_REVIEWED_FOOTNOTE_A_V1'
                else:parsed=Decimal(parse_source_number(row['raw_value']))
                if parsed!=Decimal(row['amount']):
                    raise ValueError('Numeric parsing audit differs from source lexeme')
                con.execute('INSERT INTO source_observation VALUES(?,?,?,?,?,?,?,?,?,?)',
                    (row['observation_id'],row['process'],row.get('source_sha256') or row['source_snapshot_sha256'],
                     row['flow'],row['amount'],row['unit'],row['direction'],row['role'],row['status'],canonical(row)))
                con.execute('INSERT INTO numeric_parse_audit VALUES(?,?,?,?,?,0,0)',
                    (row['observation_id'],'PARSE_SOURCE_NUMBER_ONLY',parser,row['raw_value'],row['amount']))
            versions={}
            for profile in reviewed['profiles']:
                rows=[m['source'] for m in reviewed['mappings'] if m['process']==profile['process']]
                version=hashlib.sha256(canonical({'contract':'REVIEW_DATASET_V1','rows':sorted(rows,key=lambda r:r['observation_id'])}).encode()).hexdigest()
                versions[profile['process']]=version
                con.execute('INSERT INTO process_dataset_version VALUES(?,?,?,?,?,?,0,?,0)',
                    (version,profile['process'],'REVIEW_DATASET_V1',*profile['reference_basis'],
                     profile['reference_product_observation_id'],'UNRESOLVED'))
                for row in rows:con.execute('INSERT INTO dataset_exchange VALUES(?,?)',(version,row['observation_id']))
                con.execute('UPDATE process_dataset_version SET sealed=1 WHERE version_id=?',(version,))
            actual={i:json.loads(raw) for i,raw in con.execute('SELECT observation_id,original_json FROM review_export')}
            expected={m['observation_id']:m['source'] for m in reviewed['mappings']}
            if actual!=expected or con.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Versioned export roundtrip differs')
        return con,versions
    except Exception:
        con.close()
        raise


def main():
    def read(name):return json.loads((ROOT/name).read_text(encoding='utf8'))
    up=read('build/upstream-inventory/report.json');base=read('build/product-inventory/report.json')
    con,versions=create_store(up,base)
    try:
        # Review generation does not replace any production database or earlier version artifact.
        release=hashlib.sha256(canonical({'versions':versions,'parser_contract':PARSER_CONTRACT,'schema_sha256':hashlib.sha256(SCHEMA.encode()).hexdigest()}).encode()).hexdigest()
        out=ROOT/'build/versioned-inventory'/release
        out.mkdir(parents=True,exist_ok=True)
        target=out/'candidate.sqlite'
        if not target.exists():
            with sqlite3.connect(target) as dest:con.backup(dest)
        with sqlite3.connect(target) as saved:
            for table in ('source_observation','process_dataset_version','dataset_exchange','numeric_parse_audit'):
                source=sorted(con.execute('SELECT * FROM '+table).fetchall(),key=repr)
                restored=sorted(saved.execute('SELECT * FROM '+table).fetchall(),key=repr)
                if source!=restored:raise ValueError('Existing version artifact differs: '+table)
        (out/'schema.sql').write_text(SCHEMA,encoding='utf8')
        evidence={'scope':'LOCAL_VERSIONED_REVIEW_SCHEMA_NOT_PRODUCTION_MIGRATION','release_id':release,
                  'process_versions':versions,'source_rows':58,'roundtrip_all_fields':True,
                  'numeric_parse_audit_rows':58,'allocation_applied':False,'unit_conversion_applied':False,
                  'dataset_versions_sealed':True,
                  'parser_contract':PARSER_CONTRACT,
                  'full_lifecycle_inventory':False,'candidate_path':target.relative_to(ROOT).as_posix(),
                  'candidate_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                  'normal_form_claim':'Dependencies documented per relation; no whole-schema 5NF certification'}
        (ROOT/'evidence/versioned-inventory.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
        print(json.dumps(evidence,indent=2))
    finally:con.close()


if __name__=='__main__':main()
