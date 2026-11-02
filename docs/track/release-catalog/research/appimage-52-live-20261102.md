# Accepted 52-source enrollment and recipe publication — November 2, 2026

Marek explicitly approved the complete scoped rollout in the continuation session.
Immediate controls matched source/daily pin `cc2ba588d5446df5a9fdb5366ad689e672986a2a`
and catalog parent `9f4e356ec2d50260196748374b00efdda397d7f7`, with only the
collector/dispatcher active and no unfinished runs. Enrollment was fast-forward
published as `4e379050d5a71f6494e84308383a6c36ec6d47cf`.

Exactly one manual dispatch was submitted:
[run 41442000508](https://github.com/mareklangiewicz/AM/actions/runs/41442000508),
attempt 1, completed successfully. All 52 distinct descriptors were attempted
once and returned HTTP 200. Eight requests used exact prior validators; 44 were
initially unconditional. No live 304 behavior is claimed. Collection took
42.439626544 seconds and received 36,175,616 body bytes within unchanged caps.

Accepted publication `29e37bd9207ae9557e8f57afa010699c649d4cde` has the exact sole
parent above. Both artifact ZIP digests match GitHub metadata. Independent
`delivery.verify_artifact` recomputation from the exact prior Git tree, every
published path/mode/body byte, index/lookup integrity, source/context/manifest
provenance and all prior aliases pass. Published tree: 36,338,025 bytes;
collection artifact ZIP: 5,311,968 bytes. Retained run data records actual job
timing. These figures establish this run's resource use, not fleet-scale growth.

All 107 migrated recipes were checked against actual publication bodies:
214 original install/update selectors agree with the migrated selectors and
select actual assets. Original recipe fingerprints match the frozen inventory.
Actual public HTTP reads through both production Python and shell readers,
pinned to the accepted commit, returned the exact expected body. Earlier local
validation remains [243 combined / 58 isolated enrollment tests](appimage-batch-20261102/rollout-review.json).
No app binaries were downloaded or executed for acceptance.

Only after acceptance, fast-forward published the exact combined recipe candidate
`d6e7421579d5a0f65588e39bb72995a675b9f08a` and set
`CATALOG_SCHEDULE_REVISION` to the same SHA. Final reads verified source/pin
equality, accepted catalog tip, collector/dispatcher isolation and no unfinished
runs. No rollback or second manual collection was needed. No host synchronization
or installed-updater migration occurred. Eleven legacy exception paths remain
unchanged; tickets 47/49 stay partial for their unresolved endpoint exceptions.

[Retained public evidence](appimage-52-live-20261102-evidence.tar.gz), SHA256
`9d93bcf5b6ca130f2288c332c34e9b43a9b09fcfeed56ff875e7d940ab97e959`. Includes original artifact ZIPs/metadata, run logs, acceptance script
and results, and final controls; no credentials or host inventories.
