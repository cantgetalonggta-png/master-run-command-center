# Permanent reconnection — ECHO-EC69 / MRCC

## Primary continuity session
`211e2cba-1b23-5ce8-945a-d5e158b037a2`

## AWS
- Profile: mrcc (credentials in ~/.aws/credentials — do not commit)
- Account: 166147842499
- Region: us-east-1
- Console: https://166147842499.signin.aws.amazon.com/console
- Cognito pool: us-east-1_yr5vuS7Kz
- Client: 1t94d90dg0lc6uiemlukj98p5u
- Domain: orbit-echo-ec69-1yr5vus7kz
- Test user: test@echo-ec69.dev (password set permanently; rotate for prod)

## Hugging Face
- User: albedd
- Space: albedd/orbit-command-swarm
- Collection: albedd/maximum-computational-effort-6af99ee5c9b6f21539d9973e
- Bucket: albedd/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-bucket

## GitHub
- Account: cantgetalonggta-png (gh auth active)

## Workspace roots
- Master: /workspace/work/MASTER_WORKSPACE
- Work: /workspace/work
- Artifacts: /workspace/artifacts

## Quick resume
```bash
export AWS_PROFILE=mrcc AWS_DEFAULT_REGION=us-east-1
aws sts get-caller-identity
hf auth whoami
cat /workspace/work/MASTER_WORKSPACE/session/session_status.json
```
