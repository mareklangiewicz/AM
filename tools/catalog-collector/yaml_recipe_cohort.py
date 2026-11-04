"""Named offline policy proposals; no installed client or automatic migration."""
import re

from collector import require
from yaml_selection import ASCII_LOWER, accept_selection

COHORT = ('x86_64/obsidian', 'x86_64/nvim', 'aarch64/nvim',
          'x86_64/nvim-nightly', 'aarch64/nvim-nightly')


def matches(recipe, release, asset):
    require(recipe in COHORT, 'unknown_cohort_recipe')
    arch, app = recipe.split('/')
    url = asset['url']
    if app == 'obsidian':
        url = url.translate(ASCII_LOWER)  # ASCII URLs in saved evidence; proposals use ASCII folding.
        return (re.search(r'https.*mage$', url) is not None and
                not any(s in url for s in ('i386', 'i686', 'aarch64', 'arm64', 'armv7l')))
    excluded = ('arm64', 'aarch64', 'i686', 'i386') if arch == 'x86_64' else ('x86_64', 'i686', 'i386')
    if re.search(r'https.*releases.*nvim.*mage$', url) is None or any(s in url for s in excluded):
        return False
    # Proposed tag gate makes channel intent explicit; the old selector only
    # tested a substring anywhere in the URL. prerelease is deliberately unused.
    if app == 'nvim-nightly':
        return release['tag'] == 'nightly' and 'nightly' in url.translate(ASCII_LOWER)
    return release['tag'] != 'nightly' and 'nightly' not in url


def select_cohort(recipe, repository, commit, *, now, accept_stale=None):
    require(recipe in COHORT, 'unknown_cohort_recipe')
    require(re.fullmatch('[0-9a-f]{40}', commit) is not None, 'commit_pin_required')
    require(now.tzinfo is not None and now.utcoffset().total_seconds() == 0, 'utc_now_required')
    # Input must come from the shared full validator, as in yaml_selection.select.
    for release_id, release in sorted(repository.get('releases', {}).items(),
            key=lambda item: (item[1]['published_at'], int(item[0])), reverse=True):
        for asset_id, asset in sorted(release['assets'].items(),
                key=lambda item: (item[1]['name'].encode('utf-8'), int(item[0]))):
            if matches(recipe, release, asset):
                return accept_selection(recipe.split('/')[1], str(repository['repository_id']),
                    repository, release_id, release, asset_id, asset, commit,
                    now=now, accept_stale=accept_stale)
    raise ValueError('no_matching_asset')
