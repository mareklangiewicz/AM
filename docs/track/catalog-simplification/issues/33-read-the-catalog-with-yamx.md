# Read the catalog with yamx

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: mareklangiewicz/yamx#22

## Outcome

As decided with Marek (November 26, 2026; ticket 31's Answer), the catalog
grammar (`docs/catalog-format.md`) becomes a yamx profile. Today's YAM(B)
lacks four things the catalog needs, and yamx#22 asks for them:
- UTF-8 strings;
- quoted keys;
- double-quoted strings with escapes;
- 64-bit ids.

Once that profile exists, `modules/catalog-parser.am` (hosts) and
`tools/catalog-contract/parse.mjs` (page) use yamx's shell and JS readers, and
AM keeps only its schema and cross-field rules. In the same change,
`tools/catalog-contract/platforms.json` becomes YAM(B) `platforms.yaml`, read
by the page through yamx's `yamx.mjs` and by the collector through PyYAML.
Hosts must take the new reader before any document only it accepts is
committed (see ticket 27's note).
