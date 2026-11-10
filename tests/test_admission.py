import json
from mockup.admission import Service
from mockup.fixtures import WORK,POLICY,package

def init(s): return s.init({'external_work_ref':WORK,'policy_digest':POLICY})

def test_persistent_tracer(tmp_path):
    a=Service(tmp_path)
    assert init(a)['status']=='INITIALIZED'
    c=a.submit(json.dumps(package()))
    assert c['status']=='RECORDED_CANDIDATE'
    assert a.query('AA')['claims']==[]
    assert a.review(c['candidate_id'],c['intent_digest'])['status']=='INDEPENDENCE_NOT_ENFORCED'
    b=Service(tmp_path,role='reviewer')
    r=b.review(c['candidate_id'],c['intent_digest'])
    assert r['status']=='DEMO_REVIEWED'
    result=b.admit(c['candidate_id'],r['review_id'],'admit-1',c['intent_digest'])
    assert result['status']=='DEMO_ADMITTED' and result['simulated'] is True
    assert len(Service(tmp_path).query('AA')['claims'])==1
