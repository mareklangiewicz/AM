#!/bin/sh
# Format-2 reader: full validation, byte caps and private output spooling.
set -eu
export LC_ALL=C
# BusyBox standalone shells/timeout may prefer built-in applets even when PATH
# contains another executable. Resolve external tools to paths explicitly.
external_tool() {
    remaining=${PATH-}
    while :; do
        case $remaining in
            *:*) directory=${remaining%%:*}; remaining=${remaining#*:}; more=yes ;;
            *) directory=$remaining; more=no ;;
        esac
        candidate=${directory:-.}/$1
        if [ -f "$candidate" ] && [ -x "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
        [ "$more" = yes ] || return 1
    done
}
usage() { echo 'usage: reader.sh validate|releases|apps|asset_facts FILE | assets FILE RELEASE | get FILE KEY... | rows FILE COLLECTION FIELD...' >&2; exit 2; }
[ "$#" -ge 2 ] || usage
operation=$1 file=$2; shift 2
query='' fields='' field_count=0
case $operation in
    validate|releases|apps|asset_facts) [ "$#" -eq 0 ] || usage ;;
    assets) [ "$#" -eq 1 ] || usage ;;
    get) [ "$#" -ge 1 ] || usage ;;
    rows)
        [ "$#" -ge 2 ] || usage
        case $1 in ''|*[!a-z0-9/]*) usage ;; esac
        query=/$1; shift
        for field do
            field_count=$((field_count + 1))
            [ "$field_count" -le 10 ] || usage
            case $field in ''|*[!a-z_]*) usage ;; esac
            fields="$fields$field "
        done
        set -- ;;
    *) usage ;;
esac
for key do
    case $key in ''|*[!a-zA-Z0-9_.+-]*) usage ;; esac
    query=$query/$key
done
[ -f "$file" ] && [ -r "$file" ] || { echo 'catalog YAML: unreadable file' >&2; exit 2; }
# Trial input/output bounds; awk repeats validation for direct invocation.
AM_YAML_MAX_INPUT_BYTES=${AM_YAML_MAX_INPUT_BYTES:-33554432}
AM_YAML_MAX_OUTPUT_BYTES=${AM_YAML_MAX_OUTPUT_BYTES:-16777216}
for bound in "$AM_YAML_MAX_INPUT_BYTES" "$AM_YAML_MAX_OUTPUT_BYTES"; do
    case $bound in ''|*[!0-9]*) usage ;; esac
    [ "${#bound}" -le 8 ] && [ "$bound" -le 33554432 ] || usage
done
[ "$AM_YAML_MAX_INPUT_BYTES" -gt 0 ] || usage
export AM_YAML_MAX_INPUT_BYTES AM_YAML_MAX_OUTPUT_BYTES
awk_command=$(external_tool awk) || { echo 'catalog YAML: external awk unavailable' >&2; exit 2; }
# A size check before awk bounds allocation; awk also caps consumed bytes.
[ "$(wc -c < "$file")" -le "$AM_YAML_MAX_INPUT_BYTES" ] || { echo 'catalog YAML: file too large' >&2; exit 2; }
# Spool privately: malformed suffixes never expose earlier query results.
if [ -n "${AM_YAML_PRIVATE_SPOOL:-}" ]; then
    spool=$AM_YAML_PRIVATE_SPOOL
    (set -C; : > "$spool") || exit 2
else
    spool=$(mktemp) || exit 2
fi
trap 'rm -f "$spool"' 0
trap 'exit 2' HUP INT TERM
status=0
set -- "$awk_command" -f "$(dirname "$0")/reader.awk"
AM_YAML_OPERATION=$operation AM_YAML_QUERY=$query AM_YAML_FIELDS=$fields "$@" < "$file" > "$spool" || status=$?
[ "$status" -eq 0 ] || exit "$status"
cat "$spool"
