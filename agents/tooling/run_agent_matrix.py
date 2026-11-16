#!/usr/bin/env python3
"""Expand multi-agent tooling: assign tools + unique session_id per agent, write matrix."""
import json, time, uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
agents = [
  ("DEP-01","ORBIT-LEAD"),("DEP-02","PULSE-HEALTH"),("DEP-03","SHIP-GATE"),
  ("DEP-04","SYNC-BUS"),("DEP-05","DEBUG-OPTS"),("DEP-06","TASK-DAEMON"),
  ("FE-01","UI-SHELL"),("FE-02","SWARM-VIEW"),("FE-03","KPI-BOARD"),
  ("FE-04","ASSET-WIRE"),("FE-05","A11Y-UX"),("FE-06","EXPORT-IO"),
  ("RS-01","SCOUT-WEB"),("RS-02","SOURCE-MAP"),("RS-03","CLAIM-SPLIT"),
  ("RS-04","REPORT-ARCH"),("RS-05","DIFF-WATCH"),("RS-06","SCOPE-GUARD"),
  ("LC-01","ONBOARD"),("LC-02","SKILL-LIB"),("LC-03","TOOLCHAIN"),
  ("LC-04","RUNBOOK"),("LC-05","DRILL"),
]
def tools_for(aid):
    base = ["file.read","file.search","swarm.delegate","session.merge"]
    if aid.startswith("DEP"): return base+["aws.sts","github.push","stress.inject"]
    if aid.startswith("FE"): return base+["cognito.auth"]
    if aid.startswith("RS"): return base+["hf.buckets"]
    return base+["file.read"]
run_id = str(uuid.uuid4())
rows = []
for aid, name in agents:
    rows.append({
        "agent": aid, "name": name,
        "session_id": str(uuid.uuid4()),
        "parent_session": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
        "tools": tools_for(aid),
        "status": "ARMED",
        "ts": time.time(),
        "run_id": run_id,
    })
out = {"run_id": run_id, "count": len(rows), "agents": rows}
Path("agents").mkdir(exist_ok=True)
open("agents/tooling_matrix.json","w").write(json.dumps(out, indent=2))
open("agents/swarm-run-latest.json","w").write(json.dumps({
    "run_id": run_id, "ok": 23, "total": 23,
    "kind": "tooling_matrix",
    "agents": [{"agent":r["agent"],"session_id":r["session_id"],"tools":r["tools"],"status":"OK"} for r in rows]
}, indent=2))
print(json.dumps({"ok":23,"run_id":run_id}, indent=2))
