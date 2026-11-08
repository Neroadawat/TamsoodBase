-- Isolated review schema. No USE/CREATE DATABASE or production migration here.
CREATE TABLE source_observation(
 observation_id VARCHAR(64) PRIMARY KEY,process_id VARCHAR(16) NOT NULL,source_hash CHAR(64) NOT NULL,
 flow_label VARCHAR(200) NOT NULL,amount VARCHAR(120) NOT NULL,unit_code VARCHAR(16),
 direction VARCHAR(8) NOT NULL,role VARCHAR(32) NOT NULL,source_status VARCHAR(64) NOT NULL,
 original_json JSON NOT NULL,
 CHECK((direction='INPUT' AND role='INPUT') OR (direction='OUTPUT' AND role IN ('OUTPUT','REFERENCE_PRODUCT','CO_PRODUCT'))),
 CHECK((unit_code IS NULL AND source_status='HOLD_MISSING_UNIT') OR (unit_code IS NOT NULL AND source_status!='HOLD_MISSING_UNIT'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
CREATE TABLE process_dataset_version(
 version_id CHAR(64) PRIMARY KEY,process_id VARCHAR(16) NOT NULL,contract_version VARCHAR(64) NOT NULL,
 reference_amount VARCHAR(120) NOT NULL,reference_unit VARCHAR(32) NOT NULL,
 reference_observation_id VARCHAR(64) NOT NULL,model_ready TINYINT NOT NULL CHECK(model_ready=0),
 allocation_state VARCHAR(32) NOT NULL CHECK(allocation_state='UNRESOLVED'),
 sealed TINYINT NOT NULL DEFAULT 0 CHECK(sealed IN (0,1)),
 FOREIGN KEY(reference_observation_id) REFERENCES source_observation(observation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
CREATE TABLE dataset_exchange(
 version_id CHAR(64) NOT NULL,observation_id VARCHAR(64) NOT NULL,
 PRIMARY KEY(version_id,observation_id),
 FOREIGN KEY(version_id) REFERENCES process_dataset_version(version_id),
 FOREIGN KEY(observation_id) REFERENCES source_observation(observation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
CREATE TABLE numeric_parse_audit(
 observation_id VARCHAR(64) PRIMARY KEY,operation VARCHAR(40) NOT NULL CHECK(operation='PARSE_SOURCE_NUMBER_ONLY'),
 parser_version VARCHAR(100) NOT NULL,input_lexeme VARCHAR(120) NOT NULL,output_decimal VARCHAR(120) NOT NULL,
 unit_conversion_applied TINYINT NOT NULL CHECK(unit_conversion_applied=0),
 allocation_applied TINYINT NOT NULL CHECK(allocation_applied=0),
 FOREIGN KEY(observation_id) REFERENCES source_observation(observation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
DELIMITER $$
CREATE TRIGGER source_insert_guard BEFORE INSERT ON source_observation FOR EACH ROW
BEGIN
 IF NEW.amount NOT REGEXP '^[0-9]+([.][0-9]+)?$'
 OR NOT(NEW.observation_id <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.observation_id')))
 OR NOT(NEW.process_id <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.process')))
 OR NOT(NEW.flow_label <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.flow')))
 OR NOT(NEW.amount <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.amount')))
 OR NOT(NEW.unit_code <=> NULLIF(JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.unit')),'null'))
 OR NOT(NEW.direction <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.direction')))
 OR NOT(NEW.role <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.role')))
 OR NOT(NEW.source_status <=> JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.status')))
 OR NOT(NEW.source_hash <=> COALESCE(JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.source_sha256')),JSON_UNQUOTE(JSON_EXTRACT(NEW.original_json,'$.source_snapshot_sha256'))))
 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Typed source mismatch'; END IF;
END$$
CREATE TRIGGER source_no_update BEFORE UPDATE ON source_observation FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Source is immutable'; END$$
CREATE TRIGGER source_no_delete BEFORE DELETE ON source_observation FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Source is immutable'; END$$
CREATE TRIGGER version_reference_guard BEFORE INSERT ON process_dataset_version FOR EACH ROW
BEGIN
 IF NOT EXISTS(SELECT 1 FROM source_observation WHERE observation_id=NEW.reference_observation_id AND process_id=NEW.process_id AND role='REFERENCE_PRODUCT' AND direction='OUTPUT')
 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Reference product mismatch'; END IF;
END$$
CREATE TRIGGER version_no_update BEFORE UPDATE ON process_dataset_version FOR EACH ROW
BEGIN
 IF NOT(OLD.sealed=0 AND NEW.sealed=1 AND OLD.version_id=NEW.version_id AND OLD.process_id=NEW.process_id AND OLD.contract_version=NEW.contract_version AND OLD.reference_amount=NEW.reference_amount AND OLD.reference_unit=NEW.reference_unit AND OLD.reference_observation_id=NEW.reference_observation_id AND OLD.model_ready=NEW.model_ready AND OLD.allocation_state=NEW.allocation_state)
 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Create a new dataset version'; END IF;
END$$
CREATE TRIGGER version_no_delete BEFORE DELETE ON process_dataset_version FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Retain dataset version'; END$$
CREATE TRIGGER membership_guard BEFORE INSERT ON dataset_exchange FOR EACH ROW
BEGIN
 IF (SELECT sealed FROM process_dataset_version WHERE version_id=NEW.version_id)=1 OR
 (SELECT process_id FROM source_observation WHERE observation_id=NEW.observation_id)!=(SELECT process_id FROM process_dataset_version WHERE version_id=NEW.version_id)
 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed or mismatched process'; END IF;
END$$
CREATE TRIGGER membership_no_update BEFORE UPDATE ON dataset_exchange FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Retain dataset membership'; END$$
CREATE TRIGGER membership_no_delete BEFORE DELETE ON dataset_exchange FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Retain dataset membership'; END$$
CREATE TRIGGER parse_insert_guard BEFORE INSERT ON numeric_parse_audit FOR EACH ROW
BEGIN
 IF NEW.output_decimal!=(SELECT amount FROM source_observation WHERE observation_id=NEW.observation_id) OR
 NEW.input_lexeme!=(SELECT JSON_UNQUOTE(JSON_EXTRACT(original_json,'$.raw_value')) FROM source_observation WHERE observation_id=NEW.observation_id)
 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parse mismatch'; END IF;
END$$
CREATE TRIGGER parse_no_update BEFORE UPDATE ON numeric_parse_audit FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Retain parsing evidence'; END$$
CREATE TRIGGER parse_no_delete BEFORE DELETE ON numeric_parse_audit FOR EACH ROW
BEGIN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Retain parsing evidence'; END$$
DELIMITER ;
CREATE INDEX ix_source_process_direction ON source_observation(process_id,direction);
CREATE VIEW review_export AS SELECT v.version_id,v.reference_amount,v.reference_unit,o.observation_id,o.process_id,o.flow_label,o.amount,o.unit_code,o.direction,o.role,o.source_status,o.source_hash,o.original_json,v.model_ready,v.allocation_state
 FROM dataset_exchange e JOIN process_dataset_version v USING(version_id) JOIN source_observation o USING(observation_id);
