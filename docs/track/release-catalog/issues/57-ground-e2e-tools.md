# Extract specified e2e support tools

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Apply the three accepted myground findings: tool-aware download destinations,
independent filesystem snapshots, and incremental transport-record reading.
Migrate the named duplicates and add ordinary unittest specs. Check each change
and the offline container matrix. Per myground application instructions, leave
changes uncommitted. No production, host-delivery or operational changes.

## Applied findings

- Download destinations: fixed in `test/e2e/transport_args.py`; partial and complete
  adapter paths share the parser. Tool-specific options and invalid forms have specs.
- Filesystem snapshots: fixed in `test/e2e/filesystem.py`; migrated all scenario
  calls and removed the Termux method alias. Preserved bytes/mode/mtime/link semantics.
- Transport records: fixed in `test/e2e/transport_records.py`; migrated Neovim,
  repository-switch, mixed-batch and no-argument sync readers. Specs cover checkpoint
  exclusion, deterministic order, empty records and malformed JSON.

Baseline syntax, ShellCheck and diff checks passed. Focused specs after findings
1/2/3 passed 3/6/9 tests respectively; no repair attempts or reverts were needed.
Added the documented host-safe fast check and included tool hashes in container
source identity. The lighter catalog lifecycle snapshot remains intentionally
separate because it observes a different contract.

## Answer

All three findings fixed and specified. Final Debian/Fedora/Termux matrix passes
34 scenarios / 108 installed commands, zero unexpected requests; focused tool
specs pass 9 tests. [Checks and source/image hashes](../research/e2e-ground-tools-checks.json)
retain exact tested identities. Full logs remain in the ignored run directory.
Initial sandbox launch failed at Podman runtime setup before any test; approved
retry passed. ShellCheck and diff checks pass. Changes were initially left uncommitted under myground's application rule;
Marek subsequently explicitly authorized committing them. No production change, source push,
host delivery, workflow change or live metadata/binary request.
