#!/bin/sh
# AM INSTALL SCRIPT VERSION 3.5
# AM-CATALOG-RECIPE 1
set -eu
APP=exsplode.re
CATALOG_FORMAT=3
CATALOG_RECIPE="x86_64/exsplode.re"
CATALOG_ALIAS="https://api.github.com/repos/AmarOk1412/Eksplode.re/releases"

select_asset() {
	sed 's/[()",{} ]/\n/g' | grep -oi "https.*mage$" | grep -vi "i386\|i686\|aarch64\|arm64\|armv7l" | head -1
}

# shellcheck source=modules/appimage.am
. "/opt/am/modules/appimage.am"
am_appimage "$0" "$@"
