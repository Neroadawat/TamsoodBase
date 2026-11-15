# RAG on EC2 — private loopback runbook

## Intended access

The RAG service runs as a separate TamsoodBase container. It does not replace `tamsoodbase-api`, MySQL, the HTTPS gateway, Caddy, or any Ginder service. The container joins an internal Docker network with fixed IP `10.253.77.2` and publishes no host port. The EC2 host can reach the container IP directly; an SSH local forward connects the developer computer to that internal IP:

```powershell
& 'C:\Windows\System32\OpenSSH\ssh.exe' -i 'C:\path\to\ec2-deploy.pem' -N -L 8877:10.253.77.2:8767 ubuntu@54.206.67.32
```

While that terminal remains open, visit `http://127.0.0.1:8877/`. The browser origin is allowlisted exactly; requests from a different origin receive 403. The SSH identity is the access control for this private demo. If `RAG_API_TOKEN` is configured, POST `/ask` and `/review` also require `Authorization: Bearer <token>`; keep this value in the server environment and a server-side Vercel proxy, never in browser code. Origin checking is not authentication. Do not add a public security-group rule, reverse proxy route, Vercel connection, or Cloudflare tunnel for this private prototype without completing the public release gates.

## Build and verify on the trusted workstation

From the repository root in PowerShell:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$python = '.\build\rag-verified-venv\Scripts\python.exe'
& $python .\scripts\package_rag_ec2.py
```

Use the release and context printed by the packager, then verify every allowlisted file and archive hash before building:

```powershell
$release = '<release printed by package_rag_ec2.py>'
$context = (Resolve-Path ".\build\rag-ec2-$release\context").Path
$archive = (Resolve-Path ".\build\rag-ec2-$release\tamsoodbase-rag-$release.zip").Path
& $python .\scripts\verify_rag_ec2_package.py $context $archive
docker build --pull=false -t "tamsoodbase-rag:$release" -f "$context\Dockerfile" $context
& $python .\scripts\verify_rag_image.py "tamsoodbase-rag:$release"
```

The image verification runs with `--network none`, read-only root filesystem, UID 10001, no Linux capabilities, no-new-privileges, 512 MiB RAM with a 1 GiB total RAM+swap ceiling, 0.5 CPU, and 64 PIDs. A no-swap 512 MiB trial was OOM-killed, so this deployment explicitly permits at most 512 MiB swap and aborts staging if host available RAM falls under 320 MiB or API readiness changes. The current image used about 501 MiB in the isolated local check, so this EC2 has limited headroom; staging aborts if the host health/resource guard fails. It checks page/readiness, exact statistical fact selection and cited source IDs for capacity, methane-null and whole-life-null questions, plus rejection of a wrong Origin. Do not upload a failing image.

## First installation on the owned TamsoodBase host

1. Recheck owner labels, API health/image, Ginder container snapshot, available RAM/disk, and that the fixed internal subnet `10.253.77.0/29` does not overlap any host route or existing Docker network. Require at least 832 MiB (851,968 KiB as read from `/proc/meminfo`) available RAM before staging: the 512 MiB container RAM ceiling plus the 320 MiB host safety reserve. The staging and startup checks continue enforcing the 320 MiB floor; abort if any precondition differs or the owner is unclear.
2. Save the tested image to a transfer archive and record its SHA-256. Transfer only the image archive and `deploy/install_rag_ec2.sh` over SSH/SCP. Do not transfer `.env`, API keys, raw source PDFs/CSVs, local Qdrant files, or a repository checkout.
3. On EC2, verify the transferred archive hash, `docker load` it, then invoke `bash install_rag_ec2.sh <release> <sha256:image-id>`. The script verifies the image ID and `amd64` architecture, stages the container at `10.253.77.2` on the internal-only network, checks its answer/citation and Docker hardening, then activates `tamsoodbase-rag` at the same address. It publishes no port. It aborts if the active API owner/health, Ginder snapshot, or resource gates are not preserved.
4. Check `http://10.253.77.2:8767/readyz` from the EC2 host and open the SSH-forwarded local URL. Keep the pre-existing API, all old images, and rollback containers untouched.

## Rollback and limits

For this initial additive deployment, rollback removes only the owner-verified `tamsoodbase-rag` container:

```bash
bash rollback_rag_ec2.sh
```

The image/package remain for diagnosis. The installer refuses to replace an existing RAG container. If a future update is needed, prepare a separate versioned replacement and rollback procedure; do not edit this first-install script into an unreviewed in-place upgrade.

## Updating an existing private RAG release

The first-install script intentionally refuses to replace a running RAG service. For a reviewed image that has passed the local package and image gates, copy `deploy/upgrade_rag_ec2.sh` and `deploy/rollback_rag_ec2.sh` to the private deployment directory, verify their SHA-256 hashes, and run:

```bash
bash upgrade_rag_ec2.sh <release> <sha256:image-id>
```

The updater checks the API/RAG owner and health labels, the internal network/IP, image identity/architecture, memory floor, API state and Ginder snapshot. It stops and renames only the current owner-verified RAG container, starts the new release at the same internal IP, and keeps the old container stopped under a versioned rollback name. If readiness, the method-answer smoke, API, memory, or Docker health gates fail, it removes only the candidate and restores the prior RAG release. To intentionally restore the previous release after a successful update, run `bash rollback_rag_ec2.sh`; it checks owner labels and verifies API/Ginder are unchanged. Rollback requires the previous image and container to remain on the host.

## Current deployment and limits

Release `1c49e9d40b4b3936` is deployed privately on `10.253.77.2:8767`; the preceding release is retained for rollback. The current SSH-forwarded local URL is `http://127.0.0.1:8877/` while the SSH tunnel remains open. No security-group rule, gateway route, or public port was added.

The API gateway was already reported unhealthy before this RAG install; this runbook does not repair or route through it. The RAG is not connected to Vercel or the public UI. Curated evidence still contains source reuse/redistribution statuses that are not cleared. Keep this package and endpoint private; deploying it does not grant data rights or make the records a normalized/full-lifecycle LCI dataset. Gemini is absent and no external LLM request is made by this image.

### Runtime package reconciliation — 10 November 2026

The 10 Nov source tree had drifted from the earlier EC2 image contract: its Docker command flags, health paths, runtime imports, and the installer’s smoke-question corpus no longer matched the checked-in files. The source now supports the in-memory server command, health/readiness endpoints, exact origin checks, optional server-side bearer authentication, and feedback under `/tmp`; the image/package allowlist includes its required Python modules. Initial package `4c61c7690224d841` was superseded by candidate `51d0ef861af7eb51` after deployment-profile metadata was included in the release digest. The current candidate archive SHA-256 is `9b627d4440d849badc172e9d8ccf77e3002a60b70693c6c0e68ea9c32a09ba1d`; its 19-file context and archive hashes verify locally. It has **not** been built with Docker, uploaded, or deployed: the Docker Desktop Linux engine was unavailable during this check. The deployed EC2 release remains `1c49e9d40b4b3936`; Vercel remains disconnected from EC2, and no rights or Production setting changed.

### Local candidate build and smoke verification — 12 November 2026

The Docker Desktop Linux Engine is now available on the development workstation. Candidate `51d0ef861af7eb51` built, but its isolated question smoke returned 503 because `docs/rag/retrieval-scope.json`, a runtime dependency of `rag_scope.py`, was absent from the package and image. The allowlist and Dockerfile now both include this file, with a targeted regression assertion. Candidate `9c767ef49301347b` was package-hash verified (20 files; ZIP SHA-256 `9705e8cda7c65302e1deb8d29f6236966f4390341e8391ec29bc4d12a121ceac`), built as Linux/amd64 image `sha256:1bf44daf6880dd3e65ef1fa115f3708e0156145a66bc87cb7366e441202cbdd1`, and passed the isolated image smoke: 10 evidence cards ready, page/readiness 200, FAME FU query returned the expected card with URL/locator, wrong Origin 403, feedback wrote to tmpfs. Runtime hardening verified network `none`, read-only root, UID 10001, dropped all capabilities, no-new-privileges, no Gemini key, 512 MiB memory, 1 GiB memory+swap and 0.5 CPU; observed memory was 499 MiB / 512 MiB. Targeted runtime/package tests passed 3/3. Details: `evidence/rag-image-verification-9c767ef49301347b-20261111T223742Z.json` and `evidence/rag-ec2-candidate-build-2026-11-12.json`.

This is a **local private candidate only**: no transfer, EC2 command, live Gemini call, Vercel integration, or Production change occurred. Do not upgrade EC2 from this workstation result. Before any owner-approved upgrade, recheck the host's current memory floor, the active API/Ginder baseline and rollback preconditions; the tested image used nearly all of its 512 MiB container limit. The existing private EC2 deployment remains the separately recorded older release `1c49e9d40b4b3936` pending a new authorized preflight and all release gates.


### Rollback error handling review — 12 November 2026

The rollback script now fails closed if Docker cannot enumerate retained RAG releases; it will not interpret a failed listing as “no backup” and remove the active service. Git Bash syntax and isolated success/failure mocks pass. This does not replace a live owner-approved EC2 rollback drill. See `evidence/rag-rollback-script-fail-closed-2026-11-12.json`.
