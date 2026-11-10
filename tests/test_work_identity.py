"""Work/branch scope at init, and identity fixture boundaries (T01, T02)."""
import json

from mockup.admission import Service
from mockup.fixtures import WORK, POLICY, package


def test_invalid_init_and_foreign_work_leave_no_state(tmp_path):
    service = Service(tmp_path)
    assert service.init({'external_work_ref': 'demo:other-work-W2', 'policy_digest': POLICY})['status'] == 'SCOPE_DENIED'
    assert not (tmp_path / 'dom.sqlite3').exists()
    assert service.init({'external_work_ref': WORK, 'policy_digest': 'not-the-policy'})['status'] == 'POLICY_MISMATCH'
    assert not (tmp_path / 'dom.sqlite3').exists()
    assert service.init({'shape': 'wrong'})['status'] == 'REJECTED'
    assert not (tmp_path / 'dom.sqlite3').exists()

    assert service.init({'external_work_ref': WORK, 'policy_digest': POLICY})['status'] == 'INITIALIZED'
    foreign = package()
    foreign['external_work_ref'] = 'demo:other-work-W2'
    assert service.submit(json.dumps(foreign))['status'] == 'SCOPE_DENIED'
    assert service.query('AA')['claims'] == []

    # a second session over the same binding sees the same history, not a copy
    second = Service(tmp_path)
    assert second.query('AA')['revision'] == service.query('AA')['revision'] == 0


def test_helper_and_unknown_host_cannot_review(tmp_path):
    author = Service(tmp_path)
    author.init({'external_work_ref': WORK, 'policy_digest': POLICY})
    candidate = author.submit(json.dumps(package()))
    assert candidate['status'] == 'RECORDED_CANDIDATE'

    helper = Service(tmp_path, role='helper')  # same root as the author
    assert helper.review(candidate['candidate_id'], candidate['intent_digest'])['status'] == 'INDEPENDENCE_NOT_ENFORCED'

    unknown = Service(tmp_path, role='unknown-host')
    assert unknown.query('AA')['status'] == 'SCOPE_DENIED'
    assert unknown.review(candidate['candidate_id'], candidate['intent_digest'])['status'] == 'INDEPENDENCE_NOT_ENFORCED'
