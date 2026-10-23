PRAGMA foreign_keys = ON;
CREATE TABLE source (
 source_id TEXT PRIMARY KEY, publisher TEXT NOT NULL, url TEXT NOT NULL,
 rights_status TEXT NOT NULL
);
CREATE TABLE batch (
 batch_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source,
 input_sha256 TEXT NOT NULL, evidence_sha256 TEXT NOT NULL,
 code_sha256 TEXT NOT NULL, created_at TEXT NOT NULL, method TEXT NOT NULL
);
CREATE TABLE unit (code TEXT PRIMARY KEY, description TEXT NOT NULL);
CREATE TABLE observation (
 record_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batch,
 period TEXT NOT NULL, area TEXT NOT NULL CHECK(area IN ('onshore','offshore')),
 block TEXT NOT NULL, field TEXT NOT NULL, fuel TEXT NOT NULL,
 raw_value TEXT NOT NULL, value_decimal TEXT NOT NULL,
 unit_code TEXT NOT NULL REFERENCES unit(code), evidence_locator TEXT NOT NULL,
 technical_status TEXT NOT NULL CHECK(technical_status = 'PASS'),
 review_status TEXT NOT NULL CHECK(review_status = 'PENDING'),
 UNIQUE(batch_id, period, area, block, field, fuel, unit_code)
);
CREATE TABLE rejected_record (
 row_number INTEGER PRIMARY KEY, raw_json TEXT NOT NULL, reasons_json TEXT NOT NULL
);
CREATE VIEW traceable_candidates AS
 SELECT o.*, s.url, b.input_sha256, b.evidence_sha256, b.method
 FROM observation o JOIN batch b USING(batch_id) JOIN source s USING(source_id);
