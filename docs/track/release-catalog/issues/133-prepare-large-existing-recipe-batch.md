# Prepare a large existing-recipe batch

Type: task
Status: claimed
Triage: ready-for-agent

Marek requested “do big batch” on November 6 after the completed 20x/2fac
pilot. Scope: select twenty existing, unchanged, whole-template AppImage recipes
from the pinned recognition inventory; verify provenance, upstream identity,
selector policy and static payload desktop/icon compatibility; convert locally
only those passing all gates and regenerate declarations. Record exclusions
explicitly rather than relaxing gates to meet the target. Local source work is
authorized. Collection enrollment, pushes, publication, installed changes and
live deployment remain separate. No application payload is executed.

Use primary Git objects and first-party release API facts. Preserve compact
hash-checked evidence and exact source/asset identities. Prefer direct AppImage
assets and narrow observed-name patterns; preserve original desktop argument
stripping explicitly. Assess runtime differences against the completed pilot
and shared contract, including inert lifecycle checks. Existing custom/fork
recipes, missing upstreams and ambiguous payloads are excluded from conversion.
