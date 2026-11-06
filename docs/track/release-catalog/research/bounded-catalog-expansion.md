# Bounded GitHub catalog expansion, November 6, 2026

Prepared scope is **131 apps / 128 sources**, compared with the published 54/52
baseline. All 77 additions have current first-party public numeric identities and
a public-release probe, bound to the recipe source that declared their upstream.
No catalog, workflow, source push or installed-host operation has occurred yet.

## Discovery and identity review

The current explicit-source scanner finds 6,732 candidate app identities across
7,192 architecture recipe files; 3,524 files need another source-binding review.
It recognizes an explicit literal catalog alias or an entire pinned upstream
template with a consistent release endpoint, never arbitrary GitHub links. This
is narrower than the initial 8,338-name URL-mention inventory. Neither inventory
means that every app is verified or published. The full hash-bound scan remains
under `/home/marek/Documents/Codex/am-catalog-expansion-20261106/scan.json`;
[summary](catalog-expansion-inventory.json) records its digest and baseline source.

Verification used 160 bounded first-party API requests, rechecked the complete
recipe hashes and bindings, required public/canonical metadata and a release
probe, then proposed enrollment separately. [Identity evidence](catalog-expansion-identities.json)
contains all 77 proposals. Six redirects remain review items: aegis,
aegis-vault-v7, agent-companion, agent-loom, agent-orchestrator and agent-player.
No redirected identity was silently promoted. Architectures sharing a recipe
identity collapse; distinct app identities sharing a source remain distinct.

GitHub's documented Actions GITHUB_TOKEN limit is 1,000 REST requests/hour per
repository, and list-releases supports at most 100 releases/page:
[rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api),
[release endpoint](https://docs.github.com/en/rest/releases/releases).
The maintained collector still fetches one 100-release page per attempted source.

## Collection and failure semantics

Enrollment is bounded at 128 sources, separately from the per-run request bound
of 52. Batch selection prioritizes never-attempted repositories, then oldest
attempt time, with numeric IDs breaking ties. Every-three-hour operation nominally
covers this cohort in three runs. This does not make failed observations fresh.
Prior data and exact observation times survive failed/unattempted refreshes.
New apps appear only after a successful source collection; a failed source never
manufactures a new successful observation or blocks unrelated successful sources.
Auth/rate failures stop the request loop; malformed inputs, transport failures and
file/response bounds have explicit failed attempts. Dropping retained sources
through batch enrollment refuses. No release reconciliation or selection changes.
Partial HTTP reads reserve their full allowance on failure, avoiding an accounting
hole where repeated mid-response failures could otherwise escape the shared byte
limit. The final focused batch checks exercise this without logging upstream diagnostics.

Strict all-or-nothing collection remains available for at most 52 sources;
production's prepared command explicitly opts into `--batch-size 52`. Reports
distinguish enrolled apps, actually published apps, attempts, failures and pending
identities. The previous response/time/file/history bounds remain unchanged.

Snapshot reads still validate each original byte stream with the distributed
reader, canonical encoding and cross-file references. The prior duplicate
validation pass through `candidate_tree` was removed; rejected app ordering,
missing references and wrong source paths still refuse. This reduces repeated
whole-snapshot work without changing the catalog schema or client.

[Fresh preflight](catalog-expansion-preflight.json) starts from published
`bcae3298f5ffa1461a74ecab42df1a6c41d68492` and records three remote-free
child commits. All 128 repositories succeed; previous app identities remain;
candidate `d5b2d3ad7c7e24ea556c4adbb166937bb5fc6b69` has 21.70 MB YAML,
largest file 1.16 MB. The three-run controller peaked at 641.67 MiB RSS under
the explicit 1 GiB process limit. Saved responses are local evidence, not browser
fixtures. [Offline whole-command replay](catalog-expansion-workflow-replay.json)
then measured the actual command reading the full retained snapshot and publishing
one bounded batch: 311.45 seconds / 175.35 MiB peak process RSS. This excludes
network and CI setup/fetch time. Records explicitly describe pending working-tree
preparation rather than claiming the code was already in the baseline commit.

The [unchanged prototype parser](catalog-expansion-parser.json) reads all app/source
documents in Node; the map is 3,594 bytes. No browser execution, DOM responsiveness,
mobile/accessibility check or final layout acceptance is implied.

## Recipe migrations and remaining scope

Four recipes pass exact upstream reconstruction, original/current saved selector
comparison, full digest-bound payload inspection and inert install/update/removal:
agent-smith, agent-switchboard, agent-teams-ai and agent-toolkit. They keep their
source identities while moving between enrollment lists. Only their 24 registry
data lines are added; every previous policy line remains. Agent Skills stays
unchanged because .DirIcon targets the upstream build host. See
[evidence](simple-five-evidence.json). Payloads are not executed; GUI compatibility
and live-host deployment are not claimed.

This is a measured intermediate cohort, not completion of “all GitHub-backed apps.”
Remaining work includes unsupported/redirect source attribution, further verified
cohorts, and a snapshot path that does not repeatedly materialize the whole tree
before qualifying thousands of sources. The unchanged reader's 1,024-file and
history bounds still matter. No greater enrollment or API/cost/freshness guarantee
is inferred from these 128-source measurements. [Publication plan](../issues/140-publish-bounded-catalog-expansion.md)
is concrete; source push/publication awaits Marek's call.

## Verification

The complete collector suite passes **146 tests**, including the 115-policy
legacy lifecycle group; reconstruction passes **44 tests**, including the four
new recipes through the shared three-awk and inert lifecycle gates. After the
final partial-read accounting change, all **five focused batch tests** pass.
The final main-report command path also passes its separate workflow publication
test. Python syntax, workflow structure/cron/arguments and diff whitespace checks
pass. Prior policy content is preserved byte-line for byte-line; only 24 new data
lines are added. Source preparation and test logs remain in the local evidence
directory; no live-host or remote publication operation occurred.
