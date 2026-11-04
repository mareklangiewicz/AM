"""Exact-hash review of the 17 inventoried legacy updaters; no code execution."""
import argparse
import hashlib
import json
from pathlib import Path

from yaml_cutover_package import record

# Reviewed behavior, deliberately independent of an app's current source name.
ADAPTERS={
 'appimagetool':('embedded-appimage-update','appimageupdatetool -Or',
     'Embedded update URL can differ from catalog selection; decide transport and URL identity explicitly.'),
 'appimageupdatetool':('embedded-appimage-update-custom-identity','real_version=${real_version%.zsync}',
     'Preserve Marek patch recording the URL actually used by embedded self-update, not scraped release URL.'),
 'btop':('archive-directory-layout','./bin/$APP',
     'Preserve bin/btop, extracted directory contents and launcher; raw single-file lifecycle is incompatible.'),
 'emmylua':('multi-asset-toolset','BINS="emmylua_ls emmylua_check emmylua_doc_cli luafmt"',
     'Select and stage four same-release archives before replacing tools; define interrupted multi-file recovery.'),
 'fzf':('archive-single-binary','tar fx ./*tar*',
     'Add reviewed tar extraction and exact fzf entry selection; retain URL version identity.'),
 'kitty':('archive-directory-layout','./bin/"$SUBAPP"',
     'Preserve bin/kitty, bin/kitten, supporting tree and launchers; not a raw executable replacement.'),
 'lazygit':('archive-single-binary','Linux_x86_64',
     'Select archive and extract exact lazygit entry; retain supporting files intentionally.'),
 'logseq-app-db-nightly':('publication-time-appimage','releases/tags/nightly',
     'Version identity is published_at, not asset URL; preserve same-URL refresh by release publication.'),
 'logseq-app-og':('appimage-latest-rule','releases/latest',
     'Shared AppImage lifecycle candidate after explicit latest replacement and numeric/list evidence.'),
 'neovide':('embedded-appimage-update','appimageupdatetool -Or',
     'Resolve latest selection and embedded self-update identity before switching transport.'),
 'neovide-nightly':('embedded-appimage-update','appimageupdatetool -Or',
     'Preserve nightly gate; resolve embedded self-update versus selected release and same-URL refresh.'),
 'rclone':('archive-single-binary','linux-amd64.zip',
     'Handle nested ZIP directory, exact rclone binary, supporting files and safe archive member paths.'),
 'rclone-ui':('embedded-appimage-update','appimageupdatetool -Or',
     'Resolve embedded update target/refresh behavior; do not replace by name alone.'),
 'satty':('embedded-appimage-update','appimageupdatetool -Or',
     'Resolve latest replacement and embedded update target before changing updater.'),
 'yt-dlp':('direct-single-binary',"'https.*yt.*linux$'",
     'Closest to shared executable lifecycle; still needs explicit numeric enrollment/policy and updater transition.'),
 'zellij':('archive-single-binary','apple\\|windows\\|darwin',
     'Preserve OS/architecture exclusion and archive member selection; generic raw-file lifecycle is incompatible.'),
 'zmx':('archive-single-binary','apple\\|windows\\|darwin\\|macos',
     'Preserve additional macos exclusion and exact archive entry; review source/local drift.'),
}


def audit(inventory, root):
    clients=[c for c in inventory['clients'] if c['kind']=='legacy-standalone']
    if {c['app'] for c in clients} != set(ADAPTERS):
        raise ValueError('legacy inventory differs from reviewed 17-client scope')
    rows=[]
    for client in clients:
        path=Path(client['installation'])/'AM-updater'
        expected=inventory['files'][str(path)]
        if record(path)!=expected: raise ValueError('legacy updater drift: '+client['app'])
        body=path.read_bytes()
        if hashlib.sha256(body).hexdigest()!=expected['sha256']:
            raise ValueError('legacy updater changed during audit')
        category,marker,reason=ADAPTERS[client['app']]
        if marker not in body.decode(): raise ValueError('reviewed behavior missing: '+client['app'])
        source=Path(root)/'programs'/client['recipe']
        rows.append(dict(app=client['app'],installation=client['installation'],
            updater_sha256=expected['sha256'],adapter=category,reason=reason,
            source_path=str(source.relative_to(root)),
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            shared_source=b'# AM-CATALOG-RECIPE 1' in source.read_bytes().splitlines(),
            apply_ready=False))
    return dict(format=1,clients=rows,count=len(rows),
                evidence='hash-matched local scripts; no updater execution or upstream requests',
                conclusion='No legacy updater is automatically eligible for the recipe-only migrator.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('inventory','source','out'):p.add_argument('--'+name,required=True)
    args=p.parse_args()
    result=audit(json.loads(Path(args.inventory).read_text()),Path(args.source))
    with Path(args.out).open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
