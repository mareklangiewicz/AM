"""Disposable catalog/ trees on main-marek for host tests: built by documents.py
from saved GitHub answers, committed to a bare repository's main-marek."""
import json
from pathlib import Path
import subprocess
import tempfile

from bounded import normalize
import documents
from fixture_recipes import saved_bodies

NAMES = {262342594: 'obsidianmd/obsidian-releases', 16408992: 'neovim/neovim'}


def saved_repositories():
    """Repository documents for Obsidian and Neovim, by repository id, as a first collection writes them."""
    result = {}
    for rid, (raw, received) in saved_bodies().items():
        releases = json.loads(raw)
        acquired = dict(received_at=received, releases=normalize(releases, 100, allow_missing_published=True),
                        history_complete=False)  # saved with per_page=30: a full page is not all history
        result[rid] = documents.repository(None, acquired, repository_id=rid, repository=NAMES[rid])
    return result


def tree(apps, repositories):
    """catalog/ files: apps maps an app name to its repository id (x86_64 declaration recipes)."""
    files = {f'catalog/repositories/source-{rid}.yaml': documents.encode('repository', repositories[rid])
             for rid in sorted(set(apps.values()))}
    files['catalog/apps.yaml'] = documents.encode('apps', dict(apps={
        app: dict(repository=f'repositories/source-{rid}.yaml', x86_64='declaration') for app, rid in apps.items()}))
    return files


def bare(path):
    """A new, empty bare repository at path, standing in for GitHub's; returns path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', '--bare', '--template=', str(path)], check=True)
    return Path(path)


def publish(repo, files):
    """Commit these catalog/ files as main-marek's new tip of the bare repository; return the commit."""
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        git = lambda *args: subprocess.run(['git', '-C', str(work), *args], check=True, capture_output=True, text=True).stdout.strip()
        git('init', '-q', '-b', 'main-marek')
        if subprocess.run(['git', '--git-dir', str(repo), 'rev-parse', '-q', '--verify', 'main-marek'], capture_output=True).returncode == 0:
            git('fetch', '-q', str(repo), 'main-marek')
            git('reset', '-q', '--hard', 'FETCH_HEAD')
        for path, raw in files.items():
            (work/path).parent.mkdir(parents=True, exist_ok=True)
            (work/path).write_bytes(raw)
        git('add', '-A')
        git('-c', 'user.name=t', '-c', 'user.email=t@example.org', 'commit', '-q', '--allow-empty', '-m', 'catalog')
        git('push', '-q', str(repo), 'HEAD:main-marek')
        return git('rev-parse', 'HEAD')


def repository(rid, name, releases, received, *, complete):
    """The repository document one saved releases response gives, as a first collection writes it."""
    acquired = dict(received_at=received, releases=normalize(releases, 100, allow_missing_published=True),
                    history_complete=complete)
    return documents.repository(None, acquired, repository_id=rid, repository=name)


def expanded(document):
    """The document as a reader sees it: every release with its full URLs and observed_at."""
    repository = document['repository']
    releases = {}
    for rid, release in document['releases'].items():
        tag = release['tag']
        full = dict(release, url=release.get('url', f'https://github.com/{repository}/releases/tag/{tag}'),
                    observed_at=release.get('observed_at', document.get('observed_at')))
        full['assets'] = {aid: dict(asset, url=asset.get('url', f'https://github.com/{repository}/releases/download/{tag}/{asset["name"]}'))
                          for aid, asset in release['assets'].items()}
        releases[rid] = full
    return dict(document, releases=releases)
