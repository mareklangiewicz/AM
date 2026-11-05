# Read original templates and recognize recipe instances across upstream families

Type: task
Status: resolved
Triage: ready-for-agent

Marek requested reading pinned Git originals instead of copies, discovering all
upstream templates to identify custom logic, and using the tool to simplify
migration preparation/tests. Remove vendored templates/generator excerpts;
discover templates from recorded source revisions. Keep matching conservative:
arbitrary shell inside template parameters is still custom/unreviewed logic,
and a nonmatch alone is not proof of custom behavior. Integrate a reusable
migration inventory and template-driven test cases without changing deployed
recipes, selection policy or collection enrollment. Record actual coverage and
limitations with offline validation. Commit source work locally.

## Answer

Implemented as `f691b7fb5`. All original template, generator and recipe fixture
bodies now come directly from pinned Git objects; removed seven tracked copies.
Git object availability is an explicit requirement, with no fallback copy or
automatic fetch. The legacy short-declaration renderer and its real-app round
trips remain supported against the same originals.

`Catalogue` discovers every `templates/` file at selected revisions, with no
per-app loading code. Default pins discover all 15 originals at `bbffd15c1`
and 10 historical originals at `bb53f3180`. `classify` checks every layout,
`expand` reconstructs extracted parameters, `templates` exposes provenance and
markers, and `inventory` streams a pinned recipe tree into JSONL migration
evidence or a compact `--summary`. Migration actions distinguish runtime-policy
review, parameter-logic inspection and unmatched-source inspection. The catalog
tools README now points migration preparation to this shared interface.

Conservative matching accounts for the complete file and exact physical lines.
Parameters cannot absorb added lines. App markers must agree; standard simple
installer/updater site and FUNCTION differences require review. Arbitrary shell
in FUNCTION is not approved merely because it fits a template slot: known
original generator defaults and conservative literals give `instance`; other
parameters give `parameter_review`. Nonmatches give `unmatched` and an optional
nearest unexpanded-template diff, not a claim of proven custom logic. All
outcomes leave runtime compatibility unassessed.

Used the inventory on the pinned upstream x86_64 tree: 9,234 recipes, of which
2,080 are standard instances, 5,124 fit layouts with parameters requiring review,
and 2,030 match no known layout. [Durable summary](../research/upstream-template-inventory.json)
records pins, family counts, examples, reproduction command and the hash/location
of ephemeral full JSONL evidence. Counts are preparation evidence, not converted
apps. Selection rules/repository IDs and installed behavior still need their
existing separate review.

Tests are now driven by originals: one shared contract generates an instance for
every discovered template, round-trips extraction/rendering and rejects added
commands. Shared adversarial checks cover FUNCTION code, nonliteral data,
repeated app identity, missing Git objects, malformed expansions and migration
inventory/CLI behavior. All 24 focused tests passed in 4.069 seconds; final
whitespace checks passed. Initial example cases exposed an unlisted upstream
DOMAIN/REPOSITORY marker and a Firefox fixture mutation that did not change its
input; both were corrected before the final passing run. No unrelated catalog
or container suite rerun is claimed.

Limits: marker vocabulary covers the inspected revisions, not arbitrary future
template syntaxes. Defaults embedded differently from the inspected generator
remain parameter review. Formatting edits and other historical template revisions
can produce nonmatches; recipes with already-short fork declarations are not
upstream template instances. Source-only archives/shallow clones lacking the
pins must obtain them explicitly. No broad conversion, runtime/deployment,
collection/publication, push or yadm operation occurred.
