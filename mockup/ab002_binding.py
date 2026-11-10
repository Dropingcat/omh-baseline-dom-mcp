"""Trusted disposable SQL injections surrounded by real stdio MCP calls."""
import json
import sqlite3
import uuid
from .ab002_e2e import MCP,seed,readback,save
from .dom_contract import canonical,raw_hash


def binding_negatives(d):
    from .ab002_matrix import refused_sql,recover
    seed(d)
    probes=[]
    with sqlite3.connect(d/'dom.sqlite3') as c:
        i,j=c.execute('SELECT id,tx,digest,target FROM outbox ORDER BY kind').fetchall()
        def probe(label,sql,params,diagnostic):
            probes.append(refused_sql(d,c,sql,params,{diagnostic},label))
            save(d/'binding-probes.json',probes)
        ack_sql='INSERT INTO delivery_acks VALUES(?,?,?,?,?)'
        probe('ack-first',ack_sql,(i[0],'no-observation',*i[1:]),'ACK_REQUIRES_OBSERVED')
        attempt_sql='INSERT INTO delivery_attempts VALUES(?,?,?,?,?,?,?,?)'
        for field,n in [('intent',0),('tx',1),('digest',2),('target',3)]:
            wrong=list(i); wrong[n]=j[n] if j[n]!=i[n] else 'foreign-'+field
            probe('attempt-foreign-'+field,attempt_sql,(str(uuid.uuid4()),*wrong,'fixture','fixture-root','time'),'DELIVERY_BINDING')
        attempt=str(uuid.uuid4())
        c.execute(attempt_sql,(attempt,*i,'fixture','fixture-root','time')); c.commit()
        raw=canonical({'digest':i[2],'payload':json.loads(c.execute('SELECT payload FROM outbox WHERE id=?',(i[0],)).fetchone()[0])})
        obs_sql='INSERT INTO delivery_observations VALUES('+','.join('?' for _ in range(14))+')'
        values=[str(uuid.uuid4()),attempt,*i,1,raw_hash(raw),len(raw),'time','fixture','fixture-root',canonical({'test_fixture':True}),raw]
        for field,n in [('attempt',1),('intent',2),('tx',3),('digest',4),('target',5),('actor',10),('root',11)]:
            wrong=list(values); wrong[0]=str(uuid.uuid4()); wrong[n]='foreign-'+field
            probe('observation-foreign-'+field,obs_sql,wrong,'OBSERVATION_BINDING')
        for field,n,replacement in [('fingerprint',7,'short'),('size',8,len(raw)+1),('read_at',9,''),('snapshot',12,b'not-json')]:
            wrong=list(values); wrong[0]=str(uuid.uuid4()); wrong[n]=replacement
            probe('observation-shape-'+field,obs_sql,wrong,'OBSERVATION_SHAPE')
        unmatched=list(values); unmatched[0]=str(uuid.uuid4()); unmatched[6]=0
        c.execute(obs_sql,unmatched); c.commit()
        probe('ack-unmatched-observation',ack_sql,(i[0],unmatched[0],*i[1:]),'ACK_REQUIRES_OBSERVED')
        attempt2=str(uuid.uuid4()); c.execute(attempt_sql,(attempt2,*i,'fixture','fixture-root','time'))
        matched=list(values); matched[0]=str(uuid.uuid4()); matched[1]=attempt2
        c.execute(obs_sql,matched); c.commit()
        for field,n in [('intent',0),('tx',2),('digest',3),('target',4)]:
            wrong=[i[0],matched[0],*i[1:]]; wrong[n]='foreign-'+field
            probe('ack-foreign-'+field,ack_sql,wrong,'ACK_REQUIRES_OBSERVED')
        probe('ack-absent-observation',ack_sql,(i[0],'absent',*i[1:]),'ACK_REQUIRES_OBSERVED')
        probe('legacy-ack',"INSERT INTO delivery_events(intent,state,payload) VALUES(?,'ack','{}')",(i[0],),'ACK_REQUIRES_OBSERVED')
    before=readback(d,'before-MCP-refusals')
    with MCP(d) as c:
        status=c.call('dom_sync_status',branch='AA'); trace=c.call('dom_trace',branch='AA')
        caller=c.call('delivery',intent=i[0],state='ack',payload={})
        schema=c.rpc('tools/list',{})
        assert all(x['state']!='ack' and not x['observed_id'] for x in status['intents']),status
        assert not trace['ready_for_owner_review'] and caller['status']=='UNKNOWN_TOOL'
        assert 'delivery' not in [t['name'] for t in schema['result']['tools']]
    assert before==readback(d,'after-MCP-refusals')
    assert not (d/'omh-target.json').exists()
    return {'probes':probes,'probe_count':len(probes),'status_before_recovery':status,'trace_before_recovery':trace,
            'public_caller_refusal':caller,'recovery':recover(d)}
