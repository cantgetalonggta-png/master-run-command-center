# Master-Run Command Center

Static operations console for the Grok Computer **future_session_merge v3** multi-agent swarm (23 agents).

**Live:** https://master-run-command-center.vercel.app/  
**Swarm:** https://master-run-command-center.vercel.app/#swarm  
**Learning:** https://master-run-command-center.vercel.app/#learning  
**Health:** https://master-run-command-center.vercel.app/api/health

## Modules
- Overview KPIs + module launcher
- Skills search/filter/CSV export (distilled server-skills + bundled tools)
- **Swarm-23** agent roster, capability ceilings, task bus
- **Learning-Center** onboarding, DEBUG-OPTS catalogue, runbooks
- GitHub audit + draft PR
- Media lab (contact sheet, video, transcript)
- Research report preview + PDF/DOCX downloads
- TaskFlow telemetry + STATUS
- Client-side asset health matrix
- Deploy notes + production headers

## Teams (23 agents)
1. Deployment Orchestration (DEP-01…06)
2. Frontend Engineering (FE-01…06)
3. Research (RS-01…06)
4. Learning-Center (LC-01…05)

## Local
```bash
npm run dev      # :5173
npm run audit    # html + json + headers
npm run health   # COMBINED_SKILLS_DEPLOY status
python3 scripts/verify_agents.py
```

## Vercel
Framework: Other · Root: repository root · Build: `echo static` · Output: `.`

## Security
Secrets always redacted. Individuality lock on every agent. No external app rule merge.
Primary continuity: `211e2cba-1b23-5ce8-945a-d5e158b037a2`
