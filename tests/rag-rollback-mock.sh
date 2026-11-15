#!/usr/bin/env bash
set -Eeuo pipefail

script="$(cd "$(dirname "$0")/.." && pwd)/deploy/upgrade_rag_ec2.sh"
source <(awk '/^restore_previous\(\) \{/{capture=1} /^on_exit\(\) \{/{capture=0} capture' "$script")

active=tamsoodbase-rag
api=tamsoodbase-api
network=tamsoodbase-rag-private
rag_ip=10.253.77.2
rollback=tamsoodbase-rag-rollback-aaaaaaaaaaaaaaaa
old_release=aaaaaaaaaaaaaaaa
api_before='api-image|healthy'
ginder_before='ginder-api=Up'
MOCK_ACTIVE_EXISTS=1
MOCK_ROLLBACK_EXISTS=1
MOCK_ACTIVE_RELEASE=bbbbbbbbbbbbbbbb
MOCK_ACTIVE_HEALTH=unhealthy
MOCK_API_IMAGE=api-image
MOCK_API_HEALTH=healthy
MOCK_RAG_READY=1

owner_of() { [[ "$1" == "$api" ]] && { printf 'TamsoodBase'; return; }; [[ "$1" == "$active" || "$1" == "$rollback" ]] && printf 'TamsoodBase'; }
service_of() { [[ "$1" == "$active" || "$1" == "$rollback" ]] && printf 'RAG'; }
api_healthy() { [[ "$MOCK_API_HEALTH" == healthy ]]; }
seq() { printf '1\n'; }
sleep() { :; }
curl() {
  local url="${!#}"
  case "$url" in
    http://127.0.0.1:8765/readyz) return 0 ;;
    http://10.253.77.2:8767/readyz) [[ "$MOCK_RAG_READY" == 1 ]] ;;
    *) return 22 ;;
  esac
}
docker() {
  if [[ "$1 $2" == 'ps -a' ]]; then printf '%s\n' "$ginder_before"; return 0; fi
  if [[ "$1 $2" == 'inspect -f' ]]; then
    format="$3"; name="${4:-}"
    if [[ "$name" == "$api" ]]; then
      case "$format" in
        '{{.State.Health.Status}}') printf 'healthy';;
        '{{.Image}}|{{.State.Health.Status}}') printf '%s|healthy' "$MOCK_API_IMAGE";;
        *) return 2;;
      esac
      return 0
    fi
    case "$format" in
      '{{ index .Config.Labels "org.tamsood.project" }}') [[ "$name" == "$active" || "$name" == "$rollback" ]] && printf 'TamsoodBase';;
      '{{ index .Config.Labels "org.tamsood.service" }}') [[ "$name" == "$active" || "$name" == "$rollback" ]] && printf 'RAG';;
      '{{ index .Config.Labels "org.tamsood.release" }}')
        if [[ "$name" == "$active" && "$MOCK_ACTIVE_EXISTS" == 1 ]]; then printf '%s' "$MOCK_ACTIVE_RELEASE";
        elif [[ "$name" == "$rollback" && "$MOCK_ROLLBACK_EXISTS" == 1 ]]; then printf '%s' "$old_release";
        else return 1; fi;;
      '{{json .NetworkSettings.Networks}}') [[ "$name" == "$rollback" && "$MOCK_ROLLBACK_EXISTS" == 1 ]] && printf '{"tamsoodbase-rag-private":{}}';;
      '{{.State.Health.Status}}') [[ "$name" == "$active" && "$MOCK_ACTIVE_EXISTS" == 1 ]] && printf '%s' "$MOCK_ACTIVE_HEALTH";;
      *) return 2;;
    esac
    return
  fi
  case "$1" in
    inspect)
      name="$2"
      [[ "$name" == "$active" && "$MOCK_ACTIVE_EXISTS" == 1 ]] && return 0
      [[ "$name" == "$rollback" && "$MOCK_ROLLBACK_EXISTS" == 1 ]] && return 0
      return 1;;
    rm)
      name="${*: -1}"
      if [[ "$name" == "$active" ]]; then MOCK_ACTIVE_EXISTS=0; return 0; fi
      return 1;;
    rename)
      MOCK_ACTIVE_EXISTS=1; MOCK_ROLLBACK_EXISTS=0
      MOCK_ACTIVE_RELEASE="$old_release"; MOCK_ACTIVE_HEALTH="${MOCK_RESTORE_HEALTH:-healthy}"; return 0;;
    start)
      MOCK_ACTIVE_EXISTS=1; MOCK_ACTIVE_HEALTH="${MOCK_RESTORE_HEALTH:-healthy}"; return 0;;
    update) return 0;;
    *) return 2;;
  esac
}

if ! restore_previous; then
  printf 'FAIL: healthy prior release did not pass rollback verification\n' >&2
  exit 1
fi
[[ "$MOCK_ACTIVE_EXISTS" == 1 && "$MOCK_ACTIVE_RELEASE" == "$old_release" ]]
[[ "$MOCK_ACTIVE_HEALTH" == healthy ]]
printf 'PASS: healthy prior release is restored and verified\n'

run_failed_restore_case() (
  MOCK_ACTIVE_EXISTS=1
  MOCK_ROLLBACK_EXISTS=1
  MOCK_ACTIVE_RELEASE=bbbbbbbbbbbbbbbb
  MOCK_ACTIVE_HEALTH=unhealthy
  MOCK_RAG_READY=0
  out=''
  if out="$(restore_previous 2>&1)"; then
    printf 'FAIL: rollback unexpectedly passed without readiness\n' >&2
    exit 1
  fi
  [[ "$out" == *'prior RAG release did not pass Docker health and /readyz checks'* ]]
  printf 'PASS: failed recovery is reported for owner review\n'
)
run_failed_restore_case

run_api_change_case() (
  MOCK_ACTIVE_EXISTS=1
  MOCK_ROLLBACK_EXISTS=1
  MOCK_ACTIVE_RELEASE=bbbbbbbbbbbbbbbb
  MOCK_ACTIVE_HEALTH=unhealthy
  MOCK_RAG_READY=1
  MOCK_API_IMAGE=changed-api-image
  out=''
  if out="$(restore_previous 2>&1)"; then
    printf 'FAIL: rollback unexpectedly passed after API image change\n' >&2
    exit 1
  fi
  [[ "$out" == *'API health or image changed during recovery'* ]]
  printf 'PASS: API change during recovery is reported\n'
)
run_api_change_case
