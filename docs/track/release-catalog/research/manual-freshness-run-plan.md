# One manual freshness refresh: approval target

Ticket [33](../issues/33-prepare-manual-freshness-run.md).

Read-only GitHub checks on 2026-10-28 continuation confirmed Actions enabled,
only workflow 398399199 (catalog-collector.yml) active, six other registered
workflows disabled_manually. release-catalog remains
`a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1`; main-marek remote is
`3ad023822c4df52e3f69874b21200899bf7d3e82`. These checks must be repeated
immediately before dispatch; refuse drift instead of substituting new pins.

The proposed source revision is already pushed. Collector/workflow/helper code
has no diff between that revision and current HEAD; subsequent local commits
record only pilot execution evidence. No new source push is needed for this run.
Manifest SHA256:
`1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.

## Exact action

Approve one dispatch of catalog-collector.yml on main-marek, using:

- approved_revision: 3ad023822c4df52e3f69874b21200899bf7d3e82
- manifest_sha256: 1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9
- previous_publication: a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1

Run command after rechecks:

```sh
gh workflow run catalog-collector.yml --repo mareklangiewicz/AM --ref main-marek \
  -f approved_revision=3ad023822c4df52e3f69874b21200899bf7d3e82 \
  -f manifest_sha256=1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9 \
  -f previous_publication=a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1
```

## Budget and effects

At most six serial upstream GitHub REST GETs, the existing manifest only:
Obsidian list/latest, Neovim list/latest, WezTerm list per_page=100 and
SQLite Browser list per_page=100. Existing prior validator tuples are supplied.
No pagination expansion, identity lookup, source enrollment, redirect, transport
retry, repeat dispatch or attempt to obtain a particular HTTP result. Each body
cap is 8,000,000 bytes, header cap 64,000, request deadline 30s, connect deadline
10s, batch deadline 300s; each workflow job has a five-minute timeout.
Git checkout/prior fetch, artifact upload/download/API validation, publication
ref checks and Git push are additional delivery traffic, not included in the
six upstream release requests. Artifact ZIP cap is 105,000,000 bytes.

The separate publisher validates/recomputes the same-run artifact and performs
at most one ordinary fast-forward publication to release-catalog with the exact
prior. No force or history rewrite. All six transfers must succeed as 200/304
for publication; failure preserves the old branch. Do not refresh failed
observations' ages, add stale consent, or automatically retry/recollect.
Collection uses contents:read; publication uses contents:write/actions:read.

Retain the run ID, actual permission logs, artifact ZIP/digest, exact parent/child,
request conditions/outcomes and per-observation receipt/validation times in Git
before seven-day Actions artifacts expire. Independently recompute artifact/tree
against retained prior. Then make at most two additional public GETs through the
unmodified shell helper with explicit AMREPO and the resulting full publication
pin: lookup and Obsidian body. Record actual request outcomes, hash/length and
existing filter result, using real time with no stale override. Do not run the
installed updater or download another app binary.

This is one manual refresh. No schedule, Actions-settings change, installed file
change, app execution or recurring authorization is included. Afterward report
actual expiry; sustained freshness needs an explicit cadence/operational decision.

## Preparation evidence

[Offline checks](freshness-run-preparation-checks.json) restore the retained
candidate bundle, validate its actual tree, and prepare all six sources against
that prior without credentials or live transport. Fixture context is labelled as
such; it is not a claim of workflow execution. Full implementation suite is run
in this preparation; final result is recorded in ticket 33.
