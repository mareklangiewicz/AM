# Separate host archive knowledge from the shared package lifecycle

Type: task
Status: open
Triage: ready-for-agent

Audit from 111 found additional application knowledge in modules/appimage.am:
- am_archive_stage knows EmmyLua's four filenames, rclone's archive directory
  glob/executable, btop's root/bin layout, and Kitty's bin/kitty + bin/kitten.
- am_package selects/coheres/downloads EmmyLua's four assets, and maps archive
  layouts to launcher/remover names (including kitten).

Move app-specific archive mappings, toolset membership and launcher choices into
recipes or narrow app-owned adapters, keeping download/staging/replacement,
selection freshness and custom-launcher handling shared. Preserve currently
installed recipes during module refresh; they lack any new settings. Do not
silently break their next standalone update. Preserve exact same-release and
fresh-only EmmyLua rules, archive failure behavior and all 21 host layouts.
Use actual-manager/standalone and inert archive tests, including deployment from
old installed recipes. Avoid a generic acquisition backend or hook framework.

The catalog-yaml-policy.am source registry and generated explicit selection
policies intentionally hold trusted client policies; their app-specific records
are not by themselves the same installer coupling. EmmyLua's separate fresh-only
refusal in catalog-yaml.am should be considered alongside its toolset adapter,
without weakening or bypassing it. Review source-of-truth duplication with
host-apps.json and host_cutover.py as part of the concrete adapter design.

This ticket is source follow-up, not authorization for live deployment or pushes.
