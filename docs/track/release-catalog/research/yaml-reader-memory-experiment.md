# Record-scoped YAML reader memory experiment — November 3, 2026

## Verdict

Record-scoped structural validation and private output spooling preserve the
reader contract, but **portable constant process memory was not demonstrated**.
BusyBox memory still grows substantially on the large fixture. Do not integrate
the research branch unchanged or remove consumer file limits based on this work.

Source: `research/yaml-reader-memory` at `ae1f216b4ce54a730ea38a12aa5c53d822b10d84`,
directory `tools/catalog-yaml-prototype/`. This branch descends from the published
reader prototype; it remains local and separate from main. The disposable worktree
is `/tmp/am-yaml-reader-memory`. Commit `87828c1ca` captures the experiment and
results; the following commit corrects commentary about the observed limit.

## What changed and passed

The parser checks required fields and nonempty-map rules when a record closes,
projects any requested row, and deletes that record's stored facts. Strict sibling
ordering detects repeated/out-of-order IDs without retaining all prior IDs.
App entries and whole-document ID lists are also discarded. Root relationships
are checked at EOF. A single read feeds a private output spool; the shell copies
it only after parser success. A malformed suffix therefore suppresses already
projected rows and scalar values without a second read of the input.

Nine acceptance groups pass on mawk, GNU awk and BusyBox awk. The original eight
groups cover independent YAML parsing, 46 malformed variants, strings/Unicode,
exact large IDs, query status distinctions and client selection. The extra group
checks missing required fields and repeated IDs at record boundaries, malformed
suffix suppression for both projections and enumeration/scalar queries, and
rejection of scalar lookup on a map. Shell syntax, shellcheck and whitespace
checks pass. A BusyBox regex spelling incompatibility was found and corrected.

## Measurements

Run `python3 tools/catalog-yaml-prototype/memory.py` in the research worktree.
The script runs one child at a time, generates bounded synthetic files, verifies
query status and row counts, and records `/usr/bin/time` peak RSS and elapsed time
for the shell reader process chain. These are single local observations, not a
proven worst-case allocation bound or Actions-runner measurements. The roughly
8 MiB floor includes wrapper/utility process costs and measurement effects.

The final fixed-slot variant uses these results:

| Interpreter | 100 releases / 800 assets | 1,000 / 8,000 | 10,000 / 80,000 | Large-case seconds |
| --- | ---: | ---: | ---: | ---: |
| mawk | 8,000 KiB | 7,872 KiB | 7,840 KiB | 10.33 |
| GNU awk | 7,960 KiB | 7,868 KiB | 7,840 KiB | 21.56 |
| BusyBox awk | 7,892 KiB | 7,932 KiB | 54,360 KiB | 58.98 |

The input sizes are 163,833; 1,637,134; and 16,379,135 bytes. The largest release
projection is 338,894 output bytes. A single release with 8,000 assets (1,439,355
input bytes) stayed at 7,804–8,092 KiB; 10,000 app aliases (180,138 bytes) stayed
at 7,844–8,040 KiB. These shapes establish useful counterexamples and feasibility,
not the cost of maximum-length strings or arbitrary projections.

The initial variant used full paths as array keys and discarded records. Its
exploratory results also showed BusyBox growth: 54,104 KiB at the largest fixture,
versus 7,940/7,992 KiB on mawk/GNU awk. Replacing paths with fixed reusable storage
slots **did not fix BusyBox RSS** and approximately doubled large-fixture runtime.
Those earlier observations are retained as `memory-results-path-keys.json`;
`memory-results.json` belongs to the committed fixed-slot variant. No interpreter
allocator cause was established. Prefer the simpler record-scoped design when
building a production candidate; fixed-slot rewriting has no measured benefit.

## Recommendation and limits

Replace whole-document storage with record-scoped validation, but retain an
explicit measured file ceiling for every supported interpreter. Private output
spooling is a feasible way to retain full-document refusal with one input pass;
its disk budget grows with projected output. A two-pass parser is an alternative
only over an immutable private input and still needs a validator with measured
memory use. Merely adding a second pass does not address the observed BusyBox
allocation behavior.

The proposed 16 MiB production trial file ceiling is close to the large fixture
but is **not yet a demonstrated worst-case memory/CPU budget**. Keep the existing
32 MiB/64 KiB prototype guards classified as experiment bounds. Before adopting
budgets, test maximum-length scalars, maximum projected row sizes/column counts,
file/line boundaries, write failures, temporary-space exhaustion and actual
bounded acquisition. None is established by normal-fixture success.

Production collector, reader, recipes, workflows, daily source pin and installed
files remain unchanged. No push or natural-run acceptance is part of this work.
See [candidate strategy and collection ceilings](yaml-resource-strategy.md).
