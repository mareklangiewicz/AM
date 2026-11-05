# Maintain bounded upstream recipe reconstruction

Type: task
Status: resolved
Triage: ready-for-agent

## Scope from experiment 120

Use [the experiment's evidence](../research/upstream-recipe-reconstruction.md)
to implement a maintained source-only tool for the single pinned GitHub
AppImage family. Support whole-recipe recognition, explicit declaration rendering
and a useful unmatched-content diff. Return distinct machine-readable outcomes
for exact matches, review candidates and unsupported inputs, with documented
exit codes. Never execute recipes or silently normalize meaningful source text.

Keep template identity, upstream commit/path and source hashes in maintenance
metadata. Map APP and CATALOG_REPOSITORY from our literal short declaration to
the renderer without accepting arbitrary shell assignments or updater fragments
as template parameters. Reject unknown template identity and inconsistent repeated
parameters. Do not replace the maintained runtime or invent a second installer.

Validate with pinned real fixtures, byte-exact render/check round trips and
custom installer/updater steps, parameter drift, template changes and unsupported
literal input. Add focused maintained checks rather than retaining the throwaway
HTML or prototype implementation wholesale. Document a concrete incoming-update
example, separating parameter changes from template review.

Document the supported family's compatibility decisions against our selector and
installer before recommending any conversion. Recognition alone must never
label a recipe behaviorally equivalent or automatically safe to shorten.
Keep unrecognized recipes intact. No mass conversion, collection expansion,
publication, installed changes or deployment belongs to this ticket.

## Answer

Implemented the maintained Python standard-library tool in
[`tools/recipe-reconstruction`](../../../../tools/recipe-reconstruction/README.md).
It checks complete upstream input against the pinned version-3.5 x86_64 AppImage
template and renders it from explicit JSON declarations or current literal short
recipes. Template identity and source/template/fixture hashes are maintenance
metadata. The complete source is compared without normalization; extra updater
steps and inconsistent repeated parameters produce a review diff.

Documented JSON outcomes and exit codes: exact 0, review 1, unsupported 2, error 3.
The tool never evaluates shell, performs network operations or writes recipe
files itself. Literal short-header parsing refuses unknown/duplicate assignments,
extra commands and other package layouts/architecture identities. Every exact
or candidate report says compatibility is unassessed; the README records the
separate conversion gates and a concrete incoming-update example.

Validation: 11 focused unittest cases pass in 1.163 seconds, including five real
fixture hashes and byte-exact round trips, custom installer/updater commands,
parameter drift, template/newline changes, malformed/oversized/non-UTF-8 inputs,
short-recipe refusals, provenance integrity and CLI output/exit contracts.
An additional real CLI render from current short Obsidian matched its pinned
upstream original with cmp and checked exact. Staged whitespace checks pass.
The unrelated catalog/container suites were not rerun for this isolated tool.

Source-only: no recipe conversion, enrollment, publication, installed refresh,
runtime change or deployment. The throwaway prototype remains on its separate
branch and is not a dependency. Implementation committed as `9ce557fa1`.

Follow-up [122](122-use-upstream-template-sources.md) supersedes the app-derived
template body/name with canonical pinned upstream template/generator sources,
family identity `github-appimage-3.5` and explicit upstream-source verification.
