"""Export the reviewed product-inventory subset for the isolated Neo4j lab.

The CSV is a derived import artifact, not a source file. It retains source
locators and licensing/provenance metadata and does not normalize the LCI.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build/product-inventory/report.json"
OUTPUT = ROOT / "build/neo4j-csv/product_inventory.csv"
FIELDS = [
    "observation_id", "process", "flow", "direction", "role", "subprocess",
    "raw_value", "amount", "unit", "reference_amount", "reference_unit",
    "publication_year", "data_period", "data_period_status", "source_url",
    "doi", "table_id", "source_row", "source_column", "source_snapshot_sha256",
    "licence", "authors", "boundary", "geography", "technology_level",
    "allocation", "annotation", "status", "is_national_average",
    "is_full_lci_dataset", "is_newly_allocated",
]


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = payload["rows"]
    if len(rows) != 16:
        raise ValueError(f"Expected reviewed 16-row subset; found {len(rows)}")
    if len({row["observation_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate observation_id")
    if any(row.get("status") != "SOURCE_REPORTED_PRODUCT_INVENTORY" for row in rows):
        raise ValueError("Unexpected record status")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"source": str(SOURCE), "output": str(OUTPUT), "rows": len(rows),
                      "columns": len(FIELDS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
