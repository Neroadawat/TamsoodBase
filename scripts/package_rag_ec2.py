"""Create an allowlisted, private EC2 RAG image build context."""

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "build/rag/models"
STATIC_FILES = (
    "scripts/rag_retrieve.py",
    "scripts/rag_gemini.py",
    "scripts/rag_scope.py",
    "scripts/rag_review.py",
    "scripts/rag_http.py",
    "scripts/rag_demo.html",
    "requirements-rag.txt",
    "docs/rag/public-evidence.json",
    "docs/rag/retrieval-scope.json",
    "docs/rag/statistical-facts.json",
    "docs/rag/thai-answer-copy.json",
    "deploy/RAG_MODEL_NOTICE.txt",
)
NETWORK_EXPOSURE = (
    "internal-only Docker network with no published host ports; binds inside container; "
    "optional Bearer token for POST routes"
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    if not MODEL_DIR.is_dir():
        raise SystemExit("Cached local embedding model is required; package creation does not download it.")

    source_files = {ROOT / relative: relative for relative in STATIC_FILES}
    for path in MODEL_DIR.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"Symlink is not allowed in model cache: {path.relative_to(ROOT)}")
        if path.is_file():
            source_files[path] = path.relative_to(ROOT).as_posix()
    source_files[ROOT / "deploy/Dockerfile.rag"] = "Dockerfile"
    if any(not path.is_file() for path in source_files):
        missing = [relative for path, relative in source_files.items() if not path.is_file()]
        raise SystemExit(f"Required package files are missing: {missing}")

    file_records = [
        {"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path, relative in sorted(source_files.items(), key=lambda item: item[1])
    ]
    digest_input = json.dumps({"files": file_records, "network_exposure": NETWORK_EXPOSURE},
                              sort_keys=True, separators=(",", ":")).encode()
    release = hashlib.sha256(digest_input).hexdigest()[:16]
    output_root = ROOT / "build" / f"rag-ec2-{release}"
    package_root = output_root / "context"
    output_root.mkdir(parents=True, exist_ok=True)
    if package_root.exists():
        raise SystemExit(f"Package context already exists; inspect it before reuse: {package_root}")
    package_root.mkdir()

    for path, relative in source_files.items():
        destination = package_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    manifest = {
        "schema_version": 1,
        "release": release,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": file_records,
        "file_count": len(file_records),
        "total_bytes": sum(row["bytes"] for row in file_records),
        "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "vector_database": "Qdrant local in-memory",
        "runtime_external_llm": False,
        "network_exposure": NETWORK_EXPOSURE,
        "contents": "Allowlisted application files, curated JSON evidence, and cached ONNX model only; no raw source PDFs, CSV exports, credentials, or Qdrant disk store.",
    }
    (package_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    archive_path = output_root / f"tamsoodbase-rag-{release}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as archive:
        for path in sorted(package_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_root).as_posix())

    summary = {
        "release": release,
        "context": str(package_root),
        "archive": str(archive_path),
        "archive_bytes": archive_path.stat().st_size,
        "payload_files": len(file_records),
        "payload_bytes": manifest["total_bytes"],
        "archive_sha256": sha256(archive_path),
        "manifest": manifest,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
