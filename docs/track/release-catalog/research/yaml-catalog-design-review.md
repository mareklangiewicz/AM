# YAML catalog design — shared-understanding checkpoint

Status: shared understanding confirmed by Marek; schema/reader experiment completed. See [findings](yaml-reader-experiment.md) for the proposed escape extension and remaining resource-policy work.

## Published model

Replace published raw release responses, JSON index and TSV lookup with a precisely defined YAML subset. Publish one repositories/ID.yaml file per upstream numeric repository identity and a small YAML app-to-repository map. Store readable owner/name in each repository record. A format version and immutable source documentation URL identify the schema.

Collect all published release pages, including prereleases and excluding drafts, without a separate latest request. Clients define latest and choose releases/assets using facts, not record order. Existing /latest consumers require explicit selection review rather than an identical-behavior promise. Source archive links and all embedded uploaded-asset records are retained. Complete release pagination does not claim independently audited embedded-asset completeness or a transactional cross-page snapshot.

Fields: repository identity; release ID, tag/title/page URL, creation/publication/update times where upstream provides them, prerelease flag; asset ID, original name, download URL, size, content type, upstream digest when available; source archive URLs. Omit release notes, authors/profiles and other unused upstream fields. Missing optional values are omitted, not null.

## Format

Fixed schema keys, spaces-only indentation, ID-keyed mappings in deterministic order. Scalars are quoted strings, schema-defined integers, and true/false booleans; {} is the sole empty mapping syntax. Strings are literal UTF-8 on one physical line with only quote/backslash/newline/carriage-return/tab escapes. No arbitrary YAML tags, anchors, multiline scalars, sequences or implicit string typing. Precise depth/indentation/order, integer bounds, duplicate-key rejection and unsupported-character handling will be specified and tested in the parser experiment, without adding general YAML support.

Timestamps are quoted UTC YYYY-MM-DDTHH:MM:SSZ values at whole-second precision. No duplicated epoch fields. Git commit time is publication time; per-source checked_at represents successful validation time.

## Observations and failure

Apply explicit per-repository and aggregate request/byte/runtime ceilings. No retry or ceiling policy may silently convert an incomplete history into a complete observation. Choose concrete budgets using broader measurements before production rollout; the existing 24-source sample does not bound outliers.

A successful empty result has releases: {}. On a later failed check, retain the previous complete observation and its checked_at; publish a small failed status/reason. Before the first successful check, publish identity/status without release data or checked_at. Reasons distinguish rate limiting, transport failure, invalid response and collection ceilings; detailed arbitrary errors stay in workflow logs. Pagination must be checked for detectable inconsistency such as duplicate IDs; upstream mutation means no transactional completeness claim.

## Trust and consumers

Trust the reviewed AM workflow, GitHub-hosted runners and GitHub API acquisition. All files used by a client command come from one pinned Git commit over GitHub HTTPS. No per-catalog-body checksum/size ledger or raw-JSON compatibility reconstruction. Keep transfer bounds and simple structure validation. Upstream asset digests are separate facts.

Shared POSIX shell/awk reader: validate; list release or asset IDs one per line; read a named scalar with decoding. Missing fields differ from false/zero/empty-string values. Clients implement selection and freshness policy. Initially preserve the 48-hour installation freshness rule and explicit stale override; browsing can show old facts with status. Demonstrate a small strict parser against malformed and valid cases first; reconsider grammar/consumer validation if this proves cumbersome.

## Migration and work order

One user, few installed apps: direct coordinated publication/consumer migration, without prolonged dual-format rollout. No production change until the design checkpoint is confirmed. Then:

1. Write exact schema/subset documentation and a disposable reader/validator experiment with adversarial fixtures.
2. Measure wider history/size outliers and settle operational budgets. Do not overstate asset completeness.
3. Implement normalization/publication and adapt consumers to explicit selection rules; compare existing choices where applicable and document deliberate latest-policy changes.
4. Validate and review local work; publication, exact daily source repin, and host delivery are separate explicit operations. No push or workflow dispatch authorized by this checkpoint alone.

Natural November 3 production run observation/acceptance is separate outstanding work, not established by this format research. Existing local commits advance source beyond the last recorded daily pin; recheck actual remote controls before publication decisions.

## Representative repository file

Illustrative IDs, times, URLs and sizes; not live release evidence. Schema URL SOURCE_COMMIT stands for the exact source revision containing the documentation.

```yaml
format: 2
schema: "https://raw.githubusercontent.com/mareklangiewicz/AM/SOURCE_COMMIT/docs/catalog-format-v2.md"
repository_id: 123
repository: "example/app"
checked_at: "2026-11-03T01:00:00Z"
check_status: "ok"
releases:
  "456":
    tag: "v2.0.0"
    title: "Version 2.0"
    url: "https://github.com/example/app/releases/tag/v2.0.0"
    published_at: "2026-11-02T12:00:00Z"
    prerelease: false
    source_zip_url: "https://api.github.com/repos/example/app/zipball/v2.0.0"
    assets:
      "789":
        name: "App-x86_64.AppImage"
        url: "https://github.com/example/app/releases/download/v2.0.0/App-x86_64.AppImage"
        size: 123456
        content_type: "application/octet-stream"
```

## Evidence

[Interview decisions](yaml-format-design.md), [bounded history measurement](yaml-history-measurement-20261103/findings.md), [architectural boundary](../../../adr/0001-catalog-facts-and-client-selection.md).
