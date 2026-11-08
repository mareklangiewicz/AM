# Main-owned browser — implementation checkpoint

November 8, 2026. Ticket 13 is **claimed, not resolved**. The local implementation
continues from `4162486856b512d5ca1186334c9ec76ea336db6a` and reuses the preserved
prototype at `/home/marek/code/shell/AM-catalog-pages`. That worktree/branch remains
untouched. No remote operation or installed-host change occurred.

## Available implementation

- `web/catalog/` owns the A/B/C source on main-marek, with A default. Preserves
  prototype layouts and native/Vim controls; adds 100-app directory pagination,
  global name search, explicitly source-scoped release/asset filtering and
  progressive retained-asset expansion. App identities sharing a source remain
  distinct, with explicit same-source links.
- Replaces the permissive format-2 prototype parser with the maintained strict
  `tools/catalog-contract/reader.mjs`, imported directly. Resolves target C once,
  caches by exact pin/path, loads source/provenance lazily, bounds streamed response
  bytes before decoding and rejects malformed UTF-8, unsupported contracts,
  path/kind errors and changed schema/recipe/rule/identity bindings. Keeps exact
  BigInt identities/byte sizes and decoded URL/media values, including leading `=`.
- Links carry C/app/view/release. App/view/release navigation uses native history;
  explicit Load latest creates a new pinned entry, and retries retain the chosen
  pin. Async source responses have navigation-generation guards. Back/Forward has
  route/focus/scroll restoration code; actual browser behavior is still unverified.
- Architecture-specific recipe availability, immutable review links and the four
  evidence classifications are presented separately from platform filename guesses.
  Unknown evidence stays unknown. Channel policy and actual installation asset
  selection are **not evaluated in this browser**; the page states that limitation
  and links to the pinned architecture-specific recipe. The accepted evidenced
  stable/nightly/AM-choice journey still needs verification and, if required,
  further implementation against available evidence. No support is inferred from
  enrollment, recipe classification or asset names.
- How it works explains credentials/quota, source/release observation, installation
  execution and binary authenticity. Dedicated health resolves S independently,
  shows the last reported run, counts/metrics/budgets, unknowns, retained detail,
  source outcomes when available, confirmation-pin differences and optional
  freshness/daily history. Different C/S pins are not assigned an unverified ancestry
  or latest-attempt claim. Unavailable status leaves catalog facts usable.
- Exact allowlisted artifact staging preserves relative source paths and refuses
  an existing destination. Six source files plus root redirect and `.nojekyll`;
  no tracker, fixture, preview interception, README or local paths are copied.
  Main-owned manual Pages workflow is prepared; deployment requires both explicit
  deploy input and an activation variable, neither used here. Existing public
  artifact and prototype source are preserved. The tooling README records the
  separately authorized repository-wide old-workflow disable needed at cutover;
  changing the main copy alone cannot disable the prototype branch's old workflow.

## Focused evidence

| Check | Actual result |
| --- | --- |
| `node tools/catalog-browser/test_catalog.mjs` | 10 checks pass on Node v26.12.1: lazy roots, pinned cache separation, same-pin retries/status isolation, path/kind/schema refusal, streamed size/UTF-8 refusal, exact integers/URLs/media values, recipe/rule/source evidence bindings, independent run/detail identity and unavailable detail. Synthetic wire fixtures only. |
| `node --check` on app, catalog and keyboard modules | Pass. Syntax evidence, not execution of DOM interactions. |
| Artifact staging into a disposable new directory | Exactly eight expected files; all six copied source files byte-identical. Second staging refuses without replacing existing output. No artifact uploaded. |
| Local fixture-preview HTTP smoke | Eight expected HTML/module/reader/fixture endpoints return 200; unrelated `/AGENTS.md` returns 404. HTML labels synthetic test data. Loopback socket/readback required approved sandbox escalation. This verifies serving/allowlisting, not browser fetch/DOM/CORS. |
| `git diff --check` | Pass. |
| Available UI tooling inventory | `cua.getState()` returns no apps and no browsers. No actual browser/device interaction was possible through connected UI tools. A Firefox executable exists; its presence is not evidence of an available connected/tested browser. |

The loopback preview runs with:

```
python3 tools/catalog-browser/preview.py --port 8765
```

Open `http://127.0.0.1:8765/web/catalog/?app=example`. It intercepts GitHub reads
and serves existing inert contract fixtures. These are synthetic identities/pins,
not a live or converted saved-cohort preview. Production source has no interception.

## Remaining ticket-13 gates

No real DOM/fetch/CORS, desktop Chromium/Firefox, mobile engine/device, keyboard/
focus, screen-reader, contrast/reflow/zoom or light/dark acceptance ran. No browser
performance target is qualified: render timings in diagnostics are instrumentation,
not a measurement report. The saved converted cohort, largest supported documents,
5,000-app synthetic directory and 4x CPU / 10 Mbit/s / 100 ms reference-profile
measurements remain required. Do not infer any of these from ten transport tests.

A short comprehension question was sent in this session; no answer or newcomer/
maintainer comprehension verdict is recorded here. That review remains outstanding.
The browser needs actual inspection and correction against the owning delivery
journeys before ticket 13 can resolve; ticket 14 remains blocked by 13.

Later authorized public HTTPS/CORS, deployed allowlist/readback, activation and
rollback remain tickets 14–15/rollout evidence. No AM push, acquisition, workflow
dispatch, source enrollment, public channel activation, Pages deployment, installed
host delivery or yadm pointer change occurred. Ticket-12 saved rehearsal is reused
unchanged; it was not rerun or upgraded into scale/browser qualification.
