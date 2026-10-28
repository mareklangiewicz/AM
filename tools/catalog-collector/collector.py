"""Bounded collector core. No network implementation, environment or CLI access.

Transport yields Connected, Headers, Chunk, End events. It must itself interrupt
blocking IO at the supplied absolute monotonic deadlines; the core checks every
event boundary too. Clock supplies utcnow() and monotonic().
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re

SOURCE_CAP = 7  # six historical sources plus the reviewed am-utils candidate
BODY_CAP = 8_000_000
HEADER_CAP = 64_000
VALUE_CAP = 8_192
PUBLIC_HEADERS = frozenset({
    'etag', 'last-modified', 'date', 'link', 'location', 'retry-after',
    'content-type', 'content-length', 'x-ratelimit-limit',
    'x-ratelimit-remaining', 'x-ratelimit-reset', 'x-ratelimit-used',
    'x-ratelimit-resource',
})


class Refusal(ValueError):
    """Fixed diagnostic codes only; never interpolate caller/transport values."""


def require(ok, code):
    if not ok:
        raise Refusal(code)


def timestamp(value):
    require(isinstance(value, str), 'invalid_time')
    try:
        parsed = datetime.fromisoformat(value)
        require(parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0,
                'invalid_time')
        return parsed
    except (TypeError, ValueError, OverflowError):
        raise Refusal('invalid_time') from None


def wall(clock):
    value = clock.utcnow()
    require(isinstance(value, datetime) and value.utcoffset() is not None
            and value.utcoffset().total_seconds() == 0, 'invalid_clock')
    return value


def mono(clock):
    value = clock.monotonic()
    require(type(value) in (int, float) and math.isfinite(value), 'invalid_clock')
    return value


def identity(value):
    require(type(value) is int and value > 0, 'invalid_repository_id')
    return value


@dataclass(frozen=True)
class Descriptor:
    url: str
    api_version: str = '2022-11-28'
    accept: str = 'application/vnd.github+json'

    def validate(self, repository_id):
        require(self.api_version == '2022-11-28' and
                self.accept == 'application/vnd.github+json', 'unreviewed_representation')
        require(isinstance(self.url, str), 'unreviewed_url')
        match = re.fullmatch(
            r'https://api\.github\.com/(?:repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|'
            r'repositories/(?P<id>[1-9][0-9]*))/releases'
            r'(?:/latest|/tags/[A-Za-z0-9_.%+-]+)?'
            r'(?:\?(?:page|per_page)=[1-9][0-9]*(?:&(?:page|per_page)=[1-9][0-9]*)*)?',
            self.url)
        require(match is not None, 'unreviewed_url')
        if match.group('id'):
            require(int(match.group('id')) == repository_id, 'numeric_identity_conflict')

    @property
    def request_id(self):
        return hashlib.sha256(json.dumps(
            {'url': self.url, 'api_version': self.api_version, 'accept': self.accept},
            sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Source:
    descriptor: Descriptor
    repository_id: int
    identity_evidence: str
    aliases: tuple = ()


@dataclass(frozen=True)
class Prior:
    descriptor: Descriptor
    body: bytes
    sha256: str
    validated_at: str
    validators: tuple = ()  # (('etag', value), ...) with no request credentials
    availability: str = 'available'


@dataclass(frozen=True)
class Request:
    source: Source
    prior: Prior | None = None

    @property
    def condition(self):
        return self.prior.validators if self.prior and self.prior.availability == 'available' else ()


@dataclass(frozen=True)
class Plan:
    workflow_repository_id: int
    requests: tuple


def validate_plan(value, workflow_repository_id):
    identity(workflow_repository_id)
    require(type(value) is Plan and value.workflow_repository_id == workflow_repository_id,
            'workflow_identity_mismatch')
    identity(value.workflow_repository_id)
    require(type(value.requests) is tuple and 0 < len(value.requests) <= SOURCE_CAP, 'source_count')
    seen, aliases, locators = set(), set(), {}
    for request in value.requests:
        require(type(request) is Request and type(request.source) is Source, 'invalid_plan')
        source = request.source
        identity(source.repository_id)
        require(source.repository_id != workflow_repository_id, 'workflow_repository_excluded')
        require(type(source.descriptor) is Descriptor, 'invalid_descriptor')
        source.descriptor.validate(source.repository_id)
        require(isinstance(source.identity_evidence, str) and
                re.fullmatch(r'docs/track/[A-Za-z0-9_./-]+\.md#[A-Za-z0-9_-]+', source.identity_evidence)
                and '..' not in source.identity_evidence.split('/'), 'missing_identity_evidence')
        rid = source.descriptor.request_id
        require(rid not in seen, 'duplicate_descriptor')
        seen.add(rid)
        require(type(source.aliases) is tuple, 'invalid_aliases')
        # The descriptor itself also occupies its exact consumer alias.
        for alias in (source.descriptor.url, *source.aliases):
            Descriptor(alias).validate(source.repository_id)
            locator = alias.split('/releases', 1)[0].lower()
            require(locators.get(locator, source.repository_id) == source.repository_id,
                    'repository_identity_conflict')
            locators[locator] = source.repository_id
            require(alias not in aliases, 'duplicate_alias')
            aliases.add(alias)
        prior = request.prior
        if prior is not None:
            require(type(prior) is Prior and prior.descriptor == source.descriptor,
                    'prior_descriptor_mismatch')
            require(type(prior.body) is bytes and len(prior.body) <= BODY_CAP and
                    hashlib.sha256(prior.body).hexdigest() == prior.sha256, 'prior_body_integrity')
            timestamp(prior.validated_at)
            require(prior.availability in {'available', 'unavailable', 'retired', 'unknown'},
                    'invalid_availability')
            require(type(prior.validators) is tuple and len(prior.validators) <= 2,
                    'invalid_validators')
            keys = set()
            for pair in prior.validators:
                require(type(pair) is tuple and len(pair) == 2, 'invalid_validators')
                k, v = pair
                require(k in {'etag', 'last-modified'} and k not in keys and
                        isinstance(v, str) and 0 < len(v.encode()) <= VALUE_CAP and
                        '\r' not in v and '\n' not in v, 'invalid_validators')
                keys.add(k)
    return value


def plan(manifest, workflow_identity, previous_state=None):
    """A reviewed tuple of Sources, trusted workflow ID, optional ID->Prior map."""
    require(type(manifest) is tuple, 'invalid_manifest')
    previous = previous_state if previous_state is not None else {}
    require(type(previous) is dict, 'invalid_previous_state')
    require(all(type(s) is Source and type(s.descriptor) is Descriptor for s in manifest),
            'invalid_manifest')
    ids = {s.descriptor.request_id for s in manifest}
    require(set(previous) <= ids, 'unknown_previous_source')
    value = Plan(workflow_identity, tuple(Request(s, previous.get(s.descriptor.request_id))
                                         for s in manifest))
    return validate_plan(value, workflow_identity)


@dataclass(frozen=True)
class Limits:
    connect_deadline: float
    request_deadline: float
    batch_deadline: float
    body_bytes: int = BODY_CAP
    header_bytes: int = HEADER_CAP


@dataclass(frozen=True)
class Connected:
    pass


@dataclass(frozen=True)
class Headers:
    status: int
    values: tuple  # includes discarded headers in size accounting
    condition_sent: tuple = ()  # transport's actual conditional request evidence


@dataclass(frozen=True)
class Chunk:
    data: bytes


@dataclass(frozen=True)
class End:
    pass


def selected_headers(pairs):
    require(type(pairs) is tuple, 'invalid_headers')
    selected, seen, total = {}, set(), 0
    for pair in pairs:
        require(type(pair) is tuple and len(pair) == 2, 'invalid_headers')
        key, value = pair
        require(isinstance(key, str) and isinstance(value, str), 'invalid_headers')
        total += len(key.encode()) + len(value.encode()) + 4
        require(total <= HEADER_CAP, 'header_overflow')
        require(re.fullmatch(r'[A-Za-z0-9-]+', key) and '\r' not in value and '\n' not in value,
                'invalid_headers')
        key = key.lower()
        if key in PUBLIC_HEADERS:
            require(key not in seen and len(value.encode()) <= VALUE_CAP, 'invalid_public_header')
            seen.add(key)
            selected[key] = value
    return selected


def stop_for_response(status, headers):
    if status == 429 or 'retry-after' in headers:
        return 'rate_limit'
    if status == 401:
        return 'authentication_refused'
    remaining = headers.get('x-ratelimit-remaining')
    if status == 403:
        return 'rate_limit' if remaining == '0' else 'authentication_refused'
    required = ('x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset')
    if any(not re.fullmatch(r'[0-9]{1,16}', headers.get(k, '')) for k in required):
        return 'quota_headers_missing_or_invalid'
    limit, left, reset = (int(headers[k]) for k in required)
    if limit <= 0 or left > limit or reset <= 0:
        return 'quota_headers_missing_or_invalid'
    if left <= 100:
        return 'quota_reserve'
    return None


def collect(value, transport, clock, credential, *, workflow_identity):
    """No environment lookup or credential default. Revalidate before execute.

    A future trusted adapter must establish workflow identity/token provenance.
    Opaque credentials are passed only to execute and never formatted here.
    """
    validate_plan(value, workflow_identity)
    require(credential is not None and not isinstance(credential, (str, bytes)),
            'opaque_credential_required')
    start_wall, start_mono = wall(clock), mono(clock)
    # Validate every prior against the clock before any request can run.
    for request in value.requests:
        if request.prior:
            require(timestamp(request.prior.validated_at) <= start_wall, 'future_prior')
    attempts, stop, streak, total_bytes = [], None, 0, 0
    previous_wall, previous_mono = start_wall, start_mono
    for request in value.requests:
        now_wall, now_mono = wall(clock), mono(clock)
        require(now_wall >= previous_wall and now_mono >= previous_mono, 'clock_regressed')
        if now_mono >= start_mono + 300:
            stop = 'batch_deadline'
            break
        limits = Limits(min(now_mono + 10, start_mono + 300),
                        min(now_mono + 30, start_mono + 300), start_mono + 300)
        status, headers, buffer = None, {}, bytearray()
        connected, have_headers, completed = False, False, False
        actual_condition = ()
        outcome, response_time = 'transport_error', None
        events = None
        try:
            events = iter(transport.execute(request, credential, limits))
            for event in events:
                if type(event) is Chunk and type(event.data) is bytes:
                    total_bytes += len(event.data)
                tick, utc = mono(clock), wall(clock)
                require(tick >= previous_mono and utc >= previous_wall, 'clock_regressed')
                previous_mono, previous_wall = tick, utc
                if tick >= limits.batch_deadline:
                    outcome, stop = 'timeout', 'batch_deadline'
                    break
                if tick >= limits.request_deadline or (not connected and tick >= limits.connect_deadline):
                    outcome = 'timeout'
                    break
                if type(event) is Connected:
                    require(not connected and not have_headers, 'invalid_event_order')
                    connected = True
                elif type(event) is Headers:
                    require(connected and not have_headers and type(event.status) is int
                            and 200 <= event.status <= 599, 'invalid_response')
                    require(type(event.condition_sent) is tuple and
                            event.condition_sent == request.condition, 'conditional_evidence_mismatch')
                    actual_condition = event.condition_sent
                    headers = selected_headers(event.values)
                    status, have_headers = event.status, True
                elif type(event) is Chunk:
                    require(have_headers and type(event.data) is bytes, 'invalid_event_order')
                    require(len(buffer) + len(event.data) <= BODY_CAP, 'body_overflow')
                    buffer.extend(event.data)
                elif type(event) is End:
                    require(have_headers, 'invalid_event_order')
                    if 'content-length' in headers and status != 304:
                        length = headers['content-length']
                        require(re.fullmatch(r'[0-9]{1,16}', length) is not None, 'invalid_content_length')
                        if int(length) != len(buffer):
                            outcome = 'truncated_response'
                            break
                    if status == 304:
                        require(not buffer and request.condition and request.prior is not None,
                                'invalid_conditional_response')
                    completed, outcome, response_time = True, 'response', utc.isoformat()
                    break
                else:
                    raise Refusal('invalid_event')
        except Refusal:
            # Refusal instances are internal, but transport may raise one with secret text.
            # Never emit exception text, even from the transport's Refusal subclass.
            outcome, stop = 'protocol_refusal', 'protocol_refusal'
        except Exception:
            outcome = 'transport_error'
        finally:
            if events is not None and hasattr(events, 'close'):
                try:
                    events.close()
                except Exception:
                    pass
        finish_wall, finish_mono = wall(clock), mono(clock)
        if finish_wall < previous_wall or finish_mono < previous_mono:
            outcome, stop, completed, response_time = 'clock_refusal', 'clock_refusal', False, None
        if (finish_mono >= limits.request_deadline or finish_mono >= limits.batch_deadline
                or (not connected and finish_mono >= limits.connect_deadline)):
            outcome, completed, response_time = 'timeout', False, None
            if finish_mono >= limits.batch_deadline:
                stop = 'batch_deadline'
        if not completed:
            buffer.clear()  # partial/failed bodies are never observation candidates
        attempts.append({
            'request_id': request.source.descriptor.request_id,
            'descriptor': {'url': request.source.descriptor.url,
                           'api_version': request.source.descriptor.api_version,
                           'accept': request.source.descriptor.accept},
            'repository_id': request.source.repository_id,
            'request_started_at': now_wall.isoformat(),
            'response_completed_at': response_time,
            'attempt_finished_at': finish_wall.isoformat(),
            'status': status, 'headers': headers, 'body': bytes(buffer),
            'condition': dict(actual_condition), 'outcome': outcome,
        })
        if have_headers:
            stop = stop or stop_for_response(status, headers)
        streak = streak + 1 if not completed or status >= 500 else 0
        if streak >= 2:
            stop = stop or 'consecutive_failures'
        previous_wall, previous_mono = finish_wall, finish_mono
        if stop:
            break
    return attempts, {
        'attempted': len(attempts), 'completed': sum(a['outcome'] == 'response' for a in attempts),
        'not_attempted': [r.source.descriptor.request_id for r in value.requests[len(attempts):]],
        'stop_reason': stop, 'all_attempted': len(attempts) == len(value.requests),
        'complete': len(attempts) == len(value.requests) and all(a['outcome'] == 'response' for a in attempts),
        'received_bytes': total_bytes, 'elapsed_seconds': previous_mono - start_mono,
    }
