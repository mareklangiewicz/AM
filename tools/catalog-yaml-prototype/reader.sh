#!/bin/sh
# THROWAWAY: local format experiment; no network or production integration.
set -eu
export LC_ALL=C
usage() { echo 'usage: reader.sh validate|releases|apps FILE | assets FILE RELEASE | get FILE KEY...' >&2; exit 2; }
[ "$#" -ge 2 ] || usage
operation=$1 file=$2; shift 2
case $operation in
    validate|releases|apps) [ "$#" -eq 0 ] || usage ;;
    assets) [ "$#" -eq 1 ] || usage ;;
    get) [ "$#" -ge 1 ] || usage ;;
    *) usage ;;
esac
query=
for key do
    case $key in ''|*[!a-zA-Z0-9_.+-]*) usage ;; esac
    query=$query/$key
done
[ -f "$file" ] && [ -r "$file" ] || { echo 'catalog YAML: unreadable file' >&2; exit 2; }
# A size check before awk bounds allocation; awk also caps consumed bytes.
[ "$(wc -c < "$file")" -le 33554432 ] || { echo 'catalog YAML: file too large' >&2; exit 2; }
AM_YAML_OPERATION=$operation AM_YAML_QUERY=$query awk -f "$(dirname "$0")/reader.awk" < "$file"
