# Native Termux container findings (ticket 54)

Baseline: `673b9c3ed`; test changes are committed with this record.

## Environment and claims

`termux/termux-docker` supplies Android/Bionic x86_64 userland. No `/bin` or `/usr`
compatibility links were created. Tests ran as uid/gid 1000 (`system`), with native
PREFIX/TMPDIR/Android variables and Termux's normal `libtermux-exec.so` preload.
The built test image ID is
`127af029c294d496bfdbadb7a7b8b72e312ce128666186ae5b0f4a74a58ee9b8`.
An initial image build hit incompatible old/current ncurses package dependencies;
upgrading the disposable image before installing test dependencies resolved that.
No test runtime networking is enabled; package-image builds use network.

All manager/module code is installed without source patching and byte-verified
after each scenario. The system-mode fixture under `/opt/am` is prepared by
container root; runtime commands are unprivileged. Its directory has write bits
removed, and only the negative system-mode test temporarily restores them.
Manager/modules remain root-owned. The locally installed `am` case separately
verifies automatic AppMan path selection without this system fixture or a marker.

## Actual failure and repair

The initial run had four scenarios: three passed and read-only fallback failed with `ERROR: No sudo or doas found`. The minimized run:

```sh
E2E_TEST=TermuxCLI.test_read_only_am_falls_back_without_sudo ./test/e2e/run termux
```

failed in 0.711 seconds before the fallback prompt. `_am` required a privilege
tool before the later write-permission/mode decision. Deferred that requirement
until after fallback: AppMan can operate without sudo/doas, while system mode
retains its prior refusal. The test through the normal `am` command name then
passed, including persisted mode, system-helper binding, standalone and managed
updates. Additional scenarios verify declining fallback and no-sudo refusal when
the system directory is writable.

## Final verification

- Full matrix: **25 scenarios / 70 CLI invocations**: Termux 7/14, Debian 9/28,
  Fedora 9/28. Logs retained locally under ignored
  `test/e2e/out/20261028T184857Z-684908/`.
- Final Termux rerun after evidence/result-ownership harness refinements:
  **7 scenarios / 14 commands**, all passing; logs under ignored
  `test/e2e/out/20261028T185110Z-726625/`. Source/module hashes, image ID,
  unprivileged environment, individual stdout/stderr/status, transport records,
  actual native ELF hash and structured result are retained.
- **184 catalog tests pass**. Shell syntax, new harness warning-level ShellCheck,
  Python syntax and diff checks pass. Manager ShellCheck code/message diagnostics
  exactly match baseline (no new findings).

Coverage includes direct AppMan, local `am` auto-mode, read-only fallback accepted
and declined, writable-system refusal without privilege tools, source-persistent
standalone update, transfer preservation/retry and freshness refusal. AppImage
lifecycle downloads use inert extraction scripts. A controlled legacy CLI recipe
also downloads and executes real Termux-packaged Bash ELF bytes: 841744 bytes,
SHA-256 `9f7e99e26a5b0d3ae5d516e37a3924c920f6456cdc1cab6561b7b4b8344bfeae`.
The installed bytes match the native source and execute an asserted CLI result.

These results demonstrate the tested fork's native Termux userland paths. They do
not establish ARM64 phone coverage, arbitrary Linux ELF/AppImage compatibility,
GUI/FUSE, Android SELinux/app lifecycle or real-device installation. In particular,
real Termux's ordinary user cannot create the root-prepared `/opt/am` fixture.
No host app/config/helper delivery, production release collection, workflow change,
source push or repin occurred. Timed 37/41 obligations remain independent.
