import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.build_rag_catalog import (
    EVIDENCE_PATH, FACTS_PATH, MANIFEST_PATH, REGISTRY_PATH, REQUIRED_RELEASE_GATES,
    build_outputs, load_catalog, public_release_ready,
)


class RagCatalogTests(unittest.TestCase):
    def test_release_manifest_ids_match_active_corpora(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        narratives = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
        facts = json.loads(FACTS_PATH.read_text(encoding="utf-8"))["facts"]
        self.assertEqual(
            {row["id"] for row in manifest["narrative_cards"]},
            {row["id"] for row in narratives},
        )
        self.assertEqual(
            {row["id"] for row in manifest["statistical_facts"]},
            {row["id"] for row in facts},
        )
        self.assertTrue(all(row["release_allowed"] is False and row["rights_review"] == "PENDING"
                            for row in [*manifest["narrative_cards"], *manifest["statistical_facts"]]))

    def test_all_registered_sources_have_schema_and_table_mapping(self):
        mapping, groups = load_catalog()
        self.assertEqual(set(groups), {layer["id"] for layer in mapping["layers"]})
        rows = [row for values in groups.values() for row in values]
        with REGISTRY_PATH.open(encoding="utf-8-sig", newline="") as source:
            registered = list(csv.DictReader(source))
        self.assertEqual(len(rows), len(registered))
        self.assertTrue({"DMF-MONTHLY-2569-03", "DMF-MONTHLY-2569-09"}.issubset(
            {row["source_id"] for row in registered}))
        self.assertTrue(all(row["schema"] and row["tables"] for row in rows if row["layer_id"] != "SUPPORTING"))
        self.assertTrue(all(row["schema"] is None and row["tables"] == []
                            for row in rows if row["layer_id"] == "SUPPORTING"))

    def test_unknown_unit_period_scope_and_locator_stay_unknown(self):
        _, groups = load_catalog()
        rows = [row for values in groups.values() for row in values]
        self.assertTrue(all(row["measurement_period"] is None for row in rows))
        self.assertTrue(all(row["unit"] is None for row in rows))
        self.assertTrue(all(row["scope"] is None for row in rows))
        self.assertTrue(all(row["source_locator"] is None for row in rows))

    def test_layer_statuses_and_rights_are_not_promoted_to_cleared(self):
        mapping, _ = load_catalog()
        self.assertFalse(mapping["public_filter"]["current_public_release_allowed"])
        self.assertTrue(all(not layer["release_allowed"] for layer in mapping["layers"]))
        self.assertIn("rights_status", mapping["layers"][0])
        self.assertEqual(mapping["numeric_api_status"].split(":", 1)[0], "NOT_IMPLEMENTED")
        self.assertTrue(all(layer["rights_enforcement"]["queryable_as_cleared_in_current_schema"] is False
                            for layer in mapping["layers"]))

    def test_global_hold_blocks_catalog_even_if_rows_and_sources_look_cleared(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for row in [*manifest["narrative_cards"], *manifest["statistical_facts"]]:
            row["release_allowed"] = True
            row["rights_review"] = "CLEARED"
        manifest["external_llm_allowed"] = True
        self.assertFalse(public_release_ready(manifest))

        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            manifest_path = temporary / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            registry_path = temporary / "source-registry.csv"
            with REGISTRY_PATH.open(encoding="utf-8-sig", newline="") as source:
                rows = list(csv.DictReader(source))
                fieldnames = list(rows[0])
            for row in rows:
                row["rights_status"] = "CLEARED"
            with registry_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            with patch("scripts.build_rag_catalog.MANIFEST_PATH", manifest_path), \
                    patch("scripts.build_rag_catalog.REGISTRY_PATH", registry_path):
                _, public = build_outputs()

        self.assertEqual(public["sources"], [])
        self.assertEqual(public["evidence_records"], [])

    def test_conflicting_duplicate_manifest_decision_fails_closed(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest.update({
            "status": "APPROVED_FOR_PUBLIC_RELEASE",
            "publicly_usable": True,
            "public_release_allowed": True,
            "external_llm_allowed": True,
            "release_gates": {name: True for name in REQUIRED_RELEASE_GATES},
        })
        record_id = "tsm-pdd-annual-avoidance-estimate"
        approved = next(row for row in manifest["statistical_facts"] if row["id"] == record_id)
        manifest["statistical_facts"].remove(approved)
        manifest["statistical_facts"].extend([
            {**approved, "release_allowed": False, "rights_review": "PENDING"},
            {**approved, "release_allowed": True, "rights_review": "CLEARED"},
        ])

        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            manifest_path = temporary / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            registry_path = temporary / "source-registry.csv"
            with REGISTRY_PATH.open(encoding="utf-8-sig", newline="") as source:
                rows = list(csv.DictReader(source))
                fieldnames = list(rows[0])
            for row in rows:
                row["rights_status"] = "CLEARED"
            with registry_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            with patch("scripts.build_rag_catalog.MANIFEST_PATH", manifest_path), \
                    patch("scripts.build_rag_catalog.REGISTRY_PATH", registry_path):
                with self.assertRaisesRegex(ValueError, "duplicate id"):
                    build_outputs()

    def test_duplicate_source_registry_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            registry_path = Path(temporary) / "source-registry.csv"
            with REGISTRY_PATH.open(encoding="utf-8-sig", newline="") as source:
                rows = list(csv.DictReader(source))
                fieldnames = list(rows[0])
            rows.append(dict(rows[0]))
            with registry_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            with patch("scripts.build_rag_catalog.REGISTRY_PATH", registry_path):
                with self.assertRaisesRegex(ValueError, "duplicate source_id"):
                    load_catalog()

    def test_public_release_predicate_requires_every_mandatory_global_gate(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["status"] = "APPROVED_FOR_PUBLIC_RELEASE"
        manifest["publicly_usable"] = True
        manifest["public_release_allowed"] = True
        manifest["release_gates"] = {name: True for name in REQUIRED_RELEASE_GATES}
        self.assertTrue(public_release_ready(manifest))
        manifest["release_gates"].pop("server_to_server_auth_configured")
        self.assertFalse(public_release_ready(manifest), "a missing declared launch gate must block release")
        manifest["release_gates"]["server_to_server_auth_configured"] = True
        manifest["release_gates"]["unreviewed_future_gate"] = True
        self.assertFalse(public_release_ready(manifest), "an undeclared gate must trigger contract review")
        manifest["release_gates"].pop("unreviewed_future_gate")
        manifest["release_gates"]["provider_audience_eligibility_confirmed"] = False
        self.assertFalse(public_release_ready(manifest),
                         "region/age eligibility must block public output until owner confirmation")
        manifest["release_gates"]["provider_audience_eligibility_confirmed"] = True
        manifest["release_gates"]["rollback_owner_and_drill_recorded"] = False
        self.assertFalse(public_release_ready(manifest))

    def test_search_index_keeps_provenance_and_excludes_unapproved_records(self):
        private, public = build_outputs()
        self.assertEqual(len(private["evidence_index"]), 20)
        self.assertEqual(len(private["preview_index"]), 6)
        self.assertTrue(all("record_id" in row and "source_url" in row and "locator" in row
                            for row in private["evidence_index"]))
        self.assertTrue(all(not row["release_allowed"] and not row["external_llm_allowed"]
                            for row in private["evidence_index"]))
        self.assertEqual(public["sources"], [])
        self.assertEqual(public["evidence_records"], [])
        self.assertEqual(public["withheld_source_count"], private["source_count"])
        mdpi = next(row for row in private["preview_index"] if row["record_id"] == "fame-functional-unit")
        self.assertEqual(mdpi["source_ids"], ["MDPI-SU12229415-T4"])
        self.assertEqual(mdpi["publication_year"], 2020)
        self.assertIsNone(mdpi["measurement_period"], "publication year must not be misreported as measurement period")


if __name__ == "__main__":
    unittest.main()
