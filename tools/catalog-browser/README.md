# Catalog page

Source lives in `web/catalog/`. It reads the raw `catalog/` files of
`main-marek` from GitHub (`apps.yaml` first, then one `repositories/<name>.yaml`
per app opened, and `status/` for catalog health) and parses them with the
contract's reader, `tools/catalog-contract/parse.mjs` and `schema.mjs`. There
is no generated index and nothing names a catalog commit.

Reader and transport checks:

```
node tools/catalog-browser/test_catalog.mjs
```

## Staging and deployment

Stage the public artifact into a **new** directory (staging refuses an existing one):

```
python3 tools/catalog-browser/stage.py /tmp/am-catalog-public
```

The artifact is the allowlist in `stage.py` (the page, its stylesheet and
modules, `parse.mjs`, `schema.mjs`, `platforms.json`) at their source paths,
plus a root redirect keeping query and hash, and `.nojekyll`. `--review-data DIR`
also bundles hash-checked `catalog/` files the page reads instead of
`main-marek`, for reviewing a page against saved data; `delivery.mjs` is then
the one generated file.

`.github/workflows/catalog-pages.yml` builds, tests and deploys to
https://mareklangiewicz.pl/AM/: on a push to `browser-review`, or dispatched on
`main-marek` with `deploy=true`:

```
gh workflow run catalog-pages.yml --ref main-marek -f deploy=true
```

`tools/release/release.py plan` says whether the deployed `schema.mjs` matches
HEAD's, so a contract change is not left with an old page.

## Browser smoke suite

```
cd tools/catalog-browser
npm ci
npx playwright install chromium
npm run test:e2e
```

Nine journeys (`e2e/`) run in headless Chromium at desktop 1280×900 and mobile
390×844 against a staged artifact with small fixture `catalog/` files served
over intercepted HTTP: browse, search, releases, help and history in all three
views; directory layout; a source fetch failure and its retry; Git refs and file
contents; release links and Back/Forward; an obsolete failure not replacing a
newer selection; recipe labels, shared apps and catalog health; a never-collected
repository; and data older than 14 days. Screenshots and traces are kept on
failure; there are no pixel baselines or accessibility-score gates.

Against the public site after a deployment:

```
CATALOG_BASE_URL=https://mareklangiewicz.pl/AM CATALOG_APP=0x808 npm run test:e2e
```

Desktop Firefox, optional: `npx playwright install firefox` then
`CATALOG_FIREFOX=1 npm run test:e2e -- --project=firefox`. Mobile emulation is
not a physical-device or screen-reader check; Marek's steering (November 8,
2026) puts a pleasant practical UI first, WCAG advisory.
