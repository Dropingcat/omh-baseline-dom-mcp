"""WR-ADD (L0+L1): the lite (local_single_owner) profile -- single-call tools for a cold agent.

Every function here takes the ``Service`` as ``svc`` and writes **only** through the
existing ``submit -> review -> admit`` methods, so the transaction, the append-only
event chain, the outbox, the idempotency rows and the immutability triggers are the
ones the strict profile already has.  Nothing is inserted into ``claims``/``events``
from this module.  The only direct inserts are the two additive tables of
migration v3 (``project_root``, ``adoptions`` via ``Store.initialize``).

Trust boundary: the profile, the identity (work/task/policy, principal, root,
review level) are launch-time facts of the server.  No tool argument can set them.
"""
import base64
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone

from .dom_contract import digest, raw_hash

LITE_POLICY_DOC = {'version': 'lite-policy/v1', 'profile': 'lite'}
BRANCH_RE = re.compile(r'^[A-Za-z0-9_-]{1,32}$')
MAX_TEXT_BYTES = 1 << 20
MAX_BRANCHES = 64
TYPES = ('quote', 'decision', 'formula', 'code', 'data', 'concept', 'text')
ROOT_REQUEST_REF = 'customer:request'
DEFAULT_ORIGIN_VERSION = 'lite-v1'

# optional per-type arguments of dom_claim (name -> python type) ------------------
FIELD_TYPES = {
    'source_ref': str, 'locator': str, 'source_snapshot_digest': str,
    'attribution': str, 'rationale': str, 'assumptions': list, 'alternatives': list,
    'expression': str, 'notation': dict, 'units': dict, 'derivation_refs': list,
    'repository_ref': str, 'relative_path': str, 'language': str, 'snapshot_digest': str,
    'artifact_ref': str, 'artifact_digest': str, 'method': str, 'columns': dict,
    'provenance': str, 'definition': str, 'scope': str, 'links': list,
    'classification': str, 'evidence': list,
}
COMMON_FIELDS = {'requirement_refs': list, 'reason': str, 'origin_version': str}
TYPE_ARGS = {
    'quote': ('source_ref', 'locator', 'source_snapshot_digest'),
    'decision': ('attribution', 'rationale', 'assumptions', 'alternatives'),
    'formula': ('expression', 'notation', 'units', 'assumptions', 'derivation_refs'),
    'code': ('repository_ref', 'relative_path', 'language', 'snapshot_digest', 'locator'),
    'data': ('artifact_ref', 'artifact_digest', 'method', 'columns', 'units', 'provenance'),
    'concept': ('definition', 'scope', 'assumptions', 'attribution', 'links'),
    'text': ('classification', 'evidence', 'attribution', 'assumptions'),
}


def identity(directory):
    """work_ref / task_ref / policy_digest of the lite profile, computed from the run directory."""
    h = hashlib.sha256(os.path.normcase(str(directory)).encode('utf8')).hexdigest()[:20]
    return 'lite:' + h, 'lite-task:' + h, digest(LITE_POLICY_DOC)


def _denied():
    from .admission import Denied
    return Denied


def _lite_only(svc):
    if not svc.lite:
        raise _denied()('PROFILE_STRICT')


def _now():
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------- arguments --
def _text_bytes(text, field='text'):
    Denied = _denied()
    if type(text) is not str:
        raise Denied('INVALID_FIELD', field=field)
    if not text.strip():
        raise Denied('REQUEST_REQUIRED' if field == 'request' else 'EMPTY_TEXT', field=field)
    try:
        raw = text.encode('utf-8')
    except UnicodeEncodeError:
        raise Denied('INVALID_TEXT', field=field) from None
    if len(raw) > MAX_TEXT_BYTES:
        raise Denied('TEXT_TOO_LARGE', field=field)
    return raw


def _str_list(value, field, allow_empty=True):
    Denied = _denied()
    if type(value) is not list or any(type(v) is not str or not v for v in value) or (not value and not allow_empty):
        raise Denied('INVALID_FIELD', field=field, hint="'%s' must be an array of non-empty strings." % field)
    return value


def _derived(typ, text, raw):
    """Metadata values that follow the body text (recomputed on dom_update)."""
    if typ == 'quote':
        return {'source_snapshot_digest': raw_hash(raw), 'locator': 'bytes:0-%d' % len(raw),
                'source_b64': base64.b64encode(raw).decode()}
    if typ == 'formula':
        return {'expression': text}
    if typ == 'code':
        return {'snapshot_digest': raw_hash(raw), 'locator': 'lines:1-%d' % (text.count('\n') + 1)}
    if typ == 'data':
        return {'artifact_digest': raw_hash(raw)}
    if typ == 'concept':
        return {'definition': text}
    return {}


def build_metadata(typ, text, raw, args):
    """Typed metadata with explicit arguments first and honest defaults second."""
    def pick(key, default):
        value = args.get(key)
        return default if value is None or value == '' or value == {} and key in ('notation', 'units') else value
    d = _derived(typ, text, raw)
    if typ == 'quote':
        return {'source_ref': pick('source_ref', 'agent:unspecified'),
                'source_snapshot_digest': pick('source_snapshot_digest', d['source_snapshot_digest']),
                'locator': pick('locator', d['locator']), 'source_b64': d['source_b64']}
    if typ == 'decision':
        return {'attribution': pick('attribution', 'agent'), 'rationale': pick('rationale', 'not stated by the agent'),
                'assumptions': pick('assumptions', []), 'alternatives': pick('alternatives', [])}
    if typ == 'formula':
        return {'expression': pick('expression', d['expression']),
                'notation': pick('notation', {'expression': 'free-text formula; symbols not itemised'}),
                'assumptions': pick('assumptions', []), 'units': pick('units', {'expression': 'unspecified'}),
                'derivation_refs': pick('derivation_refs', ['agent-entered'])}
    if typ == 'code':
        return {'repository_ref': pick('repository_ref', 'local:project'),
                'relative_path': pick('relative_path', 'unspecified.txt'),
                'language': pick('language', 'text'),
                'snapshot_digest': pick('snapshot_digest', d['snapshot_digest']),
                'locator': pick('locator', d['locator']), 'dirty': False}
    if typ == 'data':
        return {'artifact_ref': pick('artifact_ref', 'agent:inline'),
                'artifact_digest': pick('artifact_digest', d['artifact_digest']),
                'method': pick('method', 'agent-entered'), 'columns': pick('columns', {}),
                'units': pick('units', {'value': 'unspecified'}), 'provenance': pick('provenance', 'agent-entered')}
    if typ == 'concept':
        return {'definition': pick('definition', d['definition']), 'scope': pick('scope', 'project'),
                'assumptions': pick('assumptions', []), 'attribution': pick('attribution', 'agent'),
                'links': pick('links', [])}
    evidence = pick('evidence', [])
    classification = pick('classification', 'factual' if evidence else 'interpretation')
    return {'classification': classification, 'evidence': evidence,
            'attribution': pick('attribution', 'agent'), 'assumptions': pick('assumptions', [])}


def build_item(typ, text, raw, branch, args, requirement_refs, reason, local_id='c1'):
    return {'local_id': local_id, 'content_type': typ, 'body_b64': base64.b64encode(raw).decode(),
            'encoding': 'utf-8', 'media_type': 'text/plain', 'reason': reason, 'applicability': [branch],
            'metadata': build_metadata(typ, text, raw, args), 'requirement_refs': sorted(set(requirement_refs))}


def _package(svc, branch, revision, items, key, operation, origin_version, reason):
    return {'external_work_ref': svc.context.work, 'external_task_ref': svc.task, 'branch': branch,
            'expected_branch_revision': revision, 'schema_version': 'dom/v1', 'policy_digest': svc.policy,
            'idempotency_key': key, 'operation': operation, 'items': items, 'dependencies': {},
            'origin_version': origin_version, 'reason': reason}


# ------------------------------------------------------------- read helpers --
def _children(c):
    """old claim id -> replacement claim id (replacement events, all branches)."""
    out = {}
    for row in c.execute("SELECT claim_ref, payload FROM events WHERE kind='replacement' AND claim_ref IS NOT NULL ORDER BY seq"):
        try:
            out.setdefault(row[0], json.loads(row[1])['value']['value']['replacement_ref'])
        except (ValueError, TypeError, KeyError):
            continue
    return out


def _archived(c):
    return {r[0] for r in c.execute("SELECT DISTINCT claim_ref FROM events WHERE kind IN ('archive','replacement') AND claim_ref IS NOT NULL")}


def _lineage(children):
    """claim id -> (record_id, version): the record id is the first version's claim id."""
    parent = {new: old for old, new in children.items()}

    def info(cid):
        depth, seen = 1, {cid}
        while cid in parent and parent[cid] not in seen:
            cid = parent[cid]; seen.add(cid); depth += 1
        return cid, depth
    return info


def _level_expr(c):
    cols = {r[1] for r in c.execute('PRAGMA table_info(reviews)')}
    return 'rv.review_level' if 'review_level' in cols else 'NULL'


def _level(row_level, row_payload):
    if isinstance(row_level, str):
        return row_level
    try:
        level = json.loads(row_payload).get('review_level') if row_payload else None
    except (ValueError, TypeError, AttributeError):
        return None
    return level if isinstance(level, str) else None


def _claim_info(svc, c, claim_id):
    children = _children(c)
    record_id, version = _lineage(children)(claim_id)
    row = c.execute('SELECT s.review_id, t.revision FROM claim_snapshots s JOIN transactions t ON t.id=s.tx WHERE s.claim_id=?', (claim_id,)).fetchone()
    level = None
    if row:
        cols = {r[1] for r in c.execute('PRAGMA table_info(reviews)')}
        rv = c.execute('SELECT %s AS lvl, payload FROM reviews WHERE id=?' % ('review_level' if 'review_level' in cols else 'NULL'), (row['review_id'],)).fetchone()
        level = _level(rv['lvl'], rv['payload']) if rv else None
    sha = c.execute('SELECT raw_sha256 FROM claims WHERE id=?', (claim_id,)).fetchone()
    return {'record_id': record_id, 'version': version, 'review_level': level,
            'revision': row['revision'] if row else 0, 'raw_sha256': sha[0] if sha else ''}


def pending_rejected(c, branches):
    if not branches:
        return 0, 0
    ph = ','.join('?' * len(branches))
    pending = rejected = 0
    for r in c.execute(
            "SELECT c.id, EXISTS(SELECT 1 FROM claims cl WHERE cl.candidate=c.id) AS a1, "
            "EXISTS(SELECT 1 FROM idempotency i WHERE i.operation LIKE 'admit:%%' AND i.candidate_id=c.id) AS a2, "
            "(SELECT rr.payload FROM reviews rr WHERE rr.candidate=c.id ORDER BY rr.rowid DESC LIMIT 1) AS rp "
            "FROM candidates c WHERE c.branch IN (%s)" % ph, list(branches)):
        if r['a1'] or r['a2']:
            continue
        decision = None
        if r['rp']:
            try:
                decision = json.loads(r['rp']).get('decision')
            except (ValueError, TypeError, AttributeError):
                decision = None
        if decision is not None and decision != 'approve':
            rejected += 1
        else:
            pending += 1
    return pending, rejected


def _find_identical(svc, c, branch, item, after_rowid=0, exclude=None, unlinked=False):
    """A current claim of this branch with the same type, bytes, metadata and requirement refs."""
    raw = base64.b64decode(item['body_b64'])
    archived = _archived(c)
    linked = set(_children(c).values()) if unlinked else set()
    for row in c.execute('SELECT rowid AS rid, id, payload FROM claims WHERE origin_branch=? AND raw_sha256=? AND content_type=? ORDER BY rowid',
                         (branch, raw_hash(raw), item['content_type'])):
        if row['id'] == exclude or row['id'] in archived or row['id'] in linked or row['rid'] <= after_rowid:
            continue
        other = json.loads(row['payload'])
        if other.get('metadata') == item['metadata'] and sorted(other.get('requirement_refs', [])) == item['requirement_refs']:
            return row['id']
    return None


# -------------------------------------------------------------------- writes --
def _admitted_receipt(svc, candidate_id):
    with svc.store.read() as c:
        row = c.execute("SELECT result FROM idempotency WHERE external_work_ref=? AND operation LIKE 'admit:%' AND candidate_id=?",
                        (svc.context.work, candidate_id)).fetchone()
    return json.loads(row[0]) if row else None


def _commit(svc, branch, build):
    """submit -> self review -> admit through the existing methods; one bounded retry on a moved head."""
    res = {'status': 'REVISION_CONFLICT'}
    for attempt in range(3):
        with svc.store.read() as c:
            revision = svc.head(c, branch)
        pkg = build(revision)
        sub = svc.submit(json.dumps(pkg))
        if sub.get('status') != 'RECORDED_CANDIDATE':
            return _surface(sub)
        cid, dig = sub['candidate_id'], sub['intent_digest']
        receipt = _admitted_receipt(svc, cid)
        if receipt is None:
            rv = svc.review(cid, dig)
            if rv.get('status') != 'DEMO_REVIEWED':
                return rv
            res = svc.admit(cid, rv['review_id'], pkg['idempotency_key'], dig)
            if res.get('status') in ('REVISION_CONFLICT', 'STALE_REVIEW') and attempt < 2:
                continue
            if res.get('status') != 'DEMO_ADMITTED':
                return res
            receipt = res
        return receipt
    return res


def _surface(sub):
    """A validation refusal of the server-built package becomes a field-level hint."""
    if sub.get('status') == 'REJECTED' and sub.get('errors'):
        first = sub['errors'][0]
        return {'status': 'INVALID_FIELD', 'field': str(first.get('path'))[:80],
                'hint': 'Field %s refused (%s). %s' % (first.get('path'), first.get('code'), first.get('fix', ''))}
    return sub


def _write_claim(svc, branch, item, origin_version, reason, tag):
    """Admit one claim item on ``branch`` (or return the identical current one). -> dict with claim_id | refusal."""
    with svc.store.read() as c:
        existing = _find_identical(svc, c, branch, item)
        if existing:
            info = _claim_info(svc, c, existing)
            return dict(info, claim_id=existing, already=True)
    item_key = digest({'tag': tag, 'branch': branch, 'item': dict(item, local_id='')})[:40]

    def build(revision):
        key = 'lite-%s-%s-r%d' % (tag, item_key[:24], revision)
        return _package(svc, branch, revision, [item], key, 'claims', origin_version, reason)
    receipt = _commit(svc, branch, build)
    if receipt.get('status') != 'DEMO_ADMITTED':
        return receipt
    claim_id = receipt['claim_ids'][item['local_id']]
    with svc.store.read() as c:
        info = _claim_info(svc, c, claim_id)
    return dict(info, claim_id=claim_id, already=False)


def _validated_claim_args(svc, branch, typ, text, fields):
    """Shared argument checks of dom_claim. -> (raw, args, requirement_refs, reason, origin_version)."""
    Denied = _denied()
    if type(branch) is not str or not branch:
        raise Denied('INVALID_FIELD', field='branch', hint="'branch' must be one of the declared branch codes (see dom_describe).")
    svc.scope(branch)
    if type(typ) is not str or typ not in TYPES:
        raise Denied('UNKNOWN_TYPE', field='type')
    raw = _text_bytes(text)
    args = {}
    for name, value in fields.items():
        if value is None:
            continue
        if name in COMMON_FIELDS:
            if type(value) is not COMMON_FIELDS[name]:
                raise Denied('INVALID_FIELD', field=name)
            continue
        if name not in FIELD_TYPES:
            raise Denied('INVALID_FIELD', field=name, hint="Unknown argument '%s'." % name)
        if type(value) is not FIELD_TYPES[name]:
            raise Denied('INVALID_FIELD', field=name, hint="'%s' must be of type %s." % (name, FIELD_TYPES[name].__name__))
        if name not in TYPE_ARGS[typ]:
            raise Denied('INVALID_FIELD', field=name,
                         hint="'%s' does not apply to type '%s'. Allowed extra arguments for %s: %s." % (name, typ, typ, ', '.join(TYPE_ARGS[typ])))
        args[name] = value
    refs = _str_list(fields.get('requirement_refs') or [], 'requirement_refs')
    reason = fields.get('reason') or 'lite dom_claim'
    origin_version = fields.get('origin_version') or DEFAULT_ORIGIN_VERSION
    if type(reason) is not str or not reason.strip():
        raise Denied('INVALID_FIELD', field='reason')
    if type(origin_version) is not str or not origin_version.strip():
        raise Denied('INVALID_FIELD', field='origin_version')
    if typ == 'text' and args.get('classification') == 'factual' and not args.get('evidence'):
        raise Denied('INVALID_FIELD', field='evidence', hint="classification 'factual' needs evidence: [{\"ref\": \"...\", \"locator\": \"...\"}]; or omit classification for an interpretation.")
    return raw, args, refs, reason, origin_version


def claim(svc, branch, typ, text, fields):
    _lite_only(svc)
    svc.capability('submit')
    svc.ready()
    raw, args, refs, reason, origin_version = _validated_claim_args(svc, branch, typ, text, fields)
    item = build_item(typ, text, raw, branch, args, refs, reason)
    res = _write_claim(svc, branch, item, origin_version, reason, 'claim')
    if 'claim_id' not in res:
        return res
    cid = res['claim_id']
    steps = [
        {'tool': 'dom_find', 'arguments': {'branch': branch, 'query': text[:30]}, 'why': 'confirm the claim is stored and findable'},
        {'tool': 'dom_update', 'arguments': {'claim_id': cid, 'text': '<the full new text>', 'reason': '<why it changes>'},
         'why': 'to change this claim later: creates a new version, this one stays in history'},
        {'tool': 'dom_trace', 'arguments': {}, 'why': 'readiness: admitted_total and admitted_independent are separate numbers'},
    ]
    return {'status': 'ALREADY_RECORDED' if res['already'] else 'CLAIM_ADMITTED', 'simulated': True, 'claim_id': cid,
            'record_id': res['record_id'], 'version': res['version'], 'branch': branch, 'type': typ,
            'revision': res['revision'], 'review_level': res['review_level'], 'origin_version': origin_version,
            'raw_sha256': res['raw_sha256'], 'next_steps': steps}


def _rebuild_for_update(old_item, old_text, old_raw, new_text, new_raw, reason):
    typ = old_item['content_type']
    meta = dict(old_item['metadata'])
    old_d, new_d = _derived(typ, old_text, old_raw), _derived(typ, new_text, new_raw)
    for key, new_value in new_d.items():
        if key == 'source_b64' or meta.get(key) == old_d.get(key):
            meta[key] = new_value
    item = dict(old_item)
    item.update(local_id='u1', body_b64=base64.b64encode(new_raw).decode(), metadata=meta, reason=reason)
    return item


def update(svc, claim_id, text, reason):
    Denied = _denied()
    _lite_only(svc)
    svc.scope()
    svc.capability('submit')
    svc.ready()
    if type(claim_id) is not str or not claim_id:
        raise Denied('INVALID_FIELD', field='claim_id')
    if type(reason) is not str or not reason.strip():
        raise Denied('INVALID_FIELD', field='reason', hint="'reason' is required: say why the claim changes (it is recorded in the event chain).")
    new_raw = _text_bytes(text)
    with svc.store.read() as c:
        row = c.execute('SELECT rowid AS rid, * FROM claims WHERE id=?', (claim_id,)).fetchone()
        if row is None:
            raise Denied('NO_SUCH_CLAIM', field='claim_id')
        branch = row['origin_branch']
        children = _children(c)
        archived = _archived(c)
        old_raw = bytes(row['raw'])
        old_item = json.loads(row['payload'])
        old_rowid = row['rid']
    svc.scope(branch)
    if claim_id in children:
        current = children[claim_id]
        while current in children:
            current = children[current]
        raise Denied('NOT_CURRENT', claim_id=current)
    if claim_id in archived:
        raise Denied('NOT_CURRENT', hint='This claim was archived and has no current version.')
    if new_raw == old_raw:
        raise Denied('NO_CHANGE', claim_id=claim_id)
    old_text = old_raw.decode('utf-8')
    new_item = _rebuild_for_update(old_item, old_text, old_raw, text, new_raw, reason)
    origin_version = _origin_version_of(svc, claim_id)
    # step 1: the new version (an unlinked identical leftover of an interrupted earlier call is reused)
    with svc.store.read() as c:
        leftover = _find_identical(svc, c, branch, new_item, after_rowid=old_rowid, exclude=claim_id, unlinked=True)
    if leftover:
        new_id = leftover
    else:
        key_base = digest({'old': claim_id, 'item': dict(new_item, local_id='')})[:24]

        def build1(revision):
            return _package(svc, branch, revision, [new_item], 'lite-upd1-%s-r%d' % (key_base, revision), 'claims', origin_version, reason)
        receipt = _commit(svc, branch, build1)
        if receipt.get('status') != 'DEMO_ADMITTED':
            return receipt
        new_id = receipt['claim_ids']['u1']
    # step 2: mark the old version as replaced (existing 'replacement' event; the old row is untouched)
    event = {'local_id': 'r1', 'event_type': 'replacement', 'claim_ref': claim_id, 'reason': reason,
             'value': {'replacement_ref': new_id}, 'supersedes': '', 'ref': 'lite:dom_update'}

    def build2(revision):
        return _package(svc, branch, revision, [event], 'lite-upd2-%s-r%d' % (digest({'old': claim_id, 'new': new_id})[:24], revision),
                        'append', origin_version, reason)
    receipt2 = _commit(svc, branch, build2)
    if receipt2.get('status') != 'DEMO_ADMITTED':
        return {'status': 'UPDATE_INCOMPLETE', 'claim_id': new_id}
    with svc.store.read() as c:
        info = _claim_info(svc, c, new_id)
    steps = [
        {'tool': 'dom_find', 'arguments': {'branch': branch, 'query': text[:30]}, 'why': 'the new version is current; the old one is listed with is_current=false'},
        {'tool': 'dom_trace', 'arguments': {}, 'why': 'readiness counts only current versions'},
    ]
    return {'status': 'CLAIM_UPDATED', 'simulated': True, 'new_claim_id': new_id, 'supersedes': claim_id,
            'record_id': info['record_id'], 'version': info['version'], 'branch': branch,
            'revision': receipt2['revision'], 'review_level': info['review_level'],
            'raw_sha256': info['raw_sha256'], 'next_steps': steps}


def _origin_version_of(svc, claim_id):
    with svc.store.read() as c:
        row = c.execute('SELECT origin_version FROM claims WHERE id=?', (claim_id,)).fetchone()
    return row[0]


# ---------------------------------------------------------------------- find --
def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _strings(value)


def _preview(body, query):
    """At most 200 characters; windowed around the first hit when the hit is deep in a long body."""
    if len(body) <= 200:
        return body
    start = 0
    if query:
        low = body.lower()
        pos = low.find(query.lower()) if len(low) == len(body) else -1
        if pos > 150:
            start = max(0, pos - 60)
    head = '\u2026' if start > 0 else ''
    room = 200 - len(head)
    piece = body[start:start + room]
    if start + room < len(body):
        piece = piece[:-1] + '\u2026'
    return head + piece


def find(svc, query, branch, typ, requirement_ref, limit):
    Denied = _denied()
    svc.scope()
    svc.ready()
    if query is not None and type(query) is not str:
        raise Denied('INVALID_FIELD', field='query')
    if typ is not None and (type(typ) is not str or typ not in TYPES):
        raise Denied('UNKNOWN_TYPE', field='type')
    if requirement_ref is not None and type(requirement_ref) is not str:
        raise Denied('INVALID_FIELD', field='requirement_ref')
    if type(limit) is not int or not 1 <= limit <= 200:
        raise Denied('INVALID_FIELD', field='limit', hint="'limit' must be an integer 1..200 (default 20).")
    if branch is not None:
        if type(branch) is not str or not branch:
            raise Denied('INVALID_FIELD', field='branch')
        svc.scope(branch)
    branches = [branch] if branch else sorted(svc.context.branches)
    needle = query.casefold() if query else ''
    matches, total = [], 0
    with svc.store.read() as c:
        stamp = svc.integrity_gate(c)
        archived = _archived(c)
        info = _lineage(_children(c))
        ph = ','.join('?' * len(branches)) or "''"
        sql = ('SELECT cl.id, cl.content_type, cl.raw, cl.origin_branch, cl.origin_version, cl.payload, t.revision, '
               '%s AS lvl, rv.payload AS rvp FROM claims cl JOIN transactions t ON t.id=cl.tx '
               'LEFT JOIN claim_snapshots s ON s.claim_id=cl.id LEFT JOIN reviews rv ON rv.id=s.review_id '
               'WHERE t.branch IN (%s) ORDER BY cl.rowid DESC' % (_level_expr(c), ph))
        for row in c.execute(sql, branches):
            if typ and row['content_type'] != typ:
                continue
            item = json.loads(row['payload'])
            if requirement_ref and requirement_ref not in item.get('requirement_refs', []):
                continue
            body = bytes(row['raw']).decode('utf-8', 'replace')
            if needle and needle not in body.casefold() and not any(needle in s.casefold() for s in _strings(item.get('metadata', {}))):
                continue
            total += 1
            if len(matches) < limit:
                record_id, version = info(row['id'])
                matches.append({'claim_id': row['id'], 'branch': row['origin_branch'], 'type': row['content_type'],
                                'preview': _preview(body, query), 'origin_version': row['origin_version'],
                                'review_level': _level(row['lvl'], row['rvp']), 'is_current': row['id'] not in archived,
                                'record_id': record_id, 'version': version, 'revision': row['revision']})
    from . import public_dto
    return {'status': 'FOUND', 'simulated': True, 'matches': matches, 'total': total, 'truncated': total > len(matches),
            'read_snapshot': public_dto.read_snapshot(stamp, branches)}


# --------------------------------------------------------------------- start --
def start(svc, request, goal, branches, adopt):
    from .admission import IntegrityFailure, verify_chain
    Denied = _denied()
    _lite_only(svc)
    if not svc.context.simulation:
        raise Denied('OMH_BINDING_UNVERIFIED')
    if request is None:
        raise Denied('REQUEST_REQUIRED', field='request')
    req_raw = _text_bytes(request, 'request')
    goal_raw = None
    if goal is not None:
        if type(goal) is not str or not goal.strip():
            raise Denied('INVALID_FIELD', field='goal', hint="'goal' is optional; when given it must be a non-empty string (your one-line formulation).")
        goal_raw = _text_bytes(goal, 'goal')
    if branches is None:
        branches = ['main']
    if (type(branches) is not list or not branches or len(branches) > MAX_BRANCHES
            or any(type(b) is not str or not BRANCH_RE.match(b) for b in branches)):
        raise Denied('INVALID_FIELD', field='branches',
                     hint="'branches' must be an array of 1..%d codes of [A-Za-z0-9_-]{1,32}, e.g. [\"main\", \"alt\"]." % MAX_BRANCHES)
    branches = list(dict.fromkeys(branches))
    if type(adopt) is not bool:
        raise Denied('INVALID_FIELD', field='adopt')
    main = branches[0]

    state, existing, root, foreign = 'missing', set(), None, None
    if svc.store.path.exists():
        with svc.store.read() as c:
            state = svc.binding_state(c)
            if state in ('own', 'foreign'):
                try:
                    root = c.execute('SELECT * FROM project_root WHERE id=1').fetchone()
                except sqlite3.OperationalError:
                    root = None
            if state == 'own':
                existing = {r[0] for r in c.execute('SELECT branch FROM branch_heads')}
            if state == 'foreign':
                foreign = c.execute('SELECT work_ref FROM binding ORDER BY id LIMIT 1').fetchone()[0]
    adopt_info = None
    if state == 'foreign':
        if not adopt:
            raise Denied('SCOPE_DENIED')
        with svc.store.read() as c:
            chain = verify_chain(c)
        if chain['status'] != 'CHAIN_OK':
            raise IntegrityFailure(dict(status='CHAIN_BROKEN', blockers=['EVENT_CHAIN_BROKEN']))
        adopt_info = {'source_work': foreign, 'chain_hash': chain['head_hash'] if chain['events'] else '0' * 64, 'at': _now()}
    if root is not None:
        if root['request_sha256'] != raw_hash(req_raw):
            raise Denied('ROOT_CONFLICT', field='request')
        if goal_raw is not None and root['goal_sha256'] != raw_hash(goal_raw):
            raise Denied('ROOT_CONFLICT', field='goal')
    try:
        svc.store.initialize(svc.context.work, svc.policy, branches=tuple(branches), declare=tuple(branches), adopt=adopt_info)
    except ValueError:
        raise Denied('SCOPE_DENIED') from None
    svc.lite_sync()
    created = root is None
    if created:
        req_item = build_item('quote', request, req_raw, main, {'source_ref': ROOT_REQUEST_REF}, [], 'root request (verbatim, immutable)', 'root-request')
        req = _write_claim(svc, main, req_item, DEFAULT_ORIGIN_VERSION, 'root request (verbatim, immutable)', 'root-request')
        if 'claim_id' not in req:
            return req
        goal_id = None
        if goal_raw is not None:
            goal_item = build_item('text', goal, goal_raw, main, {'attribution': 'agent'}, [], 'agent goal (goal_confirmed=false until the customer confirms)', 'root-goal')
            g = _write_claim(svc, main, goal_item, DEFAULT_ORIGIN_VERSION, 'agent goal (goal_confirmed=false)', 'root-goal')
            if 'claim_id' not in g:
                return g
            goal_id = g['claim_id']
        with svc.store.transaction() as c:
            if c.execute('SELECT 1 FROM project_root WHERE id=1').fetchone() is None:
                c.execute('INSERT INTO project_root(id,request_claim_id,goal_claim_id,goal_confirmed,request_sha256,goal_sha256,branch,created_at) VALUES(1,?,?,0,?,?,?,?)',
                          (req['claim_id'], goal_id, raw_hash(req_raw), raw_hash(goal_raw) if goal_raw is not None else None, main, _now()))
        root_info = {'request_claim_id': req['claim_id'], 'goal_claim_id': goal_id, 'goal_confirmed': False}
    else:
        root_info = {'request_claim_id': root['request_claim_id'], 'goal_claim_id': root['goal_claim_id'],
                     'goal_confirmed': bool(root['goal_confirmed'])}
    with svc.store.read() as c:
        all_branches = sorted(r[0] for r in c.execute('SELECT branch FROM branch_heads'))
    added = [b for b in branches if b not in existing] if state == 'own' else []
    use = main if main in all_branches else all_branches[0]
    steps = [
        {'tool': 'dom_claim', 'arguments': {'branch': use, 'type': 'text', 'text': '<one statement or finding, verbatim>'},
         'why': 'record the first claim; dom_describe shows an example for every type'},
        {'tool': 'dom_find', 'arguments': {'branch': use}, 'why': 'list the latest claims of the branch (the root claims are there)'},
    ]
    return {'status': 'STARTED' if created else 'ALREADY_STARTED', 'simulated': True, 'profile': 'lite',
            'work_ref': svc.context.work, 'branches': all_branches, 'main_branch': use,
            'adopted': state == 'foreign' or _was_adopted(svc), 'branches_added': added, 'root': root_info, 'next_steps': steps}


def _was_adopted(svc):
    with svc.store.read() as c:
        try:
            return c.execute('SELECT 1 FROM adoptions WHERE new_work_ref=?', (svc.context.work,)).fetchone() is not None
        except sqlite3.OperationalError:
            return False


# ------------------------------------------------------------ tool documents --
def _arg(type_name, required, text):
    return {'type': type_name, 'required': required, 'description': text}


_TYPE_DOC = ', '.join(TYPES)

TOOL_DOCS = {
    'dom_describe': {
        'summary': 'Describe this server and how to use it: profile (lite/strict), the simulated flag, every tool with its arguments, the 7 claim types with a valid example call each, the write->find->update cycle, what review_level and the two readiness numbers mean. Read-only; takes no arguments. Call it first.',
        'arguments': {},
        'returns': 'status DESCRIBED, state (NOT_STARTED|READY|FOREIGN_BASE), tools, claim_types, cycle, review_level, readiness, limits, next_steps.',
        'example': {},
    },
    'dom_start': {
        'summary': 'Open (or create) the project database in this server directory. Computes work/task/policy itself, creates the branches, and records the customer request verbatim as the immutable root claim (plus your optional one-line goal, marked goal_confirmed=false until the customer confirms). Idempotent: repeating it with the same arguments changes nothing; a different request is refused (ROOT_CONFLICT) and the root is not overwritten.',
        'arguments': {
            'request': _arg('string', True, 'The customer request, verbatim. REQUIRED: there is no empty baseline.'),
            'goal': _arg('string', False, 'Your own one-line formulation of the goal. Stored as a separate claim, goal_confirmed=false.'),
            'branches': _arg('array of strings', False, 'Branch codes to declare, each [A-Za-z0-9_-]{1,32}. Default ["main"]. Repeat the call with more codes to add branches.'),
            'adopt': _arg('boolean', False, 'true only if another call was refused with SCOPE_DENIED because the database in this directory is bound to another work and you are sure it is your own project. Records an append-only adoption (source work, chain hash).'),
        },
        'returns': 'status STARTED|ALREADY_STARTED, work_ref, branches, main_branch, root{request_claim_id, goal_claim_id, goal_confirmed}, next_steps (the exact next call).',
        'example': {'request': 'Compare method X and Y for the report', 'goal': 'Collect evidence on X vs Y', 'branches': ['main', 'alt']},
    },
    'dom_claim': {
        'summary': 'Record one claim in a single call. The server builds the envelope (base64 body, hashes, metadata with sensible defaults, idempotency key), submits it, reviews it as the local owner (review_level=self) and admits it through the normal transaction. The text is stored byte-for-byte and never edited; to change it later use dom_update. Types: ' + _TYPE_DOC + '.',
        'arguments': {
            'branch': _arg('string', True, 'A declared branch code (dom_describe lists them).'),
            'type': _arg('string', True, 'One of: ' + _TYPE_DOC + '.'),
            'text': _arg('string', True, 'The claim body, non-empty, at most 1 MiB UTF-8. Stored exactly as given.'),
            'requirement_refs': _arg('array of strings', False, 'Requirement ids this claim supports, e.g. ["R1"]. Used for coverage in dom_trace.'),
            'reason': _arg('string', False, 'Why this claim is recorded (default "lite dom_claim").'),
            'origin_version': _arg('string', False, 'Version marker of the source/artifact (default "lite-v1").'),
            'source_ref': _arg('string', False, 'quote: where the quote comes from (url, file, person).'),
            'locator': _arg('string', False, 'quote/code: position in the source.'),
            'source_snapshot_digest': _arg('string', False, 'quote: sha256 of the source snapshot (default: hash of the quote).'),
            'attribution': _arg('string', False, 'decision/concept/text: who decided or said it (default "agent").'),
            'rationale': _arg('string', False, 'decision: why.'),
            'assumptions': _arg('array', False, 'decision/formula/concept/text: assumptions.'),
            'alternatives': _arg('array', False, 'decision: alternatives considered.'),
            'expression': _arg('string', False, 'formula: the expression (default: text).'),
            'notation': _arg('object', False, 'formula: symbol -> meaning.'),
            'units': _arg('object', False, 'formula/data: symbol -> unit.'),
            'derivation_refs': _arg('array', False, 'formula: where it was derived.'),
            'repository_ref': _arg('string', False, 'code: repository id.'),
            'relative_path': _arg('string', False, 'code: relative path (no leading slash, no "..").'),
            'language': _arg('string', False, 'code: language.'),
            'snapshot_digest': _arg('string', False, 'code: sha256 of the file snapshot.'),
            'artifact_ref': _arg('string', False, 'data: dataset/file id.'),
            'artifact_digest': _arg('string', False, 'data: sha256 of the artifact.'),
            'method': _arg('string', False, 'data: how the data was obtained.'),
            'columns': _arg('object', False, 'data: column -> type.'),
            'provenance': _arg('string', False, 'data: origin of the data.'),
            'definition': _arg('string', False, 'concept: definition (default: text).'),
            'scope': _arg('string', False, 'concept: scope of the definition.'),
            'links': _arg('array', False, 'concept: related references.'),
            'classification': _arg('string', False, 'text: "factual" (needs evidence) or "interpretation" (default when no evidence).'),
            'evidence': _arg('array', False, 'text: [{"ref": "...", "locator": "..."}]; makes the text factual.'),
        },
        'returns': 'status CLAIM_ADMITTED|ALREADY_RECORDED, claim_id, record_id, version, revision, review_level ("self"), raw_sha256, next_steps.',
        'example': {'branch': 'main', 'type': 'decision', 'text': 'Use method X for the main run.', 'rationale': 'cheaper and already validated', 'requirement_refs': ['R1']},
    },
    'dom_update': {
        'summary': 'Replace a claim by a new version. The old version is never edited or deleted: it stays in history with is_current=false and the new one supersedes it (replacement event). Only the current version can be updated.',
        'arguments': {
            'claim_id': _arg('string', True, 'The claim to replace (claim_id from dom_claim / dom_find).'),
            'text': _arg('string', True, 'The complete new text (not a diff).'),
            'reason': _arg('string', True, 'Why it changes; recorded in the event chain.'),
        },
        'returns': 'status CLAIM_UPDATED, new_claim_id, supersedes, record_id, version, revision, review_level, next_steps.',
        'example': {'claim_id': '<claim_id from dom_claim>', 'text': 'Use method Y for the main run.', 'reason': 'X failed validation on 2026-11-09'},
    },
    'dom_find': {
        'summary': 'Read-only search over claim bodies (case-insensitive substring of the UTF-8 text) and metadata values. Without a query it returns the latest claims, newest first. Includes older versions with is_current=false.',
        'arguments': {
            'query': _arg('string', False, 'Substring to look for (case-insensitive).'),
            'branch': _arg('string', False, 'Only this branch.'),
            'type': _arg('string', False, 'Only this claim type.'),
            'requirement_ref': _arg('string', False, 'Only claims supporting this requirement id.'),
            'limit': _arg('integer', False, 'Max matches, 1..200 (default 20).'),
        },
        'returns': 'status FOUND, matches[{claim_id, branch, type, preview<=200 chars, origin_version, review_level, is_current, record_id, version, revision}], total, truncated.',
        'example': {'query': 'method X', 'branch': 'main', 'limit': 10},
    },
    'dom_resume': {
        'summary': 'Everything about one branch in one read-only call: claims (snapshot), trace/readiness, outbox status and the pending list. Use it to re-orient after a pause or a REVISION_CONFLICT.',
        'arguments': {
            'branch': _arg('string', True, 'A declared branch code.'),
            'limit': _arg('integer', False, 'Pending page size 1..500 (default 50).'),
            'after': _arg('string', False, 'Keyset cursor "branch:id" from a previous page.'),
        },
        'returns': 'status RESUMED, snapshot, trace, sync, pending, readiness{admitted_total, admitted_independent, pending, rejected, stale}.',
        'example': {'branch': 'main'},
    },
    'dom_query': {
        'summary': 'Read-only snapshot of one branch at its head or at an exact earlier revision: all claims (with archived flag), event history, conflicts.',
        'arguments': {
            'branch': _arg('string', True, 'A declared branch code.'),
            'revision': _arg('integer', False, 'Historical revision >= 0 (default: head).'),
        },
        'returns': 'status SNAPSHOT, branch, revision, claims, history.',
        'example': {'branch': 'main'},
    },
    'dom_trace': {
        'summary': 'Coverage / stale / conflict / pending trace. In the lite profile readiness is {admitted_total, admitted_independent, pending, rejected, stale}: admitted_total counts every current admitted claim, admitted_independent only those an independent reviewer admitted (lite claims are review_level=self, so it is 0). Never closes the owner task.',
        'arguments': {'branch': _arg('string', False, 'One branch; omit for all branches.')},
        'returns': 'status, readiness{...}, ready_for_owner_review, residual (per requirement_ref), blockers.',
        'example': {},
    },
    'dom_export': {
        'summary': 'Write a deterministic YAML export of one branch (head or exact revision) to a server-fixed path inside the run directory.',
        'arguments': {
            'branch': _arg('string', True, 'A declared branch code.'),
            'revision': _arg('integer', False, 'Historical revision >= 0 (default: head).'),
        },
        'returns': 'status EXPORTED, handle, sha256, revision.',
        'example': {'branch': 'main'},
    },
    'dom_sync_status': {
        'summary': 'Read-only outbox status per intent (pending / ambiguous / ack) for one branch.',
        'arguments': {'branch': _arg('string', True, 'A declared branch code.')},
        'returns': 'status SYNC_STATUS, intents[].',
        'example': {'branch': 'main'},
    },
    'dom_sync': {
        'summary': 'Deliver the outbox of one branch (YAML export + simulated OMH attach with read-back).',
        'arguments': {'branch': _arg('string', True, 'A declared branch code.')},
        'returns': 'status SYNCED|SYNC_PENDING.',
        'example': {'branch': 'main'},
    },
}

LITE_TOOL_NAMES = tuple(TOOL_DOCS)


def compose_description(name):
    doc = TOOL_DOCS[name]
    args = '; '.join('%s (%s, %s) - %s' % (a, d['type'], 'REQUIRED' if d['required'] else 'optional', d['description'])
                     for a, d in doc['arguments'].items()) or 'none'
    return '%s Arguments: %s. Returns: %s Example: %s(%s)' % (doc['summary'], args, doc['returns'], name, json.dumps(doc['example'], ensure_ascii=False))


_JSON_TYPES = {'string': 'string', 'integer': 'integer', 'boolean': 'boolean', 'array of strings': 'array', 'array': 'array', 'object': 'object'}


def input_schema(name):
    doc = TOOL_DOCS[name]
    props = {}
    for arg, d in doc['arguments'].items():
        prop = {'type': _JSON_TYPES[d['type']], 'description': d['description']}
        if d['type'] == 'array of strings':
            prop['items'] = {'type': 'string'}
        if arg == 'type':
            prop['enum'] = list(TYPES)
        if arg == 'limit':
            prop.update(minimum=1, maximum=500 if name == 'dom_resume' else 200)
        if arg == 'revision':
            prop['minimum'] = 0
        props[arg] = prop
    return {'type': 'object', 'additionalProperties': False, 'properties': props,
            'required': [a for a, d in doc['arguments'].items() if d['required']]}


_CLAIM_EXAMPLES = {
    'quote': {'branch': 'main', 'type': 'quote', 'text': 'The measured value was 4.2 mol/L.', 'source_ref': 'https://example.org/report.pdf', 'locator': 'p.3'},
    'decision': {'branch': 'main', 'type': 'decision', 'text': 'Use method X for the main run.', 'rationale': 'cheaper and already validated', 'attribution': 'team lead'},
    'formula': {'branch': 'main', 'type': 'formula', 'text': 'E = m * c**2', 'notation': {'E': 'energy', 'm': 'mass', 'c': 'speed of light'}, 'units': {'E': 'J', 'm': 'kg', 'c': 'm/s'}},
    'code': {'branch': 'main', 'type': 'code', 'text': 'def add(a, b):\n    return a + b', 'relative_path': 'src/add.py', 'language': 'python', 'repository_ref': 'local:project'},
    'data': {'branch': 'main', 'type': 'data', 'text': 'x,y\n1,2\n3,4', 'artifact_ref': 'file:results.csv', 'units': {'x': 'mol/L', 'y': 's'}, 'method': 'measured'},
    'concept': {'branch': 'main', 'type': 'concept', 'text': 'Baseline: the first accepted version of the plan.', 'scope': 'this project'},
    'text': {'branch': 'main', 'type': 'text', 'text': 'Method X is probably faster on small inputs.'},
}
_CLAIM_WHEN = {
    'quote': 'a verbatim passage from a source; the text is the quote itself',
    'decision': 'a choice that was made, with rationale',
    'formula': 'an equation or expression; give units for the symbols if you know them',
    'code': 'a code fragment or file content',
    'data': 'a table or measurement; give units if you know them',
    'concept': 'a definition of a term used in the project',
    'text': 'anything else; add evidence=[{"ref":..,"locator":..}] to make it a factual statement, otherwise it is an interpretation',
}


def claim_type_examples():
    return {t: {'use_for': _CLAIM_WHEN[t], 'example_call': {'tool': 'dom_claim', 'arguments': _CLAIM_EXAMPLES[t]}} for t in TYPES}


def describe(svc):
    state, work, branches = 'NOT_STARTED', None, []
    if svc.store.path.exists():
        with svc.store.read() as c:
            st = svc.binding_state(c)
            if st == 'own':
                state, work = 'READY', svc.context.work
                branches = sorted(r[0] for r in c.execute('SELECT branch FROM branch_heads'))
            elif st == 'foreign':
                state = 'FOREIGN_BASE'
    if svc.lite:
        profile = 'lite'
        summary = ('Lite (local_single_owner) profile of a SIMULATED DOM server: the local SQLite database is real and append-only, '
                   'OMH/Git targets are simulated. One owner writes; every admitted claim is labelled review_level=self.')
        tools = [{'name': n, 'summary': TOOL_DOCS[n]['summary'], 'arguments': TOOL_DOCS[n]['arguments'],
                  'returns': TOOL_DOCS[n]['returns'], 'example': {'tool': n, 'arguments': TOOL_DOCS[n]['example']}} for n in TOOL_DOCS]
    else:
        profile = 'strict'
        summary = 'Strict profile.'
        tools = []
    cycle = [
        '1. dom_describe({}) - read this once.',
        '2. dom_start({"request": "<customer request verbatim>"}) - opens the project, records the immutable root request.',
        '3. dom_claim({"branch": "main", "type": "decision", "text": "..."}) - one call per claim; repeat for each fact, quote, decision.',
        '4. dom_find({"query": "..."}) - look a claim up before you write a similar one.',
        '5. dom_update({"claim_id": "...", "text": "<full new text>", "reason": "..."}) - changes a claim by a NEW version; the old one stays in history.',
        '6. dom_trace({}) - readiness; dom_resume({"branch": "main"}) - re-orient after a pause or after REVISION_CONFLICT.',
    ]
    next_steps = ([{'tool': 'dom_start', 'arguments': {'request': '<customer request verbatim>', 'branches': ['main']}, 'why': 'no project is open in this directory yet'}]
                  if state == 'NOT_STARTED' else
                  [{'tool': 'dom_start', 'arguments': {'request': '<customer request>', 'adopt': True}, 'why': 'the database here is bound to another work; adopt it only if it is yours'}]
                  if state == 'FOREIGN_BASE' else
                  [{'tool': 'dom_find', 'arguments': {}, 'why': 'see the latest claims'},
                   {'tool': 'dom_claim', 'arguments': {'branch': branches[0] if branches else 'main', 'type': 'text', 'text': '<statement>'}, 'why': 'add a claim'}])
    return {
        'status': 'DESCRIBED', 'profile': profile, 'simulated': svc.context.simulation, 'state': state, 'summary': summary,
        'work_ref': work, 'branches': branches, 'tools': tools, 'claim_types': claim_type_examples() if svc.lite else {},
        'cycle': cycle,
        'review_level': {
            'self': 'admitted by the same local owner who wrote it (lite profile). Honest label: nobody independent has looked at it.',
            'independent': 'admitted after review by a different identity root (strict profile).',
            'null': 'row written before the label existed; it is never counted as independent.'},
        'readiness': {
            'admitted_total': 'current (not replaced) admitted claims, whoever admitted them',
            'admitted_independent': 'of those, admitted after an independent review; 0 in the lite profile - do not read admitted_total as independently checked',
            'pending': 'submitted candidates not yet admitted or rejected',
            'rejected': 'candidates whose latest review was not an approval',
            'stale': 'admitted claims whose dependency branch moved on'},
        'limits': [
            'Simulated server: OMH delivery and Git are simulated; the SQLite database in this directory is real.',
            'Claims and quotes are immutable; there is no delete. dom_update adds a version.',
            'goal_confirmed stays false until the customer confirms; there is no confirm tool in this slice.',
            'profile, review_level, principal and work are fixed at server launch and cannot be passed as arguments.',
            'Branch codes are [A-Za-z0-9_-]{1,32}; declare them with dom_start.'],
        'next_steps': next_steps,
    }
