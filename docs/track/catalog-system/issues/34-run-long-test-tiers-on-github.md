# Run the long test tiers on GitHub

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

The whole-tree tier and the container e2e run on GitHub, so a change can be
tested before `main-marek` moves and myxps is not tied up for 20 minutes per
run.

## Answer — November 17, 2026

`.github/workflows/long-tests.yml` ("Long tests") runs four parallel jobs on
any push to `ci/**` and on dispatch: tool suites plus collector fast tier,
whole-tree tier (`tree_*.py`), and `./test/e2e/run` for Debian and Fedora
with podman. Collection runs only from `main-marek`, so a `ci/*` branch needs
no repin. Use: push the commit as `ci/<name>`, move `main-marek` once green.
The collector README says so.

First run 44071909464 on `ci/format-3-collection`: whole-tree tier and both e2e
targets green; the fast tier found three real step B regressions (ticket 25),
fixed in `585e01a69`. Rerun 44073540711 on `585e01a69`: all four jobs green.

Not covered: the Termux e2e target.

## Comments

November 17, 2026 (retro): in `~/code/shell/AM`, `gh` resolves to upstream
`ivan-hc/AM` (`gh variable list` answered 403), so every call needs
`-R mareklangiewicz/AM`. A one-time `gh repo set-default mareklangiewicz/AM`
(local git config, nothing pushed) would remove that; not done.
