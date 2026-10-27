# Validate published shell reads and standalone distribution boundaries

> **2026-10-28 ownership correction:** [Ticket 29](29-respect-configured-catalog-repository.md) supersedes
> this record's fixed-upstream ownership assumption. This fork's catalog follows
> AMREPO and must not fall back to upstream AM. Upstream acceptance/publication
> is not a prerequisite for this fork. Results and archived bytes below retain
> their historical source/revision meaning; they do not define current policy.

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Continue ticket 23's actual implementation with an offline publication-to-shell
roundtrip using retained observations. Exercise the real artifact unpacking,
validation/recomputation, local bare-remote publication and commit-pinned shell
reader together, rather than trusting separate producer/reader fixture tests.
Cover ref movement, conditional repeat and exact stale consent across publication
commits. Check the actual module distribution inventory and standalone invocation.
Fix concrete integration defects if found, without introducing another runtime,
throwaway prototype, source collector run or installed-state migration.

Use only temporary Git repositories/app roots and transport stubs. The fork's
real Git metadata remains outside this session's writable roots; commit/push are
authorized but deferred while Marek handles yadm. No upstream repository write,
workflow dispatch, schedule or host installer/updater execution is in this task.

## Answer

The real producer/consumer roundtrip passes in temporary repositories:

- Rebuild a candidate from retained measured release bodies and fixture run
  context; ZIP/unpack it through the bounded artifact parser, then run the actual
  publisher validation, recomputation, Git object creation and normal push to a
  local bare repository. Only artifact download and network transport are stubbed.
- Publish a conditional 304 repeat using the first exact parent, verify changed
  lookup timestamps with unchanged body bytes, and move the branch between shell
  lookup and body reads. The actual shell reader resolves once and keeps the
  original commit for both pinned reads.
- Confirm stale acceptance binds the actual publication commit even across two
  publications with identical response bytes/hash. Reusing the prior commit's
  consent for the next commit refuses before fetching its body.
- Execute AM's actual module inventory, sync and obsolete-module cleanup with
  local source-read stubs. An obsolete installed reader is replaced, an initially
  missing reader is delivered, and an unrelated obsolete module is removed. The
  already generated standalone updater remains usable after sync from an
  unrelated working directory, using the managed helper without sourcing AM.

No production-code defect was exposed by these cross-boundary checks. Fixed stale
README instructions that still advertised the now-retired `--catalog-version`
option; documented the actual read-only shell invocation and upstream publication
prerequisite. Historical query evidence remains linked.

These are offline retained-body/fixture-context results, not a claim of live ZIP
provenance verification, public publication or upstream adoption. No new source
request, workflow, installed state, schedule or remote repository was changed.

Validation: **92 tests passed** with
`python3 -m unittest discover -s tools/catalog-collector -p 'test_*.py'`.
Local documentation links and `git diff --check` passed. The earlier ticket-23
syntax/ShellCheck results remain applicable: this continuation changed only tests
and documentation. Work remains uncommitted while Git metadata access is deferred.
