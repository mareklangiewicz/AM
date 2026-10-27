#!/usr/bin/env python3
"""Bounded manual observations; never executes recipes or selects releases."""
import argparse
import gzip
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone

ENDPOINTS = {
    "obsidian-list": "repos/obsidianmd/obsidian-releases/releases",
    "obsidian-latest": "repos/obsidianmd/obsidian-releases/releases/latest",
    "neovim-list": "repos/neovim/neovim/releases",
    "neovim-latest": "repos/neovim/neovim/releases/latest",
    "wezterm-list": "repos/wez/wezterm/releases?per_page=100",
    "sqlitebrowser-list": "repos/sqlitebrowser/sqlitebrowser/releases?per_page=100",
}
ROUNDS = ("baseline", "hour", "day")
BODY_CAP = 10 * 1024 * 1024
VERSION = "2022-11-28"
HEADERS = {"date", "etag", "last-modified", "link", "retry-after", "content-type"}


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def write_json(path, value):
    path.write_bytes(encode(value))


def digest(body):
    return hashlib.sha256(body).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch(endpoint, headers):
    request = urllib.request.Request("https://api.github.com/" + endpoint, headers=headers)
    opener = urllib.request.build_opener(NoRedirect())
    try:
        response = opener.open(request, timeout=60)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        selected = {k.lower(): v for k, v in response.headers.items()
                    if k.lower() in HEADERS or k.lower().startswith("x-ratelimit-")}
        body = response.read(BODY_CAP + 1)
        return response.status, selected, body


def validate_history(root, expected):
    if root.is_symlink() or any(p.is_symlink() for p in root.rglob("*")):
        raise ValueError("evidence must not contain symlinks")
    if sorted(p.name for p in root.iterdir()) != sorted(expected):
        raise ValueError("previous evidence must contain exactly the preceding rounds")
    result = []
    for name in expected:
        directory = root / name
        if set(p.name for p in directory.iterdir()) != {"observation.json", *(k + ".json" for k in ENDPOINTS)}:
            raise ValueError("unexpected evidence files")
        if (directory / "observation.json").stat().st_size > 65536:
            raise ValueError("observation metadata too large")
        meta = json.loads((directory / "observation.json").read_text())
        if (meta.get("schema") != 1 or meta.get("complete") is not True or meta.get("endpoints") != ENDPOINTS
                or meta.get("api_version") != VERSION or meta.get("round") != name):
            raise ValueError("incomplete or incompatible previous observation")
        if set(meta.get("responses", {})) != set(ENDPOINTS):
            raise ValueError("missing previous responses")
        for key in ENDPOINTS:
            body_path = directory / (key + ".json")
            if body_path.stat().st_size > BODY_CAP:
                raise ValueError("previous body too large")
            body = body_path.read_bytes()
            if len(body) > BODY_CAP or digest(body) != meta["responses"][key]["sha256"]:
                raise ValueError("previous body hash or size invalid")
            validate_body(key, body)
        result.append((directory, meta))
    return result


def load_prior(root, round_name):
    """Validate all prior bodies before reusing validators or copying history."""
    index = ROUNDS.index(round_name)
    if root is None:
        if index:
            raise ValueError("repeat round requires previous evidence")
        return []
    if not index:
        raise ValueError("baseline cannot have previous evidence")
    return validate_history(root, list(ROUNDS[:index]))


def validate_body(key, body):
    data = json.loads(body)
    if key.endswith("-list"):
        if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
            raise ValueError("release list has wrong shape")
    elif not isinstance(data, dict) or not isinstance(data.get("tag_name"), str):
        raise ValueError("latest release has wrong shape")


def collect(output, round_name, previous=None, request=fetch):
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise ValueError("GH_TOKEN is required")
    prior = load_prior(previous, round_name)
    output.mkdir(parents=True, exist_ok=False)
    for directory, _ in prior:
        shutil.copytree(directory, output / directory.name)
    current = output / round_name
    current.mkdir()
    meta = {"schema": 1, "round": round_name, "api_version": VERSION, "endpoints": ENDPOINTS,
            "source_revision": os.environ.get("GITHUB_SHA"), "complete": False,
            "responses": {}, "started_at": datetime.now(timezone.utc).isoformat()}
    if prior:
        now = datetime.fromisoformat(meta["started_at"])
        meta["seconds_since_baseline"] = (now - datetime.fromisoformat(prior[0][1]["started_at"])).total_seconds()
        meta["seconds_since_previous"] = (now - datetime.fromisoformat(prior[-1][1]["started_at"])).total_seconds()
    manifest = current / "observation.json"
    write_json(manifest, meta)
    for key, endpoint in ENDPOINTS.items():
        headers = {"Authorization": "Bearer " + token,
                   "Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": VERSION, "User-Agent": "AM-catalog-churn"}
        old = prior[-1][1]["responses"][key] if prior else None
        if old:
            old_headers = old["headers"]
            if old_headers.get("etag"):
                headers["If-None-Match"] = old_headers["etag"]
            elif old_headers.get("last-modified"):
                headers["If-Modified-Since"] = old_headers["last-modified"]
        entry = {"checked_at": datetime.now(timezone.utc).isoformat()}
        meta["responses"][key] = entry
        try:
            status, response_headers, body = request(endpoint, headers)
            entry.update(status=status, headers=response_headers, received_bytes=len(body))
            if len(body) > BODY_CAP:
                raise ValueError("body cap exceeded")
            if status == 304:
                if not old or not any(k in headers for k in ("If-None-Match", "If-Modified-Since")):
                    raise ValueError("304 without a validated conditional request")
                body = (prior[-1][0] / (key + ".json")).read_bytes()
                # A 304 can omit validators; retain the prior ones for the next round.
                entry["headers"] = {**old["headers"], **response_headers}
            elif status != 200:
                raise ValueError("HTTP failure")
            validate_body(key, body)
            (current / (key + ".json")).write_bytes(body)
            entry.update(sha256=digest(body), body_bytes=len(body))
            if response_headers.get("x-ratelimit-remaining") == "0":
                raise ValueError("quota exhausted; stopping round")
        except Exception:
            # Exception messages can contain request details; persist only a fixed label.
            entry["error"] = "request, quota, size or validation failure; round stopped"
            write_json(manifest, meta)
            raise RuntimeError("observation stopped; inspect public evidence") from None
        write_json(manifest, meta)
    meta["complete"] = True
    meta["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_json(manifest, meta)


def project(value):
    """Diagnostic fields only; order preserved, no release/asset filtering."""
    def release(r):
        fields = ("tag_name", "name", "created_at", "published_at", "prerelease", "draft")
        result = {k: r[k] for k in fields if k in r}
        result["assets"] = [{k: a[k] for k in ("name", "size", "digest", "browser_download_url")
                             if k in a} for a in r.get("assets", [])]
        return result
    return [release(r) for r in value] if isinstance(value, list) else release(value)


def changed_paths(before, after, path="$"):
    if type(before) is not type(after):
        return [path]
    if isinstance(before, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            child = path + "[" + json.dumps(key) + "]"
            result.extend([child] if key not in before or key not in after
                          else changed_paths(before[key], after[key], child))
        return result
    if isinstance(before, list):
        result = [path + ".length"] if len(before) != len(after) else []
        for i, (left, right) in enumerate(zip(before, after)):
            result.extend(changed_paths(left, right, path + "[" + str(i) + "]"))
        return result
    return [] if before == after else [path]


def git_call(root, *args):
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "Catalog experiment", "GIT_AUTHOR_EMAIL": "catalog@example.invalid",
           "GIT_COMMITTER_NAME": "Catalog experiment", "GIT_COMMITTER_EMAIL": "catalog@example.invalid",
           "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z"}
    return subprocess.check_output(["git", "-C", str(root), *args], env=env,
                                   stderr=subprocess.DEVNULL).decode().strip()


def analyze(root):
    names = [name for name in ROUNDS if (root / name).exists()]
    if names != list(ROUNDS[:len(names)]) or not names:
        raise ValueError("observations must start at baseline and be contiguous")
    validate_history(root, names)
    report = {"rounds": names, "layouts": {}, "changes": {}}
    for previous, current in zip(names, names[1:]):
        report["changes"][current] = {}
        for key in ENDPOINTS:
            a = (root / previous / (key + ".json")).read_bytes()
            b = (root / current / (key + ".json")).read_bytes()
            report["changes"][current][key] = {
                "body_changed": a != b,
                "json_paths": changed_paths(json.loads(a), json.loads(b))}
    report["filter_diagnostics"] = {}
    for name in names:
        report["filter_diagnostics"][name] = {}
        for key in ("obsidian-list", "wezterm-list"):
            raw = (root / name / (key + ".json")).read_bytes()
            projected = encode(project(json.loads(raw)))
            report["filter_diagnostics"][name][key] = {
                "exact": diagnostic_filter(key, raw),
                "projection": diagnostic_filter(key, projected)}
    for layout in ("exact", "projection"):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git_call(repo, "init", "--quiet", "--template=")
            git_call(repo, "config", "core.autocrlf", "false")
            git_call(repo, "config", "gc.auto", "0")
            metrics = []
            for number, name in enumerate(names):
                observation = root / name
                size = compressed = 0
                for key in ENDPOINTS:
                    body = (observation / (key + ".json")).read_bytes()
                    if layout == "projection":
                        body = encode(project(json.loads(body)))
                    (repo / (key + ".json")).write_bytes(body)
                    size += len(body)
                    compressed += len(gzip.compress(body, mtime=0))
                # Identical observation status/time policy in both layouts.
                meta = json.loads((observation / "observation.json").read_text())
                index = {k: v for k, v in meta.items() if k != "responses"}
                index["responses"] = {k: {f: v[f] for f in ("checked_at", "status")}
                                      for k, v in meta["responses"].items()}
                write_json(repo / "index.json", index)
                git_call(repo, "add", "--", ".")
                git_call(repo, "commit", "--quiet", "--allow-empty", "-m", name)
                loose = sum(p.stat().st_size for p in (repo / ".git/objects").glob("??/*") if p.is_file())
                metrics.append({"round": name, "body_bytes": size, "body_gzip_bytes": compressed,
                                "cumulative_loose_object_bytes": loose,
                                "index_bytes": (repo / "index.json").stat().st_size})
            git_call(repo, "repack", "-adf", "--window=10", "--depth=50")
            packed = sum(p.stat().st_size for p in (repo / ".git/objects/pack").iterdir())
            report["layouts"][layout] = {"observations": metrics, "pack_and_index_bytes": packed}
    report["git_version"] = subprocess.check_output(["git", "--version"]).decode().strip()
    report["limits"] = "Small sample; positional JSON paths do not identify semantic changes after reordering; no annual forecast."
    return report


def diagnostic_filter(key, body):
    """Python transcription of two reviewed text filters, never installer code."""
    tokens = re.split(r'[()",{} \n]', body.decode())
    pattern = r"https.*nightly.*mage$" if key == "wezterm-list" else r"https.*mage$"
    matches = [t for t in tokens if re.search(pattern, t, re.I)
               and not re.search(r"i386|i686|aarch64|arm64|armv7l", t, re.I)]
    return (matches[-1] if key == "wezterm-list" else matches[0]) if matches else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect_args = sub.add_parser("collect")
    collect_args.add_argument("round", choices=ROUNDS)
    collect_args.add_argument("output", type=Path)
    collect_args.add_argument("--previous", type=Path)
    analyze_args = sub.add_parser("analyze")
    analyze_args.add_argument("observations", type=Path)
    args = parser.parse_args()
    if args.command == "collect":
        collect(args.output, args.round, args.previous)
    else:
        print(json.dumps(analyze(args.observations), indent=2))


if __name__ == "__main__":
    main()
