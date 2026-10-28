# Deliver prepared Obsidian catalog pilot

Type: task
Status: resolved
Triage: ready-for-agent

## Authorization and scope

Marek explicitly approved ticket 31's four-file delivery-only pilot. Recheck old
hashes/absence, persist backups, stage and verify payloads, preserve ownership and
modes, replace four files and verify unchanged app/version/launcher state. No
installer, updater, manager invocation, network or binary replacement.

## Attempt and blocker

Approved execution began 2026-10-27T23:51Z. All source/destination hash and
syntax prechecks passed. Backup creation stopped at preserving install.am's
uid=1000/gid=65534: chown returned EPERM. No destination was replaced (replacement
loop was not reached). Partial backup directory retained:
/opt/am/catalog-pilot-backups/20261027T235127298560Z.
A subsequent `sudo -n python3 /tmp/am-deliver-pilot.py` refused because interactive
authentication is required; it did not execute the script.

[Checked delivery script](../pilot/deliver.py) is saved for continuation. User can
prime sudo with `sudo -v` in their terminal, then request resume; authorization for
this same four-file pilot persists. No password should be sent in chat. No app,
updater or manager ran. This is an operating-system authentication blocker, not
an automatic approval-review rejection. Do not weaken ownership preservation.

## Answer — user-executed delivery and managed update

Marek ran the saved delivery script with sudo successfully, then explicitly ran
`am -u obsidian --commit a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1`.
The prior authentication blocker is resolved. Persistent backup:
`/opt/am/catalog-pilot-backups/20261027T235924594413Z`.
[Delivery result](../research/installed-pilot-delivery-result.json) records all
four replacements, ownership/modes and unchanged app state at delivery completion.

User-provided terminal output reports the original GitHub 1.14.5 asset download,
HTTP redirect followed by 200, 139,238,201 bytes saved, and return to prompt.
Subsequent [read-only local checks](../research/installed-pilot-update-checks.json)
confirm all four support hashes match the approved payloads, version now names
1.14.5, installed binary size is 139,238,201 and SHA256 is
`306815f60d15dea8610d72886ef5e50ef4b7e7185e952ffc3bb21bee1582d952`.
No tmp or AM-VERIFIED file remains. No independent binary authenticity or
application-launch claim is made. Exact live catalog GET counts were not captured
for this user-run command. No stale override was supplied.

The saved four-file rollback covers support delivery only, not this subsequent
user-executed binary update. No new collection, publication or workflow occurred.
No further updater/manager/app invocation was used for verification.
