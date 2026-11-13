-- AR-2 acceptance for tamsood_research (DMF). PREPARED, NOT APPLIED, NOT TESTED ON THE SERVER.
-- Review and run by hand inside a transaction on a restored copy first.
-- Rule and counts: docs/acceptance-rules.md, docs/acceptance-ledger.json (13 Nov 2026).
USE tamsood_research;

-- 1. The current schema pins review_status to 'PENDING' with an unnamed CHECK.
--    Find its generated name, then drop it:
--    SELECT CONSTRAINT_NAME, CHECK_CLAUSE FROM information_schema.CHECK_CONSTRAINTS
--    WHERE CONSTRAINT_SCHEMA='tamsood_research' AND CHECK_CLAUSE LIKE '%review_status%';
--    ALTER TABLE observation DROP CHECK <name_from_query>;
ALTER TABLE observation
  MODIFY review_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  ADD CONSTRAINT ck_observation_review_status
    CHECK (review_status IN ('PENDING','ACCEPTED_SOURCE_STATISTIC','HOLD_MAGNITUDE','HOLD_UNIT_LABEL'));

-- 2. Hold the rows AR-2 does not accept even though they are unique.
UPDATE observation o JOIN production_context c USING(context_id)
SET o.review_status='HOLD_UNIT_LABEL'
WHERE c.source_group LIKE '%LPG%' OR LOWER(c.source_group) LIKE '%kgs%';          -- expected 3 rows

UPDATE observation o JOIN production_context c USING(context_id)
SET o.review_status='HOLD_MAGNITUDE'
WHERE c.package='production-natural-gas' AND o.period_start='2020-02-01'
  AND o.amount=3500000;                                                           -- expected 1 row

-- 3. Accept unique, source-verified rows.
UPDATE observation o JOIN duplicate_disposition d USING(snapshot_id, source_line)
SET o.review_status='ACCEPTED_SOURCE_STATISTIC'
WHERE d.status IN ('SINGLETON','EXACT_REPRESENTATIVE') AND o.review_status='PENDING';  -- expected 34,667 rows

-- 4. Verify before COMMIT:
--    SELECT review_status, COUNT(*) FROM observation GROUP BY review_status;
--    Expected: ACCEPTED_SOURCE_STATISTIC 34667, HOLD_UNIT_LABEL 3, HOLD_MAGNITUDE 1, PENDING 228
--    (228 = 186 conflicting + 42 exact copies, which keep their duplicate_disposition status).
-- unit_time_basis stays 'UNCONFIRMED': acceptance does not confirm the time basis.
