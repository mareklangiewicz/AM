#!/bin/sh
# Usage: catalog.sh [AM_DIR] [CACHE_DIR] > versions.tsv
# AM_DIR defaults to ../.. ; reads programs/x86_64-apps and programs/x86_64/*.
set -eu
here=$(dirname "$0"); . "$here/lib/vc.sh"
am=${1:-$here/../..}; cache=${2:-${XDG_CACHE_HOME:-$HOME/.cache}/am-version-catalog}
vc_names < "$am/programs/x86_64-apps" | vc_build "$am/programs/x86_64" "$cache"
