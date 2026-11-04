# Portable named-cohort consumer rehearsal

Ticket 97 continues the five proposed policies from [96](yaml-recipe-cohort.md).
This is offline preparation. Policies, operational byte budgets and stale CLI
remain proposals. No active consumer/module/recipe/workflow is changed.

## Reader and selection boundary

The shared reader adds generic `asset_facts FILE`. It emits one TSV row per
asset: release ID, asset ID, encoded effective observation, published_at, tag,
asset name and URL. String columns use the reader's validated scalar spelling
(including its allowed escapes), not general untrusted JSON. Full validation and
byte accounting finish in the existing private spool before any rows are returned.
Malformed trailing fields still produce no externally visible candidate bytes.
The projection does not select or rank. It preserves the reader's per-record
memory reuse rather than accumulating every asset in an awk map.

`tools/catalog-collector/yaml_cohort.awk` applies the named policies separately,
keeping only the best candidate. It compares decimal IDs by digit length/string,
not floating-point conversion. It decodes literal string facts without eval,
uses C-locale name ordering, and computes UTC Gregorian observation age in POSIX
awk. It refuses future observations and anything over 48 hours without the exact
selected-record waiver. Selection occurs before freshness; no fresh lower-priority
substitution. Failed recent collection does not replace a release's observation.

## Offline acquisition interface

```
sh tools/catalog-collector/yaml_cohort.sh LOCAL_GIT PIN ARCH/APP UTC_NOW [ACCEPT]
```

PIN is an exact 40-hex commit ID. The wrapper reads apps.yaml and the selected
repository YAML from that local Git commit, preflights Git object sizes and fully
validates each file. It retains the 2 MiB trial input/output caps and private
spooling. Output is six fixed lines: commit, repository ID, release ID, asset ID,
effective observed_at and original decoded asset URL. Numeric identities and
fixed timestamps make the first five lines unambiguous; validated URLs contain
no whitespace. Callers do not eval the result. No network fallback exists.

The rehearsal's ACCEPT spelling is the first five output lines joined with `:`.
It binds commit/repository/release/asset/observation exactly. This is an offline
adapter for the existing proposed acceptance tuple, not an approved replacement
for the operational --commit/stale interface. Unsupported lifecycle arguments
refuse, rather than silently treating format-1 consent as format-2 consent.

Optional AM_YAML_SESSION names a caller-owned private command-lifetime directory.
It caches immutable acquired YAML under the exact pin and binds its local Git
source path. Repeated selection validates cached bytes and repeats policy and
freshness checks. It never caches a successful acceptance. The caller removes
the command session; each helper invocation removes its own temporary arena on
success/refusal. This is serial command-local reuse, not a concurrent cache or
production network acquisition design.

The host-facing selection path is shell/awk/Git and ordinary utilities; Python
is only a test/publisher dependency. Git is available for this local rehearsal;
this is not a proposal to add a Git checkout dependency to installed AM clients.
Production raw-file exact-pin acquisition still needs preparation.

## Disposable lifecycle candidate

`tools/catalog-yaml-prototype/cohort_lifecycle.py` produces a temporary copy of
the real shared AppImage module, replacing only its raw-body selector handoff
with the structured shell result. It produces bound copies of actual cohort
recipes with local source pin, policy, helper and offline clock. It never writes
active source modules/recipes. Installed recipe copies and generated standalone
updaters retain those bindings. The original lifecycle body handles downloads,
URL version identity, REFRESH_ALWAYS, verification repair, temporary directories,
launchers and Obsidian desktop cleanup. Fake downloads create inert AppImages
only in disposable roots. No real binary is downloaded or executed.

The tests cover all five installs/generated updaters; normal same-URL update skip;
nightly same-URL refresh; checksum-triggered repair; failed-download preservation
and retry; and stale install/update refusal before cleanup, including an incomplete
install. A serial disposable batch scenario reuses acquisition bytes, accepts one
exact Obsidian stale selection and refuses Neovim without reusing that acceptance.
This does not run the real APP-MANAGER batch dispatcher or module sync installer.

## Evidence and remaining work

Eight shell/lifecycle test groups pass. The saved five-policy comparison runs on
mawk, gawk and BusyBox awk. Adversarial cases cover IDs above 2^53, escaped name
ordering, explicit tag refusal, selected observation overrides with a failed
collection, no fresher substitution, exact 48-hour boundary, future/invalid UTC,
wrong waiver, cached malformed suffix/oversize/wrong identity and pin movement.
Entry-point success/refusal and private-arena cleanup pass on dash, bash and
BusyBox ash (not every shell × awk cross product). Nine inherited reader groups,
seven selection-reference groups, seven policy groups and five workflow groups
also pass. ShellCheck, Python compilation and whitespace pass.

Initial harness failures were corrected: install retry must use its external
recipe because cleanup deletes installed state; handcrafted normalized maps must
list asset IDs in canonical order. These were test setup defects, not relaxed
validation or lifecycle fixes. No new watchdog, worker or reservation framework.

Next: prepare production-compatible exact-pin raw-file acquisition and helper
module distribution, then the real manager/install/update/repair/batch bindings
in an isolated source candidate. Preserve configured AMREPO and no fallback,
URL identity, failure-before-mutation and per-selected-record acceptance. Review
operational stale UI and exact transition/rollback separately. No policy/capacity
acceptance, candidate promotion, workflow activation, live collection/publication,
repin, installed change or yadm pointer operation occurred here.
