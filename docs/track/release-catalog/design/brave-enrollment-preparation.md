# First deferred AppImage subset: Brave

Offline preparation, 2026-10-31, under [47](../issues/47-enroll-scoped-migration-sources.md).
This records the first frozen queue row, without enrolling it or unblocking 49.

## Exact subset and existing policy

Consumer alias: `https://api.github.com/repos/ivan-hc/Brave-appimage/releases`.
The six recipes are brave, brave-beta and brave-nightly on aarch64 and x86_64.
[Audit payload](../research/brave-enrollment-preparation.json) retains every source
fingerprint and full original install/update selection line. Each pair is identical;
all six pass shell syntax. Current recipe cost is 462 lines / 19,164 bytes.
Selection preserves case-insensitive architecture/AppImage URL matching, followed
by the stable/beta/nightly channel filter and first-match ordering. No source
conversion or asset-availability claim follows from this static check.

The queue provides no reviewed repository ID. The retained identity audit covers
Obsidian, Neovim, WezTerm and SQLiteBrowser, not Brave. Keep numeric fetch URL and
request ID unknown until actual accepted identity evidence exists. Do not infer
an ID from asset, release or owner fields.

## Prerequisite before proposing live expansion

The accepted utility publication established pinned catalog delivery and first-run
resource costs, but natural seven-source repeat/retention evidence remains absent.
Read-only GitHub inspection in this continuation found no run after 41232846271
and publication still `a113cd0aca3247111b6ba231f6a30b6477ac2c75`.
Follow the staged plan: observe and validate the next natural run before proposing
this next live subset. Do not manufacture that evidence with a manual dispatch.
Existing host utility delivery remains separate; no host inventory is needed here.

## Subsequent review sequence

1. After the repeat evidence is accepted, prepare a reviewable one-request runner
   for `GET https://api.github.com/repos/ivan-hc/Brave-appimage`. Reuse the retained
   am-utils identity runner's bounded transport, changing the exact URL and expected
   full_name together, with a fresh evidence directory and refusal of repeat use.
   The existing runner is a reference, not an executable Brave request package.
   Retain 64,000-byte body/header limits, 8,192-byte header-value limit, verified
   direct HTTPS, no credentials/proxy/config, no redirects/retries, 10-second
   connect limit and 30-second supervised absolute deadline. Review before execution
   and obtain the exact identity-only approval required by ticket 47.
2. Require HTTP 200, positive integer repository ID, expected full_name ignoring
   case, private=false and visibility=public. Retain exact bytes, hashes, timing
   and refusal evidence. A failure stops this stage without fallback.
3. Separately propose one numeric `/repositories/ID/releases` evidence request,
   keeping the exact named alias and no validators. Use existing 8 MB body,
   64 KB header and 30-second request bounds. Check all twelve original
   install/update selectors against the actual retained body and report unavailable
   assets without adapting channel/architecture filters. No pagination or latest
   substitution is authorized.
4. Only after actual compatibility/resource evidence, prepare an eight-source
   contract and exact collection/publication review. Preserve all seven accepted
   sources and bounds, conditional/failure/age behavior and pinned readers. Eight
   nominal 30-second requests consume 240 seconds of the 300-second batch bound;
   actual overhead and tree/artifact/history growth need evidence. The current
   seven-source guard must remain unchanged until that separate implementation.

No identity/release GET, source push, repin, collection, host delivery or recipe
migration belongs to this offline preparation. The other 49 deferred endpoints
remain outside this subset; ticket 49 remains blocked.

## Superseding sequencing decision — 2026-10-31

After discussion, the user approved bounded identity and release checks before the
natural repeat. The wait-before-evidence gate above is superseded for these reads;
operational expansion remains separate. [Actual findings](../research/brave-enrollment-findings.md)
record two HTTP 200 responses and 12/12 actual asset selections. The preparation
JSON retains its original null IDs, hashes and prerequisites as historical input;
the candidate queue and findings record the subsequently verified mapping.
