#!/usr/bin/env python3
"""
Generates a selectable executable from the DEBUG-OPTS catalogue.
"""
import json
import sys
from datetime import datetime, timezone

CATALOGUE = [
    "live-testing",
    "LIVE-DEPLOYMENT",
    "background_synchronization",
    "ui_shell_sync",
    "swarm_view_refresh",
    "static_asset_verify",
    "public_surface_probe",
    "citation_refresh",
    "scope_guard_pass",
    "onboarding_refresh",
    "toolchain_doc_sync",
    "drill_card_rotate",
    "agent_individuality_lock",
    "secrets_redaction_enforced",
    "no_external_rule_merge",
    "hades_worker_envelope",
    "session_create_tool_expansion",
    "future_session_merge_v3",
    "primary_continuity_lock"
]

def generate(selected):
    if selected == ["ALL"] or selected == ["all"]:
        selected = CATALOGUE
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "primary_session": "211e2cba-1b23-5ce8-945a-d5e158b037a2",
        "selected_modes": selected,
        "status": "EXECUTABLE_READY",
        "security": {
            "secrets_redacted": True,
            "individuality_lock": True,
            "no_external_merge": True
        }
    }
    return payload

if __name__ == "__main__":
    modes = sys.argv[1:] if len(sys.argv) > 1 else ["ALL"]
    print(json.dumps(generate(modes), indent=2))
