# AM metadata request inventory

Measured 2026-10-27 against recipe files at main-marek commit 4a2083e2a4ca921addfcfae2bacec59349f55b1c. This is static discovery, not a collection manifest or a live availability check. No installer or updater was executed.

## Method

The new tools/catalog-probe/inventory.awk and inventory.sh scan every file directly under programs/x86_64 and programs/aarch64. They emit file/line references, literal API URL tokens, comment/code context, conservative endpoint classification, and version-line discrepancy flags. Shell variables remain unresolved. Quotes around a URL word are removed, and closing command-substitution parentheses are trimmed. This lexer is not a shell parser: multiline constructions, concatenated variables, conditional branches, heredocs, dead code, and generated requests need review. Code-context occurrences include updater templates; they are not runtime request counts.

For reproducibility, run from the fork root: `sh tools/catalog-probe/inventory.sh /tmp/am-request-inventory`. The generated source revision describes recipe inputs; the inventory scripts themselves are introduced after that revision. Candidate URLs must be reviewed rather than automatically collected.

## Counts

| Measure | x86_64 | aarch64 |
| --- | ---: | ---: |
| Recipe files | 8,899 | 1,787 |
| Files containing a code-context API URL | 8,641 | 1,774 |
| Code-context API URL occurrences | 17,373 | 3,558 |
| Distinct extracted URL strings, including unresolved forms | 8,328 | 1,581 |
| Files with nonidentical version= lines | 48 | 12 |

The version-line flags compare all version= lines after trimming surrounding whitespace. They include non-GitHub/version-identity cases and are broader than the old classifier's rejection count; they do not prove semantic disagreement.

Across both architectures:

| Classification | Occurrences | Distinct literal strings |
| --- | ---: | ---: |
| Release list, including query variants | 19,638 | 7,988 |
| Latest release | 1,102 | 348 |
| Named release tag | 4 | 1 |
| Events | 2 | 1 |
| Other repository APIs (ordinary tags) | 4 | 2 |
| Dynamic shell-variable forms | 164 | 4 |
| REPLACETHIS template placeholders | 17 | 2 |

There are **8,337 distinct literal release-request URLs**, not verified valid endpoints. x86_64 and aarch64 share 1,559 of these strings; 6,760 appear only in x86_64 and 18 only in aarch64. Literal repository paths normalize to 8,319 owner/repository spellings across static classes. Renames, redirects, case variants in full URLs, dead code, and shared aliases may change a reviewed inventory. Dynamic forms appear in 91 recipe files and remain unresolved even when a human could infer a literal SITE assignment.

Five distinct literal query-bearing URLs request per_page=100: hockyy/miteiru, ivan-hc/Blender-appimage, sqlitebrowser/sqlitebrowser, toeverything/AFFiNE, and wez/wezterm. Other list requests inherit API default pagination unless scripts build a request dynamically. No completeness beyond the requested response is implied.

## Concrete compatibility boundaries

- programs/x86_64/wezterm-nightly:15 reads events for update identity, while line 16 reads releases?per_page=100 for a download. A release-only catalog cannot replace the former. Lines 36 and 45 repeat these roles in its updater template.
- programs/x86_64/trans and watched read ordinary Git tags, not release objects. Tag endpoints are outside the initial release scope.
- programs/x86_64/appimageupdatetool:14 and :33 interpolate SITE. Its fork-specific updater also records the URL actually used by appimageupdatetool's embedded zsync update, rather than assuming the scraped release URL identifies the installed binary. A catalog cannot silently replace this behavior.
- REPLACETHIS strings appear inside generated updater content; they are template artifacts, not approved upstream repository requests.
- APP-MANAGER:2160 onward launches each installed AM-updater as a separate executable. Those updaters contain their own network commands. A metadata helper in the manager alone will not redirect them; define helper availability and an explicit migration.
- This fork already pins ALT_GH to api.github.com and restores old proxy hosts; experiment code does not change app-management behavior.

Primary source: the recipe files and APP-MANAGER at the recorded commit. Historical comparison: docs/design/version-catalog.md and tools/proto-catalog/classify.awk at proto/release-catalog d33ccb4c0. Re-running the old classifier against current inputs reproduced **7,230 x86_64 and 1,267 aarch64 classified rows**. Its x86_64 version-disagreement rejection count remains 42; the broader inventory flags should not be conflated with that convention-based classification.

## Capacity implications, not measured runtime results

Using the documented normal 1,000 REST requests/hour workflow-repository budget, checking each of the 8,337 literal release URLs once per day would average **347.4 requests/hour**, before retries, unresolved requests, new pages, and other consumers. An example cap of 500 checks/hour would complete that bounded inventory in about 17 hourly batches, leaving nominal headroom. This is arithmetic, not an agreed operating cap or proof of scheduler/freshness behavior.

Therefore a 24-hour target does not inherently require GraphQL batching or successful 304 cache savings. A full hourly REST sweep would exceed the ordinary primary budget. Preserve these separate claims. The real workflow-token probe still needs an isolated manual run; long-term ETag hit rate, response churn, payload size, and Git growth need a subsequent measurement experiment.

Official rate-limit source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api . The prior reported 825 GraphQL-point sweep concerns a narrower projection plus CI selection, not equivalent full REST observations.
