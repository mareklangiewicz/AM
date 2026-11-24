# Record twins and drop proven-gone releases

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: none

## Outcome

On today's format, as decided in
[Record same-tag and removed releases as facts](07-same-tag-and-removed-releases-as-facts.md):

- The collector records every returned release under its own ID even when tags
  repeat; `retention_v3.merge` no longer raises `same_tag_conflict` nor replaces
  an older release ID with the same tag.
- A retained release that the fetch proves gone (the fetch reached the end of
  the history, or returned an older release) is removed; one beyond the fetched
  page keeps its `observed_at`.
- The host parser drops its "duplicate exact tag" check; the page lists twins as
  separate entries.
- `same_tag_conflict` leaves the `failed_with` enum (schemas, host tables);
  ships with `release.py ship --ci NAME --repin-schemas`.
- Tests show the 14 twin sources' shape (two IDs, one tag, split assets)
  collecting, a recreated tag keeping both IDs while upstream lists both, and a
  deleted release removed only on proof.

The 14 stuck repositories should collect on their next turn; confirm in the
first catalog run after shipping.
