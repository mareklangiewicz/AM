"""Validate in-memory bytes with the exact distributed awk grammar.

Server callers already own bounded bytes and expose no query output. Invoke the
maintained parser directly instead of creating a file, shell and private spool
for every document. Installed shell readers and their query safeguards stay intact.
"""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def validate_wire(raw,max_file_bytes,*,contract=False):
    if contract and not raw.endswith(b'\n'):
        raise ValueError('catalog YAML: final LF required')
    command=['awk']
    if contract:
        command.extend(['-f',str(ROOT/'modules/catalog-contract-tables.am')])
    command.extend(['-f',str(ROOT/'modules'/('catalog-contract-parser.am' if contract else 'catalog-yaml-parser.am'))])
    result=subprocess.run(command,input=raw,capture_output=True,
        env={'PATH':'/usr/bin:/bin','LC_ALL':'C','AM_YAML_OPERATION':'validate',
             'AM_YAML_MAX_INPUT_BYTES':str(max_file_bytes)})
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8','replace').strip())
