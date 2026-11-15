# Deploy notes 2026-11-15

## Git
- main @ e3951c6 (framework + outputDirectory fix)
- https://github.com/cantgetalonggta-png/master-run-command-center

## Temporary Vercel (anonymous, ~59m)
- https://swift-ivory-x75emw2.tmp.now
- Claim: https://vercel.com/claim-deployment?code=9f53269f-b860-4347-8af3-6328e2e6e06c
- Note: anonymous temporary returned 403 on some edge probes; claim to promote.

## Production domain
- https://master-run-command-center.vercel.app/ still serving prior build (cache HIT) until Git integration rebuild or claim/link.
- Already has HSTS + nosniff + referrer. New CSP/X-Frame appear after next production build with this vercel.json.

## Local
- http://127.0.0.1:8080/ — 200, Deploy panel present

## Framework
- docs/IMPLEMENTATION_FRAMEWORK_FRONTEND_DEPLOYMENT.md
- npm run audit PASS
- verify_headers PASS
