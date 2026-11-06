# Recognize the generator-derived archive AppImage selector

Type: task
Status: resolved
Triage: ready-for-agent

Continue 124: recognize only the exact inspected AIA/default-keyword selector
variant in the original archive-capable AppImage template. Bind the extension
to inspected generator/template hashes. Require repeated installer/updater sites
and FUNCTION values to agree in that layout. Preserve unknown shell, ordering,
filters and endpoint differences as review. Test public classification/expansion
against pinned real recipes and adversarial cases, then regenerate inventory.
No recipe conversion, enrollment or live deployment. Runtime assessment of the
three preparation candidates remains separate.

## Answer

The existing classifier now derives the exact GitHub AIA/default-keyword form
from the original generic FUNCTION assignment, only when both inspected original
template and generator hashes match. No copied upstream body, shell evaluation,
new CLI or application-specific template was added. Changed originals and other
endpoints/filter/order variants stay in review. The archive-capable AppImage
layout now reports repeated site/FUNCTION disagreements too.

All 28 focused tests pass (4.240 seconds), including three pinned candidates,
extra shell, changed endpoint/filter/order, nonliteral site, mismatched repeated
sites, individually approved but differing commands, changed original hashes,
and real pyuploadtool disagreement. The existing every-original contract still
covers all discovered templates. This is a scoped offline suite, not a complete
catalog/container/runtime validation.

[Fresh inventory](../research/default-appimage-selector-inventory.json): 9,234
recipes, 6,517 instances, 687 parameter-review, 2,030 unmatched. Compared with
123's hash-verified inventory, exactly 4,437 recipes changed from review to
instance; no other status changed. All changed recipes share the same exact
normalized selector and agree on repeated sites/FUNCTION values. All 4,437
source hashes and template expansions were checked against the pinned Git tree.
The historical inventory/report is retained as evidence at its original tool
revision, not overwritten.

Runtime compatibility remains unassessed. Next bounded work is independent
offline selection/install/updater assessment for 20x, 2fac and 4nier-patrimonio,
using 124's gates before conversion. No recipe, runtime, collection, installed
file, publication or yadm change was made.
