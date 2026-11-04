#!/bin/sh
# Offline example: inspect facts in an already obtained, single-commit snapshot.
set -eu
[ "$#" -eq 2 ] || { echo 'usage: browse.sh SNAPSHOT_DIRECTORY APP' >&2; exit 2; }
root=$1 app=$2
reader=$(dirname "$0")/reader.sh
repository_id=$(sh "$reader" get "$root/apps.yaml" apps "$app") || exit "$?"
file=$root/repositories/$repository_id.yaml
actual_id=$(sh "$reader" get "$file" repository_id) || exit "$?"
[ "$actual_id" = "$repository_id" ] || { echo 'catalog YAML: repository identity mismatch' >&2; exit 2; }
# TSV: release ID, then canonical JSON scalar tokens. Do not eval these values.
# observed_at includes the shared default when no release override is present.
exec sh "$reader" rows "$file" releases tag observed_at published_at prerelease title
