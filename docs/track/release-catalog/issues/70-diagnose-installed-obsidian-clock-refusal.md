# Installed Obsidian catalog clock refusal

Type: research
Status: open
Triage: needs-info

Separate from completed rollout ticket 69. Marek reported `am -u` refusing
Obsidian with `AM catalog: future time, regressed clock or expired read` and
`/opt/obsidian: refused`, followed by aggregate exit 1. Original timings and
command-session acquisition bytes were not captured.

## Investigation — November 2, 2026

Read-only inspection: installed `/opt/obsidian/AM-updater` delegates to
`recipe.am --am-update`, which invokes `/opt/am/modules/catalog.am` via the
shared AppImage module. Both installed modules match repository bytes.
The reader checks freshness before and after body acquisition. The exact
message combines future publication/observation, backwards sampled wall clock,
and elapsed wall-clock read time exceeding 90 seconds. A stale observation
has a different refusal message.

The existing `test_shell_consumer.ShellConsumer` fixture was run with `HELPER`
overridden to the actual installed reader, using inert transport and clock
fixtures. Control returned 0; future time, backwards time and 91-second read
fixtures each returned 1, emitted no body, and matched the exact reported
catalog message. This establishes a deterministic guard reproduction, not
reproduction of the original host event.

One live metadata-only read using [probe.py](../research/obsidian-installed-refusal-20261102/probe.py)
passed. Run with `python3 docs/track/release-catalog/research/obsidian-installed-refusal-20261102/probe.py`.
The probe executes only the installed catalog reader, discards release JSON,
and retains numeric/hex diagnostics plus concurrent 10ms clock samples.
An initial sandboxed attempt failed transport; the network-enabled attempt:

- Start: `1793639322.669784`; publication: `e391f35f61a61fde63e9d12ab10b3deb04f2abfb`.
- Generated: `1793636296.507652`; observation validated: `1793636015.030123`.
- Freshness checks: `1793639324.210319` and `1793639324.917030`, both fresh.
- Exit 0; 447378 body bytes; SHA256 `4047616b97463eb0bf4c7109b6f3fdfa9005a32ec85578f00b6a83afd90db4dd` verified.
- 284 clock samples over 2.877214419 monotonic seconds; no observed backwards step.

This isolated read deliberately omits `AM_CATALOG_SESSION`; it does not replay
the original batch's shared lookup or timings. Finite monitoring does not prove
permanent stability or recover the original cause.

## Ranked remaining explanations and predictions

1. Transient backwards wall-clock step: a failing trace would show a freshness
   sample below the reader's previous sample; concurrent clock monitoring may
   independently observe it. Earlier acceptance captured such a step, but not
   this Obsidian event.
2. Read exceeding 90 wall-clock seconds: failing trace would show `now-start>90`
   without needing future metadata or clock regression.
3. Future publication/validation relative to host time: failing trace would show
   `generated>now` or `validated>now`. The successful read of the same publication
   argues against a persistent instance of this condition.

No cause established and no production change justified. A future failing
reader-only trace can discriminate these predicates. No updater was executed,
no app binary downloaded, no clock or installed file changed, no remote controls
changed, and no push performed. Full update retry remains outside this diagnosis.
