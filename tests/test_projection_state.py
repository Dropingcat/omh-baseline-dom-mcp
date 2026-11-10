"""Regression: branch projection state must accumulate from history.

F1 (AC001): an ``applicability`` event used to rebuild the claim record, wiping
``archived`` and ``properties`` collected by earlier events.  That resurrected
archived support and produced a false ``ready_for_owner_review=true``.

These tests pin the real event order: archive -> applicability in the same
branch -> read the projection/trace.
"""
import json

from mockup.admission import Service
from mockup.fixtures import package, item, amendment, WORK, POLICY


def accepted(directory, p, role='author'):
    a = Service(directory, role=role)
    a.init({'external_work_ref': WORK, 'policy_digest': POLICY})
    c = a.submit(json.dumps(p))
    assert c['status'] == 'RECORDED_CANDIDATE', c
    b = Service(directory, role='reviewer')
    r = b.review(c['candidate_id'], c['intent_digest'])
    result = b.admit(c['candidate_id'], r['review_id'], p['idempotency_key'], c['intent_digest'])
    assert result['status'] == 'DEMO_ADMITTED', result
    return result


def by_id(snapshot, claim_id):
    return next(c for c in snapshot['claims'] if c['claim_id'] == claim_id)


def test_archived_support_stays_archived_after_same_branch_applicability(tmp_path):
    first = accepted(tmp_path, package())                                     # AA rev1: R1
    archived_claim = first['claim_ids']['one']
    accepted(tmp_path, package('aa2', revision=1, items=[item('two', requirements=['R2'])]))
    accepted(tmp_path, amendment('arch', archived_claim, 'archive', {}, 2))     # AA rev3
    before = by_id(Service(tmp_path).query('AA'), archived_claim)
    assert before['archived'] is True

    # applicability aimed at the branch it is already admitted in: it must add a
    # relation, never reset the lifecycle state.
    accepted(tmp_path, amendment('self-app', archived_claim, 'applicability', {'branch': 'AA'}, 3))
    after = by_id(Service(tmp_path).query('AA'), archived_claim)
    assert after['archived'] is True, after

    trace = Service(tmp_path).trace('AA')
    row = next(r for r in trace['residual'] if r['requirement_ref'] == 'R1')
    assert 'ARCHIVED_SUPPORT' in row['reasons'], row
    assert 'MISSING_COVERAGE' in row['reasons'], row
    assert archived_claim not in row['claim_refs'], row
    assert trace['ready_for_owner_review'] is False, trace


def test_false_ready_is_not_produced_after_archive_and_applicability(tmp_path):
    """Full master-scope reproduction of the AC001 F1 false closure."""
    first = accepted(tmp_path, package())                                     # AA rev1: R1
    archived_claim = first['claim_ids']['one']
    accepted(tmp_path, package('aa2', revision=1, items=[item('two', requirements=['R2'])]))
    accepted(tmp_path, amendment('arch', archived_claim, 'archive', {}, 2))     # AA rev3
    accepted(tmp_path, amendment('self-app', archived_claim, 'applicability', {'branch': 'AA'}, 3))
    accepted(tmp_path, package('ab', 'AB', items=[item('ab', branches=['AB'], requirements=['R1', 'R2'])]))
    accepted(tmp_path, amendment('conv-aa', '', 'converge', {}, 4))
    accepted(tmp_path, amendment('conv-ab', '', 'converge', {}, 1, 'AB'))
    reviewer = Service(tmp_path, role='reviewer')
    assert reviewer.sync('AA')['status'] == 'SYNCED'
    assert reviewer.sync('AB')['status'] == 'SYNCED'

    trace = Service(tmp_path, role='owner').trace('master')
    aa = next(r for r in trace['residual'] if r['branch'] == 'AA' and r['requirement_ref'] == 'R1')
    assert 'ARCHIVED_SUPPORT' in aa['reasons'], trace
    assert archived_claim not in aa['claim_refs'], trace
    assert trace['ready_for_owner_review'] is False, trace
    assert trace['blockers'], trace


def test_properties_survive_applicability(tmp_path):
    first = accepted(tmp_path, package())
    claim = first['claim_ids']['one']
    accepted(tmp_path, amendment('prop', claim, 'property', {'name': 'confidence', 'value': '0.9'}, 1))
    accepted(tmp_path, amendment('self-app', claim, 'applicability', {'branch': 'AA'}, 2))
    record = by_id(Service(tmp_path).query('AA'), claim)
    assert record['properties'] == {'confidence': '0.9'}, record
    assert record['archived'] is False
