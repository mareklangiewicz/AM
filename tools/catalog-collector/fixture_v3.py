"""Native v3 snapshots for maintained client tests, from saved historical facts."""
import contracts as c
from publication import publish_tree
from rehearse_pipeline import seed_source


def publish_local(repo, apps, repositories, *, schema, max_file_bytes, expected_parent):
    revision=schema.split('/')[-3]
    paths={app:'repositories/source-'+str(rid)+'.yaml' for app,rid in apps.items()}
    tree={'repositories/source-'+str(rid)+'.yaml':c.encode(seed_source(repositories[str(rid)],revision))
          for rid in sorted(set(apps.values()))}
    tree['apps.yaml']=c.encode(dict(c.header('apps',revision),apps=paths))
    tree['catalog.yaml']=c.encode(dict(c.header('catalog',revision),
        inputs={key:revision for key in ('source','policy','recipes','rules','schemas')},
        producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1'))
    tree.update(c.partition_provenance(paths,{app:{'x86_64':dict(repository_id=rid,
        availability='unknown',classification='unknown')} for app,rid in apps.items()},revision))
    c.validate_tree(tree)
    return publish_tree(repo,tree,expected_parent)
