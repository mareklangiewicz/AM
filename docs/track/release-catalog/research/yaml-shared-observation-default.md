# Shared observation default and Git history — November 4, 2026

Status: user-agreed encoding, implemented only in the isolated prototype.
Source: `research/yaml-observation-default` at `b3e8b4e70`, directory
`tools/catalog-yaml-prototype/`. No production changes, metadata acquisition,
publication, workflow dispatch, push, repin or host installation.

## Encoding and effective freshness

Repository `observed_at` supplies the default; release `observed_at` overrides it.
Omit overrides equal to the default. A successful merge first resolves prior
implicit observations, preserving them explicitly for untouched releases when
the default changes. Fetched releases replace their old facts and take their
actual page receipt time. The prototype uses final-page receipt as the new
default, including an empty final page, and elides only matching overrides.
Earlier pages retain distinct receipt times through explicit overrides.

Example: A implicitly uses Monday's default. Tuesday fetches only B. The result
has Tuesday's default, A explicitly observed Monday and B implicit Tuesday.
Wednesday fetching only C makes B explicitly Tuesday, leaves A Monday and makes
C implicit Wednesday. No release is refreshed by another release's collection.

Failure preserves the prior shared default, stored release representation and
last-success metadata exactly. Empty successful collections may materialize old
implicit records, but never refresh them. Existing reconciliation remains a local
explicit all-only proposal. A first failure has no default, retained set or
last-success metadata. Successful empty retention still has a default.

The strict reader rejects redundant equal overrides, missing/orphan defaults,
invalid times and effective observations after completion. `get` on a release's
`observed_at` and `rows releases observed_at` resolve the effective time, including
implicit observations. Missing release IDs still return 3; assets do not inherit
release observation fields. Private spooling still suppresses query output on an
invalid suffix. The draft remains format 2 because no previous format-2 revision
was deployed; an immutable schema reference distinguishes the revised grammar.

## Acceptance

Seven new default groups cover repeated partial merges, reobservation/elision,
page receipts and effective queries, failure rollback, empty/reconciliation/first
failure, selected freshness/clock regression, and malformed default/suffix refusal.
Together with nine reader, seven retention and six local JSON adapter groups,
29 unique groups pass on mawk, GNU awk and BusyBox awk. The three matrices record
their own results; inherited reader groups are not counted repeatedly. Independent
YAML parsing verifies each accepted fixture. Shell syntax, shellcheck, Python
syntax, both example documents and whitespace checks pass.

```sh
python3 tools/catalog-yaml-prototype/default_matrix.py
python3 tools/catalog-yaml-prototype/retention_matrix.py
python3 tools/catalog-yaml-prototype/bounded_matrix.py
python3 tools/catalog-yaml-prototype/history.py
```

## Paired Git-history measurement

Each scenario creates two temporary bare Git repositories with 32 snapshots:
one initial snapshot and 31 collection attempts. Fully explicit observations use
the previous encoding; shared observations use the new prototype. An independent
explicit observation oracle verifies equal effective facts after every attempt.
The comparison does not derive expected timestamps from the compact output.
Upstream facts remain unchanged for existing IDs; each release has eight assets.
Commit identities, messages, clocks and source order are fixed between variants.

Git 2.53.0 imports each history and repacks with depth 50, window 10, one thread
and 32 MiB window-memory setting. The replay has 384 MiB address-space and
128 MiB per-file guards, inherited by Git. Repeating the measurement produced the
same pack sizes. There are no remotes or network operations. Raw results are
`history-results.json` on the prototype branch.

The table includes both `.pack` and `.idx` bytes for all reachable commits, trees
and blobs. Refs and other repository administration are excluded; equal overhead
does not disappear. Savings percentages therefore differ from pack-only values.

| Scenario | Explicit packed objects + index | Shared packed objects + index | Saving |
| --- | ---: | ---: | ---: |
| Same 100 releases reobserved daily | 32,483 B | 18,415 B | 43.31% |
| 1,000 retained; same 100 reobserved daily | 91,386 B | 79,618 B | 12.88% |
| Rolling page of 100; 10 new IDs/day, four failed attempts | 106,020 B | 102,089 B | 3.71% |
| All 1,000 reobserved across ten differently timed pages | 192,850 B | 182,042 B | 5.60% |

Final snapshot savings are 3,964 bytes in each case: 100 omitted 40-byte release
timestamp lines minus the 36-byte shared field. Relative savings range from
0.18% to 2.44%, depending on retained payload. Sum-of-snapshot byte savings range
from 0.27% to 2.44%; these are not Git storage measurements.

Git added-plus-deleted line churn after the initial snapshot drops from 6,324 to
186 in the first case, 6,324 to 1,086 in the retained case, 19,816 to 15,990 in the
rolling case and 62,132 to 55,094 in the ten-page case. Initial materialization of
900 untouched implicit records in the retained case and 910 in the rolling case
is included in those histories.
Four rolling failures preserve observations in both encodings. Different page
receipt times require 900 overrides in the ten-page case, limiting savings.

## Consequences and remaining limits

This encoding measurably reduces timestamp churn and packed synthetic history;
it does not bound retention growth or make all observations equally fresh.
Materializing old defaults has a real first-transition cost. The new timestamp
field is not a claim that every retained release appeared on the latest page.

These small, synthetic, one-file histories are not a forecast of the production
catalog's multi-repository history, upstream metadata variability, packing policy
or long-term storage. Snapshot/payload compression and Git delta heuristics can
change the gain. Full-history page timing significantly reduces timestamp sharing.
Prior growth/reader CPU and RSS measurements at `ccd0273e4` remain historical for
the fully explicit encoding; they were not rerun or claimed improved here. Hard
collector/reader/staging budgets and actual default-run capacity remain open.
