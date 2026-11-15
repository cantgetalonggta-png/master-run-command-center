#!/usr/bin/env python3
"""Long-horizon continuous supervisor.

Runs real wall-clock duration (default 3600s) with chained workers.
Chat turns do not need to stay open — this is an OS process.
"""
from __future__ import annotations
import argparse, json, os, signal, socket, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/artifacts')
sys.path.insert(0, str(ROOT / 'backend' / 'supervisor'))
from workers import REGISTRY  # noqa

STATUS = ROOT / 'state' / 'supervisor_status.json'
CKPT = ROOT / 'state' / 'supervisor_checkpoint.json'
PIDF = ROOT / 'state' / 'supervisor.pid'
LOG = ROOT / 'audits' / 'supervisor.jsonl'
DEPLOY = ROOT / 'backend' / 'supervisor' / 'DEPLOYMENT.json'

def utc():
  return datetime.now(timezone.utc).isoformat()

def jwrite(path: Path, obj):
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp = path.with_suffix(path.suffix + f'.tmp{os.getpid()}')
  tmp.write_text(json.dumps(obj, indent=2))
  tmp.replace(path)

def log(event, **kw):
  LOG.parent.mkdir(parents=True, exist_ok=True)
  rec = {'ts': utc(), 'event': event, **kw}
  with LOG.open('a') as f:
    f.write(json.dumps(rec) + '\n')
  return rec

def stop_existing():
  if not PIDF.exists():
    return
  try:
    pid = int(PIDF.read_text().strip())
    os.kill(pid, signal.SIGTERM)
    time.sleep(0.5)
  except Exception:
    pass
  try:
    PIDF.unlink(missing_ok=True)
  except Exception:
    pass

def run(duration: int, tick: int):
  stop_existing()
  PIDF.write_text(str(os.getpid()))
  start = time.time()
  end = start + duration
  tick_i = 0
  results = []
  host = socket.gethostname()
  log('supervisor_start', duration=duration, tick=tick, host=host, pid=os.getpid())
  # ensure backend
  try:
    import urllib.request
    urllib.request.urlopen('http://127.0.0.1:8787/health', timeout=2)
  except Exception:
    import subprocess as sp
    sp.Popen(['python3', str(ROOT/'backend'/'secure_file_server.py')],
             stdout=open(ROOT/'logs'/'secure_backend.log','a'), stderr=sp.STDOUT,
             start_new_session=True)
    time.sleep(1)

  schedule = {1:1, 2:2, 3:3, 4:4, 5:5, 6:7, 7:10, 8:6, 10:2}
  while time.time() < end:
    tick_i += 1
    elapsed = int(time.time() - start)
    remaining = max(0, int(end - time.time()))
    tick_results = []
    for wid, every in schedule.items():
      if tick_i % every != 0:
        continue
      fn = REGISTRY.get(wid)
      if not fn:
        continue
      try:
        r = fn()
      except Exception as e:
        r = {'worker': f'W{wid}', 'ok': False, 'error': str(e)[:160]}
      tick_results.append(r)
      log('worker', tick=tick_i, **{k:v for k,v in r.items() if k!='rows'})
    ck = {
      'schema': 'gta.supervisor.checkpoint.v1',
      'ts': utc(),
      'host': host,
      'pid': os.getpid(),
      'tick': tick_i,
      'elapsed_seconds': elapsed,
      'remaining_seconds': remaining,
      'duration_seconds': duration,
      'status': 'RUNNING',
      'last_workers': [{k:r.get(k) for k in ('worker','ok','ok_count','deny_hits','action','error') if k in r} for r in tick_results],
    }
    jwrite(CKPT, ck)
    jwrite(STATUS, {
      **ck,
      'progress_pct': round(100.0 * elapsed / duration, 2),
      'target': '1h wall-clock continuous background',
      'deployment': str(DEPLOY),
    })
    results.append({'tick': tick_i, 'elapsed': elapsed})
    # sleep but wake often near end
    sleep_for = min(tick, max(1, remaining))
    time.sleep(sleep_for)

  final = {
    'schema': 'gta.supervisor.final.v1',
    'ts': utc(),
    'host': host,
    'pid': os.getpid(),
    'status': 'COMPLETED',
    'ticks': tick_i,
    'elapsed_seconds': int(time.time()-start),
    'duration_seconds': duration,
  }
  jwrite(CKPT, final)
  jwrite(STATUS, final)
  log('supervisor_complete', **final)
  try:
    PIDF.unlink(missing_ok=True)
  except Exception:
    pass
  print(json.dumps(final, indent=2))

def status():
  if STATUS.exists():
    print(STATUS.read_text())
  else:
    print(json.dumps({'status': 'NO_STATUS'}))
  if PIDF.exists():
    print('pidfile', PIDF.read_text().strip())

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('--duration', type=int, default=3600, help='wall-clock seconds (default 3600 = 1h)')
  ap.add_argument('--tick', type=int, default=30)
  ap.add_argument('--status', action='store_true')
  ap.add_argument('--stop', action='store_true')
  args = ap.parse_args()
  if args.status:
    return status()
  if args.stop:
    stop_existing()
    print(json.dumps({'stopped': True}))
    return
  if args.duration < 600:
    # enforce user min 10 minutes unless explicit tiny debug via env
    if os.environ.get('ALLOW_SHORT_SUPERVISOR') != '1':
      args.duration = 600
  run(args.duration, args.tick)

if __name__ == '__main__':
  main()
