# WezTerm redirect boundary — 2026-10-27

After the failed baseline, Marek agreed to investigate the redirect. One separate unauthenticated public GET was made to https://api.github.com/repos/wez/wezterm/releases?per_page=100, with API version 2022-11-28. curl did not follow redirects and no experiment workflow was dispatched. Response Date: 2026-10-27 11:57:32 UTC.

GitHub returned HTTP 301 with Location https://api.github.com/repositories/120568143/releases?per_page=100. The JSON error body names the same target. This establishes the observed redirect destination, not the current owner name, its cause, target success, or future stability. The target was not queried.

Prepared change: explicitly replace this one experiment endpoint with the observed repository-ID URL, retaining query parameters and keeping automatic redirects disabled. This avoids an extra GET within the six-attempt budget and records the actual source in the manifest. It does not change app recipes or imply that all old and new bodies are semantically interchangeable. Previous manifests have a different endpoint map and cannot seed the replacement experiment.

Also retain Location in the response-header allowlist and save/hash bounded HTTP failure bodies before stopping. Bodies over the 10 MiB cap are not saved. An offline regression uses urllib HTTPError(301) to verify one attempt, no redirect follow, Location/error-body retention, header allowlisting and complete=false. All eight fixture tests pass.

Evidence files: 20261027-wezterm-redirect.headers and 20261027-wezterm-redirect.json. The header file is whitespace-normalized for Git (LF line endings, trailing spaces and the final blank separator removed). These are public response data from this separate local investigation, not recovered evidence from run 40499617203. No token was supplied.

No push or replacement baseline has been performed. The six-attempt limit, no-retry rule and individual run authorization remain in force.
