"""P1: optional commit_ref, derived versions, baseline view, recall, diff."""
import json

import pytest

from mockup.admission import Service
from mockup.dom_contract import validate
from mockup.fixtures import package, item, amendment
from test_projection_state import accepted


def lite_service(directory):
    svc = Service(directory, profile='lite')
    started = svc.start('Build a versioned thing', branches=['main'])
    assert started['status'] == 'STARTED', started
    return svc


# --------------------------------------------------------------- P1.1 commit_ref
def test_code_claim_without_commit_ref_still_admits(tmp_path):
    svc = lite_service(tmp_path)
    result = svc.claim('main', 'code', 'print(1)', **{
        'repository_ref': 'demo:repo', 'relative_path': 'a.py', 'language': 'python'})
    assert result['status'] == 'CLAIM_ADMITTED', result
    snap = svc.query('main')
    claim = next(c for c in snap['claims'] if c['claim_id'] == result['claim_id'])
    assert 'commit_ref' not in claim['item']['metadata']


def test_code_claim_with_valid_commit_ref_is_stored(tmp_path):
    svc = lite_service(tmp_path)
    commit = {'hash': 'a' * 40, 'branch': 'main', 'author': 'A',
              'message': 'initial', 'committed_at': '2026-11-11T18:00:00Z'}
    result = svc.claim('main', 'code', 'print(1)', **{
        'repository_ref': 'demo:repo', 'relative_path': 'a.py', 'language': 'python',
        'commit_ref': commit})
    assert result['status'] == 'CLAIM_ADMITTED', result
    snap = svc.query('main')
    claim = next(c for c in snap['claims'] if c['claim_id'] == result['claim_id'])
    assert claim['item']['metadata']['commit_ref'] == commit


def test_strict_contract_accepts_optional_commit_ref():
    p = package(items=[item('a', typ='code')])
    p['items'][0]['metadata']['commit_ref'] = {'hash': 'b' * 64, 'branch': 'AA'}
    assert validate(p) == []
    p['items'][0]['metadata']['commit_ref'] = {'hash': 'not-a-hash', 'branch': 'AA'}
    errors = validate(p)
    assert any(error['path'] == 'metadata.commit_ref' for error in errors), errors


@pytest.mark.parametrize('bad', [
    {'hash': 'xyz', 'branch': 'main'},
    {'hash': 'a' * 40, 'branch': ''},
    {'hash': 'a' * 40, 'branch': 'main', 'extra': 1},
])
def test_invalid_commit_ref_is_refused(tmp_path, bad):
    svc = lite_service(tmp_path)
    result = svc.claim('main', 'code', 'print(1)', **{
        'repository_ref': 'demo:repo', 'relative_path': 'a.py', 'language': 'python',
        'commit_ref': bad})
    assert result['status'] == 'INVALID_FIELD', result
    assert result.get('field') == 'commit_ref', result


# ----------------------------------------------------- P1.2 derived versions
def test_version_logical_id_and_supersedes_are_derived(tmp_path):
    svc = lite_service(tmp_path)
    first = svc.claim('main', 'concept', 'First version', **{'definition': 'v1'})
    assert first['status'] == 'CLAIM_ADMITTED', first
    updated = svc.update(first['claim_id'], 'Second version', 'clarify the concept')
    assert updated['status'] == 'CLAIM_UPDATED', updated
    assert updated['version'] == 2
    assert updated['record_id'] == first['claim_id']
    assert updated['logical_claim_id'] == first['claim_id']

    snap = svc.query('main')
    claims = {c['claim_id']: c for c in snap['claims']}
    old = claims[first['claim_id']]
    new = claims[updated['new_claim_id']]
    assert (old['version'], old['logical_claim_id'], old['supersedes']) == (1, first['claim_id'], None)
    assert (new['version'], new['logical_claim_id'], new['supersedes']) == (2, first['claim_id'], first['claim_id'])

    found = svc.find('Second')
    match = next(m for m in found['matches'] if m['claim_id'] == updated['new_claim_id'])
    assert (match['version'], match['logical_claim_id'], match['supersedes']) == (2, first['claim_id'], first['claim_id'])


# --------------------------------------------------------------- P1.3 baseline
def test_baseline_view_is_deterministic_claim_chunks(tmp_path):
    accepted(tmp_path, package(items=[item('a', raw=b'A\r\n'), item('b', raw=b'B\r\n'), item('c', raw=b'C\r\n')]))
    with Service(tmp_path).store.read() as c:
        rows = c.execute(
            "SELECT seq, prev_seq, claim_id, chunk_hash, revision FROM baseline_view "
            "WHERE branch='AA' ORDER BY seq").fetchall()
        event_hashes = [r[0] for r in c.execute(
            "SELECT event_hash FROM events WHERE branch='AA' AND kind='claim' ORDER BY seq")]
    assert [r['seq'] for r in rows] == [1, 2, 3]
    assert [r['prev_seq'] for r in rows] == [0, 1, 2]
    assert [r['chunk_hash'] for r in rows] == event_hashes
    assert all(r['chunk_hash'] for r in rows)
    assert [r['revision'] for r in rows] == [1, 1, 1]


# ------------------------------------------------------------------- P1.4 recall
def test_recall_replays_branch_events_and_stops_before_archive(tmp_path):
    svc = lite_service(tmp_path)
    first = svc.claim('main', 'concept', 'First version', **{'definition': 'v1'})
    updated = svc.update(first['claim_id'], 'Second version', 'clarify')
    with svc.store.read() as c:
        rows = c.execute("SELECT seq, kind, claim_id FROM branch_event_view "
                         "WHERE branch='main' ORDER BY seq").fetchall()
    first_seq = next(r['seq'] for r in rows if r['kind'] == 'claim' and r['claim_id'] == first['claim_id'])
    new_seq = next(r['seq'] for r in rows if r['kind'] == 'claim' and r['claim_id'] == updated['new_claim_id'])
    replacement_seq = next(r['seq'] for r in rows if r['kind'] == 'replacement')

    at_first = svc.recall('main', first_seq)
    assert at_first['status'] == 'RECALL', at_first
    ids = {c['claim_id'] for c in at_first['active_claims']}
    assert first['claim_id'] in ids and updated['new_claim_id'] not in ids
    assert at_first['pending_decisions'] is None
    assert at_first['related_branches'] == []
    assert at_first['baseline_range']['to_seq'] == first_seq

    at_new = svc.recall('main', new_seq)
    ids = {c['claim_id'] for c in at_new['active_claims']}
    assert first['claim_id'] in ids and updated['new_claim_id'] in ids

    at_archive = svc.recall('main', replacement_seq)
    ids = {c['claim_id'] for c in at_archive['active_claims']}
    assert updated['new_claim_id'] in ids and first['claim_id'] not in ids
    assert first['claim_id'] in at_archive['archived_claims']

    empty = svc.recall('main', 0)
    assert empty['status'] == 'RECALL' and empty['active_claims'] == []
    assert empty['revision'] == 0

    out = svc.recall('main', replacement_seq + 100)
    assert out['status'] == 'REVISION_OUT_OF_RANGE', out


# ---------------------------------------------------------- P1.5 versions/diff
def admit(directory, p):
    author = Service(directory)
    candidate = author.submit(json.dumps(p))
    assert candidate['status'] == 'RECORDED_CANDIDATE', candidate
    reviewer = Service(directory, role='reviewer')
    review = reviewer.review(candidate['candidate_id'], candidate['intent_digest'])
    assert review['status'] == 'DEMO_REVIEWED', review
    result = reviewer.admit(candidate['candidate_id'], review['review_id'],
                            p['idempotency_key'], candidate['intent_digest'])
    assert result['status'] == 'DEMO_ADMITTED', result
    return result


def test_recall_reports_related_branches_and_resolved_conflicts(tmp_path):
    first = accepted(tmp_path, package('a', items=[item('a', raw=b'A\r\n')]))
    a = first['claim_ids']['a']
    admit(tmp_path, amendment('share', a, 'applicability', {'branch': 'AB'}, 0, 'AB'))
    admit(tmp_path, amendment('conf', a, 'conflict', {'conflict_ref': 'C1'}, 1, 'AA'))
    admit(tmp_path, amendment('res', a, 'resolve', {'conflict_ref': 'C1'}, 2, 'AA'))
    with Service(tmp_path).store.read() as c:
        rows = c.execute("SELECT seq, kind FROM branch_event_view WHERE branch='AA' ORDER BY seq").fetchall()
    conflict_seq = next(r['seq'] for r in rows if r['kind'] == 'conflict')
    resolve_seq = next(r['seq'] for r in rows if r['kind'] == 'resolve')

    before = Service(tmp_path).recall('AA', conflict_seq)
    assert before['resolved_conflicts'] == []
    assert 'AB' in before['related_branches']
    after = Service(tmp_path).recall('AA', resolve_seq)
    assert after['resolved_conflicts'] == ['C1']


def test_claim_versions_follow_the_replacement_chain(tmp_path):
    first = accepted(tmp_path, package('a', items=[item('a', raw=b'A\r\n')]))
    a = first['claim_ids']['a']
    second = admit(tmp_path, package('b', revision=1, items=[item('b', raw=b'B\r\n')]))
    b = second['claim_ids']['b']
    admit(tmp_path, amendment('rep', a, 'replacement', {'replacement_ref': b}, 2, 'AA'))

    result = Service(tmp_path).claim_versions(a)
    assert result['status'] == 'CLAIM_VERSIONS', result
    assert result['logical_claim_id'] == a
    versions = result['versions']
    assert [(v['claim_id'], v['version'], v['supersedes'], v['is_current']) for v in versions] == [
        (a, 1, None, False), (b, 2, a, True)]


def test_diff_aligns_by_logical_claim_id(tmp_path):
    first = accepted(tmp_path, package('a', items=[item('a', raw=b'A\r\n')]))
    a = first['claim_ids']['a']
    # AB gets the same claim through an explicit applicability event.
    admit(tmp_path, amendment('share', a, 'applicability', {'branch': 'AB'}, 0, 'AB'))
    # AA replaces A with B; AB still has A.
    second = admit(tmp_path, package('b', revision=1, items=[item('b', raw=b'B\r\n')]))
    b = second['claim_ids']['b']
    admit(tmp_path, amendment('rep', a, 'replacement', {'replacement_ref': b}, 2, 'AA'))

    result = Service(tmp_path).diff('AA', 'AB')
    assert result['status'] == 'DIFF', result
    assert result['comparable'] is True
    assert result['common_ancestor'] == a
    assert result['only_a'] == [] and result['only_b'] == []
    assert result['identical'] == []
    assert len(result['changed']) == 1
    change = result['changed'][0]
    assert change['logical_id'] == a
    assert change['a']['claim_id'] == b and change['a']['version'] == 2
    assert change['b']['claim_id'] == a and change['b']['version'] == 1


def test_diff_without_a_shared_logical_claim_is_not_comparable(tmp_path):
    first = accepted(tmp_path, package('a', items=[item('a', raw=b'A\r\n')]))
    a = first['claim_ids']['a']
    second = admit(tmp_path, package('b', branch='AB', revision=0, items=[item('b', raw=b'B\r\n', branches=['AB'])]))
    b = second['claim_ids']['b']
    result = Service(tmp_path).diff('AA', 'AB')
    assert result['status'] == 'DIFF', result
    assert result['comparable'] is False
    assert result['common_ancestor'] is None
    assert result['only_a'] == [a]
    assert result['only_b'] == [b]
