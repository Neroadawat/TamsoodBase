-- AR-2 acceptance for tamsood_research (DMF).
-- Rule and counts: docs/acceptance-rules.md, docs/acceptance-ledger.json (13 Nov 2026).
-- Tested on MySQL 8.4 with a fixture (tests/sql/acceptance-ar2-fixture.sql); NOT yet applied to the server.
-- Take a backup first. Step 1 is DDL and commits implicitly; step 2 runs in one transaction.
USE tamsood_research;

-- 1. The schema pins review_status to 'PENDING' with an auto-named CHECK and a VARCHAR(20)
--    that is too short for the new value. Drop that CHECK by looking up its name, widen the
--    column, and add a named CHECK listing the allowed states.
SET @check_name = (
  SELECT cc.CONSTRAINT_NAME
  FROM information_schema.CHECK_CONSTRAINTS cc
  JOIN information_schema.TABLE_CONSTRAINTS tc
    ON tc.CONSTRAINT_SCHEMA = cc.CONSTRAINT_SCHEMA AND tc.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
  WHERE cc.CONSTRAINT_SCHEMA = 'tamsood_research' AND tc.TABLE_NAME = 'observation'
    AND cc.CHECK_CLAUSE LIKE '%review_status%'
  LIMIT 1
);
SET @drop_sql = IF(@check_name IS NULL OR @check_name = 'ck_observation_review_status',
  'DO 0', CONCAT('ALTER TABLE observation DROP CHECK `', @check_name, '`'));
PREPARE drop_stmt FROM @drop_sql;
EXECUTE drop_stmt;
DEALLOCATE PREPARE drop_stmt;

SET @add_sql = IF(@check_name = 'ck_observation_review_status', 'DO 0',
  'ALTER TABLE observation
     MODIFY review_status VARCHAR(32) NOT NULL DEFAULT ''PENDING'',
     ADD CONSTRAINT ck_observation_review_status
       CHECK (review_status IN (''PENDING'',''ACCEPTED_SOURCE_STATISTIC'',''HOLD_MAGNITUDE'',''HOLD_UNIT_LABEL''))');
PREPARE add_stmt FROM @add_sql;
EXECUTE add_stmt;
DEALLOCATE PREPARE add_stmt;

-- 2. Apply the rule. Safe to re-run: every UPDATE only touches rows still PENDING.
START TRANSACTION;

-- Unique rows AR-2 does not accept: the source label itself names another unit.
UPDATE observation o JOIN production_context c USING (context_id)
SET o.review_status = 'HOLD_UNIT_LABEL'
WHERE o.review_status = 'PENDING'
  AND (c.source_group LIKE '%LPG%' OR LOWER(c.source_group) LIKE '%kgs%');       -- expected 3 rows

-- Unique row AR-2 does not accept: magnitude far outside the rest of the dataset.
UPDATE observation o JOIN production_context c USING (context_id)
SET o.review_status = 'HOLD_MAGNITUDE'
WHERE o.review_status = 'PENDING'
  AND c.package = 'production-natural-gas' AND o.period_start = '2020-02-01'
  AND o.amount = 3500000;                                                         -- expected 1 row

-- Accept unique, source-verified rows.
UPDATE observation o JOIN duplicate_disposition d USING (snapshot_id, source_line)
SET o.review_status = 'ACCEPTED_SOURCE_STATISTIC'
WHERE o.review_status = 'PENDING'
  AND d.status IN ('SINGLETON', 'EXACT_REPRESENTATIVE');                          -- expected 34,667 rows

-- Check before committing. Expected on the 22 Oct 2026 snapshot:
--   ACCEPTED_SOURCE_STATISTIC 34667 · HOLD_UNIT_LABEL 3 · HOLD_MAGNITUDE 1 · PENDING 228
--   (228 = 186 conflicting + 42 exact copies; they keep their duplicate_disposition status).
SELECT review_status, COUNT(*) AS row_count FROM observation GROUP BY review_status ORDER BY review_status;

COMMIT;
-- unit_time_basis stays 'UNCONFIRMED': acceptance does not confirm the time basis.
-- The views traceable_observations and deduplicated_pending select o.* and need no change;
-- deduplicated_pending now also contains accepted rows, so read review_status rather than the view name.
