# Consolidated YAML candidate review and inactive workflow

Ticket 94 reviews fixed candidate `3bf90b41100df44ee3aec0a9ecf2b620756b720c`
against main `dab1efd67106e0fd734f095c5373c0e3fa19ba12` using
`git diff dab1efd67106e0fd734f095c5373c0e3fa19ba12...3bf90b41100df44ee3aec0a9ecf2b620756b720c`.
The 24 candidate commits include historical experiments; maintained acquisition,
retained facts, reader/writer, verification and publication paths were the focus.
Main's schema, glossary, ADRs and consolidated design are authoritative; those
exact document bytes are now present on the prep branch too.

## Standards

No hard documented standards violations were found. The independent standards
review found two heuristic duplication issues: local and remote YAML loaders had
divergent validation/bounds, and YAML/format-1 publishers duplicated commit/ref
construction with different history checks. Both are addressed: yaml_publication
owns bounded read_tree/tree_documents, and publication.publish_tree supplies one
local Git construction/expected-old-ref implementation after format validation.

A follow-up review found a relocation regression: importing a symlinked runtime
module from legacy experiments did not add the maintained directory to Python's
search path. Four legacy entry points now bootstrap it explicitly; direct adapter
tests without PYTHONPATH and import checks pass. Follow-up review found no other
actionable standards issue in yaml_workflow.py/proposal. These are agent reviews, not
a claim of maintainer line-by-line review or production approval.

## Spec

One P2 preservation defect was reproduced: refreshing a subset under a new source
revision changed schema URLs in unselected files. Main format lines 100/121 require
unselected/unattempted sources unchanged, and failure permits only current attempt
metadata to change. Constant-revision tests had hidden the problem.

Fixed by preserving per-document schema provenance. Successful attempted files
use current source schema; failed attempts retain prior schema/facts/observations;
unselected/unattempted documents remain byte-identical. Canonical validation
accepts different valid immutable schema references across files. The app-map
schema identifies its current writer independently. Cross-revision tests exercise
success, failure and aggregate-stop unattempted state; verifier enforces exact
prior objects for untouched sources. Follow-up spec review found no new blockers.
No retention/freshness/reconciliation policy changed.

Original totals: standards 0 hard violations and 2 duplication findings; spec 1
preservation finding. Follow-up standards added 1 compatibility regression. All
recorded findings are addressed; no finding implies operational approval.

## Maintained source organization

Seven runtime files moved into tools/catalog-collector: bounded.py, retention.py,
writer.py, attempt_adapter.py, yaml_publication.py, reader.sh and reader.awk.
Prototype paths are relative symlinks so historical offline scripts still use the
same implementation. Runtime imports no prototype modules; only test fixture
builders/legacy experiment entry points need the experiment directory. Historical
measurement artifacts stay in place and are not newly measured capacity evidence.
No consumer watchdog, worker or staging-reservation framework was introduced.

## Complete inactive manual workflow

catalog-yaml-publication.yml.proposed supersedes the bootstrap-only proposal for
review; both remain outside .github/workflows. The small yaml_workflow.py entry
point validates trusted source/context/manifest/profile and explicit scope JSON
before token use. Inputs enter environment variables, not interpolated shell code.

Collection has contents-read only, fetches exact prior or proves absence, collects
and uploads normalized YAML plus receipt. Its exit status fails on any failed or
unattempted requested source; the publisher's normal needs dependency requires
successful collection. Publication alone has contents-write/actions-read and
receives upload artifact ID/digest as trusted job outputs. It reacquires the same
prior, authenticates/verifies the artifact, constructs YAML-only history and uses
the fixed-ref exact-parent lease. A partial refresh bootstrap refuses incomplete
enrollment rather than manufacturing timestamps.

There is no schedule, implicit migration, arbitrary destination or automatic retry.
Only complete new runs are supported; rerunning a failed publisher alone safely
refuses an artifact named for the earlier attempt. Lost push acknowledgement or
post-push report-write failure remains ambiguous and needs remote-state inspection.

The runner must already provide Python3/PyYAML, gh, git and existing transport
dependencies. No provisioning install, new action pin or hosted capability was
verified. Existing recorded checkout/upload pins are reused. The existing
operational format-1 branch will be refused as a format-2 prior; empty prior is
not a migration bypass. Rollout must separately settle transition and rollback.

## Validation and remaining decisions

83 collector/YAML/workflow/storage/delivery tests pass. 62 reader, normalization,
retention/default and attempt-adapter tests pass. Publication trials on mawk, GNU
awk and BusyBox pass six snapshots, nine pinned reads and fifteen rejected
candidates. Direct legacy adapter invocation passes six checks; legacy entry
imports and runtime's absence of prototype imports pass. Python compilation,
shell syntax and whitespace checks pass. Five new workflow tests validate token-
free preflight, malformed scope refusal, collection outcomes/token handoff,
publication output handoff, proposal permissions and success gates. Workflow YAML
parses with BaseLoader (avoiding YAML 1.1's boolean interpretation of `on`).

Real GitHub artifact transfer, permissions/branch protection, runner provisioning,
full 49-source/100-release capacity and retained-growth policy remain unmeasured.
Maintainer source review/promotion, accepted operating budgets, consumer migration,
transition/rollback and explicit activation/natural-run acceptance remain separate.
No active workflow edit, live collection/catalog publication, repin, installed
consumer change, schedule or yadm pointer operation occurred.
