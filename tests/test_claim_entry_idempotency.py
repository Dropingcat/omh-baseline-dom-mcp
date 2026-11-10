"""TD-DOM-22.5: idempotency key at the claim-entry level (TD-DOM-28).

The optional ``idempotency_key`` argument of ``dom_claim`` / ``dom_update`` is
threaded into the submit/admit idempotency rows.  A repeat of the same key with the
same content returns the same claim_id; the same key with different content is
refused with ``IDEMPOTENCY_MISMATCH``.
"""
from mockup.admission import Service
from mockup.fixtures import WORK, POLICY


def _lite(tmp_path):
    svc = Service(tmp_path, profile='lite')
    svc.start(request='Collect the baseline measurements')
    return svc


def _strict(tmp_path):
    svc = Service(tmp_path, role='author', simulation=True, profile='strict')
    svc.init({'external_work_ref': WORK, 'policy_digest': POLICY})
    return svc


def test_lite_claim_replay_same_key_and_content_returns_same_claim_id(tmp_path):
    svc = _lite(tmp_path)
    first = svc.claim('main', 'text', 'The measured latency is 12 ms.', idempotency_key='idem-1')
    assert first['status'] == 'CLAIM_ADMITTED', first
    second = svc.claim('main', 'text', 'The measured latency is 12 ms.', idempotency_key='idem-1')
    assert second['status'] == 'ALREADY_RECORDED', second
    assert second['claim_id'] == first['claim_id']


def test_lite_claim_same_key_different_content_is_idempotency_mismatch(tmp_path):
    svc = _lite(tmp_path)
    first = svc.claim('main', 'text', 'The measured latency is 12 ms.', idempotency_key='idem-1')
    assert first['status'] == 'CLAIM_ADMITTED', first
    second = svc.claim('main', 'text', 'The measured latency is now 13 ms.', idempotency_key='idem-1')
    assert second['status'] == 'IDEMPOTENCY_MISMATCH', second


def test_lite_claim_without_key_still_dedups_by_content(tmp_path):
    svc = _lite(tmp_path)
    first = svc.claim('main', 'text', 'The measured latency is 12 ms.', idempotency_key=None)
    assert first['status'] == 'CLAIM_ADMITTED', first
    second = svc.claim('main', 'text', 'The measured latency is 12 ms.', idempotency_key=None)
    assert second['status'] == 'ALREADY_RECORDED', second
    assert second['claim_id'] == first['claim_id']


def test_strict_claim_replay_same_key_and_content_is_the_same_candidate(tmp_path):
    svc = _strict(tmp_path)
    first = svc.claim('AA', 'text', 'Strict claim body', reason='td22.5', idempotency_key='idem-s1')
    assert first['status'] == 'RECORDED_CANDIDATE', first
    second = svc.claim('AA', 'text', 'Strict claim body', reason='td22.5', idempotency_key='idem-s1')
    assert second['status'] == 'RECORDED_CANDIDATE', second
    assert second['candidate_id'] == first['candidate_id']


def test_strict_claim_same_key_different_content_is_idempotency_mismatch(tmp_path):
    svc = _strict(tmp_path)
    first = svc.claim('AA', 'text', 'Strict claim body', reason='td22.5', idempotency_key='idem-s1')
    assert first['status'] == 'RECORDED_CANDIDATE', first
    second = svc.claim('AA', 'text', 'Another strict claim body', reason='td22.5', idempotency_key='idem-s1')
    assert second['status'] == 'IDEMPOTENCY_MISMATCH', second


def test_strict_arguments_bind_idempotency_key_on_claim_and_update():
    from mockup import server as server_mod

    ok = server_mod.strict_arguments('dom_claim', {'branch': 'AA', 'type': 'text', 'text': 'x', 'idempotency_key': 'idem-9'})
    assert ok['idempotency_key'] == 'idem-9'
    try:
        server_mod.strict_arguments('dom_claim', {'branch': 'AA', 'type': 'text', 'text': 'x', 'idempotency_key': 5})
        raise AssertionError('idempotency_key must be a string')
    except Exception as exc:  # ToolInput is the typed refusal
        assert str(exc) == 'INVALID_ARGUMENTS'

    ok_u = server_mod.strict_arguments('dom_update', {'claim_id': 'c1', 'text': 'x', 'reason': 'why', 'idempotency_key': 'idem-9'})
    assert ok_u['idempotency_key'] == 'idem-9'
