# Two existing AppImage recipes: static inspection and conversion proposal

Ticket [129](../issues/129-inspect-two-candidate-appimage-payloads.md), November 6,
2026. Source reviewed: `06c01414c`. Proposal only; no recipe conversion or
enrollment is approved or performed. 4nier-patrimonio is outside scope.

## Provenance and acquisition

[126](three-candidate-runtime-assessment.md) supplies exact original recipe,
generator and template identities. The two current recipes remain byte-identical
to `bbffd15c19d01ef9124fbf99b5b9c41d2661ea22`:

| Path | Recipe SHA-256 |
| --- | --- |
| programs/x86_64/20x | f10790639ac193a1ecbcdc81824a8a22d9577906c80f4403d616a990069f7f31 |
| programs/x86_64/2fac | 745b2c7ccd3dde951452ea86cfa33986b78f458c89b45b85ee0cdd7a82a9b0c5 |

[128](two-candidate-upstream-preparation.md) supplies verified repository IDs,
complete saved first-page responses, selected release/asset IDs and URL comparison.
Its archive SHA-256 and every saved metadata response hash were checked before
acquisition. The exact saved URLs were used; no newer release was substituted.
The acquisition script checks recorded asset IDs/sizes, HTTP 200, Content-Length
when present, streamed byte limits, exact final length and published SHA-256.
Combined payload bytes were 520,789,917, below the 550 MiB cap (576,716,800).
Initial sandbox DNS failed; the same bounded script succeeded with approved
network escalation. Payloads remain non-executable evidence under
`/tmp/am-129-evidence`; they are not committed.

| App | Release ID / asset ID | Bytes | Independently computed SHA-256, matching saved GitHub digest |
| --- | --- | ---: | --- |
| 20x | 427758388 / 688278008 | 437228965 | 6ffcb3afebfca50759099b9bc87e4573abe243dbda021da32659bc3a0d8d98cf |
| 2fac | 398019492 / 594778867 | 83560952 | 21fb4feb150e618aa6f652109a510a5c807f516124c3fe509e2509b04b4575b1 |

URLs, timestamps, digests and evidence archive hash are in the
[receipt](two-candidate-payload-evidence.json). A digest match verifies downloaded
bytes against that metadata, not publisher independence or application safety.
No AppImage, downloaded AppRun, hook, desktop entry or other application code was
executed. This does not test actual application launch behavior.

## Static payload inventory

Used system `unsquashfs` 4.7.5 (2026/03/01), Python and GNU sed versions retained
in the [evidence archive](two-candidate-payload-evidence.tar.gz). Scanned for
SquashFS magic and required a successful static `unsquashfs -s` validation;
first magic occurrences were false positives, not the filesystem offsets.
Validated offsets: 20x 188392 (gzip), 2fac 944632 (zstd). Full numeric-owner
listings, superblocks and selectively extracted desktop/icon/AppRun bytes are
retained. `-cols 1000` prevents listing truncation. Extraction used one processor
and only explicit metadata paths into disposable directories, with no root
privileges or ownership restoration. Both filesystem roots are mode 0755,
UID/GID 0/0 in the image; these image IDs do not establish installed ownership.

| Fact | 20x | 2fac |
| --- | --- | --- |
| Main entry | root `20x.desktop`, regular 0644 | root `2FAC.desktop` symlink to `usr/share/applications/2FAC.desktop`, regular target 0644 |
| Other desktop entries | None in full filesystem listing | Only that root alias and its target; one logical entry |
| Hidden/multiple entries | No `Hidden`/`NoDisplay`, actions or extra entries | No `Hidden`/`NoDisplay`, actions or extra entries |
| Original Exec | `AppRun --no-sandbox %U` | `totp-vault` |
| Icon key | `20x` | `totp-vault` |
| Root .DirIcon | symlink to `usr/share/icons/hicolor/512x512/apps/20x.png` | symlink to `2FAC.png` |
| Icon target | regular PNG, 129006 bytes | regular PNG, 3444 bytes |
| Other root icon | `20x.png` symlink to same icon | `totp-vault.png` symlink to `usr/share/icons/hicolor/32x32/apps/totp-vault.png` |
| AppRun | regular 0755 Bash script, forwards arguments to `$APPDIR/20x` on exit | regular 0755 Bash script, sources GTK hook and execs `AppRun.wrapped` with arguments |

All listed desktop/icon links are relative and resolve within the image. The
2fac desktop and icon each need one link-resolution pass; the 20x icon needs one.
The shared installer's ten-pass loop covers these observed shapes. No additional
handler launcher is evidenced. The full listings retain other symlinks, including
2fac library links; these are not installed as a loose tree by raw layout.
Reading AppRun is static evidence only: actual runtime, Electron sandbox support,
GTK dependencies, command-line handling and GUI behavior remain untested.

## Concrete source proposal

Replace only `programs/x86_64/20x` and `programs/x86_64/2fac`, through the existing
short declaration/wrapper interface, retaining the normal script header,
`set -eu`, `CATALOG_FORMAT=2`, `. /opt/am/modules/appimage.am` and
`am_appimage "$0" "$@"`. The complete proposed varying fields are:

| Setting | 20x | 2fac |
| --- | --- | --- |
| APP | `20x` | `2fac` |
| CATALOG_RECIPE | `x86_64/20x` | `x86_64/2fac` |
| CATALOG_ALIAS | `https://api.github.com/repos/peakflo/20x/releases` | `https://api.github.com/repos/jeonjw85/2fac/releases` |
| CATALOG_REPOSITORY_ID | `1152028865` | `1337965664` |
| CATALOG_REPOSITORY | `peakflo/20x` | `jeonjw85/2FAC` |
| CATALOG_CHANNEL | `any` | `any` |
| CATALOG_ASSET_PATTERN | `^20x-linux-x86_64[.]AppImage$` | `^2FAC_[0-9]+([.][0-9]+)*_amd64[.]AppImage$` |
| PACKAGE_KIND / PACKAGE_LAYOUT | `appimage` / `raw` | `appimage` / `raw` |
| DESKTOP_EXEC | `command` | `command` |
| EXTRA_APP_LAUNCHERS | empty | empty |

Use URL version identity, no forced refresh, normal 172800-second observation
freshness guard, and direct selected-asset acquisition. These are proposed values,
not accepted migration policy. The 20x alias pattern preserves the observed old
URL rather than choosing its versioned sibling. The 2fac pattern deliberately
refuses new nonnumeric version spellings pending review.

Proposed policy decisions to accept together in a separately authorized source
conversion: publication time then numeric release ID ordering; smallest bytewise
asset name then ID; structured asset membership; name-based platform/architecture
filtering; any channel (including prereleases); selection over retained releases;
explicit stale-selection acceptance; direct full download rather than
appimageupdatetool. This follows current shared interfaces and ADRs 0001/0002,
not unconditional legacy first-response-URL parity. 128 proves the saved winners
only. Do not extend the first-page observation into an all-history claim.
Future acquisition may be optimized independently, as recorded in ticket 105.

## Launcher decision and conversion gates

Applying the actual shared sed expression to copies of the extracted entries
produces `Exec=20x --no-sandbox %U` and `Exec=2fac`; icon keys become
`/opt/20x/icons/20x` and `/opt/2fac/icons/2fac`. Applying the old recipe's extra
strip produces `Exec=20x %U`. Both outputs are retained as inert desktop files.
The 2fac argument contract is compatible on this evidence. For 20x, recommend
preserving the existing fork behavior (`Exec=20x %U`) rather than silently
introducing the payload's `--no-sandbox` argument. The current shared declaration
has no sandbox-argument policy setting, so 20x needs a separately scoped,
explicitly reviewed desktop transformation or an explicit decision accepting
retention of the payload argument. Do not generalize a global strip or silently
claim the present wrapper implements this recommendation. Application launch
success under either form is untested.

Raw layout stores the AppImage and extracted icon inside `/opt/<app>`; it does
not copy the image's root-owned tree into system locations. Default command
links are `/usr/local/bin/<app>`, main desktop files are
`/usr/local/share/applications/<app>-AM.desktop`. Remover deletes the command,
app tree and main desktop. Shared installer preserves preexisting custom links
and main desktop entries, but remover still unconditionally deletes the primary
command. Source migration therefore needs explicit ownership inventory before
any existing-install transition; this ticket inspected no installed files.
An older installed release may have extra handler/numbered desktop entries,
custom commands or remover responsibilities that this sampled payload cannot
rule out. Preserve/reconcile those explicitly instead of overwriting removers
and orphaning entries. Existing desktop preservation also means a recipe refresh
alone will not apply a chosen new desktop argument policy.

A follow-up may authorize source conversion of 2fac independently; the pair
should not be described as ready for unchanged shared-runtime conversion until
the 20x argument decision is resolved. Separate collection enrollment requires
literal declaration compilation, registry regeneration and scoped offline
selection/lifecycle checks, including this real symlink metadata shape with inert
payloads. Production catalog coverage must exist before clients depend on it.
Deployment, installed transition, runtime launch testing and push remain separate
authorizations. No such action is taken here.

## Evidence verification and reproduction

The archive retains acquisition code, receipts, tool versions, full listings,
superblocks, offsets, static metadata summary, original desktop/icon/AppRun
bytes and transformed desktop copies. Its manifest hashes all regular members;
symlink targets are recorded by the summary and tar metadata. Full payloads are
intentionally omitted. Verify the archive against the JSON receipt, extract into
an empty disposable directory using Python tarfile's `filter='data'`, then verify
manifest hashes. Original metadata is inert evidence; never source or launch it.

With exact hash-verified full assets, reproduce static listing/extraction with:

```sh
unsquashfs -cols 1000 -o 188392 -lln /tmp/am-129-evidence/20x.AppImage
unsquashfs -cols 1000 -o 944632 -lln /tmp/am-129-evidence/2fac.AppImage
```

Use `-processors 1 -no-progress -d NEW_DIRECTORY` followed by the asset and
explicit metadata paths from `static-summary.json` for selective extraction.
Do not use AppImage self-extraction: that executes its runtime. No new runtime
code changed, so validation here checks evidence integrity, source identity,
textual desktop transformations and documentation; 126's inert runtime tests
remain earlier evidence, not a real-payload launch test or complete suite rerun.
