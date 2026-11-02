# Catalog YAML design interview

Provisional design constraints agreed with Marek on November 2, 2026.
This records design discussion; implementation awaits shared-understanding confirmation.

- Simplify the published catalog into a defined YAML subset. Do not distribute raw upstream JSON responses; publish important release facts.
- The catalog offers observed release facts. Clients retain decisions about which release to install, browse, present, or otherwise use.
- Human inspection, understandable diffs, and named-field extraction with short POSIX awk scripts are acceptance criteria.
- Published files must be valid YAML; the shell reader accepts a precisely specified subset with explicit string rules and rejects unsupported syntax.
- Prefer a simple, fast coordinated migration. This fork has one user and few installed apps; prolonged compatibility ceremony is unnecessary.

Open: release coverage/completeness; important fields; meaning and limits of trusted observations; YAML grammar; storage layout; client selection compatibility; freshness and failure handling.

## November 3 answers

- Release coverage remains undecided: prefer multiple available releases, but bound acquisition if full history consumes excessive GitHub quota.
- Trust boundary: Marek trusts the known, inspectable AM workflow on official GitHub-hosted runners, acquiring metadata only from GitHub API. Avoid redundant provenance fields; publication commit time is proposed as catalog timestamp. Per-source freshness consequences remain under discussion.
- Agreed normalized fields: source/release identity, tag, title, release page URL, publication/update times, prerelease status; all assets with identity, original name, download URL, byte size, content type, and upstream digest when available; observation time and acquisition status (timestamp representation still under discussion). No release notes or author profiles initially. Clients interpret architecture/package type and choose assets.
- Adapt consumers directly and verify equivalent release/asset choices before switching publication. No prolonged dual-format rollout.

Primary documentation checked: GitHub List releases supports per_page up to 100 (default 30), with page parameter. GitHub Actions GITHUB_TOKEN primary quota is 1,000 requests/hour/repository, with secondary limits also applicable. More releases per page do not themselves add primary request counts; pagination adds requests. Response size and runtime remain separate costs.
Sources: https://docs.github.com/en/rest/releases/releases#list-releases and https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
