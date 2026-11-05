"""Maintained compact-recipe bindings and managed updater bytes; no execution."""
from pathlib import Path
import re


def quote(value):
    return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('$','\\$').replace('`','\\`')+'"'


def bound_recipe(body, source_url, paths, modules):
    """Mirror the compact recipe binding subset; verify old bytes before reuse."""
    text = body.decode()
    entry = '. "/opt/am/modules/appimage.am"'
    if text.splitlines().count(entry) != 1 or '# AM-CATALOG-RECIPE 1' not in text.splitlines():
        raise ValueError('unsupported compact recipe')
    helper = 'catalog-yaml.am' if 'CATALOG_FORMAT=2' in text.splitlines() else 'catalog.am'
    binding = 'AMREPO=${AMREPO-'+quote(source_url)+'}\n'
    binding += ''.join(name+'='+quote(paths[name])+'\n' for name in
                       ('APPS_DIR','BIN_DIR','DESKTOP_DIR'))
    name = 'CATALOG_YAML_HELPER' if helper == 'catalog-yaml.am' else 'CATALOG_HELPER'
    binding += name+'='+quote(str(Path(modules)/helper))+'\n'
    return text.replace(entry,binding+'. '+quote(str(Path(modules)/'appimage.am'))).encode()


def installed_bindings(text):
    values = {}
    for name in ('APPS_DIR','BIN_DIR','DESKTOP_DIR'):
        rows = re.findall('^'+name+r'="([^"\n]+)"$',text,re.M)
        if len(rows) != 1 or not rows[0].startswith('/') or any(c in rows[0] for c in '\\$`'):
            raise ValueError('unsupported installed path binding: '+name)
        values[name]=rows[0]
    rows = re.findall(r'^AMREPO=\$\{AMREPO-"(https://raw\.githubusercontent\.com/[A-Za-z0-9_.+/-]+)"\}$',text,re.M)
    if len(rows) != 1:
        raise ValueError('unsupported installed source binding')
    return rows[0],values


def managed_updater(recipe):
    return ('#!/bin/sh\n# AM-CATALOG-UPDATER 1\nexec sh '+
            "'"+str(recipe).replace("'", "'\\''")+"' --am-update \"$@\"\n").encode()
