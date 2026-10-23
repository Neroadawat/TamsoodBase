SET NAMES utf8mb4;
SET SESSION sql_mode='STRICT_ALL_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
CREATE DATABASE IF NOT EXISTS tamsood_supplemental CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE tamsood_supplemental;
CREATE TABLE IF NOT EXISTS dataset_snapshot (
 snapshot_id CHAR(64) PRIMARY KEY, data_kind VARCHAR(30) NOT NULL,
 artifact_path VARCHAR(255) NOT NULL,
 CHECK(data_kind IN ('NSO','PRODUCT_INVENTORY'))
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS observation (
 snapshot_id CHAR(64) NOT NULL, observation_id CHAR(64) NOT NULL,
 amount DECIMAL(30,12) NOT NULL, unit_code VARCHAR(80) NOT NULL,
 status VARCHAR(60) NOT NULL, payload JSON NOT NULL,
 PRIMARY KEY(snapshot_id,observation_id),
 FOREIGN KEY(snapshot_id) REFERENCES dataset_snapshot(snapshot_id),
 CHECK(status IN ('STAGED_SOURCE_VERIFIED','SOURCE_REPORTED_PRODUCT_INVENTORY'))
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS national_statistic (
 snapshot_id CHAR(64) NOT NULL, observation_id CHAR(64) NOT NULL,
 table_id VARCHAR(10) NOT NULL, reference_year SMALLINT NOT NULL,
 measure VARCHAR(255) NOT NULL, label VARCHAR(255) NOT NULL,
 source_sha256 CHAR(64) NOT NULL, source_line INT NOT NULL, source_column INT NOT NULL,
 PRIMARY KEY(snapshot_id,observation_id),
 FOREIGN KEY(snapshot_id,observation_id) REFERENCES observation(snapshot_id,observation_id),
 CHECK(reference_year BETWEEN 1900 AND 2100), CHECK(source_line>0 AND source_column>0),
 INDEX ix_year_table(reference_year,table_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS process (
 snapshot_id CHAR(64) NOT NULL, process_id VARCHAR(30) NOT NULL,
 reference_amount DECIMAL(30,12) NOT NULL, reference_unit VARCHAR(80) NOT NULL,
 geography VARCHAR(100) NOT NULL, technology_level VARCHAR(100) NOT NULL,
 PRIMARY KEY(snapshot_id,process_id),
 FOREIGN KEY(snapshot_id) REFERENCES dataset_snapshot(snapshot_id), CHECK(reference_amount>0)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS inventory_exchange (
 snapshot_id CHAR(64) NOT NULL, observation_id CHAR(64) NOT NULL,
 process_id VARCHAR(30) NOT NULL, flow VARCHAR(255) NOT NULL,
 direction VARCHAR(10) NOT NULL, role VARCHAR(30) NOT NULL,
 data_period VARCHAR(100) NULL, source_sha256 CHAR(64) NOT NULL,
 source_row INT NOT NULL, source_column INT NOT NULL,
 PRIMARY KEY(snapshot_id,observation_id),
 FOREIGN KEY(snapshot_id,observation_id) REFERENCES observation(snapshot_id,observation_id),
 FOREIGN KEY(snapshot_id,process_id) REFERENCES process(snapshot_id,process_id),
 CHECK(direction IN ('INPUT','OUTPUT')),
 CHECK(role IN ('INPUT','OUTPUT','REFERENCE_PRODUCT','CO_PRODUCT')),
 CHECK(source_row>0 AND source_column>0)
) ENGINE=InnoDB;
