-- Team reference-data model v1; separate from raw/source-specific research DB.
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS tamsood_reusable CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE tamsood_reusable;
CREATE TABLE IF NOT EXISTS publisher (
 publisher_id VARCHAR(40) PRIMARY KEY, name VARCHAR(255) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS document (
 document_id CHAR(64) PRIMARY KEY, publisher_id VARCHAR(40) NOT NULL,
 title VARCHAR(255) NOT NULL, report_year SMALLINT NOT NULL, source_url TEXT NOT NULL,
 accessed_at VARCHAR(40) NOT NULL, rights_status VARCHAR(80) NOT NULL,
 FOREIGN KEY(publisher_id) REFERENCES publisher(publisher_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS unit (
 unit_code VARCHAR(50) PRIMARY KEY, dimension VARCHAR(50) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS context (
 context_id CHAR(64) PRIMARY KEY, document_id CHAR(64) NOT NULL,
 source_scope VARCHAR(100) NOT NULL, description TEXT NOT NULL,
 geography_status VARCHAR(100) NOT NULL,
 FOREIGN KEY(document_id) REFERENCES document(document_id),
 UNIQUE(context_id,document_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS metric (
 metric_key CHAR(64) PRIMARY KEY, document_id CHAR(64) NOT NULL,
 source_metric_id VARCHAR(100) NOT NULL, label VARCHAR(255) NOT NULL,
 context_id CHAR(64) NOT NULL, unit_code VARCHAR(50) NOT NULL,
 data_kind VARCHAR(40) NOT NULL, aggregation_role VARCHAR(20) NOT NULL,
 CHECK(data_kind IN ('ORGANIZATION_INPUT','ORGANIZATION_OUTPUT','REPORTED_INTENSITY','CONTEXT_METRIC')),
 CHECK(aggregation_role IN ('TOTAL','COMPONENT','INTENSITY','CONTEXT','MEASURE')),
 FOREIGN KEY(document_id) REFERENCES document(document_id),
 FOREIGN KEY(context_id,document_id) REFERENCES context(context_id,document_id),
 FOREIGN KEY(unit_code) REFERENCES unit(unit_code),
 INDEX ix_document_metric(document_id,source_metric_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS observation (
 observation_id CHAR(64) PRIMARY KEY, metric_key CHAR(64) NOT NULL,
 reference_year SMALLINT NOT NULL, raw_value VARCHAR(100) NOT NULL,
 raw_unit_label VARCHAR(80) NOT NULL, scale_factor DECIMAL(30,12) NOT NULL,
 scaled_amount DECIMAL(30,12) NOT NULL,
 pdf_page INT NOT NULL, printed_page VARCHAR(20) NOT NULL, extracted_text_line INT NOT NULL,
 CHECK(reference_year BETWEEN 1900 AND 2100), CHECK(scale_factor>0), CHECK(scaled_amount>=0),
 CHECK(pdf_page>0 AND extracted_text_line>0),
 FOREIGN KEY(metric_key) REFERENCES metric(metric_key), UNIQUE(metric_key,reference_year),
 INDEX ix_reference_year(reference_year,metric_key)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS quality_issue (
 issue_id CHAR(64) PRIMARY KEY, document_id CHAR(64) NOT NULL,
 source_issue_id VARCHAR(200) NOT NULL, reason TEXT NOT NULL,
 FOREIGN KEY(document_id) REFERENCES document(document_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS issue_observation (
 issue_id CHAR(64) NOT NULL, observation_id CHAR(64) NOT NULL,
 PRIMARY KEY(issue_id,observation_id),
 FOREIGN KEY(issue_id) REFERENCES quality_issue(issue_id),
 FOREIGN KEY(observation_id) REFERENCES observation(observation_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS review (
 observation_id CHAR(64) NOT NULL, decision VARCHAR(40) NOT NULL,
 policy_version VARCHAR(40) NOT NULL, review_actor VARCHAR(80) NOT NULL,
 trace_verification VARCHAR(80) NOT NULL,
 PRIMARY KEY(observation_id,policy_version),
 CHECK(decision IN ('ACCEPTED_REFERENCE','HOLD_CONTEXT')),
 FOREIGN KEY(observation_id) REFERENCES observation(observation_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS data_release (
 release_id CHAR(64) PRIMARY KEY, policy_version VARCHAR(40) NOT NULL,
 usage_profile VARCHAR(80) NOT NULL, created_at VARCHAR(40) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS release_observation (
 release_id CHAR(64) NOT NULL, observation_id CHAR(64) NOT NULL,
 PRIMARY KEY(release_id,observation_id),
 FOREIGN KEY(release_id) REFERENCES data_release(release_id),
 FOREIGN KEY(observation_id) REFERENCES observation(observation_id)
) ENGINE=InnoDB;
CREATE OR REPLACE VIEW reference_catalog AS
 SELECT ro.release_id,dr.usage_profile,o.*,m.label,m.source_metric_id,m.data_kind,m.aggregation_role,
 m.unit_code,c.source_scope,c.description AS boundary_note,c.geography_status,
 d.document_id AS pdf_sha256,d.source_url,d.report_year,d.accessed_at,d.rights_status,
 p.name AS publisher,r.decision,r.policy_version,r.review_actor,r.trace_verification
 FROM release_observation ro JOIN data_release dr USING(release_id) JOIN observation o USING(observation_id)
 JOIN metric m USING(metric_key) JOIN context c ON c.context_id=m.context_id
 JOIN document d ON d.document_id=m.document_id JOIN publisher p USING(publisher_id)
 JOIN review r ON r.observation_id=o.observation_id AND r.policy_version=dr.policy_version;
CREATE OR REPLACE VIEW accepted_reference AS SELECT * FROM reference_catalog
 WHERE decision='ACCEPTED_REFERENCE';
