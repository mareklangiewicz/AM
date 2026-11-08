"""Format-3 retention over normalized facts; format-2 retention stays independent."""
import copy
from bounded import timestamp
from retention import observation


def merge(previous, fetched, *, completed_at):
    """Apply one successful source scope. Raise before mutating on any conflict."""
    timestamp(completed_at)
    tags = {}
    for rid, record in fetched.items():
        if record['tag'] in tags and tags[record['tag']] != rid:
            raise ValueError('same_tag_conflict')
        tags[record['tag']] = rid
    retained = {
        rid: dict(copy.deepcopy(record), observed_at=observation(record, previous.get('observed_at')))
        for rid, record in previous.get('releases', {}).items()
        if record['tag'] not in tags or tags[record['tag']] == rid
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
