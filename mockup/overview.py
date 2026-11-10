"""Read-only overview of a DOM run directory for the Hermes Desktop "dom" panel.

``python -m mockup.overview --directory <run dir inside runtime/> [--branch X] [--limit N]``
prints one JSON document (schema ``dom_overview/v1``) on stdout.

Contract
- READ ONLY: SQLite is opened ``file:...?mode=ro`` (uri) plus ``PRAGMA query_only=ON``;
  nothing is created, no WAL/SHM/journal is written by this module.
- The run directory must resolve (symlinks, ``..``) to a place inside ``<project>/runtime``;
  so must the database file. A refusal is a typed record and never names the offending path.
- Never raises to the caller: every failure becomes a typed ``status`` record.
- A pending candidate is returned as metadata only (never its payload body).
- ``review_level`` is read only if the database really carries it (a ``review_level``
  column in claims / claim_snapshots / reviews, or a ``review_level`` key in the review
  payload); otherwise ``null``. It is never derived or guessed.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 'dom_overview/v1'
KNOWN_USER_VERSIONS = (2, 3)        # storage.SCHEMA_VERSION (3 since WR-ADD); kept literal: no import of product code
DEFAULT_LIMIT = 200
MAX_LIMIT = 1000
PREVIEW_CHARS = 160
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = PROJECT_ROOT / 'runtime'
DB_NAME = 'dom.sqlite3'


class _Refused(Exception):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def _record(status, **extra):
    out = {'schema': SCHEMA, 'status': status, 'generated_at': _now()}
    out.update(extra)
    return out


def _resolve_inside_runtime(path, runtime_root):
    try:
        resolved = Path(path).resolve()
        root = Path(runtime_root).resolve()
    except (OSError, ValueError, RuntimeError):
        raise _Refused()
    if resolved == root or not resolved.is_relative_to(root):
        raise _Refused()
    return resolved


def preview_text(raw, limit=PREVIEW_CHARS):
    """Safe short preview of a claim body: utf-8 text up to ``limit`` chars, else ``[binary N bytes]``."""
    if raw is None:
        return ''
    data = bytes(raw) if not isinstance(raw, str) else raw.encode('utf-8', 'replace')
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return '[binary %d bytes]' % len(data)
    if '\x00' in text:
        return '[binary %d bytes]' % len(data)
    text = ''.join(ch if (ch.isprintable() or ch == ' ') else ' ' for ch in text)
    text = ' '.join(text.split())
    if len(text) > limit:
        text = text[:limit - 1] + '\u2026'
    return text


def _open_ro(db_path):
    conn = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True, timeout=2, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA query_only=ON')
    return conn


def _tables(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _columns(conn, table):
    return {r[1] for r in conn.execute('PRAGMA table_info(%s)' % table)}


def _json(blob):
    try:
        value = json.loads(bytes(blob).decode('utf-8') if not isinstance(blob, str) else blob)
        return value if isinstance(value, dict) else None
    except (ValueError, TypeError, UnicodeDecodeError):
        return None


def _age(created_at, now):
    if not created_at:
        return None
    try:
        return max(0, int((now - datetime.fromisoformat(created_at)).total_seconds()))
    except (ValueError, TypeError):
        return None


def _review_level_source(conn, tables):
    for table in ('claims', 'claim_snapshots', 'reviews'):
        if table in tables and 'review_level' in _columns(conn, table):
            return table
    return None


def _section(warnings, name, func, default):
    try:
        return func()
    except sqlite3.Error as exc:
        warnings.append('%s: %s' % (name, type(exc).__name__))
        return default


def _collect(conn, branch, limit, warnings):
    now = datetime.now(timezone.utc)
    tables = _tables(conn)
    user_version = conn.execute('PRAGMA user_version').fetchone()[0]
    if user_version not in KNOWN_USER_VERSIONS:
        warnings.append('unknown user_version %s (known: %s); partial best-effort read'
                        % (user_version, ','.join(map(str, KNOWN_USER_VERSIONS))))
    out = {'schema_version': SCHEMA, 'user_version': user_version}
    if not tables:
        return None, 'EMPTY_DATABASE', out

    # ---- binding ------------------------------------------------------------
    work_ref, policy = None, None
    if 'binding' in tables:
        def read_binding():
            row = conn.execute('SELECT * FROM binding ORDER BY id LIMIT 1').fetchone()
            return (row['work_ref'], row['policy']) if row else (None, None)
        work_ref, policy = _section(warnings, 'binding', read_binding, (None, None))
    else:
        warnings.append('missing table: binding')
    out['binding'] = {'work_ref': work_ref,
                      'policy_prefix': (policy or '')[:12] or None,
                      'user_version': user_version}

    # ---- transactions: branch -> last time, simulated flag --------------------------
    tx_branch = {}
    sim_seen = []
    if 'transactions' in tables:
        def read_tx():
            for r in conn.execute('SELECT id, branch, receipt FROM transactions'):
                tx_branch[r['id']] = r['branch']
                rec = _json(r['receipt'])
                if rec is not None and isinstance(rec.get('simulated'), bool):
                    sim_seen.append(rec['simulated'])
        _section(warnings, 'transactions', read_tx, None)
    else:
        warnings.append('missing table: transactions')
    last_tx_at = {}
    if 'events' in tables:
        def read_ev_time():
            for r in conn.execute('SELECT e.tx AS tx, e.payload AS payload FROM events e '
                                  'WHERE e.seq IN (SELECT MIN(seq) FROM events GROUP BY tx)'):
                p = _json(r['payload'])
                t = p.get('server_time') if p else None
                b = tx_branch.get(r['tx'])
                if isinstance(t, str) and b is not None and (b not in last_tx_at or t > last_tx_at[b]):
                    last_tx_at[b] = t
        _section(warnings, 'events', read_ev_time, None)
    out['simulated'] = (all(sim_seen) if sim_seen else True)
    out['simulated_source'] = 'transaction receipts' if sim_seen else 'default (no receipt evidence)'

    # ---- branches ---------------------------------------------------------------
    heads = []
    if 'branch_heads' in tables:
        heads = _section(warnings, 'branch_heads',
                         lambda: [(r['branch'], r['revision']) for r in
                                  conn.execute('SELECT branch, revision FROM branch_heads ORDER BY branch')], [])
    else:
        warnings.append('missing table: branch_heads')
    if branch is not None:
        if branch not in {b for b, _ in heads}:
            warnings.append('unknown branch requested')
        heads = [(b, r) for b, r in heads if b == branch]

    # ---- claims -----------------------------------------------------------------
    level_table = _review_level_source(conn, tables)
    claim_total, claims = {}, []
    if 'claims' in tables:
        def read_claims():
            cols = _columns(conn, 'claims')
            for b, _ in heads:
                if 'transactions' not in tables:
                    claim_total[b] = None
                    continue
                claim_total[b] = conn.execute(
                    'SELECT COUNT(*) FROM claims c JOIN transactions t ON t.id=c.tx WHERE t.branch=?',
                    (b,)).fetchone()[0]
                level_expr = 'NULL AS review_level'
                join = ''
                if level_table == 'claims':
                    level_expr = 'c.review_level AS review_level'
                elif level_table == 'claim_snapshots':
                    join = 'LEFT JOIN claim_snapshots s ON s.claim_id=c.id'
                    level_expr = 's.review_level AS review_level'
                elif level_table == 'reviews':
                    join = ('LEFT JOIN claim_snapshots s ON s.claim_id=c.id '
                            'LEFT JOIN reviews rv ON rv.id=s.review_id')
                    level_expr = 'rv.review_level AS review_level'
                sql = ('SELECT c.id, c.origin_branch, c.origin_version, c.content_type, c.raw, c.raw_sha256, '
                       'c.tx, %s FROM claims c JOIN transactions t ON t.id=c.tx %s '
                       'WHERE t.branch=? ORDER BY c.rowid LIMIT ?') % (level_expr, join)
                for r in conn.execute(sql, (b, limit)):
                    level = r['review_level']
                    claims.append({
                        'claim_id': r['id'], 'branch': b, 'origin_branch': r['origin_branch'],
                        'origin_version': r['origin_version'], 'content_type': r['content_type'],
                        'preview': preview_text(r['raw']), 'raw_sha256': r['raw_sha256'],
                        'admitted_tx': r['tx'],
                        'review_level': level if isinstance(level, str) else None,
                    })
        _section(warnings, 'claims', read_claims, None)
    else:
        warnings.append('missing table: claims')

    # ---- review_level counts / project root / adoptions (WR-ADD; additive fields) ------
    review_levels = {}
    if level_table is not None and 'claims' in tables and 'transactions' in tables:
        def read_levels():
            join, expr = '', 'NULL'
            if level_table == 'claims':
                expr = 'c.review_level'
            elif level_table == 'claim_snapshots':
                join, expr = 'LEFT JOIN claim_snapshots s ON s.claim_id=c.id', 's.review_level'
            else:
                join, expr = ('LEFT JOIN claim_snapshots s ON s.claim_id=c.id LEFT JOIN reviews rv ON rv.id=s.review_id'), 'rv.review_level'
            for b, _ in heads:
                counts = {}
                for r in conn.execute('SELECT %s AS lvl, COUNT(*) AS n FROM claims c JOIN transactions t ON t.id=c.tx %s '
                                      'WHERE t.branch=? GROUP BY lvl' % (expr, join), (b,)):
                    counts[r['lvl'] if isinstance(r['lvl'], str) else 'null'] = r['n']
                review_levels[b] = counts
        _section(warnings, 'review_levels', read_levels, None)
    project_root = None
    if 'project_root' in tables:
        def read_root():
            row = conn.execute('SELECT request_claim_id, goal_claim_id, goal_confirmed, branch, created_at FROM project_root WHERE id=1').fetchone()
            return ({'request_claim_id': row['request_claim_id'], 'goal_claim_id': row['goal_claim_id'],
                     'goal_confirmed': bool(row['goal_confirmed']), 'branch': row['branch'], 'created_at': row['created_at']}
                    if row else None)
        project_root = _section(warnings, 'project_root', read_root, None)
    adoptions = []
    if 'adoptions' in tables:
        def read_adoptions():
            return [{'source_work_ref': r['source_work_ref'], 'chain_hash': r['chain_hash'], 'adopted_at': r['adopted_at'],
                     'user_version_at': r['user_version_at']}
                    for r in conn.execute('SELECT source_work_ref, chain_hash, adopted_at, user_version_at FROM adoptions ORDER BY seq')]
        adoptions = _section(warnings, 'adoptions', read_adoptions, []) or []

    # ---- pending / rejected -------------------------------------------------------
    pending_total = {}
    rejected_total = {}
    pending = []
    if 'candidates' in tables:
        def read_pending():
            admitted_by_idem = set()
            if 'idempotency' in tables and {'operation', 'candidate_id', 'external_work_ref'} <= _columns(conn, 'idempotency'):
                admitted_by_idem = {r[0] for r in conn.execute(
                    "SELECT candidate_id FROM idempotency WHERE external_work_ref=? AND operation LIKE 'admit:%' "
                    'AND candidate_id IS NOT NULL', (work_ref,))}
            admitted_by_claims = set()
            if 'claims' in tables:
                admitted_by_claims = {r[0] for r in conn.execute('SELECT DISTINCT candidate FROM claims')}
            last_review = {}
            if 'reviews' in tables:
                for r in conn.execute('SELECT id, candidate, payload FROM reviews ORDER BY rowid'):
                    last_review[r['candidate']] = (r['id'], _json(r['payload']))
            cand_cols = _columns(conn, 'candidates')
            created_expr = 'created_at' if 'created_at' in cand_cols else 'NULL AS created_at'
            wanted = {b for b, _ in heads}
            for r in conn.execute('SELECT id, digest, payload, author, root, branch, %s FROM candidates '
                                  'ORDER BY branch, rowid' % created_expr):
                if r['branch'] not in wanted or r['id'] in admitted_by_claims or r['id'] in admitted_by_idem:
                    continue
                review = last_review.get(r['id'])
                decision = review[1].get('decision') if review and review[1] else None
                rejected = review is not None and decision is not None and decision != 'approve'
                if rejected:
                    rejected_total[r['branch']] = rejected_total.get(r['branch'], 0) + 1
                    continue
                pending_total[r['branch']] = pending_total.get(r['branch'], 0) + 1
                if len(pending) >= limit:
                    continue
                body = _json(r['payload']) or {}
                deps = body.get('dependencies')
                pending.append({
                    'candidate_id': r['id'], 'branch': r['branch'],
                    'state': 'REVIEWED' if review is not None else 'AWAITING_REVIEW',
                    'operation': body.get('operation') if isinstance(body.get('operation'), str) else None,
                    'author': r['author'], 'root': r['root'],
                    'dependencies': {k: v for k, v in deps.items() if isinstance(v, int) and not isinstance(v, bool)}
                    if isinstance(deps, dict) else {},
                    'payload_length': len(bytes(r['payload'])),
                    'created_at': r['created_at'], 'age_seconds': _age(r['created_at'], now),
                    'review_id': review[0] if review else None,
                })
        _section(warnings, 'candidates', read_pending, None)
    else:
        warnings.append('missing table: candidates')

    # ---- delivery -----------------------------------------------------------------
    delivery = {}
    if 'outbox' in tables:
        def read_delivery():
            have_attempts = 'delivery_attempts' in tables
            have_acks = 'delivery_acks' in tables and 'delivery_observations' in tables
            if not (have_attempts and have_acks):
                warnings.append('delivery tables incomplete: counts are pending-only upper bounds')
            for b, _ in heads:
                counts = {'pending': 0, 'ambiguous': 0, 'ack': 0}
                for r in conn.execute('SELECT id FROM outbox WHERE branch=?', (b,)):
                    acked = have_acks and conn.execute(
                        'SELECT 1 FROM delivery_acks k JOIN delivery_observations o ON o.id=k.observed '
                        'WHERE k.intent=? AND o.matched=1 LIMIT 1', (r['id'],)).fetchone()
                    attempted = have_attempts and conn.execute(
                        'SELECT 1 FROM delivery_attempts WHERE intent=? LIMIT 1', (r['id'],)).fetchone()
                    counts['ack' if acked else 'ambiguous' if attempted else 'pending'] += 1
                delivery[b] = counts
        _section(warnings, 'delivery', read_delivery, None)
    else:
        warnings.append('missing table: outbox')

    out['branches'] = [{
        'branch': b, 'head_revision': rev,
        'claims_count': claim_total.get(b), 'claims_shown': sum(1 for c in claims if c['branch'] == b),
        'pending_count': pending_total.get(b, 0), 'rejected_count': rejected_total.get(b, 0),
        'last_tx_at': last_tx_at.get(b),
        'delivery': delivery.get(b),
        'review_levels': review_levels.get(b),
    } for b, rev in heads]
    out['claims'] = claims
    out['claims_limit'] = limit
    out['pending'] = pending
    out['pending_total'] = sum(pending_total.values())
    out['pending_shown'] = len(pending)
    out['rejected_count'] = sum(rejected_total.values())
    out['delivery'] = {'by_branch': delivery,
                       'total': {k: sum(v[k] for v in delivery.values()) for k in ('pending', 'ambiguous', 'ack')}}
    out['review_level_source'] = level_table
    out['project_root'] = project_root
    out['adoptions'] = adoptions
    return out, 'OK', out


def build_overview(directory, branch=None, limit=DEFAULT_LIMIT, runtime_root=RUNTIME_ROOT):
    """Return the overview record for ``directory``. Never raises."""
    try:
        if isinstance(limit, bool) or not isinstance(limit, int):
            limit = DEFAULT_LIMIT
        limit = max(1, min(int(limit), MAX_LIMIT))
        if branch is not None and (not isinstance(branch, str) or not branch or len(branch) > 64):
            return _record('INVALID_ARGUMENT', error='branch')
        try:
            run_dir = _resolve_inside_runtime(directory, runtime_root)
        except _Refused:
            return _record('DIRECTORY_REFUSED', error='directory must be inside the project runtime')
        db_path = run_dir / DB_NAME
        if not db_path.exists():
            return _record('NO_DATABASE')
        try:
            db_path = _resolve_inside_runtime(db_path, runtime_root)
        except _Refused:
            return _record('DIRECTORY_REFUSED', error='database must be inside the project runtime')
        if not db_path.is_file():
            return _record('NO_DATABASE')
        warnings = []
        conn = None
        try:
            conn = _open_ro(db_path)
            body, status, _ = _collect(conn, branch, limit, warnings)
        except sqlite3.Error as exc:
            return _record('READER_ERROR', error=type(exc).__name__, warnings=warnings)
        finally:
            if conn is not None:
                conn.close()
        try:
            rel = run_dir.relative_to(Path(runtime_root).resolve()).as_posix()
        except ValueError:
            rel = None
        record = _record(status, warnings=warnings, instance=rel)
        if body:
            body.pop('schema_version', None)
            record.update(body)
        record['schema_version'] = SCHEMA
        return record
    except Exception as exc:  # last resort: the panel gets a record, not a traceback
        return _record('READER_ERROR', error=type(exc).__name__)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='mockup.overview', description='Read-only DOM overview (JSON).')
    parser.add_argument('--directory', required=True)
    parser.add_argument('--branch', default=None)
    parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT)
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        result = _record('INVALID_ARGUMENT', error='usage')
    else:
        result = build_overview(args.directory, args.branch, args.limit)
    data = (json.dumps(result, ensure_ascii=False, sort_keys=True) + '\n').encode('utf-8')
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
