# Make catalog ownership follow AMREPO

Type: task
Status: resolved
Triage: ready-for-agent

## Scope and corrected requirement

Marek clarified that this fork must use its configured AMREPO, including its
additional packages, rather than read upstream AM's catalog. Fix reader ownership,
manager installation/update handoff and standalone updater persistence. Missing or
unsupported source configuration must refuse without upstream fallback. Preserve
pinning, freshness, stale consent, integrity and original app binary URLs.

Reconcile all tracker records that incorrectly made upstream AM ownership or
acceptance a prerequisite for this fork. Preserve historical results and archives
as historical evidence. No workflow dispatch, source collection, publication,
installed migration or host app execution is authorized by this repair.

## Answer

Fixed the hardcoded upstream owner. The shared helper derives catalog ownership
from validated AMREPO; this fork uses mareklangiewicz/AM. Manager installation
embeds the selected source in both recipe and standalone updater. Managed updates
pass current AMREPO explicitly, including real newrepo selection with a nonexported
variable. Missing, empty, unsupported/local or malformed source refuses before
network IO; failed selected-catalog transport never falls back to upstream AM.
Source embedding escapes shell metacharacters and survives sudo-style environment
clearing. No change to publisher allowlists, observation times or binary URLs.

[Reproduction, implementation and reconciliation findings](../research/catalog-source-correction-findings.md)
record the failing pre-fix command, actual handoff tests and all affected records.
Current spec/map/design/README and ticket 23's acceptance criteria are corrected;
tickets 23–28 and related historical plans/findings visibly identify superseded
ownership assumptions. Ticket 28's upstream-first frontier is withdrawn. Historical
JSON/archive bytes and hashes remain intact, with their source revisions.

Validation: **107 tests passed** with
`python3 -m unittest discover -s tools/catalog-collector -p 'test_*.py'`.
`bash -n` passed for APP-MANAGER/install.am and `sh -n` for reader/recipe.
ShellCheck passed for the reader and at warning severity for the recipe. Diff and
local Markdown link checks passed. Current source cost is +194 net client lines
against 0a21fef3c; historical +179 is superseded. No live catalog read, source collection,
workflow, publication, installed migration, host app operation or schedule ran.
