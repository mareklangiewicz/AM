"""Canonical format-2 emitter, extracted from the original reader experiment."""
import json


def emit(obj, depth=0, context=''):
    lines = []
    for k, v in obj.items():
        key = json.dumps(k) if k.isdigit() or context == 'apps' else k
        prefix = '  ' * depth + key + ':'
        if isinstance(v, dict):
            lines.append(prefix + (' {}' if not v else ''))
            if v:
                lines.extend(emit(v, depth + 1, k))
        else:
            scalar = json.dumps(v, ensure_ascii=False)
            # Experimental extension: avoid YAML's Unicode line-break folding.
            scalar = scalar.replace('\u0085', '\\N').replace('\u2028', '\\L').replace('\u2029', '\\P')
            lines.append(prefix + ' ' + scalar)
    return lines


def document(obj):
    return '\n'.join(emit(obj)) + '\n'
