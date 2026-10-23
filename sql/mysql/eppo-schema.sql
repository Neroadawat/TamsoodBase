SET NAMES utf8mb4;
SET SESSION sql_mode='STRICT_ALL_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
CREATE DATABASE IF NOT EXISTS tamsood_eppo CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE tamsood_eppo;
CREATE TABLE IF NOT EXISTS source_snapshot (
 snapshot_id CHAR(64) PRIMARY KEY,dataset_id VARCHAR(20) NOT NULL,
 source_url TEXT NOT NULL,metadata JSON NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS observation (
 observation_id CHAR(64) PRIMARY KEY,snapshot_id CHAR(64) NOT NULL,
 reference_year SMALLINT NOT NULL,month TINYINT NOT NULL,subject VARCHAR(100) NOT NULL,
 amount DECIMAL(30,12) NOT NULL,unit_code VARCHAR(40) NOT NULL,
 status VARCHAR(40) NOT NULL,source_line INT NOT NULL,payload JSON NOT NULL,
 FOREIGN KEY(snapshot_id) REFERENCES source_snapshot(snapshot_id),
 UNIQUE(snapshot_id,reference_year,month,subject),
 CHECK(month BETWEEN 1 AND 12),CHECK(reference_year BETWEEN 1900 AND 2100),
 CHECK(amount>=0),CHECK(source_line>1),
 CHECK(unit_code IN ('BBL/DAY','Million Litres')),
 CHECK(status='STAGED_SOURCE_VERIFIED'),
 INDEX ix_period(reference_year,month)
) ENGINE=InnoDB;
