"""Reading the offline adapter's one-JSON-file-per-request transport records."""
import json


def read_transport_records(directory, *, excluding=()):
    """Read records in filename order, excluding Paths from an earlier checkpoint.

    Malformed records raise rather than disappearing from assertions. The caller
    owns the checkpoint and decides which transport facts to assert.
    """
    return [json.loads(path.read_text())
            for path in sorted(set(directory.iterdir()) - set(excluding))]
