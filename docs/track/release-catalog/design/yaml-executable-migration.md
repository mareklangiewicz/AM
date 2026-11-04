# Explicit am-utils format-2 source candidate

Ticket 100; isolated prep/yaml-executable-migration, based on reviewed 7946f2167.
This is source preparation, not policy acceptance or operational migration.

## Scope and policy

All 356 enrolled executable recipe paths (178 x86_64 and 178 aarch64) declare
CATALOG_FORMAT=2 and their exact CATALOG_RECIPE. Actual source selector bodies
were checked against their four expected shapes before changing declarations.
The legacy selector remains available for explicit format-1 rollback/compatibility
rehearsal; format 2 never runs it or manufactures JSON for it.

The shared policy contains an explicit trusted list of the 178 names and two
architectures. Unknown names/architectures refuse before HTTP. The helper asks
that same policy to validate enrollment, avoiding a second shell allowlist. A
catalog apps mapping cannot silently enroll another recipe. These recipes also
require numeric repository identity 1225768109; an apps-map reassignment refuses.
No new runtime file, dependency or consumer watchdog is introduced.

URL eligibility uses ASCII case folding as the original LC_ALL=C grep -Eoi did:
`https.*download.*/ARCH-[0-9]{8}/COMPONENT_.*-ARCH-static$`. COMPONENT is the
literal app name, except the already reviewed c++filt spelling c%2B%2Bfilt.
Return the original decoded URL, preserving percent spelling and URL identity.
The eight digits are a shape constraint, not calendar validation. A matching
asset URL is eligible independently of tag/prerelease; continuous-tag records
are excluded only when their asset URL lacks the dated path. Asset names do not
establish URL eligibility. ld.bfd's dot is now literal: this intentionally
rejects an ldXbfd URL which the interpolated legacy ERE could match.

Ordering follows the existing cohort proposal: descending published_at and
numeric release ID, then UTF-8 asset-name bytes and ascending numeric asset ID.
Fall through releases with no matching asset; judge freshness only after
selection using the release's effective observation. Retained older records
remain eligible. Page/asset ordering, retained coverage, and ignoring JSON
non-asset strings are deliberate differences, not equivalence guarantees.

## Reproducible saved evidence

`python3 tools/catalog-yaml-prototype/am_utils_cohort.py` checks the saved body
against its retained report's byte length and SHA256, normalizes it through the
retained-observation adapter, validates the complete YAML candidate and projects
asset facts with the shared shell reader. It compares every current recipe's
strictly checked legacy selector to the Python reference and mawk/GNU awk/BusyBox
awk policy results. The Python reference uses the frozen static inventory as
independent enrollment evidence; tests check agreement with the runtime list.
No installer or acquired binary executes during this comparison.

The saved numeric list response contains six releases and 1750 assets, observed
October 28, 2026. Its original raw body exceeds 2 MiB; that is a saved collector
input, not an excuse to raise the client's normalized YAML cap. The audit records
normalized repository bytes separately. No live/current upstream, 100-release
capacity or retained-growth guarantee follows from this sample.

Disposable manager tests exercise real executable recipe installs, standalone
updates, encoded pluses, both architectures, module refusal, selected-release
waiver, and batch reuse of one repository. Adversarial policy checks cover literal
dot matching, date/architecture/channel shapes and deterministic asset ties on
three awk implementations. A separate explicit installed-recipe replacement
rehearsal checks refusal before replacement, unchanged binary/URL on a same-URL
update, and exact recipe-byte restoration. It is not a production migrator.

361 of 475 enrolled source paths now opt into format 2 in this candidate;
114 AppImage paths remain. All counts concern source preparation, not installed
hosts or published catalogs. No candidate is merged into main.
