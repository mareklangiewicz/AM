# Prepared fork shell publication validation

Ticket [26](../issues/26-prepare-fork-shell-validation.md), 2026-10-27.
Preparation complete; **no remote publication or live shell read performed**.

## Concrete review target

| Item | Value |
| --- | --- |
| Source implementing derivation/reader | `605b1cbba25f684fde85cac354ec425535e08ca1` |
| Remote repository | `mareklangiewicz/AM` |
| Only remote ref to advance | `refs/heads/release-catalog` |
| Required current parent | `d612ff34b492b337fe51128f769ec9d262d0ee86` |
| Prepared child | `a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1` |
| Candidate tree | `414bf57e90932ad56b552488715e232c0457ad96` |
| Only tree difference | add `lookup.tsv`, 4,638 bytes |
| Lookup SHA256 | `2c02d155e35872db4ae6e2d893f5720c77f26755ded7f316acdc314fb213bdb6` |

A read-only `gh api repos/mareklangiewicz/AM/git/ref/heads/release-catalog --jq .object.sha`
confirmed the required parent during preparation. Recheck immediately before any
approved push; this observation is not a lock or a guarantee of future state.
Workflow isolation, repository Actions settings and upstream branch existence were
not rechecked. This plan does not dispatch or change a workflow, so it needs no
workflow enablement. Any later workflow validation requires its own isolation check.

## Derivation and provenance

Restored the exact two-commit bundle from ticket 18's checksum-verified retained
evidence archive. Read and fully validated the parent tree with the current bounded
Git-tree reader. Recomputed lookup.tsv from its canonical index using the current
shell_lookup.render and validated the complete child tree. Created the child in a
separate local bare repository, then exported a bundle. AM's source branch and
installed reader were not modified by candidate construction.

The parent index and all six original response bodies are byte-identical. The
index still records its actual historical collector source/run and publication
measurement time (`2026-10-27T15:44:02.763137+00:00`). Its provenance was not rewritten
to imply a new collection. The new derived-file source is recorded separately in
the table above. This is a manually prepared format-only child, not a new
same-run collector artifact or a claim that the workflow publisher processed it.
No synthetic response, 304 or freshness timestamp was introduced.

[Candidate manifest](fork-shell-validation-candidate.json) records every file's
length/hash, observation timing, parent/child/tree and reader hashes.
[Evidence archive](fork-shell-validation-candidate.tar.gz) is 661,512 bytes,
SHA256 `9e33632359ebb1bdc46c5b6ddc106737ef14874f1bdf7377e99935bab5f5c9ee`.
It contains the exact candidate bundle (including parents), prior bundle, manifest,
fork-only reader copy, construction and verification scripts, and checks. Scripts
record this workspace's absolute path and preparation directory; they are evidence,
not a new installed runtime or supported general publication command.

## Fork-only read configuration

Production `modules/catalog.am` continues to target **ivan-hc/AM**. The archived
`fork-reader.sh` is an explicit test copy with exactly two literal owner substitutions
from `ivan-hc/AM` to `mareklangiewicz/AM`: ref resolution and raw content root. All
other bytes match the production reader at the approved source. No environment
owner override or installed configuration was introduced. This tests development
fork delivery; upstream publication, permissions and adoption remain unverified.

[Local checks](fork-shell-validation-checks.json) restored/validated the exported
bundle, compared every hash/size, checked that only lookup.tsv was added, and
rehearsed a normal fast-forward push to a temporary local bare repository. The
fork-only reader used a curl stub that serves Git blobs at the exact fork URL and
pin, with the real wall clock. It made exactly two simulated catalog requests,
returned the exact body, emitted no stderr, and selected the same original URL as
the retained parent body:

`https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.5/Obsidian-1.14.5.AppImage`

Checked at `2026-10-27T22:49:19Z`. These are local transport checks, not HTTP results.
The first rehearsal revealed that the historical bundle used a local ref name;
the harness now explicitly initializes its simulated publication ref to the
required parent before exercising the push. No production code change was needed.
The existing 100-test implementation result remains historical; this artifact-only
preparation did not rerun that unchanged suite.

## Approval boundary and exact next action

Approve one ordinary fast-forward publication of the prepared child to the fork's
release-catalog ref, followed by one explicit-pin public shell read. No source
branch push, workflow dispatch, new collection, binary download or installer is
needed for this action.

After approval, restore the bundle into an isolated bare repository, verify its
hashes/tree/parent again, and compare the current remote ref to the exact parent.
Refuse on a mismatch. Push only
`a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1:refs/heads/release-catalog`
to `git@github.com:mareklangiewicz/AM.git`, with no force, retry or rewrite. The
normal fast-forward push also rejects a concurrent divergent publication. Record
the resulting server ref.

Run the archived fork-only reader directly with alias
`https://api.github.com/repos/obsidianmd/obsidian-releases/releases` and
`--commit a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1`.
This makes exactly two public catalog GETs: pinned lookup and selected body, with
no ref-resolution GET. Save body/stderr/status, compare body size/hash and the
unchanged recipe filter result to the manifest/checks. Do not run the app recipe.
If raw content is unavailable, record refusal without retrying automatically.

The retained Obsidian observation is fresh through the inclusive boundary
`2026-10-28T15:43:58.633795+00:00`. After that boundary, the first ordinary attempt
will refuse after its lookup GET. Do not silently add stale consent or refresh
data. A later approval can instead include this exact stale tuple at the outset:

```
--commit a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1
--accept-stale a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1 98c8484a8be11cb446c110c6c2a36368618e2015793a4e241ab3aeef7a867205 e9b8569d49dcf36b37960bfe97d207d676fc570e462bbf863ca0c9374ced321c
```

An unpinned ref-resolution smoke test would add one GET and requires separate
scope. Installed migration and upstream acceptance remain separate work.
