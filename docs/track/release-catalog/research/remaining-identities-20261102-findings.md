# Remaining identity batch: environment failure

November 2, 2026, ticket [47](../issues/47-enroll-scoped-migration-sources.md).
The user approved the prepared 48-request identity-only batch. Executed the exact
reviewed runner once, in the restricted command environment, with fresh output
`remaining-identities-20261102`.

[Batch summary](remaining-identities-20261102/batch.json) records one attempted
transfer, to `https://api.github.com/repos/ARPA-SIMC/CRITERIA1D`. The
[request report](remaining-identities-20261102/01/report.json) records curl exit 6
(could not resolve host), 0.008311 seconds, zero header/body bytes and no HTTP
status. No upstream response or repository identity was obtained. This is a
local transport failure, not evidence that the repository is unavailable.

The runner stopped immediately, as approved. The other 47 identity URLs were not
attempted. Exact empty-stream SHA256 values and the single completed-attempt
summary were checked offline. No release GET, fallback, retry, identity mapping,
enrollment, source push, publication/repin or host delivery occurred.

A fresh network-enabled run requires explicit retry authorization because this
batch's contract stops on first failure and forbids automatic retries. Preserve
the failed directory; do not delete it or bypass its repeat guard. The proposed
retry retains the same runner SHA256, payload, 48 URLs and bounds, with a fresh
output path:

```sh
python3 tools/catalog-collector/identity_batch.py \
  --execute-approved-identity-batch \
  --output docs/track/release-catalog/research/remaining-identities-20261102-network
```

Run that command with network-enabled execution only after the scoped retry is
approved. No escalation/automatic-approval review was requested or rejected in
this attempt. 47 and 49 remain partial; no new evidence supports enrollment.
