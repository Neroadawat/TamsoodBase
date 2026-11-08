PRAGMA foreign_keys=ON;
CREATE TABLE release_manifest(release_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL CHECK(json_valid(payload_json)));
CREATE TABLE release_seal(release_id TEXT PRIMARY KEY REFERENCES release_manifest);
CREATE TABLE source_observation(
 observation_id TEXT PRIMARY KEY, amount TEXT NOT NULL, unit TEXT,
 payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
 CHECK(json_type(payload_json,'$.amount') IS 'text'),
 CHECK(json_extract(payload_json,'$.amount')=amount),
 CHECK(json_type(payload_json,'$.unit') IS NOT NULL),
 CHECK(json_extract(payload_json,'$.unit') IS unit));
CREATE TABLE process_dataset_version(
 version_id TEXT PRIMARY KEY, process_name TEXT NOT NULL, source_count INTEGER NOT NULL CHECK(source_count>0));
CREATE TABLE dataset_exchange(
 version_id TEXT NOT NULL REFERENCES process_dataset_version,
 observation_id TEXT NOT NULL REFERENCES source_observation,
 PRIMARY KEY(version_id,observation_id));
CREATE TRIGGER dataset_process_membership BEFORE INSERT ON dataset_exchange
WHEN (SELECT coalesce(json_extract(payload_json,'$.process'),json_extract(payload_json,'$.reference_product'))
 FROM source_observation WHERE observation_id=NEW.observation_id)
 IS NOT (SELECT process_name FROM process_dataset_version WHERE version_id=NEW.version_id)
BEGIN SELECT RAISE(ABORT,'Source process membership mismatch'); END;
CREATE TABLE product_system_version(
 model_id TEXT PRIMARY KEY, release_id TEXT NOT NULL REFERENCES release_manifest,
 functional_amount TEXT NOT NULL, functional_unit TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status='ACTIVITY_SCENARIO_NOT_FULL_LCI'));
CREATE TABLE scenario_case(
 scenario_id TEXT PRIMARY KEY, model_id TEXT NOT NULL REFERENCES product_system_version,
 scenario_key TEXT NOT NULL, metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)));
CREATE TABLE process_instance(
 scenario_id TEXT NOT NULL REFERENCES scenario_case, process_name TEXT NOT NULL,
 version_id TEXT NOT NULL REFERENCES process_dataset_version, activity_factor TEXT NOT NULL,
 PRIMARY KEY(scenario_id,process_name), UNIQUE(scenario_id,process_name,version_id));
CREATE TABLE provider_link_candidate(
 scenario_id TEXT NOT NULL REFERENCES scenario_case, provider TEXT NOT NULL, consumer TEXT NOT NULL,
 provider_version TEXT NOT NULL, provider_exchange TEXT NOT NULL,
 consumer_version TEXT NOT NULL, consumer_exchange TEXT NOT NULL,
 supplied_kg TEXT NOT NULL, consumed_kg TEXT NOT NULL,
 decision TEXT NOT NULL CHECK(decision='UNREVIEWED_BURDEN_LINK_NOT_APPLIED'),
 PRIMARY KEY(scenario_id,provider,consumer), CHECK(supplied_kg=consumed_kg),
 FOREIGN KEY(scenario_id,provider,provider_version) REFERENCES process_instance(scenario_id,process_name,version_id),
 FOREIGN KEY(scenario_id,consumer,consumer_version) REFERENCES process_instance(scenario_id,process_name,version_id),
 FOREIGN KEY(provider_version,provider_exchange) REFERENCES dataset_exchange,
 FOREIGN KEY(consumer_version,consumer_exchange) REFERENCES dataset_exchange);
CREATE TABLE allocation_decision(
 scenario_id TEXT PRIMARY KEY REFERENCES scenario_case,
 state TEXT NOT NULL CHECK(state='UNRESOLVED_NOT_APPLIED'),
 details_json TEXT NOT NULL CHECK(json_valid(details_json)));
CREATE TABLE scenario_assumption(
 scenario_id TEXT NOT NULL REFERENCES scenario_case, assumption_key TEXT NOT NULL,
 payload_json TEXT NOT NULL CHECK(json_valid(payload_json)), PRIMARY KEY(scenario_id,assumption_key));
CREATE TABLE required_decision(
 scenario_id TEXT NOT NULL REFERENCES scenario_case, decision_key TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state='OPEN'), PRIMARY KEY(scenario_id,decision_key));
CREATE TABLE calculation_run(
 run_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL REFERENCES scenario_case,
 input_sha256 TEXT NOT NULL, implementation_sha256 TEXT NOT NULL,
 manifest_json TEXT NOT NULL CHECK(json_valid(manifest_json)), UNIQUE(run_id,scenario_id));
CREATE TABLE result_exchange(
 run_id TEXT NOT NULL, scenario_id TEXT NOT NULL, process_name TEXT NOT NULL,
 version_id TEXT NOT NULL, observation_id TEXT NOT NULL, scaled_amount TEXT,
 status TEXT NOT NULL CHECK(status IN ('HOLD_SOURCE_UNIT','SCENARIO_ACTIVITY_SCALED')),
 PRIMARY KEY(run_id,observation_id),
 CHECK((status='HOLD_SOURCE_UNIT' AND scaled_amount IS NULL) OR (status='SCENARIO_ACTIVITY_SCALED' AND scaled_amount IS NOT NULL)),
 FOREIGN KEY(run_id,scenario_id) REFERENCES calculation_run(run_id,scenario_id),
 FOREIGN KEY(scenario_id,process_name,version_id) REFERENCES process_instance(scenario_id,process_name,version_id),
 FOREIGN KEY(version_id,observation_id) REFERENCES dataset_exchange);
