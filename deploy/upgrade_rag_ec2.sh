#!/usr/bin/env bash
set -Eeuo pipefail

release="${1:?usage: upgrade_rag_ec2.sh RELEASE SHA256_IMAGE_ID}"
expected_image_id="${2:?usage: upgrade_rag_ec2.sh RELEASE SHA256_IMAGE_ID}"
active="tamsoodbase-rag"
api="tamsoodbase-api"
network="tamsoodbase-rag-private"
network_subnet="10.253.77.0/29"
rag_ip="10.253.77.2"
image="tamsoodbase-rag:${release}"
stage="tamsoodbase-rag-update-stage-${release}"
old_release=""
rollback=""
old_moved=0
success=0

fail() { printf 'RAG upgrade aborted: %s\n' "$*" >&2; exit 1; }
owner_of() { docker inspect -f '{{ index .Config.Labels "org.tamsood.project" }}' "$1" 2>/dev/null || true; }
service_of() { docker inspect -f '{{ index .Config.Labels "org.tamsood.service" }}' "$1" 2>/dev/null || true; }
api_healthy() { [[ "$(docker inspect -f '{{.State.Health.Status}}' "$api" 2>/dev/null || true)" == "healthy" ]] && curl -fsS --max-time 3 http://127.0.0.1:8765/readyz >/dev/null; }

restore_previous() {
  local active_release restore_ready health
  set +e
  if [[ "$(owner_of "$active")" == "TamsoodBase" && "$(service_of "$active")" == "RAG" ]]; then
    active_release="$(docker inspect -f '{{ index .Config.Labels "org.tamsood.release" }}' "$active" 2>/dev/null || true)"
    if [[ "$active_release" != "$old_release" ]]; then
      docker rm -f "$active" >/dev/null 2>&1
      if docker inspect "$active" >/dev/null 2>&1; then
        printf 'Rollback failed: candidate RAG container could not be removed.\n' >&2
        return 1
      fi
    fi
  fi
  if [[ -n "$rollback" && "$(owner_of "$rollback")" == "TamsoodBase" && "$(service_of "$rollback")" == "RAG" ]]; then
    if ! docker inspect -f '{{json .NetworkSettings.Networks}}' "$rollback" | grep -q 'tamsoodbase-rag-private'; then
      docker network connect --ip "$rag_ip" "$network" "$rollback" >/dev/null 2>&1
    fi
    if ! docker inspect "$active" >/dev/null 2>&1 && ! docker rename "$rollback" "$active" >/dev/null 2>&1; then
      printf 'Rollback failed: could not restore the previous container name.\n' >&2
      return 1
    fi
    docker update --restart unless-stopped "$active" >/dev/null 2>&1
    docker start "$active" >/dev/null 2>&1
  elif [[ "$(owner_of "$active")" == "TamsoodBase" && "$(service_of "$active")" == "RAG" \
      && "$(docker inspect -f '{{ index .Config.Labels "org.tamsood.release" }}' "$active" 2>/dev/null || true)" == "$old_release" ]]; then
    docker start "$active" >/dev/null 2>&1
  else
    printf 'Rollback failed: no owner-verified prior RAG container is available.\n' >&2
    return 1
  fi

  restore_ready=0
  for _ in $(seq 1 120); do
    health="$(docker inspect -f '{{.State.Health.Status}}' "$active" 2>/dev/null || true)"
    if [[ "$health" == "healthy" ]] && curl -fsS --max-time 3 "http://$rag_ip:8767/readyz" >/dev/null 2>&1; then
      restore_ready=1
      break
    fi
    sleep 2
  done
  if [[ "$restore_ready" != 1 ]]; then
    printf 'Rollback failed: prior RAG release did not pass Docker health and /readyz checks; manual owner review is required.\n' >&2
    return 1
  fi
  if ! api_healthy || [[ "$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api" 2>/dev/null || true)" != "$api_before" ]]; then
    printf 'Rollback failed: API health or image changed during recovery; manual owner review is required.\n' >&2
    return 1
  fi
  if [[ "$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)" != "$ginder_before" ]]; then
    printf 'Rollback failed: Ginder container state changed during recovery; manual owner review is required.\n' >&2
    return 1
  fi
  set -e
  return 0
}

on_exit() {
  status=$?
  docker rm -f "$stage" >/dev/null 2>&1 || true
  if (( status != 0 && old_moved == 1 && success == 0 )); then
    printf 'Restoring the owner-verified prior RAG image.\n' >&2
    if ! restore_previous; then
      printf 'CRITICAL: automatic RAG rollback did not verify cleanly; stop further changes and have the host owner inspect the API, RAG, and Ginder state.\n' >&2
    fi
  fi
  exit "$status"
}
trap on_exit EXIT

[[ "$release" =~ ^[a-f0-9]{16}$ ]] || fail "invalid release id"
[[ "$expected_image_id" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "invalid expected image id"
[[ "$(owner_of "$api")" == "TamsoodBase" ]] || fail "API owner label is not TamsoodBase"
api_healthy || fail "API is not healthy before update"
[[ "$(owner_of "$active")" == "TamsoodBase" && "$(service_of "$active")" == "RAG" ]] || fail "active RAG owner/service label is not TamsoodBase/RAG"
[[ "$(docker inspect -f '{{.State.Health.Status}}' "$active")" == "healthy" ]] || fail "existing RAG is not healthy"
[[ "$(docker inspect -f '{{(index .NetworkSettings.Networks "tamsoodbase-rag-private").IPAddress}}' "$active")" == "$rag_ip" ]] || fail "existing RAG is not on the expected internal IP"
[[ "$(docker network inspect -f '{{.Internal}}' "$network")" == "true" ]] || fail "RAG network is not internal"
[[ "$(docker network inspect -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}' "$network")" == "$network_subnet" ]] || fail "RAG subnet changed"
bindings="$(docker inspect -f '{{json .HostConfig.PortBindings}}' "$active")"
[[ "$bindings" == "null" || "$bindings" == "{}" ]] || fail "existing RAG has unexpected published ports"
docker image inspect "$image" >/dev/null 2>&1 || fail "new image is not loaded"
[[ "$(docker image inspect -f '{{.Id}}' "$image")" == "$expected_image_id" ]] || fail "loaded image id differs from tested image"
[[ "$(docker image inspect -f '{{.Architecture}}' "$image")" == "amd64" ]] || fail "new image architecture is not amd64"
api_before="$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api")"
ginder_before="$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)"
[[ -n "$ginder_before" ]] || fail "Ginder baseline unavailable"
available_kb="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
(( available_kb >= 327680 )) || fail "available host memory is below the 320 MiB safety floor (327680 KiB)"
old_release="$(docker inspect -f '{{ index .Config.Labels "org.tamsood.release" }}' "$active")"
[[ "$old_release" =~ ^[a-f0-9]{16}$ ]] || fail "prior release label is missing or invalid"
rollback="tamsoodbase-rag-rollback-${old_release}"
[[ -z "$(docker ps -aq --filter "name=^/${rollback}$")" ]] || fail "rollback container name already exists"

old_moved=1
docker stop --time 20 "$active" >/dev/null
docker network disconnect "$network" "$active"
docker rename "$active" "$rollback"
docker update --restart=no "$rollback" >/dev/null

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
  [[ "$(docker inspect -f '{{.State.OOMKilled}}' "$active" 2>/dev/null || true)" != "true" ]] || break
  api_healthy || break
  (( "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" >= 327680 )) || break
  sleep 2
done
[[ "$ready" == 1 ]] || { docker logs --tail 100 "$active" >&2 || true; fail "new RAG failed readiness; rollback will restore prior release"; }

RAG_TARGET="http://$rag_ip:8767" python3 - <<'PY'
import json, os, urllib.request
target=os.environ['RAG_TARGET']
body=json.dumps({'question':'FAME functional unit 1000 MJ'},ensure_ascii=False).encode()
request=urllib.request.Request(target+'/ask',data=body,headers={
    'Content-Type':'application/json','Origin':'http://127.0.0.1:8877'})
with urllib.request.urlopen(request,timeout=30) as response:
    result=json.load(response)
hit=next((item for item in result['hits'] if item['id']=='fame-functional-unit'),None)
assert hit and hit['source_url'] and hit['locator'],result
assert result['search_id'],result
print('new release narrative/source/feedback smoke passed')
PY
api_healthy || fail "API health/readiness changed during update"
[[ "$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api")" == "$api_before" ]] || fail "API image or health changed"
[[ "$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)" == "$ginder_before" ]] || fail "Ginder state changed during update"
bindings="$(docker inspect -f '{{json .HostConfig.PortBindings}}' "$active")"
[[ "$bindings" == "null" || "$bindings" == "{}" ]] || fail "new RAG unexpectedly publishes host ports"
health=starting
for _ in $(seq 1 90); do
  health="$(docker inspect -f '{{.State.Health.Status}}' "$active" 2>/dev/null || true)"
  [[ "$health" == "healthy" ]] && break
  [[ "$health" != "unhealthy" ]] || fail "new RAG Docker health check reports unhealthy"
  api_healthy || fail "API health/readiness changed while waiting for the RAG health check"
  (( "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" >= 327680 )) || fail "host memory fell below the 320 MiB safety floor (327680 KiB)"
  sleep 2
done
[[ "$health" == "healthy" ]] || fail "new RAG Docker health check did not become healthy"
success=1
printf 'RAG upgraded to %s; previous release kept stopped for rollback as %s; API/Ginder unchanged; no public port.\n' "$release" "$rollback"
