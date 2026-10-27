# Catalog source ownership correction

Ticket [29](../issues/29-respect-configured-catalog-repository.md), 2026-10-28.
Marek clarified the runtime requirement: the fork uses its own AMREPO, including
its additional packages. Upstream submission is optional later work, not a reason
to read upstream AM from this fork.

## Reproduction and cause

The new regression was run before the production change:

```
python3 -m unittest discover -s tools/catalog-collector -p test_shell_consumer.py -k test_configured_fork
```

It failed because the actual reader, with
`AMREPO=https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek`, requested
`https://api.github.com/repos/ivan-hc/AM/commits/heads/release-catalog` instead of
the fork's URL. Both ref and raw content roots had literal upstream owners. The
then-passing tests repeated that wrong ownership expectation. Direct request logs
identified the cause; no speculative hypothesis, live request or bisection was
needed. The historical fork-only reader substitution hid the runtime defect from
public validation rather than making the installed path correct.

## Fix and boundaries

The shared reader validates AMREPO as a supported raw-GitHub source and centrally
derives its owner/repository. It uses that same repository for optional ref
resolution and both commit-pinned reads. There is no built-in repository default
or fallback. Missing/empty, malformed/multiline, unsupported-host and local sources
refuse before curl; selected-catalog HTTP failure does not try upstream AM.

Installation escapes and embeds the current AMREPO in both recipe and generated
updater. They export it to the helper. Standalone execution retains that source
without a manager, checkout or inherited environment. Managed execution passes
its current AMREPO explicitly, including after newrepo selection, so it does not
silently keep an obsolete installation-time source. An explicitly empty source
refuses; only an unset variable uses the embedded installation-time default.
An unprepared recipe must receive AMREPO explicitly. Existing installed scripts
are not rewritten; installed migration remains separate work.

The publisher/workflow retain their correct fixed development-fork allowlists.
Pinning, integrity, observation timing, exact stale consent and the original app
binary URLs are unchanged. This fix adds no source collection or schedule and
makes no claim that all additional fork packages are already catalog-enrolled.
It corrects this catalog path; it is not an audit/removal of unrelated historical
upstream links or explicit developer-mode choices elsewhere in AM.

## Tracker reconciliation

The current spec, map, shell-consumer design and tool README describe configured
AMREPO ownership. Ticket 23's acceptance criteria are corrected. Tickets 23–28,
the fork validation plan/findings, and the upstream-readiness assessment have
prominent dated correction notices. Ticket 28's upstream-first recommendation is
withdrawn as the current continuation plan; its source-bound facts remain evidence
for an optional future upstream adaptation.

Historical JSON reports, Git candidates and evidence archives keep their original
bytes/hashes and source revisions. Editing them would falsify the measured record.
The updated Markdown records identify their historical scope and link to this
correction. Original upstream *application* release URLs remain valid; the defect
concerned the AM catalog owner, not those binary/metadata source identities.

## Verification

Regression coverage exercises the real reader, actual install-module dispatch and
generated updater, the actual newrepo-selection function and marked managed route,
and real temporary Git publication/module sync. App/download/network operations
are controlled fixtures. Source variants include another repository, source branch
names with slashes, missing/empty/local/multiline sources, HTTP refusal and shell
metacharacters. The privilege fixture clears AMREPO, matching sudo's normal loss
of this custom environment variable, and standalone tests remove it entirely.
No injected shell expression is executed, and source refusal emits no body or
app mutation. The multiline-source regression caught and corrected an initial
line-oriented validation gap before final verification.

Final test/lint results are recorded in ticket 29. Current client delta against
0a21fef3c is reader 102 + manager 53 + install module 32 + recipe 7 = **194 net
lines**, versus historical +179. This measurement does not prove simplification.
No live request, publication, workflow, host app installation/update, installed
migration or schedule occurred during this repair.
