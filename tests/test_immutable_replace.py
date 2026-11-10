"""R2-1 regression: ``INSERT OR REPLACE`` must not rewrite immutable history.

AC001-R2 found that the immutability guarantee held only on ``BEFORE UPDATE`` /
``BEFORE DELETE`` triggers.  In SQLite ``INSERT OR REPLACE`` resolves a PRIMARY
KEY / UNIQUE conflict by *deleting* the conflicting row and inserting a new one,
and with ``recursive_triggers`` off (the default) that delete does not fire the
``DELETE`` trigger.  So one ordinary statement rewrote a claim's dependency
snapshot to ``{}`` -- the exact false-READY class N1 was about -- and rewrote
``claims.origin_branch``, while ``chain`` stayed ``CHAIN_OK``.

These tests use a *raw* ``sqlite3`` connection with default pragmas: the guard
must live in the schema, not in the connection setup, or a direct SQL client
simply switches it off.
"""
import json
import sqlite3
import uuid

import pytest

from mockup.admission import Service
from mockup.fixtures import package, item, WORK, POLICY


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


def stale_claim_in_aa(directory):
    """Claim with ``dependencies={'AA': 0}`` plus a head(AA)=1 -> R1 is stale."""
    _, first = admit(directory, package('r2-aa', deps={'AA': 0}))
    claim = first['claim_ids']['one']
    admit(directory, package('r2-aa2', revision=1, items=[item('two', requirements=['R2'])]))
    return claim


def raw(directory):
    connection = sqlite3.connect(directory / 'dom.sqlite3')
    connection.execute('PRAGMA foreign_keys=ON')
    return connection


def r1(trace):
    return next(row for row in trace['residual'] if row['requirement_ref'] == 'R1')


def test_insert_or_replace_cannot_rewrite_the_claim_dependency_snapshot(tmp_path):
    claim = stale_claim_in_aa(tmp_path)
    owner = Service(tmp_path, role='owner')
    before = owner.trace('AA')
    assert 'STALE_CHECK' in r1(before)['reasons'], before
    assert before['ready_for_owner_review'] is False, before

    connection = raw(tmp_path)
    try:
        row = connection.execute('SELECT claim_id,tx,branch,revision,dependencies,review_id '
                                 'FROM claim_snapshots WHERE claim_id=?', (claim,)).fetchone()
        assert row is not None and json.loads(row[4]) == {'AA': 0}, row

        # One ordinary statement: conflict on the PK deletes the old row.
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute('INSERT OR REPLACE INTO claim_snapshots '
                               'VALUES(?,?,?,?,?,?)', (row[0], row[1], row[2], row[3], '{}', row[5]))
        connection.commit()

        stored = connection.execute('SELECT dependencies FROM claim_snapshots WHERE claim_id=?',
                                    (claim,)).fetchone()
        assert stored is not None, 'the snapshot row must still exist'
        assert json.loads(stored[0]) == {'AA': 0}, 'snapshot was rewritten through REPLACE'
    finally:
        connection.close()

    after = owner.trace('AA')
    assert r1(after)['reasons'] == r1(before)['reasons'], after
    assert 'STALE_CHECK' in r1(after)['reasons'], after
    assert after['ready_for_owner_review'] is False, 'REPLACE produced a false READY'
    assert after['chain']['status'] == 'CHAIN_OK', after['chain']
    projected = next(c for c in owner.query('AA')['claims'] if c['claim_id'] == claim)
    assert projected['dependencies'] == {'AA': 0}, projected


def test_insert_or_replace_cannot_rewrite_the_origin_branch_marker(tmp_path):
    claim = stale_claim_in_aa(tmp_path)
    connection = raw(tmp_path)
    try:
        row = connection.execute('SELECT * FROM claims WHERE id=?', (claim,)).fetchone()
        assert row is not None and row[9] == 'AA', row
        values = list(row)
        values[9] = 'AB'  # origin_branch
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute('INSERT OR REPLACE INTO claims VALUES(' +
                               ','.join('?' * len(values)) + ')', values)
        connection.commit()
        stored = connection.execute('SELECT origin_branch,origin_version FROM claims WHERE id=?',
                                    (claim,)).fetchone()
        assert stored is not None, 'the claim row must still exist'
        assert stored[0] == 'AA', 'branch marker was rewritten through REPLACE'
        assert stored[1] == 'synthetic-artifact-v1', stored
    finally:
        connection.close()
    assert Service(tmp_path).trace('AA')['origins'][claim]['origin_branch'] == 'AA'


def test_insert_or_ignore_and_upsert_cannot_rewrite_immutable_rows(tmp_path):
    claim = stale_claim_in_aa(tmp_path)
    connection = raw(tmp_path)
    try:
        row = connection.execute('SELECT claim_id,tx,branch,revision,dependencies,review_id '
                                 'FROM claim_snapshots WHERE claim_id=?', (claim,)).fetchone()
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute('INSERT OR IGNORE INTO claim_snapshots VALUES(?,?,?,?,?,?)',
                               (row[0], row[1], row[2], row[3], '{}', row[5]))
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute('INSERT INTO claim_snapshots VALUES(?,?,?,?,?,?) '
                               "ON CONFLICT(claim_id) DO UPDATE SET dependencies='{}'",
                               (row[0], row[1], row[2], row[3], '{}', row[5]))
        connection.commit()
        stored = connection.execute('SELECT dependencies FROM claim_snapshots WHERE claim_id=?',
                                    (claim,)).fetchone()
        assert json.loads(stored[0]) == {'AA': 0}, 'snapshot changed by IGNORE/upsert'
    finally:
        connection.close()


def test_replace_on_secondary_unique_keys_cannot_delete_history_rows(tmp_path):
    """A REPLACE may conflict on any UNIQUE constraint, not only on the PK."""
    admit(tmp_path, package('r2-uniq', deps={'AA': 0}))
    connection = raw(tmp_path)
    try:
        head = connection.execute('SELECT branch,revision FROM branch_heads WHERE branch=?',
                                  ('AA',)).fetchone()
        tx = connection.execute('SELECT id,branch,revision,receipt FROM transactions').fetchone()
        assert tx is not None, 'admission must persist a transaction row'
        with pytest.raises(sqlite3.IntegrityError, match='IMMUTABLE'):
            connection.execute("INSERT OR REPLACE INTO transactions(id,branch,revision,receipt) "
                               "VALUES('forged-tx',?,?,'{}')", (head[0], head[1]))
        connection.commit()
        kept = connection.execute('SELECT COUNT(*) FROM transactions WHERE id=?', (tx[0],)).fetchone()
        assert kept[0] == 1, 'REPLACE on UNIQUE(branch,revision) deleted the real transaction'
    finally:
        connection.close()


def test_normal_insert_path_still_admits_and_clean_initialization_is_idempotent(tmp_path):
    """The guard only refuses a *conflict*; ordinary inserts and init must work."""
    claim = stale_claim_in_aa(tmp_path)
    # A clean re-initialization of the same database neither duplicates nor fails.
    Service(tmp_path, role='author').init({'external_work_ref': WORK, 'policy_digest': POLICY})
    snapshot = Service(tmp_path).query('AA')
    assert [c['claim_id'] for c in snapshot['claims']].count(claim) == 1, snapshot
    assert next(c for c in snapshot['claims'] if c['claim_id'] == claim)['dependencies'] == {'AA': 0}

    connection = raw(tmp_path)
    try:
        counts = {t: connection.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
                  for t in ('candidates', 'reviews', 'transactions', 'claims',
                            'claim_snapshots', 'events', 'outbox')}
        assert min(counts.values()) > 0, counts
        # A brand-new row in an append-only table is still accepted.
        connection.execute("INSERT INTO delivery_events(intent,state,payload) "
                           "SELECT id,'pending','{}' FROM outbox LIMIT 1")
        connection.commit()
        assert connection.execute('SELECT COUNT(*) FROM delivery_events').fetchone()[0] > 0
        # A repeat of the same PK is still refused (now by the immutable guard).
        row = connection.execute('SELECT claim_id,tx,branch,revision,dependencies,review_id '
                                 'FROM claim_snapshots WHERE claim_id=?', (claim,)).fetchone()
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute('INSERT INTO claim_snapshots VALUES(?,?,?,?,?,?)', row)
    finally:
        connection.close()
    assert uuid.UUID(claim)  # claim ids are real UUIDs generated by admission
