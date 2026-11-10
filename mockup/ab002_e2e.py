"""Real raw stdio MCP failure/recovery runner. All targets SIMULATION."""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import sqlite3
import subprocess
import sys
import threading
import uuid
from .fixtures import WORK,POLICY,package,item

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runtime/AB002_A'


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=True),encoding='utf8')


class MCP:
    def __init__(self,directory,role='reviewer',mode='available',crash='',read_only=False):
        self.directory=directory
        directory.mkdir(parents=True,exist_ok=True)
        tag=uuid.uuid4().hex[:8]
        self.log=directory/('frames-'+tag+'.jsonl')
        self.err=open(directory/('stderr-'+tag+'.log'),'wb')
        cmd=[sys.executable,'-B','-m','mockup.ab002_launcher','--directory',str(directory),'--role',role,'--mode',mode,'--crash',crash]
        if read_only: cmd.append('--read-only')
        self.p=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err)
        if self.p.stdin is None or self.p.stdout is None: raise RuntimeError('MISSING_PIPE')
        self.q=queue.Queue(); self.n=0
        self.meta=directory/('process-'+tag+'.json')
        self.info={'pid':self.p.pid,'command':cmd,'exit_code':None,'frames':str(self.log)}
        save(self.meta,self.info)
        def reader():
            for line in self.p.stdout:
                with self.log.open('a',encoding='utf8') as f: f.write(json.dumps({'direction':'server','raw':line.decode('utf8')})+'\n')
                self.q.put(line)
            self.q.put(None)
        self.reader=threading.Thread(target=reader,daemon=True); self.reader.start()
        self.rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'AB002-raw','version':'1'}})
        self.send({'jsonrpc':'2.0','method':'notifications/initialized'})
    def send(self,frame):
        raw=json.dumps(frame)+'\n'
        with self.log.open('a',encoding='utf8') as f: f.write(json.dumps({'direction':'client','raw':raw})+'\n')
        self.p.stdin.write(raw.encode()); self.p.stdin.flush()
    def rpc(self,method,params):
        self.n+=1; n=self.n
        self.send({'jsonrpc':'2.0','id':n,'method':method,'params':params})
        while True:
            raw=self.q.get(timeout=25)
            if raw is None:
                self.p.wait(timeout=10)
                return {'process_exit':self.p.returncode}
            frame=json.loads(raw)
            if frame.get('id')==n: return frame
    def call(self,name,**args):
        frame=self.rpc('tools/call',{'name':name,'arguments':args})
        if 'process_exit' in frame: return frame
        result=frame.get('result',{})
        if 'structuredContent' in result: return result['structuredContent']
        if result.get('content'): return json.loads(result['content'][0]['text'])
        return frame
    def close(self):
        if self.p.poll() is None:
            self.p.stdin.close()
            try: self.p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.p.terminate(); self.p.wait(timeout=10)
        self.reader.join(timeout=5)
        self.info['exit_code']=self.p.returncode; save(self.meta,self.info)
        self.err.close()
    def __enter__(self): return self
    def __exit__(self,*args): self.close()


def seed(d,p=None):
    with MCP(d,role='author') as c:
        init=c.call('dom_init',external_work_ref=WORK,policy_digest=POLICY)
        assert init['status']=='INITIALIZED',init
        candidate=c.call('dom_submit',payload_json=json.dumps(p or package()))
        assert candidate['status']=='RECORDED_CANDIDATE',candidate
    with MCP(d) as c:
        review=c.call('dom_review',candidate_id=candidate['candidate_id'],intent_digest=candidate['intent_digest'])
        receipt=c.call('dom_admit',candidate_id=candidate['candidate_id'],review_id=review['review_id'],idempotency_key='admit-'+(p or {}).get('idempotency_key','k1'),intent_digest=candidate['intent_digest'])
        assert receipt['status']=='DEMO_ADMITTED',receipt
    return receipt


def readback(d,label):
    data={'files':{},'tables':{}}
    for p in sorted(d.rglob('*')):
        if p.is_file() and (p.suffix in ('.yaml','.tmp') or p.name=='omh-target.json'):
            raw=p.read_bytes(); data['files'][str(p.relative_to(d))]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes_hex':raw.hex()}
    db=d/'dom.sqlite3'
    if db.exists():
        data['database_sha256']=hashlib.sha256(db.read_bytes()).hexdigest()
        try:
            # sqlite3.Connection.__exit__ ends the transaction but does NOT
            # close the handle; retained cycles can block Windows rename.
            with closing(sqlite3.connect(db)) as c:
                for table, in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                    data['tables'][table]=[[{'blob_hex':v.hex()} if isinstance(v,bytes) else v for v in row] for row in c.execute('SELECT * FROM '+table)]
        except sqlite3.DatabaseError as error:
            data['database_error']={'sqlite_code':error.sqlite_errorcode,'sqlite_name':error.sqlite_errorname}
    save(d/(label+'.json'),data)
    return data


def baseline():
    d=OUT/('baseline-'+uuid.uuid4().hex[:8]); d.mkdir(parents=True)
    fingerprints={}
    for p in (ROOT/'mockup').glob('*.py'):
        raw=p.read_bytes(); fingerprints[str(p.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
        (d/p.name).write_bytes(raw)
    save(d/'source_fingerprints.json',fingerprints)
    seed(d)
    readback(d,'before')
    with MCP(d,mode='liar') as c:
        sync=c.call('dom_sync',branch='AA'); status=c.call('dom_sync_status',branch='AA'); trace=c.call('dom_trace',branch='AA')
    data=readback(d,'after')
    omh=[i for i in status['intents'] if i['kind']=='OMH_EVIDENCE']
    result={'mode':'SIMULATION','sync':sync,'sync_status':status,'trace':trace,'target_exists':(d/'omh-target.json').exists(),'false_ack_reproduced':omh[0]['state']=='ack' and not (d/'omh-target.json').exists(),'evidence':str(d)}
    save(d/'baseline_result.json',result)
    print(json.dumps(result,indent=2))
    assert result['false_ack_reproduced'],result


def main():
    p=argparse.ArgumentParser(); p.add_argument('--baseline',action='store_true'); a=p.parse_args()
    if a.baseline: baseline()
    else:
        from .ab002_matrix import run
        run()

if __name__=='__main__': main()
