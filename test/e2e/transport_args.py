"""Supported download-command syntax for the offline transport adapter."""
from pathlib import Path


def download_destination(tool, args):
    """Return an explicit output Path, or None for curl stdout; reject unsupported forms.

    This is the fixture's supported subset, not a general curl/wget parser.
    """
    if tool not in ('curl', 'wget'):
        raise ValueError('Unsupported download tool')
    options = ('-O',) if tool == 'wget' else ('--output', '-o', '-Lo')
    output = None
    for i, arg in enumerate(args):
        if tool == 'curl' and arg == '-O':
            raise ValueError('Unsupported curl remote-name output')
        if arg in options:
            if i + 1 == len(args) or not args[i + 1] or args[i + 1].startswith('-'):
                raise ValueError('Missing download output operand')
            if output is not None:
                raise ValueError('Multiple download output destinations')
            output = Path(args[i + 1])
    if tool == 'wget' and output is None:
        raise ValueError('Unsupported wget invocation without -O')
    return output
