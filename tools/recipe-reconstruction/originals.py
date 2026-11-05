"""Pinned Git originals and conservative whole-file template recognition."""
from dataclasses import dataclass
import difflib
import hashlib
from collections import Counter, defaultdict
import re
import shlex
import subprocess
import tarfile
from pathlib import Path

LIMIT = 1024 * 1024
# Upstream edit markers, not arbitrary uppercase shell variables or boilerplate.
SLOTS = re.compile(r'WEBPAGE-CONTAINING-URLS|MAIN-DOMAIN-OR-SITE|USER/REPO|'
                   r'DOMAIN/REPOSITORY|GIVEMEANAME|MYWEBSITE|YOURCATEGORY|YOURICONURL|'
                   r'SAMPLE|REPLACETHIS|FUNCTION|ITEM|KEYWORD[12]|VARIANT[12]|TEST[1-4]|DESCRIPTION')
LITERAL = re.compile(r'[A-Za-z0-9_.:/+@-]*\Z')


def text(data):
    if len(data) > LIMIT or b'\0' in data:
        raise ValueError('source exceeds 1 MiB or contains NUL')
    return data.decode('utf-8')


class Originals:
    def __init__(self, repo):
        self.repo = Path(repo).resolve()
        self.cache = {}

    def git(self, *args):
        try:
            return subprocess.check_output(['git', '--no-replace-objects', '-C', str(self.repo), *args],
                                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as error:
            raise ValueError('required Git originals unavailable: '+error.stderr.decode(errors='replace').strip()) from error

    def revision(self, ref):
        return self.git('rev-parse', '--verify', '--end-of-options', ref+'^{commit}').decode().strip()

    def read(self, commit, path):
        key = (commit, path)
        if key not in self.cache:
            self.cache[key] = text(self.git('show', commit+':'+path))
        return self.cache[key]

    def paths(self, commit, prefix):
        return self.git('ls-tree', '-r', '--name-only', commit, '--', prefix).decode().splitlines()

    def recipes(self, commit, prefix):
        # Stream the selected Git tree once instead of one subprocess per recipe.
        process = subprocess.Popen(['git', '--no-replace-objects', '-C', str(self.repo),
                                    'archive', commit, '--', prefix], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
                for entry in archive:
                    if entry.isfile():
                        yield entry.name, text(archive.extractfile(entry).read(LIMIT+1))
            if process.wait():
                raise ValueError(process.stderr.read().decode(errors='replace'))
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait()
            process.stdout.close()
            process.stderr.close()


def functions(generator, repository):
    """Default GitHub/Codeberg expressions from original generator assignments.

    Unknown generator syntax simply supplies no approved default; it never
    makes a recipe's arbitrary FUNCTION parameter count as standard logic.
    """
    result = set()
    for line in generator.splitlines():
        if not line.lstrip().startswith('FUNCTION='):
            continue
        try:
            words = shlex.split(line.strip()[len('FUNCTION='):])
        except ValueError:
            continue
        if len(words) != 1 or '$CURL_COMMAND_REF' not in words[0]:
            continue
        for origin in ('https://api.github.com/repos', 'https://codeberg.org'):
            value = words[0].replace('$CURL_COMMAND_REF', 'curl -Ls '+origin)
            value = value.replace('$RESPONSE', repository).replace('$q', "'").replace('\\\\', '\\')
            result.add(value)
    return result


@dataclass
class Template:
    commit: str
    path: str
    body: str
    generator: str

    def __post_init__(self):
        self.lines = self.body.splitlines(keepends=True)
        self.slots, self.patterns = [], []
        self.tokens = list(SLOTS.finditer(self.body))
        # Matching each physical line bounds captures and prevents added lines
        # from disappearing into a greedy shell-code parameter.
        for line in self.lines:
            parts, end, names = [], 0, []
            for slot in SLOTS.finditer(line):
                name = 'p'+str(len(self.slots))
                parts += [re.escape(line[end:slot.start()]), '(?P<'+name+'>[^\r\n]*?)']
                self.slots.append(slot[0]); names.append(name); end = slot.end()
            parts.append(re.escape(line[end:]))
            self.patterns.append((re.compile(''.join(parts)), names))

    @property
    def identity(self):
        return self.commit+':'+self.path

    def render(self, parameters):
        if not isinstance(parameters, list) or len(parameters) != len(self.tokens) or any(not isinstance(v, str) or '\n' in v or '\r' in v or '\0' in v for v in parameters):
            raise ValueError('one single-line value is required for each template slot')
        values = iter(parameters)
        return SLOTS.sub(lambda match: next(values), self.body)

    def match(self, source):
        lines = source.splitlines(keepends=True)
        if len(lines) != len(self.patterns) or any(len(line) > 8192 for line in lines):
            return None
        parameters = []
        for line, (pattern, names) in zip(lines, self.patterns):
            match = pattern.fullmatch(line)
            if not match:
                return None
            parameters.extend(match[name] for name in names)
        if self.render(parameters) != source:
            return None
        samples = {value for slot, value in zip(self.slots, parameters) if slot == 'SAMPLE'}
        if len(samples) != 1 or not re.fullmatch(r'[a-z0-9][a-z0-9.+_-]*', next(iter(samples))):
            return None
        sites = {value for slot, value in zip(self.slots, parameters) if slot in ('REPLACETHIS','USER/REPO','DOMAIN/REPOSITORY')
                 and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value)}
        approved = set().union(*(functions(self.generator, site) for site in sites))
        review = []
        for index, (slot, value) in enumerate(zip(self.slots, parameters)):
            if slot == 'FUNCTION':
                if value not in approved:
                    review.append(dict(slot=index, marker=slot, reason='custom or unrecognized shell expression', value=value))
            elif not LITERAL.fullmatch(value) or value == slot:
                review.append(dict(slot=index, marker=slot, reason='unresolved or nonliteral parameter', value=value))
        # A simple generated recipe repeats the same site and download command
        # in installer/updater. A disagreement must not be blessed as standard.
        if self.path in ('templates/AM-SAMPLE-AppImage', 'templates/AM-SAMPLE-Archive'):
            for marker in ('REPLACETHIS', 'FUNCTION'):
                values = {v for k,v in zip(self.slots, parameters) if k == marker}
                if len(values) > 1:
                    review.append(dict(marker=marker, reason='installer/updater parameters differ'))
        return dict(template=self.identity, source_sha256=hashlib.sha256(self.body.encode()).hexdigest(),
                    parameters=parameters, parameter_review=review,
                    status='parameter_review' if review else 'instance', compatibility='unassessed')


class Catalogue:
    def __init__(self, originals, revisions):
        self.originals = originals
        self.templates = []
        for revision in dict.fromkeys(originals.revision(ref) for ref in revisions):
            generator = originals.read(revision, 'modules/template.am')
            for path in originals.paths(revision, 'templates/'):
                self.templates.append(Template(revision, path, originals.read(revision, path), generator))
        if not self.templates:
            raise ValueError('no upstream templates discovered')

    def check(self, source, explain=False):
        matches = [result for template in self.templates if (result := template.match(source))]
        standard = [m for m in matches if m['status'] == 'instance']
        result = dict(status='instance' if standard else 'parameter_review' if matches else 'unmatched',
                      matches=matches, templates_checked=len(self.templates), compatibility='unassessed')
        if explain and not matches:
            closest = max(self.templates, key=lambda t: difflib.SequenceMatcher(
                None, t.lines, source.splitlines(keepends=True), autojunk=False).ratio())
            result['nearest_template'] = closest.identity
            result['diff'] = ''.join(difflib.unified_diff(closest.lines, source.splitlines(keepends=True),
                                                        fromfile='original template (unexpanded)', tofile='recipe'))
        return result

    def render(self, identity, parameters):
        for template in self.templates:
            if template.identity == identity:
                return template.render(parameters)
        raise ValueError('unknown pinned template identity')

    def inventory(self, commit, prefix):
        for path, source in self.originals.recipes(commit, prefix):
            result = self.check(source)
            action = {'instance':'review_runtime_policy', 'parameter_review':'inspect_parameter_logic',
                      'unmatched':'inspect_unmatched_source'}[result['status']]
            yield dict(recipe=path, source_commit=commit, source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                       migration_action=action, **result)


def migration_summary(rows):
    """Compact, reviewable batch planning from the same classifications as tests."""
    counts, families, examples = Counter(), Counter(), defaultdict(list)
    commits = set()
    templates_checked = 0
    for row in rows:
        counts[row['status']] += 1
        commits.add(row['source_commit'])
        templates_checked = row['templates_checked']
        if len(examples[row['status']]) < 5:
            examples[row['status']].append(row['recipe'])
        for match in row['matches']:
            families[match['template']] += 1
    return dict(recipes=sum(counts.values()), counts=dict(counts), source_commits=sorted(commits),
                templates_checked=templates_checked, matched_families=dict(sorted(families.items())),
                examples=dict(examples), compatibility='unassessed', automatic_conversion=False)
