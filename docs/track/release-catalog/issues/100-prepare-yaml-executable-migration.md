# Prepare explicit executable recipe migration and installed transition

Type: task
Status: resolved
Triage: ready-for-agent

Continue reviewed candidate 7946f2167 on an isolated source branch. Inspect the
actual selectors for the 356 enrolled am-utils executable paths, implement an
explicit shared structured-fact policy and bindings, and verify using saved
responses and adversarial/disposable lifecycle fixtures. Record selection
differences, missing fixture coverage and unchanged trial capacity limits.
Prepare a concrete already-installed updater transition/rollback contract with
exact source identity checks; do not activate it implicitly during update.

No live collection, workflow activation/dispatch, catalog publication, repin,
installed host changes, main runtime promotion or yadm pointer work. Policy and
capacity acceptance remain separate. Do not restart ticket 71 or rollout 69.

## Answer

Candidate 7cfd1218f on prep/yaml-executable-migration adds explicit structured
policies/bindings for all 356 enrolled executable paths. [Findings and evidence](../research/yaml-executable-migration.md).
All 356 saved selections and 1068 three-awk comparisons agree after fixing one
review-discovered URL eligibility mismatch. Six new migration groups and the
120-test compatibility/cohort/enrollment rerun pass. Both review axes completed;
the spec reviewer confirmed the correction, with no remaining findings identified.

Candidate designs specify the installed transition/source-hash/rollback contract
and rehearse explicit recipe replacement in disposable roots. They do not
implement a production migrator or accept dual publication. 114 AppImage paths,
installed migration implementation, policy/capacity/stale UI acceptance, exact
operational pins and complete publication transition remain. Source remains
isolated/unmerged; commits are local. No live or installed host changes.
