# Correct checksum UI after YAML cutover

Type: task
Status: resolved
Triage: ready-for-agent

Marek authorized the handoff's checksum cleanup. Prefer installed download-url
for timestamp version identities, retain legacy URL fallback, and accurately report
that extracted archive files are not checksum-verified. Source-only change;
no live deployment or push. Earlier migration/interview tickets are outside scope.

## Answer

The generic verifier ignored installed download-url and assumed version was a URL.
It now prefers download-url, retaining the version URL and am-extras fallbacks.
Archive sources report skipped verification of extracted files and leave no
AM-VERIFIED marker. Successful digest comparison and checksum-failure repair
markers retain their existing behavior.

Eight offline regression tests run the actual manager function with local payloads
and stubbed digest transport: saved timestamp identity, URL precedence, legacy URL,
missing URL, three saved archive extensions, legacy archive, missing digest, and
mismatch. The tests reproduced the original failures before the fix and pass now.
All 11 YAML manager integration tests pass. Bash syntax and diff whitespace
checks pass. Independent parallel Standards and
Spec reviews found zero actionable findings.

The old test_batch_updates.py format-1 suite was also attempted: 14/15 fail at
retired format-1 installation refusal, outside this checksum change. This is not
claimed as passing compatibility coverage. No live manager deployment, app update,
publication, push or yadm operation was performed.
