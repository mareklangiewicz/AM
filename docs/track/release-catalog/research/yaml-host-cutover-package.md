# Host inventory and consolidated cutover package — November 4, 2026

Ticket 103. Main runtime is unchanged. Isolated consolidated source branch:
`prep/yaml-cutover-package`, worktree `/tmp/am-yaml-cutover-package`.
Complete clean candidate with final evidence/tracker records:
`ee89ef3bd42aed9d5613650b15c976823f73f281`.

## Exact source and package

Consolidation merge `58e4c67178de47fabe943fc879b160d60d5dd5cf` combines main's
canonical records at 83af4473f8ba77825562acb4bac1a38c70cfaf8c with candidate
5d410b1a5801a8bfbd75e69195c8a98977de7033. Three tracking-document conflicts use
main's authoritative versions. The consolidation has no runtime/code/workflow
byte difference against 5d410b1a5 (`git diff 5d410b1a5 58e4c6717 -- APP-MANAGER
modules tools .github` is empty). All inherited YAML collector, reader, policies,
475 source bindings and installed recipe transaction tooling are together.

New package/namespace code: ee9dbbc70, followed by review fixes bbfc63fad.
**Frozen package source:** `bbfc63fad0c59a7cfb4098abe8cb5ece1a35107e`.
**Legacy source used to reproduce installed recipes:**
`83af4473f8ba77825562acb4bac1a38c70cfaf8c`.

Local private package:
`/home/marek/Documents/Codex/2026-11-04/am-yaml-cutover-bbfc63fad`.
Its 69 payload files total 149,121,297 bytes, including the complete exact-source
Git archive, source manager/all modules, before-images of installed manager,
modules/updaters/recipes/version files, inventory and three bound replacements.
Installed binaries are hashed, not backed up. Preserve this directory separately
from disposable worktrees. Package manifest SHA-256:
`33d0fb8dc9e30d7cb8fcf5ffd4790a25acb4f88c2e4698dd35c01fa16a534f15`.

`yaml_cutover_package.py verify` successfully rechecks this package. The manifest
is an explicitly trusted local review input; internal hashes are not remote
package authentication. The recorded manifest hash freezes its review identity.
Publication/selection pins are null and apply_ready=false. No production-migrator
plan is fabricated without exact accepted live selected records.

## Installed inventory and the scope correction

[Inventory](yaml-host-cutover-20261104/inventory.json) covers explicitly selected
`/opt`, manager `/opt/am/APP-MANAGER`, `/opt/am/modules`, x86_64, account AppMan
configuration and AM source/mode probes. Manager/updaters were not executed.
71 file entries cover 1,013,715,046 logical bytes; binary hashes stream in 1 MiB
chunks. No directory symlinks were skipped. This is a current local snapshot,
not a supported-client census across other hosts or unconfigured roots.

No configured AppMan root, active newrepo-on, betatester or appman-mode file was
present in the probed account locations. Manager entrypoint `/usr/local/bin/am`
resolves to `/opt/am/APP-MANAGER`; no appman entrypoint was found on current PATH.

- **Three enrolled managed clients:** nvim, nvim-nightly and obsidian. Exact
  installed legacy recipes reproduce from the full legacy source with literal
  existing bindings. Exact generated updater bytes match. Package replacements
  preserve directories, package kind/default, alias and refresh behavior while
  embedding format 2, the named policy and exact source AMREPO. They await
  publication/selection, module delivery and explicit application.
- **One unenrolled managed format-1 client:** sunshine. Its existing recipe is
  outside the YAML enrollment and is explicitly retained unchanged.
- **17 unmarked legacy updaters:** appimagetool, appimageupdatetool, btop, emmylua,
  fzf, kitty, lazygit, logseq-app-db-nightly, logseq-app-og, neovide,
  neovide-nightly, rclone, rclone-ui, satty, yt-dlp, zellij and zmx. No direct
  catalog references were detected by the static scan; they are not enrolled by
  matching app names. Adapters/reviewed reinstalls remain separate.

**475/475 was complete only within the selected 49-repository enrollment.** The
frozen source contains **1,462 shared recipe paths: 475 format 2 and 987 still
format 1**. That excludes arbitrary unmarked recipes. A single-ref switch or
claim of complete installed/fork migration would therefore be unjustified even
on this no-other-users fork.

## Concrete publication proposal

Candidate YAML client resolution, remote prior loading and exact-CAS publication
now consistently use fixed `refs/heads/release-catalog-yaml-v2`. Format-1 client
and publisher continue to use fixed `refs/heads/release-catalog`. The shared
prior helper defaults to format 1 and permits only those two explicit refs.
Offline separate-ref bootstrap/refresh, exact-parent refusal/races and preservation
of an existing format-1 ref pass. No remote refs were inspected or created.
Manual YAML workflow remains a `.proposed` file outside .github/workflows;
active workflow bytes are unchanged.

This implements the separate-ref option locally so it can be reviewed; it does
not assert acceptance of live dual publication, operating capacity or retirement.
The existing format-1 publication and helpers remain necessary for Sunshine and
the 987 source recipes. The 17 legacy standalone updaters are a separate adoption
scope, not evidence that they currently require format-1 catalog data.

## Verification and independent review

At ee9dbbc70, these unchanged-by-review namespace/delivery suites passed:

```
PYTHONPATH=tools/catalog-yaml-prototype:tools/catalog-collector python3 -m unittest test_yaml_publication_delivery test_yaml_workflow test_yaml_delivery -v
```

21 tests passed in 49.410 s. The later combined 28-test run (also including the
then-seven package groups) passed in 86.894 s. No live transport occurred.

At bbfc63fad, final package and unchanged-format-1 regression command:

```
PYTHONPATH=tools/catalog-yaml-prototype:tools/catalog-collector python3 -m unittest test_yaml_cutover_package test_delivery test_shell_delivery -v
```

All 16 tests passed in 65.379 s: nine package groups and seven format-1 delivery/
shell roundtrip groups. Tests cover pinned source bytes, reproducibility from
identical inventory, bindings and shell syntax, package tamper/file-set/link
refusal, installed/hash/configuration/module/updater drift, same app in two roots,
and symlink-manager refusal. The actual package also built and verified against
the captured host inventory without installed writes.

The combined manager/migration command at ee9dbbc70:

```
PYTHONPATH=tools/catalog-yaml-prototype:tools/catalog-collector python3 -m unittest test_yaml_manager_integration test_yaml_installed_migration -v
```

All 22 tests passed in 212.624 s, covering eleven manager/network/install groups
and eleven recipe transaction/recovery groups. Across the three scoped suites,
59 distinct tests passed. A final
focused apply/idempotence/metadata-rollback test passed after extracting the
shared updater constructor (17.694 s). ShellCheck, shell syntax, Python compilation
and whitespace checks pass. One manual package-build attempt correctly refused
a mistyped full legacy commit before output creation; resolving the real full
commit and retrying succeeded. It was not a network or installed-state failure.

Independent code-review axes compare against consolidated base 58e4c6717.
Standards identified one duplicate updater-constructor contract; both tools now
share one constructor. Spec identified same-app/multiple-root payload collisions
and a manager-symlink content-drift gap. bbfc63fad separates backup/replacement
payloads by full installation-path identity and rejects linked managers. Focused
regressions pass, and both reviewers confirmed zero remaining actionable findings.
The source proposals are reviewed; no operational result follows from review.

## Fastest remaining sequence

1. Extend enrollment/policy for Sunshine and rehearse its installed transition;
   classify the 17 legacy updaters into shared-lifecycle adapters versus reviewed
   reinstalls, preserving custom behavior rather than blindly replacing them.
2. Rehearse exact manager/module delivery plus recipe migration/update/recovery
   end-to-end in disposable roots. Define binary recovery for real updates;
   before-images here are not binary rollback. Confirm restored format-1 behavior.
3. Settle documented policy/order changes, stale UI and realistic 49-source
   collection/retained-growth capacity. Current caps remain proposals; the new
   ref is not a capacity fix or permission to trim retained facts.
4. Review source/package and then authorize source push, workflow/ref transition,
   live acquisition/publication and independently accepted exact catalog pins.
   Read current remote controls first; this session has not checked them.
5. Guard and deliver exact manager/modules, generate per-installation plans from
   exact selected records, then perform the separately authorized host migration.
   Accept actual standalone/manager updates and a natural scheduled cycle.
6. Expand or explicitly retire remaining format-1 source support before deleting
   its publication/helpers. Local installed enrollment alone cannot retire 987
   still-supported source recipes.

No installed host changes, pushes, source/catalog publication, live acquisition,
workflow activation/dispatch, repin, main runtime promotion or yadm pointer changes
occurred. Only isolated local source/package work and main tracking records were
written. The package's three replacements are review artifacts, not applied plans.
