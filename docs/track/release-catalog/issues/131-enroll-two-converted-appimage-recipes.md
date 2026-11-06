# Enroll the two converted AppImage recipes for collection

Type: task
Status: resolved
Triage: ready-for-agent

Marek's November 6 “continue” follows 130's completed local source conversion.
Continue with local collection enrollment of only x86_64/20x and x86_64/2fac.
Keep verified numeric identities and source-owned narrow selectors. Validate the
actual collection configuration, saved real-response normalization/retention,
YAML writer/reader/selection and disposable install/update lifecycle. Record
coverage/resource limits accurately: 128's saved responses use per_page=30,
whereas production requests per_page=100. No production completeness/capacity
claim follows from the smaller saved sample. Keep acquisition budgets unchanged.

Commit locally. No remote push, live publication/workflow dispatch, deployment,
real app execution, installed/recovery path changes or yadm pointer operations.
4nier-patrimonio stays outside scope. A push would activate the changed enrollment
on a later workflow run and requires Marek's separate decision.

## Answer

Added only `x86_64/20x` and `x86_64/2fac` to the local collection list, increasing
source enrollment from 21 recipes / 19 repositories to 23 / 21. Numeric identity,
canonical repository spelling, narrow patterns and launcher settings remain owned
by the converted declarations from 130. No selector/runtime/workflow code changed.
The 52-source limit, 16 MiB response / 96 MiB total / 300-second collection
budgets and 2 MiB per-repository YAML limit remain unchanged. An activated cycle
will attempt two additional numeric release-list requests.

[Offline replay measurements](../research/two-candidate-enrollment-replay.json)
retain exact saved response hashes: 20x's 30 releases / 569 assets normalize to
190644 YAML bytes; 2fac's four releases / 60 assets to 20810 bytes, using the
production schema URL pinned to base `c2beede263111db3d1eb1dce871719e6451e2db6`.
Both fit the existing per-repository limit. These are saved per_page=30 samples,
not live per_page=100 transport/capacity evidence or a fresh upstream observation.
The replay uses explicit page_size=30 and the saved next-page evidence: 20x's
history remains incomplete; 2fac's saved response has no next page. No evidence
was relabelled as a current production response or complete 20x observation.

New disposable publication/reader coverage starts from the former 21-app/19-source
baseline, adds the two normalized saved sources at an exact local parent,
validates YAML through the distributed reader, reloads the local Git snapshot,
and verifies both narrow URL winners with mawk, gawk and BusyBox awk. Existing
19 source documents and the old pinned app map remain unchanged. The existing
full configured collector test now covers all 23 apps/21 sources with synthetic
empty saved responses and checks refusal preserves the prior local publication.
Neither test publishes to a remote or executes a payload.

All 27 relevant tests pass: six publication/collection groups, three declaration/
selection groups, two source-compiler groups and 16 host lifecycle/cutover groups.
The host fixture now supplies exact-pattern inert asset names for both newly
enrolled apps; actual disposable manager installs, standalone updates and
maintenance apply include them. Prior ticket 130's real-metadata symlink and
20x-argument tests remain its recorded evidence. No full catalog/container suite
or independent review is claimed. Documentation links and whitespace checks pass.

Source enrollment is complete and locally committed. No remote push, live
collection/publication/dispatch, installed-host/recovery changes, deployment,
real app execution or yadm operation occurred. Production coverage remains the
previous 21/19 baseline until source push and a successful publication; future
per_page=100 acquisition can still refuse existing limits. Next step is Marek's
push decision (which makes the next workflow publication attempt the new sources),
then observing that publication before any client/host deployment.

## Publication follow-up

Marek authorized pushing all five pending source commits through `fa36ebb7e`,
then requested an immediate catalog run. [Run 42150558139](https://github.com/mareklangiewicz/AM/actions/runs/42150558139)
succeeded at that source, publishing `a547f48289475ed474de10a6389ce69c12c62060`.
Read back the exact-pin app map and both repository files with the distributed
reader: 23 app identities; 20x 100 releases / 1818 assets / 608940 YAML bytes,
2fac four releases / 60 assets / 20812 bytes. Both collection statuses are ok;
20x history is incomplete, 2fac reached end. Actual current selection returns the
same asset IDs 688278008 and 594778867 as the inspected payloads. This supplies
one live production-page capacity observation, not a future-growth guarantee.
No app was installed or launched. Shared-module review/deployment follows in 132.
