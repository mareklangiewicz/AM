# Record direct asset acquisition and future self-update boundary

Type: task
Status: resolved
Triage: ready-for-agent

Marek prefers exact catalog downloads for simplicity and asks whether this would
prevent partial upstream adoption or improved self-updates later. Record that
preferred migration direction, distinguish selection from asset acquisition,
and preserve a future target-respecting delta/self-update option without adding
a speculative transport framework or promising upstream acceptance.

Documentation/terminology only. No adapter implementation, source promotion,
installed changes, network acquisition, workflow/publication, push, repin or yadm.

## Answer

[Direction and limits](../research/yaml-asset-acquisition-direction.md) records
Marek's direct selected-asset download preference, superseding the unanswered
checkpoint in 104. GLOSSARY.md distinguishes asset acquisition from client
selection. Future delta/native updates remain possible if they honor the selected
target and add adequate staged-result verification; the current handoff/lifecycle
is not described as providing a digest guarantee. Partial upstream adoption is
an architectural proposal shape, not a claim of maintainer acceptance.

No ADR or speculative acquisition framework was added: this is a reversible
migration direction. No adapter/runtime, installed, network, remote, workflow,
publication, push, repin or yadm changes. Documentation links/whitespace checked.
