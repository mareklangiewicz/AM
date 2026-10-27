# Review and repair the shell adoption slice

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Review the complete uncommitted slice against baseline 0a21fef3c and ticket 23.
Include new/untracked files. Apply the standards/spec review skill with separate
reviewers, then fix evidenced integration regressions and test actual entrypoints
in temporary roots before any live adoption. Do not expand to fleet migration,
new collection, publication, scheduling or host app execution.

## Review findings

Standards reviewer: no documented-standard breaches or actionable baseline smells.
Additional behavioral findings: interrupted-download retry deadlock and unrelated
launcher-update refusal. Spec reviewer: four P2 findings: those two regressions,
same-version checksum repair being bypassed, and manager installation mutating
previous app/launcher state before catalog acceptance. The latter requires tests
of the actual installation dispatch, beyond isolated recipe/patch harnesses.

## Standards

No documented-standard violations or actionable baseline smells were reported.
The reviewer additionally reproduced two behavior regressions: interrupted-download
retry failure and collateral refusal of launcher-only updates. CONTRIBUTING.md's
human ownership/review requirements apply before upstream submission; no upstream
submission is part of this task.

## Spec

Four P2 findings against ticket 23:

1. “Failure handling”: after a failed wget, the new foreground path skipped the
   old global tmp cleanup while the updater still used plain mkdir. A subsequent
   healthy retry could not run.
2. “Integrity and failure handling”: bypassing the old version deletion prevented
   a same-version binary with a recorded checksum failure from being downloaded
   again. It repeatedly reported no update and failed verification.
3. “No installer/update mutation before acceptance”: ordinary installation could
   run the old incomplete installation's remover, delete a broken launcher or
   create system launcher directories before reader/helper acceptance. An empty
   replacement-recipe response also entered that destructive path.
4. “Keep unrelated installer cleanup and later fleet migration out”: leading
   --launcher was treated as selecting catalog apps and blocked a separate
   launcher-only operation.

## Fixes and verification

The reviewed updater now clears only its own interrupted tmp directory after
catalog/body/filter acceptance and then attempts the binary download. A prior
checksum-failure marker selects a repair after that same preflight; the installed
version is not deleted first. The original managed binary-digest verification
remains afterward.

The foreground router preserves the launcher-only route, including debug flag
orders, and consumes the standard manager --debug flag before calling the reader.
Batch/mixed catalog app selection remains explicitly unsupported.

Installation now defers incomplete-app removal, broken launcher repair and system
launcher-directory creation into the reviewed recipe after preflight. It skips
legacy destructive interruption cleanup for that recipe. Real dispatch retains
and visibly refuses an incomplete app if its replacement recipe is unavailable;
legacy/variant cleanup requires a valid replacement source. Local incomplete
catalog script installation follows the same acceptance path.

Regression tests exercise failed download followed by refusal and healthy retry,
same-version corruption repair, both debug orders, actual launcher dispatch,
whole install.am dispatch/functions for database and local scripts, missing helper,
unavailable replacement source, broken-link/directory preservation, and successful
post-acceptance repair. Temporary app/Git roots and controlled transport/app
operations are used throughout. No host app execution, installed migration,
collection, publication, workflow or schedule occurred.

A focused spec recheck confirmed all four reported findings are addressed. Current
client source cost versus 0a21fef3c is reader 96 + manager 53 + install module 29 +
recipe 1 = **179 net added lines**, up from the initial 139. This review does not
establish a net simplification or live usability merely from source/test counts.

Final verification: **100 tests passed** with
`python3 -m unittest discover -s tools/catalog-collector -p 'test_*.py'`.
`bash -n` passed for APP-MANAGER/install.am; `sh -n` passed for the reader/recipe.
ShellCheck passed for the reader and at warning severity for the recipe. The two
pre-existing informational recipe findings remain unchanged. Diff and local
Markdown link checks passed. Work is saved locally; commit/push remain deferred
while Marek handles the separate Git metadata/yadm access issue.
