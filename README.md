# Master-Run Command Center

Static operations console for the Grok Computer master-run pipeline.

## Modules
- Overview KPIs + module launcher
- Skills search/filter/CSV export (50 custom + 10 bundled)
- GitHub audit + draft PR
- Media lab (contact sheet, video, transcript)
- Research report preview + PDF/DOCX downloads
- TaskFlow telemetry + STATUS
- Client-side asset health matrix
- Deploy notes

## Local
```bash
python3 -m http.server 5173 --bind 0.0.0.0
```

## Vercel
Framework: Other · Root: this directory · no build command

## GitHub Pages
Publish this directory as Pages source (root or /docs).


## Swarm-23 Multi-Agent Framework
Strictly **23 unique session agents** linked from the continuity roster.

Teams:
1. **Deployment Orchestration** — live_application_session, live-testing, LIVE-DEPLOYMENT, debug-options, background sync
2. **Frontend Engineering** — UI shell, swarm view, assets, a11y, export
3. **Research** — public probes, citations, claim tags, scope guard
4. **Learning-Center** — onboarding, skills glossary, toolchain docs, runbooks, drills

Data files: `data/swarm-23.json`, `data/swarm-tasks.json`  
UI: https://master-run-command-center.vercel.app/#swarm

Each agent lists `capabilities_allowed` and `capabilities_forbidden` — the task bus will **block** work beyond the agent’s ceiling.
