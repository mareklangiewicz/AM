# Use upstream template sources and family naming

Type: task
Status: resolved
Triage: ready-for-agent

Marek requested removing the app-specific template name and reusing upstream's
own template/generator guidance where possible, avoiding a second maintained
recipe body. Rename the family, pin the actual upstream template that produces
the supported fixtures, and use that unmodified source. Record generator
substitutions and provenance, verify byte-exact behavior, and explain how newer
upstream templates are reviewed. Do not silently treat legacy and current
upstream layouts as equivalent. No runtime, conversion or collection changes.

## Answer

Renamed the family to `github-appimage-3.5`; the former app-specific identity is
no longer accepted. Obsidian is a fixture/example, with no app-specific rendering
or loading code.

Upstream already documents `am -t` in `docs/guides-and-tutorials/template.md`;
its generator in `modules/template.am` fills `templates/AM-SAMPLE-AppImage`.
The current cached upstream template is version 3.6 with different desktop
handling. Examining its history found that the unmodified template at
`bb53f3180ec92f862020f8bdccef0f6614015bae` reconstructs all five supported
fixtures exactly using upstream's default GitHub/x86_64 generator substitution.

Removed our derived `template.txt`. The source is now an unmodified pinned
upstream template in `tools/recipe-reconstruction/upstream/AM-SAMPLE-AppImage`,
plus the verbatim FUNCTION assignment excerpt from that same upstream generator.
Provenance records source commit/path/hash, generator full-file hash/excerpt line
and hash, and the separate fixture commit/hashes. A narrow inert-text adapter
performs upstream's literal substitutions; no shell or interactive generator runs.
The upstream files remain authoritative: snapshots must be copied from reviewed
upstream revisions, not edited as independently maintained fork templates.

Added `verify-upstream --repo PATH`: it verifies canonical snapshot bytes,
the complete generator hash, exact excerpt and five fixtures against the pinned
local Git objects. Real verification passes. Git is needed only for this explicit
verification operation; ordinary check/render remains offline standard-library
Python. Normal unit tests do not require historical Git objects.

All 14 focused tests pass in 1.234 seconds, including source integrity, upstream
snapshot verification/refusal, five original round trips and a repository whose
name resembles template placeholders. Real short Obsidian rendering still matches
its pinned upstream original with cmp. Whitespace checks pass. The README records
source verification/update procedure and the required separate review for newer
template/generator revisions. No claim of current-3.6 coverage or automatic import.
No runtime changes, recipe conversions, collection expansion, deployment or push.
