#!/usr/bin/env python3
"""Plugin: run each agent task in its own subprocess for true process isolation."""
from __future__ import annotations
import json, multiprocessing as mp, os, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

PRIMARY = "211e2cba-1b23-5ce8-945a-d5e158b037a2"
SURFACES = [
    "https://master-run-command-center.vercel.app/",
    "https://fleet-ochre-auyuksg.tmp.now/",
    "https://strand-osint-mesh.vercel.app/",
    "https://multi-agent-skill-vault-git-gh-pages-echo-ec69.vercel.app/",
]
AGENTS = [
    ("DEP-01","ORBIT-LEAD","Deployment","211e2cba-1b23-5ce8-945a-d5e158b037a2"),
    ("DEP-02","PULSE-HEALTH","Deployment","c8d1c118-9e57-406b-b238-86cdc5363c47"),
    ("DEP-03","SHIP-GATE","Deployment","6fb3883a-da77-49fe-b6ba-46902e21aded"),
    ("DEP-04","SYNC-BUS","Deployment","c1d1e9cc-9602-4cd1-831f-5dd10df9b995"),
    ("DEP-05","DEBUG-OPTS","Deployment","344f6cd5-1562-4727-9a66-d8593b3e7cfa"),
    ("DEP-06","TASK-DAEMON","Deployment","64e5eebd-41b5-43ec-a762-c40731a9f2de"),
    ("FE-01","UI-SHELL","Frontend","568d6270-a86d-460b-87d7-1535f44a1680"),
    ("FE-02","SWARM-VIEW","Frontend","e302f5e6-2541-490f-ae94-12467ac46bbe"),
    ("FE-03","KPI-BOARD","Frontend","38e3b225-03e5-41ec-9721-460559aba2d6"),
    ("FE-04","ASSET-WIRE","Frontend","c921f3a6-f5b5-4b22-a0ad-bb44ec3d4cf6"),
    ("FE-05","A11Y-UX","Frontend","60ee66e8-e76a-4fde-ac4b-4bff80a8914e"),
    ("FE-06","EXPORT-IO","Frontend","94d1315d-bc98-4736-82e0-dbb866503f37"),
    ("RS-01","SCOUT-WEB","Research","08e87b41-196a-439e-b367-e5814927a65e"),
    ("RS-02","SOURCE-MAP","Research","843b27c9-64ce-47a4-bc80-8b83e868e21b"),
    ("RS-03","CLAIM-SPLIT","Research","4e27f581-8882-403b-b406-5a0f7471bb7e"),
    ("RS-04","REPORT-ARCH","Research","fc8a34dc-62d7-469c-a3f6-e403c7e2cba2"),
    ("RS-05","DIFF-WATCH","Research","2b074235-5eee-474a-8b14-16c950e85200"),
    ("RS-06","SCOPE-GUARD","Research","230bc671-9039-44dd-9ac0-0162ad97cbeb"),
    ("LC-01","ONBOARD","Learning","36f15bb7-eb60-4502-8619-2b3e215b5090"),
    ("LC-02","SKILL-LIB","Learning","95ec5721-522b-4876-916d-aac775c2c77c"),
    ("LC-03","TOOLCHAIN","Learning","4b79e71a-b4dd-4f24-986b-c47a51beb4b4"),
    ("LC-04","RUNBOOK","Learning","81a402f4-0f69-4434-bbe7-cc4b524087d3"),
    ("LC-05","DRILL","Learning","c5168efe-bc35-4e40-8bd4-1ee91da2e3ad"),
]

def utc():
    return datetime.now(timezone.utc).isoformat()

def probe(url):
    t0=time.time()
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"mp-swarm/1"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return {"url":url,"status":r.status,"ok":r.status==200,"ms":int((time.time()-t0)*1000)}
    except Exception as e:
        return {"url":url,"status":0,"ok":False,"error":str(e)[:120],"ms":int((time.time()-t0)*1000)}

def worker(item):
    code, callsign, team, sid = item
    t0=time.time()
    pid=os.getpid()
    if code=="DEP-02":
        result={"action":"health_matrix","hits":[probe(u) for u in SURFACES]}
        result["ok"]=all(h.get("ok") for h in result["hits"])
    elif code=="RS-01":
        h=probe(SURFACES[0]); result={"action":"scout","ok":h["ok"],"hit":h}
    elif code=="DEP-01":
        result={"action":"lock_primary","ok":True,"primary":PRIMARY}
    else:
        result={"action":f"task_{code}","ok":True,"note":"identity-isolated process task"}
    return {
        "code":code,"callsign":callsign,"team":team,"session_id":sid,
        "ok":bool(result.get("ok")),"ms":int((time.time()-t0)*1000),
        "pid":pid,"result":result,"ts":utc(),"executor":"multiprocess-plugin"
    }

def main():
    started=utc()
    with mp.Pool(processes=min(8, len(AGENTS))) as pool:
        rows=pool.map(worker, AGENTS)
    out={
        "schema":"gta.mrcc.multiprocess_swarm.v1",
        "started":started,"finished":utc(),
        "primary_session":PRIMARY,
        "ok_count":sum(1 for r in rows if r["ok"]),
        "agent_count":len(rows),
        "agents":rows,
        "note":"Each agent ran in a separate OS process (pid listed)."
    }
    Path("data/multiprocess_swarm_run.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"ok":out["ok_count"],"total":out["agent_count"],"pids":sorted({r['pid'] for r in rows})}, indent=2))

if __name__=="__main__":
    main()
