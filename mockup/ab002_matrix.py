"""Evidence-producing E2E matrix; expected data is never used as actual."""
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
import uuid
from .ab002_e2e import MCP,OUT,ROOT,save,seed,readback
from .fixtures import WORK,POLICY,package,item
from .dom_contract import canonical,digest


def prepare(d,p):
    with MCP(d,role='author') as c:
        assert c.call('dom_init',external_work_ref=WORK,policy_digest=POLICY)['status']=='INITIALIZED'
        candidate=c.call('dom_submit',payload_json=json.dumps(p))
        assert candidate['status']=='RECORDED_CANDIDATE',candidate
    with MCP(d) as c:
        review=c.call('dom_review',candidate_id=candidate['candidate_id'],intent_digest=candidate['intent_digest'])
    return dict(candidate_id=candidate['candidate_id'],review_id=review['review_id'],intent_digest=candidate['intent_digest'],idempotency_key='admit-'+p['idempotency_key'])


def check_target(d):
    with sqlite3.connect(d/'dom.sqlite3') as c:
        c.row_factory=sqlite3.Row
        intents=[dict(r) for r in c.execute("SELECT * FROM outbox WHERE kind='OMH_EVIDENCE'")]
    target=json.loads((d/'omh-target.json').read_text(encoding='utf8')) if (d/'omh-target.json').exists() else {}
    writes=[json.loads(x) for x in (d/'omh-writes.jsonl').read_text(encoding='utf8').splitlines()] if (d/'omh-writes.jsonl').exists() else []
    for i in intents:
        assert target.get(i['target'],{}).get(i['tx'])=={'digest':i['digest'],'payload':json.loads(i['payload'])},(i,target)
        assert sum(w['tx']==i['tx'] and w['target']==i['target'] for w in writes)==1,writes
    assert sum(len(x) for x in target.values())==len(intents),(target,intents)
    return {'target':target,'physical_write_log':writes,'intent_count':len(intents)}


def recover(d,branches=('AA',)):
    with MCP(d) as c:
        resumed={b:c.call('dom_resume',branch=b) for b in branches}
        sync={b:c.call('dom_sync',branch=b) for b in branches}
        for r in sync.values(): assert r['status']=='SYNCED',r
        states={b:c.call('dom_sync_status',branch=b) for b in branches}
        assert all(i['state']=='ack' and i['observed_id'] for s in states.values() for i in s['intents']),states
    return {'resume':resumed,'sync':sync,'status':states,'target_readback':check_target(d)}


def normal(d):
    with MCP(d,role='author') as c:
        assert c.call('dom_init',external_work_ref=WORK,policy_digest=POLICY)['status']=='INITIALIZED'
        empty=c.call('dom_resume',branch='AA')
        assert empty['snapshot']['revision']==0 and not empty['trace']['ready_for_owner_review'],empty
    a=seed(d)
    before=readback(d,'accepted-AA')
    b=seed(d,package('ab','AB',items=[item('ab',branches=['AB'])]))
    after=readback(d,'accepted-AB')
    for t in ('claims','events','claim_snapshots','transactions','outbox'):
        assert all(row in after['tables'][t] for row in before['tables'][t]),t
    recovered=recover(d,('AA','AB'))
    return {'initial_empty':empty,'AA':a,'AB':b,'recovery':recovered}


def crash_admit(d,stage,existing):
    if existing: seed(d)
    args=prepare(d,package('crash',revision=1 if existing else 0))
    before=readback(d,'before-crash')
    with MCP(d,crash=stage) as c:
        actual=c.call('dom_admit',**args)
        assert actual=={'process_exit':71},actual
        crash_pid=c.p.pid
    after=readback(d,'after-crash')
    expected=len(before['tables']['transactions'])+(stage=='after_commit')
    assert len(after['tables']['transactions'])==expected,(expected,after)
    assert not (d/'omh-target.json').exists()
    with MCP(d) as c:
        assert c.p.pid!=crash_pid
        resumed=c.call('dom_resume',branch='AA')
        admitted=c.call('dom_admit',**args)
        assert admitted['status']=='DEMO_ADMITTED',admitted
        assert all(i['state']!='ack' for i in resumed['sync']['intents']),resumed
    return {'crash':actual,'crash_pid':crash_pid,'reopened':resumed,'admitted':admitted,'recovery':recover(d)}


def crash_sync(d,stage):
    seed(d)
    readback(d,'before-crash')
    with MCP(d,crash=stage) as c:
        result=c.call('dom_sync',branch='AA')
        assert result=={'process_exit':71},result
        pid=c.p.pid
    after=readback(d,'after-crash')
    with MCP(d) as c:
        assert c.p.pid!=pid
        status=c.call('dom_sync_status',branch='AA')
        kind='OMH_EVIDENCE' if stage=='after_external_send' else 'YAML_EXPORT'
        assert any(i['kind']==kind and i['state']!='ack' for i in status['intents']),status
    if stage=='before_rename': assert any(x.endswith('.tmp') for x in after['files']) and not any(x.endswith('.yaml') for x in after['files'])
    if stage=='after_rename': assert any(x.endswith('.yaml') for x in after['files'])
    return {'crash':result,'pid':pid,'status_before_reconcile':status,'recovery':recover(d)}


def bad_target(d,mode):
    seed(d)
    with MCP(d,mode=mode) as c:
        result=c.call('dom_sync',branch='AA'); status=c.call('dom_sync_status',branch='AA'); trace=c.call('dom_trace',branch='AA')
        assert result['status']=='SYNC_PENDING' and not trace['ready_for_owner_review'],(result,trace)
        assert next(i for i in status['intents'] if i['kind']=='OMH_EVIDENCE')['state']!='ack',status
    if mode!='ambiguous': assert not (d/'omh-target.json').exists()
    readback(d,'after-failure')
    return {'sync':result,'sync_status':status,'trace':trace,'recovery':recover(d)}


def locked(d):
    seed(d)
    command=[sys.executable,'-B','-m','mockup.ab002_lock',str(d)]
    process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    deadline=time.monotonic()+10
    try:
        while not (d/'lock-ready.json').exists():
            if process.poll() is not None or time.monotonic()>deadline: raise RuntimeError('lock process failed')
            time.sleep(.02)
        with MCP(d) as c:
            busy=c.call('dom_sync',branch='AA')
            assert busy['status']=='STORAGE_BUSY' and busy['error']['sqlite_code']==sqlite3.SQLITE_BUSY,busy
            pids=[process.pid,c.p.pid]
    finally:
        (d/'lock-release').write_text('release',encoding='utf8')
        stdout,stderr=process.communicate(timeout=15)
        save(d/'lock-process.json',{'pid':process.pid,'command':command,'exit_code':process.returncode,'stdout':stdout.decode(),'stderr':stderr.decode()})
    assert process.returncode==0
    return {'pids':pids,'busy':busy,'recovery':recover(d)}


def mismatch(d):
    seed(d)
    recover(d)
    before=readback(d,'before-mismatch')
    with MCP(d,role='author') as c:
        p=package(items=[item(raw=b'changed exact bytes')])
        refused=c.call('dom_submit',payload_json=json.dumps(p))
        assert refused['status']=='IDEMPOTENCY_MISMATCH',refused
    after=readback(d,'after-mismatch')
    assert before==after
    return {'refusal':refused,'unchanged_exact':True}


def spoof(d):
    seed(d)
    seed(d,package('ab','AB',items=[item('ab',branches=['AB'])]))
    before=readback(d,'before-spoof')
    with MCP(d,role='author') as c:
        results=[c.call('dom_review',candidate_id='missing',intent_digest='missing'),c.call('dom_sync',branch='AA'),
                 c.call('dom_sync',branch='AA',role='reviewer'),c.call('dom_query',branch='ZZ'),
                 c.call('delivery',intent='forged',state='ack',payload={})]
        assert [r['status'] for r in results]==['INDEPENDENCE_NOT_ENFORCED','INDEPENDENCE_NOT_ENFORCED','INVALID_ARGUMENTS','SCOPE_DENIED','UNKNOWN_TOOL'],results
        incomplete=c.call('dom_submit',payload_json=json.dumps(package(items=[{}])))
        assert incomplete['status']=='REJECTED' and incomplete['accepted_count']==0 and incomplete['errors'],incomplete
    assert before==readback(d,'after-spoof')
    return {'refusals':results,'incomplete':incomplete,'unchanged_exact':True}


def broken(d,kind,multiple=False):
    seed(d)
    if multiple: seed(d,package('ab','AB',items=[item('ab',branches=['AB'])]))
    # Disposable injection bypasses the file-owner boundary; record the exact change.
    with sqlite3.connect(d/'dom.sqlite3') as c:
        c.row_factory=sqlite3.Row
        row=dict(c.execute('SELECT * FROM events LIMIT 1').fetchone())
        c.execute('DROP TRIGGER immutable_events_UPDATE')
        if kind=='envelope':
            payload=json.loads(row['payload']); payload.pop('value')
            h=digest({'previous':row['previous_hash'],'payload':payload,'tx':row['tx'],'branch':row['branch']})
            c.execute('UPDATE events SET payload=?,event_hash=? WHERE seq=?',(canonical(payload),h,row['seq']))
        else: c.execute("UPDATE events SET event_hash=? WHERE seq=?",('f'*64,row['seq']))
    save(d/'injection.json',{'table':'events','seq':row['seq'],'kind':kind,'trigger_bypassed':'immutable_events_UPDATE','original_payload_hex':bytes(row['payload']).hex()})
    before=readback(d,'after-injection')
    with MCP(d) as c:
        tools=('dom_query','dom_trace','dom_resume','dom_export','dom_sync','dom_sync_status')
        results={b+':'+name:c.call(name,branch=b) for b in (('AA','AB') if multiple else ('AA',)) for name in tools}
        assert all(r['status']=='CHAIN_BROKEN' and not r['ready_for_owner_review'] for r in results.values()),results
        assert all(r['chain']['broken_at_seq']==row['seq'] for r in results.values())
    after=readback(d,'after-refusals')
    assert before==after and not after['files']
    return {'responses':results,'unchanged_exact':True}


def refused_sql(d,c,sql,params,expected,label):
    """Require a specific trigger refusal AND exact rows/file bytes after rollback."""
    before=readback(d,label+'-before')
    try:
        c.execute(sql,params)
    except sqlite3.IntegrityError as error:
        actual=str(error); code=error.sqlite_errorcode; name=error.sqlite_errorname
    else:
        c.rollback()
        raise AssertionError((label,'SQL was not refused'))
    c.rollback()
    after=readback(d,label+'-after')
    assert before==after,(label,'historical bytes/rows changed')
    assert code==sqlite3.SQLITE_CONSTRAINT_TRIGGER,(label,code,actual)
    assert actual in expected,(label,actual,expected)
    return {'label':label,'sql':sql,'parameters':[{'blob_hex':v.hex()} if isinstance(v,bytes) else v for v in params],
            'actual':actual,'sqlite_code':code,'sqlite_name':name,'expected_diagnostics':sorted(expected),
            'before_ref':label+'-before.json','after_ref':label+'-after.json',
            'database_sha256':after['database_sha256'],'unchanged_exact':True}


def immutable(d):
    from .admission import Service
    from .storage import IMMUTABLE
    from .delivery import KEYS
    seed(d); recover(d)
    with sqlite3.connect(d/'dom.sqlite3') as c:
        c.execute("INSERT INTO delivery_events(intent,state,payload) SELECT id,'pending','{}' FROM outbox LIMIT 1")
    before=readback(d,'before-immutable')
    probes=[]
    with sqlite3.connect(d/'dom.sqlite3') as c:
        for table in IMMUTABLE+tuple(KEYS):
            row=c.execute('SELECT * FROM '+table+' LIMIT 1').fetchone()
            assert row is not None,table
            cols=[r[1] for r in c.execute('PRAGMA table_info('+table+')')]
            placeholders=','.join('?' for _ in row)
            insert='INSERT INTO '+table+' VALUES('+placeholders+')'
            statements=[('UPDATE','UPDATE '+table+' SET '+cols[0]+'='+cols[0],()),
                        ('DELETE','DELETE FROM '+table,()),
                        ('REPLACE',insert.replace('INSERT INTO','INSERT OR REPLACE INTO'),row),
                        ('IGNORE',insert.replace('INSERT INTO','INSERT OR IGNORE INTO'),row),
                        ('UPSERT',insert+' ON CONFLICT DO UPDATE SET '+cols[0]+'=excluded.'+cols[0],row),
                        ('DUPLICATE',insert,row)]
            for verb,sql,params in statements:
                expected={'IMMUTABLE'}
                # Replaying an old event cannot extend the current chain. Its
                # BEFORE INSERT guard may run before the duplicate-key guard.
                if table=='events' and verb in ('REPLACE','IGNORE','UPSERT','DUPLICATE'):
                    head=c.execute('SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()[0]
                    assert row[cols.index('previous_hash')]!=head
                    expected.add('CHAIN_INTEGRITY')
                if table=='delivery_events' and verb in ('REPLACE','IGNORE','UPSERT','DUPLICATE') and row[cols.index('state')]=='ack':
                    expected.add('ACK_REQUIRES_OBSERVED')
                probe=refused_sql(d,c,sql,params,expected,table+'-'+verb)
                probes.append(dict(probe,table=table,verb=verb))
                save(d/'immutable-probes.json',probes)
            for index in c.execute('PRAGMA index_list('+table+')').fetchall():
                if not index[2]: continue
                keys=[r[2] for r in c.execute('PRAGMA index_info('+index[1]+')')]
                # A conflict through each unique index while changing non-index identity.
                values=list(row)
                for identity in ('id','intent','seq','claim_id'):
                    if identity in cols and identity not in keys:
                        pos=cols.index(identity); values[pos]=999999 if identity=='seq' or table=='binding' else str(uuid.uuid4()); break
                else: continue
                expected={'IMMUTABLE'}
                if table=='events':
                    assert values[cols.index('previous_hash')]!=c.execute('SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()[0]
                    expected.add('CHAIN_INTEGRITY')
                probe=refused_sql(d,c,insert.replace('INSERT INTO','INSERT OR REPLACE INTO'),values,expected,table+'-SECONDARY-'+index[1])
                probes.append(dict(probe,table=table,verb='SECONDARY_REPLACE',key=keys))
                save(d/'immutable-probes.json',probes)
        intent=c.execute('SELECT id,tx,digest,target FROM outbox LIMIT 1').fetchone()
        bad=[("INSERT INTO delivery_acks VALUES(?,?,?,?,?)",(intent[0],'missing-observation',*intent[1:])),
             ("INSERT INTO delivery_events(intent,state,payload) VALUES(?,'ack','{}')",(intent[0],))]
        for n,(sql,params) in enumerate(bad):
            expected={'ACK_REQUIRES_OBSERVED','IMMUTABLE'} if n==0 else {'ACK_REQUIRES_OBSERVED'}
            probes.append(refused_sql(d,c,sql,params,expected,'forged-ack-'+str(n)))
    # Public helper cannot be used to assign state, even with reviewer capability.
    author=Service(d); reviewer=Service(d,role='reviewer')
    public=[author.delivery(intent[0],'ack',{}),reviewer.delivery(intent[0],'ack',{})]
    assert [r['status'] for r in public]==['INDEPENDENCE_NOT_ENFORCED','DELIVERY_ENGINE_ONLY'],public
    after=readback(d,'after-immutable')
    assert before==after
    with MCP(d) as c:
        trace=c.call('dom_trace',branch='AA'); query=c.call('dom_query',branch='AA')
        assert query['claims'][0]['origin_branch']=='AA' and trace['chain']['status']=='CHAIN_OK'
    return {'probes':probes,'probe_count':len(probes),'public_delivery':public,'unchanged_exact':True,'trace':trace,'target':check_target(d)}


def parallel(d,initial):
    seed(d)
    seed(d,package('ab','AB',items=[item('ab',branches=['AB'])]))
    if initial=='ambiguous':
        with MCP(d,mode='ambiguous') as c:
            for b in ('AA','AB'): assert c.call('dom_sync',branch=b)['status']=='SYNC_PENDING'
    before=readback(d,'before-parallel')
    import threading
    barrier=threading.Barrier(2)
    with MCP(d) as a, MCP(d) as b:
        def worker(client):
            barrier.wait(timeout=10)
            return {'pid':client.p.pid,'sync':{branch:client.call('dom_sync',branch=branch) for branch in ('AA','AB')}}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(worker,c) for c in (a,b)]
            results=[f.result(timeout=60) for f in futures]
        assert a.p.pid!=b.p.pid
        assert all(r['status'] in ('SYNCED','STORAGE_BUSY') for x in results for r in x['sync'].values()),results
    recovery=recover(d,('AA','AB'))
    after=readback(d,'after-parallel')
    for table in ('claims','transactions','events','outbox','claim_snapshots'):
        assert before['tables'][table]==after['tables'][table],table
    return {'concurrent':results,'recovery':recovery,'immutable_facts_unchanged':True}


def errors(d,kind):
    seed(d)
    before=readback(d,'before-error')
    if kind=='unavailable':
        db=d/'dom.sqlite3'; saved=d/'saved-dom.sqlite3'; blocked=d/'blocked-directory'
        db.rename(saved); db.mkdir()
        try:
            with MCP(d) as c: result=c.call('dom_query',branch='AA')
            assert result['status']=='STORAGE_UNAVAILABLE',result
            # SQLite on Windows reports the precise directory subtype (526),
            # not only primary CANTOPEN (14); require the exact code/name pair.
            assert (result['error']['sqlite_code'],result['error']['sqlite_name']) in (
                (sqlite3.SQLITE_CANTOPEN,'SQLITE_CANTOPEN'),
                (sqlite3.SQLITE_CANTOPEN_ISDIR,'SQLITE_CANTOPEN_ISDIR')),result
            save(d/'unavailable-response.json',result)
        finally:
            db.rename(blocked); saved.rename(db)
        assert before==readback(d,'after-restore')
        return {'response':result,'injection':'Temporarily replace disposable DB pathname with directory; saved exact original restored',
                'unchanged_exact_after_restore':True,'recovery':recover(d)}
    if kind=='corrupt':
        (d/'dom.sqlite3').write_bytes(b'AB002 disposable invalid sqlite bytes')
        with MCP(d) as c:
            result=c.call('dom_query',branch='AA')
        assert result['status']=='STORAGE_CORRUPT' and result['error']['sqlite_code']==sqlite3.SQLITE_NOTADB,result
        return {'response':result,'injection':'Replace disposable DB bytes; original run not touched','recovery':'NOT_TESTED: repair policy UD-03 not selected'}
    with MCP(d,read_only=True) as c:
        result=c.call('dom_sync',branch='AA')
    assert result['status']=='STORAGE_READ_ONLY' and result['error']['sqlite_code']==sqlite3.SQLITE_READONLY,result
    assert before==readback(d,'after-error')
    return {'response':result,'uri':'mode=ro','unchanged_exact':True,'recovery':recover(d)}


def migration(d):
    baseline=OUT/'baseline-a668de14'
    assert (baseline/'dom.sqlite3').exists(),'Original pre-fix baseline missing'
    shutil.copy2(baseline/'dom.sqlite3',d/'dom.sqlite3')
    before=readback(d,'legacy-before')
    with MCP(d) as c:
        refused=c.call('dom_resume',branch='AA')
        assert refused['status']=='MIGRATION_REQUIRED',refused
        initialized=c.call('dom_init',external_work_ref=WORK,policy_digest=POLICY)
        assert initialized['status']=='INITIALIZED',initialized
        pending=c.call('dom_sync_status',branch='AA')
        assert all(i['state']!='ack' for i in pending['intents']),pending
    after=readback(d,'legacy-after-additive')
    for t,rows in before['tables'].items(): assert rows==after['tables'][t],t
    return {'legacy_ref':str(baseline),'before_init':refused,'init':initialized,'after_init_status':pending,'legacy_history_exact':True,'recovery':recover(d)}


def incompatible(d):
    with sqlite3.connect(d/'dom.sqlite3') as c: c.execute('CREATE TABLE old_layout(id TEXT PRIMARY KEY,payload BLOB)')
    before=readback(d,'before-incompatible')
    with MCP(d) as c: result=c.call('dom_init',external_work_ref=WORK,policy_digest=POLICY)
    assert result['status']=='MIGRATION_REQUIRED',result
    assert before==readback(d,'after-incompatible')
    return {'response':result,'unchanged_history':True,'recovery':'No reset or unsupported migration attempted'}


def run():
    from .ab002_binding import binding_negatives
    run_dir=OUT/('matrix-'+uuid.uuid4().hex[:8]); run_dir.mkdir(parents=True)
    if (OUT/'e2e_manifest.json').exists():
        shutil.copy2(OUT/'e2e_manifest.json',run_dir/'previous-manifest.json')
    manifest={'mode':'SIMULATION','live':'NOT_TESTED','entrypoint':'python -B -m mockup.ab002_e2e','run_directory':str(run_dir),'cases':[],
              'omissions':[{'id':'E11','verdict':'NOT_TESTED','reason':'UD-02/06 revalidation policy, outside A'}, {'id':'LIVE','verdict':'NOT_TESTED','reason':'No live OMH contract or authorization; local target is SIMULATION'}]}
    specs=[('E0','S0-S1-S3-AA-AB',normal),
           ('E1','S0-before-commit',lambda d:crash_admit(d,'before_commit',False)),
           ('E1','S1-before-commit',lambda d:crash_admit(d,'before_commit',True)),
           ('E2','S1-after-commit',lambda d:crash_admit(d,'after_commit',True)),
           ('E3','S1-S6-before-rename',lambda d:crash_sync(d,'before_rename')),
           ('E4','S1-S6-after-rename',lambda d:crash_sync(d,'after_rename')),
           ('E5','S1-S2-writer-lock',locked),
           ('E6','S1-unavailable',lambda d:bad_target(d,'unavailable')),
           ('E6','S1-liar',lambda d:bad_target(d,'liar')),
           ('E6','S6-lost-reply',lambda d:bad_target(d,'ambiguous')),
           ('E6','S6-death-after-send',lambda d:crash_sync(d,'after_external_send')),
           ('E7','S1-S2-changed-payload',mismatch),('E8','S3-S5-spoof-incomplete',spoof),
           ('E9','S1-envelope',lambda d:broken(d,'envelope')),('E9','S1-hash',lambda d:broken(d,'hash')),
           ('E9','S1-S3-envelope',lambda d:broken(d,'envelope',True)),('E9','S1-S3-hash',lambda d:broken(d,'hash',True)),
           ('E10','S1-immutable-all-tables',immutable),('A1-A2-A5','S1-S6-binding-negatives',binding_negatives),
           ('E12','S2-S3-pending-parallel',lambda d:parallel(d,'pending')),
           ('E12','S2-S3-S6-ambiguous-parallel',lambda d:parallel(d,'ambiguous')),
           ('A7','S1-corrupt-database',lambda d:errors(d,'corrupt')),
           ('A7','S1-read-only-database',lambda d:errors(d,'read-only')),
           ('A7','S1-unavailable-database',lambda d:errors(d,'unavailable')),
           ('A9','S1-legacy-additive',migration),('A9','incompatible-layout',incompatible)]
    for case_id,variant,fn in specs:
        d=run_dir/(case_id+'-'+variant); d.mkdir()
        case={'id':case_id,'variant':variant,'mode':'SIMULATION','initial_state':variant,'entrypoint':'raw stdio MCP subprocess via trusted test launcher',
              'injection':variant,'expected':'Contracted refusal/recovery with no false ack, no loss or duplicate and physical target read-back',
              'verdict':'NOT_TESTED','actual':None,'evidence_paths':[str(d)],'final_readback':None,'recovery':None}
        manifest['cases'].append(case); save(OUT/'e2e_manifest.json',manifest)
        try:
            case['actual']=fn(d)
            case['final_readback']=readback(d,'final')
            case['recovery']=case['actual'].get('recovery','No recovery mutation required for this negative case')
            case['verdict']='PASS'
        except Exception as error:
            case['verdict']='FAIL'; case['actual']={'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()}
        save(d/'case.json',case); save(OUT/'e2e_manifest.json',manifest)
        print(case_id,variant,case['verdict'],flush=True)
    manifest['coverage']={v:sum(c['verdict']==v for c in manifest['cases']) for v in ('PASS','FAIL','NOT_TESTED')}
    save(OUT/'e2e_manifest.json',manifest); save(run_dir/'manifest.json',manifest)
    print(json.dumps(manifest['coverage']),str(run_dir),flush=True)
    if manifest['coverage']['FAIL']: raise SystemExit(1)
