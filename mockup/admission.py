"""Single admission path; model input never supplies authority."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .dom_contract import canonical,digest,raw_hash,decode,strict_loads,validate,normalized
from .fixtures import WORK,TASK,POLICY
from .ports import fixture_context
from .storage import Store,MigrationRequired
from . import delivery as delivery_facts
from . import public_dto
from functools import wraps
from dataclasses import replace as _replace
from . import claim_entry as claim_entry_mod

class IntegrityFailure(Exception):
    def __init__(self,result): self.result=result

def storage_error(error):
    code=getattr(error,'sqlite_errorcode',None)
    primary=code & 255 if code is not None else None
    if primary in (sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED): status='STORAGE_BUSY'
    elif primary in (sqlite3.SQLITE_CORRUPT,sqlite3.SQLITE_NOTADB): status='STORAGE_CORRUPT'
    elif primary==sqlite3.SQLITE_READONLY: status='STORAGE_READ_ONLY'
    elif primary==sqlite3.SQLITE_CONSTRAINT: status='STORAGE_CONSTRAINT'
    elif primary==sqlite3.SQLITE_ERROR and ('no such table' in str(error) or 'no such column' in str(error)): status='MIGRATION_REQUIRED'
    else: status='STORAGE_UNAVAILABLE'
    return {'status':status,'error':{'code':status,'sqlite_code':code,'sqlite_name':getattr(error,'sqlite_errorname',None)}}

class Denied(Exception):
    """Typed refusal.  ``extra`` carries values the caller already owns (own branch
    names, a field name, a claim id) into the public DomainError; it is empty for
    every refusal that existed before WR-ADD."""
    def __init__(self,status,**extra):
        super().__init__(status); self.extra=extra

_UNSET=object()

def guarded(fn):
    @wraps(fn)
    def run(*a,**kw):
        try: return fn(*a,**kw)
        except IntegrityFailure as e: return public_dto.broken(e.result)
        except Denied as e: return dict({'status':str(e)},**e.extra)
        except MigrationRequired as e: return {'status':str(e)}
        except sqlite3.DatabaseError as e: return storage_error(e)
    return run

def verify_chain(c):
    """Recompute the append-only event hash chain.

    Each event stores ``previous_hash`` plus ``event_hash = digest({previous,
    payload, tx, branch})``.  Recomputing them from the stored rows detects
    forged inserts that bypassed the admission path (and shows whether an
    administrator replaced bytes).  No external checkpoint: truncation of the
    whole chain is still out of scope (AA002 immutability clause).
    """
    rows=c.execute('SELECT seq,id,tx,branch,kind,payload,previous_hash,event_hash FROM events ORDER BY seq').fetchall()
    previous='0'*64
    def broken(row,reason):
        return {'status':'CHAIN_BROKEN','events':len(rows),'broken_at_seq':row['seq'],'broken_event_id':row['id'],'reason':reason}
    for row in rows:
        try:
            payload=strict_loads(row['payload'])
            expected=digest({'previous':previous,'payload':payload,'tx':row['tx'],'branch':row['branch']})
        except (ValueError,TypeError,UnicodeError): return broken(row,'EVENT_SHAPE_INVALID')
        if row['previous_hash']!=previous: return broken(row,'PREVIOUS_HASH_MISMATCH')
        if row['event_hash']!=expected: return broken(row,'EVENT_HASH_MISMATCH')
        required={'value':dict,'actor':str,'root':str,'server_time':str,'origin_version':str,'context_revision':int,'reason':str,'review_id':str,'dependencies':dict}
        if type(payload) is not dict or any(type(payload.get(k)) is not t for k,t in required.items()): return broken(row,'EVENT_SHAPE_INVALID')
        value=payload['value']; kind=row['kind']
        if kind=='claim':
            if type(value.get('item')) is not dict or type(value.get('origin_version')) is not str: return broken(row,'EVENT_SHAPE_INVALID')
        else:
            from .dom_contract import EVENTS,EVENT_FIELDS
            if kind not in EVENTS or any(type(value.get(k)) is not t for k,t in EVENT_FIELDS.items()): return broken(row,'EVENT_SHAPE_INVALID')
            fields={'property':('name','value'),'applicability':('branch',),'conflict':('conflict_ref',),'resolve':('conflict_ref',),'exclude':('branch',)}
            if any(type(value['value'].get(k)) is not str for k in fields.get(kind,())): return broken(row,'EVENT_SHAPE_INVALID')
        previous=row['event_hash']
    return {'status':'CHAIN_OK','events':len(rows),'head_hash':previous}

def claim_snapshot_gaps(c):
    """Claim ids that have no immutable dependency snapshot (P0 invariant).

    The admission transaction inserts both rows together; this read-only check
    makes a future bypass visible without pretending SQLite can enforce a
    cross-row invariant (the snapshot values come from the envelope, not from
    ``claims.payload``).
    """
    return [r[0] for r in c.execute(
        'SELECT c.id FROM claims c LEFT JOIN claim_snapshots s ON s.claim_id=c.id '
        'WHERE s.claim_id IS NULL ORDER BY c.id')]

class Service:
    def __init__(self,directory,role='author',simulation=True,branches=('AA','AB'),profile='strict'):
        if profile not in ('strict','lite'): raise ValueError('UNKNOWN_PROFILE')
        self.directory=Path(directory).resolve()
        runtime=Path(__file__).resolve().parents[1]/'runtime'
        if not self.directory.is_relative_to(runtime): raise ValueError('RUNTIME_PATH_REQUIRED')
        self.context=fixture_context(role,simulation,branches,profile)
        self.profile=profile; self.lite=profile=='lite'
        if self.lite:
            # work/task/policy are computed by the server (never typed by the model)
            work,task,policy=claim_entry_mod.identity(self.directory)
            self.context=_replace(self.context,work=work,task=task,policy=policy,branches=frozenset())
        self.store=Store(self.directory)
        self.fault_hook=lambda stage: None
        self.omh_mode='available'
    task=property(lambda self: self.context.task)
    policy=property(lambda self: self.context.policy)
    def known_branches(self):
        return tuple(sorted(self.context.branches)) if self.lite else ('AA','AB')
    def binding_state(self,c):
        """'missing' | 'own' | 'foreign' -- the persisted binding against this launch (D-02).
        Reveals nothing about a foreign binding beyond the word 'foreign'."""
        try: row=c.execute('SELECT work_ref FROM binding ORDER BY id LIMIT 1').fetchone()
        except sqlite3.OperationalError: return 'missing'
        if row is None: return 'missing'
        if row[0]==self.context.work: return 'own'
        try:
            if c.execute('SELECT 1 FROM adoptions WHERE new_work_ref=? AND source_work_ref=?',(self.context.work,row[0])).fetchone(): return 'own'
        except sqlite3.OperationalError: pass
        return 'foreign'
    def lite_sync(self,branch=None):
        """Lite: branches are the ones declared in the own/adopted database, not a launch constant."""
        if not self.store.path.exists(): raise Denied('NOT_INITIALIZED')
        with self.store.read() as c:
            state=self.binding_state(c)
            if state=='missing': raise Denied('NOT_INITIALIZED')
            if state=='foreign': raise Denied('SCOPE_DENIED')
            branches=frozenset(r[0] for r in c.execute('SELECT branch FROM branch_heads'))
        self.context=_replace(self.context,branches=branches)
        if branch is not None and branch not in branches: raise Denied('UNKNOWN_BRANCH',branches=sorted(branches))
    def scope(self,branch=None,work=_UNSET):
        if self.lite: self.lite_sync(branch)
        if work is _UNSET: work=self.context.work
        if work!=self.context.work or self.context.principal=='unknown' or branch is not None and branch not in self.context.branches: raise Denied('SCOPE_DENIED')
    def capability(self,cap):
        if not self.context.simulation: raise Denied('INDEPENDENCE_NOT_ENFORCED')
        if cap not in self.context.capabilities: raise Denied('INDEPENDENCE_NOT_ENFORCED')
    def ready(self):
        if not self.store.path.exists(): raise Denied('NOT_INITIALIZED')
        with self.store.read() as c:
            if not delivery_facts.installed(c): raise MigrationRequired('MIGRATION_REQUIRED')
            # D-02 / AN009 H3: the persisted binding must be this launch's (or an adopted one)
            # BEFORE any scoped data is read.  A binding-less file stays readable as before.
            if self.binding_state(c)=='foreign': raise Denied('SCOPE_DENIED')
    def integrity(self,c):
        """Verify once, return ``(stamp, chain)`` so read paths can reuse the result."""
        chain=verify_chain(c)
        stamp={'read_at':datetime.now(timezone.utc).isoformat(),'chain_head':chain.get('head_hash'),
               'revisions':dict(c.execute('SELECT branch,revision FROM branch_heads'))}
        if chain['status']!='CHAIN_OK':
            # Only identity locators from intact claims, not a projection of bad events.
            origins={r['id']:{'origin_branch':r['origin_branch'],'origin_version':r['origin_version']}
                     for r in c.execute('SELECT id,origin_branch,origin_version FROM claims') if r['origin_branch'] in self.context.branches}
            raise IntegrityFailure(dict(status='CHAIN_BROKEN',chain=chain,read_snapshot=stamp,
                                        readiness='NOT_READY',ready_for_owner_review=False,
                                        blockers=['EVENT_CHAIN_BROKEN'],origins=origins))
        return stamp,chain
    def integrity_gate(self,c):
        return self.integrity(c)[0]
    @guarded
    def init(self,request):
        if not self.context.simulation: raise Denied('OMH_BINDING_UNVERIFIED')
        if self.lite: raise Denied('PROFILE_LITE')
        if type(request) is not dict or set(request)!={'external_work_ref','policy_digest'}: raise Denied('REJECTED')
        self.scope(work=request['external_work_ref'])
        if request['policy_digest']!=POLICY: raise Denied('POLICY_MISMATCH')
        self.store.initialize(WORK,POLICY)
        return {'status':'INITIALIZED','simulated':True,'work_ref':WORK}
    def head(self,c,branch):
        # WS-F04: granted-but-absent branch is a typed absence, not an internal
        # failure. The single physical check lives here (query/resume/trace/export
        # all reach _snapshot -> head); sync/sync_status call require_branch
        # explicitly because they do not go through head().
        row=c.execute('SELECT revision FROM branch_heads WHERE branch=?',(branch,)).fetchone()
        if not row: raise Denied('NO_SUCH_BRANCH')
        return row[0]
    def require_branch(self,c,branch):
        if c.execute('SELECT 1 FROM branch_heads WHERE branch=?',(branch,)).fetchone() is None:
            raise Denied('NO_SUCH_BRANCH')
    def dedupe(self,c,operation,key,d,binding):
        # WS-F02 L2: replay identity = (key, candidate_id, branch, review_id,
        # digest, result_scope). A cached result is served ONLY when the full
        # binding matches and result_scope remains within the current grant.
        rows=c.execute('SELECT * FROM idempotency WHERE external_work_ref=? AND operation=? AND key=?',
                       (self.context.work,operation,key)).fetchall()
        if not rows: return None
        if any(r['candidate_id'] is None for r in rows):
            # Legacy (pre-migration) row on this key: inert. Never served,
            # never rewritten, never authorizes this key for a new binding.
            raise Denied('IDEMPOTENCY_BINDING_UNKNOWN')
        if binding.get('candidate_id') is None:
            pick=rows[0]  # submit-style replay: key alone selects its operation
        else:
            pick=next((r for r in rows if r['candidate_id']==binding['candidate_id'] and r['branch']==binding['branch']),None)
        if pick is None: raise Denied('IDEMPOTENCY_BINDING_MISMATCH')
        if pick['review_id']!=binding.get('review_id'): raise Denied('IDEMPOTENCY_REVIEW_MISMATCH')
        if pick['digest']!=d: raise Denied('IDEMPOTENCY_MISMATCH')
        stored_scope=set(json.loads(pick['result_scope']))
        if not stored_scope<=set(self.context.branches): raise Denied('SCOPE_DENIED')
        return json.loads(pick['result'])
    def remember(self,c,operation,key,d,result,binding):
        c.execute('INSERT INTO idempotency(external_work_ref,operation,key,scope_digest,digest,result,candidate_id,review_id,branch,result_scope) VALUES(?,?,?,?,?,?,?,?,?,?)',
                  (self.context.work,operation,key,binding['scope_digest'],d,canonical(result),
                   binding['candidate_id'],binding.get('review_id'),binding['branch'],
                   json.dumps(sorted(binding['result_scope']))))
    def scope_digest(self): return digest(sorted(self.context.branches))
    @guarded
    def submit(self,payload_json):
        self.scope(); self.capability('submit'); self.ready()
        try: p=strict_loads(payload_json)
        except (ValueError,TypeError): return {'status':'REJECTED','accepted_count':0,'errors':[{'local_id':None,'path':'$','code':'INVALID_JSON','required':True,'fix':'Use restricted JSON.'}],'rejected_local_ids':[]}
        if type(p) is not dict: raise Denied('REJECTED')
        self.scope(p.get('branch'),p.get('external_work_ref'))
        for branch in p.get('dependencies',{}) if type(p.get('dependencies')) is dict else []: self.scope(branch)
        errors=validate(p,self.known_branches())
        if errors: return {'status':'REJECTED','accepted_count':0,'errors':errors,'rejected_local_ids':[i.get('local_id') for i in p.get('items',[]) if isinstance(i,dict)]}
        if p['external_task_ref']!=self.task: raise Denied('SCOPE_DENIED')
        if p['policy_digest']!=self.policy: raise Denied('POLICY_MISMATCH')
        for i in p['items']:
            for branch in i.get('applicability',[]): self.scope(branch)
            if i.get('event_type')=='exclude' and 'owner' not in self.context.capabilities: raise Denied('OWNER_AUTHORITY_REQUIRED')
            if i.get('event_type')=='applicability' and i['value']['branch']!=p['branch']: raise Denied('SCOPE_DENIED')
        with self.store.read() as c: self.check_references(c,p)
        q=normalized(p,self.context.principal,self.context.root); d=digest(q)
        with self.store.transaction() as c:
            binding={'candidate_id':None,'review_id':None,'branch':p['branch'],
                     'scope_digest':self.scope_digest(),'result_scope':{p['branch']}|set(p['dependencies'])}
            old=self.dedupe(c,'submit:'+self.context.principal,p['idempotency_key'],d,binding)
            if old: return old
            candidate=str(uuid.uuid4())
            c.execute('INSERT INTO candidates VALUES(?,?,?,?,?,?,?)',(candidate,d,canonical(q),self.context.principal,self.context.root,p['branch'],datetime.now(timezone.utc).isoformat()))
            result={'status':'RECORDED_CANDIDATE','candidate_id':candidate,'intent_digest':d,'accepted_count':0,'simulated':True}
            self.remember(c,'submit:'+self.context.principal,p['idempotency_key'],d,result,dict(binding,candidate_id=candidate))
        return result
    def check_references(self,c,p):
        if p['operation']!='append': return
        from .projections import snapshot
        visible={cl['claim_id'] for b in self.context.branches for cl in snapshot(c,b,self.head(c,b))['claims']}
        scoped={cl['claim_id'] for cl in snapshot(c,p['branch'],self.head(c,p['branch']))['claims']}
        for i in p['items']:
            cid=i['claim_ref']; ev=i['event_type']
            if cid and cid not in (visible if ev=='applicability' else scoped): raise Denied('SCOPE_DENIED')
            if ev=='replacement' and i['value']['replacement_ref'] not in scoped: raise Denied('SCOPE_DENIED')
            if i['supersedes']:
                row=c.execute('SELECT branch,claim_ref FROM events WHERE id=?',(i['supersedes'],)).fetchone()
                if not row or row['branch']!=p['branch'] or row['claim_ref']!=cid: raise Denied('SCOPE_DENIED')
    def candidate(self,c,ref):
        row=c.execute('SELECT * FROM candidates WHERE id=?',(ref,)).fetchone()
        if not row: raise Denied('SCOPE_DENIED')
        self.scope(row['branch'])
        p=json.loads(row['payload'])
        for b in p['dependencies']: self.scope(b)
        return row,p
    @guarded
    def review(self,candidate_id,intent_digest):
        self.capability('review'); self.ready()
        with self.store.read() as c:
            row,p=self.candidate(c,candidate_id)
            # Lite (local_single_owner): author and reviewer are the same local owner; the
            # record is then honestly labelled 'self'.  Strict still refuses same-root review.
            if row['root']==self.context.root and not self.lite: raise Denied('INDEPENDENCE_NOT_ENFORCED')
            if row['digest']!=intent_digest: raise Denied('DIGEST_MISMATCH')
            level='self' if row['root']==self.context.root else 'independent'
            review=dict(review_level=level,candidate_digest=intent_digest,snapshot_digest=digest(p['dependencies']),dependencies=p['dependencies'],expected_revision=p['expected_branch_revision'],policy=p['policy_digest'],reviewer=self.context.principal,root=self.context.root,decision='approve',simulated=True,proof_ref='launcher-fixture-only')
        rid=str(uuid.uuid4())
        with self.store.transaction() as c:
            if 'review_level' in {r[1] for r in c.execute('PRAGMA table_info(reviews)')}:
                c.execute('INSERT INTO reviews(id,candidate,payload,review_level) VALUES(?,?,?,?)',(rid,candidate_id,canonical(review),level))
            else:  # pre-v3 database not yet migrated by dom_init/dom_start: label lives in the payload only
                c.execute('INSERT INTO reviews(id,candidate,payload) VALUES(?,?,?)',(rid,candidate_id,canonical(review)))
        return {'status':'DEMO_REVIEWED','review_id':rid,'simulated':True}
    def _record_claim(self,c,claim_id,candidate_id,tx,p,item,revision,review_id):
        """Insert the claim and its immutable snapshot as one pair (TD-DOM-36).

        The snapshot values come from the admitted envelope (dependencies and
        review id), not from ``claims.payload``; a SQLite trigger cannot derive
        them.  Keeping the two inserts in one helper makes the invariant true by
        construction; ``claim_snapshot_gaps`` is the read-only guard.
        """
        raw=decode(item['body_b64'])
        metadata=item.get('metadata') if type(item.get('metadata')) is dict else {}
        source_ref=metadata.get('source_ref') or metadata.get('artifact_ref') or metadata.get('repository_ref') or ''
        c.execute('INSERT INTO claims VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(claim_id,candidate_id,tx,item['content_type'],raw,raw_hash(raw),item['encoding'],item['media_type'],source_ref,p['branch'],p['origin_version'],canonical(item)))
        c.execute('INSERT INTO claim_snapshots VALUES(?,?,?,?,?,?)',(claim_id,tx,p['branch'],revision,canonical(p['dependencies']).decode('utf8'),review_id))
    @guarded
    def admit(self,candidate_id,review_id,idempotency_key,intent_digest):
        self.capability('admit'); self.ready()
        with self.store.transaction() as c:
            row,p=self.candidate(c,candidate_id)
            # WS-F02 L1: candidate digest vs claimed intent BEFORE any cache lookup.
            if row['digest']!=intent_digest or digest(p)!=intent_digest: raise Denied('DIGEST_MISMATCH')
            binding={'candidate_id':candidate_id,'review_id':review_id,'branch':p['branch'],
                     'scope_digest':self.scope_digest(),'result_scope':{p['branch']}|set(p['dependencies'])}
            old=self.dedupe(c,'admit:'+self.context.principal,idempotency_key,intent_digest,binding)
            if old: return old
            rr=c.execute('SELECT * FROM reviews WHERE id=? AND candidate=?',(review_id,candidate_id)).fetchone()
            if not rr: raise Denied('STALE_REVIEW')
            r=json.loads(rr['payload'])
            if (r['root']==row['root'] and not self.lite) or r['reviewer']!=self.context.principal: raise Denied('INDEPENDENCE_NOT_ENFORCED')
            if r['candidate_digest']!=intent_digest or r['policy']!=self.policy or p['policy_digest']!=self.policy or r['snapshot_digest']!=digest(p['dependencies']): raise Denied('STALE_REVIEW')
            if r.get('review_level','self' if r['root']==row['root'] else 'independent')!=('self' if r['root']==row['root'] else 'independent'): raise Denied('STALE_REVIEW')
            if any(self.head(c,b)!=v for b,v in p['dependencies'].items()): raise Denied('STALE_REVIEW')
            if self.head(c,p['branch'])!=p['expected_branch_revision'] or r['expected_revision']!=p['expected_branch_revision']: raise Denied('REVISION_CONFLICT')
            self.check_references(c,p)
            tx=str(uuid.uuid4()); revision=p['expected_branch_revision']+1
            ids={i['local_id']:str(uuid.uuid4()) for i in p['items']}
            receipt=dict(status='DEMO_ADMITTED',simulated=True,tx_id=tx,branch=p['branch'],revision=revision,intent_digest=intent_digest,claim_ids=ids if p['operation']=='claims' else {},event_ids=ids if p['operation']=='append' else {})
            c.execute('INSERT INTO transactions VALUES(?,?,?,?)',(tx,p['branch'],revision,canonical(receipt)))
            for i in p['items']:
                if p['operation']=='claims':
                    # N1: the claim's dependency snapshot and reviewing id are bound
                    # to the claim inside the same transaction (TD-DOM-36).
                    self._record_claim(c,ids[i['local_id']],candidate_id,tx,p,i,revision,review_id)
                    value={'item':i,'origin_version':p['origin_version']}; kind='claim'; claim=ids[i['local_id']]
                else:
                    value=i; kind=i['event_type']; claim=i['claim_ref'] or None
                provenance=dict(value=value,actor=row['author'],root=row['root'],server_time=datetime.now(timezone.utc).isoformat(),origin_version=p['origin_version'],context_revision=revision,reason=i['reason'],review_id=review_id,dependencies=p['dependencies'])
                prev=c.execute('SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
                previous=prev[0] if prev else '0'*64
                c.execute('INSERT INTO events(id,tx,claim_ref,branch,revision,kind,payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),tx,claim,p['branch'],revision,kind,canonical(provenance),previous,digest({'previous':previous,'payload':provenance,'tx':tx,'branch':p['branch']})))
            self.fault_hook('after_facts')
            changed=c.execute('UPDATE branch_heads SET revision=? WHERE branch=? AND revision=?',(revision,p['branch'],p['expected_branch_revision'])).rowcount
            if changed!=1: raise Denied('REVISION_CONFLICT')
            self.remember(c,'admit:'+self.context.principal,idempotency_key,intent_digest,receipt,binding)
            for kind,target in [('OMH_EVIDENCE',self.task),('YAML_EXPORT','scoped-snapshot')]:
                payload={'tx_id':tx,'branch':p['branch'],'revision':revision,'intent_digest':intent_digest,'target_ref':target}
                c.execute('INSERT INTO outbox VALUES(?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),tx,kind,target,p['branch'],revision,digest(payload),canonical(payload)))
            self.fault_hook('before_commit')
        self.fault_hook('after_commit')
        with self.store.read() as c: return json.loads(c.execute('SELECT receipt FROM transactions WHERE id=?',(tx,)).fetchone()[0])
    @guarded
    def query(self,branch,revision=None):
        self.scope(branch); self.ready()
        with self.store.read() as c:
            stamp=self.integrity_gate(c)
            snap=self._snapshot(c,branch,revision)
            return public_dto.project(
                dict(snap, read_snapshot=public_dto.read_snapshot(stamp, [branch])),
                'QueryResponse', scope=self.context.branches)
    def _snapshot(self,c,branch,revision=None):
        head=self.head(c,branch)
        revision=head if revision is None else revision
        if type(revision) is not int or revision<0 or revision>head: raise Denied('REJECTED')
        from .projections import snapshot
        return snapshot(c,branch,revision,self.lite)

    @guarded
    def claim_versions(self,claim_id):
        """P1.5: the replacement chain of one logical claim, oldest first."""
        if type(claim_id) is not str or not claim_id:
            raise Denied('INVALID_FIELD',field='claim_id')
        with self.store.read() as c:
            row=c.execute('SELECT origin_branch FROM claims WHERE id=?',(claim_id,)).fetchone()
            if row is None: raise Denied('NO_SUCH_CLAIM',field='claim_id')
            self.scope(row['origin_branch']); self.ready()
            stamp=self.integrity_gate(c)
            children=claim_entry_mod._children(c)
            archived=claim_entry_mod._archived(c)
            info=claim_entry_mod._lineage(children)
            parent={new:old for old,new in children.items()}
            root,_=info(claim_id)
            versions=[]; cid=root; seen=set()
            while cid is not None and cid not in seen:
                seen.add(cid)
                found=c.execute('SELECT cl.raw_sha256,t.revision FROM claims cl '
                                'JOIN transactions t ON t.id=cl.tx WHERE cl.id=?',(cid,)).fetchone()
                if found is None: break
                _,version=info(cid)
                versions.append({'claim_id':cid,'version':version,'supersedes':parent.get(cid),
                                 'raw_sha256':found['raw_sha256'],'revision':found['revision'],
                                 'is_current':cid not in archived})
                cid=children.get(cid)
            body={'status':'CLAIM_VERSIONS','logical_claim_id':root,'versions':versions,
                  'read_snapshot':public_dto.read_snapshot(stamp,[row['origin_branch']])}
            return public_dto.project(body,'ClaimVersions',scope=self.context.branches)

    @guarded
    def diff(self,branch_a,branch_b):
        """P1.5: compare current claims of two branches by logical claim id."""
        self.scope(branch_a); self.scope(branch_b); self.ready()
        with self.store.read() as c:
            self.require_branch(c,branch_a); self.require_branch(c,branch_b)
            stamp=self.integrity_gate(c)
            a=self._snapshot(c,branch_a); b=self._snapshot(c,branch_b)

        def current(snap):
            out={}
            for claim in snap['claims']:
                if not claim['archived']:
                    out[claim['logical_claim_id']]=claim
            return out

        def deepest(snap):
            out={}
            for claim in snap['claims']:
                lid=claim['logical_claim_id']
                out[lid]=max(out.get(lid,0),claim['version'])
            return out

        ca,cb=current(a),current(b)
        shared=set(deepest(a))&set(deepest(b))
        only_a=sorted(set(ca)-set(cb)); only_b=sorted(set(cb)-set(ca))
        changed=[]; identical=[]
        for lid in sorted(set(ca)&set(cb)):
            left,right=ca[lid],cb[lid]
            if left['raw_sha256']==right['raw_sha256']:
                identical.append(lid)
            else:
                changed.append({'logical_id':lid,
                                'a':{'claim_id':left['claim_id'],'version':left['version'],'sha':left['raw_sha256']},
                                'b':{'claim_id':right['claim_id'],'version':right['version'],'sha':right['raw_sha256']}})
        da,db=deepest(a),deepest(b)
        common=max(shared,key=lambda lid:(max(da[lid],db[lid]),lid)) if shared else None
        body={'status':'DIFF','comparable':bool(shared),'common_ancestor':common,
              'only_a':only_a,'only_b':only_b,'changed':changed,'identical':identical,
              'read_snapshot':public_dto.read_snapshot(stamp,[branch_a,branch_b])}
        return public_dto.project(body,'Diff',scope=self.context.branches)

    @guarded
    def recall(self,branch,at_seq):
        """P1.4: branch-local replay up to an event seq (archive-aware)."""
        self.scope(branch); self.ready()
        if type(at_seq) is not int or at_seq < 0:
            raise Denied('INVALID_FIELD',field='at_seq')
        with self.store.read() as c:
            self.require_branch(c,branch)
            stamp=self.integrity_gate(c)
            from .projections import snapshot_at_seq
            snap=snapshot_at_seq(c,branch,at_seq,self.lite)
            if snap is None:
                raise Denied('REVISION_OUT_OF_RANGE',field='at_seq')
            active=[cl for cl in snap['claims'] if not cl['archived']]
            archived=[cl['claim_id'] for cl in snap['claims'] if cl['archived']]
            conflicts=set(); resolved=set()
            for event in snap['history']:
                if event['kind']=='conflict':
                    ref=event['provenance']['value']['value']['conflict_ref']
                    conflicts.add(ref); resolved.discard(ref)
                elif event['kind']=='resolve':
                    ref=event['provenance']['value']['value']['conflict_ref']
                    conflicts.discard(ref); resolved.add(ref)
            related={b for cl in active for b in cl['applicable_branches'] if b != branch}
            related |= {b for cl in active for b in cl['dependencies'] if b != branch}
            active_ids={cl['claim_id'] for cl in active}
            if active_ids:
                for ref,target in c.execute(
                        "SELECT claim_ref,branch FROM events WHERE kind='applicability' AND seq<=?",
                        (snap['event_seq'],)):
                    if ref in active_ids and target != branch:
                        related.add(target)
            related=sorted(related)
            body={'status':'RECALL','branch':branch,'at_seq':at_seq,'revision':snap['revision'],
                  'active_claims':active,'archived_claims':archived,
                  # Candidate/review rows have no event seq, so historical pending
                  # is not reconstructible from the append-only log.  Documented
                  # as null until candidates become events.
                  'pending_decisions':None,
                  'resolved_conflicts':sorted(resolved),'related_branches':related,
                  'as_of':datetime.now(timezone.utc).isoformat(),
                  'baseline_range':{'branch':branch,'from_seq':1 if at_seq else 0,'to_seq':at_seq},
                  'read_snapshot':public_dto.read_snapshot(stamp,[branch])}
            return public_dto.project(body,'Recall',scope=self.context.branches)

    @guarded
    def append(self,payload_json):
        try: p=strict_loads(payload_json)
        except (ValueError,TypeError): raise Denied('REJECTED')
        if type(p) is not dict or p.get('operation')!='append': raise Denied('REJECTED')
        return self.submit(payload_json)

    @guarded
    def sync_status(self,branch):
        self.scope(branch); self.ready()
        with self.store.read() as c:
            self.require_branch(c,branch)
            stamp=self.integrity_gate(c)
            body=dict(delivery_facts.status(c,branch),
                      read_snapshot=public_dto.read_snapshot(stamp,[branch]))
            return public_dto.project(body,'SyncStatusResponse',scope=self.context.branches)

    @guarded
    def trace(self,branch='master'):
        self.scope()
        self.ready()
        if branch!='master': self.scope(branch)
        with self.store.read() as c:
            stamp,chain=self.integrity(c)
            if branch=='master' and not self.lite and not {'AA','AB'}<=self.context.branches:
                scope=[]
            elif branch=='master':
                scope=sorted(self.context.branches)
            else:
                scope=[branch]
            body=dict(self._trace(c,branch,chain),
                      read_snapshot=public_dto.read_snapshot(stamp,scope))
            return public_dto.project(body,'TraceResponse',scope=self.context.branches)
    def _trace(self,c,branch,chain=None):
        if branch=='master':
            if self.lite: branches=sorted(self.context.branches)
            elif not {'AA','AB'}<=self.context.branches: return {'status':'TRACE','readiness':'UNKNOWN','ready_for_owner_review':False,'simulated':True}
            else: branches=['AA','AB']
        else: branches=[branch]
        from .projections import trace_branch
        chain=public_dto.chain(chain if chain is not None else verify_chain(c))
        snaps=[self._snapshot(c,b) for b in branches]
        excluded=sorted({b for s in snaps for b in s['excluded_branches']})
        def reqs(s):
            # strict: the two fixture requirements; lite: whatever requirement_refs the claims actually carry
            return tuple(sorted({r for cl in s['claims'] for r in cl['item']['requirement_refs']})) if self.lite else ('R1','R2')
        traces=[trace_branch(c,s,any(i['state']!='ack' for i in delivery_facts.status(c,s['branch'])['intents']),reqs(s)) for s in snaps if s['branch'] not in excluded]
        residual=[r for t in traces for r in t['residual']]
        origins={k:v for t in traces for k,v in t.get('origins',{}).items()}
        blockers=sorted({b for t in traces for b in t['blockers']})
        ready=not blockers and bool(traces)
        readiness='READY' if ready else 'NOT_READY'
        if self.lite: readiness=self._readiness_counts(c,[s for s in snaps if s['branch'] not in excluded])
        return dict(status='ready_for_owner_review' if ready else 'TRACE',readiness=readiness,simulated=True,ready_for_owner_review=ready,residual=residual,origins=origins,blockers=blockers,chain=chain,excluded_branches=excluded,owner_close_called=False)

    def _readiness_counts(self,c,snaps):
        """Lite: admitted by anybody vs admitted by an independent reviewer, kept apart (O1).
        Rows without a label (written before v3) count as admitted but never as independent."""
        heads=dict(c.execute('SELECT branch,revision FROM branch_heads'))
        total=independent=stale=0
        for s in snaps:
            for cl in s['claims']:
                if cl['archived']: continue
                total+=1
                if cl.get('review_level')=='independent': independent+=1
                if any(heads.get(b)!=v for b,v in cl['dependencies'].items()): stale+=1
        pending,rejected=claim_entry_mod.pending_rejected(c,[s['branch'] for s in snaps])
        return dict(admitted_total=total,admitted_independent=independent,pending=pending,rejected=rejected,stale=stale)

    @guarded
    def export(self,branch,revision=None):
        self.scope(branch); self.ready()
        with self.store.read() as c:
            stamp=self.integrity_gate(c)
            info,raw=self._export_bytes(c,branch,revision)
        # File I/O happens after the read transaction: no read lock is held
        # across the filesystem (TD-DOM-34).
        if self._write_export(info['handle'],raw):
            result=dict(status='EXPORTED',handle=info['handle'],sha256=info['sha256'],
                        revision=info['revision'],simulated=True)
        else:
            result={'status':'EXPORT_PENDING','simulated':True}
        body=dict(result,read_snapshot=public_dto.read_snapshot(stamp,[branch]))
        return public_dto.project(body,'ExportResponse',scope=self.context.branches)
    def _export_bytes(self,c,branch,revision=None):
        import yaml
        # AU004-F-01: the YAML bytes are the same public Snapshot object the MCP
        # query returns -- branch-keyed dependency maps filtered by the caller's
        # launch grant.  Internal claim_snapshots / events keep the full maps.
        snap=public_dto.project(self._snapshot(c,branch,revision),'Snapshot',scope=self.context.branches)
        raw=yaml.safe_dump(snap,sort_keys=True,allow_unicode=False).encode('utf8')
        sha=raw_hash(raw); handle=f"exports/{branch}-{snap['revision']}-{sha}.yaml"
        return dict(handle=handle,sha256=sha,revision=snap['revision']),raw
    def _write_export(self,handle,raw):
        import os
        dest=self.directory/handle
        try:
            dest.parent.mkdir(parents=True,exist_ok=True)
            temp=dest.with_name(dest.name+'.'+str(uuid.uuid4())+'.tmp')
            with open(temp,'xb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
            self.fault_hook('before_rename')
            os.replace(temp,dest)
            self.fault_hook('after_rename')
            if dest.read_bytes()!=raw: raise OSError('readback mismatch')
        except OSError: return False
        return True

    @guarded
    def _delivery(self,intent,state,payload):
        # Compatibility surface: state may never be assigned by a caller, including
        # reviewers.  Capability/scope/state are validated before the refusal so
        # that no caller can forge a delivery state (TD-DOM-13, F-AU-03/F-AU-04).
        if state not in ('pending','ambiguous','ack'): raise Denied('REJECTED')
        self.scope(); self.capability('admit'); self.ready()
        with self.store.read() as c:
            row=c.execute('SELECT branch FROM outbox WHERE id=?',(intent,)).fetchone()
            if not row: raise Denied('SCOPE_DENIED')
            self.scope(row['branch'])
        raise Denied('DELIVERY_ENGINE_ONLY')

    @guarded
    def sync(self,branch):
        self.scope(branch); self.capability('admit'); self.ready()
        from .ports import OMHPort
        with self.store.read() as c:
            self.require_branch(c,branch)
            self.integrity_gate(c)
            intents=[dict(r) for r in c.execute('SELECT * FROM outbox WHERE branch=? ORDER BY revision,kind',(branch,))]
        for intent in intents:
            attempt=str(uuid.uuid4())
            with self.store.transaction() as c:
                self.integrity_gate(c)
                if delivery_facts.confirmed(c,intent): continue
                c.execute('INSERT INTO delivery_attempts VALUES(?,?,?,?,?,?,?,?)',
                          (attempt,intent['id'],intent['tx'],intent['digest'],intent['target'],self.context.principal,self.context.root,datetime.now(timezone.utc).isoformat()))
            self.fault_hook('after_attempt')
            exact=False; raw=b''; report='not_sent'
            # No read transaction around the external effect: the intent row is
            # immutable and the recording transaction below re-verifies the
            # chain.  Holding a read lock here would block writers until
            # busy_timeout under journal_mode=DELETE (TD-DOM-34).
            if intent['kind']=='YAML_EXPORT':
                with self.store.read() as c:
                    self.integrity_gate(c)
                    info,exported=self._export_bytes(c,branch,intent['revision'])
                if self._write_export(info['handle'],exported):
                    raw=exported
                    exact=raw_hash(raw)==info['sha256']
                    report='EXPORTED'
                else:
                    report='EXPORT_PENDING'
            else:
                port=OMHPort(self.directory,self.omh_mode)
                payload=json.loads(intent['payload'])
                expected={'digest':intent['digest'],'payload':payload}
                try:
                    observed=port.read_target(intent['target']).get(intent['tx'])
                    exact=observed==expected
                    if not exact:
                        report=port.attach(intent['target'],intent['tx'],intent['digest'],payload)
                        self.fault_hook('after_external_send')
                        observed=port.read_target(intent['target']).get(intent['tx'])
                        exact=observed==expected
                    raw=canonical(observed)
                except (OSError,ValueError):
                    report='TARGET_UNAVAILABLE'; exact=False; raw=b''
            observed_id=str(uuid.uuid4())
            with self.store.transaction() as c:
                stamp=self.integrity_gate(c)
                stamp['read_at']=datetime.now(timezone.utc).isoformat()
                stamp['port_reported']=report
                c.execute('INSERT INTO delivery_observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                          (observed_id,attempt,intent['id'],intent['tx'],intent['digest'],intent['target'],int(exact),raw_hash(raw),len(raw),stamp['read_at'],self.context.principal,self.context.root,canonical(stamp),raw))
                # An explicitly lost reply remains ambiguous until a fresh reconcile.
                if exact and report!='ambiguous' and not delivery_facts.confirmed(c,intent):
                    c.execute('INSERT INTO delivery_acks VALUES(?,?,?,?,?)',
                              (intent['id'],observed_id,intent['tx'],intent['digest'],intent['target']))
            self.fault_hook('after_observation')
        with self.store.read() as c:
            stamp=self.integrity_gate(c)
            status=delivery_facts.status(c,branch)
        pending=any(i['state']!='ack' for i in status['intents'])
        return public_dto.project({'status':'SYNC_PENDING' if pending else 'SYNCED','simulated':True,
                                   'read_snapshot':public_dto.read_snapshot(stamp,[branch])},'Sync',scope=self.context.branches)

    @staticmethod
    def _parse_after(after):
        """Strict keyset cursor (F1): exactly ``'branch:id'``, both components
        non-empty, no extra ``':'`` inside the id (candidate ids are UUIDs).
        Anything else is a typed ``REJECTED`` before any DB work, so an empty
        branch can never reach the ``IN (...)`` keyset comparison."""
        if after is None:
            return None
        if type(after) is not str:
            raise Denied('REJECTED')
        parts = after.split(':', 1)
        if len(parts) != 2 or not parts[0] or not parts[1] or ':' in parts[1]:
            raise Denied('REJECTED')
        return (parts[0], parts[1])

    @guarded
    def resume(self, branch, limit=50, after=None):
        self.scope(branch); self.ready()
        # Pagination args are validated here (typed refusals, never raw
        # exceptions): limit must be an int in [1,500]; after a 'branch:id'
        # keyset cursor when present, with BOTH components non-empty and no
        # stray ':' inside the id (F1: ':x', 'AA:', 'AA:x:y', '', ints ->
        # REJECTED).
        if type(limit) is not int or not 1 <= limit <= 500: raise Denied('REJECTED')
        if after is not None:
            self._parse_after(after)
        with self.store.read() as c:
            stamp,chain=self.integrity(c)
            trace=self._trace(c,branch,chain)
            body={'status':'RESUMED','snapshot':self._snapshot(c,branch),
                  'trace':trace,
                  'sync':delivery_facts.status(c,branch),'simulated':True,
                  'pending':self._pending_page(c, limit, after),
                  'read_snapshot':public_dto.read_snapshot(stamp,[branch])}
            if self.lite: body['readiness']=trace['readiness']
            return public_dto.project(body,'Resume',scope=self.context.branches)
    def _pending_page(self, c, limit, after):
        """Pending section page (RS007 W1, option A): metadata ONLY, never payload text.

        Visible to grant G iff candidate.branch in G AND payload.dependencies keys
        ⊆ G (same scope rule as candidate()/submit). Admitted predicate matches
        storage: EXISTS claims.candidate OR EXISTS idempotency admit-row. State is
        derived WITHOUT LLM: REVIEWED = has review; REJECTED = last review
        decision != 'approve'. ``count`` is EXACT and scope-filtered (its own pass,
        so no exists-oracle and no dependence on the page position). Keyset
        pagination ORDER BY (branch, id).

        AB007 (F2/F3): the visibility filters (deps ⊆ grant, admitted excluded)
        are applied IN SQL BEFORE LIMIT, so a page is always computed over the
        already-filtered set — an empty page cannot occur while visible rows
        remain, every visible row is reachable by following the last returned
        item's keyset, and ``has_more`` (fetch limit+1) counts only rows the
        reader can actually see (no exists-signal about hidden rows).
        """
        grant = set(self.context.branches)
        g_sorted = sorted(grant)
        ph = ','.join('?' * len(g_sorted))
        where = ['c.branch IN (%s)' % ph]
        params = [self.context.work] + list(g_sorted)   # idem_key subquery + branch IN
        if after is not None:
            parsed = self._parse_after(after)   # F1: strict cursor
            assert parsed is not None
            ab, aid = parsed
            where.append('(c.branch, c.id) > (?, ?)')
            params.extend([ab, aid])
        where.append('NOT EXISTS (SELECT 1 FROM claims cl WHERE cl.candidate = c.id)')
        where.append("NOT EXISTS (SELECT 1 FROM idempotency i WHERE i.external_work_ref = ? "
                     "AND i.operation LIKE 'admit:%' AND i.candidate_id = c.id)")
        params.append(self.context.work)
        where.append("NOT EXISTS (SELECT 1 FROM json_each(json_extract(c.payload, '$.dependencies')) je "
                     'WHERE je.key NOT IN (%s))' % ph)
        params.extend(g_sorted)
        rows = c.execute(
            'SELECT c.id, c.digest, c.author, c.root, c.branch, LENGTH(c.payload) AS plen, c.created_at, '
            "json_extract(c.payload,'$.dependencies') AS deps_json, "
            "json_extract(c.payload,'$.expected_branch_revision') AS expected_revision, "
            "json_extract(c.payload,'$.operation') AS operation, "
            '(SELECT r.id FROM reviews r WHERE r.candidate=c.id ORDER BY r.rowid DESC LIMIT 1) AS last_review_id, '
            '(SELECT r.payload FROM reviews r WHERE r.candidate=c.id ORDER BY r.rowid DESC LIMIT 1) AS last_review_payload, '
            "(SELECT i.key FROM idempotency i WHERE i.external_work_ref=? AND i.operation LIKE 'submit:%' "
            '       AND i.candidate_id=c.id ORDER BY i.scope_digest LIMIT 1) AS idem_key '
            'FROM candidates c WHERE {where} ORDER BY c.branch, c.id LIMIT ?'.format(where=' AND '.join(where)),
            params + [limit + 1]).fetchall()
        items = []
        has_more = len(rows) > limit   # F3: post-filter — visible rows only
        for r in rows[:limit]:
            deps = self._scoped_deps(r['deps_json'], grant)
            state = 'AWAITING_REVIEW'
            review_id = None
            if r['last_review_id'] is not None:
                decision = None
                try:
                    decision = json.loads(r['last_review_payload']).get('decision') if r['last_review_payload'] else None
                except (ValueError, TypeError):
                    decision = None
                state = 'REJECTED' if (decision is not None and decision != 'approve') else 'REVIEWED'
                review_id = r['last_review_id']
            item = {
                'candidate_id': r['id'],
                'intent_digest': r['digest'],
                'state': state,
                'branch': r['branch'],
                'operation': r['operation'],
                'origin': {'author': r['author'], 'root': r['root']},
                'dependencies': deps,
                'expected_branch_revision': int(r['expected_revision'] or 0),
                'payload_length': int(r['plen']),
                'idempotency_key': r['idem_key'],
                'review_id': review_id,
            }
            if r['created_at'] is not None:
                try:
                    created = datetime.fromisoformat(r['created_at'])
                    age = int((datetime.now(timezone.utc) - created).total_seconds())
                    item['age_seconds'] = max(0, age)
                except (ValueError, TypeError):
                    pass  # legacy/unparseable: age omitted (never 0)
            items.append(item)
        status = 'PENDING_PRESENT' if items else 'NO_PENDING'
        return {'status': status, 'count': self._pending_count(c), 'has_more': has_more,
                'items': items, 'page': {'limit': limit, 'after': after}}
    @staticmethod
    def _scoped_deps(deps_json_text, grant):
        if not deps_json_text:
            return {}
        d = json.loads(deps_json_text)
        return {k: int(v) for k, v in d.items() if isinstance(v, int) and not isinstance(v, bool)}
    def _pending_count(self, c):
        """Exact pending count over the grant: in-branch, deps ⊆ grant, NOT admitted.

        Scope-filtered exactly like the page items (anti-exists-oracle: hidden
        candidates contribute neither items nor counters). A separate pass keeps
        the count exact at any page position (independent of after/limit).
        """
        grant = set(self.context.branches)
        rows = c.execute(
            "SELECT c.branch, json_extract(c.payload,'$.dependencies') AS deps_json, "
            'EXISTS(SELECT 1 FROM claims cl WHERE cl.candidate=c.id) AS admitted_by_claims, '
            "EXISTS(SELECT 1 FROM idempotency i WHERE i.external_work_ref=? AND i.operation LIKE 'admit:%' "
            '       AND i.candidate_id=c.id) AS admitted_by_idem '
            'FROM candidates c WHERE c.branch IN ({ph})'.format(ph=','.join('?' * len(grant))),
            [self.context.work] + list(sorted(grant))).fetchall()
        n = 0
        for r in rows:
            if r['admitted_by_claims'] or r['admitted_by_idem']:
                continue
            d = self._scoped_deps(r['deps_json'], grant)
            if set(d).issubset(grant):
                n += 1
        return n

    # ---- WR-ADD (L0+L1): lite tools.  Logic lives in mockup/lite.py; every write goes
    # through the same submit -> review -> admit methods above (no bypass).
    @guarded
    def describe(self): return claim_entry_mod.describe(self)
    @guarded
    def start(self,request=None,goal=None,branches=None,adopt=False): return claim_entry_mod.start(self,request,goal,branches,adopt)
    @guarded
    def claim(self,branch,type,text,**fields): return claim_entry_mod.claim(self,branch,type,text,fields)
    @guarded
    def update(self,claim_id,text,reason,idempotency_key=None): return claim_entry_mod.update(self,claim_id,text,reason,idempotency_key)
    @guarded
    def find(self,query=None,branch=None,type=None,requirement_ref=None,limit=20): return claim_entry_mod.find(self,query,branch,type,requirement_ref,limit)
