# Reduce snapshot processing before the next catalog cohort

Ticket [142](../issues/142-reduce-full-snapshot-processing.md), November 6, 2026.

The maintained loader previously decoded every prior snapshot twice: `load_local`
called validating `read_tree`, then validated/decoded the result again. It now
reads bounded inert blobs privately and validates/decodes each exactly once.
Public `read_tree` still validates. The distributed shell reader checks original
bytes before either safe PyYAML loader runs. Safe LibYAML is preferred when
available, with the safe Python loader retained as fallback. Canonical bytes,
path/source identity and cross-file app references remain checked.

Publication starts a private index from the exact parent and reuses unchanged
blob IDs. Only changed blobs are written; one NUL-delimited index operation
applies additions, changes and explicit deletions. The complete validated next
tree is still required. Remote refusal, expected-parent compare-and-swap and the
unchanged conservative history bound remain. Clients and catalog schema do not
change. This is not a lazy/incremental reader: the full snapshot is still decoded,
encoded and validated in memory.

[Timing receipt](snapshot-processing-timing.json) runs the same saved 128-source
parent, evidence and 52-source batch as the earlier recorded 311.45-second replay:
94.51 seconds / 167,784 KiB peak RSS under 1 GiB, versus 179,560 KiB historically.
All 129 output documents match the earlier replay byte-for-byte after substituting
only the current source-schema revision; all 52 source receipts are identical.
This is an offline local comparison, excluding HTTP/CI overhead and without a
claim of universal speedup. It measures the uncommitted source hashes recorded
in the receipt, relative to base `e38c04cd1`.

Focused checks cover one validation per document, the safe-loader fallback,
unchanged-blob reuse, exact addition/deletion/tree replacement, unchanged-tree
child commits, stale parents, malformed documents, canonical bytes and size/history
bounds. The broad collector run executes 149 tests: 147 pass and two declaration checks
see a mixed enrollment revision while the manifest is edited. Their complete
three-test module passes on the final configuration; six final identity checks
and two final enrollment checks also pass. The [next-cohort report](next-224-catalog-expansion.md)
records the exact validation limits and log digests.
