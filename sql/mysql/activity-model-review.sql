-- Isolated candidate; not a production migration.

CREATE TABLE release_manifest(release_id VARCHAR(128) PRIMARY KEY, payload_json JSON NOT NULL CHECK(json_valid(payload_json))) ENGINE=InnoDB;
CREATE TABLE release_seal(release_id VARCHAR(128) PRIMARY KEY,FOREIGN KEY(release_id) REFERENCES release_manifest(release_id)) ENGINE=InnoDB;
CREATE TABLE source_observation(
 observation_id VARCHAR(128) PRIMARY KEY, amount VARCHAR(128) NOT NULL, unit VARCHAR(128),
 payload_json JSON NOT NULL CHECK(json_valid(payload_json)),
 CHECK(JSON_CONTAINS_PATH(payload_json,'one','$.amount')=1 AND JSON_TYPE(JSON_EXTRACT(payload_json,'$.amount'))='STRING'),
 CHECK(JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.amount'))=amount),
 CHECK(JSON_CONTAINS_PATH(payload_json,'one','$.unit')=1),
 CHECK((CASE WHEN JSON_TYPE(JSON_EXTRACT(payload_json,'$.unit'))='NULL' THEN NULL ELSE JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.unit')) END) <=> unit)) ENGINE=InnoDB;
CREATE TABLE process_dataset_version(
 version_id VARCHAR(128) PRIMARY KEY, process_name VARCHAR(128) NOT NULL, source_count INTEGER NOT NULL CHECK(source_count>0)) ENGINE=InnoDB;
CREATE TABLE dataset_exchange(
 version_id VARCHAR(128) NOT NULL,
 observation_id VARCHAR(128) NOT NULL,
 PRIMARY KEY(version_id,observation_id),FOREIGN KEY(version_id) REFERENCES process_dataset_version(version_id),FOREIGN KEY(observation_id) REFERENCES source_observation(observation_id)) ENGINE=InnoDB;

CREATE TABLE product_system_version(
 model_id VARCHAR(128) PRIMARY KEY, release_id VARCHAR(128) NOT NULL,
 functional_amount VARCHAR(128) NOT NULL, functional_unit VARCHAR(128) NOT NULL,
 status VARCHAR(128) NOT NULL CHECK(status='ACTIVITY_SCENARIO_NOT_FULL_LCI'),FOREIGN KEY(release_id) REFERENCES release_manifest(release_id)) ENGINE=InnoDB;
CREATE TABLE scenario_case(
 scenario_id VARCHAR(128) PRIMARY KEY, model_id VARCHAR(128) NOT NULL,
 scenario_key VARCHAR(128) NOT NULL, metadata_json JSON NOT NULL CHECK(json_valid(metadata_json)),FOREIGN KEY(model_id) REFERENCES product_system_version(model_id)) ENGINE=InnoDB;
CREATE TABLE process_instance(
 scenario_id VARCHAR(128) NOT NULL, process_name VARCHAR(128) NOT NULL,
 version_id VARCHAR(128) NOT NULL, activity_factor VARCHAR(128) NOT NULL,
 PRIMARY KEY(scenario_id,process_name), UNIQUE(scenario_id,process_name,version_id),FOREIGN KEY(scenario_id) REFERENCES scenario_case(scenario_id),FOREIGN KEY(version_id) REFERENCES process_dataset_version(version_id)) ENGINE=InnoDB;
CREATE TABLE provider_link_candidate(
 scenario_id VARCHAR(128) NOT NULL, provider VARCHAR(128) NOT NULL, consumer VARCHAR(128) NOT NULL,
 provider_version VARCHAR(128) NOT NULL, provider_exchange VARCHAR(128) NOT NULL,
 consumer_version VARCHAR(128) NOT NULL, consumer_exchange VARCHAR(128) NOT NULL,
 supplied_kg VARCHAR(128) NOT NULL, consumed_kg VARCHAR(128) NOT NULL,
 decision VARCHAR(128) NOT NULL CHECK(decision='UNREVIEWED_BURDEN_LINK_NOT_APPLIED'),
 PRIMARY KEY(scenario_id,provider,consumer), CHECK(supplied_kg=consumed_kg),
 FOREIGN KEY(scenario_id,provider,provider_version) REFERENCES process_instance(scenario_id,process_name,version_id),
 FOREIGN KEY(scenario_id,consumer,consumer_version) REFERENCES process_instance(scenario_id,process_name,version_id),
 FOREIGN KEY(provider_version,provider_exchange) REFERENCES dataset_exchange(version_id,observation_id),
 FOREIGN KEY(consumer_version,consumer_exchange) REFERENCES dataset_exchange(version_id,observation_id),FOREIGN KEY(scenario_id) REFERENCES scenario_case(scenario_id)) ENGINE=InnoDB;
CREATE TABLE allocation_decision(
 scenario_id VARCHAR(128) PRIMARY KEY,
 state VARCHAR(128) NOT NULL CHECK(state='UNRESOLVED_NOT_APPLIED'),
 details_json JSON NOT NULL CHECK(json_valid(details_json)),FOREIGN KEY(scenario_id) REFERENCES scenario_case(scenario_id)) ENGINE=InnoDB;
CREATE TABLE scenario_assumption(
 scenario_id VARCHAR(128) NOT NULL, assumption_key VARCHAR(128) NOT NULL,
 payload_json JSON NOT NULL CHECK(json_valid(payload_json)), PRIMARY KEY(scenario_id,assumption_key),FOREIGN KEY(scenario_id) REFERENCES scenario_case(scenario_id)) ENGINE=InnoDB;
CREATE TABLE required_decision(
 scenario_id VARCHAR(128) NOT NULL, decision_key VARCHAR(128) NOT NULL,
 state VARCHAR(128) NOT NULL CHECK(state='OPEN'), PRIMARY KEY(scenario_id,decision_key),FOREIGN KEY(scenario_id) REFERENCES scenario_case(scenario_id)) ENGINE=InnoDB;
CREATE TABLE calculation_run(
 run_id VARCHAR(128) PRIMARY KEY, scenario_id VARCHAR(128) NOT NULL,
 input_sha256 VARCHAR(128) NOT NULL, implementation_sha256 VARCHAR(128) NOT NULL,
 manifest_json JSON NOT NULL CHECK(json_valid(manifest_json)), UNIQUE(run_id,scenario_id),FOREIGN KEY(scenario_id) REFERENCES scenario_case(scenario_id)) ENGINE=InnoDB;
CREATE TABLE result_exchange(
 run_id VARCHAR(128) NOT NULL, scenario_id VARCHAR(128) NOT NULL, process_name VARCHAR(128) NOT NULL,
 version_id VARCHAR(128) NOT NULL, observation_id VARCHAR(128) NOT NULL, scaled_amount VARCHAR(128),
 status VARCHAR(128) NOT NULL CHECK(status IN ('HOLD_SOURCE_UNIT','SCENARIO_ACTIVITY_SCALED')),
 PRIMARY KEY(run_id,observation_id),
 CHECK((status='HOLD_SOURCE_UNIT' AND scaled_amount IS NULL) OR (status='SCENARIO_ACTIVITY_SCALED' AND scaled_amount IS NOT NULL)),
 FOREIGN KEY(run_id,scenario_id) REFERENCES calculation_run(run_id,scenario_id),
 FOREIGN KEY(scenario_id,process_name,version_id) REFERENCES process_instance(scenario_id,process_name,version_id),
 FOREIGN KEY(version_id,observation_id) REFERENCES dataset_exchange(version_id,observation_id)) ENGINE=InnoDB;

DELIMITER $$
CREATE TRIGGER dataset_process_membership BEFORE INSERT ON dataset_exchange FOR EACH ROW BEGIN IF NOT ((SELECT COALESCE(JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.process')),JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.reference_product'))) FROM source_observation WHERE observation_id=NEW.observation_id) <=> (SELECT process_name FROM process_dataset_version WHERE version_id=NEW.version_id)) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Source process membership mismatch'; END IF; END$$
CREATE TRIGGER immutable_release_manifest_update BEFORE UPDATE ON release_manifest FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_release_manifest_delete BEFORE DELETE ON release_manifest FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_release_manifest_insert BEFORE INSERT ON release_manifest FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_release_seal_update BEFORE UPDATE ON release_seal FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_release_seal_delete BEFORE DELETE ON release_seal FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_source_observation_update BEFORE UPDATE ON source_observation FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_source_observation_delete BEFORE DELETE ON source_observation FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_source_observation_insert BEFORE INSERT ON source_observation FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_process_dataset_version_update BEFORE UPDATE ON process_dataset_version FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_process_dataset_version_delete BEFORE DELETE ON process_dataset_version FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_process_dataset_version_insert BEFORE INSERT ON process_dataset_version FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_dataset_exchange_update BEFORE UPDATE ON dataset_exchange FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_dataset_exchange_delete BEFORE DELETE ON dataset_exchange FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_dataset_exchange_insert BEFORE INSERT ON dataset_exchange FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_product_system_version_update BEFORE UPDATE ON product_system_version FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_product_system_version_delete BEFORE DELETE ON product_system_version FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_product_system_version_insert BEFORE INSERT ON product_system_version FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_scenario_case_update BEFORE UPDATE ON scenario_case FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_scenario_case_delete BEFORE DELETE ON scenario_case FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_scenario_case_insert BEFORE INSERT ON scenario_case FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_process_instance_update BEFORE UPDATE ON process_instance FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_process_instance_delete BEFORE DELETE ON process_instance FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_process_instance_insert BEFORE INSERT ON process_instance FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_provider_link_candidate_update BEFORE UPDATE ON provider_link_candidate FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_provider_link_candidate_delete BEFORE DELETE ON provider_link_candidate FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_provider_link_candidate_insert BEFORE INSERT ON provider_link_candidate FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_allocation_decision_update BEFORE UPDATE ON allocation_decision FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_allocation_decision_delete BEFORE DELETE ON allocation_decision FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_allocation_decision_insert BEFORE INSERT ON allocation_decision FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_scenario_assumption_update BEFORE UPDATE ON scenario_assumption FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_scenario_assumption_delete BEFORE DELETE ON scenario_assumption FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_scenario_assumption_insert BEFORE INSERT ON scenario_assumption FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_required_decision_update BEFORE UPDATE ON required_decision FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_required_decision_delete BEFORE DELETE ON required_decision FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_required_decision_insert BEFORE INSERT ON required_decision FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_calculation_run_update BEFORE UPDATE ON calculation_run FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_calculation_run_delete BEFORE DELETE ON calculation_run FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_calculation_run_insert BEFORE INSERT ON calculation_run FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
CREATE TRIGGER immutable_result_exchange_update BEFORE UPDATE ON result_exchange FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER immutable_result_exchange_delete BEFORE DELETE ON result_exchange FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'$$
CREATE TRIGGER sealed_result_exchange_insert BEFORE INSERT ON result_exchange FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END$$
DELIMITER ;
