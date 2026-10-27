#!/usr/bin/env python3
"""Read exact catalog response bytes. No upstream API fallback or installer effects."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time

from collector import Refusal, require
from public_http import REF_URL, RAW_ROOT, get
from reader import StaleObservation, select, verify_body
from storage import INDEX_CAP, decode, digest


def resolve(fetch, deadline):
    raw = fetch(REF_URL,64_000,deadline)
    require(type(raw) is bytes and len(raw) <= 64_000, 'catalog_ref_bound')
    value = decode(raw)
    require(type(value) is dict and value.get('ref') == 'refs/heads/release-catalog' and
            type(value.get('object')) is dict and value['object'].get('type') == 'commit' and
            type(value['object'].get('sha')) is str and re.fullmatch('[0-9a-f]{40}',value['object']['sha']),
            'catalog_ref_refusal')
    return value['object']['sha']


def lookup(alias, *, commit=None, stale_acceptance=None, fetch=get,
           utcnow=lambda: datetime.now(timezone.utc), monotonic=time.monotonic):
    require(type(alias) is str and 0 < len(alias.encode()) <= 8192, 'invalid_alias')
    require(commit is None or type(commit) is str and re.fullmatch('[0-9a-f]{40}',commit), 'commit_pin_required')
    deadline=monotonic()+90
    pin=commit if commit is not None else resolve(fetch,deadline)
    require(monotonic() < deadline,'catalog_deadline')
    index_url=RAW_ROOT+pin+'/index.json'
    index_raw=fetch(index_url,INDEX_CAP,deadline)
    require(monotonic() < deadline,'catalog_deadline')
    started=utcnow()
    entry, metadata=select(index_raw,alias,pin,now=started.isoformat(),stale_acceptance=stale_acceptance)
    body_url=RAW_ROOT+pin+'/'+entry['observation']['path']
    raw=fetch(body_url,entry['observation']['bytes'] or 1,deadline)
    verify_body(raw,entry)
    # Expiry or a future clock after IO must still refuse without emitting bytes.
    require(monotonic() < deadline,'catalog_deadline')
    finished=utcnow()
    require(finished >= started,'catalog_clock_regressed')
    _, metadata=select(index_raw,alias,pin,now=finished.isoformat(),stale_acceptance=stale_acceptance)
    metadata.update(index_url=index_url,body_url=body_url,index_sha256=digest(index_raw),
                    checked_at=finished.isoformat(),resolved_ref_once=commit is None,
                    catalog_gets=3 if commit is None else 2)
    return raw,metadata


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('alias',help='Exact reviewed release URL used by the existing filter')
    parser.add_argument('--commit',help='Full publication SHA; skips ref resolution')
    parser.add_argument('--accept-stale',nargs=3,metavar=('COMMIT','REQUEST_ID','BODY_SHA256'))
    parser.add_argument('--metadata',type=Path,help='Optional metadata JSON file, separate from stdout body')
    args=parser.parse_args(argv)
    consent=dict(zip(('commit','request_id','sha256'),args.accept_stale)) if args.accept_stale else None
    try:
        raw,metadata=lookup(args.alias,commit=args.commit,stale_acceptance=consent)
        if args.metadata is not None:
            args.metadata.write_text(json.dumps(metadata,indent=2)+'\n')
        sys.stdout.buffer.write(raw)
        return 0
    except StaleObservation as error:
        print(json.dumps({'error':'stale_acceptance_required','acceptance':error.acceptance}),file=sys.stderr)
    except (Refusal,ValueError,KeyError,TypeError,OSError):
        print('{"error":"catalog_lookup_refused"}',file=sys.stderr)
    return 1


if __name__=='__main__':
    raise SystemExit(main())
