# Installed Obsidian catalog clock refusal

Type: research
Status: resolved
Triage: ready-for-agent

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

## Follow-up — reproduced formatter failure and local correction

The preceding no-cause finding describes the initial single successful probe.
A bounded series of up to twelve installed-reader reads stopped at attempt four
with the exact catalog refusal. [Retained series](../research/obsidian-installed-refusal-20261102/reader-series.json):

- First freshness sample `1793639541.892750`; second `1793639541.523636`.
- The apparent backwards step is 0.369114 seconds; both metadata timestamps
  were in the past, body hash matched, and duration was far below 90 seconds.
- Concurrent Python CLOCK_REALTIME monitoring saw no backwards step.

The execution environment resolves `/usr/bin/date` to uutils coreutils 0.10.0.
Its width-limited nanosecond format loses leading zeros. This deterministic
command reproduces the defect without network access or clock changes:

```sh
date -u -d @1793639584.006207078 '+%s.%6N %s.%N'
# 1793639584.620707 1793639584.006207078
```

[Four-second comparison](../research/obsidian-installed-refusal-20261102/date-comparison.json)
found 36 inconsistent outputs in 336 samples, with Python timestamps bracketing
each call. The formatted reader clock can therefore regress while real time
advances. This explains the newly reproduced reader failure in this environment;
it does not independently establish the date implementation used in Marek's
original terminal or the cause of that uncaptured event. Do not infer NTP or
hardware failure from this formatted-clock trace. Earlier rollout evidence is
preserved, with no retrospective claim that its host clock actually stepped.

Repository correction: read `%s.%N`, validate nine fractional digits, and
explicitly truncate to six. This preserves the microsecond inclusive freshness
boundary, backwards-clock refusal and 90-second limit. No guard is relaxed.
The regression test drives the real reader with the system date executable at
three fixed increasing timestamps. It failed before the correction with the
exact refusal, then passed afterward:

```sh
cd tools/catalog-collector
python3 -m unittest test_shell_consumer.ShellConsumer.test_system_date_leading_fractional_zeros_do_not_invent_regression
```

Validation: 107 tests passed across `test_shell_consumer`, `test_shell_delivery`,
`test_appimage_lifecycle`, `test_acceptance_reader_diagnostics` and
`test_scheduled_dispatch`. Separate focused regression/freshness checks passed;
shell syntax, shellcheck and diff whitespace checks passed.
[Candidate reader series](../research/obsidian-installed-refusal-20261102/candidate-reader-series.json)
retains an initial transport refusal and five subsequent successful metadata-only
reads with matching body hashes. The transport refusal was not a clock failure.

## Remaining work

- Confirm the actual user's terminal date implementation before attributing
  the original `am -u` event to this formatter defect.
- Review publication of the local correction together with its exact daily pin.
  This changes the runtime reader, so it is not merely a documentation-only repin.
- Deliver the reviewed helper through the normal module sync, then perform only
  the named Obsidian retry and verify its exit. No updater or host sync was run
  in this investigation; installed helper bytes remain unchanged.
- Observe the natural November 3 sharded run; November 2 control checks show
  source=pin=`519c0e484` and unchanged catalog `e391f35f6` with only the two intended
  workflows active. See [controls](../research/obsidian-installed-refusal-20261102/current-controls.json)
  and [refs/runs](../research/obsidian-installed-refusal-20261102/current-refs-runs.json).

Ticket remains open for original-host confirmation and installed delivery.

## Answer — host confirmation and delivery, November 2, 2026

Marek supplied output from his original terminal on myxps: `type -a date`
resolved `/usr/bin/date` and `/bin/date`; `date --version` reported uutils
coreutils 0.10.0. This confirms the affected implementation on the original
host. The original refusal itself remains uncaptured, so its exact predicates
cannot be reconstructed; the formatter defect is the supported explanation,
not proof of an NTP or hardware clock step.

Marek then ran normal `am -s` at approximately 18:26 Warsaw. It reported
updating `catalog.am` and AM already current at 10.6-4. His named
`am -u obsidian` retry at 18:27 downloaded Obsidian 1.15.0 and ended with
`/opt/obsidian: updated` at approximately 18:27:25. No catalog refusal appeared.
The transcript does not print a numeric exit status; success is established by
the updater's completion message. Signed redirect URLs and tokens are omitted.
Agent read-only verification with `cmp /opt/am/modules/catalog.am modules/catalog.am`
returned 0: installed helper equals the corrected repository bytes.

Publication had already completed before this confirmation: source and daily
pin were both `0464ec126f2d65ba23d0a06871f284590efe06f1`, catalog remained
`e391f35f61a61fde63e9d12ab10b3deb04f2abfb`, as recorded in the
20261102T1721Z handoff. These are prior verified controls, not a fresh remote
survey. This documentation follow-up is local only and must not be pushed
without reviewing its exact source and matching daily repin together.

Host confirmation, helper delivery and the named retry are settled; ticket 70
is resolved. Observing and independently accepting the next natural daily run
(November 3, 03:17 UTC / 04:17 Warsaw) remains separate frontier work.
