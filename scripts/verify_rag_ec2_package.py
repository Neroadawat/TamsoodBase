"""Verify the allowlisted package context and ZIP against its SHA-256 manifest."""

import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_rag_ec2_package.py CONTEXT_DIR ARCHIVE.zip")
    context = Path(sys.argv[1]).resolve()
    archive = Path(sys.argv[2]).resolve()
    manifest = json.loads((context / "manifest.json").read_text(encoding="utf-8"))
    records = manifest["files"]
    names = {record["path"] for record in records}
    if len(names) != len(records):
        raise SystemExit("Duplicate file path in manifest")
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise SystemExit(f"Unsafe manifest path: {name}")
    expected_context = names | {"manifest.json"}
    actual_context = {path.relative_to(context).as_posix() for path in context.rglob("*") if path.is_file()}
    if actual_context != expected_context:
        raise SystemExit(f"Context contains unexpected/missing files: {actual_context ^ expected_context}")
    for record in records:
        path = context / record["path"]
        if path.stat().st_size != record["bytes"] or digest(path) != record["sha256"]:
            raise SystemExit(f"Payload integrity check failed: {record['path']}")
    if manifest["file_count"] != len(records) or manifest["total_bytes"] != sum(r["bytes"] for r in records):
        raise SystemExit("Manifest count/size mismatch")

    with zipfile.ZipFile(archive) as package:
        archive_names = set(package.namelist())
        if archive_names != expected_context:
            raise SystemExit(f"Archive contains unexpected/missing files: {archive_names ^ expected_context}")
        for record in records:
            if hashlib.sha256(package.read(record["path"])).hexdigest() != record["sha256"]:
                raise SystemExit(f"Archive integrity check failed: {record['path']}")
        if hashlib.sha256(package.read("manifest.json")).hexdigest() != digest(context / "manifest.json"):
            raise SystemExit("Archive manifest differs from build context")

    print(json.dumps({"release": manifest["release"], "files_verified": len(records),
                      "bytes_verified": manifest["total_bytes"], "archive_verified": True,
                      "archive_sha256": digest(archive)}, indent=2))


if __name__ == "__main__":
    main()
