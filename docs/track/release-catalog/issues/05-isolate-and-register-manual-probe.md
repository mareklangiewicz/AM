# Isolate existing workflows and register the manual probe

Type: task
Status: open
Triage: ready-for-human

## Question

How can we make the approved experiment available without triggering unrelated workflows or merging 871 development commits into main?

## Prepared result

[Research and sources](../research/manual-registration-research.md). While keeping Actions disabled, prepared local branch experiment/catalog-probe-registration at commit 43cceedf77f4dc46e647569ca6e2f63f14737b8b, parent origin/main 10900b9fc60069dbd39d185e914d71006dac5eb0. Its only change adds a harmless manual-only registration stub at the real probe's workflow path. Default-ref dispatch merely prints instructions; an explicit --ref main-marek uses the actual experiment. The live checkout remains main-marek. No branch was pushed for registration.

## Isolation plan requiring approval

1. Keep repository Actions off. Snapshot and individually disable the five existing workflows; verify disabled_manually for every one. Stop if any transition cannot be verified.
2. Push the single registration commit to default main using an ordinary fast-forward push. Stop if remote main moved; inspect and rebuild rather than force pushing. Also push the inventory/progress commit to main-marek when approved.
3. Enable repository Actions only after isolation is verified. Recheck registry and ensure the probe is the only active workflow. If an unrelated workflow is active, turn repository Actions off and investigate. Check pending runs.
4. Leave experiments unexecuted until Marek explicitly asks to run one. A future authorized run uses gh workflow run catalog-quota-probe.yml --repo mareklangiewicz/AM --ref main-marek.

## Baseline

2026-10-27: repository Actions enabled=false. Five individually active workflows: Auto-label AM or AppMan (329958059), Check archived and obsolete sources (329958061), Deploy Jekyll with GitHub Pages dependencies preinstalled (329958062), Language Manager (329958063), Sync Apps List (329958064). gh reported two historical runs, none pending. No Actions settings changed during preparation. Record state transitions and resulting refs here before resolving.
