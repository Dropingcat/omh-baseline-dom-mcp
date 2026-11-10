"""Additive v2 delivery facts; legacy state strings never establish delivery."""
import json
from .dom_contract import canonical,raw_hash

KEYS={'delivery_attempts':(('id',),), 'delivery_observations':(('id',),('attempt',)),
      'delivery_acks':(('intent',),('observed',))}
DDL='''
CREATE TABLE IF NOT EXISTS delivery_attempts(
 id TEXT PRIMARY KEY, intent TEXT NOT NULL REFERENCES outbox(id), tx TEXT NOT NULL,
 digest TEXT NOT NULL, target TEXT NOT NULL, actor TEXT NOT NULL, root TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS delivery_observations(
 id TEXT PRIMARY KEY, attempt TEXT NOT NULL UNIQUE REFERENCES delivery_attempts(id),
 intent TEXT NOT NULL REFERENCES outbox(id), tx TEXT NOT NULL, digest TEXT NOT NULL, target TEXT NOT NULL,
 matched INTEGER NOT NULL CHECK(matched IN(0,1)), fingerprint TEXT NOT NULL, size INTEGER NOT NULL CHECK(size>=0),
 read_at TEXT NOT NULL, actor TEXT NOT NULL, root TEXT NOT NULL, snapshot BLOB NOT NULL, evidence BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS delivery_acks(
 intent TEXT PRIMARY KEY REFERENCES outbox(id), observed TEXT NOT NULL UNIQUE REFERENCES delivery_observations(id),
 tx TEXT NOT NULL, digest TEXT NOT NULL, target TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS attempt_binding BEFORE INSERT ON delivery_attempts
 BEGIN SELECT RAISE(ABORT,'DELIVERY_BINDING') WHERE NOT EXISTS(
 SELECT 1 FROM outbox i WHERE i.id=NEW.intent AND i.tx=NEW.tx AND i.digest=NEW.digest AND i.target=NEW.target); END;
CREATE TRIGGER IF NOT EXISTS observation_binding BEFORE INSERT ON delivery_observations
 BEGIN SELECT RAISE(ABORT,'OBSERVATION_BINDING') WHERE NOT EXISTS(
 SELECT 1 FROM delivery_attempts a JOIN outbox i ON i.id=a.intent
 WHERE a.id=NEW.attempt AND a.intent=NEW.intent AND a.tx=NEW.tx AND a.digest=NEW.digest AND a.target=NEW.target
 AND a.actor=NEW.actor AND a.root=NEW.root AND i.tx=NEW.tx AND i.digest=NEW.digest AND i.target=NEW.target);
 SELECT RAISE(ABORT,'OBSERVATION_SHAPE') WHERE length(NEW.fingerprint)<>64 OR NEW.size<>length(NEW.evidence)
 OR NEW.read_at='' OR NOT json_valid(CAST(NEW.snapshot AS TEXT)); END;
CREATE TRIGGER IF NOT EXISTS ack_binding BEFORE INSERT ON delivery_acks
 BEGIN SELECT RAISE(ABORT,'ACK_REQUIRES_OBSERVED') WHERE NOT EXISTS(
 SELECT 1 FROM delivery_observations o JOIN delivery_attempts a ON a.id=o.attempt JOIN outbox i ON i.id=o.intent
 WHERE o.id=NEW.observed AND o.matched=1 AND o.intent=NEW.intent AND o.tx=NEW.tx AND o.digest=NEW.digest AND o.target=NEW.target
 AND a.intent=i.id AND a.tx=i.tx AND a.digest=i.digest AND a.target=i.target
 AND i.tx=NEW.tx AND i.digest=NEW.digest AND i.target=NEW.target); END;
CREATE TRIGGER IF NOT EXISTS legacy_ack_refused BEFORE INSERT ON delivery_events
 WHEN NEW.state='ack' BEGIN SELECT RAISE(ABORT,'ACK_REQUIRES_OBSERVED'); END;
'''


def installed(c):
    return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")} >= set(KEYS)


def confirmed(c,intent):
    row=c.execute('SELECT o.*,a.intent AS ai,a.tx AS atx,a.digest AS ad,a.target AS atarget '
                  'FROM delivery_acks k JOIN delivery_observations o ON o.id=k.observed '
                  'JOIN delivery_attempts a ON a.id=o.attempt '
                  'WHERE k.intent=? AND k.tx=? AND k.digest=? AND k.target=?',
                  (intent['id'],intent['tx'],intent['digest'],intent['target'])).fetchone()
    if not row: return None
    if not row['matched'] or any(row[k]!=intent[v] for k,v in [('intent','id'),('tx','tx'),('digest','digest'),('target','target'),('ai','id'),('atx','tx'),('ad','digest'),('atarget','target')]): return None
    raw=bytes(row['evidence'])
    if raw_hash(raw)!=row['fingerprint'] or len(raw)!=row['size']: return None
    try:
        json.loads(row['snapshot'])
        if intent['kind']=='OMH_EVIDENCE':
            expected={'digest':intent['digest'],'payload':json.loads(intent['payload'])}
            if raw!=canonical(expected): return None
        elif intent['kind']=='YAML_EXPORT':
            import yaml
            snap=yaml.safe_load(raw)
            if not isinstance(snap,dict) or snap.get('branch')!=intent['branch'] or snap.get('revision')!=intent['revision']: return None
        else: return None
    except (ValueError,TypeError): return None
    return row['id']


def status(c,branch):
    result=[]
    for row in c.execute('SELECT * FROM outbox WHERE branch=? ORDER BY revision,kind',(branch,)).fetchall():
        observed=confirmed(c,row)
        attempted=c.execute('SELECT 1 FROM delivery_attempts WHERE intent=? LIMIT 1',(row['id'],)).fetchone()
        result.append(dict(intent_id=row['id'],kind=row['kind'],tx_id=row['tx'],revision=row['revision'],
                           state='ack' if observed else 'ambiguous' if attempted else 'pending',observed_id=observed))
    return {'status':'SYNC_STATUS','simulated':True,'branch':branch,'intents':result}
