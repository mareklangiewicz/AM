# Recipe exceptions and remaining legacy callers

Static source audit for ticket [45](../issues/45-recipe-inventory-and-migration-batches.md),
2026-10-28, recipe/manager baseline `ee56537bcfbdea5d373980f7ad8d7c59cf40bbee`.
No recipe/updater, binary, metadata filter or network request was executed. Counts
below describe source text, including generated updater heredocs, not runtime
requests, installed-host coverage or current upstream availability.

## Exact enrolled aliases leave three straightforward legacy candidates

The six numeric requests and their exact named aliases are declared in the
[staged manifest](../design/staged-manifest.json). Each literal GitHub API token
was compared to the full alias string after stripping shell quote delimiters and
trailing command-substitution parentheses. No query, pagination, endpoint or
repository spelling was normalized. This is lexical discovery rather than shell
interpretation; variable-composed URLs remain outside this exact-match result.

| Enrolled alias | Current literal recipe matches | Consequence |
| --- | --- | --- |
| Obsidian `/releases` | x86_64 `obsidian` | Already migrated; no additional matching recipe. |
| Obsidian `/releases/latest` | None | Retained latest data is not permission to replace a release-list selector. |
| Neovim `/releases` | x86_64 `nvim`, x86_64 `nvim-nightly`, aarch64 `nvim`, aarch64 `nvim-nightly` | Stable x86_64 is migrated; three remaining AppImage recipes form one exact-covered batch. |
| Neovim `/releases/latest` | None | Does not expand current recipe coverage. |
| WezTerm `/releases?per_page=100` | x86_64 `wezterm-nightly` | Partial coverage only: its update identity requires a second, unenrolled events request. |
| SQLite Browser `/releases?per_page=100` | x86_64 `sqlitebrowser` | Already migrated; no additional matching recipe. |

The existing shared recipe declarations provide the three migrated matches:
[Obsidian:6](../../../../programs/x86_64/obsidian#L6),
[nvim:6](../../../../programs/x86_64/nvim#L6),
[SQLite Browser:6](../../../../programs/x86_64/sqlitebrowser#L6).
The other four files and precise differences are described below. Seven recipe
files match at least one enrolled alias; that is not seven additional migratable
apps.

The three remaining Neovim recipes already use an AppImage binary and duplicate
install/update selectors. Stable aarch64 excludes nightly and x86 variants;
nightly x86_64 excludes ARM variants and requires `nightly`; nightly aarch64
excludes x86 variants and requires `nightly`. Preserve these exact filters rather
than inventing a new architecture/channel policy. All three contain the common
AppImage lifecycle and alternate update branch. Their source evidence is
[aarch64 stable:15/36](../../../../programs/aarch64/nvim#L15),
[x86_64 nightly:15/36](../../../../programs/x86_64/nvim-nightly#L15), and
[aarch64 nightly:15/36](../../../../programs/aarch64/nvim-nightly#L15).
Their `readlink` loops differ from the managed runtime's normalization, but this
is the same extraction/symlink family, not evidence for an extra hook. A migration
must prove each preserved filter on retained bytes, exercise both install/update
and delivery, and report absent matching assets honestly rather than change the
filter or collect new releases just to make the test pass.

Stable WezTerm reads plain `/releases` in both its installer and updater, while
only `?per_page=100` is enrolled. Reusing the latter would change the response
contract and potentially the selected release; stable WezTerm therefore needs a
separate exact-alias enrollment decision. [Stable source:15/36](../../../../programs/x86_64/wezterm#L15).

Nightly WezTerm records a numeric value filtered from `/events` as its `version`,
then selects a nightly AppImage from the enrolled release-list URL using `tail
-1`. Its generated updater repeats that split (and contains an existing `wget
wget` spelling). The shared AppImage interface currently uses the selected binary
URL as the version identity. A read substitution cannot preserve this independent
events-derived identity. Do not claim this recipe is ready from release metadata
alone, silently replace the identity, or create an events/identity hook before a
concrete reviewed decision. [Nightly source:15/16](../../../../programs/x86_64/wezterm-nightly#L15),
[updater:36/45](../../../../programs/x86_64/wezterm-nightly#L36).

`appimageupdatetool` itself is another real exception, rather than evidence for a
universal hook. It composes the GitHub request from SITE, self-updates from embedded
zsync metadata, then records the URL reported by `appimageupdatetool -d` so optional
verification checks the binary actually downloaded. Removing that branch while
writing a different scraped release URL would discard an existing fork-specific
repair. Its endpoint is not in the six-source manifest. [Source:14/33](../../../../programs/x86_64/appimageupdatetool#L14),
[self-update repair:58–65](../../../../programs/x86_64/appimageupdatetool#L58).

## Remaining support has real callers

The fork already pins `ALT_GH` to GitHub itself; `_alt_gh_on` is an identity rewrite,
not an active third-party fallback. `_alt_gh_off` restores historical proxy URLs
in installed scripts. Zero old-proxy literals in current recipes does not prove
there are zero such installed scripts. [Manager:2041–2053](../../../../APP-MANAGER#L2041).

| Support | Current callers/conditions | Removal conclusion |
| --- | --- | --- |
| Token insertion into installed updaters | Legacy branch of normal batch processing calls `_update_github_api_key_in_the_updater_files`; the function explicitly excludes marked catalog updaters. [Manager:1447](../../../../APP-MANAGER#L1447), [2246](../../../../APP-MANAGER#L2246). | Retain while legacy GitHub updaters remain; migrating three recipes cannot remove it. |
| API quota probe | Legacy normal updates call `_update_determine_gh_apps_number`; force-latest and rollback filtering call it separately. It explicitly excludes marked catalog updaters from counts. [Manager:2056](../../../../APP-MANAGER#L2056), [2247](../../../../APP-MANAGER#L2247), [2283](../../../../APP-MANAGER#L2283), [2078](../../../../APP-MANAGER#L2078). | Retain for remaining callers; catalog enrollment does not migrate force-latest or rollback. |
| `_alt_gh_on` | Legacy updater preparation, low-budget legacy installer and rollback generation. [Manager:2104](../../../../APP-MANAGER#L2104), [install:326–330](../../../../modules/install.am#L326), [rollback:232](../../../../modules/management.am#L232). | No unused-helper claim. The identity rewrites could be simplified separately only with caller-specific behavior/tests. |
| `_alt_gh_filter` | Rollback obtains a command pipeline and evaluates it. [management:203–204](../../../../modules/management.am#L203). | Preserve nonempty command output, including the existing high-budget `cat` repair. |
| `_alt_gh_off` | Legacy updater completion and installation completion. [Manager:2116](../../../../APP-MANAGER#L2116), [install:432](../../../../modules/install.am#L432). | Source-only migration cannot establish that installed historical-proxy repair is unnecessary. |
| Installer token edits | General install preparation and AppMan conversion still insert the configured token header into inline API command patterns. [install:25](../../../../modules/install.am#L25), [289](../../../../modules/install.am#L289). The catalog alias declaration does not match that inline command pattern. | Retain for unmigrated installers. Do not infer this whole preparation path is unused from tiny catalog recipes. |
| GitHub template/preview | Repository description lookup and preview strings still use the configured token and quota probe; ALT_GH remains GitHub here too. [template:220–230](../../../../modules/template.am#L220). | This is not an installed updater caller; future removal must address template behavior explicitly. |
| Alternate AppImage updater | Thousands of recipe-generated update bodies still call `appimageupdatetool -Or`; manually integrated launchers also use it directly. [manager:2142–2156](../../../../APP-MANAGER#L2142). Rollback disables the embedded branch in its copied updater. [management:234](../../../../modules/management.am#L234). | Delete only each migrated recipe's displaced branch. Launcher integration remains a separate supported feature. |

The actual marked batch branch executes the trusted updater and verification
without legacy preparation; legacy preparation is confined to its separate
subshell. This confirms ticket 44's local integration rather than evidence of a
fleet migration. [Manager:2230–2249](../../../../APP-MANAGER#L2230).

## Static caller scale and reproducibility

Scan every regular file immediately under `programs/{x86_64,aarch64,i686,armv7l}`.
For each needle, count files with at least one matching non-comment line and total
matching lines. A comment line is one whose `lstrip()` starts with `#`; heredoc
bodies and quoted shell strings are included. This makes the metric reproducible
without pretending it is a parser or runtime counter.

| Architecture | Files scanned | Files containing `appimageupdatetool -Or` | Matching non-comment lines | Files containing `https://api.github.com` | Matching non-comment lines |
| --- | ---: | ---: | ---: | ---: | ---: |
| x86_64 | 8899 | 8298 | 8299 | 8641 | 17370 |
| aarch64 | 1787 | 1570 | 1570 | 1774 | 3558 |
| i686 | 28 | 21 | 21 | 21 | 42 |
| armv7l | 2 | 2 | 2 | 2 | 4 |
| Total | 10716 | 9891 | 9892 | 10438 | 20974 |

The extra x86_64 alternate-updater line is kdenlive's rollback `sed` expression,
not an additional execution site. [kdenlive:169](../../../../programs/x86_64/kdenlive#L169).
API text counts include catalog alias declarations, dynamic forms and generated
updaters. They are not counts of direct API runtime calls or distinct endpoints.
All four architectures have **zero** non-comment source lines containing
`api.gh.pkgforge.dev`. That is a current source-text result only.

Reproduce the table with Python's standard library; it reads source bytes only:

```python
from pathlib import Path
for arch in ('x86_64', 'aarch64', 'i686', 'armv7l'):
    files = [p for p in (Path('programs') / arch).iterdir() if p.is_file()]
    print(arch, len(files))
    for needle in ('appimageupdatetool -Or', 'https://api.github.com',
                   'api.gh.pkgforge.dev'):
        counts = [sum(needle in line and not line.lstrip().startswith('#')
                      for line in p.read_text(errors='replace').splitlines())
                  for p in files]
        print(needle, sum(n > 0 for n in counts), sum(counts))
```

This audit supports a three-recipe Neovim batch using the unchanged managed
AppImage interface. It supports separate review of stable WezTerm's exact
endpoint enrollment and nightly WezTerm's independent identity requirement. It
supports retaining the shared legacy/token/quota/alternate machinery until actual
remaining callers and installed-delivery obligations have been addressed.
