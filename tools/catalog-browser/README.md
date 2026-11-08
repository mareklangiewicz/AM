# Main-owned browser integration

Source lives in `web/catalog/`. The maintained strict reader is imported directly
from `tools/catalog-contract/`; there is no prototype parser or generated index.

Run focused contract/transport checks with:

```
node tools/catalog-browser/test_catalog.mjs
```

Run the explicitly labelled, loopback-only synthetic contract-fixture preview:

```
python3 tools/catalog-browser/preview.py --port 8765
```

Open `http://127.0.0.1:8765/web/catalog/?app=example`. This preview intercepts
GitHub reads and serves existing inert wire fixtures. It does not exercise real
public CORS, enrolled source coverage or browser performance qualification.
It exposes only browser modules/strict readers and the explicit fixture map.
The fixture identities, recipe links and commit IDs are synthetic examples.

Stage the public artifact into a **new** directory:

```
python3 tools/catalog-browser/stage.py /tmp/am-catalog-public
```

The artifact copies the explicit browser, stylesheet and strict-reader allowlist
at their original relative paths, plus a root redirect preserving query/hash and
`.nojekyll`. Source bytes are unchanged except the review delivery configuration. Tests, tracker material, fixtures, preview interception and this README
are excluded. Keep the previous deployed artifact for rollback; staging refuses
to replace any existing output directory.

## Published review iterations

Marek authorized publishing unfinished browser iterations on November 8, 2026.
Canonical browser source stays on local main-marek. Push that exact revision to
`browser-review` to deploy; only the browser workflow is registered on the default branch; scheduled collection
workflow and other default-branch source remain unchanged. The Pages environment allows this specific branch.
The old prototype deployment workflow is disabled repository-wide to prevent it
replacing the review site. Do not enable target collection channels or mutate the
default branch merely to publish a browser iteration.

```
git push origin HEAD:refs/heads/browser-review
```

The workflow builds a clearly labelled saved-observation review snapshot from
public baseline `cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f`, using the accepted
converter and strict whole-tree validation. Tied tag evidence is refused per source.
Recipe evidence and operational health are not fabricated. Static data lives only
in the Pages artifact, not a new catalog branch or source index. Its content ID
is explicitly a review snapshot identity, not a catalog Git commit.

Artifact staging additionally accepts `--review-data <prepared-directory>` and
copies only hash-checked canonical YAML paths. `delivery.mjs` is the one generated
configuration file; all other browser/reader source stays byte-identical. The
review builder and metadata manifest are excluded. The root redirect preserves
query/hash. Old review IDs refuse in a newer build rather than returning different
data at the old identity; Load latest selects the bundled review. Long-term Git
pin retention remains the real catalog channel's responsibility.

The saved data intentionally retains original observation ages. This is UI review,
not production freshness, scale, recipe-evidence or accessibility acceptance.
The normal catalog reader mode remains available with null delivery configuration;
main-branch deployment still has its separate explicit input/activation gate.

Deployment status, November 8: live at https://mareklangiewicz.pl/AM/ from
`bc48b66a95dd04b47e81258a66be8dc1e2b46733`. Build/deploy run
42496639918 succeeded with all 12 Chromium checks and 13 transport/contract checks.
Public readback matched seven source files and the delivery revision; six public
smoke checks passed across desktop/narrow Chromium and desktop Firefox. Ticket 13 retains scoped performance/device and
comprehension limits in `docs/track/catalog-system/implementation-13.md`.

## Small browser smoke suite

```
cd tools/catalog-browser
npm ci
npx playwright install chromium
npm run test:e2e
```

Six journeys (12 checks) run in headless Chromium at desktop 1280×900 and narrow 390×844:
browse/search/source filter → app/releases → help/Escape/focus → all A/B/C views
→ Back/theme; directory layout and hidden source controls; source network failure
and retry at the same URL. Native browser fetch and DOM execute against a staged
artifact with tiny inert fixtures; no preview fetch wrapper masks receiver errors.
Three additional controlled-channel journeys cover pinned release links, explicit latest, Back/Forward and missing identities/releases; obsolete source failures; and architecture-specific recipe evidence, shared stable/nightly identities and independent health confirmation/failure. They use the strict normal reader with intercepted HTTP fixture responses and real native fetch, without changing public channels.
Screenshots cover directory/detail/views/help/dark; traces are kept on failure.
There are no pixel-baseline updates or accessibility-score gates. CI runs these
checks before Pages publication and retains screenshots/traces for seven days.

To smoke-test the public site after publication (four checks run; eight local-only failure/channel-fixture cases are skipped):

```
CATALOG_BASE_URL=https://mareklangiewicz.pl/AM CATALOG_APP=0x808 npm run test:e2e
```

The headless test engine is independent of a browser extension or connected tab.
Mobile viewport emulation is not a physical-device or screen-reader qualification.
Marek's November 8 steering prioritizes a pleasant practical UI; WCAG is advisory.

For an optional local desktop Firefox check using the same six journeys:

```
npx playwright install firefox
CATALOG_FIREFOX=1 npm run test:e2e -- --project=firefox
```

The default Chromium CI gate stays small. Firefox is an additional recorded engine
check, not physical mobile or screen-reader evidence. Directory checks also exercise
Vim h/j/k/search, typing guards and native Tab/Shift-Tab.

Format-3 recipe evidence is now stored at `provenance/<source-label>.yaml`, derived
from the selected validated source path and loaded at the same snapshot pin. Each
partition must cover exactly its source's app/channel identities. The former
private global provenance path is rejected; regenerate old saved-review candidates
with the current builder. No document byte allowance was increased.
