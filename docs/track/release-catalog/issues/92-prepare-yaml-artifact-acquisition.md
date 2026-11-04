# Prepare authenticated bounded YAML artifact acquisition

Type: task
Status: resolved
Triage: ready-for-agent

Continue ticket 91 on the inactive prep branch. Reuse the authenticated GitHub
artifact downloader, bind the same-run artifact identity and SHA-256 digest,
and decode only bounded normalized YAML plus receipt. Validate against trusted
context and pinned prior before exposing a new private staged directory.

Use offline adversarial ZIP and fake API checks. No live requests, active
workflow changes, remote catalog publication, repin or installed changes.
Remote format-2 prior acquisition and publication CAS remain subsequent work.

## Answer

Prepared source candidate `eecdbdc09` on `prep/yaml-offline-publication`.
[Findings](../research/yaml-artifact-acquisition.md) record authenticated same-run
identity/digest checks, bounded closed ZIP decoding and verification before private
staging. Six new acquisition tests plus 49 regression checks pass (55 total).
Compilation and whitespace pass. No live requests or operational changes.
Remote prior loading and publication CAS remain subsequent work.
