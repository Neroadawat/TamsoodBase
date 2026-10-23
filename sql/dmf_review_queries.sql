-- SQLite review database: build/dmf/<run_id>/candidates.sqlite
-- Status counts preserve every structurally valid source row.
SELECT package,status,COUNT(*) AS row_count
FROM duplicate_disposition GROUP BY package,status ORDER BY package,status;

-- All members of conflicts, including the first occurrence.
SELECT c.package,c.identity_sha256,c.source_line,c.source_group,c.raw_value,s.raw_json
FROM candidate c JOIN duplicate_disposition d USING(package,source_line)
JOIN staging s USING(package,source_line)
WHERE d.status='HOLD_CONFLICT'
ORDER BY c.package,c.identity_sha256,c.source_line;

-- Data pending review, never competition accepted.
SELECT package,COUNT(*) AS pending_candidates FROM deduplicated_candidates GROUP BY package;
