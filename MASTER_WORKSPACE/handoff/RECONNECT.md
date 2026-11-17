# Permanent reconnection — ECHO-EC69 / MRCC

## Primary continuity session
`211e2cba-1b23-5ce8-945a-d5e158b037a2`

## Org / AWS
| Field | Value |
|-------|--------|
| Org | **ECHO-EC69** |
| Account | **166147842499** |
| Console | https://166147842499.signin.aws.amazon.com/console |
| Profile | **mrcc** |
| Region | **us-east-1** |

## Paths (this sandbox)
- Artifacts: `/home/workdir/artifacts`
- Master: `/home/workdir/artifacts/MASTER_WORKSPACE`
- Fuse script: `/home/workdir/artifacts/scripts/session_fuse_bootstrap.sh`

## Cognito (do not recreate)
- Pool: `us-east-1_yr5vuS7Kz`
- Client: `1t94d90dg0lc6uiemlukj98p5u`
- Domain: `orbit-echo-ec69-1yr5vus7kz`
- Identity pool: `us-east-1:30f5888a-2359-4e47-a2ff-5942bec8582f`

## Hugging Face
- User: albedd
- Space: albedd/orbit-command-swarm
- Bucket: albedd/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic-bucket

## GitHub
- cantgetalonggta-png/master-run-command-center

## Resume
```bash
export AWS_PROFILE=mrcc AWS_DEFAULT_REGION=us-east-1
export HF_TOKEN=...
bash /home/workdir/artifacts/scripts/session_fuse_bootstrap.sh
```
Secrets never committed.
