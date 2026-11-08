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

## Quieter browsing — November 8, 2026

Marek requested shorter visible copy with longer explanations behind nearby “?”
buttons. Context help now covers search/platform inference, observation/history,
identity/recipe evidence, refresh, snapshots and health measurements. Short factual
labels and failed/unknown/partial states remain visible; exact contextual evidence
is retained in help or collapsed revision details. Native dialogs have named
triggers, Close/Escape handling and focus restoration; Vim shortcuts defer to the
context dialog. Syntax, the ten existing transport checks and whitespace pass.
Real-browser interaction/accessibility acceptance remains outstanding.

## Authorized public iteration route — November 8, 2026

Marek explicitly requested reviewing each iteration through the published live
version and accepted unfinished/unstable browser deployments. This supersedes
the browser deployment hold above, including future review iterations; it does
not authorize collector activation, enrollment or installed-host changes.

Publish exact local source to the `browser-review` branch, leaving remote
main-marek and its scheduled collection workflow unchanged. A Pages build embeds
a static, labelled conversion of the saved public 500-input cohort, using the
accepted converter and full contract validation, with conflict refusals visible.
No public v3 channel exists yet. Review content IDs are distinct from Git catalog
commits; static review data does not claim live observations or health.

The artifact allowlist adds delivery configuration and canonical hash-checked
review YAML. The workflow performs no source acquisition or catalog ref writes.
Eleven focused checks cover normal and review reader modes. Deployment/readback
receipt follows after completion; browser acceptance remains separate.

### Publication attempt and external blocker

Source `0291e278ac87f51aad7d78322f6e19feae384a22` was pushed to
`browser-review`. The local saved conversion passed full contract validation:
499 sources / 508 app identities; source 1245849062 refused for tied exact-tag
evidence as before. Staging contains 511 allowlisted files, with no tracker or
preview interception files. Eleven reader checks and syntax/whitespace pass.

The prior four live files were downloaded byte-for-byte with SHA-256 receipts to
`/home/marek/Documents/Codex/am-browser-review-20261108/last-good/`. Their hashes
match the November 6 public prototype receipt. The prepared local review artifact
is `/tmp/am-browser-public-review-20261108/`; its data is generated from the saved
public baseline, not new collection. The saved review metadata remains in
`/tmp/am-browser-review-data-20261108/review.json`.

Pages environment rule 65931830 allows exactly browser-review. The superseded
prototype workflow is disabled repository-wide. Remote main-marek advanced only
to `03582e8e44c42e11bbd5992bc23646532778cb69`, adding the browser workflow for
registration; all its other files, including the active collector workflow, remain
unchanged. That registration commit was merged into local main-marek. The planned
new collector is still local/review-branch code only; no collector dispatch ran.

**No new site deployed.** Push produced no review workflow run; after registration,
manual dispatch repeatedly returned HTTP 422: “Actions has been disabled for this
repository.” Workflow 411091894 is active; Actions permissions report enabled=true
and allowed_actions=all. Explicit workflow enable and reapplying the existing
repository enabled setting both succeeded but did not restore dispatch. No budget,
billing, token or broader allowed-action policy was changed.

GitHub's official [repository Actions settings guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
documents a separate GitHub-controlled disabled state that these settings cannot
clear and directs affected owners to Support. The exact cause for this account/repo
is not established here. Resolve that external restriction, then dispatch
`catalog-pages.yml` with ref browser-review and verify artifact/HTTPS readback.
The existing live prototype is unchanged; no new browser/CORS/deployment acceptance
is claimed. Future unfinished browser iteration publishing is already authorized.

### Public review deployed — November 8, 2026

Marek enabled Actions through GitHub's fork opt-in UI. He reported the generic
notice about avoiding wasted compute on forks. That points to the fork activation
gate rather than observed rate-limit enforcement; the earlier contradictory REST
state is not explained by the available evidence. No volume penalty is established.
The subsequent browser-review dispatch was accepted.

[Pages run 42476898945](https://github.com/mareklangiewicz/AM/actions/runs/42476898945)
completed build and deploy successfully from source
`d4dcb80f45f67b520de599e71a5b3b10d1a3c36a`. Live URL:
https://mareklangiewicz.pl/AM/ (redirects to web/catalog/ with query/hash retained).
The labelled review snapshot is `c8f35a86d93e286e05b5816b1712e8f3ebaeefc9`, with
508 identities / 499 sources and explicit refusal of source 1245849062.

Anonymous HTTPS readback checked 12 files: root, six byte-identical browser/reader
source files, generated delivery configuration, three catalog roots and source
0x808. Configuration matches the deployed revision; the four fetched YAML files
match hashes predicted from the checked local saved conversion with the deployed
schema/input revision. Receipt:
`/home/marek/Documents/Codex/am-browser-review-20261108/public-readback.json`.
This establishes deployment/source/data delivery, not DOM execution, actual browser
CORS, keyboard, mobile, accessibility or performance acceptance. Those remain open.

Only YAML release catalog and browser-review workflows are active; all previously
disabled unrelated workflows and the old prototype deployer remain disabled.
No collector dispatch, enrollment or installed-host change occurred.

### Browser fetch receiver correction — November 8, 2026

Marek reported `Failed to execute 'fetch' on 'Window': Illegal invocation` on the
published page. The injected fetch function was stored directly and invoked as
`this.fetcher(...)`, passing Catalog as its receiver. Browser fetch requires its
Window receiver; prior arrow-function transports and HTTP byte checks missed this.

A new receiver-sensitive transport test drives actual Catalog channel/document
reads. `node tools/catalog-browser/test_catalog.mjs` first reproduced the exact
reported TypeError (11 pass / 1 fail). Binding the injected/default transport to
globalThis fixes both paths (12 pass). No parser/domain behavior changed. The
receiver-specific reproduction isolates the cause; broader speculative hypotheses
and instrumentation were unnecessary. Connected UI inventory still has no browsers,
so this is a targeted regression test, not claimed real DOM acceptance.

The Pages trigger now excludes tooling README-only changes, preventing deployment
receipt commits from rebuilding an otherwise unchanged review snapshot. Browser
source, workflow, tests and build scripts still trigger review deployment.
