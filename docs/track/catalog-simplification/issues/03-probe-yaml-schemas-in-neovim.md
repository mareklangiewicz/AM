# Probe YAML-authored JSON Schemas in Marek's Neovim

Type: task
Label: wayfinder:task
Status: open
Blocked by: none

## Question

Does Marek's Neovim (yaml-language-server from mason, SchemaStore.nvim) validate,
complete and hover a catalog YAML file against a JSON Schema written as YAML,
selected by a first-line `# yaml-language-server: $schema=<url-or-path>` comment?
Check a relative path and a raw GitHub URL. Record what works, with the exact
files used, in an isolated fixture outside Marek's live config.
