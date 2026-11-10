"""Git boundary is fixture-only: HEAD never moves, real intents are NOT_IMPLEMENTED (T20)."""
from mockup.ports import GitPort


def test_git_fixture_reports_state_without_mutation(tmp_path):
    port = GitPort(tmp_path)
    head = port.head()
    assert head['dirty'] is True and head['simulation'] is True

    artifact_a = port.snapshot(b'print("A")\n')
    artifact_b = port.snapshot(b'print("B")\n')
    assert artifact_a['digest'] != artifact_b['digest']
    assert artifact_a['dirty'] is True and artifact_a['simulation'] is True

    for operation in ('create', 'merge'):
        intent = port.intent(operation)
        assert intent['status'] == 'NOT_IMPLEMENTED'
        assert intent['simulation'] is True and intent['head_unchanged'] is True

    assert port.head() == head
    assert not (tmp_path / '.git').exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == []
