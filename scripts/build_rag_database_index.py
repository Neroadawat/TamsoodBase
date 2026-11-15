"""Build a private, provenance-preserving FTS index from local DB snapshots.

This artifact is ignored under build/ and is never copied into the public frontend.
It is a local snapshot index, not a live-MySQL export or a rights-cleared corpus.
"""

import argparse
import csv
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
from urllib.parse import urldefrag


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/source-registry.csv"
OUTPUT = ROOT / "build/rag/catalog/private-database-record-index.sqlite"
REPORTS = {
    "NSO": ROOT / "build/nso/report.json",
    "EPPO": ROOT / "build/eppo/report.json",
    "RESEARCH": ROOT / "build/product-inventory/report.json",
}
DMF_LATEST = ROOT / "data/raw/dmf/latest.json"
DMF_ROOT = ROOT / "build/dmf"
REFERENCE_DB = ROOT / "build/reusable/reference.sqlite"
EPPO_DB = ROOT / "build/eppo/eppo.sqlite"
LAYERS = ("DMF", "COMPANY", "NSO", "EPPO", "RESEARCH", "SUPPORTING")
DMF_PACKAGE_SOURCE = {
    "production-oil": "DMF-CKAN-OIL",
    "production-condensate": "DMF-CKAN-CONDENSATE",
    "production-natural-gas": "DMF-CKAN-GAS",
}
DOI_RE = re.compile(r"10\.\d{4,9}/[^?#\s]+", re.I)
THAI_RUN_RE = re.compile(r"[ก-๙]{2,}")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def flatten(value):
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{flatten(k)} {flatten(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return " ".join(flatten(item) for item in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def search_text(values):
    base = " ".join(flatten(value) for value in values if value is not None)
    bigrams = []
    for run in THAI_RUN_RE.findall(base):
        bigrams.extend(run[index:index + 2] for index in range(len(run) - 1))
    return (base + " " + " ".join(bigrams)).strip()


def fts_query(value):
    value = str(value or "")
    groups = []
    for run in dict.fromkeys(THAI_RUN_RE.findall(value)):
        terms = list(dict.fromkeys(run[index:index + 2] for index in range(len(run) - 1)))
        if terms:
            groups.append(" AND ".join('"' + term.replace('"', '""') + '"' for term in terms))
    remainder = THAI_RUN_RE.sub(" ", value)
    # Python's standard re lacks Unicode property escapes; \w also matches underscores.
    terms = list(dict.fromkeys(re.findall(r"[^\W_]+", remainder, flags=re.UNICODE)))
    if terms:
        groups.append(" AND ".join('"' + term.replace('"', '""') + '"' for term in terms))
    return " OR ".join("(" + group + ")" for group in groups)


def load_registry(path=REGISTRY):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_url = {}
    by_doi = {}
    by_id = {}
    for row in rows:
        source_id = row["source_id"]
        by_id[source_id] = row
        url = canonical_url(row.get("url"))
        if url:
            by_url[url] = row
        match = DOI_RE.search(url)
        if match:
            by_doi[match.group(0).lower()] = row
    return rows, by_url, by_doi, by_id


def classify_source(source_id):
    upper = source_id.upper()
    if upper.startswith("DMF-"):
        return "DMF"
    if upper.startswith("NSO-"):
        return "NSO"
    if upper.startswith("EPPO-"):
        return "EPPO"
    if upper.startswith(("MDPI-", "PNU-")):
        return "RESEARCH"
    if "-REPORT-" in upper:
        return "COMPANY"
    return "SUPPORTING"


def source_for(row, layer, by_url, by_doi):
    if layer == "EPPO":
        dataset = str(row.get("dataset_id", ""))
        source_id = {"11_13": "EPPO-11_13", "11_14": "EPPO-11_14"}.get(dataset)
        if source_id:
            return next((item for item in by_url.values() if item["source_id"] == source_id), None)
    url = canonical_url(row.get("source_url") or row.get("url"))
    if url in by_url:
        return by_url[url]
    match = DOI_RE.search(url)
    if match and match.group(0).lower() in by_doi:
        return by_doi[match.group(0).lower()]
    return None


def canonical_url(value):
    return urldefrag(str(value or "").strip())[0].rstrip("/")


def locator_for(row, fallback_hash=None, fallback_line=None):
    source_hash = (row.get("source_sha256") or row.get("csv_sha256")
                   or row.get("source_snapshot_sha256") or fallback_hash)
    locator = {
        "source_sha256": source_hash,
        "source_line": row.get("source_line", fallback_line),
        "source_row": row.get("source_row"),
        "source_column": row.get("source_column"),
        "pdf_page": row.get("pdf_page"),
        "printed_page": row.get("printed_page"),
        "table_id": row.get("table_id"),
    }
    return {key: value for key, value in locator.items() if value is not None}


def normalize_record(row, layer, source, record_id, source_hash=None, source_line=None):
    row = dict(row)
    source = source or {}
    source_id = source.get("source_id")
    if not source_id:
        raise ValueError(f"Unmapped {layer} source for record {record_id}")
    source_url = row.get("source_url") or row.get("url") or source.get("url") or None
    publication_year = row.get("publication_year") or row.get("report_year")
    reference_year = row.get("reference_year") or row.get("year_ce")
    unit = row.get("unit") or row.get("unit_code") or row.get("metadata_unit")
    scope = {
        key: row.get(key) for key in
        ("scope", "geography", "area", "block_label", "boundary", "process", "subject_type")
        if row.get(key) is not None
    }
    period = row.get("data_period")
    if period is None and (reference_year is not None or row.get("month") is not None):
        period = {"reference_year": reference_year, "month": row.get("month")}
    record_status = row.get("review_status") or row.get("status") or row.get("decision")
    record_rights = row.get("redistribution_status") or row.get("rights_status")
    license_label = row.get("license_label") or row.get("licence")
    locator = locator_for(row, source_hash, source_line)
    title_fields = (
        "label", "measure", "subject", "source_group", "block_label", "process",
        "flow", "activity", "source_metric_id", "publisher", "originating_agency",
        "notes", "annotation", "raw_value", "amount", "unit", "unit_code",
        "reference_year", "publication_year", "year_ce", "month", "data_period",
        "scope", "geography", "boundary", "status", "review_status", "decision",
    )
    index_text = search_text([source_id, source.get("publisher"), source.get("title"), source.get("notes"),
                              *(row.get(key) for key in title_fields), locator])
    payload = dict(row)
    if layer == "DMF" and "raw_json" in payload:
        # The raw row already lives in the immutable source SQLite snapshot.
        # Avoid copying it into every FTS record; the hash/line below locates it.
        payload.pop("raw_json")
        payload["source_payload_pointer"] = {
            "source_sha256": locator.get("source_sha256"),
            "source_line": locator.get("source_line"),
        }
    return {
        "record_id": str(record_id),
        "source_id": source_id,
        "layer": layer,
        "data_status": record_status,
        "source_rights_status": source.get("rights_status"),
        "record_rights_status": record_rights,
        "license_label": license_label,
        "publication_year": publication_year,
        "reference_year": reference_year,
        "period_json": json.dumps(period, ensure_ascii=False, sort_keys=True) if period is not None else None,
        "unit": str(unit) if unit is not None else None,
        "scope_json": json.dumps(scope, ensure_ascii=False, sort_keys=True) if scope else None,
        "source_url": source_url,
        "locator_json": json.dumps(locator, ensure_ascii=False, sort_keys=True) if locator else None,
        "payload_json": json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str),
        "search_text": index_text,
        # This index deliberately has no release-approved record mapping today.
        "release_allowed": 0,
        "external_llm_allowed": 0,
    }


def readonly_sqlite(path):
    resolved = path.resolve(strict=True)
    return sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True)


def collect_dmf(by_url, by_doi, by_id):
    latest = json.loads(DMF_LATEST.read_text(encoding="utf-8"))
    run_id = latest["run_id"]
    db = DMF_ROOT / run_id / "candidates.sqlite"
    con = readonly_sqlite(db)
    try:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM deduplicated_candidates ORDER BY package,source_line")
        for item in rows:
            row = dict(item)
            source = by_id.get(DMF_PACKAGE_SOURCE.get(row.get("package")))
            record_id = f"DMF:{row['package']}:{row['source_line']}"
            yield normalize_record(row, "DMF", source, record_id,
                                   row.get("csv_sha256"), row.get("source_line"))
    finally:
        con.close()


def collect_reference(by_url, by_doi):
    con = readonly_sqlite(REFERENCE_DB)
    try:
        con.row_factory = sqlite3.Row
        for item in con.execute("SELECT * FROM reference_catalog ORDER BY publisher,source_metric_id,reference_year"):
            row = dict(item)
            source = source_for(row, "COMPANY", by_url, by_doi)
            yield normalize_record(row, "COMPANY", source, row.get("observation_id"))
    finally:
        con.close()


def collect_report(layer, path, by_url, by_doi):
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data.get("rows", []):
        source = source_for(row, layer, by_url, by_doi)
        record_id = row.get("observation_id") or row.get("record_id")
        if not record_id:
            raise ValueError(f"{layer} report row has no stable observation/record ID")
        yield normalize_record(row, layer, source, record_id)


def collect_all():
    source_rows, by_url, by_doi, by_id = load_registry()
    rows = []
    for source in source_rows:
        layer = classify_source(source.get("source_id", ""))
        # Source catalog entries also make report titles/notes searchable.
        rows.append(normalize_record({
            "source_url": source.get("url"),
            "publisher": source.get("publisher"),
            "label": source.get("title"),
            "notes": source.get("notes"),
            "status": source.get("status"),
        }, layer, source, "SRC:" + source["source_id"]))
    rows.extend(collect_dmf(by_url, by_doi, by_id))
    rows.extend(collect_reference(by_url, by_doi))
    for layer, path in REPORTS.items():
        rows.extend(collect_report(layer, path, by_url, by_doi))
    return rows


def snapshot_metadata():
    paths = [REGISTRY, DMF_LATEST, DMF_ROOT / json.loads(DMF_LATEST.read_text(encoding="utf-8"))["run_id"] / "candidates.sqlite",
             REFERENCE_DB, EPPO_DB, *REPORTS.values()]
    inputs = []
    for path in paths:
        resolved = path.resolve(strict=True)
        inputs.append({
            "path": resolved.relative_to(ROOT.resolve()).as_posix(),
            "sha256": sha256(resolved),
            "modified_at": datetime.fromtimestamp(resolved.stat().st_mtime, timezone.utc).isoformat(),
        })
    return inputs


def snapshot_freshness(inputs):
    times = [datetime.fromisoformat(item["modified_at"]) for item in inputs]
    return {
        "basis": "LOCAL_FILE_MTIME_ONLY",
        "live_database_read": False,
        "freshness_attested": False,
        "oldest_input_modified_at": min(times).isoformat() if times else None,
        "newest_input_modified_at": max(times).isoformat() if times else None,
        "warning": "File modification times do not prove source freshness or current database state.",
    }


def _time_range(values):
    times = sorted(str(value) for value in values if value)
    return {"count": len(times), "oldest": times[0] if times else None,
            "newest": times[-1] if times else None}


def source_activity_metadata():
    dmf_run = json.loads(DMF_LATEST.read_text(encoding="utf-8"))["run_id"]
    dmf_db = DMF_ROOT / dmf_run / "candidates.sqlite"
    with closing(readonly_sqlite(dmf_db)) as con:
        dmf_times = [row[0] for row in con.execute("SELECT acquired_at FROM resource")]
    with closing(readonly_sqlite(REFERENCE_DB)) as con:
        company_times = [row[0] for row in con.execute("SELECT accessed_at FROM document")]
        company_release_times = [row[0] for row in con.execute("SELECT created_at FROM data_release")]
    nso = json.loads((ROOT / "build/nso/report.json").read_text(encoding="utf-8"))
    nso_times = [resource.get("acquired_at") for resource in
                 nso.get("source_manifest", {}).get("resources", {}).values()]
    with closing(readonly_sqlite(EPPO_DB)) as con:
        eppo_times = []
        for (payload,) in con.execute("SELECT payload FROM source_snapshot"):
            metadata = json.loads(payload)
            eppo_times.append(metadata.get("acquired_at"))
    research = json.loads((ROOT / "build/product-inventory/report.json").read_text(encoding="utf-8"))
    return {
        "DMF": {"timestamp_type": "source_acquired_at", "basis": "resource.acquired_at", **_time_range(dmf_times)},
        "COMPANY": {"timestamp_type": "source_accessed_at", "basis": "document.accessed_at", **_time_range(company_times),
                    "release_build": _time_range(company_release_times)},
        "NSO": {"timestamp_type": "source_acquired_at", "basis": "source_manifest.resources[].acquired_at", **_time_range(nso_times)},
        "EPPO": {"timestamp_type": "source_acquired_at", "basis": "source_snapshot.payload.acquired_at", **_time_range(eppo_times)},
        "RESEARCH": {"timestamp_type": "local_validation_checked_at", "basis": "report.checked_at; not source-acquisition time",
                     **_time_range([research.get("checked_at")])},
        "SUPPORTING": {"timestamp_type": "unknown", "basis": "source registry has no standardized acquisition/access timestamp",
                       "count": 0, "oldest": None, "newest": None},
    }


def create_index(path, records, inputs, source_activity=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix="private-rag-index-", suffix=".sqlite", dir=path.parent)
    os.close(descriptor)
    temp = Path(temp_name)
    con = None
    try:
        con = sqlite3.connect(temp)
        con.execute("PRAGMA journal_mode=DELETE")
        con.executescript("""
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value_json TEXT NOT NULL);
            CREATE TABLE records (
                record_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                layer TEXT NOT NULL,
                data_status TEXT,
                source_rights_status TEXT,
                record_rights_status TEXT,
                license_label TEXT,
                publication_year INTEGER,
                reference_year INTEGER,
                period_json TEXT,
                unit TEXT,
                scope_json TEXT,
                source_url TEXT,
                locator_json TEXT,
                payload_json TEXT NOT NULL,
                release_allowed INTEGER NOT NULL CHECK(release_allowed=0),
                external_llm_allowed INTEGER NOT NULL CHECK(external_llm_allowed=0)
            );
            CREATE VIRTUAL TABLE record_fts USING fts5(
                record_id UNINDEXED, source_id UNINDEXED, layer UNINDEXED, search_text,
                tokenize='unicode61'
            );
            CREATE INDEX ix_records_source ON records(source_id,layer);
            CREATE INDEX ix_records_year_unit ON records(reference_year,unit);
            CREATE INDEX ix_records_status_rights ON records(data_status,source_rights_status);
        """)
        con.executemany("INSERT INTO metadata VALUES (?,?)", [
            ("schema_version", json.dumps(1)),
            ("visibility", json.dumps("PRIVATE_INTERNAL_SNAPSHOT_ONLY")),
            ("generated_at", json.dumps(datetime.now(timezone.utc).isoformat())),
            ("source_count", json.dumps(len(load_registry()[0]))),
            ("record_count", json.dumps(len(records))),
            ("snapshot_inputs", json.dumps(inputs, ensure_ascii=False, sort_keys=True)),
            ("snapshot_freshness", json.dumps(snapshot_freshness(inputs), ensure_ascii=False, sort_keys=True)),
            ("source_activity", json.dumps(source_activity if source_activity is not None else {}, ensure_ascii=False, sort_keys=True)),
            ("public_release_allowed", json.dumps(False)),
            ("external_llm_allowed", json.dumps(False)),
        ])
        values = []
        fts = []
        for row in records:
            values.append(tuple(row[key] for key in (
                "record_id", "source_id", "layer", "data_status", "source_rights_status",
                "record_rights_status", "license_label", "publication_year", "reference_year",
                "period_json", "unit", "scope_json", "source_url", "locator_json", "payload_json",
                "release_allowed", "external_llm_allowed")))
            fts.append((row["record_id"], row["source_id"], row["layer"], row["search_text"]))
        con.executemany("INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
        con.executemany("INSERT INTO record_fts VALUES (?,?,?,?)", fts)
        con.commit()
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fts_count = con.execute("SELECT COUNT(*) FROM record_fts").fetchone()[0]
        record_count = con.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        public_count = con.execute("SELECT COUNT(*) FROM records WHERE release_allowed=1 OR external_llm_allowed=1").fetchone()[0]
        con.close()
        con = None
        if integrity != "ok" or fts_count != record_count or public_count != 0:
            raise ValueError("Private RAG index integrity or rights gate failed")
        os.replace(temp, path)
        return {"record_count": record_count, "fts_count": fts_count, "public_count": public_count}
    except Exception:
        if con is not None:
            con.close()
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def search_records(path, query, limit=20, *, audience="public"):
    query = str(query or "").strip()
    if not query:
        return []
    if (len(query) > 500 or not isinstance(limit, int) or not 1 <= limit <= 50
            or audience not in {"public", "external_llm", "internal"}):
        raise ValueError("Invalid local index search parameters")
    rights_predicate = {
        "public": "r.release_allowed=1",
        "external_llm": "r.release_allowed=1 AND r.external_llm_allowed=1",
        "internal": "1=1",
    }[audience]
    fts = fts_query(query)
    if not fts:
        return []
    con = readonly_sqlite(Path(path))
    try:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT r.record_id,r.source_id,r.layer,r.data_status,r.source_rights_status,"
            "r.record_rights_status,r.publication_year,r.reference_year,r.period_json,r.unit,"
            "r.scope_json,r.source_url,r.locator_json,r.release_allowed,r.external_llm_allowed,"
            "r.payload_json,bm25(record_fts) AS rank "
            "FROM record_fts JOIN records r ON r.record_id=record_fts.record_id "
            f"WHERE record_fts MATCH ? AND {rights_predicate} ORDER BY rank LIMIT ?",
            (fts, limit),
        )
        return [dict(row) for row in rows]
    finally:
        con.close()


def validate_inputs():
    missing = [str(path.relative_to(ROOT)) for path in [REGISTRY, DMF_LATEST, REFERENCE_DB, EPPO_DB, *REPORTS.values()] if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing current local snapshots: " + ", ".join(missing))
    run_id = json.loads(DMF_LATEST.read_text(encoding="utf-8"))["run_id"]
    dmf_db = DMF_ROOT / run_id / "candidates.sqlite"
    if not dmf_db.is_file():
        raise FileNotFoundError(f"Missing DMF candidate snapshot: {dmf_db.relative_to(ROOT)}")
    return dmf_db


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate local snapshots and record mapping without writing an index")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    validate_inputs()
    records = collect_all()
    inputs = snapshot_metadata()
    freshness = snapshot_freshness(inputs)
    source_activity = source_activity_metadata()
    counts = {layer: sum(row["layer"] == layer for row in records) for layer in LAYERS}
    unmapped = [row["record_id"] for row in records if not row["source_id"]]
    if unmapped:
        raise ValueError(f"Unmapped record source IDs: {unmapped[:10]}")
    if args.check:
        print(json.dumps({"status": "valid", "visibility": "PRIVATE_INTERNAL_SNAPSHOT_ONLY",
                          "source_count": len(load_registry()[0]), "record_count": len(records),
                          "records_by_layer": counts, "public_release_allowed": False,
                          "external_llm_allowed": False,
                          "snapshot_freshness": freshness, "source_activity": source_activity}, ensure_ascii=False))
        return
    result = create_index(args.output, records, inputs, source_activity)
    print(json.dumps({"status": "built", **result, "records_by_layer": counts,
                      "output": str(args.output), "visibility": "PRIVATE_INTERNAL_SNAPSHOT_ONLY",
                      "snapshot_freshness": freshness, "source_activity": source_activity}, ensure_ascii=False))


if __name__ == "__main__":
    main()
