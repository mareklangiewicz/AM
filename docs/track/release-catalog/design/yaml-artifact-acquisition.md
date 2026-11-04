# Inactive YAML artifact acquisition candidate

Ticket 92 continues the staging candidate. `yaml_delivery.acquire` authenticates
a caller-selected artifact using the existing fixed-repository downloader, checks
its bounded ZIP as inert data, verifies normalized YAML and receipt against trusted
source/context/profile/scope/enrollment/pinned prior, then writes a new private
staged directory. No CLI or workflow imports this candidate.

The caller supplies trusted artifact ID and upload digest, never values inferred
from receipt. Metadata checks repository/run/source/branch and the existing
proposal's `yaml-bootstrap-RUN-ATTEMPT` name; exact downloaded ZIP bytes must match
GitHub's SHA-256 digest. The name binds the attempt under the trusted collection
workflow; the artifact metadata's workflow_run object does not independently
prove an attempt number. This retains the agreed workflow trust boundary.

ZIP central-directory count and bytes are bounded before ZipFile parses member
objects. The profile permits only stored/deflated entries, the two structural
directories, receipt.json and normalized candidate YAML. No extraction, raw body
archive or executable artifact is introduced. File/count/uncompressed-tree/receipt
bounds are distinct from the archive envelope: tree + receipt + 1,000,000 bytes,
136,266,304 bytes for yaml-policy.json. ZIP64/multidisk are refused. These are
explicit candidate bounds, not measured runner capacity or peak-RSS guarantees.
The existing downloader buffers bounded ZIP bytes; decoded files also occupy
memory. This does not add a watchdog, worker or reservation framework.

Authentication and verification finish before exposing a new private directory.
Existing destinations refuse before API work. Failed writes use existing staging
cleanup. The exact-pin prior must already exist locally; this adapter does not
infer branch absence, perform format-1 conversion, fetch prior state or publish.
Receipt stays artifact-only. Upstream successful facts rely on the trusted
workflow, as previously agreed, rather than raw-body recomputation.

Six offline acquisition tests exercise fake authenticated API responses, real
ZIP decoding and staged bootstrap YAML. Regressions include the existing format-1
local delivery, sharded delivery and shell delivery tests. No live artifact or
GitHub runner capability was checked. Remote prior loading and exact publication
CAS, reviewed source promotion and operational activation remain separate.
