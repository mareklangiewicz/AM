# Named format-2 recipe cohort — proposal

Offline source preparation after ticket 95. No policy acceptance or operational
migration. Run `python3 tools/catalog-yaml-prototype/recipe_cohort.py` to repeat
five comparisons against two SHA256/size-checked list responses inside the tracked
supervised-baseline-40529551070 archive. Candidate normalization runs through the
full shared YAML validator. The selected-record freshness helper is shared with
the earlier offline reference. Neither Python file is a host prerequisite.

## Explicit proposed rules

| Recipe | URL rule | Channel/tag | Other retained behavior |
| --- | --- | --- | --- |
| x86_64/obsidian | ASCII case-insensitive `https.*mage$`; exclude i386/i686/aarch64/arm64/armv7l anywhere | All tags, including prereleases | Negative arch filtering, no positive x86 requirement |
| x86_64/nvim | Case-sensitive `https.*releases.*nvim.*mage$`; exclude nightly/arm64/aarch64/i686/i386 anywhere | Additionally exclude exact tag nightly | Prereleases other than nightly allowed |
| aarch64/nvim | Same URL expression; exclude nightly/x86_64/i686/i386 anywhere | Additionally exclude exact tag nightly | Unlabelled assets remain eligible |
| x86_64/nvim-nightly | Same URL expression; exclude arm64/aarch64/i686/i386; ASCII case-insensitive nightly substring | Require exact tag nightly | REFRESH_ALWAYS must survive integration |
| aarch64/nvim-nightly | Same URL expression; exclude x86_64/i686/i386; same nightly substring | Require exact tag nightly | REFRESH_ALWAYS must survive integration |

The URL expressions deliberately preserve the broad legacy `mage$` intent,
including its ability to match a non-AppImage URL ending in those letters.
They operate on the literal decoded asset URL, not asset name. The proposed
client examines asset facts only: a matching release-note/other JSON string can
no longer become a download. No JSON is synthesized for old selectors.
Asset name only breaks ties. A misleading name does not change URL eligibility.
The recipe's custom desktop cleanup for Obsidian remains a lifecycle concern.

Release ordering changes from returned page order to descending published_at,
then descending numeric release ID. Within each release, eligible assets sort
by UTF-8 name bytes, then ascending numeric ID. This replaces upstream asset
order. If a release has no eligible asset, continue to the next release. Retained
older records are eligible beyond the saved first page; this is a coverage change
from the old one-response selector and each record keeps its own observation age.
A selected stale record refuses rather than substituting a fresher lower-priority
one. Future observations refuse; exactly 48 hours remains fresh. The existing
exact commit/repository/release/asset/observed_at rehearsal waiver is reused.

The exact nightly tag gate is an intentional proposed tightening: an asset URL
containing nightly on tag nightly-experiment no longer qualifies. A stable recipe
also excludes exact tag nightly even if its URL hides the channel. These rules
need acceptance. No general stable-only rule is added: both Obsidian and nvim may
still select prereleases. Case-sensitive stable URL exclusion can admit uppercase
NIGHTLY on other tags, as before. Negative architecture rules can admit generic
or ambiguously named assets, as before. Those are visible policy choices, not
newly proven architecture guarantees.

## Saved-fixture results and limits

All five exact URLs match the current actual generic shell selector:

| Recipe | Selected tag | Release ID | Asset ID |
| --- | --- | --- | --- |
| x86_64/obsidian | v1.14.5 | 420802120 | 666061989 |
| x86_64/nvim | v0.12.6 | 408064517 | 625399159 |
| aarch64/nvim | v0.12.6 | 408064517 | 625399210 |
| x86_64/nvim-nightly | nightly | 425065797 | 680562221 |
| aarch64/nvim-nightly | nightly | 425065797 | 680562264 |

`recipe-cohort-results.json` records full URLs, recipe fingerprints, body and
archive hashes, effective observations and both release orders. On these saved
pages, page order and proposed publication order coincide; equality does not
prove the policies equivalent. Responses are historical default-size 30 pages,
not current upstream state, full history or default 100-release capacity evidence.
The offline clock is each response's observation, not a real current freshness
claim. Draft normalization follows the shared collector contract.

Seven adversarial groups cover publication-order/fallback, exact tag differences,
prereleases/case, URL-versus-name and architecture, broad Obsidian suffix behavior,
numeric ties beyond IEEE-754 precision, selected stale acceptance/boundary/future
and missing recipe/asset refusal. Existing seven selection and five workflow
checks also pass. No three-awk matrix or full lifecycle suite is claimed here.

## Next integration boundary

Portable shell implementation must query the shared fully validating reader,
retain byte caps/private spooling, and return structured selected facts. Preserve
literal URL version identity, REFRESH_ALWAYS, pre-mutation refusal, installed
module/updater bindings and command-private pinned acquisition reuse. Acceptance
remains per selection. Then exercise disposable install/update/repair/batch flows.
This cohort proposal does not implement those steps, choose an operational stale
CLI, approve capacity, promote the candidate, or resolve format transition/rollback.
