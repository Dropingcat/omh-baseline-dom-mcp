"""P0 invariants from the 2026-11-11 architecture audit.

TD-DOM-33: one chain verification per read (trace/resume).
TD-DOM-34: sync must not hold a read transaction across external I/O.
TD-DOM-36: every claim has exactly one immutable snapshot.
"""
import json
import sqlite3
import threading

from mockup import admission
from mockup import ports
from mockup.admission import Service
from mockup.fixtures import package, item
from test_projection_state import accepted


def test_trace_and_resume_verify_chain_once(tmp_path, monkeypatch):
    accepted(tmp_path, package())
    calls = []
    real = admission.verify_chain

    def counting(c):
        calls.append(1)
        return real(c)

    monkeypatch.setattr(admission, 'verify_chain', counting)
    assert Service(tmp_path).trace('AA')['chain']['status'] == 'CHAIN_OK'
    assert len(calls) == 1, 'trace must verify the chain once'

    calls.clear()
    assert Service(tmp_path).resume('AA')['status'] == 'RESUMED'
    assert len(calls) == 1, 'resume must verify the chain once'

    calls.clear()
    assert Service(tmp_path).query('AA')['status'] == 'SNAPSHOT'
    assert len(calls) == 1, 'query must verify the chain once'


def test_sync_does_not_hold_a_read_transaction_across_external_io(tmp_path, monkeypatch):
    """A writer on another branch must not wait for the slow OMH port.

    The old sync kept a read transaction open while ``read_target``/``attach``
    ran.  With ``journal_mode=DELETE`` that blocks the writer's commit until
    ``busy_timeout`` (2 s), so this test observes STORAGE_BUSY instead of an
    admitted claim.
    """
    accepted(tmp_path, package())  # AA outbox: OMH_EVIDENCE + YAML_EXPORT

    pending = package('ab', 'AB', items=[item('ab', branches=['AB'])])
    author = Service(tmp_path)
    candidate = author.submit(json.dumps(pending))
    assert candidate['status'] == 'RECORDED_CANDIDATE', candidate
    review = Service(tmp_path, role='reviewer').review(candidate['candidate_id'], candidate['intent_digest'])
    assert review['status'] == 'DEMO_REVIEWED', review

    entered = threading.Event()
    release = threading.Event()
    real_read = ports.OMHPort.read_target

    def slow_read(self, target):
        entered.set()
        if not release.wait(15):
            raise OSError('TEST_TIMEOUT')
        return real_read(self, target)

    monkeypatch.setattr(ports.OMHPort, 'read_target', slow_read)

    result = {}

    def run_sync():
        try:
            result['sync'] = Service(tmp_path, role='reviewer').sync('AA')
        except BaseException as error:  # pragma: no cover - surfaced below
            result['error'] = error

    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()
    try:
        assert entered.wait(10), 'sync never reached the external OMH port'
        admitted = Service(tmp_path, role='reviewer').admit(
            candidate['candidate_id'], review['review_id'], 'ab-key', candidate['intent_digest'])
        assert admitted['status'] == 'DEMO_ADMITTED', admitted
    finally:
        release.set()
        thread.join(20)
    assert not thread.is_alive(), 'sync did not finish'
    assert 'error' not in result, result.get('error')
    assert result['sync']['status'] == 'SYNCED', result['sync']


def test_every_claim_has_exactly_one_snapshot(tmp_path):
    accepted(tmp_path, package(items=[item('one'), item('two', typ='quote')]))
    with Service(tmp_path).store.read() as c:
        assert admission.claim_snapshot_gaps(c) == []
        claim_count, snapshot_count = c.execute(
            'SELECT (SELECT count(*) FROM claims), (SELECT count(*) FROM claim_snapshots)').fetchone()
        assert (claim_count, snapshot_count) == (2, 2)


def test_snapshot_gap_checker_sees_a_bypassing_insert(tmp_path):
    """The guard is real: a raw claim INSERT without its snapshot is reported."""
    accepted(tmp_path, package())
    with sqlite3.connect(tmp_path / 'dom.sqlite3') as raw:
        raw.execute(
            "INSERT INTO claims(id,candidate,tx,content_type,raw,raw_sha256,encoding,media_type,"
            "source_ref,origin_branch,origin_version,payload) "
            "SELECT 'gap-claim',candidate,tx,content_type,raw,raw_sha256,encoding,media_type,"
            "source_ref,origin_branch,origin_version,payload FROM claims LIMIT 1")
    with Service(tmp_path).store.read() as c:
        assert admission.claim_snapshot_gaps(c) == ['gap-claim']
