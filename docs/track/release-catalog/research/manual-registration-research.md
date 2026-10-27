# Manual probe registration and isolation

Research date: 2026-10-27. No remote changes or workflow dispatch performed. Repository facts below were supplied by the parent agent; this research checked the controlling documentation and local gh help.

## Verified behavior

- `workflow_dispatch` requires the workflow to exist on the repository's default branch. A dispatch can then select another branch using `gh workflow run WORKFLOW --ref BRANCH`. The CLI describes this ref as the branch/tag containing the workflow version to run. [Manual runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow?tool=cli), [CLI run reference](https://cli.github.com/manual/gh_workflow_run).
- GitHub selects the workflow version associated with the event's commit/ref; this supports keeping the experimental workflow and script on `main-marek` while registering the same workflow path on default `main`. [Workflow trigger model](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows).
- Repository Actions disablement means no workflows run. Repository enablement is distinct from the state of each workflow. Thus five individually active workflows must be isolated before enabling the repository-wide switch. [Repository Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository).
- A workflow can be individually disabled using `gh workflow disable ID --repo mareklangiewicz/AM`, or `PUT /repos/mareklangiewicz/AM/actions/workflows/ID/disable`. Its resulting state is `disabled_manually`. Classic/OAuth tokens need `repo`; fine-grained credentials need Actions write. [Disable API](https://docs.github.com/en/rest/actions/workflows#disable-a-workflow), [CLI disable](https://cli.github.com/manual/gh_workflow_disable).
- Disabling a workflow does not cancel existing runs; existing runs must be checked independently. [Disable/enable guidance](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).

## Recommended staged plan

1. While repository Actions is still disabled, snapshot its permissions/policy, all workflow IDs and states, and any queued/in-progress runs. Explicitly list the workflows being isolated; do not enable repository Actions at this stage.
2. Obtain approval for disabling those existing workflows, registering one file on default `main`, and eventual repository-wide enablement. These are separate from approval to run a specific experiment. The user has required manual experiment control; no implicit dispatch.
3. Disable each pre-existing workflow individually while repository Actions remains off, then verify every state is `disabled_manually`. The docs describe this API but do not explicitly guarantee the endpoint's behavior while the repository-wide switch is off. If any disable/verification fails, stop with Actions still off.
4. Prepare a minimal commit against current remote default `main` adding only `.github/workflows/catalog-quota-probe.yml`. Do not merge the 871-commit development history or change the default branch. A useful registration file is a manual-only harmless stub, with the same path and name, read-only contents permissions, and a step explaining to dispatch `--ref main-marek`. It needs no checkout or script. The actual `main-marek` workflow at that path already invokes its own probe script. Alternatively copy the full workflow plus its script to `main`, but that is more default-branch churn.
5. Review and push that narrow registration commit while Actions remains off. Inspect both refs' workflow contents remotely. Keep the default-branch file manual-only; an accidental default-ref dispatch must be harmless if using the stub.
6. With all other workflows verified disabled and no unwanted queued runs, enable repository Actions preserving existing allowed-action and SHA-pinning policy. Recheck workflow registry and states. Enable the probe individually if required. If an unexpected workflow is active, turn repository Actions off and investigate before any experiment dispatch.
7. Only after an explicit instruction to run the probe, use `gh workflow run catalog-quota-probe.yml --repo mareklangiewicz/AM --ref main-marek`. Immediately identify the resulting run by event, head SHA, workflow, and branch; watch that exact run and preserve evidence. This selects the branch version, not the default-branch stub.
8. Keep pre-existing workflows disabled until restoration is explicitly wanted. Record baseline and resulting states in the Git-tracked ticket so a future restoration is intentional.

## Uncertainties and guardrails

- The cited documentation does not promise replay or non-replay of every event that occurred while Actions was disabled. Do not rely on an assumed no-replay guarantee. Manual-only triggers, disabled unrelated workflows, and a check for existing queued runs are the protections.
- The docs do not promise immediate workflow-registry appearance after adding a file while repository Actions is off. Verify after the narrow registration commit and again after enabling; never work around a missing registry entry by adding an automatic trigger.
- A successful CLI dispatch does not establish quota or cache behavior. Those measurements come from the actual run's statuses, headers, bodies, and GraphQL errors/cost.
- The registration commit and workflow-state changes are a proposed plan, not actions completed by this research.
