USE tamsood_reusable;
-- Always select a release; joining all historical releases would double-count observations.
SET @release_id=(SELECT release_id FROM data_release ORDER BY created_at DESC,release_id DESC LIMIT 1);

-- Count records by suitability/type, not as independent flows.
SELECT decision,data_kind,aggregation_role,COUNT(*) AS record_count
FROM reference_catalog WHERE release_id=@release_id
GROUP BY decision,data_kind,aggregation_role;

-- A source-specific reported ratio; no derived product-normalization is implied.
SELECT publisher,reference_year,scaled_amount,unit_code,boundary_note,source_url,pdf_page
FROM accepted_reference WHERE release_id=@release_id
AND publisher='Star Petroleum Refining Public Company Limited'
AND source_metric_id='fuel_intensity' AND reference_year=2024;

-- Inputs with units and scope exposed. Do not sum totals and components together.
SELECT publisher,reference_year,label,scaled_amount,unit_code,aggregation_role,source_scope
FROM accepted_reference WHERE release_id=@release_id AND data_kind='ORGANIZATION_INPUT'
ORDER BY publisher,reference_year,source_metric_id;

-- Show evidence for every member of unresolved issues.
SELECT qi.source_issue_id,qi.reason,c.label,c.reference_year,c.raw_value,c.raw_unit_label,c.pdf_page,c.source_url
FROM quality_issue qi JOIN issue_observation io USING(issue_id)
JOIN reference_catalog c ON c.observation_id=io.observation_id
WHERE c.release_id=@release_id ORDER BY qi.source_issue_id,c.label;
