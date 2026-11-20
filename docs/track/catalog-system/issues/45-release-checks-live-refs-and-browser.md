# `release.py` checks live refs and the deployed browser

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

Before a schema repin, `release.py plan`/`ship` validate the live
`catalog-status-v1` and `release-catalog-v3` refs under HEAD's contract and
refuse if either fails. Every plan and ship says whether the deployed
browser's `definitions.mjs` matches HEAD's, and gives the redeploy command
when it does not.

## Why

Ticket 25 retro, item 1. Retirement step 3 drops a summary property while
retained summaries may still carry it; shipped early, every catalog run
would refuse. The browser at mareklangiewicz.pl/AM had to be checked by hand
(curl) before steps 1 and 2.

## Scope

- Validation only when the `schemas` scope changed (ticket 44): it takes
  about 10 minutes; other ships pay one curl.
- The browser comparison reports; it never refuses (an unreadable site is
  reported too).

## Comments

## Answer — November 20, 2026

`validate_live_refs` fetches both refs, reads each tree with one
`git cat-file --batch` (`read_tree`; `contracts.read_local` spawns one git per
blob and did not finish the status ref in 9 minutes) and runs
`contracts.validate_tree` from the checkout. `decide` calls it after the
schema-pin check, then curls the deployed definitions and compares them with
`git show HEAD:tools/catalog-contract/definitions.mjs`.

Tests: `test_release.py` 36 OK (7 new; a byte-exact `read_tree` round trip on
a temporary repository fails when its offset is off by one). Real control:
in a scratch worktree with step 3's contract (property removed, regenerated),
`validate_live_refs` reported `catalog-status-v1 1a9b285bc: catalog YAML:
line 22: unknown or out-of-order field`; under the current contract both refs
passed (each about 11 minutes, run side by side). The deployed definitions
matched HEAD (curl, 17,781 bytes).
