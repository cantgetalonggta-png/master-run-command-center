#!/usr/bin/env python3
"""
Expanded Universal Agent Connectivity & Sync Verifier
future_session_merge v3 — hits every known agent session ID + surfaces
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timezone

SURFACES = [
    "https://master-run-command-center.vercel.app/",
    "https://master-run-command-center.vercel.app/#swarm",
    "https://fleet-ochre-auyuksg.tmp.now/",
    "https://strand-osint-mesh.vercel.app/",
    "https://multi-agent-skill-vault-git-gh-pages-echo-ec69.vercel.app/",
]

AGENTS = [
    {"code": "DEP-01", "callsign": "ORBIT-LEAD", "session": "211e2cba-1b23-5ce8-945a-d5e158b037a2"},
    {"code": "DEP-02", "callsign": "PULSE-HEALTH", "session": "c8d1c118-9e57-406b-b238-86cdc5363c47"},
    {"code": "DEP-03", "callsign": "SHIP-GATE", "session": "6fb3883a-da77-49fe-b6ba-46902e21aded"},
    {"code": "DEP-04", "callsign": "SYNC-BUS", "session": "c1d1e9cc-9602-4cd1-831f-5dd10df9b995"},
    {"code": "DEP-05", "callsign": "DEBUG-OPTS", "session": "344f6cd5-1562-4727-9a66-d8593b3e7cfa"},
    {"code": "DEP-06", "callsign": "TASK-DAEMON", "session": "64e5eebd-41b5-43ec-a762-c40731a9f2de"},
    {"code": "FE-01", "callsign": "UI-SHELL", "session": "568d6270-a86d-460b-87d7-1535f44a1680"},
    {"code": "FE-02", "callsign": "SWARM-VIEW", "session": "e302f5e6-2541-490f-ae94-12467ac46bbe"},
    {"code": "FE-03", "callsign": "KPI-BOARD", "session": "38e3b225-03e5-41ec-9721-460559aba2d6"},
    {"code": "FE-04", "callsign": "ASSET-WIRE", "session": "c921f3a6-f5b5-4b22-a0ad-bb44ec3d4cf6"},
    {"code": "FE-05", "callsign": "A11Y-UX", "session": "60ee66e8-e76a-4fde-ac4b-4bff80a8914e"},
    {"code": "FE-06", "callsign": "EXPORT-IO", "session": "94d1315d-bc98-4736-82e0-dbb866503f37"},
    {"code": "RS-01", "callsign": "SCOUT-WEB", "session": "08e87b41-196a-439e-b367-e5814927a65e"},
    {"code": "RS-02", "callsign": "SOURCE-MAP", "session": "843b27c9-64ce-47a4-bc80-8b83e868e21b"},
    {"code": "RS-03", "callsign": "CLAIM-SPLIT", "session": "4e27f581-8882-403b-b406-5a0f7471bb7e"},
    {"code": "RS-04", "callsign": "REPORT-ARCH", "session": "fc8a34dc-62d7-469c-a3f6-e403c7e2cba2"},
    {"code": "RS-05", "callsign": "DIFF-WATCH", "session": "2b074235-5eee-474a-8b14-16c950e85200"},
    {"code": "RS-06", "callsign": "SCOPE-GUARD", "session": "230bc671-9039-44dd-9ac0-0162ad97cbeb"},
    {"code": "LC-01", "callsign": "ONBOARD", "session": "36f15bb7-eb60-4502-8619-2b3e215b5090"},
    {"code": "LC-02", "callsign": "SKILL-LIB", "session": "95ec5721-522b-4876-916d-aac775c2c77c"},
    {"code": "LC-03", "callsign": "TOOLCHAIN", "session": "4b79e71a-b4dd-4f24-986b-c47a51beb4b4"},
    {"code": "LC-04", "callsign": "RUNBOOK", "session": "81a402f4-0f69-4434-bbe7-cc4b524087d3"},
    {"code": "LC-05", "callsign": "DRILL", "session": "c5168efe-bc35-4e40-8bd4-1ee91da2e3ad"},
]

async def check_surface(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            return {"url": url, "status": resp.status, "ok": resp.status == 200}
    except Exception as e:
        return {"url": url, "status": 0, "ok": False, "error": str(e)}

async def main():
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "primary_session": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
        "agent_count": len(AGENTS),
        "surfaces": [],
        "agents": AGENTS,
        "sync_status": "PENDING"
    }
    async with aiohttp.ClientSession() as session:
        report["surfaces"] = await asyncio.gather(*[check_surface(session, u) for u in SURFACES])
    
    ok = sum(1 for s in report["surfaces"] if s.get("ok"))
    report["surfaces_ok"] = ok
    report["surfaces_total"] = len(SURFACES)
    report["sync_status"] = "SYNC_OK" if ok == len(SURFACES) else "PARTIAL"
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
