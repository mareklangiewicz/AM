# Maintained YAML capacity rehearsal

Ticket 95: synthetic local measurements at runtime baseline ff2dc1499 with exact
policy digest d464ee0c14d8712ef625d47308d8faf47f5faf459fc565b926d2952d98a73e7b.
Reproduce cases serially:

```
/usr/bin/time -f '%U %S %M' python3 -B tools/catalog-yaml-prototype/capacity.py ordinary
/usr/bin/time -f '%U %S %M' python3 -B tools/catalog-yaml-prototype/capacity.py dense
/usr/bin/time -f '%U %S %M' python3 -B tools/catalog-yaml-prototype/capacity.py growth
/usr/bin/time -f '%U %S %M' python3 -B tools/catalog-yaml-prototype/capacity.py saved
```

Recorded JSON is tools/catalog-yaml-prototype/capacity-results.json. No HTTP,
credentials, workflow dispatch, remote Git or installed change is involved.
The current 49 real manifest identities/255 app names and static enrollment are
used for the ordinary shape, but all release/asset facts in that case are synthetic. The separate saved case
uses historical hash-checked real responses and original receipt times. Reruns
record their checkout revision; emitted schema/context hashes change with that pin.

| Case | Result | YAML bytes | Local wall seconds | CPU seconds | Largest-process RSS KiB |
| --- | --- | ---: | ---: | ---: | ---: |
| 49 sources × 100 releases × 8 assets | Full normalized artifact staged and verified | 13,297,011 | 287.855 | 287.32 | 103,884 |
| One scoped source × 100 × 80 assets | Failed-source metadata only; job would refuse publication | 529 | 1.764 | 1.90 | 48,528 |
| Retain 100 new releases/round, 8 assets each | Round eight refused, prior 700 retained | 1,866,872 failed document | 20.810 | 20.93 | 89,324 |
| 41 saved real list responses | Normalized canonical tree validated | 5,261,143 | 70.480 | 70.09 | 123,412 |

Ordinary: 49 requests, 12,525,709 response bytes, 4,900 releases, 39,200 assets,
largest repository YAML 305,994 bytes, receipt 96,051 bytes. All sources succeed.
It exercises the maintained collect_stage path and an additional read_staged
validation; its wall time includes that extra read. This is not a full publisher
job or end-to-end workflow timing. Mock transport advances a logical clock by one
second per request (49 total); that is not observed API latency or proof that the
real default completes inside the 300-second transport budget. Validation/staging
remain outside that budget.

Dense: a schema-2 manifest scoped to one existing identity is explicit. The
2,434,589-byte JSON response fits the 8,000,000-byte response cap, but normalized
retained YAML exceeds the 2,097,152-byte file cap. Collection records an honest
collection_limit failure without releases/observations; it stages metadata for
review, and the proposed workflow's all-ok job gate would fail. This is not a
successful 49-source dense run.

Growth: seven successful retained sets reach 700 releases / 1,866,839 bytes;
merging another 100 exceeds 2 MiB. The failure document is 1,866,872 bytes and
preserves all prior records, schema, shared/overridden observations and last
success. No eviction or partial merge occurs. This intentionally high synthetic
arrival rate is not an estimate of real daily repository growth.

Saved: 27,821,797 raw bytes, 914 releases / 14,242 assets; largest repository YAML
1,251,974 bytes. Body lengths/hashes match saved reports and receipt times are
preserved. Forty responses are page size 30, one is page size 100; three latest
endpoint bodies are excluded. This normalizes saved facts and validates the tree;
it does not exercise fresh default acquisition, full staging context or real
transport duration. It agrees with earlier replay quantities on the maintained
runtime, rather than establishing the missing full-default live capacity.

GNU time reports aggregate child CPU and maximum RSS of a single process, not
aggregate peak memory. Python and shell/awk validation are included. Harness
limits are 768 MiB address space and 180 CPU seconds per process, inherited by
children; they are measurement controls, not an aggregate deadline or new runtime
worker layer. Measurements are serial local evidence, not hosted-runner capacity.

The profile remains unaccepted. This evidence shows both a plausible ordinary
shape and concrete dense/retained-growth refusal: one page of 100 cannot bound
asset density or accumulated retention. Do not silently increase caps, evict
records or mark a failed source successful. A future bounded read-only real
49-source/100-release measurement must separately measure actual response bytes,
source outliers, API duration and runner costs before operating budgets are
accepted. Earlier saved-response evidence (mostly page size 30) is not a substitute.
