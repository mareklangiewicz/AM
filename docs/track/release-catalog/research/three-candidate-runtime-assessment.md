# Three-candidate runtime assessment

Ticket [126](../issues/126-assess-three-candidate-runtime-behavior.md), November 6, 2026.
This section records source inspection only. Executable offline evidence is
recorded separately below when available; source inspection is not a passing
runtime test. No recipe conversion or collection enrollment is recommended yet.

## Source identity and candidate locality

The upstream recipe source is Git commit
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22` (R36). The original template is
`templates/AM-SAMPLE-AppImage-in-archive` at R36, SHA-256
`d1ae5ae71a055af61f174425bfcd84e370ece780bcc50536b7674c76336f5119`.
The original generator `modules/template.am` at R36 has SHA-256
`48652a23fb28e8d912ed36ba40c8db6db9365d8ea3dc6bc7a77df39cfad3b12e`.
The [selector investigation](selector-review-groups.md) records their relationship
and source locations. Obtain original bytes using `git show R36:PATH`, replacing
R36 with the full commit above; do not substitute a working-tree generator.

Current fork evidence is commit `44fe43a1b293101e681c289f8b3d8430e78d2472`.
The following source hashes were checked directly against Git originals and
working-tree bytes, without executing a source recipe:

| Candidate | Repository literal in pinned recipe | R36 recipe SHA-256 | Current fork state |
| --- | --- | --- | --- |
| 20x | `peakflo/20x` | `f10790639ac193a1ecbcdc81824a8a22d9577906c80f4403d616a990069f7f31` | `programs/x86_64/20x` is byte-identical |
| 2fac | `jeonjw85/2fac` | `745b2c7ccd3dde951452ea86cfa33986b78f458c89b45b85ee0cdd7a82a9b0c5` | `programs/x86_64/2fac` is byte-identical |
| 4nier-patrimonio | `4nier-app/patrimonio` | `36ea29727167c231ac7fc2fb61d770c9a2622eccec258e726a1f26edce89a8ff` | `programs/x86_64/4nier-patrimonio` is absent |

All three have the same original body and same normalized installer/updater
selector. The first two are replacement candidates; the third would be a new
fork recipe, requiring a separate scope decision. No conclusion about current
upstream project activity or available assets follows from these pinned scripts.

None appears in the current [collection list](../../../../tools/catalog-collector/collection-recipes.txt)
or generated recipe declarations in
[catalog-yaml-policy.am](../../../../modules/catalog-yaml-policy.am:222).
The repository literals are evidence of spelling at the pin, not verified numeric
repository identity. No numeric IDs were found in the inspected recipe/declaration
and catalog research sources; all three IDs remain **unverified**. Do not invent
IDs for a production declaration or silently enroll these sources.

Current shared source SHA-256 values:

| Source | SHA-256 |
| --- | --- |
| `modules/appimage.am` | `961322c0d54aaeeaea98c5dcd78820cb2111c356478fd3f2f65181707761d132` |
| `modules/catalog-yaml.am` | `2edcf2bc445812985769a6cf95d65d281302d1345bb5f305a0c274e97464ecc7` |
| `modules/catalog-yaml-policy.am` | `6018c9b5d3d0081dd58d72c55432ba162f0b2ba44dc2c8606540db7fbe7f1fd4` |

## Proposed policy for assessment, not a production declaration

Use `CATALOG_CHANNEL=any`, URL version identity, `PACKAGE_KIND=appimage`,
`PACKAGE_LAYOUT=raw`, ordinary command-name desktop execution and no extra
launchers. The original selector accepts prereleases and direct URLs ending in
case-insensitive `appimage`; it does not choose a stable-only channel.
Conventional `.tar.gz`, `.zip` and `.7z` URL suffixes cannot pass this selector.
The archive-capable template name therefore does not justify choosing an archive
layout for these three candidates. Rehearsing archive behavior assesses a shared
runtime capability, not a claim that these apps publish such artifacts.

An assessment-only generic suffix pattern can be written
`^.*[.][Aa][Pp][Pp][Ii][Mm][Aa][Gg][Ee]$`. It is deliberately not a reviewed,
app-specific production asset pattern. Real asset names, repository identities
and acquisition formats need primary evidence before production declarations.
A synthetic repository ID in a disposable fixture is solely a test identity.
[recipe_declarations.py](../../../../tools/catalog-collector/recipe_declarations.py:37)
requires literal numeric identity and a complete header; an incomplete proposal
is not an installable short recipe.

## Client selection comparison

The three R36 scripts, lines 15 and 36, use the same full-response text pipeline:
extract HTTPS download-looking text, reject `i386|i686|armhf|aarch64|arm64|armv7l`
case-insensitively anywhere in the URL, require `appimage$` case-insensitively,
then take the first match. They do not read release/asset structures, publication
times or prerelease flags. Their request has no explicit pagination traversal.
A matching URL in other response text can count; the pipeline itself imposes
no structured-asset membership check.

The proposed generic declaration uses maintained
[selection logic](../../../../modules/catalog-yaml-policy.am:365):

| Dimension | Pinned pipeline | Shared declaration policy | Assessment consequence |
| --- | --- | --- | --- |
| Release order | First matching URL in response order | Greatest `published_at`, then greatest numeric release ID | May choose a different release even from identical facts; intentional policy choice needed |
| Asset order in one release | First matching URL encountered | Smallest bytewise asset name, then smallest numeric asset ID | Reordered/multiple assets can differ; do not claim unconditional equivalence |
| Prereleases | No exclusion | `any` accepts; `stable` rejects preview or tag `nightly` | `any` is the closest channel proposal |
| Architecture | Negative filter over whole URL | Negative filter over lowercased asset name | Repository/tag/path tokens and name tokens can give different answers |
| `armhf` | Rejected anywhere in URL | x86_64 declaration guard does **not** reject `armhf` | Generic suffix proposal may select an ARM hard-float asset; migration blocker |
| `armv7` | Rejects `armv7l` substring | Rejects `armv7` substring | Shared policy is stricter for some names |
| OS | No explicit OS filter | Rejects `macos`, `darwin`, `windows` in name | Shared policy intentionally narrows eligibility; review collisions in actual names |
| AppImage suffix | Case-insensitive full URL suffix | Case-sensitive ERE against asset name | Use explicit case classes for comparison; inspect real names before choosing production pattern |
| Missing asset | Falls through response text to later matches | Chooses among eligible structured assets from retained releases | Missing newest asset can select an older release under different ordering |
| Empty/no match | Installer calls `wget` with empty version; updater explicitly fails | Policy refuses `no_matching_asset` before acquisition | Shared refusal is stronger preflight behavior |
| Retained history | Only URLs in one fetched response | Entire retained release set in the catalog | An older retained match can be chosen outside the old response window |
| Freshness | No observation-age guard | Selected observation older than 172800 seconds needs exact acceptance tuple | New explicit refusal/consent behavior |

Sources: pinned recipes at R36; policy
[eligibility](../../../../modules/catalog-yaml-policy.am:365),
[selection order](../../../../modules/catalog-yaml-policy.am:428) and
[freshness](../../../../modules/catalog-yaml-policy.am:439).
[catalog-yaml.am](../../../../modules/catalog-yaml.am:108) validates the app map,
repository ID and document before selecting. The catalog's retained release set
can include records beyond current collection scope; see
[ADR 0002](../../../adr/0002-retained-release-observations.md).
The catalog deliberately does not publish GitHub's latest designation
([ADR 0001](../../../adr/0001-catalog-facts-and-client-selection.md)); these
candidates use `/releases`, not `/latest`.

The `armhf` admission is a concrete eligibility gap for a generic parity proposal,
not a demonstrated wrong selection from any candidate's real releases. A reviewed
app-specific pattern could exclude it, but no actual asset-name evidence has been
collected here. A generic policy correction or explicit narrower asset contract
must precede declaring this family migration-ready.

## Installation, update and removal comparison

The R36 template supplies the primary source for the upstream column below.
Current shared behavior is in [appimage.am](../../../../modules/appimage.am).

| Behavior | Pinned template | Shared runtime | Meaning for migration |
| --- | --- | --- | --- |
| Acquisition | `wget` chosen URL; updater first tries `appimageupdatetool -Or` even before URL-change check | Direct selected-asset `wget -O`, otherwise curl; no appimageupdatetool branch | Intentional acquisition policy difference; same URL skips shared update unless refresh/checksum settings require it |
| Raw payload | Conditional extraction based on downloaded filename suffix; otherwise move direct file | Explicit `raw` layout requires nonempty file, chmod and move | Generic AppImage URL selector supports proposed raw layout; neither path establishes real binary validity |
| Archives | Automatically tries 7z/tar/zip by suffix, loosely moves root or nested payload | Explicit tar/zip layout, checked member paths, declared root/executables, no 7z layout | Archive formats/layouts require an explicit reviewed declaration; not automatic equivalence |
| Replacement/backups | `mv --backup=t`; updater subsequently deletes `*~` alongside temporary paths | Stage inside app dir; raw `mv -f`, archives `cp -a --remove-destination`; recovery by reinstall | Do not promise durable numbered backup parity or transaction rollback |
| Failures | `set -u` with mixed explicit checks, no global `set -e`; some move/extraction errors can be followed by version write | `set -eu`, staged acquisition, explicit pre-replacement checks; version written after payload replacement | Test old payload survival for pre-replacement failures, but no whole-install transaction claim |
| Version state | Selected URL in `version` | URL by default in `version`, plus `download-url` | URL identity matches proposal; auxiliary state changes |
| Standalone updater | Embedded copy of original logic | Saved `recipe.am`, updater execs it with `--am-update` | Must rehearse saved recipe/helper paths in isolation, including no-change update |
| Binary links | Blind `ln -s /opt/$APP/$APP` | Creates missing links; preserves existing custom links/files | Stronger preservation is intentional; inspect actual installation paths before replacement |
| Desktop entries | Handles multiple desktop entries, hidden handler entries, deduplication; strips ` --no-sandbox` | Preserves an existing main desktop entry; otherwise extracts a main entry; no equivalent handler loop or sandbox stripping | Multi-entry and argument behavior are not equivalent; candidate-specific real extraction evidence remains required |
| Extraction fallback | Calls AppImage extraction directly | Falls back to installed `7z`/`7zz` on extraction failure | Shared fallback is an additional capability, not proof arbitrary extraction succeeds |
| Remover | Removes app link/tree/main desktop and discovered extra entries | Rewrites remover for declared links/app tree/main desktop | Existing extra desktop entries/removal ownership need separate inventory before converting an installation |

Primary locations in the shared source: [configuration/staging](../../../../modules/appimage.am:5),
[selection and URL identity](../../../../modules/appimage.am:85),
[update gate and acquisition](../../../../modules/appimage.am:116),
[replacement](../../../../modules/appimage.am:139),
[remover/updater](../../../../modules/appimage.am:154),
[link preservation](../../../../modules/appimage.am:177),
[desktop preservation/extraction](../../../../modules/appimage.am:194).
These comparisons apply to all three candidates because their original body and
normalized selectors are identical; they do not establish that actual AppImages
emit identical desktop/icon structures.

## Per-candidate readiness and next gates

| Candidate | Evidence-supported use now | Remaining blockers before conversion |
| --- | --- | --- |
| 20x | Existing fork recipe can be compared/rehearsed offline from exact pin | Numeric repository ID; actual asset names/desktop layout; eligibility contract including armhf; accepted release/asset ordering and acquisition differences; explicit collection/conversion scope |
| 2fac | Same bounded offline comparison as 20x | Same gates, independently verified for jeonjw85/2fac |
| 4nier-patrimonio | Pinned-source comparison only; suitable as inert fixture | Same gates plus explicit decision to add an absent recipe; not a routine replacement |

Recommendation: retain 20x and 2fac as the bounded existing-recipe preparation
pair, and keep 4nier-patrimonio as a source-only comparison until its addition is
explicitly scoped. Do not convert or enroll any of the three based solely on
recognition or synthetic checks. The ordering, structured-assets-only selection,
freshness and direct-acquisition differences need a recorded policy contract;
the armhf mismatch needs a precise eligibility decision. Actual repository IDs
and asset/launcher facts remain unknown in this offline assessment.

## Reproducing source inspection

Use `git show FULL_COMMIT:PATH` and SHA-256 for each original listed above.
Compare current `programs/x86_64/20x` and `programs/x86_64/2fac` byte-for-byte;
check absence of `programs/x86_64/4nier-patrimonio`. Inspect the named shared files
at the recorded fork commit. No upstream recipe, app payload or desktop launcher
was executed for this source comparison; no network or live install was used.

## Executable offline evidence

[Assessment checks](../../../../tools/recipe-reconstruction/test_candidate_runtime.py)
create a disposable command directory and synthetic declarations compiled by the
maintained `recipe_policy_source.py`. IDs 1, 2 and 3 are explicitly fixture-only;
they are not candidate repository identities. The actual awk selection module
runs against locally authored structured asset facts. Separately, only the
hash-checked, classified upstream FUNCTION expression runs, with curl returning
local JSON. No upstream installer/updater body executes.

Fourteen selection scenarios run for each of the three pinned candidates (42
comparisons). Explicit expected answers cover one match, response/publication
order divergence, multiple assets and name ordering, prerelease admission,
arm64 rejection, name/URL disagreements, architecture tokens in URL paths,
uppercase suffixes, no matches, empty responses, missing newest assets,
retained assets outside the response page, OS filtering, and the armhf gap.
Separate checks verify stale-record and wrong-repository refusal for all three.
The observed differences match the source comparison above. `any` plus the
case-expanded suffix is an assessment proposal, not a parity-approved policy.

The actual shared installer module runs with a stub six-line selection helper,
all install/link/desktop paths under TemporaryDirectory, stub wget/curl, and an
authored inert payload that responds only to desktop/icon extraction. For each
candidate, checks cover direct install, icon/main desktop output, link target,
saved-recipe standalone no-change updater, changed-URL replacement, app-data and
custom desktop preservation, custom command preservation during reinstall,
remover output exercised in the disposable tree, and absence of a durable raw
backup. A present appimageupdatetool stub is never called. Failed transfer, empty
payload and helper refusal preserve the existing executable/version/metadata;
staging directories are cleaned after transfer/payload failure.

One additional shared-capability case rehearses a local tar archive: raw layout
stores archive bytes without autodetection (existing desktop prevents executing
those bytes); explicit tar/root configuration stages the inert payload; a wrong
root fails before replacing it. This is not evidence of archive availability for
any candidate. Zip, 7z, symlinked/multiple/hidden desktops, extraction fallback,
post-replacement interruption, curl fallback, and manager dispatch were not
executed by this harness. Full catalog acquisition/parser/publication integration
is also outside it; the lifecycle selection helper is intentionally stubbed.

A concrete removal limitation is preserved in the evidence: install/reinstall
preserves a custom primary command, but the generated remover still removes that
primary path unconditionally. The fixture verifies this current behavior rather
than implying uninstall preserves custom commands. Existing extra desktop/remover
ownership therefore remains a conversion inventory gate.

Reproduce the focused checks from the repository root:

```sh
python3 -B -m unittest discover -s tools/recipe-reconstruction \
  -p 'test_candidate_runtime.py' -v
```

The first harness run lacked gzip in its isolated PATH; adding that required
local archive tool made the tar rehearsal pass. This was a harness setup issue,
not a production runtime change. No real app binary, network fetch, live
installation, enrollment or recipe conversion was performed.

Final validation: the focused assessment passes all five test groups; the full
recipe-reconstruction suite passes all 33 tests in 7.533 seconds. Documentation
links and whitespace checks pass. This does not claim a full catalog/container
suite or an independent code review.

## Ticket 127 source follow-up

The armhf gap above describes the source at `44fe43a1b`; it is retained as
historical evidence. Ticket [127](../issues/127-review-armhf-declaration-eligibility.md)
adds armhf exclusions on x86_64, aarch64 and i686 in current source. armv7l still
requires an explicit armv7 label; armhf alone is insufficient. The assessment
oracle now expects both the old selector and proposed x86_64 declaration to
refuse App-armhf.AppImage. Other recorded name/URL, ordering, OS, freshness and
acquisition differences remain. This source change is not a deployment or
conversion approval, and it does not verify actual candidate assets or IDs.
