"""Pure branch projection. Historical revision is branch-local; sharing is an explicit target-branch event."""
import json
import sqlite3

def _review_level(c,review_id):
    """WR-ADD: ``reviews.review_level`` if the column exists, else the label in the review payload, else None."""
    try:
        row=c.execute('SELECT review_level,payload FROM reviews WHERE id=?',(review_id,)).fetchone()
    except sqlite3.OperationalError:
        row=c.execute('SELECT NULL AS review_level,payload FROM reviews WHERE id=?',(review_id,)).fetchone()
    if not row: return None
    if isinstance(row['review_level'],str): return row['review_level']
    try:
        level=json.loads(row['payload']).get('review_level')
    except (ValueError,TypeError,AttributeError): return None
    return level if isinstance(level,str) else None

def _materialize(c,cid,claims,with_level=False):
    """Create the per-branch claim entry once; later events accumulate into it.

    The projection is a fold over history, so a claim record must never be
    rebuilt from scratch: ``applicability`` only adds a branch relation and
    must not reset ``archived``/``properties`` collected by earlier events.

    ``dependencies`` and ``review_id`` come from the immutable
    ``claim_snapshots`` row written by the admission transaction (N1), never
    from the package that carried the current event: an ``applicability``
    event supplies a branch relation only.  A claim with no admission snapshot
    is left out of the projection, which is fail-closed (missing coverage, not
    a silent ready).
    """
    record=claims.get(cid)
    if record is not None: return record
    r=c.execute('SELECT * FROM claims WHERE id=?',(cid,)).fetchone()
    if not r: return None
    snap=c.execute('SELECT dependencies,review_id FROM claim_snapshots WHERE claim_id=?',(cid,)).fetchone()
    if not snap: return None
    item=json.loads(r['payload'])
    record=dict(claim_id=cid,origin_branch=r['origin_branch'],origin_version=r['origin_version'],body_b64=item['body_b64'],raw_sha256=r['raw_sha256'],item=item,archived=False,properties={},dependencies=json.loads(snap['dependencies']),review_id=snap['review_id'],applicable_branches=[])
    if with_level: record['review_level']=_review_level(c,snap['review_id'])
    claims[cid]=record
    return record

def snapshot(c,branch,revision,with_level=False):
    rows=c.execute('SELECT * FROM events WHERE branch=? AND revision<=? ORDER BY seq',(branch,revision)).fetchall()
    claims={}; history=[]; conflicts=set(); converged=False; excluded=set()
    for row in rows:
        p=json.loads(row['payload']); v=p['value']; kind=row['kind']; cid=row['claim_ref']
        history.append(dict(event_id=row['id'],kind=kind,revision=row['revision'],claim_ref=cid,provenance=p))
        if kind=='claim':
            _materialize(c,cid,claims,with_level)
        elif kind=='applicability':
            record=_materialize(c,cid,claims,with_level)
            target=v['value']['branch']
            if record is not None and target not in record['applicable_branches']: record['applicable_branches'].append(target)
        elif kind=='archive' and cid in claims: claims[cid]['archived']=True
        elif kind=='property' and cid in claims: claims[cid]['properties'][v['value']['name']]=v['value']['value']
        elif kind=='replacement' and cid in claims: claims[cid]['archived']=True
        elif kind=='conflict': conflicts.add(v['value']['conflict_ref'])
        elif kind=='resolve': conflicts.discard(v['value']['conflict_ref'])
        elif kind=='converge': converged=True
        elif kind=='exclude': excluded.add(v['value']['branch'])
        # TD-DOM-18: convergence is not a permanent latch.  Any content change
        # after a 'converge' event invalidates it, so BRANCH_NOT_CONVERGED
        # reappears until the branch is re-converged explicitly.
        if kind != 'converge' and kind in ('claim','applicability','archive','property','replacement','conflict','resolve','exclude'):
            converged = False
    # The owner-provided branch marker must be visible on every historical row,
    # not only on the current claim record.
    for entry in history:
        claim=claims.get(entry['claim_ref'])
        if claim: entry['origin_branch']=claim['origin_branch']; entry['origin_version']=claim['origin_version']
    return dict(status='SNAPSHOT',branch=branch,revision=revision,simulated=True,claims=sorted(claims.values(),key=lambda x:x['claim_id']),history=history,conflicts=sorted(conflicts),converged=converged,excluded_branches=sorted(excluded))

def trace_branch(c,snap,pending,requirements=('R1','R2')):
    residual=[]
    origins={cl['claim_id']:dict(origin_branch=cl['origin_branch'],origin_version=cl['origin_version']) for cl in snap['claims']}
    heads=dict(c.execute('SELECT branch,revision FROM branch_heads'))
    for req in requirements:
        covered=[]; stale=[]; archived=[]
        for cl in snap['claims']:
            if req not in cl['item']['requirement_refs']: continue
            if cl['archived']: archived.append(cl['claim_id'])
            elif any(heads.get(b)!=v for b,v in cl['dependencies'].items()): stale.append(cl['claim_id'])
            else: covered.append(cl['claim_id'])
        reasons=[]
        if not covered: reasons.append('MISSING_COVERAGE')
        if stale: reasons.append('STALE_CHECK')
        if archived and not covered: reasons.append('ARCHIVED_SUPPORT')
        if snap['conflicts']: reasons.append('CONFLICT')
        residual.append(dict(requirement_ref=req,branch=snap['branch'],claim_refs=covered,check_refs=[cl['review_id'] for cl in snap['claims'] if cl['claim_id'] in covered],claim_origins=[dict(claim_id=cid,**origins[cid]) for cid in covered],reasons=reasons))
    blockers=[]
    if any(r['reasons'] for r in residual): blockers.append('CRITERIA_NOT_CURRENT')
    if snap['conflicts']: blockers.append('CONFLICT')
    if not snap['converged']: blockers.append('BRANCH_NOT_CONVERGED')
    if pending: blockers.append('SYNC_PENDING')
    return dict(status='TRACE',simulated=True,branch=snap['branch'],revision=snap['revision'],origins=origins,residual=residual,blockers=blockers,ready_for_owner_review=not blockers)
