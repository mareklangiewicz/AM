# Maintain bounded upstream recipe reconstruction

Type: task
Status: open
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
