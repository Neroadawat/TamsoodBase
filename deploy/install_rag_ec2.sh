#!/usr/bin/env bash
set -Eeuo pipefail

release="${1:?usage: install_rag_ec2.sh RELEASE IMAGE_ID}"
expected_image_id="${2:?usage: install_rag_ec2.sh RELEASE IMAGE_ID}"
image="tamsoodbase-rag:${release}"
network="tamsoodbase-rag-private"
network_subnet="10.253.77.0/29"
rag_ip="10.253.77.2"
stage="tamsoodbase-rag-stage-${release}"
active="tamsoodbase-rag"
api="tamsoodbase-api"
MIN_INSTALL_AVAILABLE_KB=851968 # 512 MiB container RAM ceiling + 320 MiB host safety reserve

fail() { printf 'RAG install aborted: %s\n' "$*" >&2; exit 1; }
owner_of() { docker inspect -f '{{ index .Config.Labels "org.tamsood.project" }}' "$1" 2>/dev/null || true; }

[[ "$release" =~ ^[a-f0-9]{16}$ ]] || fail "invalid release id"
[[ "$expected_image_id" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "invalid expected image id"
[[ "$(owner_of "$api")" == "TamsoodBase" ]] || fail "active API owner label is not TamsoodBase"
[[ "$(docker inspect -f '{{.State.Running}}' "$api" 2>/dev/null)" == "true" ]] || fail "active API is not running"
[[ "$(docker inspect -f '{{.State.Health.Status}}' "$api" 2>/dev/null)" == "healthy" ]] || fail "active API is not healthy"
[[ ! "$(docker ps -aq --filter "name=^/${active}$")" ]] || fail "RAG service name already exists; refusing to replace it"

available_kb="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
(( available_kb >= MIN_INSTALL_AVAILABLE_KB )) || fail "host MemAvailable below 832 MiB (851968 KiB: 512 MiB container ceiling + 320 MiB host reserve)"
free_kb="$(df -Pk /home/ubuntu/tamsoodbase | awk 'NR==2 {print $4}')"
(( free_kb >= 1048576 )) || fail "less than 1 GiB free on the project filesystem"

api_before="$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api")"
ginder_before="$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)"
[[ -n "$ginder_before" ]] || fail "Ginder owner baseline unavailable"
docker image inspect "$image" >/dev/null 2>&1 || fail "image $image is not loaded"
[[ "$(docker image inspect -f '{{.Id}}' "$image")" == "$expected_image_id" ]] || fail "loaded image id does not match the tested image"
[[ "$(docker image inspect -f '{{.Architecture}}' "$image")" == "amd64" ]] || fail "image architecture does not match this EC2 deployment target"

if docker network inspect "$network" >/dev/null 2>&1; then
  [[ "$(docker network inspect -f '{{.Internal}}' "$network")" == "true" ]] || fail "existing RAG network is not internal"
  [[ "$(docker network inspect -f '{{ index .Labels "org.tamsood.project" }}' "$network")" == "TamsoodBase" ]] || fail "existing RAG network has a different owner"
  [[ "$(docker network inspect -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}' "$network")" == "$network_subnet" ]] || fail "existing RAG network has an unexpected subnet"
else
  python3 - "$network_subnet" <<'PY'
import ipaddress, json, subprocess, sys
candidate = ipaddress.ip_network(sys.argv[1], strict=True)
routes = subprocess.check_output(['ip', '-o', 'route', 'show', 'table', 'all'], text=True)
for row in routes.splitlines():
    try:
        route = ipaddress.ip_network(row.split()[0], strict=False)
    except (ValueError, IndexError):
        continue
    if route.version == candidate.version and route.overlaps(candidate):
        raise SystemExit(f'RAG subnet overlaps host route {route}')
ids = subprocess.check_output(['docker', 'network', 'ls', '-q'], text=True).split()
for network_id in ids:
    details = json.loads(subprocess.check_output(['docker', 'network', 'inspect', network_id], text=True))[0]
    for config in details.get('IPAM', {}).get('Config') or []:
        try:
            subnet = ipaddress.ip_network(config.get('Subnet', ''), strict=False)
        except ValueError:
            continue
        if subnet.version == candidate.version and subnet.overlaps(candidate):
            raise SystemExit(f'RAG subnet overlaps existing Docker network {details["Name"]}: {subnet}')
PY
  docker network create --driver bridge --internal --subnet "$network_subnet" --label org.tamsood.project=TamsoodBase "$network" >/dev/null
fi

docker run -d --name "$stage" \
  --label org.tamsood.project=TamsoodBase \
  --label org.tamsood.service=RAG-staging \
  --label org.tamsood.release="$release" \
  --network "$network" --ip "$rag_ip" \
  --env RAG_ALLOWED_ORIGIN=http://127.0.0.1:8877 \
  --user 10001:10001 --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL --security-opt no-new-privileges:true \
  --memory 512m --memory-swap 1g --cpus 0.50 --pids-limit 64 --restart=no \
  --log-opt max-size=10m --log-opt max-file=2 "$image" >/dev/null

cleanup_stage() { docker rm -f "$stage" >/dev/null 2>&1 || true; }
trap cleanup_stage EXIT

ready=0
for _ in $(seq 1 120); do
  if curl -fsS --max-time 3 "http://$rag_ip:8767/readyz" >/dev/null 2>&1; then ready=1; break; fi
  if [[ "$(docker inspect -f '{{.State.OOMKilled}}' "$stage" 2>/dev/null || true)" == "true" ]]; then
    docker logs --tail 80 "$stage" >&2 || true
    fail "staging container was OOM-killed"
  fi
  [[ "$(docker inspect -f '{{.State.Health.Status}}' "$api" 2>/dev/null || true)" == "healthy" ]] || fail "active API health changed during RAG staging"
  sleep 2
done
[[ "$ready" == 1 ]] || { docker logs --tail 100 "$stage" >&2 || true; fail "staging readiness timed out"; }

RAG_TARGET="http://$rag_ip:8767" python3 - <<'PY'
import json, urllib.request
import os
url = os.environ['RAG_TARGET']+'/ask'
body = json.dumps({'question': 'FAME functional unit 1000 MJ'}, ensure_ascii=False).encode()
request = urllib.request.Request(url, data=body, headers={
    'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:8877'
})
with urllib.request.urlopen(request, timeout=15) as response:
    payload = json.load(response)
hit = next((item for item in payload['hits'] if item['id'] == 'fame-functional-unit'), None)
assert hit and hit['source_url'] and hit['locator'], payload
assert payload['search_id'], payload
print('staging smoke passed: narrative hit, source locator, and feedback token')
PY

stage_hardening="$(docker inspect -f '{{.HostConfig.ReadonlyRootfs}}|{{.HostConfig.Memory}}|{{.HostConfig.MemorySwap}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.PidsLimit}}|{{.Config.User}}' "$stage")"
[[ "$stage_hardening" == "true|536870912|1073741824|500000000|64|10001:10001" ]] || fail "staging container hardening did not match expected settings: $stage_hardening"
stage_ip="$(docker inspect -f '{{(index .NetworkSettings.Networks "tamsoodbase-rag-private").IPAddress}}' "$stage")"
[[ "$stage_ip" == "$rag_ip" ]] || fail "staging RAG IP did not match the SSH-tunnel target"
stage_bindings="$(docker inspect -f '{{json .HostConfig.PortBindings}}' "$stage")"
[[ "$stage_bindings" == "null" || "$stage_bindings" == "{}" ]] || fail "staging container unexpectedly publishes a host port"
stage_memory="$(docker stats --no-stream --format '{{.MemUsage}}' "$stage")"
host_available_kb="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
(( host_available_kb >= 327680 )) || fail "host MemAvailable fell below 320 MiB during staging: ${host_available_kb} KiB"
curl -fsS --max-time 4 http://127.0.0.1:8765/readyz >/dev/null || fail "active API readiness changed during staging"
cleanup_stage
trap - EXIT

docker run -d --name "$active" \
  --label org.tamsood.project=TamsoodBase \
  --label org.tamsood.service=RAG \
  --label org.tamsood.release="$release" \
  --network "$network" --ip "$rag_ip" \
  --env RAG_ALLOWED_ORIGIN=http://127.0.0.1:8877 \
  --user 10001:10001 --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL --security-opt no-new-privileges:true \
  --memory 512m --memory-swap 1g --cpus 0.50 --pids-limit 64 --restart unless-stopped \
  --log-opt max-size=10m --log-opt max-file=2 "$image" >/dev/null

ready=0
for _ in $(seq 1 120); do
  if curl -fsS --max-time 3 "http://$rag_ip:8767/readyz" >/dev/null 2>&1; then ready=1; break; fi
  if [[ "$(docker inspect -f '{{.State.OOMKilled}}' "$active" 2>/dev/null || true)" == "true" ]]; then break; fi
  host_available_kb="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
  (( host_available_kb >= 327680 )) || break
  [[ "$(docker inspect -f '{{.State.Health.Status}}' "$api" 2>/dev/null || true)" == "healthy" ]] || break
  sleep 2
done
if [[ "$ready" != 1 ]]; then
  docker logs --tail 100 "$active" >&2 || true
  docker rm -f "$active" >/dev/null 2>&1 || true
  fail "active RAG readiness failed; removed only the new RAG container and left the pre-existing API untouched"
fi

if ! RAG_TARGET="http://$rag_ip:8767" python3 - <<'PY'
import json, urllib.request
body = json.dumps({'question': 'FAME functional unit 1000 MJ'}, ensure_ascii=False).encode()
import os
request = urllib.request.Request(os.environ['RAG_TARGET']+'/ask', data=body, headers={
    'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:8877'
})
with urllib.request.urlopen(request, timeout=15) as response:
    payload = json.load(response)
hit = next((item for item in payload['hits'] if item['id'] == 'fame-functional-unit'), None)
assert hit and hit['source_url'] and hit['locator'], payload
assert payload['search_id'], payload
print('active loopback smoke passed')
PY
then
  docker rm -f "$active" >/dev/null 2>&1 || true
  fail "active RAG smoke failed; stopped the new RAG container and left the existing API untouched"
fi

active_ip="$(docker inspect -f '{{(index .NetworkSettings.Networks "tamsoodbase-rag-private").IPAddress}}' "$active")"
active_bindings="$(docker inspect -f '{{json .HostConfig.PortBindings}}' "$active")"
[[ "$active_ip" == "$rag_ip" ]] || { docker rm -f "$active" >/dev/null 2>&1 || true; fail "active RAG IP changed from the SSH-tunnel target"; }
[[ "$active_bindings" == "null" || "$active_bindings" == "{}" ]] || { docker rm -f "$active" >/dev/null 2>&1 || true; fail "active RAG published a host port"; }

api_after="$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api")"
ginder_after="$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)"
[[ "$api_after" == "$api_before" ]] || { docker rm -f "$active" >/dev/null 2>&1 || true; fail "API changed during additive install"; }
[[ "$ginder_after" == "$ginder_before" ]] || { docker rm -f "$active" >/dev/null 2>&1 || true; fail "Ginder container state changed during install"; }

printf 'RAG active on internal container IP %s; tunnel local 8877 to %s:8767; release=%s; staging memory=%s; rollback: bash rollback_rag_ec2.sh\n' "$rag_ip" "$rag_ip" "$release" "$stage_memory"

