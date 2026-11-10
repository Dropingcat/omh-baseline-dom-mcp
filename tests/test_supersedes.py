"""Append supersedes links must point at an event of the same branch and claim (T13)."""
import json

from mockup.admission import Service
from mockup.fixtures import WORK, POLICY, package, item, amendment


def accepted(directory, payload):
    author = Service(directory)
    author.init({'external_work_ref': WORK, 'policy_digest': POLICY})
    candidate = author.submit(json.dumps(payload))
    assert candidate['status'] == 'RECORDED_CANDIDATE', candidate
    reviewer = Service(directory, role='reviewer')
    review = reviewer.review(candidate['candidate_id'], candidate['intent_digest'])
    result = reviewer.admit(candidate['candidate_id'], review['review_id'], payload['idempotency_key'], candidate['intent_digest'])
    assert result['status'] == 'DEMO_ADMITTED', result
    return result


def test_supersedes_chain_is_scoped_to_branch_and_claim(tmp_path):
    first = accepted(tmp_path, package())
    claim_one = first['claim_ids']['one']
    accepted(tmp_path, amendment('comment-1', claim_one, 'comment', {'text': 'first'}, 1))

    history = Service(tmp_path).query('AA')['history']
    original = [h for h in history if h['kind'] == 'comment'][0]['event_id']

    second_claim = accepted(tmp_path, package('two', revision=2, items=[item('two', requirements=['R2'])]))
    claim_two = second_claim['claim_ids']['two']

    cross_claim = amendment('cross', claim_two, 'comment', {'text': 'wrong target'}, 3)
    cross_claim['items'][0]['supersedes'] = original
    assert Service(tmp_path).submit(json.dumps(cross_claim))['status'] == 'SCOPE_DENIED'

    correction = amendment('comment-2', claim_one, 'comment', {'text': 'second'}, 3, supersedes=original)
    accepted(tmp_path, correction)
    snapshot = Service(tmp_path).query('AA')
    chain = [h for h in snapshot['history'] if h['kind'] == 'comment']
    assert len(chain) == 2
    assert chain[1]['provenance']['value']['supersedes'] == original
    assert chain[0]['origin_branch'] == chain[1]['origin_branch'] == 'AA'
