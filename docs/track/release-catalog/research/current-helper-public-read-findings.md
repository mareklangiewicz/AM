# Current helper pinned public read

Ticket [30](../issues/30-current-helper-public-read.md), source 3a843e656.

The current unmodified modules/catalog.am, SHA256
`b827f9febc90a45012f540926674f8f4210e3e1f3626cb30050b4422092be6fc`,
used explicit AMREPO=https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek
and publication `a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1`.
At 2026-10-27T23:47:22.159432+00:00 through 23:47:23.399754+00:00,
exactly two GETs returned 200: pinned lookup.tsv and Obsidian body. Exit 0,
empty stderr, normal real-clock freshness, no stale override. A transparent
wrapper forwarded arguments to real curl and retained responses before cleanup.
No transport, response or clock substitution was used.

Lookup: 4,638 bytes, SHA256
`2c02d155e35872db4ae6e2d893f5720c77f26755ded7f316acdc314fb213bdb6`.
Body/stdout: 450,991 bytes, SHA256
`e9b8569d49dcf36b37960bfe97d207d676fc570e462bbf863ca0c9374ced321c`.
Both files match ticket 27's archived responses byte for byte. Extracting and
running the current recipe's existing selection pipeline returned
`https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.5/Obsidian-1.14.5.AppImage`.

Initial sandbox attempt failed DNS, curl 6, before any successful HTTP response;
its actual HTTP request count is not established. Network escalation was approved
for the subsequent successful invocation. Both attempts are retained separately.

[Evidence archive](current-helper-public-read-evidence.tar.gz), SHA256
`83c5383c7ee5e25094c2969154e6e46e4adb781f5d87c1bc0ac91ec23b1cc23b`,
contains helper bytes, invocation/recording/check scripts, request argument/status
logs, downloaded bytes, stdout/stderr, timestamps and local comparison results.

This validates current configured-source explicit-pin public reading. It does not
verify unpinned resolution, continued freshness, current publication ref or workflow
settings, installed delivery/migration, or app installation/update. No source
collection, binary download, workflow, publication or schedule occurred.
