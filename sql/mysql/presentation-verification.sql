-- Read-only checks for the queries shown on the 3-minute slides and the poster (block 5 and 6).
-- Run by someone who can reach the MySQL server; SELECT only, no data is changed.
-- Save the output next to evidence/ so the slides can say "run against MySQL on <date>".

-- ===== Slide 5 / poster block 6: crude oil, March 2026 (top 4) =====
-- Expected (from the API parity check of 15 Nov 2026):
--   เบญจมาศ 19337.54839 line 11399 | Sirikit และอื่นๆ ใน S1 18557 line 11425
--   ปลาทอง 11760.67294 line 11407 | นงเยาว์ 9703.50129 line 11402 ; 34 rows in that month
USE tamsood_research;
SELECT source_group, area, raw_value, metadata_unit, source_line, csv_sha256
FROM deduplicated_pending
WHERE product_code = 'crude_oil' AND period_start = '2026-03-01'
ORDER BY amount DESC
LIMIT 4;

SELECT COUNT(*) AS rows_in_month
FROM deduplicated_pending
WHERE product_code = 'crude_oil' AND period_start = '2026-03-01';

-- The view name is legacy: it keeps SINGLETON / EXACT_REPRESENTATIVE rows only and is NOT an accepted-only view.
-- Accepted-only variant (confirm the four rows above are ACCEPTED_SOURCE_STATISTIC):
SELECT source_group, source_line, review_status
FROM deduplicated_pending
WHERE product_code = 'crude_oil' AND period_start = '2026-03-01'
ORDER BY amount DESC
LIMIT 4;

-- ===== Poster block 5: Q1 and Q2 (inventory exchanges) =====
-- Expected: Q1 returns 8 rows for FAME INPUT; Q2 returns FAME INPUT 8 / OUTPUT 2, H-FAME INPUT 5 / OUTPUT 1.
USE tamsood_supplemental;
SELECT ie.flow, o.amount, o.unit_code
FROM inventory_exchange ie JOIN observation o USING (snapshot_id, observation_id)
WHERE ie.process_id = 'FAME' AND ie.direction = 'INPUT';

SELECT process_id, direction, COUNT(*) AS exchanges
FROM inventory_exchange
GROUP BY process_id, direction
ORDER BY process_id, direction;
