-- Read-only API projections over typed project schemas. Presentation text preserves
-- original decimal strings/JSON formatting; it does not replace typed observations.
CREATE DATABASE IF NOT EXISTS tamsood_api CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE tamsood_api;
CREATE TABLE artifact(name VARCHAR(100) PRIMARY KEY,payload JSON NOT NULL) ENGINE=InnoDB;
CREATE TABLE current_dmf(package VARCHAR(80) PRIMARY KEY,snapshot_id CHAR(64) NOT NULL,
 FOREIGN KEY(snapshot_id) REFERENCES tamsood_research.resource_snapshot(snapshot_id)) ENGINE=InnoDB;
CREATE TABLE raw_representation(snapshot_id CHAR(64) NOT NULL,source_line INT NOT NULL,raw_text LONGTEXT NOT NULL,
 PRIMARY KEY(snapshot_id,source_line),FOREIGN KEY(snapshot_id,source_line) REFERENCES tamsood_research.source_record(snapshot_id,source_line)) ENGINE=InnoDB;
CREATE TABLE candidate_representation(snapshot_id CHAR(64) NOT NULL,source_line INT NOT NULL,
 decimal_value VARCHAR(100) NOT NULL,production_days_text VARCHAR(10) NOT NULL,duplicate_of_line INT NULL,
 PRIMARY KEY(snapshot_id,source_line),FOREIGN KEY(snapshot_id,source_line) REFERENCES tamsood_research.observation(snapshot_id,source_line)) ENGINE=InnoDB;
CREATE TABLE row_order(dataset VARCHAR(30) NOT NULL,observation_id CHAR(64) NOT NULL,ordinal INT NOT NULL,
 PRIMARY KEY(dataset,observation_id),UNIQUE(dataset,ordinal)) ENGINE=InnoDB;
CREATE TABLE reference_representation(observation_id CHAR(64) PRIMARY KEY,payload JSON NOT NULL,
 FOREIGN KEY(observation_id) REFERENCES tamsood_reusable.observation(observation_id)) ENGINE=InnoDB;
CREATE OR REPLACE VIEW candidate AS
 SELECT s.package,o.source_line,YEAR(o.period_start) AS year_ce,MONTH(o.period_start) AS month,
 c.area,c.block_label,c.source_group,
 CASE s.package WHEN 'production-oil' THEN 'OIL' WHEN 'production-condensate' THEN 'CONDENSATE' ELSE 'GAS' END AS amount_column,
 o.raw_value,p.decimal_value,p.production_days_text AS production_days,o.identity_sha256,p.duplicate_of_line,o.review_status
 FROM tamsood_research.observation o JOIN current_dmf s USING(snapshot_id)
 JOIN tamsood_research.production_context c USING(context_id)
 JOIN candidate_representation p ON p.snapshot_id=o.snapshot_id AND p.source_line=o.source_line;
CREATE OR REPLACE VIEW duplicate_disposition AS
 SELECT s.package,d.source_line,d.status,d.representative_line FROM tamsood_research.duplicate_disposition d JOIN current_dmf s USING(snapshot_id);
CREATE OR REPLACE VIEW resource AS
 SELECT c.package,s.csv_url AS url,s.csv_sha256,s.metadata_sha256,s.license_label,s.metadata_unit,s.acquired_at
 FROM current_dmf c JOIN tamsood_research.resource_snapshot s USING(snapshot_id);
CREATE OR REPLACE VIEW staging AS
 SELECT c.package,r.source_line,r.raw_text AS raw_json FROM raw_representation r JOIN current_dmf c USING(snapshot_id);
CREATE OR REPLACE VIEW traceable_candidate AS
 SELECT c.*,r.url,r.csv_sha256,r.metadata_unit,r.license_label,r.acquired_at,s.raw_json
 FROM candidate c JOIN resource r USING(package) JOIN staging s USING(package,source_line);
CREATE OR REPLACE VIEW deduplicated_candidates AS
 SELECT c.* FROM candidate c JOIN duplicate_disposition d USING(package,source_line)
 WHERE d.status IN ('SINGLETON','EXACT_REPRESENTATIVE');
