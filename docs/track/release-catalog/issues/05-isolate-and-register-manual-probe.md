# Isolate existing workflows and register the manual probe

Type: task
Status: resolved
Triage: ready-for-human

## Question

How can we enable the manual experiment without allowing unrelated workflows to run?

## Registration resolved

2026-10-27: Marek approved making main-marek the fork's default branch. Applied via gh repo edit and verified default_branch=main-marek. GitHub immediately registered Catalog quota probe (398162689), individually active. Repository Actions remains enabled=false; nothing was dispatched.

The former one-file main registration proposal is superseded. Its local branch experiment/catalog-probe-registration at 43cceedf77f4dc46e647569ca6e2f63f14737b8b was never pushed and is not needed. Keep main unchanged. Historical [registration research](../research/manual-registration-research.md) remains useful for manual dispatch semantics, but its branch-topology assumptions no longer apply.

## Isolation plan requiring approval

1. Keep repository Actions off. Snapshot and individually disable the five unrelated workflows; verify disabled_manually for every one. Stop if any transition cannot be verified.
2. Enable repository Actions only after isolation is verified. Recheck registry and ensure the probe is the only active workflow. If an unrelated workflow is active, turn repository Actions off and investigate. Check pending runs.
3. Leave experiments unexecuted until Marek explicitly asks to run one. A future authorized run uses gh workflow run catalog-quota-probe.yml --repo mareklangiewicz/AM --ref main-marek.

Push pending inventory/progress commits only with approval under the inherited home AGENTS.md convention.

## Baseline

2026-10-27: repository Actions enabled=false. Five individually active unrelated workflows: Auto-label AM or AppMan (329958059), Check archived and obsolete sources (329958061), Deploy Jekyll with GitHub Pages dependencies preinstalled (329958062), Language Manager (329958063), Sync Apps List (329958064). Probe: Catalog quota probe (398162689), individually active but prevented from running by repository disablement. gh previously reported two historical runs, none pending. The default-branch change is completed; no Actions enablement, individual workflow-state change, or dispatch has occurred. Record those transitions here before resolving.

## Answer

2026-10-27, after Marek said go on to the described isolation/enablement step: confirmed repository Actions was off and there were no pending runs. Disabled workflows 329958059, 329958061, 329958062, 329958063, and 329958064 using gh workflow disable. Verified disabled_manually individually and verified the probe (398162689) was the only individually active workflow before enabling repository Actions.

Enabled repository Actions via PUT actions/permissions with enabled=true. Re-read permissions and every workflow state: Actions enabled, allowed_actions=all, sha_pinning_required=false; all five unrelated workflows remain disabled_manually; Catalog quota probe is the only active workflow. No pending runs. Default remains main-marek. No workflow was dispatched. This resolves setup; explicit authorization for the bounded probe run remains separate.

Keep unrelated workflows disabled until Marek explicitly wants them restored. If additional workflows are introduced or state changes, repeat the isolation check before an experiment.
