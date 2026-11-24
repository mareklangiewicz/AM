#!/usr/bin/env python3
"""Ticket 03 fixture: a JSON Schema authored as YAML, and catalog files that name it by modeline.

Writes, next to this script:
  repository.schema.yaml  schemas/catalog/repository.schema.json (from git HEAD) as YAML, with a
                          YAML comment and two added field descriptions (the JSON has none) so
                          hover has something to show
  local.yaml              a real repository file, modeline `$schema=./repository.schema.yaml`
  local-invalid.yaml      the same with two planted errors (string size, unknown key)
  remote.yaml             the same file, modeline = raw GitHub URL of the schema at COMMIT
                          (only with --remote-commit COMMIT)

Usage: make_fixture.py [--catalog-ref REF] [--remote-commit COMMIT]
Run from anywhere inside the AM checkout.
"""

import argparse
import json
import pathlib
import subprocess

import yaml

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA_PATH = "schemas/catalog/repository.schema.json"
SAMPLE = "repositories/aether.yaml"
REPO_REL = HERE.relative_to(pathlib.Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=HERE, text=True).strip()))


def git_show(ref_path: str) -> str:
    return subprocess.check_output(["git", "show", ref_path], cwd=HERE, text=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog-ref", default="origin/release-catalog-v3")
    ap.add_argument("--remote-commit")
    args = ap.parse_args()

    schema = json.loads(git_show(f"HEAD:{SCHEMA_PATH}"))
    props = schema["$defs"]["release"]["properties"]
    props["tag"]["description"] = "The release's Git tag, as GitHub returns it."
    schema["$defs"]["asset"]["properties"]["size"]["description"] = "The asset's size in bytes."
    body = yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=100)
    (HERE / "repository.schema.yaml").write_text(
        f"# {SCHEMA_PATH} at HEAD, converted to YAML by make_fixture.py (ticket 03).\n" + body)

    sample = git_show(f"{args.catalog_ref}:{SAMPLE}")
    (HERE / "local.yaml").write_text(
        "# yaml-language-server: $schema=./repository.schema.yaml\n" + sample)
    # Two planted errors: a string size, and a key the closed schema forbids.
    bad = sample.replace("size: 4490994", 'size: "big"', 1).replace("kind:", "bogus: 1\nkind:", 1)
    assert bad.count('size: "big"') == 1 and bad.count("bogus: 1") == 1
    (HERE / "local-invalid.yaml").write_text(
        "# yaml-language-server: $schema=./repository.schema.yaml\n" + bad)
    if args.remote_commit:
        url = ("https://raw.githubusercontent.com/mareklangiewicz/AM/"
               f"{args.remote_commit}/{REPO_REL}/repository.schema.yaml")
        (HERE / "remote.yaml").write_text(f"# yaml-language-server: $schema={url}\n" + sample)


if __name__ == "__main__":
    main()
