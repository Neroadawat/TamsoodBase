"""Build private and rights-filtered source catalog indexes for RAG."""

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "docs/rag/dataset-catalog-map.json"
REGISTRY_PATH = ROOT / "docs/source-registry.csv"
MANIFEST_PATH = ROOT / "docs/rag/public-release-manifest.json"
REQUIRED_RELEASE_GATES_PATH = ROOT / "docs/rag/required-release-gates.json"
EVIDENCE_PATH = ROOT / "docs/rag/public-evidence.json"
FACTS_PATH = ROOT / "docs/rag/statistical-facts.json"
PREVIEW_PATH = ROOT / "docs/rag/vercel-preview-corpus.json"
REQUIRED_RELEASE_GATES = tuple(json.loads(REQUIRED_RELEASE_GATES_PATH.read_text(encoding="utf-8")))


def require_unique_ids(rows, field, label):
    if not isinstance(rows, list):
        raise ValueError(f"{label} must be a list")
    seen = set()
    duplicates = set()
    for row in rows:
        value = row.get(field) if isinstance(row, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} contains a missing {field}")
        value = value.strip()
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise ValueError(f"{label} contains duplicate {field}: {sorted(duplicates)}")


def public_release_ready(manifest):
    gates = manifest.get("release_gates")
    return (
        manifest.get("status") == "APPROVED_FOR_PUBLIC_RELEASE"
        and manifest.get("publicly_usable") is True
        and manifest.get("public_release_allowed") is True
        and isinstance(gates, dict)
        and set(gates) == set(REQUIRED_RELEASE_GATES)
        and all(gates.get(name) is True for name in REQUIRED_RELEASE_GATES)
    )


def load_catalog():
    mapping = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    with REGISTRY_PATH.open(encoding="utf-8-sig", newline="") as stream:
        sources = list(csv.DictReader(stream))
    require_unique_ids(sources, "source_id", "Source registry")
    layers = mapping["layers"]
    groups = {layer["id"]: [] for layer in layers}
    unknown = []
    for row in sources:
        source_id = row["source_id"].upper()
        if source_id.startswith("DMF-"):
            key = "DMF"
        elif source_id.startswith("NSO-"):
            key = "NSO"
        elif source_id.startswith("EPPO-"):
            key = "EPPO"
        elif source_id.startswith("MDPI-") or source_id.startswith("PNU-"):
            key = "RESEARCH"
        elif "-REPORT-" in source_id:
            key = "COMPANY"
        elif source_id.startswith(("GHG-PROTOCOL-", "IPCC-", "UNFCCC-", "DEDE-")):
            key = "SUPPORTING"
        else:
            unknown.append(source_id)
            continue
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", row.get("title", ""))
        groups[key].append({
            "source_id": row["source_id"],
            "publisher": row["publisher"],
            "title": row["title"],
            "url": row["url"],
            "type": row["type"],
            "status": row["status"],
            "rights_status": row["rights_status"],
            "notes": row["notes"],
            "layer_id": key,
            "schema": next(layer["schema"] for layer in layers if layer["id"] == key),
            "tables": next(layer["tables"] for layer in layers if layer["id"] == key),
            "publication_year_hint": int(year_match.group(1)) if year_match else None,
            "measurement_period": None,
            "unit": None,
            "scope": None,
            "source_locator": None,
            "index_text": " ".join(filter(None, [row["source_id"], row["publisher"], row["title"], row["notes"]])),
            "release_allowed": False,
            "external_llm_allowed": False,
        })
    if unknown:
        raise ValueError(f"Source registry rows need an explicit layer mapping: {unknown}")
    return mapping, groups


def build_outputs():
    mapping, groups = load_catalog()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    global_release_ready = public_release_ready(manifest)
    approvals = {row["id"]: row for row in
                 [*manifest.get("narrative_cards", []), *manifest.get("statistical_facts", [])]}
    private_rows = [row for layer in mapping["layers"] for row in groups[layer["id"]]]
    source_by_id = {row["source_id"]: row for row in private_rows}
    evidence_rows = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    facts_doc = json.loads(FACTS_PATH.read_text(encoding="utf-8"))
    fact_rows = facts_doc["facts"]
    approval_rows = [*manifest.get("narrative_cards", []), *manifest.get("statistical_facts", [])]
    require_unique_ids(approval_rows, "id", "Release manifest")
    require_unique_ids(evidence_rows, "id", "Narrative corpus")
    require_unique_ids(fact_rows, "id", "Statistical-fact corpus")
    if ({row["id"] for row in evidence_rows} != {row["id"] for row in manifest.get("narrative_cards", [])}
            or {row["id"] for row in fact_rows} != {row["id"] for row in manifest.get("statistical_facts", [])}):
        raise ValueError("Release manifest record IDs must exactly match the narrative and statistical corpora")
    source_by_url = {row["url"].rstrip("/"): row["source_id"] for row in private_rows}

    def source_ids_for(url, locator=""):
        normalized = (url or "").rstrip("/")
        # DOI URLs commonly differ by resolver host but retain the same DOI.
        doi_match = re.search(r"10\.\d{4,9}/[^?#\s]+", normalized, re.IGNORECASE)
        if doi_match:
            target = doi_match.group(0).lower()
            if target == "10.3390/su12229415":
                locator_text = str(locator).lower()
                matched = []
                if "table 4" in locator_text:
                    matched.append("MDPI-SU12229415-T4")
                if any(f"table {number}" in locator_text for number in ("1", "2", "3")):
                    matched.append("MDPI-SU12229415-T1-3")
                if matched:
                    return matched
            matches = [row["source_id"] for row in private_rows if target in row["url"].lower()]
            if matches:
                return matches
        exact = source_by_url.get(normalized)
        return [exact] if exact else []

    def approved_record(record_id, source_ids):
        if not global_release_ready:
            return False
        decision = approvals.get(record_id, {})
        if decision.get("release_allowed") is not True or decision.get("rights_review") != "CLEARED":
            return False
        if not source_ids or any(source_id not in source_by_id
                                 or source_by_id[source_id]["rights_status"].strip().upper() != "CLEARED"
                                 for source_id in source_ids):
            return False
        return True

    narrative = [{
        "record_id": row["id"], "record_type": "narrative", "title": row["title"],
        "text": row["text"], "index_text": " ".join(filter(None, [row["title"], row["text"]])),
        "publication_year": None, "measurement_period": None, "unit": None,
        "scope": None, "source_ids": source_ids_for(row.get("source_url"), row.get("locator")),
        "source_url": row.get("source_url"), "locator": row.get("locator"),
        "data_status": "CURATED_SOURCE_SUMMARY",
        "rights_status": "CLEARED" if approved_record(row["id"], source_ids_for(row.get("source_url"), row.get("locator"))) else "PENDING_OR_UNMAPPED",
        "release_allowed": approved_record(row["id"], source_ids_for(row.get("source_url"), row.get("locator"))),
        "external_llm_allowed": bool(manifest.get("external_llm_allowed")) and approved_record(row["id"], source_ids_for(row.get("source_url"), row.get("locator"))),
    } for row in evidence_rows]
    facts = [{
        "record_id": row["id"], "parent_record_id": row.get("parent_id"),
        "record_type": "statistical_fact", "title": row["title"],
        "text": " ".join(filter(None, [row.get("subject"), row.get("metric"), row.get("qualifier")])),
        "index_text": " ".join(filter(None, [row.get("title"), row.get("subject"), row.get("metric"),
                                               " ".join(row.get("aliases", [])), row.get("qualifier")])),
        "value": row.get("value"), "unit": row.get("unit"),
        "publication_year": None, "measurement_period": row.get("period"),
        "scope": {"geography": row.get("geography"), "basis": row.get("basis")},
        "data_status": row.get("status"), "source_ids": source_ids_for(row.get("source_url"), row.get("locator")),
        "source_url": row.get("source_url"), "locator": row.get("locator"),
        "rights_status": "CLEARED" if approved_record(row["id"], source_ids_for(row.get("source_url"), row.get("locator"))) else "PENDING_OR_UNMAPPED",
        "release_allowed": approved_record(row["id"], source_ids_for(row.get("source_url"), row.get("locator"))),
        "external_llm_allowed": bool(manifest.get("external_llm_allowed")) and approved_record(row["id"], source_ids_for(row.get("source_url"), row.get("locator"))),
    } for row in fact_rows]
    restricted_evidence = [*narrative, *facts]
    approved_source_ids = {source_id for row in restricted_evidence if row["release_allowed"]
                           for source_id in row["source_ids"]}
    public_rows = [row for row in private_rows if row["source_id"] in approved_source_ids
                   and row["rights_status"].strip().upper() == "CLEARED"]
    preview = json.loads(PREVIEW_PATH.read_text(encoding="utf-8"))
    preview_records = [{
        "record_id": row["id"], "record_type": "preview_narrative", "title": row["title"],
        "text": row["text"], "index_text": " ".join([row["title"], row["text"]]),
        "publication_year": 2020, "measurement_period": None, "unit": None,
        "scope": None, "source_ids": source_ids_for(row.get("source_url"), row.get("locator")),
        "source_url": row["source_url"], "locator": row["locator"],
        "rights_status": row["licence"], "license_url": row["licence_url"],
        "data_status": "LIMITED_PREVIEW_ONLY", "release_allowed": True,
        "external_llm_allowed": True,
    } for row in preview["records"]]
    layers = [{**layer, "source_count": len(groups[layer["id"]]), "sources": groups[layer["id"]]}
              for layer in mapping["layers"]]
    private = {
        "schema_version": 1,
        "status_as_of": mapping["status_as_of"],
        "visibility": "PRIVATE_INTERNAL_CATALOG",
        "source_registry": "docs/source-registry.csv",
        "source_count": len(private_rows),
        "layers": layers,
        "evidence_index": restricted_evidence,
        "preview_index": preview_records,
        "unknown_layer_source_ids": [],
    }
    public = {
        "schema_version": 1,
        "status_as_of": mapping["status_as_of"],
        "visibility": "PUBLIC_RELEASE_CLEARED_ONLY",
        "source_count": len(public_rows),
        "sources": public_rows,
        "evidence_records": [row for row in restricted_evidence if row["release_allowed"]],
        "withheld_source_count": len(private_rows) - len(public_rows),
    }
    out = ROOT / "build/rag/catalog"
    return private, public


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate catalog without writing build artifacts")
    args = parser.parse_args()
    private, public = build_outputs()
    if args.check:
        if public["sources"] or public["evidence_records"]:
            print(f"Catalog valid; {private['source_count']} private source entries; {len(private['evidence_index'])} restricted evidence records; {len(public['sources']) + len(public['evidence_records'])} cleared public records.")
        else:
            print(f"Catalog valid; {private['source_count']} private source entries; {len(private['evidence_index'])} restricted evidence records; 0 cleared public records (rights gate closed).")
        return
    out = ROOT / "build/rag/catalog"
    out.mkdir(parents=True, exist_ok=True)
    (out / "private-source-catalog.json").write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "public-source-index.json").write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {private['source_count']} private source entries and {public['source_count']} release-cleared public entries.")


if __name__ == "__main__":
    main()
