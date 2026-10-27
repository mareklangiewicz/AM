# Deliver prepared Obsidian catalog pilot

Type: task
Status: open
Triage: ready-for-human

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
