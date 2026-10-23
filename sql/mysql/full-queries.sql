USE tamsood_research;
-- Counts by review disposition; never represent these as accepted LCI totals.
SELECT package,duplicate_status,COUNT(*) AS rows_in_status
FROM traceable_observations GROUP BY package,duplicate_status ORDER BY package,duplicate_status;

-- Search by product and period, with all provenance fields available in the view.
SELECT package,source_group,period_start,amount,metadata_multiplier,metadata_unit,
       unit_time_basis,csv_url,source_line,csv_sha256
FROM deduplicated_pending
WHERE product_code='natural_gas' AND period_start='2026-01-01'
ORDER BY source_group;

-- Coverage at a compatible grain. Counts only, never sum rates across months.
SELECT product_code,YEAR(period_start) AS year_ce,area,COUNT(*) AS pending_records
FROM deduplicated_pending GROUP BY product_code,YEAR(period_start),area
HAVING COUNT(*)>0 ORDER BY product_code,year_ce,area;

-- Registered resources with no records (LEFT JOIN).
SELECT r.package,COUNT(o.source_line) AS observation_count
FROM source_resource r LEFT JOIN resource_snapshot s ON s.package=r.package
LEFT JOIN observation o ON o.snapshot_id=s.snapshot_id
GROUP BY r.package;
