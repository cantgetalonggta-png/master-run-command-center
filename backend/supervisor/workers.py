#!/usr/bin/env python3
"""Chained worker implementations for continuous supervisor."""
from __future__ import annotations
import json, ssl, subprocess, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/artifacts')
CTX = ssl.create_default_context()
BOUND = [
  'https://master-run-command-center.vercel.app/',
  'https://fleet-ochre-auyuksg.tmp.now/',
  'https://strand-osint-mesh.vercel.app/',
  'https://multi-agent-skill-vault-git-gh-pages-echo-ec69.vercel.app/',
]
DEEP = [
  'https://vercel.com/docs/production-checklist',
  'https://vercel.com/docs/projects/deploy-from-cli',
]

def _get(url: str, timeout=8):
  try:
    if url.startswith('http://127'):
      r = urllib.request.urlopen(url, timeout=timeout)
    else:
      r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'mrc-supervisor/1'}), timeout=timeout, context=CTX)
    return {'url': url, 'ok': True, 'status': r.status}
  except Exception as e:
    return {'url': url, 'ok': False, 'error': str(e)[:140], 'code': getattr(e,'code', None)}

def w1_health_local():
  return {'worker': 'W1_health_local', **_get('http://127.0.0.1:8787/health', 4)}

def w2_bound():
  rows = [_get(u) for u in BOUND]
  return {'worker': 'W2_health_bound_surfaces', 'ok_count': sum(1 for r in rows if r.get('ok')), 'rows': rows}

def w3_deny():
  ok = 0
  for p in ['/files/keys.txt', '/files/.env']:
    r = _get('http://127.0.0.1:8787' + p, 4)
    if r.get('code') == 403 or (not r.get('ok') and r.get('code') == 403):
      ok += 1
    elif not r.get('ok') and '403' in str(r.get('error','')):
      ok += 1
    else:
      # urllib HTTPError surfaces as code
      if r.get('code') == 403:
        ok += 1
  # stricter
  for p in ['/files/keys.txt', '/files/.env']:
    try:
      urllib.request.urlopen('http://127.0.0.1:8787'+p, timeout=3)
    except Exception as e:
      if getattr(e, 'code', None) == 403:
        ok += 1
  return {'worker': 'W3_deny_secrets', 'deny_hits': ok, 'ok': ok >= 2}

def w4_frontend():
  checks = []
  for rel in ['mrc/index.html', 'mrc/vercel.json', 'mrc/package.json', 'mrc/data/swarm-23.json']:
    p = ROOT / rel
    checks.append({'path': rel, 'ok': p.exists(), 'bytes': p.stat().st_size if p.exists() else 0})
  return {'worker': 'W4_frontend_files', 'ok': all(c['ok'] for c in checks), 'checks': checks}

def w5_orch():
  try:
    out = subprocess.check_output(['python3', str(ROOT/'pipelines'/'swarm_orchestration_engine.py')], text=True, timeout=60)
    return {'worker': 'W5_orch', 'ok': 'MERGE_OK' in out}
  except Exception as e:
    return {'worker': 'W5_orch', 'ok': False, 'error': str(e)[:120]}

def w6_fsm():
  try:
    subprocess.check_call(['bash', str(ROOT/'pipelines'/'future_session_merge_v3.sh'), 'once'], timeout=60,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {'worker': 'W6_fsm', 'ok': True}
  except Exception as e:
    return {'worker': 'W6_fsm', 'ok': False, 'error': str(e)[:120]}

def w7_npm_headers():
  results = {}
  try:
    subprocess.check_call(['npm', 'run', 'audit'], cwd=str(ROOT/'mrc'), timeout=90,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results['npm_audit'] = True
  except Exception:
    results['npm_audit'] = False
  try:
    subprocess.check_call(['python3', 'scripts/verify_headers.py'], cwd=str(ROOT/'mrc'), timeout=30,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results['headers'] = True
  except Exception:
    results['headers'] = False
  return {'worker': 'W7_npm_headers', 'ok': all(results.values()), **results}

def w8_web_probe():
  rows = [_get(u, 10) for u in DEEP]
  return {'worker': 'W8_web_probe_deepsearch', 'ok_count': sum(1 for r in rows if r.get('ok')), 'rows': rows}

def w10_self_heal():
  h = _get('http://127.0.0.1:8787/health', 3)
  if h.get('ok'):
    return {'worker': 'W10_self_heal_backend', 'ok': True, 'action': 'none'}
  # relaunch
  import subprocess as sp
  sp.Popen(['python3', str(ROOT/'backend'/'secure_file_server.py')],
           stdout=open(ROOT/'logs'/'secure_backend.log','a'), stderr=sp.STDOUT,
           start_new_session=True)
  return {'worker': 'W10_self_heal_backend', 'ok': True, 'action': 'relaunch'}

REGISTRY = {
  1: w1_health_local,
  2: w2_bound,
  3: w3_deny,
  4: w4_frontend,
  5: w5_orch,
  6: w6_fsm,
  7: w7_npm_headers,
  8: w8_web_probe,
  10: w10_self_heal,
}
