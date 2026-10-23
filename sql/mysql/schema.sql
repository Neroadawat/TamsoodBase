-- Experimental schema for the three-row pilot. Not an approved LCI model.
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS tamsood_pilot CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE tamsood_pilot;
CREATE TABLE IF NOT EXISTS source (
 source_id VARCHAR(80) PRIMARY KEY,
 publisher VARCHAR(255) NOT NULL,
 url TEXT NOT NULL,
 rights_status VARCHAR(40) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS extraction_batch (
 batch_id CHAR(64) PRIMARY KEY,
 source_id VARCHAR(80) NOT NULL,
 input_sha256 CHAR(64) NOT NULL,
 evidence_sha256 CHAR(64) NOT NULL,
 code_sha256 CHAR(64) NOT NULL,
 accessed_date DATE NOT NULL,
 method VARCHAR(255) NOT NULL,
 evidence_level VARCHAR(40) NOT NULL,
 FOREIGN KEY(source_id) REFERENCES source(source_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS unit (
 unit_code VARCHAR(40) PRIMARY KEY,
 description VARCHAR(255) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS production_context (
 context_id CHAR(64) PRIMARY KEY,
 source_id VARCHAR(80) NOT NULL,
 area VARCHAR(16) NOT NULL,
 block_label VARCHAR(255) NOT NULL,
 field_label VARCHAR(255) NOT NULL,
 CHECK(area IN ('onshore','offshore')),
 FOREIGN KEY(source_id) REFERENCES source(source_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS observation (
 record_id VARCHAR(80) NOT NULL,
 batch_id CHAR(64) NOT NULL,
 context_id CHAR(64) NOT NULL,
 period_start DATE NOT NULL,
 fuel_code VARCHAR(40) NOT NULL,
 raw_value VARCHAR(80) NOT NULL,
 amount DECIMAL(20,6) NOT NULL,
 unit_code VARCHAR(40) NOT NULL,
 evidence_locator VARCHAR(500) NOT NULL,
 review_status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
 PRIMARY KEY(batch_id, record_id),
 UNIQUE(batch_id, context_id, period_start, fuel_code, unit_code),
 CHECK(DAYOFMONTH(period_start)=1),
 CHECK(amount>=0),
 CHECK(fuel_code='natural_gas' AND unit_code='million_ft3_per_day'),
 CHECK(review_status='PENDING'),
 FOREIGN KEY(batch_id) REFERENCES extraction_batch(batch_id),
 FOREIGN KEY(context_id) REFERENCES production_context(context_id),
 FOREIGN KEY(unit_code) REFERENCES unit(unit_code)
) ENGINE=InnoDB;
CREATE OR REPLACE VIEW traceable_candidates AS
 SELECT o.*, c.area, c.block_label, c.field_label, s.url,
 b.input_sha256, b.evidence_sha256, b.accessed_date, b.evidence_level
 FROM observation o
 JOIN production_context c ON c.context_id=o.context_id
 JOIN extraction_batch b ON b.batch_id=o.batch_id
 JOIN source s ON s.source_id=b.source_id;
