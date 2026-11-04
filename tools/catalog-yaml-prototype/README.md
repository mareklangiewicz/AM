# Retained-observation schema revision (local experiment)

Current branch: `research/yaml-observation-default`. This supersedes this
README's older full-history/check-time examples. No production collector,
workflow, recipe, installed helper or remote control is changed.

Run `python3 tools/catalog-yaml-prototype/retention_matrix.py` for all 16 unique
acceptance groups on mawk, GNU awk and BusyBox awk. The generated
`retention-results.json` records results. `retention.py` is a fixture-driven
per-source transition model with subset selection, page size/limit inputs,
explicit trial budgets and optional all-only reconciliation; it makes no network
calls. Shared fixture budgets account requests/bytes/time across sources and
report untouched unattempted sources; this is not actual transport/deadline
enforcement, fair runner scheduling or a production normalizer.

The reader validates `collection`, `last_success`, required repository `observed_at`
and optional per-release overrides, requested-scope completion and effective
timestamp relationships. Release `get`/`rows observed_at` resolve the default. The
example repository uses that revised schema. Model fixtures prove partial
retention, fetched-record replacement (including omitted optional fields/assets),
untouched observation times, per-page response times, failure rollback, default
all-source selection, empty subsets and source/parameter rejection. Selected
stable releases remain available but can be stale despite a recent collection.

Reconciliation defaults false. With explicit `page_limit=all` and reconciliation
true, success replaces the retained ID set with fetched IDs; failure preserves
all prior observations. A finite scope with reconciliation is rejected before
work. This is an explicit local design policy, not a deployed deletion mechanism.

`memory.py` uses the revised fixture builder if rerun. The existing
`memory-results*.json` files are historical measurements of the previous schema;
they do not measure this revision or establish memory/CPU ceilings. BusyBox's
previous large-fixture RSS growth remains unresolved. The 32 MiB file / 64 KiB
line guards are still experiment bounds, independent of requested page count.

## Shared observation default — November 4

Repository `observed_at` supplies the shared default. The writer chooses final
page receipt, materializes old implicit observations for untouched releases, and
omits release overrides equal to the new default. Failed collections preserve
the old default and stored observations exactly. Earlier page receipt times are
explicit overrides when different. This changes representation, not freshness.

Run `default_matrix.py`, `retention_matrix.py` and `bounded_matrix.py` in this
directory for 29 unique groups (nine reader, seven retention, six adapter, seven
default groups) on each of mawk/GNU awk/BusyBox awk. Examples validate against the
revised reader. All matrices use independent YAML parsing in the test harness.

Run `python3 tools/catalog-yaml-prototype/history.py` from the repository root
for paired 32-snapshot temporary Git histories. It independently checks effective
facts, then measures snapshot bytes, line churn and packed Git objects/indexes.
No remotes, credentials or network calls are involved. Results are synthetic,
with fixed Git packing options; they are not live-catalog storage forecasts.
The replay has 384 MiB address-space and 128 MiB per-file guards, inherited by Git.

`growth-results.json` and `growth-pilot-results.json` are historical measurements
at `ccd0273e4`, before shared defaults; their measured reader timings must not be
attributed to this encoding. `growth.py` uses the current fixture/schema if rerun.

---

The following is preserved background from the earlier reader experiments.

# THROWAWAY YAML reader experiment

Question: can AM's proposed YAML subset support small POSIX shell/awk structure
validation, ID iteration and lossless scalar lookup without a YAML dependency?
This is research code, not a production reader. It makes no network calls.

Run from the repository root (Python plus PyYAML required for the independent
reference-parser experiment, not for the shell reader):

```sh
python3 tools/catalog-yaml-prototype/experiment.py
```

Reader examples:

```sh
sh tools/catalog-yaml-prototype/reader.sh validate repository.yaml
sh tools/catalog-yaml-prototype/reader.sh releases repository.yaml
sh tools/catalog-yaml-prototype/reader.sh assets repository.yaml 456
sh tools/catalog-yaml-prototype/reader.sh get repository.yaml releases 456 tag
sh tools/catalog-yaml-prototype/reader.sh apps apps.yaml
sh tools/catalog-yaml-prototype/reader.sh get apps.yaml apps obsidian
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases published_at prerelease
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases/456/assets name size digest
```

Exit status: 0 success, 2 invalid file/query/usage, 3 absent field or collection.
Scalar output is exact decoded bytes with no added newline. This preserves empty
strings, including trailing newlines; shell command substitution cannot preserve
trailing newlines, so use redirection when exact bytes matter. ID lists are LF
terminated. Validation completes before any result is emitted. Data is never
sourced, evaluated or used as an awk program.

Experimental bounds: 32 MiB/file, 64 KiB/line. These are local probe bounds, not
approved production collection budgets. Required fields, integer ranges and
fixed field order are a concrete trial of the schema, not deployed compatibility.

The original five-escape design cannot losslessly represent all Unicode line
breaks in YAML double-quoted text: NEL is folded, and spaces around Unicode line
separators can be folded. This branch **proposes** three additional standard YAML
escapes: `\N` (U+0085), `\L` (U+2028), `\P` (U+2029). They cost three fixed
decoder branches. Literal forms are rejected. This extension needs design
acceptance before production adoption. Other unsupported control characters
are deliberately unrepresentable; the eventual publisher must reject such an
observation rather than silently alter it.

UTF-8 validity is a publisher responsibility. The shell reader validates structure,
ASCII controls and the specific Unicode forms above, but does not implement a
general UTF-8 decoder. The Python experiment checks accepted fixtures against
PyYAML and compares decoded objects and scalar query bytes.

The parser stores paths and values, and each command scans the entire file.
Repeated one-field queries are unsuitable for large-history selection loops.
The experiment therefore adds `rows`: project requested scalar fields in one
validated scan. It writes ID then TAB-separated canonical YAML scalar tokens;
missing optional fields have an empty column, actual empty strings have `""`.
Escapes remain encoded, so tabs/newlines inside a name cannot break row framing.
This is ephemeral query output, not another published catalog representation.

For example, the client rule "newest published non-prerelease" is:

```sh
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases published_at prerelease > rows.tmp || exit
awk -F '\t' '$3=="false" && $2>newest {newest=$2; id=$1} END {if(id!="") print id; else exit 1}' rows.tmp
```

The conditional avoids using a shell pipeline that hides a reader failure.
Fixed quoted timestamps compare in chronological order. No version or asset
selection policy is built into the reader. Nothing here proves the complete new
collector/consumer system simpler or faster yet.

## Memory follow-up (isolated research/yaml-reader-memory branch)

Run `python3 tools/catalog-yaml-prototype/memory.py`. This runs the acceptance
corpus on mawk, GNU awk and BusyBox awk and writes `memory-results.json`.
The reader closes and validates records before discarding them; ID ordering
needs only the previous sibling ID. App entries are also discarded immediately.
Query output is spooled to a private temporary file and copied only after success.
No second input pass or whole-file result buffer is needed. Temporary disk use
therefore grows with query output. Output transport errors can still yield a
partial stdout stream; the caller must check status as before.

This experiment retains the original trial 32 MiB file and 64 KiB physical-line
caps. They remain experiment bounds, not accepted collection policy. Production
needs explicit projection-column/output bounds, temporary-storage failure tests,
a bounded transfer path and measured operational budgets. Validation alone emits
no data but currently still creates an empty spool. Synthetic record-count
measurements do not establish performance for maximum-length strings.

The resource result is mixed: mawk/GNU awk RSS stays roughly flat for the sampled
record shapes, but BusyBox reaches about 53 MiB at 10,000 releases/80,000 assets.
Fixed storage slots do not remove that growth and slow parsing; they are an
experiment, not a recommended optimization. Do not claim portable constant RSS.
`memory-results-path-keys.json` records the earlier exploratory variant; the main
`memory-results.json` matches the fixed-slot source in this branch. No allocator
or interpreter-level cause was established. Use measured file/resource ceilings,
or investigate another reader strategy before production integration.

## Hard offline worker follow-up

`worker.py` wraps the local JSON adapter with a POSIX fork supervisor. Run
`python3 tools/catalog-yaml-prototype/worker_matrix.py` for six process-limit
acceptance groups plus nine inherited reader groups on each awk implementation.
`collect_supervised` runs normalization/retained merge and result serialization
inside the child; only a complete JSON result from exit 0 is returned. A hard
worker refusal yields parent-built `collection_limit` metadata while preserving
prior facts, default, overrides and last-success metadata.

Trial defaults: 120 seconds elapsed, 384 MiB address space and 32 MiB per regular
file. These are configurable experimental inputs, not accepted operating budgets.
The parent sends SIGKILL at deadline (10 ms polling plus OS scheduling latency),
kills remaining members of the child's session and reaps its direct child. Child
stdout/stderr are discarded. A private result directory is removed on exit.
The process is trusted, single-threaded fork work; this is not a security sandbox.
Descendants deliberately escaping the session are outside the contract.

RLIMIT_AS limits virtual address space, not RSS; existing input/parent allocation,
parent result decoding, aggregate memory and aggregate temporary disk are not
bounded here. RLIMIT_FSIZE limits each regular file and output serialization;
it does not constrain the sum of files. Setup/I/O failures propagate without a
candidate. Failure status cannot distinguish OOM from arbitrary child faults;
no precise diagnosis is inferred. No network transport, live capacity measurement,
fair scheduler, production integration or reader resource ceiling follows.
