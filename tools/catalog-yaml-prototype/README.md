# THROWAWAY YAML reader experiment

Question: can AM's proposed YAML subset support small POSIX shell/awk structure
validation, ID iteration and lossless scalar lookup without a YAML dependency?
This is research code, not a production reader. It makes no network calls.

Run from the repository root (Python plus PyYAML required for the independent
reference-parser experiment, not for the shell reader):

```sh
python3 tools/catalog-yaml-prototype/experiment.py
```

Reader examples:

```sh
sh tools/catalog-yaml-prototype/reader.sh validate repository.yaml
sh tools/catalog-yaml-prototype/reader.sh releases repository.yaml
sh tools/catalog-yaml-prototype/reader.sh assets repository.yaml 456
sh tools/catalog-yaml-prototype/reader.sh get repository.yaml releases 456 tag
sh tools/catalog-yaml-prototype/reader.sh apps apps.yaml
sh tools/catalog-yaml-prototype/reader.sh get apps.yaml apps obsidian
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases published_at prerelease
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases/456/assets name size digest
```

Exit status: 0 success, 2 invalid file/query/usage, 3 absent field or collection.
Scalar output is exact decoded bytes with no added newline. This preserves empty
strings, including trailing newlines; shell command substitution cannot preserve
trailing newlines, so use redirection when exact bytes matter. ID lists are LF
terminated. Validation completes before any result is emitted. Data is never
sourced, evaluated or used as an awk program.

Experimental bounds: 32 MiB/file, 64 KiB/line. These are local probe bounds, not
approved production collection budgets. Required fields, integer ranges and
fixed field order are a concrete trial of the schema, not deployed compatibility.

The original five-escape design cannot losslessly represent all Unicode line
breaks in YAML double-quoted text: NEL is folded, and spaces around Unicode line
separators can be folded. This branch **proposes** three additional standard YAML
escapes: `\N` (U+0085), `\L` (U+2028), `\P` (U+2029). They cost three fixed
decoder branches. Literal forms are rejected. This extension needs design
acceptance before production adoption. Other unsupported control characters
are deliberately unrepresentable; the eventual publisher must reject such an
observation rather than silently alter it.

UTF-8 validity is a publisher responsibility. The shell reader validates structure,
ASCII controls and the specific Unicode forms above, but does not implement a
general UTF-8 decoder. The Python experiment checks accepted fixtures against
PyYAML and compares decoded objects and scalar query bytes.

The parser stores paths and values, and each command scans the entire file.
Repeated one-field queries are unsuitable for large-history selection loops.
The experiment therefore adds `rows`: project requested scalar fields in one
validated scan. It writes ID then TAB-separated canonical YAML scalar tokens;
missing optional fields have an empty column, actual empty strings have `""`.
Escapes remain encoded, so tabs/newlines inside a name cannot break row framing.
This is ephemeral query output, not another published catalog representation.

For example, the client rule "newest published non-prerelease" is:

```sh
sh tools/catalog-yaml-prototype/reader.sh rows repository.yaml releases published_at prerelease > rows.tmp || exit
awk -F '\t' '$3=="false" && $2>newest {newest=$2; id=$1} END {if(id!="") print id; else exit 1}' rows.tmp
```

The conditional avoids using a shell pipeline that hides a reader failure.
Fixed quoted timestamps compare in chronological order. No version or asset
selection policy is built into the reader. Nothing here proves the complete new
collector/consumer system simpler or faster yet.
