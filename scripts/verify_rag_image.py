"""Test a built RAG image in an isolated, resource-limited container."""

import json
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def run(*args, check=True, capture=True):
    result = subprocess.run(args, check=False, text=True, encoding="utf-8",
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None)
    if check and result.returncode:
        detail = (result.stderr or result.stdout or "").strip()[-6000:]
        raise RuntimeError(f"Command failed ({result.returncode}): {args[0]} {args[1:3]}\n{detail}")
    return result


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: verify_rag_image.py IMAGE [MEMORY_SWAP_MIB]")
    image = sys.argv[1]
    memory_swap_mib = int(sys.argv[2]) if len(sys.argv) == 3 else 1024
    if memory_swap_mib < 512:
        raise SystemExit("MEMORY_SWAP_MIB must be at least 512")
    name = "rag-verify-" + uuid.uuid4().hex[:10]
    run("docker", "run", "-d", "--name", name, "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m", "--user", "10001:10001",
        "--env", "RAG_ALLOWED_ORIGIN=http://127.0.0.1:8767",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
        "--memory", "512m", "--memory-swap", f"{memory_swap_mib}m",
        "--cpus", "0.50", "--pids-limit", "64", image)
    try:
        ready = False
        for _ in range(120):
            state = run("docker", "inspect", "-f", "{{.State.Running}}|{{.State.OOMKilled}}", name).stdout.strip()
            if state == "false|true":
                raise RuntimeError("Image container was OOM-killed under a 512 MiB memory limit")
            if state.startswith("true|"):
                code = "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8767/readyz',timeout=2).read()"
                if run("docker", "exec", name, "python", "-c", code, check=False).returncode == 0:
                    ready = True
                    break
            time.sleep(2)
        if not ready:
            logs = run("docker", "logs", "--tail", "100", name, check=False).stdout
            raise RuntimeError("Image failed readiness within 240 seconds\n" + logs)

        probe = r'''
import json, urllib.error, urllib.request
def get(path):
        with urllib.request.urlopen('http://127.0.0.1:8767'+path, timeout=10) as r:
            return r.status, r.read()
status, body = get('/readyz')
ready = json.loads(body)
assert status == 200 and ready['evidence_records'] == 10, ready
status, body = get('/healthz')
assert status == 200 and json.loads(body)['status'] == 'ok'
status, page = get('/')
assert status == 200 and b'TamsoodBase' in page
assert 'CO₂e' in page.decode('utf-8') and 'ทั้งวงจร' in page.decode('utf-8')
def ask(question, origin='http://127.0.0.1:8767'):
    body = json.dumps({'question': question}, ensure_ascii=False).encode()
    request = urllib.request.Request('http://127.0.0.1:8767/ask', data=body,
        headers={'Content-Type':'application/json','Origin':origin})
    try:
        with urllib.request.urlopen(request, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        error_body = e.read()
        try:
            return e.code, json.loads(error_body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return e.code, {'error':error_body.decode('utf-8',errors='replace')[:2000]}
status, fame = ask('FAME functional unit 1000 MJ')
assert status == 200 and 'fame-functional-unit' in [hit['id'] for hit in fame['hits']], fame
assert fame['hits'][0]['source_url'] and fame['hits'][0]['locator']
assert fame['search_id']
status, _ = ask('test', origin='https://attacker.invalid')
assert status == 403, status
review = urllib.request.Request('http://127.0.0.1:8767/review',
    data=json.dumps({'search_id':fame['search_id'],'verdict':'uncertain','note':'container smoke'}).encode(),
    headers={'Content-Type':'application/json','Origin':'http://127.0.0.1:8767'})
with urllib.request.urlopen(review, timeout=10) as response:
    saved = json.loads(response.read())
assert saved['saved'] is True, saved
print(json.dumps({'ready_records': ready['evidence_records'], 'page_status': 200,
  'fame_functional_unit_hit': 'fame-functional-unit', 'source_locator_present': True,
  'feedback_saved_to_tmp': True, 'wrong_origin_status': 403}, ensure_ascii=False))
'''
        try:
            result = run("docker", "exec", name, "python", "-c", probe)
        except RuntimeError as error:
            logs = run("docker", "logs", "--tail", "80", name, check=False)
            detail = (logs.stderr or logs.stdout or "").strip()[-6000:]
            raise RuntimeError(f"Functional smoke failed: {error}\nContainer logs:\n{detail}") from error
        inspection = json.loads(run("docker", "inspect", name).stdout)[0]
        hardening = {
            "network_mode": inspection["HostConfig"]["NetworkMode"],
            "read_only": inspection["HostConfig"]["ReadonlyRootfs"],
            "memory_bytes": inspection["HostConfig"]["Memory"],
            "memory_swap_bytes": inspection["HostConfig"]["MemorySwap"],
            "nano_cpus": inspection["HostConfig"]["NanoCpus"],
            "pids_limit": inspection["HostConfig"]["PidsLimit"],
            "user": inspection["Config"]["User"],
            "cap_drop": inspection["HostConfig"]["CapDrop"],
            "security_opt": inspection["HostConfig"]["SecurityOpt"],
            "gemini_key_present": any(value.startswith("GEMINI_API_KEY=")
                                       for value in inspection["Config"].get("Env", [])),
        }
        hardening["memory_usage"] = run("docker", "stats", "--no-stream", "--format",
                                         "{{.MemUsage}}", name).stdout.strip()
        assert hardening["network_mode"] == "none", hardening
        assert (hardening["read_only"] is True and hardening["memory_bytes"] == 536870912
                and hardening["memory_swap_bytes"] == memory_swap_mib * 1024 * 1024), hardening
        assert hardening["nano_cpus"] == 500000000 and hardening["pids_limit"] == 64, hardening
        assert hardening["user"] == "10001:10001" and hardening["cap_drop"] == ["ALL"], hardening
        assert not hardening["gemini_key_present"], hardening
        image_record = json.loads(run("docker", "image", "inspect", image).stdout)[0]
        report = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
                  "image": image, "image_id": image_record["Id"],
                  "architecture": f"{image_record['Os']}/{image_record['Architecture']}",
                  "probe": json.loads(result.stdout), "hardening": hardening,
                  "gemini_live_called": False, "production_changed": False}
        release_tag = image.rsplit(":", 1)[-1]
        safe_release = "".join(ch for ch in release_tag.lower() if ch.isalnum() or ch in "._-")[:64]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        evidence = (Path(__file__).resolve().parents[1] / "evidence"
                    / f"rag-image-verification-{safe_release}-{timestamp}.json")
        if evidence.exists():
            raise FileExistsError(f"Refusing to overwrite verification evidence: {evidence.name}")
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["evidence_path"] = evidence.as_posix()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        run("docker", "rm", "-f", name, check=False)


if __name__ == "__main__":
    main()
