# YAML executable source migration — November 4, 2026

Ticket [100](../issues/100-prepare-yaml-executable-migration.md). Candidate
prep/yaml-executable-migration at
7cfd1218f5be0d04e77d4d12d426ad9ae8cbd01c, based on reviewed 7946f2167;
worktree /tmp/am-yaml-executable-migration. Initial implementation d00582573,
followed by a reviewed URL-policy correction. Neither source candidate is merged
into main. No source push has been made for these new commits in this session.

## Source coverage and policy

All 356 enrolled am-utils executable paths (178 names on x86_64 and aarch64)
now declare format 2 and exact recipe bindings in the candidate. The shared
policy has an explicit trusted enrollment registry, reused by the acquisition
helper for refusal before HTTP; unknown names/architectures are not enrolled by
catalog data. The expected numeric repository is 1225768109. No new runtime
module/dependency or consumer supervision layer is added. Main runtime is unchanged.

Actual selector bodies were checked against their four expected shapes. The
previously repaired c++filt encoded component remains c%2B%2Bfilt; literal original
URLs survive selection. ld.bfd's dot is deliberately literal rather than an ERE
wildcard. Published-time/release-ID ordering, asset-name/ID ties, retained coverage
and structured asset-only matching remain proposed policy differences, not proven
legacy equivalence. See candidate design/yaml-executable-migration.md.

Together with the earlier five-recipe cohort, 361 of 475 enrolled paths now have
format-2 source bindings; 114 AppImage paths remain (one generic sqlitebrowser and
113 custom selectors). This does not count installed hosts or operational rollout.

## Saved evidence

The audit am_utils_cohort.py verifies the October 28 saved body's retained length
and SHA256, normalizes through merge_attempts, validates canonical YAML, then
compares each actual legacy selector against the independent Python reference
and three awk implementations. Saved body SHA256:
679d4c67e284d6ae3d752be9d27b08890edfda93894280e8492fdd53daf58dd8.
The body is 2,722,290 bytes; six releases/1750 assets normalize to a 583,974-byte
repository YAML file under the unchanged 2 MiB client trial cap. All 356 selected
URLs match; all 1068 mawk/GNU awk/BusyBox awk comparisons agree. The candidate's
am-utils-cohort-results.json records per-recipe hashes and selected IDs/URLs.
This is historical saved evidence, not a new live request or default-size/retained-
growth capacity acceptance.

## Review and failure accounting

Independent parallel code-review standards/spec axes reviewed d00582573 against
7946f2167. Standards found zero actionable findings. Spec found one P2 runtime
mismatch: matching a greedy URL prefix separately could skip an earlier valid
component when the URL contains repeated dated directories. A direct regression
failed on all three awk tools before the fix. Commit 7cfd1218f matches the full
expression with the literal component; the regression passes and the spec
reviewer confirmed the correction, with no remaining findings identified.

Initial disposable executable tests also exposed fixture problems: reusing an
installed basename across architecture cases made the real installer correctly
skip the second installation; accumulated fake curl logs exceeded the tiny ref
transfer's inherited file-size limit. Clean per-architecture roots and reset call
logs corrected the fixtures. The format-1 executable suite needed explicit
format-1 declarations, as existing AppImage compatibility fixtures already use.
A 120-test invocation begun before that fixture correction failed; its failures
are not passing evidence. The corrected executable suite independently passed
all six tests. Final reruns are recorded below.

## Installed transition proposal

Candidate design/yaml-installed-transition.md specifies an exact source-package
and installed-hash manifest, architecture/source/module bindings, refusal on
local drift, selected-release preflight before changing bindings, same-filesystem
atomic recipe replacement, unchanged managed updater launcher, backups/receipts,
and rollback limits. Its disposable rehearsal checks stale refusal, a same-URL
format-2 update preserving binary/version, and exact recipe-byte restoration.
It does not execute a restored format-1 updater, preserve privileged metadata,
exercise crash/receipt recovery or implement a production host migrator.

The document proposes a separately named format-2 publication ref while retaining
format-1 release-catalog data. This is not accepted dual publication. Current
candidate helpers still resolve release-catalog and are not operationally safe
for a mixed deployment. Exact new ref/source pins, support/retirement interval,
publication CAS/collector wiring, installed migration implementation and rollback
acceptance remain required. A single-ref switch cannot be justified by source
coverage alone.

No live acquisition, workflow activation/dispatch, catalog publication, repin,
installed host change or yadm pointer operation occurred. Policy/capacity/stale UI
acceptance and natural-run verification remain separate.

## Verification

At the final corrected source revision, the six new executable migration groups
pass in 89.866 seconds. The clean combined compatibility/cohort/enrollment run
passes all 120 tests in 274.227 seconds: six format-1 executable lifecycle,
two original utility-selector, 80 AppImage lifecycle, 15 batch, eight portable
cohort and nine enrollment checks. Seven Python policy and 11 manager integration
tests passed in the earlier 23-test run before the final utility-only expression
correction. The new repeated-directory regression passed after the correction
and is included in the six-group final run. The independent corrected executable
compatibility run also passed six tests in 24.674 seconds.

ShellCheck, shell syntax for the shared entry points and all 356 changed recipes,
Python compilation and whitespace checks pass. No new full-capacity, live-client
or network/platform cross-product test was run. The complete saved-body/three-awk
audit passed after the correction: all 356 saved selector comparisons and all
1068 three-awk comparisons agree. Regenerating the report left the source
worktree clean.
