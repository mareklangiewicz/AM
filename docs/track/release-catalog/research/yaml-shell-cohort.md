# Portable YAML cohort consumer — November 4, 2026

[97](../issues/97-prepare-portable-yaml-cohort-consumer.md), candidate `7e62a68cc`
on prep/yaml-offline-publication. Detailed interface, limits and commands live in
candidate `docs/track/release-catalog/design/yaml-shell-cohort.md`.

The shared validating reader adds a generic asset_facts projection. Separate
POSIX awk implements the five proposed Obsidian/Neovim policies without retaining
all asset facts. An offline shell wrapper acquires apps/repository YAML from an
exact local Git commit, with 2 MiB trial caps, private spooling and complete
validation. Its structured result preserves literal original download URLs.
Selected-record freshness and exact commit/repository/release/asset/observation
acceptance stay separate from command-private acquisition reuse. Future times
refuse; exactly 48 hours is fresh; a newer collection does not refresh old facts.
No Python/jq is used in the shell path. Local Git is a rehearsal facility, not a
new installed-client checkout prerequisite or production acquisition proposal.

A test-only builder copies the actual shared lifecycle and actual cohort recipes
to disposable roots, replacing only the raw-body selection handoff. All five
install/generated-updater bindings, URL identity, normal same-URL update skip,
nightly refresh, checksum repair, download failure preservation/retry and
pre-mutation stale refusal pass. A serial disposable batch scenario shares
acquired bytes but does not reuse Obsidian acceptance for a Neovim selection.
The real APP-MANAGER batch dispatcher/module sync installer is not exercised.

Eight shell/lifecycle groups pass. Fifteen saved-response comparisons cover
five recipes × mawk/gawk/BusyBox awk; large-ID/escaped-name/boundary tests run on
all three tools. Entry-point success/refusal/arena cleanup passes dash, bash and
BusyBox ash, not a full shell × awk matrix. The final added selected-override /
failed-collection / no-fresher-substitution case passes as a targeted rerun after
the full eight-group pass. Nine inherited reader groups plus seven selection,
seven policy and five workflow groups pass (28 additional). ShellCheck,
compilation and whitespace pass. Active modules/recipes/manager/workflows match
ff2dc1499. Measurements at older revisions remain historical.

Two test setup defects were corrected without loosening runtime validation:
install retry must use its external recipe because cleanup deletes installed
state; manually built normalized records must preserve canonical ID/field order.
No watchdog/worker/reservation prerequisites were introduced.

Next source preparation: production-compatible exact-pin raw-file acquisition,
configured AMREPO and module distribution, followed by actual manager/install/
update/repair/batch bindings in an isolated candidate. Operational stale UI,
policy/capacity acceptance, promotion, transition/rollback and activation remain
separate. No live API request, catalog publication, active workflow/module/recipe
change, repin, installed change or yadm pointer operation occurred.
