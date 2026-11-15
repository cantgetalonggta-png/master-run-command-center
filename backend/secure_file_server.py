#!/usr/bin/env python3
"""Secure local backend for the project folder.

Inventories every file. Serves only an allowlisted public tree.
Never returns bodies of secret-named files. Never logs file contents.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(os.environ.get("PROJECT_ROOT", "/workspace/artifacts")).resolve()
HOST = os.environ.get("SECURE_BIND", "127.0.0.1")
PORT = int(os.environ.get("SECURE_PORT", "8787"))
SKIP_PARTS = {".git", "node_modules", ".vercel", "__pycache__"}
SECRET_NAME = re.compile(
    r"(^\\.env|key|secret|token|passwd|password|credential|apikey|api[_\\s-]?key|auth)",
    re.I,
)
PUBLIC_PREFIXES = (
    "mrc/",
    "pipelines/",
    "future_session_merge/",
    "backend/",
    "state/",
    "archives/",
    "docs/",
)
PUBLIC_FILES = {
    "FUTURE_SESSION_MERGE_REPORT.md",
    "IMPLEMENTATION_FRAMEWORK_FRONTEND_DEPLOYMENT.md",
    "DEPLOY_NOTES_LATEST.md",
}

def is_skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)

def is_secret_name(rel: str) -> bool:
    name = Path(rel).name
    if name.startswith(".env"):
        return True
    if SECRET_NAME.search(name):
        return True
    low = name.lower()
    if low in {"env.txt", "env (2).txt", "second.env.txt", "openaikey.txt", "live_keys.txt", "all_keys.txt", "keys.txt", "new_keys.txt"}:
        return True
    return False

def is_public(rel: str) -> bool:
    if is_secret_name(rel):
        return False
    if rel in PUBLIC_FILES:
        return True
    if any(rel.startswith(p) for p in PUBLIC_PREFIXES):
        # never serve env-looking paths even under public prefixes
        if is_secret_name(rel):
            return False
        return True
    return False

def inventory() -> dict:
    files = []
    blocked = 0
    public = 0
    for p in ROOT.rglob("*"):
        if not p.is_file() or is_skipped(p):
            continue
        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        size = p.stat().st_size
        secret = is_secret_name(rel)
        pub = is_public(rel)
        item = {
            "path": rel,
            "bytes": size,
            "blocked": secret or not pub,
            "public": pub,
        }
        if pub and size <= 8_000_000:
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            item["sha256"] = h.hexdigest()
        files.append(item)
        if item["blocked"]:
            blocked += 1
        if pub:
            public += 1
    files.sort(key=lambda x: x["path"])
    return {
        "schema": "gta.secure_backend.inventory.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "policy": "KEY NAMES ONLY. Secret-named files are inventoried as blocked and never served.",
        "counts": {
            "files": len(files),
            "public": public,
            "blocked": blocked,
            "bytes": sum(i["bytes"] for i in files),
        },
        "files": files,
    }

INV = inventory()
INV_PATH = ROOT / "backend" / "inventory.json"
# persist without rewriting during request storms
INV_PATH.write_text(json.dumps({
    "schema": INV["schema"],
    "generated_at_utc": INV["generated_at_utc"],
    "counts": INV["counts"],
    "policy": INV["policy"],
    "blocked_names": [i["path"] for i in INV["files"] if i["blocked"] and is_secret_name(i["path"])],
    "public_count": INV["counts"]["public"],
}, indent=2))

class Handler(BaseHTTPRequestHandler):
    server_version = "SecureProjectBackend/1.0"

    def log_message(self, fmt, *args):
        # path only, never bodies
        try:
            sys_msg = "%s %s %s" % (self.address_string(), self.command, self.path.split("?")[0])
        except Exception:
            sys_msg = "request"
        print(sys_msg)

    def _headers(self, code: int, ctype: str, length: int | None = None, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if length is not None:
            self.send_header("Content-Length", str(length))
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()

    def _json(self, code: int, obj: dict):
        body = json.dumps(obj).encode()
        self._headers(code, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in ("/", "/health"):
            self._json(200, {
                "ok": True,
                "service": "secure-project-backend",
                "bind": f"{HOST}:{PORT}",
                "counts": INV["counts"],
                "policy": INV["policy"],
            })
            return
        if path == "/api/inventory":
            # summary only — not full path dump of every private pdf name if huge; include all paths but no content
            summary = {
                "schema": INV["schema"],
                "generated_at_utc": INV["generated_at_utc"],
                "counts": INV["counts"],
                "policy": INV["policy"],
                "files": [
                    {"path": i["path"], "bytes": i["bytes"], "public": i["public"], "blocked": i["blocked"]}
                    for i in INV["files"]
                ],
            }
            self._json(200, summary)
            return
        if path == "/api/blocked":
            self._json(200, {
                "policy": "names only; contents never returned",
                "blocked_secret_names": [i["path"] for i in INV["files"] if is_secret_name(i["path"])],
            })
            return
        if not path.startswith("/files/"):
            self._json(404, {"error": "not_found", "hint": "/health /api/inventory /api/blocked /files/<public-path>"})
            return
        rel = path[len("/files/"):].lstrip("/")
        rel = rel.replace("\\", "/")
        if ".." in rel.split("/") or rel.startswith("/"):
            self._json(403, {"error": "path_rejected"})
            return
        if not is_public(rel):
            self._json(403, {"error": "blocked", "path": rel, "reason": "not on public allowlist or secret-named"})
            return
        target = (ROOT / rel).resolve()
        if not str(target).startswith(str(ROOT)) or not target.is_file():
            self._json(404, {"error": "missing"})
            return
        data = target.read_bytes()
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self._headers(200, ctype, len(data))
        self.wfile.write(data)

def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"SECURE_BACKEND listening http://{HOST}:{PORT} files={INV['counts']['files']} public={INV['counts']['public']} blocked={INV['counts']['blocked']}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
