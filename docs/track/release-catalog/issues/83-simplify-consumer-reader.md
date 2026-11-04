# Simplify the consumer reader and measure ordinary queries

Type: prototype
Status: resolved
Triage: ready-for-agent

Marek prioritizes simplicity over increasingly defensive supervision. Keep complete
validation and private output spooling; remove the optional parser watchdog from
the consumer candidate. Measure direct shell/awk queries at modest representative
synthetic sizes, propose a practical size/tool policy, and distinguish measurements
from accepted limits. Preserve earlier supervision experiments as research evidence.
No production integration, live acquisition, publication or push.

## Answer

[Findings](../research/yaml-simple-consumer.md): simplified prototype `7e8210a56`
on `research/yaml-simple-consumer` removes the parser watchdog, keeps validation,
byte caps/private spooling and documents historical harness boundaries. Nine
ordinary-shape direct measurements match full hashes; 45 reader/budget checks,
syntax, shellcheck, compilation and whitespace checks pass. Proposed 2 MiB
source/output policy remains a proposal; no production defaults changed.
Marek's simplicity direction removes further speculative consumer supervision
from the recommended critical path. Integration and live/remote actions remain
separate; no push or production change occurred.
