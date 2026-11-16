# Chat Hub / LiveKitBridge — Production Ready Package
**Primary session:** 211e2cba-1b23-5ce8-945a-d5e158b037a2 (DEP-01 ORBIT-LEAD)
**Status:** PRODUCTION_READY
**Updated:** 2026-11-16

## Modules
1. session_registry.py — 23-agent SessionRegistry
2. livekit_bridge.py — sendAgentConfig + heartbeat
3. max_stress_daemon.py — long-running probes + failure injection
4. chat_hub_status.json — module completion
5. livekit_bridge_config.json — tool schemas + modes

## Call path
UI → SwarmViewModel → SwarmRepository → SessionRegistry.setTabUnlocked ↳ LiveKitBridge

## Run
```bash
python3 bridge/livekit_bridge.py
python3 bridge/max_stress_daemon.py --duration 900 --tick 20
```
