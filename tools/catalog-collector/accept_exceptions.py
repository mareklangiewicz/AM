"""Read-only ticket-68 live acceptance, including all 922 already migrated recipes."""
import argparse
from pathlib import Path

from accept_large import accept
from exception_batch import DIRECTORY, PREVIOUS

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--parent',required=True)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    accept(args.run_id,args.revision,args.parent,args.output,package=DIRECTORY,
           payload_package=PREVIOUS,extra_migration=PREVIOUS/'prepared/migration.json')
