"""Physical process/race tests; all databases and IPC artifacts under runtime."""
import json
import multiprocessing as mp
import os
from pathlib import Path
import pytest
from mockup.admission import Service
from mockup.fixtures import package,item,WORK,POLICY

def prepare(directory,p):
    a=Service(directory); a.init({'external_work_ref':WORK,'policy_digest':POLICY})
    candidate=a.submit(json.dumps(p)); b=Service(directory,role='reviewer')
    review=b.review(candidate['candidate_id'],candidate['intent_digest'])
    return candidate,review

def admit(b,c,r,key='admit'):
    return b.admit(c['candidate_id'],r['review_id'],key,c['intent_digest'])

def worker(directory,c,r,key,barrier=None,death=None):
    b=Service(directory,role='reviewer')
    def hook(stage):
        if stage==death:
            Path(directory,f'{key}.death.json').write_text(json.dumps({'pid':os.getpid(),'stage':stage}),encoding='utf8')
            os._exit(71)
    b.fault_hook=hook
    if barrier: barrier.wait(timeout=15)
    result=admit(b,c,r,key)
    Path(directory,f'{key}.result.json').write_text(json.dumps(result),encoding='utf8')

def counts(directory):
    with Service(directory).store.read() as c:
        return {t:c.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('claims','events','transactions','outbox','idempotency')}|{'head':c.execute("SELECT revision FROM branch_heads WHERE branch='AA'").fetchone()[0]}

def joined(p):
    p.join(20)
    if p.is_alive(): p.terminate(); p.join(5); pytest.fail('child timeout')

@pytest.mark.parametrize('death',['after_facts','before_commit','after_commit'])
def test_actual_death_reopen(tmp_path,death):
    c,r=prepare(tmp_path,package())
    before=counts(tmp_path)
    ctx=mp.get_context('spawn'); p=ctx.Process(target=worker,args=(str(tmp_path),c,r,'death',None,death)); p.start(); joined(p)
    assert p.exitcode==71
    assert json.loads((tmp_path/'death.death.json').read_text())['stage']==death
    after=counts(tmp_path)
    if death!='after_commit': assert after==before
    else:
        assert after['claims']==1 and after['head']==1 and after['outbox']==2
        b=Service(tmp_path,role='reviewer'); replay=admit(b,c,r,'death')
        assert replay['status']=='DEMO_ADMITTED'
        assert admit(Service(tmp_path,role='reviewer'),c,r,'death')==replay
        assert counts(tmp_path)==after
        # WS-F02 L1 checks candidate-vs-intent digest before the cache lookup, so a
        # different intent is a DIGEST_MISMATCH (never an idempotency oracle).
        assert b.admit(c['candidate_id'],r['review_id'],'death','different')['status']=='DIGEST_MISMATCH'
    (tmp_path/'readback.json').write_text(json.dumps({'before':before,'after':after,'exit_code':p.exitcode,'pid':p.pid}),encoding='utf8')

def test_two_process_race(tmp_path):
    c1,r1=prepare(tmp_path,package('one')); c2,r2=prepare(tmp_path,package('two'))
    ctx=mp.get_context('spawn'); barrier=ctx.Barrier(2)
    processes=[ctx.Process(target=worker,args=(str(tmp_path),c,r,key,barrier)) for c,r,key in [(c1,r1,'one'),(c2,r2,'two')]]
    try:
        for p in processes: p.start()
        for p in processes: joined(p); assert p.exitcode==0
    finally:
        for p in processes:
            if p.is_alive(): p.terminate(); p.join(5)
    results=[json.loads((tmp_path/f'{k}.result.json').read_text()) for k in ('one','two')]
    assert sorted(r['status'] for r in results)==['DEMO_ADMITTED','REVISION_CONFLICT']
    state=counts(tmp_path); assert state['claims']==state['events']==state['transactions']==state['head']==1
    (tmp_path/'race.json').write_text(json.dumps({'processes':[p.pid for p in processes],'results':results,'state':state}),encoding='utf8')

def test_unrelated_branch_and_stale_dependency(tmp_path):
    aa,ar=prepare(tmp_path,package('aa'))
    dep,dr=prepare(tmp_path,package('dep',deps={'AB':0}))
    ab,br=prepare(tmp_path,package('ab','AB',items=[item(branches=['AB'])]))
    b=Service(tmp_path,role='reviewer')
    assert admit(b,ab,br,'ab')['status']=='DEMO_ADMITTED'
    assert admit(b,dep,dr,'dep')['status']=='STALE_REVIEW'
    assert admit(b,aa,ar,'aa')['status']=='DEMO_ADMITTED'

def test_digest_and_revision_bound_review(tmp_path):
    c,r=prepare(tmp_path,package())
    b=Service(tmp_path,role='reviewer')
    before=counts(tmp_path)
    assert b.admit(c['candidate_id'],r['review_id'],'bad','bad')['status']=='DIGEST_MISMATCH'
    assert counts(tmp_path)==before
    c2,r2=prepare(tmp_path,package('other'))
    assert admit(b,c,r)['status']=='DEMO_ADMITTED'
    assert admit(b,c2,r2,'second')['status']=='REVISION_CONFLICT'
