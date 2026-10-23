-- Full DMF research database v1. Keeps all original rows and unresolved reviews.
SET NAMES utf8mb4;
SET SESSION sql_mode='STRICT_ALL_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
CREATE DATABASE IF NOT EXISTS tamsood_research CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE tamsood_research;
CREATE TABLE IF NOT EXISTS publisher (
 publisher_id VARCHAR(40) PRIMARY KEY, name VARCHAR(255) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS product (
 product_code VARCHAR(40) PRIMARY KEY, name_th VARCHAR(255) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS source_resource (
 package VARCHAR(80) PRIMARY KEY, publisher_id VARCHAR(40) NOT NULL,
 product_code VARCHAR(40) NOT NULL, title VARCHAR(255) NOT NULL,
 FOREIGN KEY(publisher_id) REFERENCES publisher(publisher_id),
 FOREIGN KEY(product_code) REFERENCES product(product_code)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS resource_snapshot (
 snapshot_id CHAR(64) PRIMARY KEY, package VARCHAR(80) NOT NULL,
 acquisition_run VARCHAR(40) NOT NULL, acquired_at VARCHAR(40) NOT NULL,
 csv_url TEXT NOT NULL, csv_sha256 CHAR(64) NOT NULL, metadata_sha256 CHAR(64) NOT NULL,
 metadata_unit VARCHAR(80), metadata_multiplier VARCHAR(40), license_label VARCHAR(80),
 metadata_json JSON NOT NULL,
 FOREIGN KEY(package) REFERENCES source_resource(package),
 UNIQUE(package,csv_sha256,metadata_sha256)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS source_record (
 snapshot_id CHAR(64) NOT NULL, source_line INT NOT NULL,
 raw_json JSON NOT NULL, record_content_sha256 CHAR(64) NOT NULL,
 PRIMARY KEY(snapshot_id,source_line),
 CHECK(source_line>=2), FOREIGN KEY(snapshot_id) REFERENCES resource_snapshot(snapshot_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS production_context (
 context_id CHAR(64) PRIMARY KEY, package VARCHAR(80) NOT NULL,
 area VARCHAR(16) NOT NULL, block_label VARCHAR(255), source_group VARCHAR(255) NOT NULL,
 CHECK(area IN ('บนบก','ในทะเล')),
 FOREIGN KEY(package) REFERENCES source_resource(package)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS observation (
 snapshot_id CHAR(64) NOT NULL, source_line INT NOT NULL, context_id CHAR(64) NOT NULL,
 period_start DATE NOT NULL, raw_value VARCHAR(100) NOT NULL,
 amount DECIMAL(30,12) NOT NULL, production_days TINYINT NOT NULL,
 identity_sha256 CHAR(64) NOT NULL,
 unit_time_basis VARCHAR(20) NOT NULL DEFAULT 'UNCONFIRMED',
 review_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
 PRIMARY KEY(snapshot_id,source_line),
 CHECK(amount>=0), CHECK(DAYOFMONTH(period_start)=1),
 CHECK(production_days BETWEEN 0 AND DAYOFMONTH(LAST_DAY(period_start))),
 CHECK(unit_time_basis='UNCONFIRMED'), CHECK(review_status='PENDING'),
 FOREIGN KEY(snapshot_id,source_line) REFERENCES source_record(snapshot_id,source_line),
 FOREIGN KEY(context_id) REFERENCES production_context(context_id),
 INDEX ix_period_context(period_start,context_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS duplicate_disposition (
 snapshot_id CHAR(64) NOT NULL, source_line INT NOT NULL, status VARCHAR(32) NOT NULL,
 representative_line INT, PRIMARY KEY(snapshot_id,source_line),
 CHECK(status IN ('SINGLETON','EXACT_REPRESENTATIVE','EXCLUDE_EXACT_COPY','HOLD_CONFLICT')),
 CHECK((status='EXCLUDE_EXACT_COPY' AND representative_line IS NOT NULL) OR
       (status<>'EXCLUDE_EXACT_COPY' AND representative_line IS NULL)),
 FOREIGN KEY(snapshot_id,source_line) REFERENCES observation(snapshot_id,source_line),
 FOREIGN KEY(snapshot_id,representative_line) REFERENCES observation(snapshot_id,source_line)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS rejected_record (
 snapshot_id CHAR(64) NOT NULL, source_line INT NOT NULL, reasons_json JSON NOT NULL,
 PRIMARY KEY(snapshot_id,source_line),
 FOREIGN KEY(snapshot_id,source_line) REFERENCES source_record(snapshot_id,source_line)
) ENGINE=InnoDB;
CREATE OR REPLACE VIEW traceable_observations AS
 SELECT o.*,c.area,c.block_label,c.source_group,s.package,r.product_code,
        s.csv_url,s.csv_sha256,s.metadata_sha256,s.metadata_unit,s.metadata_multiplier,
        s.license_label,s.acquired_at,d.status AS duplicate_status
 FROM observation o JOIN production_context c USING(context_id)
 JOIN resource_snapshot s ON s.snapshot_id=o.snapshot_id
 JOIN source_resource r ON r.package=s.package
 JOIN duplicate_disposition d ON d.snapshot_id=o.snapshot_id AND d.source_line=o.source_line;
CREATE OR REPLACE VIEW deduplicated_pending AS
 SELECT * FROM traceable_observations WHERE duplicate_status IN ('SINGLETON','EXACT_REPRESENTATIVE');
