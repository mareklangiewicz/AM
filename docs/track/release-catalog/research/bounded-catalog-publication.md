# Bounded catalog expansion publication — November 6, 2026

Marek authorized pushing both prepared commits and publishing the 131-app /
128-source cohort. Source `42abcbc8e71ea2e0ee3000a5815c825976b78f6d` was pushed;
three sequential manual workflow runs succeeded, each attempting 52 sources with
zero failures. Their union successfully observed all 128 enrolled repositories.

| Run | Published pin | Apps / sources | CI job seconds |
| --- | --- | --- | --- |
| [42290499851](https://github.com/mareklangiewicz/AM/actions/runs/42290499851) | `e5bdc3de98e25c0e5197a833ff584dd528a3d58c` | 107 / 104 | 126 |
| [42293419706](https://github.com/mareklangiewicz/AM/actions/runs/42293419706) | `73629bbb0f35bb608e1e069d9a969ad53f2a69ec` | 131 / 128 | 162 |
| [42294451524](https://github.com/mareklangiewicz/AM/actions/runs/42294451524) | `e9d713eb74ca02dca24a5269ace5ee9e28466f41` | 131 / 128 | 195 |

Each exact pin was fetched and independently validated using the maintained
bounded reader in an isolated catalog-only Git repository. Canonical YAML and
cross-file references pass. Every snapshot retains all previous app identities,
matching configured numeric repository IDs and names. Untouched source documents
are byte-identical (52 / 76 / 76 respectively). The first batch adds new sources;
subsequent batches retain every previous release ID and never decrease effective
release observation times. All current collection statuses are successful.
Final snapshot has 21,703,160 YAML bytes, largest document 1,159,110 bytes;
no pending app identities. Each publication is a direct child of its exact prior
pin, starting at `bcae3298f5ffa1461a74ecab42df1a6c41d68492`.

[Portable receipt](bounded-catalog-publication.json) records per-source identities,
statuses, last-success times, document digests, job timing and log digests. Full
logs and local verifier are retained under
`/home/marek/Documents/Codex/am-catalog-expansion-20261106/publication/`.
The verifier initially refused the full AM checkout's size; it then passed using
an isolated catalog-only repository, without changing production tools or bounds.

The three-hour schedule and 128-source enrollment are now published in source.
This operation includes four source recipe migrations already prepared in 139,
but no installed policy/module/recipe refresh, app installation, binary update or
yadm pointer bump. Agent Skills remains catalog-only with its known icon-link
exclusion. No website rebuild, new browser/CORS/DOM/mobile acceptance or natural
scheduled-trigger observation is claimed. Full regression suites were not rerun;
shared mechanics did not change during publication. Broader GitHub coverage and
whole-snapshot scaling remain with ticket 138.
