# Local browser verification

[Chinese instructions](runbook-local.md#本地网页和公开快照)

Run checks from `web/` after installing the locked dependencies and building the site:

```bash
npm ci
npm test
npm run build
npm run verify:static
npx playwright install chromium
PORT=54387 npm run e2e -- --workers=2 --output=/tmp/quant-market-research-browser
```

Choose an unused local port. `PORT` configures both the static preview server and Playwright URLs. The default is `4321`. Playwright always starts its own server and fails if the selected port is already occupied. It does not reuse another checkout's preview server. Keep other worktree servers running and select a different port.

Layout tests cover seven routes at each of five widths (`320`, `390`, `768`, `1280`, `1440`). Each route and width pair has its own test and the standard 30-second timeout. The checks retain one main heading, viewport fit, aligned shell gutters, and no page errors. Browser artifacts in the example stay outside the repository.
