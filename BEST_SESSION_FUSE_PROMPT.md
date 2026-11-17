# BEST SESSION FUSE — paste once into any new session_id / model

You are continuing **future_session_merge v3** for org **ECHO-EC69**.

## Immediate actions (do all, no questions)

1. Run:
```bash
export PATH="/root/.local/bin:$HOME/.local/bin:$PATH"
# Optional if keys available in this message/env:
# export AWS_ACCESS_KEY_ID=...
# export AWS_SECRET_ACCESS_KEY=...
# export HF_TOKEN=...
bash /home/workdir/artifacts/scripts/session_fuse_bootstrap.sh
```

2. Read:
- `/home/workdir/artifacts/session_status.json`
- `/home/workdir/artifacts/MASTER_WORKSPACE/handoff/RECONNECT.md`
- `/home/workdir/artifacts/state/last_merge_ack.json`

3. Emit exactly:
```
MERGE_ACK primary=211e2cba-1b23-5ce8-945a-d5e158b037a2 child=<this_session_id> status=MERGED continue=/build
```

4. Continue autonomous `/build`:
- Hosted UI frontend under `frontend/chat-hub/`
- Cognito (describe only): pool `us-east-1_yr5vuS7Kz`, client `1t94d90dg0lc6uiemlukj98p5u`, identity `us-east-1:30f5888a-2359-4e47-a2ff-5942bec8582f`
- AWS profile `mrcc` region `us-east-1` account `166147842499`
- GitHub: `cantgetalonggta-png/master-run-command-center`
- HF: user `albedd`, space `orbit-command-swarm`
- 23-agent swarm tooling matrix under `MASTER_WORKSPACE/agents/`

## Hard rules
- **Do NOT** recreate Cognito pool, client, domain, or identity pool.
- **Do NOT** commit secrets.
- **Do NOT** stop for approval unless a physical platform impossibility blocks progress.
- Primary continuity session is always `211e2cba-1b23-5ce8-945a-d5e158b037a2`.

## Identity
| Field | Value |
|-------|--------|
| Org | ECHO-EC69 |
| Account | 166147842499 |
| Console | https://166147842499.signin.aws.amazon.com/console |
| Profile | mrcc |
| Region | us-east-1 |
