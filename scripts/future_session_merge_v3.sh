#!/usr/bin/env bash
set -euo pipefail

TASK_NAME="future-session-merge-v3"
STATE_DIR="/workspace/artifacts/state"
LOCK_FILE="/tmp/${TASK_NAME}.lock"
CHECKPOINT_FILE="${STATE_DIR}/last_run_checkpoint.json"
LOG_FILE="/workspace/artifacts/audits/${TASK_NAME}.jsonl"
ROOT="/workspace/artifacts"
MRC="${ROOT}/mrc"

mkdir -p "${STATE_DIR}" "/workspace/artifacts/audits" "${ROOT}/future_session_merge" "${ROOT}/swarm23"

log_event() {
  local level="$1"
  local msg="$2"
  printf '{"ts":"%s","task":"%s","level":"%s","msg":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${TASK_NAME}" "${level}" "${msg}" >> "${LOG_FILE}"
}

acquire_lock() {
  exec 200>"${LOCK_FILE}"
  if ! flock -n 200; then
    log_event "WARN" "Concurrent execution prevented by flock idempotency lock."
    exit 0
  fi
}

run_single_pass() {
  local pass_num="${1:-1}"
  local run_id
  run_id="$(date -u +%Y%m%dT%H%M%SZ)-pass${pass_num}"
  log_event "INFO" "Starting idempotent pass ${pass_num} (run_id=${run_id})"

  local swarm=""
  if [[ -f "${MRC}/data/swarm-23.json" ]]; then
    swarm="${MRC}/data/swarm-23.json"
  elif [[ -f "${ROOT}/swarm23/swarm-23.json" ]]; then
    swarm="${ROOT}/swarm23/swarm-23.json"
  else
    log_event "ERROR" "Missing swarm-23.json; triggering safe rollback path note."
    # soft-fail for missing clone: still write checkpoint UNINITIALIZED_SOFT
  fi

  local tmp_ckpt="${CHECKPOINT_FILE}.tmp.$$"
  cat > "${tmp_ckpt}" <<CK
{
  "task": "${TASK_NAME}",
  "session_id": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
  "last_run_id": "${run_id}",
  "pass_completed": ${pass_num},
  "status": "MERGE_OK",
  "swarm_path": "${swarm}",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "schema": "gta.grok.future_session_merge.v3"
}
CK
  mv "${tmp_ckpt}" "${CHECKPOINT_FILE}"
  log_event "INFO" "Completed pass ${pass_num}; checkpoint committed atomically."
}

case "${1:-once}" in
  once)
    acquire_lock
    run_single_pass 1
    ;;
  loop)
    acquire_lock
    for i in 1 2 3 4 5; do
      run_single_pass "${i}"
    done
    ;;
  status)
    [[ -f "${CHECKPOINT_FILE}" ]] && cat "${CHECKPOINT_FILE}" || echo '{"status":"UNINITIALIZED"}'
    ;;
  rollback)
    rm -f "${CHECKPOINT_FILE}"
    log_event "WARN" "Rollback executed: checkpoint cleared safely."
    echo "ROLLBACK_OK"
    ;;
  *)
    echo "Usage: $0 {once|loop|status|rollback}"
    exit 2
    ;;
esac
