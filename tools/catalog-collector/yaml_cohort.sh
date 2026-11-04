#!/bin/sh
# Offline exact-pin acquisition + named policy. No network or installed binding.
set -eu
export LC_ALL=C
[ "$#" -ge 4 ] && [ "$#" -le 5 ] || exit 2
repo=$1 AM_YAML_PIN=$2 AM_YAML_RECIPE=$3 AM_YAML_NOW=$4 AM_YAML_ACCEPT=${5-}
case $AM_YAML_PIN in *[!0-9a-f]*|'') exit 2;; esac
[ "${#AM_YAML_PIN}" -eq 40 ] || exit 2
app=${AM_YAML_RECIPE#*/}
here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
reader=$here/reader.sh
AM_YAML_RECIPE=$AM_YAML_RECIPE AM_YAML_CHECK_RECIPE=1 \
    awk -f "$here/yaml_cohort.awk" </dev/null || exit 2
# Keep the existing trial caps, not an acceptance or increase.
AM_YAML_MAX_INPUT_BYTES=2097152 AM_YAML_MAX_OUTPUT_BYTES=2097152
export AM_YAML_MAX_INPUT_BYTES AM_YAML_MAX_OUTPUT_BYTES
[ "$(git -C "$repo" rev-parse --verify "$AM_YAML_PIN^{commit}")" = "$AM_YAML_PIN" ] || exit 2
source=$(git -C "$repo" rev-parse --absolute-git-dir)
umask 077
arena=$(mktemp -d) || exit 2
trap 'rm -rf "$arena"' 0
trap 'exit 2' HUP INT TERM
if [ -n "${AM_YAML_SESSION:-}" ]; then
    # Caller supplies an already private command-lifetime directory. Cache only
    # immutable acquisition bytes; never reuse selection/acceptance results.
    [ -d "$AM_YAML_SESSION" ] && [ ! -L "$AM_YAML_SESSION" ] || exit 2
    cache=$AM_YAML_SESSION/$AM_YAML_PIN
    if [ ! -d "$cache" ]; then
        mkdir "$cache"
        printf '%s\n' "$source" > "$cache/source"
    fi
    [ "$(cat "$cache/source")" = "$source" ] || exit 2
else
    cache=$arena/snapshot
    mkdir "$cache"
fi
acquire() {
    name=$1 target=$cache/$1
    if [ ! -f "$target" ]; then
        bytes=$(git -C "$repo" cat-file -s "$AM_YAML_PIN:$name") || return 2
        case $bytes in ''|*[!0-9]*) return 2;; esac
        [ "$bytes" -le "$AM_YAML_MAX_INPUT_BYTES" ] || return 2
        git -C "$repo" show "$AM_YAML_PIN:$name" > "$arena/object" || return 2
        [ "$(wc -c < "$arena/object")" -eq "$bytes" ] || return 2
        sh "$reader" validate "$arena/object" || return 2
        cp "$arena/object" "$target"
    fi
}
acquire apps.yaml || exit 2
AM_YAML_REPOSITORY=$(sh "$reader" get "$cache/apps.yaml" apps "$app") || exit 2
case $AM_YAML_REPOSITORY in ''|*[!0-9]*) exit 2;; esac
mkdir -p "$cache/repositories"
acquire "repositories/$AM_YAML_REPOSITORY.yaml" || exit 2
file=$cache/repositories/$AM_YAML_REPOSITORY.yaml
actual=$(sh "$reader" get "$file" repository_id) || exit 2
[ "$actual" = "$AM_YAML_REPOSITORY" ] || exit 2
sh "$reader" asset_facts "$file" > "$arena/facts" || exit 2
export AM_YAML_PIN AM_YAML_RECIPE AM_YAML_NOW AM_YAML_ACCEPT AM_YAML_REPOSITORY
# Full input validation has completed before policy or any output reaches caller.
awk -f "$here/yaml_cohort.awk" "$arena/facts" > "$arena/result" || exit 3
[ "$(wc -c < "$arena/result")" -le "$AM_YAML_MAX_OUTPUT_BYTES" ] || exit 2
cat "$arena/result"
