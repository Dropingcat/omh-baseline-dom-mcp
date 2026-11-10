"""Customer requirement: the branch marker on every claim must actually surface.

The marker is ``claims.origin_branch`` (with ``origin_version``).  It has to be
observable in the branch snapshot, in the exported YAML, in history/trace, and it
must be impossible to rewrite it through a ``property`` event or plain SQL.
"""
import json
import sqlite3

import pytest
import yaml

from mockup.admission import Service
from mockup.fixtures import WORK, POLICY, package, amendment


def init(directory, role='author'):
    service = Service(directory, role=role)
    assert service.init({'external_work_ref': WORK, 'policy_digest': POLICY})['status'] == 'INITIALIZED'
    return service


def accepted(directory, payload):
    author = init(directory)
    candidate = author.submit(json.dumps(payload))
    assert candidate['status'] == 'RECORDED_CANDIDATE', candidate
    reviewer = Service(directory, role='reviewer')
    review = reviewer.review(candidate['candidate_id'], candidate['intent_digest'])
    result = reviewer.admit(candidate['candidate_id'], review['review_id'], payload['idempotency_key'], candidate['intent_digest'])
    assert result['status'] == 'DEMO_ADMITTED', result
    return result


def test_origin_branch_in_snapshot_export_trace_and_history(tmp_path):
    first = accepted(tmp_path, package())
    claim = first['claim_ids']['one']
    # Share the AA-authored claim into AB: AB must keep the AA origin marker.
    accepted(tmp_path, amendment('share', claim, 'applicability', {'branch': 'AB'}, 0, 'AB'))

    service = Service(tmp_path)
    aa = service.query('AA')
    ab = service.query('AB')
    assert aa['claims'][0]['origin_branch'] == 'AA'
    assert ab['claims'][0]['origin_branch'] == 'AA'
    assert ab['claims'][0]['origin_version'] == 'synthetic-artifact-v1'

    # history of both branches carries the marker
    for snapshot in (aa, ab):
        marker = [h for h in snapshot['history'] if h['claim_ref'] == claim]
        assert marker and all(h['origin_branch'] == 'AA' for h in marker)

    # YAML export (historical revision, deterministic) carries it as a field
    exported = service.export('AA', 1)
    assert exported['status'] == 'EXPORTED'
    text = (tmp_path / exported['handle']).read_text(encoding='utf8')
    assert 'origin_branch' in text
    document = yaml.safe_load(text)
    assert document['claims'][0]['origin_branch'] == 'AA'
    ab_export = service.export('AB', 1)
    assert yaml.safe_load((tmp_path / ab_export['handle']).read_text(encoding='utf8'))['claims'][0]['origin_branch'] == 'AA'

    # trace: per-requirement claims must expose their origin marker
    trace = service.trace('master')
    assert trace['origins'][claim]['origin_branch'] == 'AA'
    entries = [c for residual in trace['residual'] for c in residual['claim_origins']]
    assert entries and all(c['claim_id'] != claim or c['origin_branch'] == 'AA' for c in entries)
    assert any(c['claim_id'] == claim and c['origin_branch'] == 'AA' for c in entries)


def test_property_event_cannot_rewrite_origin_marker(tmp_path):
    result = accepted(tmp_path, package())
    claim = result['claim_ids']['one']
    service = Service(tmp_path)

    for name in ('origin_branch', 'origin_version'):
        tamper = amendment('tamper-' + name, claim, 'property', {'name': name, 'value': 'AB'}, 1)
        refused = service.submit(json.dumps(tamper))
        assert refused['status'] == 'REJECTED', refused
        assert any(e['code'] == 'IMMUTABLE_FIELD' for e in refused['errors']), refused

    # an ordinary property event is accepted but never touches the marker
    accepted(tmp_path, amendment('confidence', claim, 'property', {'name': 'confidence', 'value': '1.2300e-40'}, 1))
    snapshot = service.query('AA')
    assert snapshot['claims'][0]['origin_branch'] == 'AA'
    assert snapshot['claims'][0]['origin_version'] == 'synthetic-artifact-v1'
    assert snapshot['claims'][0]['properties'] == {'confidence': '1.2300e-40'}

    # the stored row is immutable even for ordinary SQL
    with service.store.read() as connection:
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute("UPDATE claims SET origin_branch='AB' WHERE id=?", (claim,))
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute('DELETE FROM claims WHERE id=?', (claim,))
        raw = connection.execute('SELECT origin_branch FROM claims WHERE id=?', (claim,)).fetchone()[0]
    assert raw == 'AA'
    assert service.query('AA')['claims'][0]['origin_branch'] == 'AA'
