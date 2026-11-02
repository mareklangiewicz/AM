# Bounded release-history measurement — November 3, 2026

## Result

A reproducible uniform random sample of 24 of the active inventory’s 772 distinct upstream repository IDs required 26 list-release requests to acquire complete release pagination for the sampled repositories. Twenty-three fit in one page; one had 227 releases across three pages. This supports considering complete-history collection, but does not establish the cost of a full census or rule out repositories with very large histories.

| Measurement | Observed sample |
| --- | ---: |
| Distinct repositories | 24 |
| API requests | 26 |
| Release records | 751 |
| Embedded asset records | 6246 |
| Raw API response bytes transferred | 13,117,687 |
| Provisional normalized YAML bytes | 2,338,942 |
| Elapsed seconds | 27.2289 |

The sample used 8.3% more requests than one list page per repository. It used fewer requests than the 48 that one page plus a separate latest request would use for these same repositories; the design now deliberately drops the GitHub latest designation and gives selection rules to clients. These comparisons concern this sample, not all 772 repositories.

## Method and bounds

Run from the AM repository root:

```sh
python3 docs/track/release-catalog/research/yaml-history-measurement-20261103/measure.py
```

The script follows the 16 manifests in the active `appimage-exceptions-next-20261102/prepared/inventory.json`, deduplicates numeric repository IDs, sorts them, and samples 24 with Python random seed `20261103`. It requests numeric GitHub API `/repositories/ID/releases?per_page=100&page=N` URLs. First-page Link headers determine page counts; remaining pages are acquired only when their count fits the remaining request budget. All sampled histories fit. No sampled pagination produced duplicate release IDs.

Hard configured bounds: 48 API requests, 16 MiB per response, 120 MiB aggregate response bytes, 180-second overall initiation deadline with remaining-time request timeouts. Sequential requests, no retries, no redirects, no proxies. A sandboxed initial run stopped after a transport failure with zero response bytes. The separately authorized network-enabled run used gh’s existing authenticated credential in memory and completed without API refusals. No token, auth headers, raw release bodies, asset URLs, signed URLs, or JWTs are retained in evidence. No app binary was fetched or executed. No production catalog, source pin, workflow, installed helper, or upstream state was changed.

`results.json` records per-repository/page counts, sizes, timings, pagination, and numeric quota remainder. The provisional serializer in `measure.py` computes byte size in memory only. It includes release identity, tag/title/page URL/times/prerelease and asset identity/name/download URL/size/content type/digest when supplied. Its exact field names, null handling, and empty mappings are not a proposed finalized schema; per-repository schema/observation headers are not included in that size estimate. This is a size experiment, not implementation of the new format.

## Limits and interpretation

- This is a 24-repository sample, not a census. The observed 1/24 fraction over 100 releases is too small a sample to confidently characterize the entire inventory, especially rare repositories with thousands of releases. A naive linear projection would be about 836 requests, 422 MB raw response traffic, and 75 MB normalized YAML, but those are illustrative sample extrapolations, not capacity guarantees.
- Complete means the API list pagination reached a response with no next page during this run. It does not include drafts unavailable to these credentials, bare Git tags, historical/deleted releases, or a transactional snapshot across mutable pages.
- Embedded asset lists were counted as returned by release responses; independent asset pagination/completeness was not audited. We must settle how to detect or handle any upstream embedded-asset limits before claiming complete asset inventories.
- API ordering is not a promised selection rule. Clients must choose using fields, not record position.
- Runtime measured locally with this network/credential is not GitHub runner duration. Conditional requests, Git storage growth, full-inventory outliers, normalization CPU, and future history growth are not measured.
- A once-per-run page cap and explicit partial coverage may still be appropriate even if the normal policy becomes full pagination. That is a design decision, not settled by this experiment.

## Sample detail

| Repository ID | Releases | API pages | Raw bytes | Projected YAML bytes |
| --- | ---: | ---: | ---: | ---: |
| 77793775 | 1 | 1 | 9,879 | 1,813 |
| 120568143 | 64 | 1 | 2,935,397 | 582,176 |
| 134030857 | 39 | 1 | 314,892 | 50,652 |
| 159577551 | 12 | 1 | 69,231 | 12,072 |
| 1234036192 | 1 | 1 | 28,798 | 5,169 |
| 1231334462 | 227 | 3 | 3,422,622 | 532,223 |
| 115342681 | 7 | 1 | 33,990 | 6,158 |
| 46184935 | 10 | 1 | 85,097 | 15,722 |
| 1135743227 | 63 | 1 | 414,334 | 63,487 |
| 230754486 | 48 | 1 | 696,625 | 107,402 |
| 1136495056 | 53 | 1 | 1,173,364 | 217,870 |
| 1379205525 | 6 | 1 | 231,430 | 46,846 |
| 1312293010 | 59 | 1 | 992,723 | 196,404 |
| 1333808333 | 14 | 1 | 155,524 | 24,072 |
| 1099962703 | 13 | 1 | 78,393 | 12,626 |
| 103708670 | 9 | 1 | 165,948 | 29,317 |
| 146724162 | 10 | 1 | 144,445 | 25,652 |
| 857418119 | 28 | 1 | 508,758 | 82,963 |
| 153924058 | 18 | 1 | 81,640 | 15,402 |
| 407838094 | 2 | 1 | 10,363 | 1,852 |
| 1272378195 | 21 | 1 | 459,203 | 93,613 |
| 1078137951 | 29 | 1 | 956,709 | 187,953 |
| 147603441 | 12 | 1 | 125,034 | 23,606 |
| 365366353 | 5 | 1 | 23,288 | 3,892 |

## Primary references

- [GitHub List releases API](https://docs.github.com/en/rest/releases/releases#list-releases): page size up to 100, page parameter, published release visibility.
- [GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api): request-based primary limits plus secondary limits.

All measurements are observations at the time in `results.json`, not permanent source guarantees.
