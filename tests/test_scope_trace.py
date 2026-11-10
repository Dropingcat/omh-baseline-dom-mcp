import json
import sqlite3
import pytest
from mockup.admission import Service
from mockup.fixtures import package,item,amendment,WORK,POLICY
from test_storage_faults import prepare,admit

def accepted(directory,p,role='author'):
    a=Service(directory,role=role); a.init({'external_work_ref':WORK,'policy_digest':POLICY})
    c=a.submit(json.dumps(p)); assert c['status']=='RECORDED_CANDIDATE',c
    b=Service(directory,role='reviewer'); r=b.review(c['candidate_id'],c['intent_digest'])
    result=admit(b,c,r,p['idempotency_key']); assert result['status']=='DEMO_ADMITTED',result
    return result

def test_append_archive_scope_and_origin(tmp_path):
    r=accepted(tmp_path,package()); claim=r['claim_ids']['one']
    accepted(tmp_path,amendment('share',claim,'applicability',{'branch':'AB'},0,'AB'))
    accepted(tmp_path,amendment('comment',claim,'comment',{'text':'Exact comment\r\n'},1))
    accepted(tmp_path,amendment('link',claim,'link',{'url':'https://example.invalid/%20?q=é','locator':'p1'},2))
    accepted(tmp_path,amendment('prop',claim,'property',{'name':'confidence','value':'1.2300e-40'},3))
    accepted(tmp_path,amendment('archive',claim,'archive',{},4))
    a=Service(tmp_path)
    aa=a.query('AA'); ab=a.query('AB')
    assert aa['claims'][0]['archived'] is True
    assert ab['claims'][0]['archived'] is False
    assert ab['claims'][0]['origin_branch']=='AA'
    assert ab['claims'][0]['origin_version']=='synthetic-artifact-v1'
    assert len(aa['history'])==5
    with a.store.read() as c:
        for table in ('claims','events','reviews','candidates','transactions','idempotency','outbox','binding'):
            for op in (f'UPDATE {table} SET '+('raw=raw' if table=='claims' else 'payload=payload' if table in ('events','reviews','candidates','outbox') else 'receipt=receipt' if table=='transactions' else 'result=result' if table=='idempotency' else 'policy=policy'), f'DELETE FROM {table}'):
                with pytest.raises(sqlite3.IntegrityError,match='IMMUTABLE'): c.execute(op)
    bad=amendment('body',claim,'property',{'name':'body_b64','value':'tamper'},5)
    assert a.submit(json.dumps(bad))['status']=='REJECTED'

def test_scope_before_query_export_and_trace(tmp_path):
    accepted(tmp_path,package())
    limited=Service(tmp_path,branches=('AA',))
    for branch in ('AB','ZZ'):
        assert limited.query(branch)=={'status':'SCOPE_DENIED'}
        assert limited.trace(branch)=={'status':'SCOPE_DENIED'}
        assert limited.export(branch)=={'status':'SCOPE_DENIED'}
        assert limited.sync_status(branch)=={'status':'SCOPE_DENIED'}
    assert limited.trace('master')['readiness']=='UNKNOWN'
    assert not (tmp_path/'exports').exists()

def test_trace_coverage_pending_convergence_and_ack(tmp_path):
    r=accepted(tmp_path,package())
    a=Service(tmp_path); trace=a.trace('master')
    assert trace['ready_for_owner_review'] is False
    assert any(x['requirement_ref']=='R2' and 'MISSING_COVERAGE' in x['reasons'] for x in trace['residual'])
    accepted(tmp_path,package('aa2',revision=1,items=[item('two',requirements=['R2'])]))
    accepted(tmp_path,package('ab','AB',items=[item('ab',branches=['AB'],requirements=['R1','R2'])]))
    accepted(tmp_path,amendment('ca','','converge',{},2))
    accepted(tmp_path,amendment('cb','','converge',{},1,'AB'))
    assert a.trace('master')['ready_for_owner_review'] is False
    b=Service(tmp_path,role='reviewer')
    assert b.sync('AA')['status']=='SYNCED'
    assert b.sync('AB')['status']=='SYNCED'
    assert a.trace('master')['ready_for_owner_review'] is True
    assert a.trace('master')['status']=='ready_for_owner_review'
    assert 'close' not in (tmp_path/'omh-target.json').read_text()

def test_historical_yaml_failure_recovery(tmp_path):
    accepted(tmp_path,package())
    a=Service(tmp_path); first=a.export('AA',1)
    assert first['status']=='EXPORTED'
    old=(tmp_path/first['handle']).read_bytes()
    accepted(tmp_path,package('two',revision=1))
    assert a.export('AA',1)['sha256']==first['sha256']
    assert (tmp_path/first['handle']).read_bytes()==old
    # Physical I/O failure: server-fixed export directory replaced by a file in a separate run.
    broken=tmp_path/'broken'; accepted(broken,package())
    (broken/'exports').write_text('not a directory')
    s=Service(broken,role='reviewer'); result=s.sync('AA')
    assert result['status']=='SYNC_PENDING'
    assert any(x['kind']=='YAML_EXPORT' and x['state']!='ack' for x in s.sync_status('AA')['intents'])
    (broken/'exports').unlink(); assert s.sync('AA')['status']=='SYNCED'

def test_omh_failure_ambiguous_and_reconcile(tmp_path):
    accepted(tmp_path,package()); b=Service(tmp_path,role='reviewer')
    b.omh_mode='unavailable'
    assert b.sync('AA')['status']=='SYNC_PENDING'
    b.omh_mode='ambiguous'
    assert b.sync('AA')['status']=='SYNC_PENDING'
    assert any(x['state']=='ambiguous' for x in b.sync_status('AA')['intents'])
    assert Service(tmp_path,role='reviewer').sync('AA')['status']=='SYNCED'
    with b.store.read() as c: assert c.execute('SELECT count(*) FROM transactions').fetchone()[0]==1

def test_stale_conflict_and_owner_exclusion(tmp_path):
    r=accepted(tmp_path,package(deps={'AB':0}))
    accepted(tmp_path,package('ab','AB',items=[item(branches=['AB'])]))
    a=Service(tmp_path)
    assert any('STALE_CHECK' in x['reasons'] for x in a.trace('master')['residual'])
    accepted(tmp_path,amendment('conflict',r['claim_ids']['one'],'conflict',{'conflict_ref':'C1'},1))
    assert 'CONFLICT' in a.trace('AA')['blockers']
    bad=amendment('exclude','','exclude',{'branch':'AB'},2)
    assert a.submit(json.dumps(bad))['status']=='OWNER_AUTHORITY_REQUIRED'
    accepted(tmp_path,bad,role='owner')
    assert a.trace('master')['excluded_branches']==['AB']
