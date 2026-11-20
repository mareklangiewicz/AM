"""Native v3 snapshots for maintained client tests, built the way collection builds them."""
import contracts as c
from bounded import normalize
from publication import publish_tree

# The schemas revision test snapshots use.
REVISION='a'*40


def sample_release():
    """One normalized release fact with awkward text, as normalize returns it."""
    return dict(tag='v2.0.0', title='Quotes " and \\; caf\u00e9 \u4e2d\u6587 \U0001f427\n\r\t\n',
                url='https://github.com/example/app/releases/tag/v2.0.0',
                published_at='2026-11-02T12:00:00Z', prerelease=False,
                assets={'789': dict(name="John's app #1.AppImage",
                                    url='https://github.com/example/app/releases/download/v2.0.0/app?x=a:b#part',
                                    size=0, content_type='')})


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


def publish_local(repo, apps, repositories, *, expected_parent, revision=REVISION):
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
