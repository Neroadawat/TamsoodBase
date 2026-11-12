#!/usr/bin/env bash
set -Eeuo pipefail

active="tamsoodbase-rag"
network="tamsoodbase-rag-private"
api="tamsoodbase-api"
rag_ip="10.253.77.2"
owner_of() { docker inspect -f '{{ index .Config.Labels "org.tamsood.project" }}' "$1" 2>/dev/null || true; }
service_of() { docker inspect -f '{{ index .Config.Labels "org.tamsood.service" }}' "$1" 2>/dev/null || true; }

[[ "$(owner_of "$active")" == "TamsoodBase" && "$(service_of "$active")" == "RAG" ]] || {
  echo "Rollback refused: active service absent or owner/service label differs" >&2; exit 1;
}
api_before="$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api")"
[[ "$(owner_of "$api")" == "TamsoodBase" && "$(docker inspect -f '{{.State.Health.Status}}' "$api")" == "healthy" ]] || {
  echo "Rollback refused: API owner/readiness precondition failed" >&2; exit 1;
}
ginder_before="$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)"
[[ -n "$ginder_before" ]] || { echo "Rollback refused: Ginder baseline unavailable" >&2; exit 1; }

backup_list="$(docker ps -aq --filter 'name=^/tamsoodbase-rag-rollback-')" || {
  echo "Rollback refused: could not inspect previous RAG releases; active service was left unchanged" >&2
  exit 1
}
backups=()
if [[ -n "$backup_list" ]]; then mapfile -t backups <<<"$backup_list"; fi
if ((${#backups[@]} == 0)); then
  docker rm -f "$active"
  echo "Removed only the owner-verified TamsoodBase RAG container; image/package remain."
  exit 0
fi
((${#backups[@]} == 1)) || { echo "Rollback refused: more than one RAG rollback container exists" >&2; exit 1; }
backup="${backups[0]}"
[[ "$(owner_of "$backup")" == "TamsoodBase" && "$(service_of "$backup")" == "RAG" ]] || {
  echo "Rollback refused: previous container owner/service label differs" >&2; exit 1;
}
[[ "$(docker inspect -f '{{.State.Running}}' "$backup")" == "false" ]] || {
  echo "Rollback refused: previous release is not stopped" >&2; exit 1;
}
[[ "$(docker network inspect -f '{{.Internal}}' "$network")" == "true" ]] || {
  echo "Rollback refused: RAG network is not internal" >&2; exit 1;
}
docker rm -f "$active" >/dev/null
docker network connect --ip "$rag_ip" "$network" "$backup"
docker rename "$backup" "$active"
docker update --restart unless-stopped "$active" >/dev/null
docker start "$active" >/dev/null

ready=0
for _ in $(seq 1 120); do
  if curl -fsS --max-time 3 "http://$rag_ip:8767/readyz" >/dev/null 2>&1; then ready=1; break; fi
  sleep 2
done
[[ "$ready" == 1 ]] || { echo "Rollback release failed readiness; investigate before further changes" >&2; exit 1; }
[[ "$(docker inspect -f '{{.Image}}|{{.State.Health.Status}}' "$api")" == "$api_before" ]] || {
  echo "API state changed during rollback" >&2; exit 1;
}
[[ "$(docker ps -a --filter 'name=ginder-' --format '{{.Names}}={{.Status}}' | sort)" == "$ginder_before" ]] || {
  echo "Ginder state changed during rollback" >&2; exit 1;
}
echo "Restored previous RAG release; API and Ginder state unchanged."
