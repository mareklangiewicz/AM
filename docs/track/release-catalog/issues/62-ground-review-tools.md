# Ground review tools

Type: task
Status: resolved
Triage: ready-for-agent

Extract recipe replacement encoding and file fingerprinting from the reviewed
branch. Preserve behavior, migrate both callers, and specify boundary cases.
User explicitly selected this work following the myground review.

## Answer

Extracted `am_recipe_replacement` in the installer and migrated module/source
encoding. Added a real sed/shell round-trip test covering empty values, spaces,
backslashes, metacharacters, and inert command substitutions.

Added `fingerprint_files` to e2e filesystem support and migrated input, module,
and manager hashing in both platform fixtures. Specs cover empty input, nested
binary files, changed contents, and missing files.

Validation: baseline nine e2e support tests and bash syntax passed; after the
first finding the encoder test and bash syntax passed; after the second all ten
e2e support tests passed. Both scenario modules parse and git diff --check passes.
No reverts. Container scenarios were not rerun; report layout and input selection
are unchanged. No commit created.
