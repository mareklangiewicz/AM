# Version catalog instead of one script per app

Notes from 2026-10-20. Direction only. Items under "Still open" are not chosen.

## Direction

The maintenance problem is inside AM. Most files in `programs/x86_64/` are the AppImage template with a different `version=$(curl … api.github.com … | sed | grep | head)` line. See `templates/AM-SAMPLE-AppImage` and `programs/x86_64/astra`. The rest of the script is directories, wget, optional archive extract, chmod, symlink, desktop and icon, and an `AM-updater` that repeats the same fetch.

For a normal GitHub release, that per-app file should stop being a shell script. One shared installer takes parameters from a catalog. Adding an app is adding a row. The code to audit is the shared installer, plus the rows that are not the common case.

Apps that are not a single GitHub release asset stay as scripts. Examples already in the templates: portable2appimage, ghcr, multi-choice installers, LibreOffice. How large that set is has not been counted.

## Why a catalog, not the pkgforge proxy

Upstream rewrites `api.github.com` to `https://api.gh.pkgforge.dev` when the REST budget is low (`ALT_GH` in `APP-MANAGER`, and the install path in `modules/install.am`). The proxy's JSON chooses the download URL. Checksums are taken from that URL, so a bad answer still verifies. With `am apikey`, the rewritten request can send the token to the proxy.

`main-marek` pins `ALT_GH` to `https://api.github.com` (`a47ce8850`, `db72e07ff`). Updates fail until the limit resets. Unauthenticated REST is 60 calls per hour per IP, and each installed GitHub app costs one call.

A workflow in this repo (a repo the user already trusts, because they already run its install scripts) calls the API, applies each app's asset rule, and publishes the chosen URLs. `am -i` and `am -u` download that file from raw GitHub or a release asset. Those downloads are not the REST core quota. The user's machine then wgets the asset from GitHub's CDN. No third-party API proxy.

A bad workflow or a bad row can still publish a bad URL. That is the same trust as today's scripts. It is not an outside proxy.

## Still open

These are the current lean, written down so the next pass can drop them. None of them is a commitment.

- **File format.** TSV is the lean: one app per line, TAB-separated, read with `awk -F '\t'`, no `jq`, and no `sed` JSON splitting on the client. JSONL is the alternative if a parser on the install path is acceptable. It diffs well and suits a Python generator. It is a worse fit for POSIX `sh`. Plain JSON is a poor client format for the same reason. Revisit before any file is generated.
- **One file or two.** The lean is a small recipe catalog (name, kind, repo, how to pick the asset) reviewed by humans, and a resolved catalog (name, tag, url, size, published) rewritten by the workflow and only read by `am`. A single file that stores both the rule and the last resolved URL may be enough and easier to explain. Not settled.
- **How an asset is chosen.** The lean copies today's filters: an include pattern and an exclude pattern, basic regular expressions, evaluated only on the runner. Named fields (`suffix=AppImage`, `arch=x86_64`) might cover the common rows with less regex. Not surveyed against the real scripts.
- **Kinds.** `appimage`, `archive`, and `binary` are guesses from the templates. The shared installer should grow a kind only after a count of how many scripts that kind would replace.
- **Stale or missing row.** The lean is: that one app falls back to a live API call, and the run does not use the proxy. Always trusting the snapshot, or refusing to update when it is old, are both plausible. Not chosen.
- **Workflow budget.** One REST call per repo per scan, deduplicated. A maintainer PAT is 5000 requests per hour. `GITHUB_TOKEN` on Actions is 1000 per hour per repository. Daily and incremental is the lean. Schedule, token type, and what "unchanged" means are not designed.
- **Integrity of the published file.** Signing or pinning a commit is optional extra trust. Not required to beat the proxy, and not decided.
- **Where it lives.** This fork first. Whether any of it is offered upstream is a later question.
