# Fix native Termux YAML parser compilation

Type: task
Status: resolved
Triage: ready-for-agent

Migrating the retained whole-command tests in 118 exposed a pre-existing parser
failure on native Termux GNU awk 5.4.1: the C1 byte range cannot compile, even for
valid YAML. Reproduce with the maintained reader and a valid small document;
minimize the expression, preserve forbidden-character rejection and verify native
Termux plus existing portable reader tests. Source-only fix; no live deployment.

## Answer

Native Termux GNU awk 5.4.1 rejects the continuation-byte range in the literal
regular expression before reading any input. A minimal BEGIN-only expression
fails under both C and C.UTF-8 locales and with `awk -b`; spelling equivalent
complete UTF-8 sequences compiles. The maintained reader failed on a small valid
YAML document before the fix, independently of all historical tooling.

Replaced the range/partial-sequence classes with complete UTF-8 alternatives.
The same C1 controls, Unicode line separators and noncharacters remain forbidden.
A standalone regression exercises ordinary ASCII/Unicode release titles and each
of the 36 forbidden raw codepoints through the actual reader. It passes with host
mawk, GNU awk and BusyBox awk, and native Termux GNU awk. Whole-command Termux
validation follows as part of 118. No debug instrumentation or live deployment.
