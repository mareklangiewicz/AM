# Consolidated YAML review and inactive workflow — November 4, 2026

[94](../issues/94-review-consolidated-yaml-candidate.md), candidate `ff2dc1499`
on `prep/yaml-offline-publication`. Implementation `deba0518e` plus trailing-blank
cleanup. The initial independent reviews pinned candidate `3bf90b411` against main
`dab1efd67`, with follow-up review of fixes/workflow. Main schema/glossary/ADRs are
authoritative; their exact bytes are now present on the prep branch too.

## Standards

No hard documented standards violation. Two heuristic duplication findings:

1. Local and remote YAML loaders independently implemented listing/layout/blob/
   reference validation, with divergent bounds/canonical checks. Consolidated
   in maintained yaml_publication.read_tree/tree_documents.
2. YAML and format-1 publishers duplicated index/tree/commit/ref construction;
   YAML omitted the original history gate. Both now call publication.publish_tree
   after their own format validation, sharing history and expected-old-ref checks.

Follow-up review confirmed both addressed, then found a legacy entry-point import
regression from relocation. Four historical scripts now explicitly bootstrap the
maintained module path. Direct adapter tests without PYTHONPATH and legacy import
checks pass. No remaining actionable standards finding in the workflow proposal.
These are agent reviews, not a substitute for maintainer line-by-line review.

## Spec

One P2 violation: candidate_tree rewrote every repository schema URL under a new
source revision, including unselected/unattempted files. Main format lines 100/121
require these unchanged; failure permits only current attempt metadata to change.
A two-source, cross-revision subset refresh reproduced the bug; old tests used
one revision and missed it.

Fixed: each repository keeps immutable schema provenance unless successfully
attempted. Failed sources retain schema/facts/observations; untouched files remain
byte-identical. The app document uses its current writer schema independently.
Canonical validation permits different valid per-document references. New tests
exercise successful, failed and aggregate-stop unattempted cross-revision cases;
verifier requires exact prior objects for untouched sources. Follow-up spec review
found no new blocker or scope creep. Retention/freshness and all-only explicit
reconciliation are unchanged.

Original totals: standards 0 hard violations/2 heuristic findings; spec 1 finding.
Follow-up standards added 1 compatibility regression. All findings are addressed.

## Consolidation and complete inactive proposal

Seven reusable runtime files/readers now live in tools/catalog-collector rather
than the prototype directory. Historical paths are relative symlinks; experiments
retain recorded evidence. Runtime imports no prototype modules. Only tests use
historical fixture builders; no new consumer worker/watchdog framework is added.

The complete manual proposal connects source/context/profile/scope preflight,
read-only exact-prior collection, normalized artifact upload, then separate
contents-write/actions-read publication. Artifact ID/digest come from trusted job
outputs. Publication requires successful collection, reacquires the same prior,
authenticates/verifies the artifact and uses the exact-parent lease. Input values
enter environment variables, never interpolated run commands. Failed/unattempted
requested sources fail collection, leaving artifacts for review without publishing.

The proposal remains outside .github/workflows and has no schedule, implicit
format-1 migration or automatic retry. The prior format-1 branch is refused, not
reinterpreted as bootstrap. The earlier bootstrap-only proposal is historical;
this complete proposal supersedes it for review. Publisher-only partial reruns
safely refuse an earlier-attempt artifact; use a complete new run. Lost push
acknowledgement/post-push report failure still needs remote-state inspection.

Runner provisioning must supply PyYAML and existing gh/git/transport dependencies;
no installation or hosted-runner capability was verified. Existing recorded action
pins are reused. Source review/promotion, policy/capacity acceptance, direct
consumer migration, transition/rollback and activation remain separate decisions.

## Validation and boundaries

83 collector/YAML/workflow/storage/delivery tests and 62 reader/normalization/
retention/default/adapter tests pass (145 total test executions). Three awk
publication trials pass six snapshots, nine pinned reads and fifteen rejected
candidates. Direct legacy adapter invocation passes six checks (overlapping the
adapter matrix), plus legacy import checks and runtime's absence of prototype
imports. Python compilation, shell syntax, proposal YAML parsing and final
whitespace checks pass. Final staged check caught inherited trailing blanks in
promoted modules; cleanup is included in the final candidate.

Five new workflow tests cover token-free preflight, invalid scope refusal before
remote/token handoff, collection outcome gates, trusted artifact-output handoff,
proposal job permissions and success dependencies. These are offline checks, not
GitHub execution or runner-capacity evidence.

[Full source review](https://github.com/mareklangiewicz/AM/blob/ff2dc1499/docs/track/release-catalog/design/yaml-consolidated-review.md),
[inactive complete workflow](https://github.com/mareklangiewicz/AM/blob/ff2dc1499/docs/track/release-catalog/design/catalog-yaml-publication.yml.proposed).
No active workflow edit, live API collection/catalog publication, schedule, daily
repin, installed consumer change or yadm pointer operation occurred.
