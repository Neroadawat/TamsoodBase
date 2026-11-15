#!/usr/bin/env bash
set -Eeuo pipefail

script="$(cd "$(dirname "$0")/.." && pwd)/deploy/rollback_rag_ec2.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

failure_log="$tmp/failure.log"
set +e
output="$(MOCK_LOG="$failure_log" bash -c '
  docker() {
    if [[ "$1 $2" == "ps -a" ]]; then printf "ginder-api=Up\n"; return 0; fi
    if [[ "$1 $2" == "inspect -f" ]]; then
      format="$3"; name="$4"
      if [[ "$format" == *org.tamsood.project* ]]; then [[ "$name" == tamsoodbase-rag || "$name" == tamsoodbase-api ]] && printf TamsoodBase; return 0; fi
      if [[ "$format" == *org.tamsood.service* ]]; then [[ "$name" == tamsoodbase-rag ]] && printf RAG; return 0; fi
      case "$format:$name" in
        "{{.Image}}|{{.State.Health.Status}}:tamsoodbase-api") printf "api-image|healthy";;
        "{{.State.Health.Status}}:tamsoodbase-api") printf healthy;;
        *) return 2;;
      esac
      return 0
    fi
    if [[ "$1 $2" == "ps -aq" ]]; then printf "inspect-error: simulated Docker listing failure\n" >&2; return 9; fi
    if [[ "$1" == rm ]]; then printf "rm %s\n" "${*: -1}" >>"$MOCK_LOG"; return 0; fi
    return 2
  }
  source "$1"
' _ "$script" 2>&1)"
status=$?
set -e
[[ "$status" -ne 0 ]]
[[ "$output" == *"could not inspect previous RAG releases"* ]]
[[ ! -s "$failure_log" ]]
printf 'PASS: backup-list failure aborts without removing the active RAG container\n'

success_log="$tmp/success.log"
output="$(MOCK_LOG="$success_log" bash -c '
  docker() {
    if [[ "$1 $2" == "ps -a" ]]; then printf "ginder-api=Up\n"; return 0; fi
    if [[ "$1 $2" == "ps -aq" ]]; then printf "rollback-previous\n"; return 0; fi
    if [[ "${1:-} ${2:-} ${3:-}" == "network inspect -f" ]]; then printf true; return 0; fi
    if [[ "$1 $2" == "inspect -f" ]]; then
      format="$3"; name="$4"
      if [[ "$format" == *org.tamsood.project* ]]; then [[ "$name" == tamsoodbase-rag || "$name" == rollback-previous || "$name" == tamsoodbase-api ]] && printf TamsoodBase; return 0; fi
      if [[ "$format" == *org.tamsood.service* ]]; then [[ "$name" == tamsoodbase-rag || "$name" == rollback-previous ]] && printf RAG; return 0; fi
      case "$format:$name" in
        "{{.Image}}|{{.State.Health.Status}}:tamsoodbase-api") printf "api-image|healthy";;
        "{{.State.Health.Status}}:tamsoodbase-api") printf healthy;;
        "{{.State.Running}}:rollback-previous") printf false;;
        "{{.Internal}}:tamsoodbase-rag-private") printf true;;
        *) return 2;;
      esac
      return 0
    fi
    case "$1" in
      rm|network|rename|update|start) printf "%s %s\n" "$1" "${*: -1}" >>"$MOCK_LOG"; return 0;;
      *) return 2;;
    esac
  }
  curl() { [[ "${!#}" == "http://10.253.77.2:8767/readyz" ]]; }
  sleep() { :; }
  source "$1"
' _ "$script" 2>&1)"
[[ "$output" == *"Restored previous RAG release; API and Ginder state unchanged."* ]]
grep -Fqx 'rm tamsoodbase-rag' "$success_log"
grep -Fqx 'rename tamsoodbase-rag' "$success_log"
printf 'PASS: owner-verified previous release is restored and readiness checked\n'
