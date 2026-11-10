"""Restricted dom-c14n/v1: NOT JCS; exact strings and source bytes."""
import base64
import hashlib
import json
MAX_INT=9007199254740991
ENVELOPE={'external_work_ref','external_task_ref','branch','expected_branch_revision','schema_version','policy_digest','idempotency_key','operation','items','dependencies','origin_version','reason'}
COMMON={'local_id':str,'content_type':str,'body_b64':str,'encoding':str,'media_type':str,'reason':str,'applicability':list,'metadata':dict,'requirement_refs':list}
TYPE_FIELDS={
 'quote':{'source_ref':str,'source_snapshot_digest':str,'locator':str,'source_b64':str},
 'decision':{'attribution':str,'rationale':str,'assumptions':list,'alternatives':list},
 'formula':{'expression':str,'notation':dict,'assumptions':list,'units':dict,'derivation_refs':list},
 'code':{'repository_ref':str,'relative_path':str,'language':str,'snapshot_digest':str,'locator':str,'dirty':bool},
 'data':{'artifact_ref':str,'artifact_digest':str,'method':str,'columns':dict,'units':dict,'provenance':str},
 'concept':{'definition':str,'scope':str,'assumptions':list,'attribution':str,'links':list},
 'text':{'classification':str,'evidence':list,'attribution':str,'assumptions':list}}
EVENTS={'comment','link','property','applicability','archive','replacement','conflict','resolve','converge','exclude'}
EVENT_FIELDS={'local_id':str,'event_type':str,'claim_ref':str,'reason':str,'value':dict,'supersedes':str,'ref':str}

def check_tree(v):
    if isinstance(v,str):
        if any(0xD800<=ord(c)<=0xDFFF for c in v): raise ValueError('INVALID_UNICODE')
    elif type(v) is int:
        if not 0<=v<=MAX_INT: raise ValueError('INVALID_NUMBER')
    elif type(v) in (list,dict):
        if isinstance(v,dict) and any(type(k) is not str or not k.isascii() for k in v): raise ValueError('INVALID_KEY')
        for x in (v.values() if isinstance(v,dict) else v): check_tree(x)
    elif v is not None and type(v) is not bool: raise ValueError('INVALID_TYPE')

def strict_loads(text):
    def pairs(kvs):
        d={}
        for k,v in kvs:
            if k in d: raise ValueError('DUPLICATE_KEY')
            d[k]=v
        return d
    def reject(_): raise ValueError('INVALID_NUMBER')
    v=json.loads(text,object_pairs_hook=pairs,parse_float=reject,parse_constant=reject)
    check_tree(v)
    return v

def canonical(v):
    check_tree(v)
    return json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')
def digest(v): return hashlib.sha256(canonical(v)).hexdigest()
def raw_hash(b): return hashlib.sha256(b).hexdigest()
def decode(s):
    if type(s) is not str: raise ValueError('INVALID_ENCODING')
    try: b=base64.b64decode(s,validate=True)
    except Exception: raise ValueError('INVALID_ENCODING') from None
    if base64.b64encode(b).decode()!=s: raise ValueError('INVALID_ENCODING')
    return b

def normalized(p,principal,root):
    p=strict_loads(canonical(p).decode()); p.pop('idempotency_key',None)
    p.update(author_principal=principal,author_root=root)
    p['items']=sorted(p['items'],key=lambda x:x['local_id'])
    for i in p['items']:
        for k in ('applicability','requirement_refs'):
            if k in i: i[k]=sorted(i[k])
    p['dependencies']=dict(sorted(p['dependencies'].items()))
    return p

def validate(p,branches=('AA','AB')):
    errors=[]
    def err(local,path,code='MISSING_FIELD',required=True): errors.append(dict(local_id=local,path=path,code=code,required=required,fix='Supply schema-conforming field; no coercion.'))
    def fields(o,spec,local,prefix):
        if type(o) is not dict: err(local,prefix,'INVALID_TYPE'); return
        for k,t in spec.items():
            if k not in o: err(local,prefix+'.'+k)
            elif type(o[k]) is not t or t is str and not o[k] and k not in ('supersedes','claim_ref'): err(local,prefix+'.'+k,'INVALID_TYPE')
        for k in o.keys()-spec.keys(): err(local,prefix+'.'+k,'UNKNOWN_FIELD',False)
    if type(p) is not dict: err(None,'$','INVALID_TYPE'); return errors
    spec={k:str for k in ENVELOPE}; spec.update(items=list,dependencies=dict,expected_branch_revision=int)
    fields(p,spec,None,'$')
    if type(p.get('expected_branch_revision')) is int and not 0<=p['expected_branch_revision']<=MAX_INT: err(None,'$.expected_branch_revision','INVALID_TYPE')
    if p.get('schema_version')!='dom/v1': err(None,'$.schema_version','INVALID_TYPE')
    if p.get('operation') not in ('claims','append'): err(None,'$.operation','INVALID_TYPE')
    deps=p.get('dependencies')
    if type(deps) is dict and any(k not in branches or type(v) is not int or v<0 for k,v in deps.items()): err(None,'$.dependencies','INVALID_TYPE')
    items=p.get('items',[])
    if type(items) is not list: return errors
    if not items: err(None,'$.items','INVALID_TYPE')
    seen=set()
    for n,i in enumerate(items):
        if type(i) is not dict: err(None,f'items[{n}]','INVALID_TYPE'); continue
        local=i.get('local_id') if type(i.get('local_id')) is str else None
        if local in seen: err(local,'local_id','DUPLICATE_LOCAL_ID')
        seen.add(local)
        if p.get('operation')=='append':
            fields(i,EVENT_FIELDS,local,'item')
            if i.get('event_type') not in EVENTS: err(local,'event_type','INVALID_TYPE')
            ev=i.get('event_type'); value=i.get('value')
            event_specs={'comment':{'text':str},'link':{'url':str,'locator':str},'property':{'name':str,'value':str},'applicability':{'branch':str},'archive':{},'replacement':{'replacement_ref':str},'conflict':{'conflict_ref':str},'resolve':{'conflict_ref':str},'converge':{},'exclude':{'branch':str}}
            if ev in event_specs: fields(value,event_specs[ev],local,'value')
            if ev=='property' and isinstance(value,dict) and value.get('name') in ('body','body_b64','raw','origin_branch','origin_version','claim_id'): err(local,'value.name','IMMUTABLE_FIELD')
            if ev not in ('converge','exclude') and not i.get('claim_ref'): err(local,'claim_ref')
            if ev in ('applicability','exclude') and isinstance(value,dict) and value.get('branch') not in branches: err(local,'value.branch','INVALID_BRANCH')
            continue
        fields(i,COMMON,local,'item'); typ=i.get('content_type'); known=typ in TYPE_FIELDS
        if not known: err(local,'content_type','INVALID_TYPE')
        m=i.get('metadata',{})
        # An unknown content_type is one error for that item, not a reason to stop
        # checking the fields every item shares (body bytes, encoding, applicability).
        if known:
            tspec=dict(TYPE_FIELDS[typ])
            if typ=='code' and isinstance(m,dict) and m.get('dirty') is True: tspec['artifact_manifest']=list
            fields(m,tspec,local,'metadata')
        try:
            raw=decode(i.get('body_b64'))
            if i.get('encoding')!='utf-8': err(local,'encoding','INVALID_ENCODING')
            else: raw.decode('utf-8')
            if typ=='quote' and isinstance(m,dict) and 'source_b64' in m and decode(m['source_b64'])!=raw: err(local,'metadata.source_b64','SOURCE_BYTES_MISMATCH')
        except (ValueError,UnicodeError): err(local,'body_b64','INVALID_ENCODING')
        if isinstance(m,dict):
            if typ=='text' and (m.get('classification') not in ('factual','interpretation') or m.get('classification')=='factual' and not m.get('evidence')): err(local,'metadata.evidence')
            if typ=='formula' and (not m.get('units') or not m.get('notation')): err(local,'metadata.units','MISSING_UNIT')
            if typ=='data' and not m.get('units'): err(local,'metadata.units','MISSING_UNIT')
            if typ=='code' and ('..' in str(m.get('relative_path','')).split('/') or str(m.get('relative_path','')).startswith(('/','\\'))): err(local,'metadata.relative_path','INVALID_TYPE')
        a=i.get('applicability')
        if type(a) is list and (not a or any(x not in branches for x in a) or len(set(a))!=len(a)): err(local,'applicability','INVALID_BRANCH')
    return errors
