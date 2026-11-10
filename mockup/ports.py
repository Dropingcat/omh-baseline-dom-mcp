"""Trusted launcher fixture identities. Not production authentication."""
import json
import os
import uuid
from dataclasses import dataclass
from contextlib import contextmanager
import time
from pathlib import Path
from .dom_contract import raw_hash
from .fixtures import WORK,TASK,POLICY

@dataclass(frozen=True)
class Context:
    principal: str
    root: str
    capabilities: frozenset
    branches: frozenset
    simulation: bool
    work: str=WORK
    profile: str='strict'
    task: str=TASK
    policy: str=POLICY

def fixture_context(role='author',simulation=True,branches=('AA','AB'),profile='strict'):
    if profile=='lite':
        # local_single_owner: one trusted owner identity chosen by the launcher
        # (never by a tool argument).  It may submit, review and admit; the
        # review it records is labelled review_level='self'.  No 'owner' capability.
        return Context('lite-owner','root-lite',frozenset({'submit','review','admit'}),frozenset(branches),simulation,profile='lite')
    mapping={'author':('demo-author','root-A',{'submit'}),'helper':('demo-helper','root-A',{'submit','review','admit'}),'reviewer':('demo-reviewer','root-B',{'review','admit'}),'owner':('demo-owner','root-C',{'submit','review','admit','owner'})}
    p,r,c=mapping.get(role,('unknown','unknown',set()))
    return Context(p,r,frozenset(c),frozenset(branches),simulation)

class OMHPort:
    """Simulation-only evidence target. No network, no real OMH, no auth claim."""
    def __init__(self,directory,mode='available'):
        self.path=Path(directory)/'omh-target.json'
        self.mode=mode
    def _load(self):
        try: data=json.loads(self.path.read_text(encoding='utf8'))
        except FileNotFoundError: return {}
        if not isinstance(data,dict): raise ValueError('TARGET_INVALID')
        return data
    def read_target(self,target):
        if self.mode=='unavailable': raise OSError('TARGET_UNAVAILABLE')
        store=self._load().get(target)
        return dict(store) if isinstance(store,dict) else {}
    @contextmanager
    def _locked(self):
        # OS lock is released on real process death; no stale lockfile ownership.
        with open(self.path.with_suffix('.lock'),'a+b') as lock:
            if lock.tell()==0: lock.write(b'0'); lock.flush()
            deadline=time.monotonic()+5
            while True:
                try:
                    lock.seek(0)
                    if os.name=='nt':
                        import msvcrt
                        msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
                    else:
                        import fcntl
                        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic()>=deadline: raise OSError('TARGET_BUSY') from None
                    time.sleep(.02)
            try: yield
            finally:
                lock.seek(0)
                if os.name=='nt': msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
                else: fcntl.flock(lock,fcntl.LOCK_UN)
    def attach(self,target,tx,digest,payload):
        if self.mode=='unavailable': return 'error'
        with self._locked():
            store=self._load(); expected={'digest':digest,'payload':payload}
            prior=store.get(target,{}).get(tx)
            if prior is not None:
                return 'ack' if prior==expected else 'conflict'
            store.setdefault(target,{})[tx]=expected
            temp=self.path.with_name(self.path.name+'.'+uuid.uuid4().hex+'.tmp')
            try:
                with open(temp,'x',encoding='utf8') as f:
                    f.write(json.dumps(store,sort_keys=True)); f.flush(); os.fsync(f.fileno())
                os.replace(temp,self.path)
                with open(self.path.with_name('omh-writes.jsonl'),'a',encoding='utf8') as f:
                    f.write(json.dumps({'pid':os.getpid(),'target':target,'tx':tx,'digest':digest})+'\n'); f.flush(); os.fsync(f.fileno())
            except OSError:
                # Temp is evidence of an incomplete effect, never proof of delivery.
                return 'error'
        return 'ambiguous' if self.mode=='ambiguous' else 'ack'

class GitPort:
    """Fixture-only Git boundary: reports state, performs nothing.

    Mutating operations return NOT_IMPLEMENTED; the fixture HEAD is constant and
    no repository is created or touched.
    """
    HEAD='refs/heads/fixture-b1'
    COMMIT='0'*40
    def __init__(self,directory):
        self.directory=Path(directory)
    def head(self): return {'branch':self.HEAD,'commit':self.COMMIT,'dirty':True,'simulation':True}
    def snapshot(self,content,path='synthetic.py'):
        return {'path':path,'digest':raw_hash(content),'dirty':True,'simulation':True,'head':self.HEAD,'commit':self.COMMIT}
    def intent(self,operation):
        return {'status':'NOT_IMPLEMENTED','operation':operation,'simulation':True,'head_unchanged':True,'head':self.HEAD}
