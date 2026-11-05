"""Test-only independent reference for catalog selection.

No network, installation or automatic translation of legacy recipe regexes.
Uses the publisher's Python/YAML dependencies for rehearsal; portable shell
integration and per-recipe selection review remain separate.
"""
from datetime import datetime, timezone
import re
import string

from bounded import require
from yaml_publication import load_local

POLICY_KEYS = {'release_order','stable_only','asset_suffix','include','exclude','ignore_case'}
ASCII_LOWER = str.maketrans(string.ascii_uppercase,string.ascii_lowercase)


class StaleSelection(ValueError):
    def __init__(self, acceptance):
        super().__init__('stale_release_acceptance_required')
        self.acceptance = acceptance


def policy(value):
    require(type(value) is dict and set(value) == POLICY_KEYS and
            value['release_order'] == 'published_desc' and
            type(value['stable_only']) is bool and type(value['ignore_case']) is bool and
            type(value['asset_suffix']) is str and bool(value['asset_suffix']) and
            all(type(value[k]) is list and all(type(s) is str and bool(s) for s in value[k])
                for k in ('include','exclude')), 'invalid_selection_policy')
    return value


def select(apps, repositories, app, commit, rule, *, now, accept_stale=None):
    """Client policy chooses a release/asset before checking its observation age.

    Never silently substitute a fresher release when the chosen record is stale.
    Include means all substrings, exclude means any substring, on asset name only.
    Asset order is UTF-8 byte name then numeric ID; release ties use numeric ID.
    """
    rule = policy(rule)
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}',commit), 'commit_pin_required')
    require(type(now) is datetime and now.tzinfo is not None and
            now.utcoffset().total_seconds() == 0, 'utc_now_required')
    require(app in apps, 'unknown_app')
    rid = str(apps[app]); repository = repositories[rid]
    require(str(repository['repository_id']) == rid, 'repository_identity_mismatch')
    records = repository.get('releases',{})
    ordered = sorted(records.items(),key=lambda item:(item[1]['published_at'],int(item[0])),reverse=True)
    fold = (lambda value:value.translate(ASCII_LOWER)) if rule['ignore_case'] else (lambda value:value)
    for release_id,release in ordered:
        if rule['stable_only'] and release['prerelease']:
            continue
        for asset_id,asset in sorted(release['assets'].items(),
                                     key=lambda item:(item[1]['name'].encode('utf-8'),int(item[0]))):
            name = fold(asset['name'])
            if (not name.endswith(fold(rule['asset_suffix'])) or
                    not all(fold(s) in name for s in rule['include']) or
                    any(fold(s) in name for s in rule['exclude'])):
                continue
            return accept_selection(app, rid, repository, release_id, release, asset_id,
                                    asset, commit, now=now, accept_stale=accept_stale)
    raise ValueError('no_matching_asset')


def select_local(repo, commit, app, rule, *, now, accept_stale=None, max_file_bytes=2097152):
    apps,repositories = load_local(repo,commit,max_file_bytes=max_file_bytes)
    return select(apps,repositories,app,commit,rule,now=now,accept_stale=accept_stale)


def accept_selection(app, rid, repository, release_id, release, asset_id, asset, commit, *, now, accept_stale=None):
    """Shared selected-record freshness check for offline policy rehearsals."""
    observed = release.get('observed_at',repository.get('observed_at'))
    require(type(observed) is str, 'missing_release_observation')
    received = datetime.strptime(observed,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    age = (now-received).total_seconds()
    require(age >= 0, 'future_release_observation')
    acceptance = dict(commit=commit,repository_id=rid,release_id=release_id,
                      asset_id=asset_id,observed_at=observed)
    stale = age > 48*3600
    if stale and accept_stale != acceptance:
        raise StaleSelection(acceptance)
    return dict(app=app,**acceptance,tag=release['tag'],published_at=release['published_at'],
                prerelease=release['prerelease'],stale=stale,asset=dict(asset))
