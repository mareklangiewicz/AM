# am-utils bounded release evidence and selector compatibility

2026-10-28. Partial stage of ticket [47](../issues/47-enroll-scoped-migration-sources.md).
Following the user's approval of the next bounded release read, exactly one
unauthenticated GET to the reviewed numeric endpoint was performed:

`https://api.github.com/repositories/1225768109/releases`

Local source revision: `0e7dcbb33e6da6c36189d71222e69f774e6b526c`.

HTTP 200; start 2026-10-28T19:20:28.498248+00:00, completion
2026-10-28T19:20:30.275464+00:00; monotonic duration **1.777211 seconds**.
No redirects, retries, conditional validators, pagination or binary downloads.
This is standalone public evidence, not a collector workflow run or publication.

## Retained transport evidence

- [Body](am-utils-release-20261028/body.json): **2,722,290 bytes**;
  SHA256 `679d4c67e284d6ae3d752be9d27b08890edfda93894280e8492fdd53daf58dd8`.
- [Headers](am-utils-release-20261028/headers.txt): **1283 bytes**;
  SHA256 `155ed07f87829227d88211c14f3fc224817d8668f7d4a2d83384b3a495593609`.
- [Machine report](am-utils-release-20261028/report.json) and
  [runner](am-utils-release-20261028/request.py) retain representation, request ID,
  exact times, public headers, process outcome and release-shape validation.

The numeric descriptor request ID is
`033cc5f80e8fbd7074c6a2e48cace911348e6ff63652618cbf8f3d95cdfb2700`.
Body satisfies existing storage release-shape validation: six public releases,
1750 assets. The one returned response is retained exactly; no Link was returned.
No assertion about future body size or route availability follows from one sample.

The parent bounds streamed body at 8,000,000 bytes and headers at 64,000 bytes,
with an overflow sentinel. Curl -q first, clean allowlisted environment, verified
direct HTTPS, HTTP/1.1, pinned API/Accept, identity encoding, no credentials/config/
proxy/netrc. Connect timeout 10 seconds, overall parent/curl deadline 30 seconds;
child reaped, exit 0, no parent termination. Existing report prevents repeat use.
The report's accepted=true means transport and response shape only, not family
compatibility or operational enrollment.

## Whole-family original selector audit

[Reproducible offline checker](am-utils-release-20261028/verify_selectors.py)
reads the frozen 356 paths, verifies APP/install/updater selector identity, and
requires each exact version line to match the expected original pipeline before
running it against retained bytes. It runs only fixed sed/grep/head selectors;
no installer, updater or asset executes. LC_ALL=C makes the audit reproducible;
the original selectors are case-insensitive and use ASCII match components here.
Recipe and body/queue hashes are retained in the
[full report](am-utils-release-20261028/selector-report.json).

| Result | Count |
| --- | ---: |
| Checked recipes | 356 (178 per architecture) |
| Differentially equal to original pipeline | 356 |
| Selected URL present in saved release assets | 354 |
| Missing result | 2 |
| Multiple matching URL tokens | 160 |
| Exactly one matching token | 194 |
| Selected non-asset URL | 0 |

Multiple matches retain original first-match policy; 160 recipes match two dated
versions. No sorting, date ranking or last/latest substitution was added.

The missing selectors are `programs/aarch64/c++filt` and
`programs/x86_64/c++filt`. Their dated assets exist, but GitHub's actual URLs use
`c%2B%2Bfilt`, whereas the patterns interpolate APP as `c++filt` into an extended
regex. There are two issues: the URL-encoding mismatch and unescaped regex
operators. An offline [diagnostic](am-utils-release-20261028/c++filt-diagnostic.json)
shows original and escaped-plus patterns both miss, while the URL-encoded pattern
finds actual asset URLs on both architectures. This is an existing selector defect
exposed by real metadata. Both recipes remain unchanged. The full 356-path family
must not be called compatible until this is explicitly repaired/reviewed; do not
silently change selector policy as part of enrollment.

## Resource meaning and remaining stages

The measured response is 34.03% of the current 8 MB cap. It provides actual
single-request cost, not a seven-source workflow/artifact/tree/history guarantee.
For scale only, adding this body to ticket 34's historical 4,898,621-byte six-source
tree yields 7,620,911 bytes **before seventh-source index/lookup overhead**. That
is arithmetic on evidence at different times, not a new merged candidate or
current remote size. No candidate artifact, live conditional repeat, publication
or history-growth measurement was performed. Keep existing resource/count
refusals intact until the coordinated implementation/review stage.

Next: review the c++filt exception and seven-source implementation contract,
replay the complete retained prior across storage/delivery/readers, then prepare
an exact collection/publication approval. Neither this read nor the authorized
six-source daily activation authorizes seventh-source operational enrollment.
Ticket 47 remains claimed/partial, and 48/49 remain blocked. No source push,
repin, workflow/schedule change or host operation occurred.
