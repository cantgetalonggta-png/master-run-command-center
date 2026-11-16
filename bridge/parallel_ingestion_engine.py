#!/usr/bin/env python3
"""ParallelIngestionEngine — multi-process surface/registry ingestion."""
from __future__ import annotations
import concurrent.futures, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path

SURFACES = [
    "https://master-run-command-center.vercel.app/",
    "https://master-run-command-center.vercel.app/api/health",
    "https://fleet-ochre-auyuksg.tmp.now/",
    "https://strand-osint-mesh.vercel.app/",
    "https://multi-agent-skill-vault-git-gh-pages-echo-ec69.vercel.app/",
]

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ParallelIngestionEngine/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read(500).decode("utf-8", "replace")
            return {"url": url, "status": r.status, "ok": r.status == 200, "snippet_len": len(body)}
    except Exception as e:
        return {"url": url, "status": 0, "ok": False, "error": str(e)[:100]}

def run():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(fetch, SURFACES))
    out = {
        "schema": "gta.mrcc.parallel_ingestion.v1",
        "ts": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "ok": sum(1 for r in results if r.get("ok")),
        "total": len(results),
        "primary_session": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
    }
    Path("/workspace/artifacts/state/parallel_ingestion_latest.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out

if __name__ == "__main__":
    run()
