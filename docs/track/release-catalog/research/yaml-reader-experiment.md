# YAML reader experiment — November 3, 2026

## Verdict

Strict structure validation and useful fact queries fit in 31 lines of POSIX
shell plus 179 lines of POSIX awk, with no YAML runtime dependency. Keep consumer
validation rather than assuming well-formed input. This demonstrates feasibility,
not that the complete collector/consumer migration is already simpler or ready
to deploy.

The prototype is deliberately retained outside main on
`research/yaml-reader-prototype`, final commit `8a3e5c623` (initial experiment
`623eb55de`). Local worktree: `/tmp/am-yaml-reader-prototype`.
Files: `tools/catalog-yaml-prototype/{reader.sh,reader.awk,experiment.py,README.md}`
plus two example YAML documents. The committed branch is the portable source;
the temporary worktree is disposable. Main contains the design and findings only.

## What works

- Validate the complete file before any query output. Reject malformed suffixes,
  unknown/duplicate/out-of-order fields, wrong types, missing required facts,
  bad nesting, invalid timestamps, noncanonical integers and unsupported YAML.
- List release/asset IDs and app aliases. Get exact decoded scalar bytes,
  including Unicode, quotes, backslashes, tabs and trailing newlines.
- Distinguish missing (exit 3) from valid false, zero and empty strings (exit 0).
  Invalid data/query/usage returns 2, with no partial query output.
- Keep large IDs exact beyond awk's floating-point precision by decimal-text
  comparisons. Quoted app keys such as `on`, `null` and `123` remain strings in
  standard YAML parsers.
- Validate failed-with-retained-data, failed-before-first-observation, successful
  empty histories/assets, and empty app-map states.
- Perform a batch projection with one scan. A client awk rule chooses the newest
  published non-prerelease; no version selection is embedded in the reader.
- Never evaluate catalog contents as shell code or awk program text.

## Two discoveries

### Fixed extra escapes are needed for Unicode line breaks

The originally agreed string set does not safely represent all literal Unicode
line-break characters. Independent PyYAML round-trip checks exposed changed
values: U+0085 is folded to a space; U+2028/U+2029 can preserve themselves but
change adjacent whitespace. A deterministic 100-string corpus caught the latter
after ordinary Unicode fixtures passed.

The branch proposes standard YAML `\N`, `\L`, `\P` escapes for those three code
points, with literal forms forbidden. Three fixed decoder branches make both
the shell reader and standard YAML parser preserve the original values. This is
a proposed extension to the accepted five-escape grammar, not an unnoticed
production change. Unsupported other control characters must cause normalization
failure; there is no silent rewriting. General UTF-8 validation remains the
publisher's responsibility; the shell checks structure and selected forbidden
byte forms rather than implementing a Unicode decoder.

### Repeated scalar queries are not an efficient selection interface

Every query validates/scans the full file. Looping over 1,000 releases and starting
a new reader for each field would multiply the parse cost unnecessarily. The
demonstrated client need justified adding the originally deferred batch operation:

```sh
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases published_at prerelease > rows.tmp || exit
awk -F '\t' '$3=="false" && $2>newest {newest=$2; id=$1} END {if(id!="") print id; else exit 1}' rows.tmp
```

This emits ID plus requested canonical scalar tokens separated by tabs. Strings
retain YAML escapes, so embedded tab/newline values cannot corrupt framing. An
empty column means absent; `""` means actual empty string. This is transient query
output, not another distributed catalog format. Checking the reader before the
client awk avoids a pipeline hiding its failure.

## Verification and measured bounds

Run in the prototype worktree:

```sh
python3 tools/catalog-yaml-prototype/experiment.py
```

Python and PyYAML are development-only dependencies of the experiment. Eight
test groups pass under mawk, GNU awk and BusyBox awk, covering 46 malformed
variants, independent YAML object comparisons, 100 deterministic string
round-trips, scalar byte preservation, shell non-evaluation, large IDs and actual
client selection from projected fields. The shell wrapper passes `sh -n` and
shellcheck; whitespace checks pass.

Synthetic fixture: 1,000 releases, 8,000 assets, 1,637,134 YAML bytes. Each
projection emits 1,000 rows:

| Interpreter | Full validation | Validation + projection |
| --- | ---: | ---: |
| mawk | 0.558 s | 0.559 s |
| GNU awk | 0.873 s | 0.894 s |
| BusyBox awk | 3.077 s | 3.116 s |

Times are single local measurements including process/file overhead, not runner
benchmarks. A separate `/usr/bin/time` measurement of the final GNU awk validator
used 33,336 KiB peak RSS and 0.90 seconds on the same fixture. The straightforward
prototype stores paths, decoded values and encoded tokens; memory grows with
document size. Its trial 32 MiB/file and 64 KiB/line limits do not constitute a
production memory policy. Before deployment, choose tighter measured resource
budgets or reduce storage through streaming/two-pass validation. No claim is made
that very large histories fit the existing collector/reader limits.

## Next work and boundaries

The [schema draft](../../../catalog-format-v2.md) records exact trial fields,
ordering, types and state relationships. Accept or revise the three extra escapes
before production implementation. Then settle broader history/outlier budgets
and the reader's memory strategy, implement the normalized publisher and explicit
consumer selection rules, and compare actual app behavior.

Marek confirmed the overall design and authorized this schema/reader experiment.
No production reader/collector/recipe/workflow, installed file, remote branch,
daily pin, or catalog publication changed. No workflow dispatched or app binary
downloaded. No additional network measurement was run in this experiment.
The natural November 3 production-run acceptance remains separate outstanding
work. All prototype and main-branch commits are local.
