"""AC001 minor findings: uniform scope refusal, event chain, idempotency, columns.

F4 scope-before-trace, F5 hash-chain verification + insert guard, F6 work-scoped
idempotency key, F7 aggregated INVALID_TYPE, F8 claims columns vs AA002 contract.
"""
import json
import sqlite3

import pytest

from mockup.admission import IntegrityFailure, Service, verify_chain
from mockup.dom_contract import validate, raw_hash
from mockup.fixtures import package, item, amendment, WORK, POLICY
from test_projection_state import accepted


def database(tmp_path):
    return tmp_path / 'dom.sqlite3'


def test_trace_for_forbidden_principal_is_scope_denied(tmp_path):
    """F4: refusal has the same safe shape for every entry point."""
    accepted(tmp_path, package())
    foreign = Service(tmp_path, role='unknown-host')
    assert foreign.trace('master') == {'status': 'SCOPE_DENIED'}
    assert foreign.trace('AA') == {'status': 'SCOPE_DENIED'}
    assert foreign.query('AA') == {'status': 'SCOPE_DENIED'}
    # the legitimate scope still produces a real trace, not a blanket denial
    assert Service(tmp_path).trace('master')['status'] in ('TRACE', 'ready_for_owner_review')


def test_event_chain_is_verified_and_forgery_is_detected(tmp_path):
    """F5: recompute previous_hash/event_hash; a direct INSERT is caught.

    Public Trace exposes only the chain status (the internal head hash, event
    count and broken locators stay server-side).  The detailed locators are
    asserted through the internal gate that raises IntegrityFailure.
    """
    first = accepted(tmp_path, package())
    claim = first['claim_ids']['one']
    clean = Service(tmp_path).trace('AA')
    assert clean['chain'] == {'status': 'CHAIN_OK'}
    with Service(tmp_path).store.read() as c:
        verified = verify_chain(c)
    assert verified['status'] == 'CHAIN_OK'
    assert verified['events'] == 1

    with sqlite3.connect(database(tmp_path)) as raw:
        head = raw.execute('SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()[0]
        forged_payload = json.dumps({'value': {'value': {}}, 'actor': 'intruder'}, sort_keys=True)
        raw.execute('INSERT INTO events(id,tx,claim_ref,branch,revision,kind,payload,previous_hash,event_hash) '
                    "SELECT 'forged-event',tx,claim_ref,branch,revision,'archive',?,?,'" + 'f' * 64 + "' FROM events LIMIT 1",
                    (forged_payload, head))

    broken = Service(tmp_path).trace('AA')
    assert broken['status'] == 'CHAIN_BROKEN'
    assert 'EVENT_CHAIN_BROKEN' in broken['blockers']
    assert broken['ready_for_owner_review'] is False
    # Public Broken DTO must not leak internal chain/origin locators.
    assert 'origins' not in broken and 'read_snapshot' not in broken

    with Service(tmp_path).store.read() as c:
        with pytest.raises(IntegrityFailure) as raised:
            Service(tmp_path).integrity_gate(c)
    internal = raised.value.result
    assert internal['chain']['reason'] == 'EVENT_HASH_MISMATCH'
    assert internal['chain']['broken_event_id'] == 'forged-event'
    # the forged archive is what the projection saw, which is why the chain check matters
    assert claim in internal['origins']


def test_event_insert_must_extend_the_stored_chain(tmp_path):
    """F5: an out-of-chain INSERT is rejected by the append guard, not silently stored."""
    first = accepted(tmp_path, package())
    with Service(tmp_path).store.read() as c:
        tx = c.execute('SELECT tx FROM events LIMIT 1').fetchone()[0]
        with pytest.raises(sqlite3.IntegrityError, match='CHAIN_INTEGRITY'):
            c.execute('INSERT INTO events(id,tx,claim_ref,branch,revision,kind,payload,previous_hash,event_hash) '
                      "VALUES('detached','" + str(tx) + "',NULL,'AA',1,'archive','{}','" + '0' * 64 + "','" + 'a' * 64 + "')")
    assert Service(tmp_path).trace('AA')['chain']['status'] == 'CHAIN_OK'
    assert first['status'] == 'DEMO_ADMITTED'


def test_idempotency_is_scoped_to_external_work_ref(tmp_path):
    """F6: work (and the launch-grant digest) are part of the replay key."""
    accepted(tmp_path, package())
    with Service(tmp_path).store.read() as c:
        info = list(c.execute('PRAGMA table_info(idempotency)'))
        columns = {row[1] for row in info}
        assert {'external_work_ref', 'operation', 'key', 'digest', 'result'} <= columns
        primary_key = [row[1] for row in sorted(info, key=lambda r: r[5]) if row[5]]
        # WS-F02 extended the key with the launch grant digest; work stays in it.
        assert primary_key == ['external_work_ref', 'operation', 'key', 'scope_digest']
        rows = [row[0] for row in c.execute('SELECT DISTINCT external_work_ref FROM idempotency')]
        assert rows == [WORK]
        # the same operation/key under another work is a different intent...
        c.execute("INSERT INTO idempotency(external_work_ref,operation,key,scope_digest,digest,result) "
                  "VALUES('demo:other-work','admit:demo-reviewer','k1','scope-a','digest-a','result-a')")
        # ...while a repeat inside the same work and scope still collides
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO idempotency(external_work_ref,operation,key,scope_digest,digest,result) "
                      "VALUES('demo:other-work','admit:demo-reviewer','k1','scope-a','digest-b','result-b')")
        # the same key under this work's scope is a different intent, not a collision
        c.execute('INSERT INTO idempotency(external_work_ref,operation,key,scope_digest,digest,result) '
                  'VALUES(?,?,?,?,?,?)',
                  (WORK, 'admit:demo-reviewer', 'k1', 'scope-a', 'digest-c', 'result-c'))


def test_unknown_content_type_does_not_abort_error_aggregation():
    """F7: INVALID_TYPE for the item, then the shared-field checks still run."""
    body = item('ok')['body_b64']
    unknown_encoding = {'local_id': 'y1', 'content_type': 'not-a-type', 'body_b64': body, 'encoding': 'utf-16',
                        'media_type': 'text/plain', 'reason': 'r', 'metadata': {}, 'applicability': ['ZZ']}
    unknown_body = {'local_id': 'y2', 'content_type': 'not-a-type', 'body_b64': 'not-base64!', 'encoding': 'utf-8',
                    'media_type': 'text/plain', 'reason': 'r', 'metadata': {}, 'applicability': ['AA']}
    errors = validate({'items': [unknown_encoding, unknown_body]})
    found = {(e['local_id'], e['path'], e['code']) for e in errors}
    assert ('y1', 'content_type', 'INVALID_TYPE') in found
    assert ('y1', 'encoding', 'INVALID_ENCODING') in found
    assert ('y1', 'applicability', 'INVALID_BRANCH') in found
    assert ('y2', 'content_type', 'INVALID_TYPE') in found
    assert ('y2', 'body_b64', 'INVALID_ENCODING') in found
    assert not any(e['local_id'] is None for e in errors if e['path'].startswith('content_type'))


def test_claims_columns_match_storage_contract(tmp_path):
    """F8: content_type/encoding/media/source are real columns, not payload-only."""
    accepted(tmp_path, package(items=[item('q', typ='quote')]))
    with Service(tmp_path).store.read() as c:
        row = c.execute('SELECT content_type,encoding,media_type,source_ref,raw,raw_sha256 FROM claims').fetchone()
    assert row['content_type'] == 'quote'
    assert row['encoding'] == 'utf-8'
    assert row['media_type'] == 'text/plain'
    assert row['source_ref'] == 'https://example.invalid/raw?x=%20'
    assert row['raw_sha256'] == raw_hash(bytes(row['raw']))


def test_storage_invariants_are_explicit_not_assertions():
    """M4: PRAGMA/immutability invariants must survive ``python -O``."""
    import ast
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / 'mockup' / 'storage.py').read_text(encoding='utf8')
    assert [node.lineno for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assert)] == []
    for code in ('PRAGMA_FOREIGN_KEYS_NOT_ENFORCED', 'PRAGMA_SYNCHRONOUS_NOT_FULL', 'JOURNAL_MODE_NOT_DELETE'):
        assert code in source, code
