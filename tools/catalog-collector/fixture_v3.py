"""Native v3 snapshots for maintained client tests, built the way collection builds them."""
import contracts as c
from bounded import normalize
from publication import publish_tree

# The schemas revision test snapshots use (test_yaml_reader.SCHEMA's).
REVISION='a'*40


def repository(rid, name, releases, received_at, revision, *, complete=None):
    """The format-3 source document one releases response gives, through the
    same contracts.source projection collection uses. releases is the parsed
    response list; complete defaults to collection's rule (fewer than 100)."""
    acquired=dict(received_at=received_at,releases=normalize(releases,100,allow_missing_published=True),
                  history_complete=len(releases)<100 if complete is None else complete)
    return c.source(None,acquired,rid=rid,repository=name,revision=revision)


def expanded(document):
    """The document with every release expanded (full asset URLs, content
    types, observed_at), as a reader sees it."""
    return dict(document,releases={rid:c.expand_release(release,document['observed_at'])
                                   for rid,release in document['releases'].items()})


def publish_local(repo, apps, repositories, *, schema, max_file_bytes, expected_parent):
    revision=schema.split('/')[-3]
    paths={app:'repositories/source-'+str(rid)+'.yaml' for app,rid in apps.items()}
    tree={'repositories/source-'+str(rid)+'.yaml':c.encode(repositories[str(rid)])
          for rid in sorted(set(apps.values()))}
    tree['apps.yaml']=c.encode(dict(c.header('apps',revision),apps=paths))
    tree['catalog.yaml']=c.encode(dict(c.header('catalog',revision),
        inputs={key:revision for key in ('source','policy','recipes','rules','schemas')},
        producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1'))
    tree.update(c.partition_provenance(paths,{app:{'x86_64':dict(repository_id=rid,
        availability='unknown',classification='unknown')} for app,rid in apps.items()},revision))
    c.validate_tree(tree)
    return publish_tree(repo,tree,expected_parent)
