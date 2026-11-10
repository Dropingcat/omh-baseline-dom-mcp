"""AB002-A delivery guard regressions; matrix remains primary acceptance."""
import sqlite3
import pytest
from mockup.ab002_binding import binding_negatives
from mockup.ab002_matrix import refused_sql


def test_binding_negatives_and_target_recovery_over_real_mcp(tmp_path):
    result=binding_negatives(tmp_path)
    assert result['probe_count']==23
    assert all(p['unchanged_exact'] and p['sqlite_code']==sqlite3.SQLITE_CONSTRAINT_TRIGGER for p in result['probes'])
    assert result['recovery']['target_readback']['intent_count']==1


def test_refusal_oracle_rejects_unrelated_trigger_diagnostic(tmp_path):
    with sqlite3.connect(tmp_path/'dom.sqlite3') as c:
        c.executescript("CREATE TABLE facts(id PRIMARY KEY); INSERT INTO facts VALUES(1); CREATE TRIGGER unrelated BEFORE UPDATE ON facts BEGIN SELECT RAISE(ABORT,'UNRELATED'); END;")
        with pytest.raises(AssertionError,match='UNRELATED'):
            refused_sql(tmp_path,c,'UPDATE facts SET id=id',(),{'IMMUTABLE'},'unknown-diagnostic')


def test_refusal_oracle_rejects_successful_noop_update(tmp_path):
    with sqlite3.connect(tmp_path/'dom.sqlite3') as c:
        c.executescript('CREATE TABLE facts(id PRIMARY KEY); INSERT INTO facts VALUES(1);')
        with pytest.raises(AssertionError,match='not refused'):
            refused_sql(tmp_path,c,'UPDATE facts SET id=id',(),{'IMMUTABLE'},'successful-noop')
