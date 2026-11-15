#!/usr/bin/env bash
# future_session_merge long-task background agent — idempotent, observable
set -uo pipefail
NAME="${1:-fsm_supervisor}"
STATE="/tmp/monitors/state/${NAME}.json"
LOG="/workspace/artifacts/logs/${NAME}.log"
LOCK="/tmp/monitors/${NAME}.lock"
INTERVAL="${2:-20}"
mkdir -p /tmp/monitors/state /workspace/artifacts/logs

ts(){ date -u +%Y-%m-%dT%H:%M:%SZ; }
if [[ -f "$LOCK" ]]; then
  old=$(cat "$LOCK" 2>/dev/null || true)
  if [[ -n "$old" && -d "/proc/$old" ]]; then
    echo "$(ts) already_running pid=$old" >> "$LOG"
    exit 0
  fi
fi
echo $$ > "$LOCK"
echo "$(ts) START $NAME" >> "$LOG"
while true; do
  free=$(df -BG /tmp 2>/dev/null | awk 'NR==2{print $4}' | tr -d G)
  fuse_ok=true
  echo probe > /workspace/artifacts/logs/.fuse_probe 2>/dev/null || fuse_ok=false
  weights=0; [[ -d /tmp/heretic_local ]] && weights=$(find /tmp/heretic_local -name '*.safetensors' 2>/dev/null | wc -l)
  printf '{"ts":"%s","agent":"%s","status":"TICK","tmp_free_gb":%s,"fuse_ok":%s,"weights_shards":%s,"merge_dir":"/workspace/artifacts/future_session_merge"}\n' \
    "$(ts)" "$NAME" "${free:-0}" "$fuse_ok" "$weights" > "$STATE"
  echo "$(ts) TICK free=${free}G fuse=$fuse_ok shards=$weights" >> "$LOG"
  sleep "$INTERVAL"
done
