"""N1 regression: the dependency snapshot belongs to the claim, not to the event.

AC001-R2 found that ``_materialize`` took ``dependencies``/``review_id`` from the
package that carried the event.  A claim shared into another branch therefore
inherited the *sharing* package's dependencies (normally ``{}``), so
``STALE_CHECK`` could not fire in the target branch and ``trace`` could report
``ready_for_owner_review=true`` over a stale support.

The snapshot is fixed at admission time, in the same transaction, in an
immutable ``claim_snapshots`` row.  The ``applicability`` event supplies a branch
relation only -- never the claim's dependencies.
"""
import json
import sqlite3

import pytest

from mockup.admission import Service
from mockup.fixtures import package, item, amendment, WORK, POLICY


def admit(directory, p, submit_role='author', key=None):
    """Full real path: init -> submit -> independent review -> atomic admit."""
    author = Service(directory, role=submit_role)
    reviewer = Service(directory, role='reviewer')
    author.init({'external_work_ref': WORK, 'policy_digest': POLICY})
    candidate = author.submit(json.dumps(p))
    assert candidate['status'] == 'RECORDED_CANDIDATE', candidate
    review = reviewer.review(candidate['candidate_id'], candidate['intent_digest'])
    assert review['status'] == 'DEMO_REVIEWED', review
    admitted = reviewer.admit(candidate['candidate_id'], review['review_id'],
                              key or p['idempotency_key'], candidate['intent_digest'])
    assert admitted['status'] == 'DEMO_ADMITTED', admitted
    return review['review_id'], admitted


def by_id(snapshot, claim_id):
    return next(claim for claim in snapshot['claims'] if claim['claim_id'] == claim_id)


def test_sharing_event_does_not_replace_the_claim_dependency_snapshot(tmp_path):
    origin_review, first = admit(tmp_path, package('n1-aa', deps={'AA': 0}))
    claim = first['claim_ids']['one']

    # AA moves on: head(AA) becomes 2, so a dependency on revision 0 is stale.
    admit(tmp_path, package('n1-aa2', revision=1, items=[item('two', requirements=['R2'])]))

    # The sharing package carries its own dependencies ({} here) and its own review.
    share_review, _ = admit(tmp_path, amendment('n1-share', claim, 'applicability',
                                                {'branch': 'AB'}, 0, 'AB'))
    assert share_review != origin_review

    admit(tmp_path, package('n1-ab', 'AB', revision=1,
                            items=[item('ab', branches=['AB'], requirements=['R2'])]))
    admit(tmp_path, amendment('n1-conv-ab', '', 'converge', {}, 2, 'AB'))

    shared = by_id(Service(tmp_path).query('AB'), claim)
    assert shared['dependencies'] == {'AA': 0}, shared
    assert shared['review_id'] == origin_review, shared

    reviewer = Service(tmp_path, role='reviewer')
    assert reviewer.sync('AA')['status'] == 'SYNCED'
    assert reviewer.sync('AB')['status'] == 'SYNCED'

    ab_trace = Service(tmp_path, role='owner').trace('AB')
    r1 = next(row for row in ab_trace['residual'] if row['requirement_ref'] == 'R1')
    assert 'STALE_CHECK' in r1['reasons'], r1
    assert claim not in r1['claim_refs'], r1
    assert ab_trace['ready_for_owner_review'] is False, ab_trace

    # The owner excludes the stale origin branch; the remaining branch still
    # depends on it and therefore must stay NOT_READY.
    admit(tmp_path, amendment('n1-exclude', '', 'exclude', {'branch': 'AA'}, 3, 'AB'),
          submit_role='owner')
    assert reviewer.sync('AB')['status'] == 'SYNCED'

    master = Service(tmp_path, role='owner').trace('master')
    assert master['excluded_branches'] == ['AA'], master
    remaining = next(row for row in master['residual'] if row['requirement_ref'] == 'R1')
    assert 'STALE_CHECK' in remaining['reasons'], master
    assert master['ready_for_owner_review'] is False, master
    assert 'CRITERIA_NOT_CURRENT' in master['blockers'], master


def test_claim_snapshot_is_immutable_through_ordinary_sql(tmp_path):
    _, first = admit(tmp_path, package('n1-immutable', deps={'AA': 0}))
    claim = first['claim_ids']['one']
    database = tmp_path / 'dom.sqlite3'
    connection = sqlite3.connect(database)
    try:
        row = connection.execute('SELECT dependencies,review_id FROM claim_snapshots WHERE claim_id=?',
                                 (claim,)).fetchone()
        assert row is not None, 'admission must persist the claim dependency snapshot'
        assert json.loads(row[0]) == {'AA': 0}

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE claim_snapshots SET dependencies='{}' WHERE claim_id=?", (claim,))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute('DELETE FROM claim_snapshots WHERE claim_id=?', (claim,))
    finally:
        connection.close()
    assert Service(tmp_path).query('AA')['claims'][0]['dependencies'] == {'AA': 0}
