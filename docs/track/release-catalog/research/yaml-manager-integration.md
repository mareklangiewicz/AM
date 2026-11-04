# YAML acquisition and manager integration — November 4, 2026

[98](../issues/98-prepare-yaml-network-and-manager-integration.md), candidate
`7946f2167` on separate branch prep/yaml-consumer-integration, worktree
`/tmp/am-yaml-consumer-integration`. Based on prep/yaml-offline-publication at
7e62a68cc; neither candidate is merged into main. Detailed source interface and
verification live in candidate docs/track/release-catalog/design/yaml-manager-integration.md.

The candidate distributes four shared runtime modules using ordinary .am module
sync/cleanup. The reader/parser/policy are relocated, with compatibility entries
under tools; they are not independently maintained copies. The new shell helper
follows configured AMREPO, resolves one release-catalog pin and acquires only
apps.yaml plus the selected numeric repository document. It uses HTTPS-only,
no-config/no-proxy/no-redirect/no-credential curl, HTTP 200, existing transfer
limits/file-size rlimit, 128-byte ref and unchanged 2 MiB trial YAML/output caps.
It fully validates and privately spools; no Git/Python/jq on clients.

The five cohort recipes use an explicit format/policy binding in this source
candidate. Actual install and manager batch seams preserve literal URL identity,
REFRESH_ALWAYS, checksum repair, refusal-before-mutation and standalone installed
module/source bindings. The proposed distinct --accept-stale-release tuple binds
commit/repository/release/asset/effective observation; format-1 consent does not
apply. Installer arrays prevent option operands becoming app names. Unsupported
--force-latest exits nonzero before changes. Main's runtime source is unchanged.

Command-private update sessions share pin/apps/repository acquisition, including
stable/nightly Neovim's shared repository. Every selection revalidates bytes,
rechecks the current clock and applies its own acceptance. A failed transfer
latches acquisition; stale refusal does not authorize another app. Exact local
Git-backed fake HTTP confirms pin consistency across tip movement, configured
source override, missing-module refusal and actual sync/cleanup retention.

161 scoped checks pass: 11 new integration, 80 explicit format-1 lifecycle
compatibility, 15 format-1 batch, 17 format-1 shell consumer, eight prior portable
cohort/lifecycle, nine reader, nine enrollment and twelve staging. The complete
11-group run precedes the final stale diagnostic wording; targeted stale-install
forwarding/diagnostic passes afterward. ShellCheck, shell syntax, Python
compilation and whitespace pass. This is not a new capacity benchmark or full
network-client/platform matrix. Actual manager functions run with external AM
services stubbed; no live GitHub or binary transport occurs.

Initial failing runs were not accepted as evidence. Explicit module imports
prevent accidental discovery of unrelated test classes. Format-1 compatibility
fixtures remove the new cohort mode declarations; the new suite tests actual
format-2 declarations. A stale batch clock replacement was corrected so date +%s
returns integer seconds. A real installer refusal test exposed swallowed return
status; the new named-policy guard now exits nonzero through dispatch.

Remaining: source review; policies/migration for 470 enrolled recipe paths;
operational stale UI acceptance; exact consumer/source pins, already-installed
updater migration and complete transition/rollback. The separate code paths do
not make mixed-format publication safe. A single release-catalog ref cannot
switch while format-1 clients still require lookup.tsv/raw bodies. Empty prior
is not a migration bypass. No live acquisition, workflow activation/dispatch,
catalog publication, repin, installed change or yadm pointer work occurred.
Policy/capacity acceptance, maintainer promotion and natural-run gates stay open.
