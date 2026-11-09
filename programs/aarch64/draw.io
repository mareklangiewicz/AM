#!/bin/sh
# AM INSTALL SCRIPT VERSION 3.5
# AM-CATALOG-RECIPE 1
# AM-RECIPE-DECLARATION 1
set -eu
APP=draw.io
CATALOG_ALIAS=https://api.github.com/repos/jgraph/drawio-desktop/releases
CATALOG_FORMAT=3
CATALOG_RECIPE=aarch64/draw.io
CATALOG_REPOSITORY_ID=92443980
CATALOG_REPOSITORY=jgraph/drawio-desktop
CATALOG_CHANNEL=any
CATALOG_ASSET_PATTERN='^.*$'
CATALOG_URL_RULES='[{"pattern":"https.*download.*mage$","ignore_case":true,"exclude":false},{"pattern":"aarch64|arm64","ignore_case":true,"exclude":false}]'

# shellcheck source=modules/appimage.am
. "/opt/am/modules/appimage.am"
am_appimage "$0" "$@"
