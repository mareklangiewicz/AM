# Exact-prior catalog delivery

Ticket 18, 2026-10-27. This wires the accepted observation-storage boundary into
manual remote delivery for the same six sources. Marek approved continuation,
pushes and workflow runs. New operational branch: release-catalog in this fork;
it was verified absent before implementation. No schedule or installer change.

## Workflow and credentials

One manually dispatched workflow has two jobs and workflow-level non-cancelling
concurrency. Both check out exact github.sha with persist-credentials:false and
verify current/source/workflow/approved SHAs plus manifest hash. The collection
job explicitly has contents:read only. Its token loads the prior catalog from this
repository separately from release transport, then the same isolated supervised
transport reads only the six numeric upstream descriptors. The prior commit is a
new explicit full-SHA input; an empty value is allowed only when the publication
branch is absent. Any mismatch refuses before starting release workers.

The separate publisher job needs successful collection, has contents:write and
actions:read, and receives its own built-in token only in its publication step.
The token is repository-scoped write authority, not branch-scoped authority;
reviewed code restricts writes to refs/heads/release-catalog. No writer credential
is passed to upstream transport, an artifact or a client. No PAT/App fallback is
accepted. Existing action pins are unchanged and no downloader action is added.

Git network operations use a clean environment, disabled global/system config and
hooks, an ephemeral HTTP auth header in process environment, no credential file or
argv token, fixed HTTPS repository URL and fixed ref. gh artifact requests use a
separate empty config directory and explicit step token. Command stderr is discarded
and exceptions use fixed diagnostics. Each delivery command has a deadline/output
bound; Git object storage is monitored against 128 MB. A shallow prior fetch is
revalidated as a closed regular-blob tree. These are application bounds, not a
hard real-time/disk-allocation guarantee under OS scheduling.

## Prior state and conditional requests

Read the remote ref once and compare it to the exact input (or verified absence),
then shallow-fetch that branch to a fresh local bare repository with no configured
remote. Verify the fetched SHA still equals the input. Read blobs as data without
checkout, hooks, submodules or code execution; enforce regular 100644 modes,
expected paths and index/body/tree caps before applying full storage validation.
Refuse a future prior generation. Match exact request IDs; only available matching
observations supply Prior bytes/digest/time/validators to collector planning.
Changed descriptors never inherit validators. Missing/corrupt priors do not cause
an unconditional fallback or an implicit collection retry.

Storage receives the actual prior tree, so successful 304 responses retain bytes
and receipt time while advancing measured validation. New 200 responses replace
bytes normally. Live publication currently requires all six attempts to complete
as observed/validated; a failed collection preserves the previous remote catalog
and retains inert artifact evidence. It does not publish a partial new generation.
The underlying pure storage module supports failure retention but this workflow
uses that conservative all-six publication gate.

## Artifact boundary and recomputation

The upload action returns an immutable artifact ID/digest to the dependent job.
The publisher retrieves that exact artifact metadata and ZIP, not an arbitrary
latest run/name. Verify name/run/attempt, source SHA, repository/head repository,
branch, expiry, size and API digest against trusted context/job outputs; verify
SHA256 of the downloaded ZIP. The action/REST service supplies this provenance;
it is not an independent cryptographic code-approval mechanism.

Bound metadata, compressed bytes, member count and total declared uncompressed
bytes. Inspect every member before bounded reading; reject duplicate names,
symlinks/executable modes, directories, encryption, traversal and unexpected paths.
Never extract paths or execute files. Only original report/bodies, storage report
and candidate/index/bodies are eligible. Candidate byte trees are fully validated.
Rebuild the tree from the independently fetched exact prior plus inert original
attempt bytes using approved storage code, then require complete byte equality
and matching transition/file-hash reports. Recheck source/run/manifest provenance,
measured timing and all-six acceptance before constructing any commit.

## Commit and normal push

Construct one local complete-tree child of the expected parent using a private Git
index and local compare-and-swap. Recheck the remote parent immediately before a
normal fast-forward push of that exact commit to the fixed ref. There is no force,
lease override, retry, deletion or history-rewriting operation. A racing descendant
is rejected by ordinary fast-forward semantics. The manual single-publisher rule
also assumes no external actor concurrently rewinds/deletes the branch; the last
read plus normal push is not a server-side arbitrary-ref compare-and-swap API.
Publication failure never invokes collection. Publication JSON records the commit,
parent, source/run, artifact ID/digest, index hash and tree size. The public branch
contains only index.json and bodies, without experiment archives or writer code.

## Validation envelope and remaining limits

66 offline tests pass, including conditional prior planning/304 recomputation,
ZIP traversal/mode checks, provenance/body/candidate mutations, local bare-remote
bootstrap/repeat, stale prior refusal, and old/new pinned generation reads. The
actual previous GitHub artifact ZIP also passed digest/member validation and full
candidate recomputation without source HTTP requests.

After pushing, run one bootstrap with empty prior, inspect both jobs and publish
commit, then run one repeat pinned to that exact commit. Each run remains capped
at six serial release GET attempts; no redirects, pagination or retries. Compare
real 200/304 behavior without promising 304 if GitHub changes bytes or validators.
Independently fetch and validate both published commits and verify hashes/freshness.
Record all results and persistent evidence. No hour/day wait is required.

Long-term history retention/fleet expansion and client/installer delivery remain
separate work. Current object-plus-candidate 128 MB bound is conservative and
measured under this shallow/local method, not a full remote-history storage cap.
Do not silently increase limits or rewrite history when they are reached.

Primary GitHub references: [artifact REST metadata/download semantics](https://docs.github.com/en/rest/actions/artifacts)
and [per-job GITHUB_TOKEN permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).
The application checks and restricted public-source inference are our design;
these documents do not establish a completed adversarial or privilege audit.
