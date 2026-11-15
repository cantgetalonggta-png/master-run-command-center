#!/usr/bin/env bash
# COMBINED_SKILLS_DEPLOY.sh — idempotent health + seed + loop for future_session_merge
# Commands: once | loop | continue | finish | status
set -uo pipefail
ROOT="/workspace/artifacts/future_session_merge"
STATE="/tmp/monitors/state/combined_skills_deploy.json"
LOG="/workspace/artifacts/logs/combined_skills_deploy.log"
LOCK="/tmp/monitors/combined_skills_deploy.lock"
PIDF="/tmp/monitors/combined_skills_deploy.pid"
mkdir -p /tmp/monitors/state /workspace/artifacts/logs "$ROOT"

ts(){ date -u +%Y-%m-%dT%H:%M:%SZ; }
log(){ echo "$(ts) $*" | tee -a "$LOG"; }

write_state(){
  python3 - "$@" <<'PY'
import json,sys,os,time
from pathlib import Path
cmd=sys.argv[1] if len(sys.argv)>1 else "status"
state_path=Path("/tmp/monitors/state/combined_skills_deploy.json")
prev={}
if state_path.exists():
  try: prev=json.loads(state_path.read_text())
  except: prev={}
prev.update({
  "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "cmd": cmd,
  "pid": os.getpid(),
  "merge_dir": "/workspace/artifacts/future_session_merge",
  "schema": "gta.grok.future_session_merge.v3",
})
# health probes
import urllib.request, ssl
ctx=ssl.create_default_context()
urls=[
  "https://master-run-command-center.vercel.app/",
  "https://fleet-ochre-auyuksg.tmp.now/",
  "https://strand-osint-mesh.vercel.app/",
  "https://multi-agent-skill-vault-git-gh-pages-echo-ec69.vercel.app/",
  "http://127.0.0.1:8080/",
]
health=[]
for u in urls:
  try:
    r=urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"csd/1"}), timeout=8, context=ctx)
    health.append({"url":u,"status":r.status,"ok":True})
  except Exception as e:
    health.append({"url":u,"ok":False,"error":str(e)[:120]})
prev["health"]=health
prev["ok_count"]=sum(1 for h in health if h.get("ok"))
state_path.write_text(json.dumps(prev, indent=2))
print(json.dumps({"cmd":cmd,"ok_count":prev["ok_count"],"total":len(health)}, indent=2))
PY
}

seed(){
  log "SEED manifest + stack copies"
  test -f "$ROOT/MERGE_CHAIN.json" || { log "MISSING MERGE_CHAIN"; return 1; }
  test -f "$ROOT/stack/swarm-23.json" || { log "MISSING swarm"; return 1; }
  test -f "$ROOT/stack/BACKEND_REGISTRY_23.json" || { log "MISSING backend"; return 1; }
  # ensure fsm monitor
  if [[ ! -f /tmp/monitors/fsm_merge.pid ]] || [[ ! -d /proc/$(cat /tmp/monitors/fsm_merge.pid 2>/dev/null) ]]; then
    nohup bash /workspace/artifacts/deployment/fsm_background_task.sh fsm_merge 15 >> /workspace/artifacts/logs/fsm_merge.stdout 2>&1 &
    echo $! > /tmp/monitors/fsm_merge.pid
    log "restarted fsm_merge pid=$(cat /tmp/monitors/fsm_merge.pid)"
  fi
  write_state seed
  log "SEED_OK"
}

cmd_once(){
  seed
  write_state once
  log "ONCE complete"
}

cmd_loop(){
  if [[ -f "$LOCK" ]]; then
    old=$(cat "$LOCK" 2>/dev/null || true)
    if [[ -n "$old" && -d "/proc/$old" ]]; then
      log "loop already running pid=$old"
      exit 0
    fi
  fi
  seed
  (
    echo $$ > "$LOCK"
    echo $$ > "$PIDF"
    log "LOOP start interval=90s"
    while true; do
      if [[ -f /tmp/monitors/combined_skills_deploy.finish ]]; then
        log "FINISH flag seen — exiting loop"
        rm -f /tmp/monitors/combined_skills_deploy.finish
        write_state finished
        break
      fi
      write_state loop
      log "LOOP tick ok"
      sleep 90
    done
    rm -f "$LOCK"
  ) >> "$LOG" 2>&1 &
  echo $! > "$PIDF"
  log "LOOP background pid=$(cat $PIDF)"
}

cmd_continue(){
  rm -f /tmp/monitors/combined_skills_deploy.finish
  cmd_loop
}

cmd_finish(){
  touch /tmp/monitors/combined_skills_deploy.finish
  write_state finish_requested
  log "FINISH requested"
}

cmd_status(){
  write_state status
  cat "$STATE" 2>/dev/null || echo '{}'
  echo "---"
  tail -20 "$LOG" 2>/dev/null || true
}

case "${1:-status}" in
  once) cmd_once ;;
  loop) cmd_loop ;;
  continue) cmd_continue ;;
  finish) cmd_finish ;;
  status) cmd_status ;;
  *) echo "usage: $0 once|loop|continue|finish|status"; exit 2 ;;
esac
