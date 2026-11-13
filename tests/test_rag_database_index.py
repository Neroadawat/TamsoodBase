import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scripts.build_rag_database_index import (
    canonical_url,
    classify_source,
    create_index,
    fts_query,
    normalize_record,
    search_records,
    search_text,
    snapshot_freshness,
    source_activity_metadata,
)


class RagDatabaseIndexTests(unittest.TestCase):
    def test_source_layers_match_the_catalog_rules(self):
        self.assertEqual(classify_source("DMF-CKAN-GAS"), "DMF")
        self.assertEqual(classify_source("THAIOIL-REPORT-2024"), "COMPANY")
        self.assertEqual(classify_source("NSO-SYB2026-13.5"), "NSO")
        self.assertEqual(classify_source("EPPO-11_13"), "EPPO")
        self.assertEqual(classify_source("MDPI-SU12229415-T4"), "RESEARCH")
        self.assertEqual(classify_source("GHG-PROTOCOL-2025"), "SUPPORTING")

    def test_canonical_url_discards_article_locator_fragment(self):
        self.assertEqual(
            canonical_url("https://www.mdpi.com/2071-1050/12/22/9415#table4"),
            "https://www.mdpi.com/2071-1050/12/22/9415",
        )

    def test_normalized_record_keeps_provenance_unknowns_and_closed_rights(self):
        record = normalize_record(
            {
                "observation_id": "obs-1",
                "reference_year": 2024,
                "amount": "12.50",
                "unit": "BBL/DAY",
                "scope": "COMPANY_REFINERY_STATISTIC",
                "status": "STAGED_SOURCE_VERIFIED",
                "source_line": 7,
                "source_column": "Quantity",
                "source_sha256": "a" * 64,
            },
            "EPPO",
            {"source_id": "EPPO-11_13", "publisher": "EPPO", "rights_status": "reuse_unknown"},
            "obs-1",
        )
        self.assertEqual(record["record_id"], "obs-1")
        self.assertEqual(record["reference_year"], 2024)
        self.assertEqual(record["unit"], "BBL/DAY")
        self.assertIn('"source_line": 7', record["locator_json"])
        self.assertEqual(record["source_rights_status"], "reuse_unknown")
        self.assertEqual(record["release_allowed"], 0)
        self.assertEqual(record["external_llm_allowed"], 0)
        self.assertIsNone(record["publication_year"])

    def test_dmf_index_points_to_original_row_without_copying_duplicate_raw_json(self):
        record = normalize_record(
            {"package": "production-natural-gas", "source_line": 2, "csv_sha256": "c" * 64,
             "raw_json": {"well": "name", "value": "100"}, "review_status": "PENDING"},
            "DMF", {"source_id": "DMF-CKAN-GAS", "rights_status": "reuse_supported_metadata_anomaly"},
            "DMF:production-natural-gas:2", source_line=2,
        )
        payload = json.loads(record["payload_json"])
        self.assertNotIn("raw_json", payload)
        self.assertEqual(payload["source_payload_pointer"]["source_line"], 2)
        self.assertEqual(payload["source_payload_pointer"]["source_sha256"], "c" * 64)

    def test_thai_bigrams_support_fts_queries_without_rewriting_payload(self):
        text = search_text(["ปริมาณก๊าซธรรมชาติ", "STAGED_SOURCE_VERIFIED"])
        self.assertIn("ธรรม", text)
        self.assertIn("ก๊าซธรรมชาติ", text)
        self.assertIn('"รม"', fts_query("ธรรม"))

    def test_snapshot_mtime_is_not_claimed_as_freshness_or_live_database_state(self):
        result = snapshot_freshness([
            {"modified_at": "2026-10-22T00:00:00+00:00"},
            {"modified_at": "2026-11-09T00:00:00+00:00"},
        ])
        self.assertEqual(result["basis"], "LOCAL_FILE_MTIME_ONLY")
        self.assertFalse(result["live_database_read"])
        self.assertFalse(result["freshness_attested"])
        self.assertEqual(result["oldest_input_modified_at"], "2026-10-22T00:00:00+00:00")
        self.assertEqual(result["newest_input_modified_at"], "2026-11-09T00:00:00+00:00")
        empty = snapshot_freshness([])
        self.assertIsNone(empty["oldest_input_modified_at"])
        self.assertIsNone(empty["newest_input_modified_at"])

    def test_source_activity_distinguishes_acquisition_access_and_review_times(self):
        activity = source_activity_metadata()
        for layer in ("DMF", "NSO", "EPPO"):
            self.assertEqual(activity[layer]["timestamp_type"], "source_acquired_at")
            self.assertGreater(activity[layer]["count"], 0)
            self.assertIsNotNone(activity[layer]["oldest"])
        self.assertEqual(activity["COMPANY"]["timestamp_type"], "source_accessed_at")
        self.assertEqual(activity["RESEARCH"]["timestamp_type"], "local_validation_checked_at")
        self.assertIn("not source-acquisition", activity["RESEARCH"]["basis"])
        self.assertEqual(activity["SUPPORTING"]["timestamp_type"], "unknown")

    def test_private_fts_database_is_searchable_and_cannot_release_rows(self):
        source = {"source_id": "NSO-TEST", "publisher": "NSO", "title": "ข้อมูลก๊าซ"}
        row = normalize_record(
            {"observation_id": "nso-1", "label": "ปริมาณก๊าซธรรมชาติ", "reference_year": 2024,
             "unit": "TJ", "status": "STAGED_SOURCE_VERIFIED", "source_line": 4,
             "source_sha256": "b" * 64},
            "NSO", source, "nso-1")
        row["search_text"] = search_text(["ข้อมูลก๊าซ", "ปริมาณก๊าซธรรมชาติ", "2024", "TJ"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private.sqlite"
            result = create_index(path, [row], [])
            self.assertEqual(result, {"record_count": 1, "fts_count": 1, "public_count": 0})
            con = sqlite3.connect(path)
            try:
                # Public and external-model searches fail closed; local review is explicit.
                self.assertEqual(search_records(path, "ธรรม"), [])
                self.assertEqual(search_records(path, "ธรรม", audience="external_llm"), [])
                hit = search_records(path, "ธรรม", audience="internal")[0]
                self.assertEqual(hit["record_id"], "nso-1")
                self.assertEqual(hit["release_allowed"], 0)
                self.assertEqual(hit["external_llm_allowed"], 0)
                self.assertIn('"source_line": 4', hit["locator_json"])
                self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                metadata = dict((key, json.loads(value)) for key, value in con.execute("SELECT * FROM metadata"))
                self.assertEqual(metadata["visibility"], "PRIVATE_INTERNAL_SNAPSHOT_ONLY")
                self.assertFalse(metadata["public_release_allowed"])
                self.assertFalse(metadata["external_llm_allowed"])
            finally:
                con.close()

    def test_search_rejects_unknown_audience_instead_of_weakening_rights_filter(self):
        with self.assertRaises(ValueError):
            search_records("does-not-need-to-exist.sqlite", "query", audience="all")


if __name__ == "__main__":
    unittest.main()
