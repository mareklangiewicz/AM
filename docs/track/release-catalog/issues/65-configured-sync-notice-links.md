# Show configured sources in synchronization notices

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User observed upstream links after successful fork synchronization. Recipe-change
notices must link to the actual APPSDB recipe, and manager sync summaries must
identify the actual AMREPO manager source. Avoid assuming GitHub hosting or a
particular branch. Reporting-only change; no host sync or publication.

## Answer

Recipe notices now print APPSDB/scriptname literally; both manager-sync result
branches print AMREPO/APP-MANAGER as Source. These are actual configured source
URLs rather than fabricated GitHub browse/history links. Bash syntax and diff
checks pass; notice rendering checked with fork, alternate HTTP and file sources.
No behavior change, network request, host delivery or source push.
