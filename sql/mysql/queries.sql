USE tamsood_pilot;
-- Trace one candidate through context, batch and source (4-table JOIN via view).
SELECT record_id, field_label, amount, unit_code, period_start,
       url, evidence_locator, evidence_level, review_status
FROM traceable_candidates ORDER BY record_id;

-- Coverage count only: do not add rates across months or overlapping fields.
SELECT period_start, area, fuel_code, unit_code, COUNT(*) AS candidate_count
FROM traceable_candidates
GROUP BY period_start, area, fuel_code, unit_code
HAVING COUNT(*) >= 1;

-- LEFT JOIN identifies registered sources with no imported observations.
SELECT s.source_id, COUNT(o.record_id) AS candidate_count
FROM source s LEFT JOIN extraction_batch b ON b.source_id=s.source_id
LEFT JOIN observation o ON o.batch_id=b.batch_id
GROUP BY s.source_id;

-- PENDING is deliberately not equivalent to competition accepted.
SELECT review_status, COUNT(*) AS candidate_count
FROM observation GROUP BY review_status;
