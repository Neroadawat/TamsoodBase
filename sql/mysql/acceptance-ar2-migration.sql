-- MySQL 8.4, DMF snapshot 20261022T151321110294Z. Run with the mysql client.
-- Back up before use. The atomic schema ALTER commits separately from row updates.
USE tamsood_research;

SET @old_check = (
  SELECT cc.CONSTRAINT_NAME
  FROM information_schema.CHECK_CONSTRAINTS cc
  JOIN information_schema.TABLE_CONSTRAINTS tc
    USING (CONSTRAINT_SCHEMA, CONSTRAINT_NAME)
  WHERE cc.CONSTRAINT_SCHEMA = DATABASE() AND tc.TABLE_NAME = 'observation'
    AND cc.CHECK_CLAUSE LIKE '%review_status%'
);
SET @alter_sql = IF(@old_check = 'ck_observation_review_status', 'DO 0',
  CONCAT('ALTER TABLE observation ',
    IF(@old_check IS NULL, '', CONCAT('DROP CHECK `', REPLACE(@old_check, '`', '``'), '`, ')),
    'MODIFY review_status VARCHAR(32) NOT NULL DEFAULT ''PENDING'',
     ADD CONSTRAINT ck_observation_review_status
     CHECK (review_status IN (''PENDING'',''ACCEPTED_SOURCE_STATISTIC'',''HOLD_MAGNITUDE'',''HOLD_UNIT_LABEL''))'));
PREPARE ar2_alter FROM @alter_sql;
EXECUTE ar2_alter;
DEALLOCATE PREPARE ar2_alter;

DROP PROCEDURE IF EXISTS migrate_dmf_ar2_20261022;
DELIMITER //
CREATE PROCEDURE migrate_dmf_ar2_20261022()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    DROP TEMPORARY TABLE IF EXISTS ar2_expected;
    RESIGNAL;
  END;

  SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  START TRANSACTION;
  CREATE TEMPORARY TABLE ar2_expected (
    snapshot_id CHAR(64) NOT NULL, source_line INT NOT NULL,
    expected_status VARCHAR(32) NOT NULL,
    PRIMARY KEY (snapshot_id, source_line)
  ) ENGINE=InnoDB;

  INSERT INTO ar2_expected
  SELECT o.snapshot_id, o.source_line,
    CASE
      WHEN d.status IN ('EXCLUDE_EXACT_COPY','HOLD_CONFLICT') THEN 'PENDING'
      WHEN c.source_group LIKE '%LPG%' OR LOWER(c.source_group) LIKE '%kgs%' THEN 'HOLD_UNIT_LABEL'
      WHEN c.package = 'production-natural-gas' AND o.period_start = '2020-02-01'
           AND o.amount = 3500000 THEN 'HOLD_MAGNITUDE'
      WHEN d.status IN ('SINGLETON','EXACT_REPRESENTATIVE') THEN 'ACCEPTED_SOURCE_STATISTIC'
    END
  FROM observation o
  JOIN production_context c USING (context_id)
  JOIN duplicate_disposition d USING (snapshot_id, source_line)
  WHERE o.snapshot_id IN (
    '69af636f95011438feb0f11b6cb01bce1f9d1f82b1d476df11dc398c254137be',
    '553bdffc57e07a18948da0514ec3dc1ff0e9c748fd46cd18b751a169f472cb3c',
    '9461da0da4ab039d0c9dbb041f6cf613d5243a20f1780669496cf294ac318d68'
  );

  IF (SELECT COUNT(*) FROM observation) <> 34899 OR NOT EXISTS (
    SELECT COUNT(*) FROM ar2_expected
    HAVING COUNT(*) = 34899 AND SUM(expected_status = 'ACCEPTED_SOURCE_STATISTIC') = 34667
       AND SUM(expected_status = 'HOLD_UNIT_LABEL') = 3 AND SUM(expected_status = 'HOLD_MAGNITUDE') = 1
       AND SUM(expected_status = 'PENDING') = 228
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'AR-2 source rows or expected status totals differ from the 22 Oct ledger';
  END IF;

  UPDATE observation o JOIN ar2_expected e USING (snapshot_id, source_line)
  SET o.review_status = e.expected_status
  WHERE o.review_status = 'PENDING' AND e.expected_status <> 'PENDING';

  IF EXISTS (
    SELECT 1 FROM observation o JOIN ar2_expected e USING (snapshot_id, source_line)
    WHERE o.review_status <> e.expected_status
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'AR-2 row status mismatch; status updates rolled back';
  END IF;
  DROP TEMPORARY TABLE ar2_expected;
  COMMIT;
END//
DELIMITER ;
CALL migrate_dmf_ar2_20261022();
DROP PROCEDURE migrate_dmf_ar2_20261022;
SELECT review_status, COUNT(*) AS row_count FROM observation GROUP BY review_status ORDER BY review_status;
