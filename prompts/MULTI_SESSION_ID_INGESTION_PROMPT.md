# MULTI SESSION_ID INGESTION PROMPT
# Paste this entire block at the top of any message when you switch session / model / MCP context.
# Repeat as needed. Agent must merge into primary continuity without re-doing dead OAuth.

```
SESSION_MERGE_V3_INGEST
schema: gta.grok.future_session_merge.v3
primary_continuity_session: 211e2cba-1b23-5ce8-945a-d5e158b037a2
org: ECHO-EC69
aws_account: "166147842499"
aws_profile: mrcc
aws_region: us-east-1
console: https://166147842499.signin.aws.amazon.com/console

# --- FILL THESE WHEN SWITCHING ---
incoming_session_id: <PASTE_CURRENT_SESSION_ID_HERE>
incoming_model: <e.g. grok-4.5 / claude / gpt / local>
incoming_mcp_profile: <e.g. hf-mcp / aws-agent-toolkit / default>
merge_mode: automated-development
priority: high

# --- PERMANENT ROOTS (do not re-bootstrap from zero) ---
master_workspace: /workspace/work/MASTER_WORKSPACE
work_root: /workspace/work
artifacts_root: /workspace/artifacts
github_repo: cantgetalonggta-png/master-run-command-center
github_branch: main
hf_user: albedd
hf_space: albedd/orbit-command-swarm
hf_bucket: albedd/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-bucket
hf_collection: albedd/maximum-computational-effort-6af99ee5c9b6f21539d9973e
hf_meta_path: hf://buckets/albedd/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-bucket/mrcc-data/

# --- COGNITO / CHAT HUB (already live) ---
cognito_user_pool_id: us-east-1_yr5vuS7Kz
cognito_client_id: 1t94d90dg0lc6uiemlukj98p5u
cognito_domain: orbit-echo-ec69-1yr5vus7kz
cognito_hosted_ui: https://orbit-echo-ec69-1yr5vus7kz.auth.us-east-1.amazoncognito.com
cognito_identity_pool_id: us-east-1:30f5888a-2359-4e47-a2ff-5942bec8582f
test_user: test@echo-ec69.dev
# password only in secure session notes — do not commit

# --- 23 AGENTS (individuality_lock: true) ---
agents:
  DEP: [DEP-01 ORBIT-LEAD, DEP-02 PULSE-HEALTH, DEP-03 SHIP-GATE, DEP-04 SYNC-BUS, DEP-05 DEBUG-OPTS, DEP-06 TASK-DAEMON]
  FE:  [FE-01 UI-SHELL, FE-02 SWARM-VIEW, FE-03 KPI-BOARD, FE-04 ASSET-WIRE, FE-05 A11Y-UX, FE-06 EXPORT-IO]
  RS:  [RS-01 SCOUT-WEB, RS-02 SOURCE-MAP, RS-03 CLAIM-SPLIT, RS-04 REPORT-ARCH, RS-05 DIFF-WATCH, RS-06 SCOPE-GUARD]
  LC:  [LC-01 ONBOARD, LC-02 SKILL-LIB, LC-03 TOOLCHAIN, LC-04 RUNBOOK, LC-05 DRILL]

# --- AGENT INSTRUCTIONS ON PASTE ---
1. Read MASTER_WORKSPACE/session/session_status.json and handoff/RECONNECT.md first.
2. Treat primary_continuity_session as root caller; log incoming_session_id as a child merge edge.
3. Do NOT re-run aws login OAuth device flow if STS already works for profile mrcc.
4. Do NOT re-create Cognito pool/client/domain if IDs above still resolve.
5. Resume: frontend Hosted UI routes, multi-agent tooling, stress daemons, HF/GitHub sync.
6. Push durable state to GitHub main + HF mrcc-data/; secrets never committed.
7. If sandbox restarted: re-export AWS_PROFILE=mrcc; credentials live in ~/.aws/credentials.
8. Emit a one-line MERGE_ACK with both session IDs, then continue autonomous /build.

MERGE_ACK_TEMPLATE:
MERGE_ACK primary=211e2cba-1b23-5ce8-945a-d5e158b037a2 child=<incoming_session_id> model=<incoming_model> mcp=<incoming_mcp_profile> status=MERGED continue=/build
```

## Short paste variant (mobile)
```
SESSION_MERGE_V3_INGEST
primary: 211e2cba-1b23-5ce8-945a-d5e158b037a2
child: <SESSION_ID>
model: <MODEL>
mcp: <MCP>
org: ECHO-EC69
aws_profile: mrcc
repo: cantgetalonggta-png/master-run-command-center
master: /workspace/work/MASTER_WORKSPACE
action: read session_status.json + RECONNECT.md → MERGE_ACK → continue autonomous /build
```
