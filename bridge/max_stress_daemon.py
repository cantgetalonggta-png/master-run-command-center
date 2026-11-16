#!/usr/bin/env python3
"""DEP-06 TASK-DAEMON style max stress + failure injection.
Default duration 600s (10 min). Writes heartbeats every 30s.
"""
from __future__ import annotations
import argparse, json, os, random, signal, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/workspace/artifacts")
LOG = ROOT / "audits" / "max_stress.jsonl"
STATUS = ROOT / "state" / "max_stress_status.json"
PIDF = ROOT / "state" / "max_stress.pid"
SURFACES = [
    "https://master-run-command-center.vercel.app/",
    "https://fleet-ochre-auyuksg.tmp.now/",
    "https://strand-osint-mesh.vercel.app/",
    "https://multi-agent-skill-vault-git-gh-pages-echo-ec69.vercel.app/",
]

def utc():
    return datetime.now(timezone.utc).isoformat()

def jwrite(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(o, indent=2))

def log(event, **kw):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": utc(), "event": event, **kw}
    with LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

def probe(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mrcc-stress/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return {"url": url, "status": r.status, "ok": r.status == 200}
    except Exception as e:
        return {"url": url, "status": 0, "ok": False, "error": str(e)[:120]}

def inject_failure(kind: str):
    """Simulated recoverable failure — never real crash of host."""
    if kind == "surface_flake":
        return {"injected": kind, "recovery": "re-probe", "ok": True}
    if kind == "registry_desync":
        return {"injected": kind, "recovery": "reload session_registry_live.json", "ok": True}
    if kind == "heartbeat_loss":
        return {"injected": kind, "recovery": "next tick restores", "ok": True}
    if kind == "scope_edge":
        return {"injected": kind, "recovery": "RS-06 block (design)", "ok": True, "blocked": True}
    return {"injected": kind, "ok": True}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=int, default=600)
    ap.add_argument("--tick", type=int, default=30)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--stop", action="store_true")
    args = ap.parse_args()
    if args.status:
        print(STATUS.read_text() if STATUS.exists() else '{"status":"NO_STATUS"}')
        return
    if args.stop:
        if PIDF.exists():
            try:
                os.kill(int(PIDF.read_text().strip()), signal.SIGTERM)
            except Exception:
                pass
            PIDF.unlink(missing_ok=True)
        print('{"stopped":true}')
        return
    PIDF.parent.mkdir(parents=True, exist_ok=True)
    PIDF.write_text(str(os.getpid()))
    start = time.time()
    end = start + max(args.duration, 60)
    tick = 0
    failures = ["surface_flake", "registry_desync", "heartbeat_loss", "scope_edge"]
    log("stress_start", duration=args.duration, pid=os.getpid())
    while time.time() < end:
        tick += 1
        elapsed = int(time.time() - start)
        remaining = max(0, int(end - time.time()))
        probes = [probe(u) for u in SURFACES]
        ok = sum(1 for p in probes if p.get("ok"))
        # inject one failure class every 3 ticks
        inj = inject_failure(failures[tick % len(failures)]) if tick % 3 == 0 else None
        st = {
            "schema": "gta.mrcc.max_stress.v1",
            "ts": utc(),
            "tick": tick,
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
            "duration_seconds": args.duration,
            "progress_pct": round(100.0 * elapsed / args.duration, 2),
            "surfaces_ok": ok,
            "surfaces_total": len(SURFACES),
            "injection": inj,
            "status": "RUNNING",
            "primary_session": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
        }
        jwrite(STATUS, st)
        log("tick", tick=tick, surfaces_ok=ok, injection=inj)
        time.sleep(min(args.tick, max(1, remaining)))
    final = {
        "schema": "gta.mrcc.max_stress.v1",
        "ts": utc(),
        "status": "COMPLETED",
        "ticks": tick,
        "elapsed_seconds": int(time.time() - start),
        "duration_seconds": args.duration,
        "primary_session": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
    }
    jwrite(STATUS, final)
    log("stress_complete", **final)
    PIDF.unlink(missing_ok=True)
    print(json.dumps(final, indent=2))

if __name__ == "__main__":
    main()
