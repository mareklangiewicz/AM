"""Format-3 retention over normalized facts."""
import copy
from bounded import timestamp


def observation(release, default=None):
    value=release.get('observed_at',default)
    if value is None:
        raise ValueError('release observation needs a shared default')
    return value


def merge(previous, fetched, *, completed_at, history_complete):
    """Apply one successful source scope. Raise before mutating on any conflict.

    A retained release the fetch did not return stays, unless the fetch proves it gone by
    reaching the end of the history. GitHub's list is not strictly ordered by any timestamp,
    so a partial page proves nothing about a release it did not return."""
    timestamp(completed_at)
    retained = {
        rid: dict(copy.deepcopy(record), observed_at=observation(record, previous.get('observed_at')))
        for rid, record in previous.get('releases', {}).items()
        if rid in fetched or not history_complete
    }
    retained.update(copy.deepcopy(fetched))
    for record in retained.values():
        timestamp(record.get('published_at', record.get('created_at')))
        if observation(record) > completed_at:
            raise ValueError('future_observation')
    ordered = sorted(retained, key=lambda rid: (
        retained[rid].get('published_at', retained[rid].get('created_at')), int(rid)), reverse=True)
    selected = ordered[:32]
    if not any(not retained[rid]['prerelease'] for rid in selected):
        stable = next((rid for rid in ordered if not retained[rid]['prerelease']), None)
        if stable is not None and stable not in selected:
            selected.append(stable)
    return {rid: {k: v for k, v in retained[rid].items()
                  if k != 'observed_at' or v != completed_at}
            for rid in sorted(selected, key=int)}
