# Backend Integration Contracts (Planning)

## Policy
- Values of secrets never stored in this repository or Drive merge docs.
- OAuth2/OIDC: PKCE, minimal scopes, redirect allowlist only.
- Agent capabilities_forbidden must not be overridden by task bus.

## Contract slots
1. GitHub REST/GraphQL — via connected tools / gh CLI
2. Google Drive — list/search/read/create folder/download
3. Vercel — deploy/logs via CLI or Git integration
4. Multi-URL health — scripts/COMBINED_SKILLS_DEPLOY.sh
5. TaskFlow bus — JSON + log append
6–10. Fleet / Strand / Skill Vault / Voice / Automations — URL or MCP when available

## OAuth2 sketch
- Flow: authorization code + PKCE
- Redirects: production + preview + localhost:5173
- Storage: BFF httpOnly cookies preferred; static SPA does not hold refresh tokens long-term

## Simulation
Frontend uses /data/*.json as mock backend. Real BFF is out of scope until Next/Vite + env secrets configured in Vercel UI.
