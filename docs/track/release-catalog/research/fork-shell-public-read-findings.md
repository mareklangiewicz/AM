# Fork shell publication and pinned public read succeeded

Ticket [27](../issues/27-publish-fork-shell-validation.md), 2026-10-27.
Marek explicitly approved the [ticket-26 candidate and action](fork-shell-validation-plan.md).

Published `a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1` to
[mareklangiewicz/AM release-catalog](https://github.com/mareklangiewicz/AM/tree/a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1).
Restored the checksum-verified candidate archive into an isolated bare repository;
verified full parent, tree, every file hash/length, exact index/body preservation,
and fork-only reader derivation before publishing. A live `git ls-remote` confirmed
exact parent `d612ff34b492b337fe51128f769ec9d262d0ee86` immediately before the
ordinary fast-forward push. A second read confirmed the server ref equals the
approved child. Only lookup.tsv was added. No force, retry or history rewrite.

At `2026-10-27T22:52:39.209775+00:00`, ran the archived fork-only shell reader with
its explicit full pin, real wall clock and real curl. Both catalog GETs returned
HTTP 200; the shell exited 0 at `22:52:40.625277+00:00`, with 450,991 stdout bytes
and empty stderr. Exactly two GETs occurred: pinned lookup.tsv and the selected
Obsidian body. No ref resolution, redirect, retry, source collection, asset
request or installer execution occurred. Observation freshness passed normally;
no stale consent or fabricated measurement time was used.

The pinned lookup and response bytes match the local candidate byte for byte:

| Object | Bytes | SHA256 |
| --- | ---: | --- |
| lookup.tsv | 4,638 | `2c02d155e35872db4ae6e2d893f5720c77f26755ded7f316acdc314fb213bdb6` |
| Obsidian body | 450,991 | `e9b8569d49dcf36b37960bfe97d207d676fc570e462bbf863ca0c9374ced321c` |

The unchanged recipe filter selected the same original upstream URL as the retained
candidate body:

`https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.5/Obsidian-1.14.5.AppImage`

A recording wrapper forwarded every curl argument unchanged to `/usr/bin/curl`,
recorded return/HTTP codes, and copied downloaded files before the reader's normal
scratch cleanup. It did not substitute responses, clocks or transport results.
The exact wrapper, invocation, URL/argument log, downloaded lookup/body, stdout,
empty stderr and result/check JSON are retained in the
[evidence archive](fork-shell-public-read-evidence.tar.gz), 55,462 bytes,
SHA256 `9a7fae0b16b122f9e842230bd4f47205599afd161d5615dcba39b8e29c4781d6`.
[Machine checks](fork-shell-public-read-checks.json) summarize independent local
hash/byte/filter comparisons after the read. The earlier
[candidate bundle](fork-shell-validation-candidate.tar.gz) retains the exact Git
commit and parent history; the new archive retains actual public response bytes.

This proves the bounded fork publication and explicit-pin public shell path.
The production reader still targets **ivan-hc/AM**, with its original SHA256
`9fd9d343ad27facab6d2ec257ee4d9054f9fe8fa7e4f3207733d930825d06440`.
Upstream publication/acceptance, unpinned resolution and installed migration are
not established by this result. No workflow was dispatched, no schedule changed,
and no source branch was pushed. Workflow isolation/settings and upstream branch
existence were not rechecked; any subsequent workflow work must recheck isolation.

No implementation code changed; targeted archive/tree/hash/real HTTP/filter checks
and diff checks validate this task. The existing 100-test suite is prior evidence,
not a newly run suite. All authorized publication/read work is complete.
