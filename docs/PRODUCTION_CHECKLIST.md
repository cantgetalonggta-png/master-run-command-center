# Production Checklist — Master-Run Command Center (Vercel 2026 mapping)

## Security
- [x] CSP + HSTS + nosniff + frame deny + referrer + permissions-policy (vercel.json)
- [ ] Deployment Protection for sensitive previews (optional)
- [x] KEY NAMES ONLY policy; no secrets in git
- [x] X-XSS-Protection legacy header present

## Performance
- [x] System font stack
- [x] Cache-Control for /data and /media
- [ ] Lighthouse score baseline after next deploy
- [ ] Extract inline CSS/JS to tighten CSP (follow-up)

## Reliability
- [x] Health probes script
- [x] Instant Rollback documented
- [x] Git history for revert
- [x] status.md + taskflow.log

## Environments
- Local: npm run dev / python http.server
- Preview: Vercel branch deploys
- Production: main → Vercel production

## CLI
```
vercel link
vercel env pull .env.local   # values never committed
vercel deploy
vercel deploy --prod
```

## Framework
- Current: Other / static root
- Optional: Vite SPA rewrites; Next App Router later

See also: docs/IMPLEMENTATION_FRAMEWORK_FRONTEND_DEPLOYMENT.md
