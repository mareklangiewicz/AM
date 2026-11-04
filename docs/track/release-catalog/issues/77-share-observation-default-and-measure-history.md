# Share observation default and measure Git history

Type: prototype
Status: resolved
Triage: ready-for-agent

User-agreed design: repository observation timestamp supplies the default;
release observed_at is omitted when equal and overrides otherwise. Materialize
old effective observations for untouched implicit releases before changing the
default. Failed collections preserve default and observations. Preserve page
receipt times via overrides. Update draft schema and isolated prototype; measure
Git-history savings against equivalent fully explicit release observations.
No production integration, push, workflow dispatch or repin.

## Answer

[Shared-default findings](../research/yaml-shared-observation-default.md), schema
and ADR 0002 record the agreed encoding. Prototype `b3e8b4e70` preserves implicit
effective times before a default change and preserves exact observations/default
on failure. Reader queries return effective timestamps. All 29 unique groups pass
on three awk tools. Four paired 32-snapshot Git histories show packed-object-plus-
index savings of 43.31%, 12.88%, 3.71% and 5.60%; these are synthetic scenarios,
not production storage guarantees. No production or remote changes.
