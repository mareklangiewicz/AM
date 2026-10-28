# Review the queued daily-switch publication scope offline

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Continue authorized preparation before pilot closure: compare daily workflow and
controller to ticket 40, verify six-source operational selection despite the
separate seven-source candidate, inspect queued publication paths/history for
private delivery payloads, and record exact local review boundaries. This is a
bounded activation-readiness review, not a fresh full standards/spec review of
all queued application code. No live API request, source push, repin, workflow
change, dispatch or host delivery. Remote tracking refs are cached evidence only.

## Answer

At reviewed source `f2eab989e46469184a623cb56d23be7ccc630a8e`, cached
`origin/main-marek` was `466e1facce4e66d4b26c06446fc1e524aa0d76df`:
26 queued commits, 137 changed paths. This is not a live remote verification.

- Daily workflow/controller are byte-identical to ticket 40's `9719fdcee`:
  `17 3 * * *`, exact revision/context/isolation/prior guards, no retry.
- Collector workflow and operational six-source manifest are byte-identical to
  the cached remote. All three collector/publisher manifest reads select that
  file; controller hash is its SHA256
  `1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.
- Seven-source candidate preserves the six original rows and remains separate.
  Manifest loaders plan six versus seven requests respectively. Library count
  changes bind transport/storage/publication to the selected plan; byte-cap
  definitions are unchanged. Shell/reference freshness remains 172800 seconds.
- Known private delivery paths are absent from every queued commit's changed
  paths; no ignored paths are tracked. Removed commits `cd3043c27` and
  `26f9ff4c0` are not ancestors of reviewed HEAD. Queued archive member names
  have no absolute/traversal or known private-delivery paths. This is a path and
  ancestry audit, not a claim that every archive payload received a privacy audit.

[Machine-readable hashes and scope](../research/daily-switch-offline-review.json)
and [reproducible audit](../research/daily-switch-offline-review.py) retain the
boundary. Run the latter from the repository root with
`PYTHONDONTWRITEBYTECODE=1 python3 docs/track/release-catalog/research/daily-switch-offline-review.py`.
Four dispatcher tests plus the workflow-staging regression pass (5 tests,
1.155 seconds). Initial targeted invocation used the wrong class name and failed
test discovery; corrected invocation passed. No production change was needed.

## Remaining activation work

Ticket 37 must still close/assess actual pilot history at/after expiry. After that,
41 must verify live branch/workflow states, preserve old variables, review the
final queued source (including closure evidence), push and verify exact remote
bytes, pin that full SHA, remove pilot window variables and enable daily scheduling.
No extra collection dispatch. This report's HEAD is a review boundary, not an
activation pin: later evidence commits must be included and checked before pinning.
Host helper delivery remains separate and user-run. No new approval is required
for the already authorized six-source switch; seven-source enrollment stays separate.
