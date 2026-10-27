# Prepared installed Obsidian delivery pilot

Ticket [31](../issues/31-prepare-installed-obsidian-pilot.md).
Prepared from source 80bddc039; production code is unchanged since 3a843e656.
Payloads and their sizes/hashes are in [manifest.json](manifest.json).
[prepare.py](prepare.py) extracts the actual recipe heredoc, embeds the configured
source and stages the current manager/install module/helper. All four pass syntax
checks. Preparation executes no app code and makes no network requests.

## Read-only host findings

`/usr/local/bin/am` points to `/opt/am/APP-MANAGER`. Installed manager already
selects the fork but predates catalog support. `/opt/am/modules/catalog.am` is
absent. `/opt/obsidian/AM-updater` is legacy. No AM newrepo-on override was present
at `/home/marek/.local/share/AM/newrepo-on`.

The version file names Obsidian 1.14.4; retained catalog selects 1.14.5.
The installed binary SHA256 is
`6362ddbeeeebb7bbccb48fae009572cf2284ef92f5c919c1332aba48de6ffeaa`.
No AM-VERIFIED file exists. These are observations, not concurrency locks.

## Proposed first pilot: delivery only

No updater or installer execution, app replacement, network request or normal
whole-manager sync is included. Narrowly deliver these four staged payloads:

| Destination | Payload | Expected old SHA256 |
| --- | --- | --- |
| /opt/am/APP-MANAGER | APP-MANAGER | bb32c8ea853b06660f2d50cd9300f241a6403b08088cd6c80dc1fc952a0800f9 |
| /opt/am/modules/install.am | install.am | 695bbefd85e62cf7a9a0755fc88350c7255b239b56e01a786ee55080007b6796 |
| /opt/am/modules/catalog.am | catalog.am | absent |
| /opt/obsidian/AM-updater | AM-updater | aa94662966dcd31ff09dbda5ece63f2f55a8c3edc3326d8bb43a0aff5dc9d969 |

Manager/install delivery keeps the catalog routing and module inventory coherent
with the generated updater. The updater uses /opt/am/modules/catalog.am and an
embedded fork AMREPO when standalone. This narrow file delivery does not establish
that a live normal module sync works; temporary-root sync evidence remains in
prior tickets. It avoids updating unrelated modules during the first host pilot.

Before any writes, recheck all old hashes, absence, symlinks and regular-file
status; refuse drift. Save original files with ownership/modes and a manifest in
a new persistent backup directory under /opt/am/catalog-pilot-backups/. Record
its exact path. Stage replacement files alongside destinations, verify hashes,
preserve existing modes/ownership (new helper: 0644, manager ownership), then
rename into place. If any step fails, restore every already-replaced file.
Verify installed hashes/syntax and unchanged app binary/version/launcher hashes
without invoking am, the installer or updater. No user Obsidian data is touched.

## Rollback

Refuse rollback if a target no longer matches its installed pilot hash. Restore
manager/install/updater bytes and original modes/ownership from the recorded
backup; remove catalog.am only if it still matches the pilot helper hash and was
absent originally. Verify original hashes. Preserve backup/evidence until Marek
chooses to remove them. Rollback concerns these four files only; this pilot does
not modify the app binary or version file.

## Separate execution decision

Running the prepared updater on this host would attempt a 1.14.5 binary download
and replacement, even with a pinned catalog read. It is not a no-op smoke test.
A future execution plan must include that binary transfer, app backup/rollback,
standalone versus manager route, optional manager digest checks and exact read
budget. The retained publication is fresh through 2026-10-28T15:43:58.633795Z;
afterward require exact explicit stale consent or separately authorized collection.
Do not run it automatically as part of delivery or invent a matching version file.

This plan awaits authorization for the four installed-file changes. The installed
migration is an explicit operational boundary in the accepted tracker scope;
generic continuation authorized preparation, not host updater activation.
