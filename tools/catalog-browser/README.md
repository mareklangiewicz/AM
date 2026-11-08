# Main-owned browser integration

Source lives in `web/catalog/`. The maintained strict reader is imported directly
from `tools/catalog-contract/`; there is no prototype parser or generated index.

Run focused contract/transport checks with:

```
node tools/catalog-browser/test_catalog.mjs
```

Run the explicitly labelled, loopback-only synthetic contract-fixture preview:

```
python3 tools/catalog-browser/preview.py --port 8765
```

Open `http://127.0.0.1:8765/web/catalog/?app=example`. This preview intercepts
GitHub reads and serves existing inert wire fixtures. It does not exercise real
public CORS, enrolled source coverage or browser performance qualification.
It exposes only browser modules/strict readers and the explicit fixture map.
The fixture identities, recipe links and commit IDs are synthetic examples.

Stage the public artifact into a **new** directory:

```
python3 tools/catalog-browser/stage.py /tmp/am-catalog-public
```

The artifact contains exactly six source files at their original relative paths,
plus a root redirect preserving query/hash and `.nojekyll`. Source bytes are
unchanged. Tests, tracker material, fixtures, preview interception and this README
are excluded. Keep the previous deployed artifact for rollback; staging refuses
to replace any existing output directory.

The prepared `catalog-pages.yml` runs only by manual dispatch on main-marek.
Deployment additionally requires both explicit `deploy=true` and the separately
controlled `CATALOG_BROWSER_ENABLED=true` variable. No variable is changed here.
The prototype worktree/branch and existing public artifact are preserved.

At separately authorized cutover, disable the old workflow repository-wide
before main deployment (the preserved prototype branch has its own old workflow
bytes, so a main-only conditional cannot disable those automatically):

```
gh workflow disable catalog-pages-prototype.yml --repo mareklangiewicz/AM
```

This command is preparation only; it has not run. The main copy additionally
skips prototype deployment when the activation variable is true. Review exact
source revisions, saved last-good artifact, activation/readback and rollback
commands in ticket 15 before dispatch or variable changes. No automatic public
activation is part of this implementation.
