#!/usr/bin/env python3
"""Ticket 10 fixture: does yamlls take a catalog file's schema from an inline `$schema` key?

Writes, next to this script, ticket 03's local-invalid.yaml (two planted errors) with its
modeline comment replaced by a first key `$schema:`:
  inline-relative-invalid.yaml  `$schema: "../03/repository.schema.yaml"`
  inline-remote-invalid.yaml    `$schema:` the raw GitHub URL of that schema at commit 3dfbc36a7
  repository-ref.schema.yaml    a kind file whose root is `$ref: ../03/repository.schema.yaml#/$defs/repository`
  inline-split-invalid.yaml     `$schema: "./repository-ref.schema.yaml"` (cross-file $ref)
  defs-only.schema.yaml         ticket 03's schema without its root `$ref` (its root accepts anything)
  inline-fragment-invalid.yaml  `$schema: "./defs-only.schema.yaml#/$defs/repository"`; errors can
                                only come from the fragment
  inline-nofragment-invalid.yaml  `$schema: "./defs-only.schema.yaml"`, the control: no errors expected

Probe: gndx nvim lspprobe --ask='hover:16:6' <file>, from the AM checkout.
"""

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
URL = ('https://raw.githubusercontent.com/mareklangiewicz/AM/3dfbc36a724ff750bd2c553c9e61a4519090c040/'
       'docs/track/catalog-simplification/scripts/03/repository.schema.yaml')
body = (HERE.parent / '03/local-invalid.yaml').read_text().split('\n', 1)[1]
(HERE / 'inline-relative-invalid.yaml').write_text('$schema: "../03/repository.schema.yaml"\n' + body)
(HERE / 'inline-remote-invalid.yaml').write_text(f'$schema: "{URL}"\n' + body)
(HERE / 'repository-ref.schema.yaml').write_text(
    '$schema: https://json-schema.org/draft/2020-12/schema\n'
    'title: AM repository (split)\n'
    "$ref: '../03/repository.schema.yaml#/$defs/repository'\n")
(HERE / 'inline-split-invalid.yaml').write_text('$schema: "./repository-ref.schema.yaml"\n' + body)
schema = (HERE.parent / '03/repository.schema.yaml').read_text()
assert schema.count("$ref: '#/$defs/repository'\n") == 1
(HERE / 'defs-only.schema.yaml').write_text(schema.replace("$ref: '#/$defs/repository'\n", ''))
(HERE / 'inline-fragment-invalid.yaml').write_text('$schema: "./defs-only.schema.yaml#/$defs/repository"\n' + body)
(HERE / 'inline-nofragment-invalid.yaml').write_text('$schema: "./defs-only.schema.yaml"\n' + body)
