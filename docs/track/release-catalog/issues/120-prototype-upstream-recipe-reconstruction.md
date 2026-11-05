# Prototype upstream recipe recognition and reconstruction

Type: prototype
Status: resolved
Triage: ready-for-agent

## Request and purpose

Marek proposed a tool that expands our short recipe into the corresponding
upstream AM recipe, allowing comparison with incoming upstream additions and
updates. Start with this experiment before broad recipe conversion. Determine
whether a standard recipe can be shortened without overlooking custom code,
and whether later upstream changes can be reviewed with less repeated work.

## Scope

Choose one actual upstream GitHub AppImage recipe template and a small handful
of matching recipes. Pin the upstream commit and record all fixture provenance.
Recognize the complete template, extract its literal parameters, represent them
as a short declaration, and reconstruct the upstream recipe for comparison.
The experiment may retain upstream template identity/provenance in maintenance
metadata; do not burden installed recipes with it unless evidence requires that.

Use exact reconstruction first, with only explicitly justified normalization
(for example line endings). Do not broadly strip comments or whitespace: shell
quoting and heredocs can make them meaningful. Never execute incoming recipes to
recognize them. Any unexplained content must refuse automatic conversion and
produce a useful diff or diagnostic. A near match remains a review candidate.

Keep the interface small: recognize/reconstruct/check a recipe against a pinned
template. Avoid a general shell equivalence engine or a second maintained copy
of our installer. Investigate whether the existing short declaration contains
enough information; record missing upstream parameters rather than guessing.

## Acceptance evidence

- Reconstruct a handful of real matching recipes and compare their complete
  contents against the pinned originals; record supported variation explicitly.
- Reject a matching recipe with an added custom command, including a custom
  updater step. Explain the unmatched content without silently dropping it.
- Demonstrate an ordinary parameter change and an upstream template change:
  distinguish a declaration update from a shared-template review requirement.
- Separate template recognition from runtime behavioral compatibility. Matching
  upstream reconstruction establishes that all original code is accounted for;
  it does not prove our catalog selection/shared installer behaves identically.
  Record relevant intentional differences and any unsupported behavior before
  recommending a family for conversion.
- Report the maintenance cost and a concrete go/no-go recommendation for a
  maintained tool. Keep the experiment small; do not expand into batch conversion.

## Constraints and follow-up

No collection enrollment, publication, installed refresh, deployment or mass
recipe rewrite. Collection expansion and recipe conversion remain separate.
After the experiment, scope any maintained implementation and conversion work
from its evidence. No date for all-app catalog coverage is established here.

## Comments

November 5, 2026: Marek approved recording this direction in the tracker first.
Implementation has not started.

November 5, 2026: claimed for the pinned-template reconstruction experiment.

## Answer

Five real recipes reconstruct byte-for-byte using one complete upstream template
and literal app/repository values; eight scenarios demonstrate parameter updates
and refusals for custom steps, updater drift and template changes. Proceed with
a small maintained tool, keeping runtime compatibility as a separate gate.
[Report](../research/upstream-recipe-reconstruction.md) records provenance,
validation, limitations and compatibility differences. Prototype preserved on
`prototype/120-upstream-reconstruction` at `69c76db1f`, outside main-marek.
[121](121-maintain-upstream-recipe-reconstruction.md) scopes maintained work.
No runtime changes, conversion, enrollment, publication or deployment occurred.
