"""Owner-provided synthetic inputs, never a task registry or issuer."""
import base64
from ..dom_contract import digest
WORK='demo:existing-work-W1'
TASK='demo:existing-task-AA001'
POLICY=digest({'version':'demo-policy/v1','requirements':['R1','R2'],'branches':['AA','AB']})

def package(key='k1',branch='AA',revision=0,items=None,deps=None):
    return dict(external_work_ref=WORK,external_task_ref=TASK,branch=branch,expected_branch_revision=revision,schema_version='dom/v1',policy_digest=POLICY,idempotency_key=key,operation='claims',items=items if items is not None else [item()],dependencies=deps or {},origin_version='synthetic-artifact-v1',reason='synthetic demonstration')

def item(local='one',typ='decision',raw=b'Exact assertion\r\n',branches=None,requirements=None):
    b=base64.b64encode(raw).decode()
    metadata={
      'quote':dict(source_ref='https://example.invalid/raw?x=%20',source_snapshot_digest=digest('snapshot'),locator='bytes:0-'+str(len(raw)),source_b64=b),
      'decision':dict(attribution='demo author',rationale='bounded experiment',assumptions=[],alternatives=[]),
      'formula':dict(expression='E = mc^2',notation={'E':'energy','m':'mass','c':'speed'},assumptions=[],units={'E':'J','m':'kg','c':'m/s'},derivation_refs=['author-origin']),
      'code':dict(repository_ref='demo:repo',relative_path='synthetic.py',language='python',snapshot_digest=digest('artifact'),locator='lines:1-2',dirty=False),
      'data':dict(artifact_ref='demo:data',artifact_digest=digest('data'),method='synthetic',columns={'x':'decimal-string'},units={'x':'mol/L'},provenance='fixture'),
      'concept':dict(definition='A synthetic concept',scope='demo',assumptions=[],attribution='author',links=[]),
      'text':dict(classification='factual',evidence=[{'ref':'demo:source','locator':'line:1'}],attribution='author',assumptions=[])}[typ]
    return dict(local_id=local,content_type=typ,body_b64=b,encoding='utf-8',media_type='text/plain',reason='fixture evidence',applicability=branches or ['AA'],metadata=metadata,requirement_refs=requirements if requirements is not None else ['R1'])

def amendment(key,claim,event_type,value,revision,branch='AA',supersedes='',ref='demo:ref'):
    p=package(key,branch,revision)
    p['operation']='append'
    p['items']=[dict(local_id='event',event_type=event_type,claim_ref=claim,reason='audited amendment',value=value,supersedes=supersedes,ref=ref)]
    return p
