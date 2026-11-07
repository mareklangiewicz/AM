# 224-source catalog publication

Marek authorized pushing and publishing the prepared cohort on November 7 local
time (the first runs are dated November 6 UTC). Source
`fde55f59883353e5aa27c73d674a57e1e20613c2` is pushed to `main-marek`.
Five sequential manual runs succeed: 260 successful source attempts, zero failures,
224 distinct sources, **228 app identities / 224 repositories** in the final map.

| Run | Exact published pin | Apps / sources | CI job seconds |
| --- | --- | --- | ---: |
| [42312245000](https://github.com/mareklangiewicz/AM/actions/runs/42312245000) | `f0f73d0d01ec2834b4a2302c14fa08a2d16814fc` | 184 / 180 | 99 |
| [42314245555](https://github.com/mareklangiewicz/AM/actions/runs/42314245555) | `df317883fb902b5064a6023c1819f90dc2474a3d` | 228 / 224 | 83 |
| [42314670373](https://github.com/mareklangiewicz/AM/actions/runs/42314670373) | `d400aef2819eec285e40808a89555062e2b43938` | 228 / 224 | 119 |
| [42315145006](https://github.com/mareklangiewicz/AM/actions/runs/42315145006) | `0c61fffde68021c76adb75b20f37438e31ee7673` | 228 / 224 | 115 |
| [42315622825](https://github.com/mareklangiewicz/AM/actions/runs/42315622825) | `26d82aa94bb5a8f70449e42500dc78a597583ab3` | 228 / 224 | 87 |

Each workflow fetched its actual latest published parent and pushed a direct child
with an exact lease. The local controller checked the current remote pin before
each subsequent dispatch. Each exact published pin and parent passed the maintained
bounded distributed-reader/canonical/cross-reference validation in an isolated
catalog repository. All prior app identities survive; numeric source identities
match enrollment, retained release IDs remain, and effective release observations
never decrease. The first run leaves 128 source documents byte-identical; later
runs leave 172 untouched each. Union coverage confirms success for all 224 sources.

Final pin: `26d82aa94bb5a8f70449e42500dc78a597583ab3`, 33,152,148 YAML bytes,
largest document 1,159,110 bytes. [Portable receipt](next-224-publication.json)
records exact parents, source/document identities, observation/status receipts,
job timings and log digests. Raw logs and controller remain in
`/home/marek/Documents/Codex/am-catalog-publication-20261107/`.

The source adds 97 catalog-only app identities. No new recipe migration,
installed-host refresh, app installation/update, website rebuild or yadm pointer
operation occurred. The host remains at 21 installed apps. No new browser DOM,
CORS/mobile acceptance, natural scheduled-trigger observation or full-suite rerun
is claimed. Actual CI operation of the 224-source scope is now observed; the
larger-batch assessment remains a separate proposal in
[145](../issues/145-assess-larger-metadata-refresh-batches.md).

The deployed cadence stays at 52 attempts every three hours. The proposed hourly
500-source profile is not included in this operation; its quota, replay, freshness
and storage constraints are recorded in [the assessment](refresh-batch-sizing.md).
