#!/usr/bin/env python3
"""Verify vercel.json security headers against production checklist."""
import json
from pathlib import Path
v = json.loads(Path("vercel.json").read_text())
required = {
    "X-Content-Type-Options", "Referrer-Policy", "X-Frame-Options",
    "Content-Security-Policy", "Strict-Transport-Security"
}
found = set()
for block in v.get("headers", []):
    for h in block.get("headers", []):
        found.add(h["key"])
missing = required - found
print("headers present:", sorted(found))
print("missing required:", sorted(missing) if missing else "NONE — PASS")
assert not missing, "missing security headers"
print("verify_headers.py: PASS")
