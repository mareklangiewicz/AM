# Large existing-recipe batch: runtime gates

Ticket [133](../issues/133-prepare-large-existing-recipe-batch.md), November 6,
2026. Source assessment of the first 35 alphabetical unchanged whole-template
AppImage instances from the regenerated pinned inventory. This is a candidate
pool for a twenty-recipe batch, not conversion approval for all 35. No payload
was acquired or application code executed by this assessment. Per-app upstream
and static-payload evidence is a separate prerequisite.

## Primary source and provenance

Recipe source pin R36 is `bbffd15c19d01ef9124fbf99b5b9c41d2661ea22`.
Template pins are R36 and R35 (`bb53f3180ec92f862020f8bdccef0f6614015bae`).
Read originals with `git show FULL_COMMIT:templates/NAME`; no copied template
was used. Current runtime assessed is [modules/appimage.am](../../../../modules/appimage.am)
at the completed pilot revision `b61eb2733441d2dd5f998f350ce32a3da1ebc2f9`.
[ADR 0001](../../../adr/0001-catalog-facts-and-client-selection.md) owns the
client-selection boundary; [ADR 0002](../../../adr/0002-retained-release-observations.md)
owns retained observations. Historical [design notes](../../../design/version-catalog.md)
do not override these accepted decisions or the current
[operating policy](../../../catalog-operating-policy.md).

Replayed `Catalogue.render` directly from each inventory match and checked
bytes against both the current recipe and `git show R36:programs/x86_64/APP`.
All 35 are exact; installer/updater app, repository and FUNCTION captures agree.
The matching template identities and SHA-256 values are:

| Short name | Git identity | SHA-256 |
| --- | --- | --- |
| R36 AI | R36:`templates/AM-SAMPLE-AppImage` | `5353962fac61f7e0f8d3e949a824700c522c6229c6243ab16e2847a4e71edfa2` |
| R36 AIA | R36:`templates/AM-SAMPLE-AppImage-in-archive` | `d1ae5ae71a055af61f174425bfcd84e370ece780bcc50536b7674c76336f5119` |
| R35 AI | R35:`templates/AM-SAMPLE-AppImage` | `1049be481f39bdcdcd3ffa348ac94cdbdaaa65cfe1d341940e4b017963344931` |

| App | Repository capture | Template | Original recipe SHA-256 |
| --- | --- | --- | --- |
| 0x808 | `averagenative/0x808` | R36 AI | `135d39140f10709b8854b20df8ee5cfcce0d4c13ea705129fa12858217bc7ce5` |
| 0xsynth | `averagenative/0xsynth` | R36 AI | `e9c0e827f2ff661d9192bbfe4a65b4d1845d6cb025e770bcda8ab175a0100b1f` |
| 3mf-katalog-manager | `bexxs75/3mf-katalog-manager` | R36 AI | `05c1b2d3b69cdc5e6d97e46be598e3f38bcdda45c25998303b28e8cc14b8de3e` |
| 5ire | `nanbingxyz/5ire` | R35 AI | `134e8bc2607d077a9b71428bb2e431fd2a1fb92ee08bf5ab5c7bee99e4c4906f` |
| 6502-emulator | `acwright/6502-emulator` | R36 AIA | `1d817ccb527a5da43559eb51e31a98122d435ceca2deff1e9d1be3042c459551` |
| a0-launcher | `agent0ai/a0-launcher` | R36 AIA | `032ffcfa9055dca9d471e3f1c4555f79daba3205dcb62d00083b32e1469ab761` |
| aartiq | `latestinssan/aartiq` | R36 AIA | `21d9d7b4ff3c1510e6a3ac234ea0481cb5a32f3a915e6e3916bd474736d88ce5` |
| abcarus | `topchyan/abcarus` | R36 AIA | `618ddebe01a775fc5dd2ad64c3c4a9e58d533fa9df7d93a786f3de9e93fce303` |
| abundio | `emullernl/abundio` | R36 AIA | `1f1e027921ed1f6170d8c01559e1be521be399deb76cb9a3dc17381d41dc318c` |
| accordserver | `daccordproject/accordserver` | R36 AIA | `2bece698731f5d991bb15f91f400e4dad34179f53e80b213ee5032aec9ab3364` |
| accshift | `klnuno/accshift` | R36 AIA | `8eb5689baec3bab9795289bb0f82c61b6ef11e9afc896995484dcc9dbdd77898` |
| ace-gui | `daisy/ace-gui` | R36 AIA | `cf94279ca07520dec58aa670f470a5090965849c2686c0c020b154f6ccf09629` |
| ace-step-studio | `timoncool/ace-step-studio` | R36 AIA | `90c70a404e7c38ab9d50ad5764b1ecd0917146b043323c40a6d44e4c87f232f8` |
| acp-ui | `formulahendry/acp-ui` | R36 AIA | `22810029eed1db6d5615e3be88e3b62b9c9e2950e8746b6f38eb6af33d71a16b` |
| acreom | `Acreom/releases` | R35 AI | `6600c502e7303f31a6b131157251761896cc0e42214049467e335702d05e829f` |
| actiona | `Jmgr/actiona` | R35 AI | `0a54832d98925c0b1a32319b7f2bf8bf56d4b0bf45d85429cd230fc9c76656ea` |
| actone-screenplay | `beetlebot/actone-screenplay` | R36 AIA | `60c1b39615d210aee36c408c09623bb07e721605c00e51ff0335b21c1a0bcb12` |
| actual | `actualbudget/releases` | R35 AI | `3173c53f4bde64d7e06ddbec16839975626aa3acce8c63aab5716a41744649dc` |
| ada | `black141312/ada-releases` | R36 AIA | `be6e8ff6866e4986ba94e898700a68a931ca8356b666f45ab24448481b9bf88d` |
| adbkit | `drenzzz/adbkit` | R36 AIA | `542e525954bc42b98e7cbf50cf57907d91e4b0cb39a693000754fd881cc3851a` |
| adelie | `lmliheng/adelie` | R36 AIA | `e7d1e7492dc8c3f45470707478590412f7253777ddde8142111c40c4382ec682` |
| adiman | `chaosthechaotic/adiman` | R36 AIA | `cade2ad4e42c6a08766fdf47a3bfc0574a0f1a5dd6be5c2b3fd962f53240956a` |
| adt-studio | `unicef/adt-studio` | R36 AIA | `a88ec2cd39304cdba674c67bd414d96668a20fa179c538f83faf9b701350ab2a` |
| advanced-rest-client | `advanced-rest-client/arc-electron` | R35 AI | `ca33a83851d3842f9b35a52ff449c39e9bf06ee89ed1aae884a0377b24883aa1` |
| adventshow | `adventtools/adventshow` | R36 AIA | `522eefcad3f63b4d3dc71002c2933e910f3fd754c35c05c4547da6053a4598c6` |
| aegis | `dylanddeng/aegis` | R36 AI | `ecfc53d655017d991a48c6383a8cc70bd7cfa56748b96c11485c3d053c2fd466` |
| aero-sync | `atulsain011/aero_sync` | R36 AIA | `b8dd59301446bfdd19daebbae09d334213163ed53009e97cbfd3577801936916` |
| aeroftp | `axpdev-lab/aeroftp` | R36 AI | `ce2608ab20495acff1113d10e258c419267cb856df447c6fb1a367924a4ace8b` |
| aes-lacrima | `aruantec/aes_lacrima` | R36 AIA | `153aec44cf2263808d76a726765a52c5b533135b170673df3db0cbbe15a59533` |
| aether | `alisawari/aether` | R36 AIA | `66992e5acffb4234afbc11c468cdee8a3c0c8ee1315ebb23c7afcaa5d69b9d5a` |
| aether-gui | `matinsenpai/aether-gui` | R36 AI | `de9d6bcede4486cab02983389e0313579979c2c81d1f11e2d0ecdefbfb3089c4` |
| aethersdr | `aethersdr/aethersdr` | R36 AIA | `5611690f43ccf07e99fa23b535282fb17ee120a12d1f6c6d942011c6ff944828` |
| aevum | `alonera/aevum` | R36 AIA | `3f818b587727f1983ab78f0fa878c188b60a67eca5a15970b792de9ea4b535da` |
| affinity | `ryzendew/Linux-Affinity-Installer` | R35 AI | `5e19aecb783a33b05e69d4d48ad4023af41c08767fd01dadaf33a0d7fa051302` |
| afsplug | `zhangxianhe666/afsplug` | R36 AIA | `9f4d6ed202cfe0770c660dd5ed054d778cdcb27f9914c07ab444ef11d7caa435` |

## Gates that must hold per converted recipe

All 35 source selectors use `/releases`, including prereleases. None requires
reproducing GitHub's `/latest` designation. Six R36 AI selectors use a
case-insensitive AppImage URL suffix with armhf exclusion. Six R35 AI selectors
also use an AppImage suffix but omit armhf exclusion. Sixteen R36 AIA selectors
add the recognized default `appimage$` keyword. Seven R36 AIA selectors have no
suffix constraint: **6502-emulator, aartiq, accordserver, actone-screenplay,
adt-studio, aero-sync and aether**. For those seven, an archive or sidecar may win;
whole-template recognition does not make `PACKAGE_LAYOUT=raw` suitable.

Before conversion, compare the exact extracted old selector's winner on the
saved first-party release response with the proposed declaration's winner.
Record and decide any mismatch rather than substituting a convenient direct
AppImage silently. Verify repository numeric identity/full-name redirects,
release/asset IDs, observed name and download URL, exact length and digest.
Use a narrow asset-name pattern supported by observed names and explicit
version grammar. Shared architecture/platform exclusions operate on asset names;
old exclusions operated on arbitrary matching URL text, including tag/release
body URLs. Saved winner agreement is one observation, not a universal semantic
parity proof or a complete-history assertion.

The explicit shared policy remains publication time descending then numeric
release ID, bytewise asset name then numeric asset ID, structured asset
membership, retained releases, `any` channel when preserving these templates'
prerelease eligibility, normal 48-hour release-observation freshness, URL version
identity and direct selected-asset download. These differences from first URL in
upstream response text need acceptance as part of the conversion policy. Empty
responses and missing assets must refuse/fall through as specified; older retained
releases can remain selectable even outside the latest fetched page.

For direct raw acquisition, statically validate a real AppImage filesystem with
system tools and hash the complete payload. Never invoke AppImage extraction,
AppRun or a downloaded script as inspection. Require one visible logical root
`.desktop` entry and a usable `.DirIcon` with internal, relative link chains
resolvable within the shared ten-pass limit. Preserve the entire filesystem
listing, desktop text, icon link targets and data hashes. An additional desktop
deep in the tree is not necessarily another root launcher; account for whether
it is the root alias target or a distinct logical entry. Refuse absent/broken
metadata, absolute/escaping chains, ambiguous multiple root desktops, hidden or
NoDisplay handlers needing additional installed outputs.

Both R36 templates implement multiple/NoDisplay desktop handling and additional
remover entries; the shared runtime moves a single root `*.desktop` into one
main file. R35 AI has the single-entry shape already. No source template declares
extra command aliases beyond its primary app link. `EXTRA_APP_LAUNCHERS` therefore
stays empty unless independent evidence establishes another requirement; it
cannot represent a second desktop handler. Existing install migration needs a
separate inventory of historical additional desktop files and custom links.

All three original templates globally remove the literal substring
` --no-sandbox` after rewriting Exec/Icon. The shared runtime preserves arguments
by default; set `DESKTOP_STRIP_NO_SANDBOX=true` for simple space-delimited flags
to retain source behavior. Inspect all desktop fields: the shared opt-in only
changes Exec lines and avoids prefix collisions such as `--no-sandboxing`, while
the originals strip globally and can change comments/other arguments. Quoted or
escaped flags and meaningful occurrences outside Exec require individual review.
Apply actual old/new sed transformations to inert metadata copies and compare
results. Quoted Exec program paths also require review because the common
`Exec=[^ ]*` replacement is textual, not a desktop argument parser.

Original updaters try `appimageupdatetool -Or` before URL comparison and then use
numbered backups; shared acquisition downloads exactly the catalog-selected URL,
stages and renames the raw executable and does not use embedded delta selection.
This is the accepted pilot direction, not byte-for-byte updater equivalence.
Failed transfer leaves the old executable/version; no full rollback transaction
is promised. App data and custom existing main desktop/command are preserved on
install, but the generated remover unconditionally deletes the primary command
and app tree. Source conversion does not authorize replacing installed recipe,
remover or launcher metadata. The shared normal updater skips an unchanged URL,
updates the binary/version only on a changed URL, and preserves desktop metadata.

## Validation performed

`python3 -B -m unittest discover -s tools/recipe-reconstruction -p test_candidate_runtime.py -v`
passed all **7 tests** in 4.338 seconds. These existing focused checks cover
selection ordering and URL/name/architecture/channel differences, stale/wrong
repository refusal, direct install and standalone update, custom data/desktop
preservation and generated remover, failed/empty downloads, both pilot metadata
link shapes, narrow desktop argument transformation, and explicit archive layout
refusal. They run authored inert assets and stubbed transfers in disposable
paths; they do not test any of these 35 real applications or GUI launches.

The 35 exact reconstructions are separate source-integrity verification; no
upstream live availability, current asset identity or static payload compatibility
is inferred from them. No recipe/runtime/collection edit, enrollment, push,
publication, installation or deployment was performed by this assessment.
