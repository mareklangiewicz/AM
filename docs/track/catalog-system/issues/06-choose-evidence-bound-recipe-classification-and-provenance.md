# Choose evidence-bound recipe classification and provenance

Type: grilling
Label: wayfinder:grilling
Status: claimed
Assignee: codex-provenance
Blocked by: 01, 03

## Question

What evidence and revision/path bindings justify public recipe classification and
installation-review links, including architecture variants and catalog-only apps?

Compare “shared/declarative installer”, “custom recipe” and “not yet classified”
against actual declarations, reconstruction evidence and transitional recipes.
An unmatched recognizer is not proof of custom behavior. A shared installer is
not proof of binary authenticity; a custom recipe is not an accusation.
Separate source recipe execution, installed generated updater behavior, inferred
asset matches, known AM selections and absence of installation support.

Specify precise evidence predicates, provenance age/revalidation, unknown states,
source revision and architecture/path mapping, review-link targets, and behavior
when recipe/catalog revisions diverge or a file moves/disappears. Metadata
collection must not execute recipes or downloaded app payloads.
Use real examples and obtain Marek's terminology/contract decision. Link new
settled domain terms to the glossary only if they are genuinely new concepts.

## Comments

### Prepared terminology and contract proposal — November 8, 2026

Pending Marek's decision, not an accepted schema or classification of all recipes.
The storage prerequisite is resolved; this ticket owns recipe evidence, distinct
from the independently claimed browser layout review.

#### Factual examples

Read-only source inspection at `4d8f799e5f5154f3728db8ca76fd900d3a058f80`
provides these examples. Classifier observations are inert local text analysis,
not recipe execution, runtime compatibility tests or current upstream claims.

| Example | Evidence | Consequence |
| --- | --- | --- |
| `x86_64/20x` | `programs/x86_64/20x`, blob `32ba9d40149183858d736124b5d7e04b426d103c`, declares numeric source 1152028865 and invokes `modules/appimage.am`; ticket 130 records conversion evidence. The original-template classifier reports `unmatched` for this shared wrapper. | Template nonrecognition cannot establish custom behavior. |
| `ageha-editor` | Catalog-only enrollment in `tools/catalog-collector/collection-apps.json` (numeric source 1016549971), absent from `collection-recipes.txt`, yet `programs/x86_64/ageha-editor` exists (blob `cb62f00f8a2b4e25cbc9cf95d62306dbfa26fba0`) and matches a pinned original template. Historical conversion evidence records an absolute-icon-link exclusion. | Catalog-only enrollment does not establish absence of an AM recipe or successful shared-installer migration. |
| `x86_64/actual` | `programs/x86_64/actual`, blob `5ab5a65d0019add100627b920920825f302ba478`, is an `instance` of `bb53f3180ec92f862020f8bdccef0f6614015bae:templates/AM-SAMPLE-AppImage`; runtime compatibility is `unassessed`. | Positive template accounting differs from using the maintained shared installer or having validated runtime compatibility. |

`tools/recipe-reconstruction/README.md` defines the inert classifier's limits.
`recipe_declarations.py` extracts literal bindings/settings but does not validate
the complete executable wrapper tail. Its success alone is insufficient proof
that a recipe exclusively invokes shared installation. The narrower reconstruction
short-reader checks an exact tail but does not cover every architecture/declaration
shape. Reuse these checks within their scope; do not promote either into a
universal classifier. Missing architecture paths remain missing: an x86_64
recipe does not establish an aarch64 recipe. Stable/nightly app identities retain
separate selection policies even when they share source facts.

#### Recommended public classification

Use four understandable states, with positive evidence for each known state:

- **Shared installer**: the complete recipe matches a supported literal declaration
  and allowlisted wrapper, including its whole executable tail; bind the relevant
  shared module/policy revisions. Extra unaccounted shell prevents this verdict.
- **Template-based recipe**: complete pinned-original reconstruction with accepted
  literal/default parameters (`instance`), preserving template identity/hash.
  This describes source structure, not shared-runtime use or runtime equivalence.
- **Custom recipe**: an explicit reviewed classification bound to exact recipe bytes
  and describing the custom portion. No inference from `unmatched`, file size,
  failed declaration parsing or an unresolved FUNCTION slot.
- **Not yet classified**: missing, unsupported, ambiguous or insufficient evidence,
  including `parameter_review` without a separate reviewed classification.

Catalog enrollment and known recipe availability are separate facts. A known
recipe may receive a review link even while its classification is unknown;
classification does not establish a current valid catalog selection. Keep AM
selection/support evidence separate from inferred platform matches. These labels
assess neither binary authenticity nor maliciousness and say nothing about the
visitor's installed updater. Source metadata collection executes no recipes or
app payloads.

#### Recommended revision and review-link contract

Bind every assertion to AM app identity, architecture, exact recipe repository/
commit/path and blob identity, classification-rule revision and evidence inputs.
Shared-module and policy pins are distinct inputs; template evidence names the
original template commit/path/hash. Keep evidence evaluation time separate from
release observations. No arbitrary age expiry: the assertion remains about its
pinned bytes, not whatever is currently at a moving branch.

Reuse classifications only while their recipe and relevant rule/dependency inputs
remain identical. Recheck affected assertions when those inputs change; otherwise
publish unknown for the new binding, never silently carry a verdict onto changed
bytes. An old snapshot retains its historical verdict and exact review links.
Record missing evidence explicitly rather than guessing. No full recipe-body
classification rerun just because release observations changed.

Review links target the recipe's own immutable revision and architecture path,
with shared/template evidence available as detail. A recipe revision need not equal
the catalog commit: the catalog descriptor pins those distinct inputs. Explain
that revision context rather than constructing a recipe URL at the catalog ref.
Join recipe/source facts only through verified numeric identities and explicit
app/architecture policy bindings. If a binding cannot be established, keep facts
browsable and leave installation selection/support unknown.

An explicitly checked absence may be shown as no recipe at that revision/path;
transport failure is unknown, not absence. A rename is a new binding at a new
revision; never retarget historical links to a same-named file at HEAD. A failed
review-link fetch does not erase a valid pinned classification or prove the recipe
never existed. Custom recipes get the required prominent review link; unknown
recipes with known paths remain reviewable. Wire fields and executable predicates
follow after the terminology/contract decision, with focused fixtures covering
these examples and divergence cases.

#### Decision to take

Accept the four labels and revision contract together, or simplify the public
labels while retaining these evidence distinctions in detail. The recommendation
is four labels: collapsing known legacy templates into either shared or custom
would misdescribe existing recipes. This is the material product/contract choice;
routine validator and fixture mechanics do not need individual approval rounds.
