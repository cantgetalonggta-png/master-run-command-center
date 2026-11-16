#!/usr/bin/env python3
"""Production SessionRegistry — source of truth for 23-agent swarm.
Schema: gta.mrcc.session_registry.v1
Primary: 211e2cba-1b23-5ce8-945a-d5e158b037a2 (DEP-01 ORBIT-LEAD)
"""
from __future__ import annotations
import json, os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(os.environ.get("MRCC_ROOT", "/workspace/artifacts"))
REGISTRY_PATH = ROOT / "bridge" / "session_registry_live.json"
AUDIT_LOG = ROOT / "audits" / "session_registry.jsonl"

PRIMARY = "211e2cba-1b23-5ce8-945a-d5e158b037a2"

@dataclass
class SessionSpec:
    sessionId: str
    displayName: str
    modelIdentifier: str = "grok-4.5-high"
    reasoningEffort: Optional[str] = "xhigh"  # low|medium|high|xhigh|effort-100
    contextWindow: int = 256000
    supportedTools: List[str] = field(default_factory=list)
    supportsCustomFunctions: bool = True
    isTabUnlocked: bool = True
    team: str = ""
    callsign: str = ""
    code: str = ""
    individuality_lock: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SessionRegistry:
    def __init__(self):
        self.sessions: Dict[str, SessionSpec] = {}
        self._load()

    def _load(self):
        if REGISTRY_PATH.exists():
            try:
                data = json.loads(REGISTRY_PATH.read_text())
                for item in data.get("sessions", []):
                    spec = SessionSpec(**{k: v for k, v in item.items() if k in SessionSpec.__dataclass_fields__})
                    self.sessions[spec.sessionId] = spec
            except Exception:
                pass
        if PRIMARY not in self.sessions:
            self.register_session(SessionSpec(
                sessionId=PRIMARY,
                displayName="DEP-01 ORBIT-LEAD",
                code="DEP-01",
                callsign="ORBIT-LEAD",
                team="Deployment",
                reasoningEffort="effort-100",
                supportedTools=["bash", "web_search", "github", "vercel", "file", "delegate_to_session"],
            ))

    def save(self):
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "gta.mrcc.session_registry.v1",
            "primary_session": PRIMARY,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(self.sessions),
            "sessions": [s.to_dict() for s in self.sessions.values()],
        }
        REGISTRY_PATH.write_text(json.dumps(payload, indent=2))
        return payload

    def register_session(self, spec: SessionSpec):
        self.sessions[spec.sessionId] = spec
        self._audit("register", spec.sessionId)
        self.save()

    def get_session(self, session_id: str) -> Optional[SessionSpec]:
        return self.sessions.get(session_id)

    def set_tab_unlocked(self, session_id: str, unlocked: bool, debug_only: bool = True) -> bool:
        if debug_only and os.environ.get("MRCC_DEBUG", "1") != "1":
            return False
        spec = self.sessions.get(session_id)
        if not spec:
            return False
        if spec.isTabUnlocked == unlocked:
            return True
        spec.isTabUnlocked = unlocked
        self._audit("setTabUnlocked", session_id, unlocked=unlocked)
        self.save()
        return True

    def audit_all_sessions(self) -> str:
        report = []
        for spec in self.sessions.values():
            report.append({
                "session_id": spec.sessionId,
                "model": spec.modelIdentifier,
                "reasoning": spec.reasoningEffort or "fixed/none",
                "context_limit": spec.contextWindow,
                "custom_tools_allowed": spec.supportsCustomFunctions,
                "active_tools": spec.supportedTools,
                "ui_unlocked": spec.isTabUnlocked,
                "code": spec.code,
                "callsign": spec.callsign,
                "team": spec.team,
                "individuality_lock": spec.individuality_lock,
            })
        return json.dumps(report, indent=2)

    def _audit(self, event: str, session_id: str, **kw):
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, "session_id": session_id, **kw}
        with AUDIT_LOG.open("a") as f:
            f.write(json.dumps(rec) + "\n")

def bootstrap_from_registry_json(path: Path) -> SessionRegistry:
    reg = SessionRegistry()
    if not path.exists():
        return reg
    data = json.loads(path.read_text())
    for a in data.get("agents", []):
        sid = a.get("session_id") or a.get("sessionId")
        if not sid:
            continue
        reg.register_session(SessionSpec(
            sessionId=sid,
            displayName=f"{a.get('agent_code', a.get('code', ''))} {a.get('callsign', '')}".strip(),
            code=a.get("agent_code") or a.get("code", ""),
            callsign=a.get("callsign", ""),
            team=a.get("team", ""),
            reasoningEffort="xhigh",
            supportedTools=a.get("capabilities_allowed", [])[:20],
            individuality_lock=bool(a.get("individuality_lock", True)),
        ))
    reg.save()
    return reg

if __name__ == "__main__":
    src = ROOT / "bridge" / "BACKEND_REGISTRY_23.json"
    if not src.exists():
        src = ROOT / "mrc" / "data" / "BACKEND_REGISTRY_23.json"
    reg = bootstrap_from_registry_json(src)
    print(reg.audit_all_sessions())
    print("count", len(reg.sessions))
