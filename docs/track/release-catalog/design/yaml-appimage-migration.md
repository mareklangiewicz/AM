# Remaining AppImage format-2 source candidate

Ticket 101, isolated prep/yaml-appimage-migration based on 7cfd1218f. This extends
source preparation to all 475 enrolled paths (114 here, following 361 already
prepared). It does not enroll the 987 marked paths outside the staged manifest,
change installed recipes, or promote/publish the candidate.

## Trusted selection policy

Each of the 114 paths declares CATALOG_FORMAT=2 and its exact CATALOG_RECIPE.
The existing shared awk policy owns an exact recipe-to-numeric-repository binding
and explicit URL predicates. Unknown recipes refuse before HTTP; a mapping to a
different numeric repository refuses before returning a selection. The JSON
policy inventory and compiler are development tools only; clients neither fetch
nor interpret them. The generated registry is checked against its trusted source.
The inventory preserves the original source hash and actual selector for review;
tests strip only the two added declarations to confirm exact source identity.

The policies translate each existing grep stage's URL regular expression,
inclusion/exclusion and ASCII case flag. BRE escaped alternation becomes ERE
alternation; bare BRE pipes remain literal. Case-sensitive DEV and continuous
filters remain case-sensitive. SQLite Browser requires its x86/64 AppImage URL
and numeric version directory, excluding nightly/continuous/dev/rc directories.
No universal suffix, architecture or tag rule replaces these filters. Asset
names only determine ordering; matching uses decoded asset URLs and returns the
original complete URL with its percent spelling intact.

Known suspicious pre-existing filters are preserved explicitly, not silently
repaired: aarch64/lapce asks for x86_64; armv7l/headlamp and armv7l/wekan exclude
armv7l; x86_64/opera and four Wine variants use literal pipe-separated architecture
text inside a BRE alternative. chatterino2-nightly has the same eligibility as
chatterino2; soil-editor has no soil-specific URL requirement. These are visible
policy debt, not proof that the resulting assets fit their labels.

## Replacement for /latest

After being asked about nine /latest paths, Marek clarified that he does not use
any of these apps and nobody else uses this fork. The candidate therefore makes
these explicit local choices without preserving GitHub's latest designation:

- PolyMC (x86_64/aarch64), SuperTuxKart (x86_64/aarch64/i686) and Vivaldi stable
  (x86_64/aarch64): newest published non-prerelease release with a matching URL.
- Vivaldi snapshot (x86_64/aarch64): newest published release with a matching
  snapshot URL, allowing prereleases. A stable gate would defeat channel intent.

List-based paths keep prereleases eligible, as their actual filters did. All
policies fall through releases without an eligible asset. Ordering is descending
published_at then numeric release ID, and UTF-8 asset-name bytes then ascending
numeric asset ID. Selected-release effective observation controls freshness;
fresher lower-priority matches do not rescue stale selections. Exact stale
consent and all existing private spooling/byte caps remain unchanged.

The generic reader's asset_facts projection appends prerelease as column eight;
the first seven columns retain their meaning. A stable policy refuses eligibility
unless that column is exactly false. The reader validates the whole repository
before exposing any candidate, as before.

## Observable changes and saved-data limits

Structured asset-only matching ignores matching strings in upstream descriptions.
It treats a decoded complete URL as a fact rather than splitting on JSON-text
punctuation. It does not reproduce raw JSON spelling, delimiter splitting or
substring extraction from a longer URL. Retained release coverage can exceed an
old page or /latest singleton. Published-time/ID and name/ID ordering differs
from upstream response order. These differences are proposals, not an equivalence
claim or operational acceptance.

appimage_cohort.py verifies saved body lengths/hashes before normalization and
full YAML validation, compares actual legacy selectors with Python, and compares
the complete selection tuple with mawk/GNU awk/BusyBox awk. List fixtures use
merge_attempts. Where only a saved /latest object exists (PolyMC and Vivaldi), it
normalizes that object's single release directly into a fixture, with incomplete
history; it never forges a list response or claims list-route acquisition. The
legacy /latest comparison uses the actual saved latest body even when a list
fixture also exists for that repository. No JSON is manufactured from YAML.

The saved sample yields eight different URL choices: Brave beta and nightly on
both architectures, DBFlux on both architectures, soil-editor and Wine Proton.
The results JSON preserves both URLs and selected IDs. Brave/DBFlux/Wine changes
follow published-time/ID release order; soil-editor follows asset-name order
rather than original response order. All other saved selections match. These
measured differences remain explicit policy changes, not corrected legacy bugs.
Saved pages are historical, never current upstream or 100-release/retained-growth
capacity evidence. The 2 MiB per-file trial cap is unchanged.

## Remaining migration work

The production installed-updater migrator is still only a contract/rehearsal in
yaml-installed-transition.md. Exact operational source pins, publication/ref
transition, stale UI acceptance, capacity acceptance and rollback after binary
updates remain separate. Candidate helpers still resolve release-catalog; source
coverage alone does not authorize switching that ref or deploying mixed clients.
No acquisition, workflow activation/dispatch, source/catalog push, repin, installed
host changes or yadm pointer operation is part of this increment.
