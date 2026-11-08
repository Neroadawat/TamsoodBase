"""Replay the pinned ethanol inputs in isolation and register internal evidence versions."""
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = "evidence/ethanol-proxy-scenario.json"
MANIFEST = "evidence/ethanol-reviewed-inputs.json"
RAW = (
    "data/raw/dede-bioethanol1/source.pdf",
    "data/raw/tgo-cfp-2026-11-03/page.html",
)
CASES = {
    "dede": REPORT,
    "cmu": "evidence/ethanol-assumption-validation.json",
    "tsm": "evidence/ethanol-tsm-wastewater.json",
    "uasb": "evidence/ethanol-uasb-lab-benchmark.json",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replay():
    expected = (ROOT / REPORT).read_bytes()
    report = json.loads(expected)
    pins = json.loads((ROOT / MANIFEST).read_bytes())
    paths = [MANIFEST, *pins["sha256"], *report["code_sha256"], *RAW]
    with tempfile.TemporaryDirectory(prefix="tamsood-ethanol-replay-") as directory:
        isolated = Path(directory)
        for name in paths:
            target = isolated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        subprocess.run(
            [sys.executable, "-m", "scripts.build_ethanol_proxy_scenario"],
            cwd=isolated, check=True, capture_output=True, timeout=30,
        )
        actual = (isolated / REPORT).read_bytes()
    if actual != expected:
        raise ValueError("Isolated replay differs from the recorded scenario")
    return {"report_sha256": sha(actual), "files_copied": len(paths), "byte_identical": True}


def register(database):
    schema = (ROOT / "sql/review-workflow.sql").read_text(encoding="utf-8")
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        if not connection.execute(
            "SELECT 1 FROM sqlite_master WHERE name='review_release'"
        ).fetchone():
            connection.executescript(schema)
            connection.executescript("""
                CREATE TABLE ethanol_evidence_version(
                    release_id TEXT PRIMARY KEY REFERENCES review_release(id),
                    case_key TEXT NOT NULL CHECK(case_key IN ('dede','cmu','tsm','uasb')),
                    evidence_path TEXT NOT NULL,
                    content BLOB NOT NULL,
                    rights_status TEXT NOT NULL CHECK(rights_status='NOT_CLEARED')
                );
                CREATE TRIGGER ethanol_version_update BEFORE UPDATE ON ethanol_evidence_version
                BEGIN SELECT RAISE(ABORT,'Retain immutable evidence version'); END;
                CREATE TRIGGER ethanol_version_delete BEFORE DELETE ON ethanol_evidence_version
                BEGIN SELECT RAISE(ABORT,'Retain immutable evidence version'); END;
            """)
        records = []
        for case_key, name in CASES.items():
            content = (ROOT / name).read_bytes()
            digest = sha(content)
            release_id = f"ethanol-{case_key}-{digest}"
            connection.execute(
                "INSERT INTO review_release(id,content_sha256,scope) VALUES(?,?,'INTERNAL_ACTIVITY_REVIEW') ON CONFLICT(id) DO NOTHING",
                (release_id, digest),
            )
            connection.execute(
                "INSERT INTO ethanol_evidence_version VALUES(?,?,?,?,'NOT_CLEARED') ON CONFLICT(release_id) DO NOTHING",
                (release_id, case_key, name, content),
            )
            stored, state = connection.execute(
                "SELECT v.content,r.state FROM ethanol_evidence_version v JOIN review_release r ON r.id=v.release_id WHERE v.release_id=?",
                (release_id,),
            ).fetchone()
            if sha(stored) != digest:
                raise ValueError("Registry content does not match release identity")
            records.append({"case": case_key, "release_id": release_id, "state": state})
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Registry foreign key violation")
        return records


def main():
    report = replay()
    destination = ROOT / "build/ethanol-proxy-scenario/review-registry.sqlite"
    destination.parent.mkdir(parents=True, exist_ok=True)
    report["internal_registry"] = register(destination)
    report["scope"] = "ISOLATED_REPLAY_WITH_PINNED_LOCAL_INPUTS"
    report["human_approval_recorded"] = False
    (ROOT / "evidence/ethanol-release-verification.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report))


if __name__ == "__main__":
    main()
