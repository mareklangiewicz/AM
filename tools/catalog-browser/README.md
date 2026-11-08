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

## Published review iterations

Marek authorized publishing unfinished browser iterations on November 8, 2026.
Canonical browser source stays on local main-marek. Push that exact revision to
`browser-review` to deploy; the default remote branch and scheduled collection
workflow remain unchanged. The Pages environment allows this specific branch.
The old prototype deployment workflow is disabled repository-wide to prevent it
replacing the review site. Do not enable target collection channels or mutate the
default branch merely to publish a browser iteration.

```
git push origin HEAD:refs/heads/browser-review
```

The workflow builds a clearly labelled saved-observation review snapshot from
public baseline `cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f`, using the accepted
converter and strict whole-tree validation. Tied tag evidence is refused per source.
Recipe evidence and operational health are not fabricated. Static data lives only
in the Pages artifact, not a new catalog branch or source index. Its content ID
is explicitly a review snapshot identity, not a catalog Git commit.

Artifact staging additionally accepts `--review-data <prepared-directory>` and
copies only hash-checked canonical YAML paths. `delivery.mjs` is the one generated
configuration file; all other browser/reader source stays byte-identical. The
review builder and metadata manifest are excluded. The root redirect preserves
query/hash. Old review IDs refuse in a newer build rather than returning different
data at the old identity; Load latest selects the bundled review. Long-term Git
pin retention remains the real catalog channel's responsibility.

The saved data intentionally retains original observation ages. This is UI review,
not production freshness, scale, recipe-evidence or accessibility acceptance.
The normal catalog reader mode remains available with null delivery configuration;
main-branch deployment still has its separate explicit input/activation gate.
