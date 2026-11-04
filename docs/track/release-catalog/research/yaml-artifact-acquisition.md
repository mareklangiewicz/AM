# YAML authenticated artifact acquisition — November 4, 2026

[92](../issues/92-prepare-yaml-artifact-acquisition.md), source candidate
`eecdbdc09` on `prep/yaml-offline-publication`.

`yaml_delivery.acquire` reuses the fixed-repository authenticated downloader.
Trusted caller artifact ID/digest plus workflow context bind GitHub metadata to
repository, run, source SHA, main branch and `yaml-bootstrap-RUN-ATTEMPT` name.
Downloaded ZIP bytes must match GitHub's SHA-256 digest before decoding. The
attempt association relies on trusted workflow naming, not an independent attempt
field in artifact metadata. Receipt values are not authentication input.

The shared downloader adds optional decoder/envelope arguments; existing format-1
callers retain defaults. Strict archive-size metadata rejects booleans/negative
sizes. A YAML-only decoder bounds central-directory bytes/count before parsing,
accepts only store/deflate normalized YAML, receipt and optional structural
directories, and never extracts paths. It refuses duplicates, traversal, NUL,
symlink/executable/special files, encryption, extra files, ZIP64 and multidisk.
Per-file, candidate-tree, receipt and count caps apply to decompressed data.
The archive envelope is tree + receipt + 1,000,000 bytes: 136,266,304 bytes for the
existing profile. This is candidate policy, not measured capacity or a peak-RSS
claim. ZIP and decoded files are bounded in-memory buffers; no new consumer
worker, watchdog or storage reservation framework is added.

After authentication, existing staging verification checks source, schema,
context/profile/scope, enrollment, exact local prior and retained failure state.
Only then is a new private output directory created. Existing output refuses
before network work; invalid authentication/receipt creates no accepted output.
Successful upstream facts still rely on the trusted workflow, without raw-body
archives or duplicate recomputation. Receipt remains artifact-only.

Six new tests use fake API responses and actual ZIP data: authenticated round trip
without ref mutation; wrong ID/name/run/source/repository/branch/expiry/digest/size;
preflight/existing-output refusal before API; authenticated invalid receipt;
closed-layout paths/modes/duplicates/NUL; directory and resource/envelope bounds.
The existing YAML adapter/enrollment/staging and format-1 delivery/shard/shell
regressions pass: **55 tests total**, plus compilation and whitespace checks.
No live artifact, new action/runner capability or actual full-default capacity was
measured.

[Detailed source design](https://github.com/mareklangiewicz/AM/blob/eecdbdc09/docs/track/release-catalog/design/yaml-artifact-acquisition.md).
Remote exact-pin format-2 prior acquisition and publication CAS remain unwired.
No active workflow, catalog ref, daily pin, installed consumer, schedule or yadm
pointer changed. Source promotion and operational activation remain separate.
