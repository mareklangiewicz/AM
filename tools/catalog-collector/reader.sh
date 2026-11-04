#!/bin/sh
# Compatibility entry point; maintained runtime is distributed with AM.
exec sh "$(dirname "$0")/../../modules/catalog-yaml-reader.am" "$@"
