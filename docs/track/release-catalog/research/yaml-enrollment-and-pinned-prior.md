# Real YAML enrollment and pinned previous state — November 4, 2026

[90](../issues/90-wire-yaml-enrollment-and-pinned-prior.md), source candidate
`d422860de` on `prep/yaml-offline-publication`.

`yaml_enrollment.py` derives actual app names from marked shared AM recipes and
exact aliases in the reviewed staged manifest. It statically reads APP and
CATALOG_ALIAS, never evaluating shell. Architecture paths coalesce into one app
name; conflicting numeric identities across architectures are refused. The
returned review report records manifest hash, source revision, enrolled recipe
hashes and excluded paths; only apps/repository YAML enters a candidate tree.

Current scope is 255 app names / 475 recipe paths / 49 numeric repositories from
the 52-endpoint manifest. Another 987 marked shared recipe paths lie outside this
manifest and are explicitly excluded. Forty-eight enrolled repositories have
marked recipe app names; wez/wezterm's numeric source remains enrolled without an
app entry because its current recipe is unmarked legacy code. This does not
expand enrollment to the separately prepared larger/sharded batch.
Readable bootstrap owner/name values come from reviewed manifest aliases, not a
new upstream canonical-name check. No placeholder source-ID app aliases remain.

Recipe inputs match the recipe state at `2f9292218e2d23f483d385361902ba60b4afd70c`.
Manifest SHA-256:
`8d9eb1ec29b5e9a28e940e9a898cef20dcdf8246a57820e7ceb328ff8378e265`.
Canonical enrolled recipe-row list SHA-256 (json.dumps with sort_keys=True,
separators=(',', ':')):
`1d4428de508d5dc8eb544cc17040e053852da2f4b4272843ad19859962dad81a`.
Runtime callers remain responsible for supplying recipes from their reviewed
checkout; the module does not establish workflow provenance.

`prepare_pinned` loads previous format-2 state at an exact commit, preserves
existing apps/repositories, adds current enrollment and rejects app reassignment.
Absence from the current inputs does not infer retirement. `collect_pinned`
passes that state into scoped collection and returns the previous publication pin
with its report. Neither updates a ref. A later publication step must validate
and compare-and-swap against that exact pin. No format-1 snapshot conversion or
remote loading is implicit.

Explicit commit=None starts bootstrap. New identities have no fabricated
collection or observation metadata before acquisition. Actually attempted failure
can be represented with failed collection metadata and no last-success/releases.
If any new identity remains unattempted, IncompleteBootstrap refuses the entire
candidate and carries an aggregate .report, including unattempted bootstrap IDs.
A caller can retain diagnostics and retry without publishing placeholder times.
Existing pinned sources may remain unattempted unchanged. New enrollment can
therefore require attempts even when an ordinary refresh would select a subset.

Nine enrollment/pinned checks pass: actual scope/counts, complete 49-source
bootstrap using synthetic empty responses, incomplete-bootstrap refusal/report,
honest attempted failure, unselected byte preservation, exact pin despite a moved
tip and retained old aliases, cross-architecture/nonstatic refusals, prior alias
reassignment refusal, and real saved-response bootstrap/refresh. The latter uses
release-07's hash-checked 334,543-byte response (61 releases/122 assets), mapped
to blender-alpha/blender-beta/blender-rc. It preserves original receipt time,
checks release IDs/tags and asset IDs/names independently against saved JSON, and
returns identical YAML on pinned replay without moving the ref. The scripted
request adds explicit page=1 to the recorded per_page=100 endpoint; this is an
offline equivalent first-page replay, not new request/framing evidence. The
original anonymous quota headers trigger the existing quota-reserve stop after
this completed one-source scope; no subsequent acquisition occurs.

Nineteen adapter checks and six attempt-adapter checks also pass: 34 total relevant
executions. Python compilation and whitespace checks pass. The full real
49-source default acquisition/capacity remains unmeasured; empty fake bodies are
not capacity evidence. Test file allowances remain provisional.

Next: accepted production budget choices and reviewed workflow/artifact staging,
including actual trusted source revision/context and publication wiring. Shared
YAML components remain under catalog-yaml-prototype. No live request, workflow
edit/dispatch, remote catalog publication, daily repin, installed change,
natural-run inspection or yadm pointer operation occurred. Source pushes are
separately authorized.
