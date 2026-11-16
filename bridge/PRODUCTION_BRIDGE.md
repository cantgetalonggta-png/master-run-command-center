# Chat Hub / LiveKitBridge — Production Ready Package
**Primary session:** 211e2cba-1b23-5ce8-945a-d5e158b037a2 (DEP-01 ORBIT-LEAD)
**Schema:** gta.mrcc.chat_hub.v1 + livekit_bridge.v1 + session_registry.v1
**Status:** PRODUCTION_READY
**Updated:** 2026-11-16

## Modules
1. `session_registry.py` — 23-agent SessionRegistry with audit, setTabUnlocked, bootstrap from BACKEND_REGISTRY_23
2. `livekit_bridge.py` — sendAgentConfig (effort, modes, multi-step), heartbeat log
3. `max_stress_daemon.py` — long-running probes + failure injection (DEP-06 style)
4. `session_registry_live.json` — live 23-agent registry
5. `livekit_bridge_config.json` — production bridge config + tool schemas
6. `chat_hub_status.json` — module completion status

## Call path
UI → SwarmViewModel → SwarmRepository → SessionRegistry.setTabUnlocked ↳ LiveKitBridge

## Run
```bash
python3 bridge/session_registry.py
python3 bridge/livekit_bridge.py
python3 bridge/max_stress_daemon.py --duration 900 --tick 20
python3 bridge/max_stress_daemon.py --status
```

## Deploy
Push this package to `backend/bridge/` or `bridge/` on main. Live surface remains static SPA; bridge is the server-side / worker contract.
