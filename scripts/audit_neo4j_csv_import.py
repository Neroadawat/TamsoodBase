"""Verify CSV LOAD CSV + MERGE for the reviewed 16-row inventory, in isolation."""
import csv
import hashlib
import io
import json
import secrets
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from compare_data_models import project_inventory

ROOT = Path(__file__).resolve().parents[1]
OWNER = "TamsoodBase-M3-CSV-Import"
NETWORK = "tamsood-m3csv-" + secrets.token_hex(5)
CONTAINER = "tamsood-m3csv-" + secrets.token_hex(5)
CSV_PATH = ROOT / "build/neo4j-csv/product_inventory.csv"
IMPORT_SCRIPT = ROOT / "scripts/load_product_inventory_csv.cypher"


def run(args, *, input_bytes=None, check=True, timeout=120):
    result = subprocess.run(["docker", *args], input=input_bytes, capture_output=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace")[:1200])
    return result


def inspect_owned(name):
    result = run(["inspect", name], check=False)
    if result.returncode:
        return False
    item = json.loads(result.stdout)[0]
    labels = item.get("Config", {}).get("Labels") or {}
    if labels.get("org.tamsood.m3csv") != OWNER:
        raise RuntimeError("Refusing to act on a resource without the expected owner label")
    if item["HostConfig"].get("PortBindings"):
        raise RuntimeError("CSV import lab unexpectedly publishes host ports")
    if item["HostConfig"].get("NetworkMode") != NETWORK:
        raise RuntimeError("CSV import lab is not on its isolated network")
    return True


def cypher(statement, *, params=None, check=True):
    if not inspect_owned(CONTAINER):
        raise RuntimeError("Owned Neo4j lab is not available")
    args = ["exec", "-i", "-e", "JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=2 -Xmx128m",
            CONTAINER, "cypher-shell", "--non-interactive", "--format", "plain"]
    if params:
        args += ["--param", "{" + ",".join(k + ":" + json.dumps(v) for k, v in params.items()) + "}"]
    return run(args, input_bytes=statement.encode("utf-8"), check=check, timeout=90)


def query_rows(statement):
    output = cypher(statement).stdout.decode("utf-8")
    return list(csv.reader(io.StringIO(output), escapechar="\\", skipinitialspace=True))


def main():
    subprocess.run(["python", "-X", "utf8", str(ROOT / "scripts/export_product_inventory_csv.py")],
                   check=True, cwd=ROOT)
    source_path = ROOT / "build/product-inventory/report.json"
    source_bytes = source_path.read_bytes()
    source_rows = json.loads(source_bytes)["rows"]
    expected_graph = project_inventory(source_rows)
    if not run(["image", "inspect", "neo4j:5-community"], check=False).returncode == 0:
        raise RuntimeError("Required neo4j:5-community image is not available locally")
    run(["network", "create", "--internal", "--label", "org.tamsood.m3csv=" + OWNER, NETWORK])
    try:
        run(["run", "-d", "--name", CONTAINER, "--label", "org.tamsood.m3csv=" + OWNER,
             "--network", NETWORK, "--memory", "1536m", "--cpus", "1", "--pids-limit", "512",
             "-e", "NEO4J_AUTH=none", "-e", "NEO4J_server_jvm_additional=-XX:ActiveProcessorCount=2",
             "-e", "NEO4J_server_memory_heap_initial__size=256m",
             "-e", "NEO4J_server_memory_heap_max__size=512m",
             "-e", "NEO4J_server_memory_pagecache_size=128m",
             "--mount", "type=bind,source=" + str(CSV_PATH.parent) + ",target=/var/lib/neo4j/import",
             "neo4j:5-community"])
        deadline = time.monotonic() + 100
        while run(["exec", CONTAINER, "wget", "-q", "-O", "/dev/null", "http://127.0.0.1:7474"], check=False).returncode:
            state = json.loads(run(["inspect", CONTAINER]).stdout)[0]["State"]
            if not state["Running"]:
                raise RuntimeError("Neo4j stopped during CSV import startup")
            if time.monotonic() > deadline:
                raise TimeoutError("Neo4j readiness timeout")
            time.sleep(1)
        cypher(IMPORT_SCRIPT.read_text(encoding="utf-8"))
        rows = query_rows(
            "MATCH (p:Entity:Process)-[:HAS_EXCHANGE]->(e:Entity:Exchange)-[:OF_FLOW]->(f:Entity:Flow) "
            "RETURN e.observation_id,p.name,e.direction,e.amount,e.unit,f.name,"
            "e.source_snapshot_sha256,e.status,toString(e.source_row),toString(e.source_column) "
            "ORDER BY e.observation_id;"
        )
        if not rows or rows[0][0] != "e.observation_id":
            raise RuntimeError("Unexpected Neo4j CSV query output")
        returned = {r[0]: r[1:] for r in rows[1:] if r}
        expected = {r["observation_id"]: [r["process"], r["direction"], r["amount"], r["unit"],
                    r["flow"], r["source_snapshot_sha256"], r["status"], str(r["source_row"]),
                    str(r["source_column"])] for r in source_rows}
        if returned != expected:
            raise ValueError("Neo4j-loaded fields differ from the reviewed report rows")
        node_count = query_rows("MATCH (n:Entity) RETURN count(n);")
        relationship_count = query_rows("MATCH ()-[r]->() RETURN count(r);")
        graph_counts = [int(node_count[1][0]), int(relationship_count[1][0])]
        expected_counts = [len(expected_graph["nodes"]), len(expected_graph["edges"])]
        if graph_counts != expected_counts:
            raise ValueError(f"Graph counts {graph_counts} differ from projection {expected_counts}")
        cases = []
        for process in sorted({r["process"] for r in source_rows}):
            for direction in ("INPUT", "OUTPUT"):
                expected_rows = sorted(
                    (r["observation_id"], r["flow"], r["amount"], r["unit"])
                    for r in source_rows if r["process"] == process and r["direction"] == direction
                )
                raw = cypher(
                    "MATCH (p:Entity:Process)-[:HAS_EXCHANGE]->(e:Entity:Exchange) "
                    "-[:OF_FLOW]->(f:Entity:Flow) "
                    "WHERE p.name=$process AND e.direction=$direction "
                    "RETURN e.observation_id,f.name,e.amount,e.unit ORDER BY e.observation_id;",
                    params={"process": process, "direction": direction},
                ).stdout.decode("utf-8")
                parsed = list(csv.reader(io.StringIO(raw), escapechar="\\", skipinitialspace=True))
                actual_rows = [tuple(row) for row in parsed[1:] if row]
                cases.append({"process": process, "direction": direction,
                              "rows": len(actual_rows), "relationships_traversed": 2,
                              "equal_to_csv": actual_rows == expected_rows})
        if not all(c["equal_to_csv"] for c in cases):
            raise ValueError("Process/direction query did not match CSV")
        result = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "passed": True,
            "method": "Neo4j LOAD CSV WITH HEADERS + MERGE",
            "source_report_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "csv_sha256": hashlib.sha256(CSV_PATH.read_bytes()).hexdigest(),
            "csv_rows": len(source_rows),
            "csv_columns": len(next(csv.reader(CSV_PATH.open(encoding="utf-8-sig")))),
            "loaded_rows_match_source_fields": len(returned),
            "nodes": graph_counts[0], "relationships": graph_counts[1],
            "expected_projection_nodes": expected_counts[0],
            "expected_projection_relationships": expected_counts[1],
            "process_direction_checks": cases,
            "network": "owner-labelled internal network; no published ports",
            "scope": "Local disposable graph import of 16 source-reported Table 4 inventory rows; not full lifecycle LCI; no production change",
        }
        target = ROOT / "evidence/neo4j-csv-import-2026-11-09.json"
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        if inspect_owned(CONTAINER):
            run(["rm", "-f", "-v", CONTAINER])
        network = run(["network", "inspect", NETWORK], check=False)
        if network.returncode == 0:
            info = json.loads(network.stdout)[0]
            if (info.get("Labels") or {}).get("org.tamsood.m3csv") != OWNER:
                raise RuntimeError("Refusing to remove network without expected owner label")
            run(["network", "rm", NETWORK])


if __name__ == "__main__":
    main()
