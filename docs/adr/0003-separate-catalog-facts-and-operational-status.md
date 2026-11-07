# Publish operational status independently of release facts

A failed collection or publication must be publicly visible while the last good
catalog remains usable. Publish operational status through a separately pinned
channel whose confirmed publication references bind exact catalog revisions;
allow and label confirmation lag rather than claiming atomic publication across
both channels. This avoids coupling failure visibility to advancement of release
facts; the target contract and compatibility boundary live in
[Choose public YAML contracts and revision consistency](../track/catalog-system/issues/03-choose-public-yaml-contracts-and-revision-consistency.md#answer--november-7-2026).
This is a target architecture decision, with no deployed behavior change.
