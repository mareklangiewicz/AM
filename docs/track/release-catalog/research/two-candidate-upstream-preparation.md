# Existing candidate pair: primary upstream preparation

Ticket [128](../issues/128-verify-two-candidate-upstream-evidence.md), observed
November 6, 2026, approximately 01:29–01:30 UTC. Source selector is `e2e96b3a4`;
original recipe/template provenance remains in
[126's assessment](three-candidate-runtime-assessment.md). This is preparation,
not conversion, collection enrollment or deployment.

## Verified identities and observed assets

Read-only, anonymous requests to GitHub returned HTTP 200 for both repository
metadata endpoints and the first release-list page (`per_page=30`). No repository
identity redirect was observed; 2fac's canonical spelling differs in case.

| Fork recipe | Requested repository | Canonical repository | Numeric ID | Response scope |
| --- | --- | --- | ---: | --- |
| 20x | peakflo/20x | peakflo/20x | 1152028865 | 30 releases, 569 assets; another page advertised |
| 2fac | jeonjw85/2fac | jeonjw85/2FAC | 1337965664 | 4 releases, 60 assets; no next-page link |

Primary sources: [20x repository](https://api.github.com/repos/peakflo/20x),
[20x release page](https://api.github.com/repos/peakflo/20x/releases?per_page=30),
[2FAC repository](https://api.github.com/repos/jeonjw85/2fac),
[2FAC release page](https://api.github.com/repos/jeonjw85/2fac/releases?per_page=30).
Counts and conclusions refer to saved responses at the observation time, not
future API state or complete release observation. Both metadata responses report
`archived=false` and `disabled=false`; this alone does not establish support or
maintenance quality.

Selected observed assets:

| Candidate | Release / release ID | Asset / asset ID | Declared size |
| --- | --- | --- | ---: |
| 20x | v0.0.186 / 427758388 | 20x-linux-x86_64.AppImage / 688278008 | 437,228,965 bytes |
| 2fac | v0.1.6 / 398019492 | 2FAC_0.1.6_amd64.AppImage / 594778867 | 83,560,952 bytes |

The 20x release also contains `20x-0.0.186-x86_64.AppImage` (688278010).
GitHub reports the same full-file SHA-256 for those two asset names. That is
metadata evidence, not a full-file integrity check performed here. All URLs,
API digests, sizes, observation times and response hashes are retained in the
[evidence archive](two-candidate-upstream-evidence.tar.gz); the
[compact receipt](two-candidate-upstream-evidence.json) records identities,
comparison results and archive hash.

## Selection comparison and proposed declarations

Replayed the exact hash-checked pinned FUNCTION against the **complete saved
release response**, including text fields, with local curl output. The maintained
awk selector ran on structured facts projected from the same response, compiled
from disposable declaration headers with the real verified numeric IDs. Release
observation and selection clocks were set to the recorded observation time.
No collector, production registry or actual recipe was changed.

| Candidate | Proposed asset pattern | Result on saved evidence |
| --- | --- | --- |
| 20x | `^20x-linux-x86_64[.]AppImage$` | Same selected URL as upstream |
| 2fac | `^2FAC_[0-9]+([.][0-9]+)*_amd64[.]AppImage$` | Same selected URL as upstream |

Both proposals retain `CATALOG_CHANNEL=any`, URL version identity, raw AppImage
layout, ordinary command desktop execution and no extra launchers. They are
review proposals, not installed or enrollment-ready declarations. In particular,
the 2fac pattern supports the observed dotted numeric version form; future
prerelease/other version spellings need deliberate review.

A broad case-expanded AppImage suffix chooses the **versioned** 20x asset, while
the pinned pipeline chooses `20x-linux-x86_64.AppImage` first in the saved response.
The narrower alias pattern preserves the URL identity on this observation.
The broad and narrow patterns both agree with upstream for 2fac. This validates
the proposed winners on the saved pages only; publication/name ordering, retained
history, structured-assets-only eligibility, freshness and acquisition differences
from 126 remain policy decisions. It does not prove all-history equivalence.

## Bounded payload evidence and remaining gates

Requested only bytes 0–4095 of each selected asset. Both servers returned HTTP
206 with the expected Content-Range total, and both prefixes contain ELF64 and
`AI` type-2 AppImage markers. Neither header proves payload architecture,
complete-file integrity, desktop entries, icons or executable behavior. The
2FAC API asset content_type says `application/zip`; its actual prefix is ELF,
so MIME metadata alone must not select the layout.

No full asset was acquired and no application code was executed. Full assets
would total 520,789,917 bytes; static payload extraction and full-file digest
verification are left to [129](../issues/129-inspect-two-candidate-appimage-payloads.md).
Available local static tools include unsquashfs and 7z. That follow-up should
inventory main/hidden/multiple desktop entries, Exec arguments (especially
`--no-sandbox`), icon paths and ownership/removal implications before approving
a concrete conversion plan. The inert lifecycle checks in 126 remain useful,
but cannot supply those real payload facts.

No new recipe or metadata was added for 4nier-patrimonio. No production recipe,
collection list, registry, installed file, module deployment, publication,
workflow or yadm pointer was changed during this evidence step.

## Offline replay

From the AM root, extract our trusted research archive into an empty temporary
directory, then replay the local comparison (no network):

```sh
mkdir -p /tmp/am-128-replay
sha256sum docs/track/release-catalog/research/two-candidate-upstream-evidence.tar.gz
tar -xzf docs/track/release-catalog/research/two-candidate-upstream-evidence.tar.gz \
  -C /tmp/am-128-replay
python3 /tmp/am-128-replay/compare.py /tmp/am-128-replay
```

Replay asserts both narrow selections equal the pinned old selection. The
replayed JSON was checked byte-for-byte against the recorded comparison. The
archive includes full repository/release JSON, receipt headers/hashes, the two
4-KiB prefixes, their receipts, comparison results and the replay script. Each
saved response/prefix hash was independently rechecked against its receipt.
Initial sandbox DNS failed; the four public metadata requests and two range
reads succeeded with reviewed network access. There was no API mutation or
asset execution.
