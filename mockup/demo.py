"""One-command reproducible synthetic demo.

    E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.demo

Each invocation creates a NEW run directory under ``runtime/runs`` and writes real
SQLite facts, append-only events, YAML exports and a JSON summary there.  It never
reuses or overwrites an earlier run; ``--output-dir`` is confined to ``runtime/``
and requires ``--reset`` before it will reuse a non-empty directory.

Everything external (OMH evidence target, Git, issuer) is simulated.  The demo
prints what it produced AND what is still not implemented.
"""
import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .admission import Service
from .fixtures import WORK, TASK, POLICY, package, item, amendment

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / 'runtime').resolve()
RUNS = RUNTIME / 'runs'
DEMO_TOOL = 'mockup.demo'


def demo_marker(path):
    """Parsed ``demo.json`` only when it belongs to *this* demo's own run.

    A run directory is disposable only if the marker names this tool and the
    same absolute directory.  Anything else (another tool's output, a hand-made
    ``demo.json``, a copied directory) is foreign and is never deleted.
    """
    try:
        data = json.loads((path / 'demo.json').read_text(encoding='utf8'))
    except (OSError, ValueError):
        return None
    if type(data) is not dict or data.get('tool') != DEMO_TOOL or data.get('simulated') is not True:
        return None
    if data.get('run_directory') != str(path):
        return None
    return data


def new_run_directory(explicit=None, reset=False):
    if explicit is None:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        path = RUNS / f'run-{stamp}-{uuid.uuid4().hex[:8]}'
    else:
        path = Path(explicit).resolve()
        if not path.is_relative_to(RUNTIME):
            raise SystemExit(f'REFUSED: --output-dir must resolve inside {RUNTIME}')
        if path == RUNTIME or path == RUNS:
            raise SystemExit(f'REFUSED: {path} is the shared run root, not a demo run directory')
        if path.exists() and not path.is_dir():
            raise SystemExit(f'REFUSED: {path} exists and is not a directory')
        if path.exists() and any(path.iterdir()):
            if not reset:
                raise SystemExit(f'REFUSED: {path} is not empty; pass --reset for a demo run directory')
            if demo_marker(path) is None:
                raise SystemExit(f'REFUSED: --reset is only allowed for a directory this demo created '
                                 f'(demo.json with tool={DEMO_TOOL} and matching run_directory); '
                                 f'earlier runs and foreign directories are never deleted')
            shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=False)
    return path


def step(label, expected, call):
    result = call()
    status = result.get('status') if isinstance(result, dict) else None
    print(f'  {label:<46} {status}')
    if status != expected:
        raise SystemExit(f'demo step failed: {label}: expected {expected}, got {json.dumps(result)[:400]}')
    return result


def deny(label, expected, call):
    result = call()
    status = result.get('status') if isinstance(result, dict) else None
    print(f'  {label:<46} {status} (expected refusal)')
    if status != expected:
        raise SystemExit(f'demo denial not enforced: {label}: expected {expected}, got {json.dumps(result)[:400]}')
    return result


def run(directory):
    author = Service(directory, role='author')
    reviewer = Service(directory, role='reviewer')
    owner = Service(directory, role='owner')
    record = {'tool': DEMO_TOOL, 'run_directory': str(directory), 'simulated': True, 'admissions': [], 'denials': []}

    print('1) binding')
    record['init'] = step('author init', 'INITIALIZED',
                          lambda: author.init({'external_work_ref': WORK, 'policy_digest': POLICY}))

    print('2) AA origin claim (R1) and independent admission')
    candidate = step('author submit (AA, R1)', 'RECORDED_CANDIDATE',
                     lambda: author.submit(json.dumps(package())))
    record['denials'].append(deny('author reviews own candidate', 'INDEPENDENCE_NOT_ENFORCED',
                                  lambda: author.review(candidate['candidate_id'], candidate['intent_digest'])))
    review = step('reviewer review', 'DEMO_REVIEWED',
                  lambda: reviewer.review(candidate['candidate_id'], candidate['intent_digest']))
    first = step('reviewer admit (AA rev 1)', 'DEMO_ADMITTED',
                 lambda: reviewer.admit(candidate['candidate_id'], review['review_id'], 'demo-aa-1',
                                        candidate['intent_digest']))
    record['admissions'].append(first)
    claim_one = first['claim_ids']['one']

    print('3) share the AA claim into AB (explicit target-branch event)')
    share = step('author submit applicability AA->AB', 'RECORDED_CANDIDATE',
                 lambda: author.submit(json.dumps(amendment('demo-share-1', claim_one, 'applicability',
                                                            {'branch': 'AB'}, 0, 'AB'))))
    share_review = step('reviewer review share', 'DEMO_REVIEWED',
                        lambda: reviewer.review(share['candidate_id'], share['intent_digest']))
    record['admissions'].append(step('reviewer admit (AB rev 1)', 'DEMO_ADMITTED',
                                     lambda: reviewer.admit(share['candidate_id'], share_review['review_id'],
                                                            'demo-ab-1', share['intent_digest'])))

    print('4) second AA claim (R2) and its AB applicability')
    second = step('author submit (AA, R2)', 'RECORDED_CANDIDATE',
                  lambda: author.submit(json.dumps(package('demo-aa-2', revision=1,
                                                           items=[item('two', requirements=['R2'])]))))
    second_review = step('reviewer review', 'DEMO_REVIEWED',
                         lambda: reviewer.review(second['candidate_id'], second['intent_digest']))
    record['admissions'].append(step('reviewer admit (AA rev 2)', 'DEMO_ADMITTED',
                                     lambda: reviewer.admit(second['candidate_id'], second_review['review_id'],
                                                            'demo-aa-2', second['intent_digest'])))
    claim_two = record['admissions'][-1]['claim_ids']['two']

    share_two = step('author submit applicability AA->AB', 'RECORDED_CANDIDATE',
                     lambda: author.submit(json.dumps(amendment('demo-share-2', claim_two, 'applicability',
                                                                {'branch': 'AB'}, 1, 'AB'))))
    share_two_review = step('reviewer review', 'DEMO_REVIEWED',
                            lambda: reviewer.review(share_two['candidate_id'], share_two['intent_digest']))
    record['admissions'].append(step('reviewer admit (AB rev 2)', 'DEMO_ADMITTED',
                                     lambda: reviewer.admit(share_two['candidate_id'], share_two_review['review_id'],
                                                            'demo-ab-2', share_two['intent_digest'])))

    print('5) deny an attempt to rewrite the origin marker through a property event')
    tamper = amendment('demo-tamper', claim_one, 'property', {'name': 'origin_branch', 'value': 'AB'}, 2)
    record['denials'].append(deny('property origin_branch (AA rev 3)', 'REJECTED',
                                  lambda: author.submit(json.dumps(tamper))))

    print('6) audited amendment + convergence on both branches')
    note = step('author submit comment', 'RECORDED_CANDIDATE',
                lambda: author.submit(json.dumps(amendment('demo-comment', claim_one, 'comment',
                                                           {'text': 'Reviewed exact bytes, no normalization.\r\n'}, 2))))
    note_review = step('reviewer review comment', 'DEMO_REVIEWED',
                       lambda: reviewer.review(note['candidate_id'], note['intent_digest']))
    record['admissions'].append(step('reviewer admit (AA rev 3)', 'DEMO_ADMITTED',
                                     lambda: reviewer.admit(note['candidate_id'], note_review['review_id'],
                                                            'demo-aa-3', note['intent_digest'])))
    for branch, revision, key in (('AA', 3, 'demo-converge-aa'), ('AB', 2, 'demo-converge-ab')):
        converged = step(f'author submit converge ({branch})', 'RECORDED_CANDIDATE',
                         lambda branch=branch, revision=revision, key=key: author.submit(
                             json.dumps(amendment(key, '', 'converge', {}, revision, branch))))
        converged_review = step(f'reviewer review converge ({branch})', 'DEMO_REVIEWED',
                                lambda c=converged: reviewer.review(c['candidate_id'], c['intent_digest']))
        record['admissions'].append(step(f'reviewer admit converge ({branch})', 'DEMO_ADMITTED',
                                         lambda c=converged, r=converged_review, k=key, b=branch: reviewer.admit(
                                             c['candidate_id'], r['review_id'], k, c['intent_digest'])))

    print('7) trace before external delivery (pending blocks readiness)')
    pending_trace = owner.trace('master')
    print(f'  readiness={pending_trace["readiness"]} blockers={pending_trace["blockers"]}')
    if pending_trace['ready_for_owner_review']:
        raise SystemExit('demo invariant failed: ready although outbox is still pending')
    record['trace_pending'] = pending_trace

    print('8) scoped export + simulated owner delivery, then read-back')
    record['sync'] = {branch: step(f'sync {branch}', 'SYNCED', lambda b=branch: reviewer.sync(b))
                      for branch in ('AA', 'AB')}
    ready_trace = owner.trace('master')
    print(f'  readiness={ready_trace["readiness"]} blockers={ready_trace["blockers"]} '
          f'owner_close_called={ready_trace["owner_close_called"]}')
    record['trace_ready'] = ready_trace
    if not ready_trace['ready_for_owner_review'] or ready_trace['owner_close_called']:
        raise SystemExit('demo invariant failed: expected ready_for_owner_review without owner close')

    print('9) historical scoped YAML at an exact revision is stable')
    first_export = author.export('AA', 1)
    again = author.export('AA', 1)
    if first_export['sha256'] != again['sha256']:
        raise SystemExit('demo invariant failed: historical export is not deterministic')
    print(f'  AA rev1 {first_export["handle"]} sha256={first_export["sha256"]}')
    record['historical_export'] = first_export

    snapshot = author.query('AA')
    ab_snapshot = author.query('AB')
    markers = {claim['claim_id']: {'origin_branch': claim['origin_branch'],
                                   'origin_version': claim['origin_version']}
               for branch in (snapshot, ab_snapshot) for claim in branch['claims']}
    record['origin_markers'] = markers
    record['counts'] = {'AA_revision': snapshot['revision'], 'AB_revision': ab_snapshot['revision'],
                        'AA_claims': len(snapshot['claims']), 'AB_claims': len(ab_snapshot['claims']),
                        'history_AA': len(snapshot['history']), 'history_AB': len(ab_snapshot['history'])}
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(prog='mockup.demo', description='Synthetic DOM/OMH demo run.')
    parser.add_argument('--output-dir', default=None, help='new directory inside <project>/runtime')
    parser.add_argument('--reset', action='store_true', help='allow reuse of a non-empty demo run dir')
    args = parser.parse_args(argv)

    directory = new_run_directory(args.output_dir, args.reset)
    print(f'run directory: {directory}')
    record = run(directory)
    exports = sorted(str(p.relative_to(directory)).replace('\\', '/') for p in (directory / 'exports').glob('*.yaml'))
    record['artifacts'] = [str(directory / 'dom.sqlite3'), str(directory / 'omh-target.json'),
                           str(directory / 'demo.json')] + [str(directory / item_) for item_ in exports]
    (directory / 'demo.json').write_text(json.dumps(record, indent=1, sort_keys=True), encoding='utf8')

    print('\n== RESULT ==')
    print(f'  run directory        {directory}')
    print(f'  work / task          {WORK} / {TASK} (simulated)')
    print(f'  revisions            AA={record["counts"]["AA_revision"]} AB={record["counts"]["AB_revision"]}')
    print(f'  claims               AA={record["counts"]["AA_claims"]} AB={record["counts"]["AB_claims"]}')
    print(f'  origin markers       {len(record["origin_markers"])} claims carry origin_branch/origin_version')
    print(f'  readiness            {record["trace_ready"]["readiness"]} (owner_close_called=false)')
    print(f'  exports              {len(exports)} YAML files: ' + ', '.join(exports))
    print(f'  demo summary         {directory / "demo.json"}')
    print('\n== REMAINDER (NOT IMPLEMENTED / NOT PROVEN) ==')
    for line in ('live OMH / Git / issuer adapters: simulation only, no network calls',
                 'production identity + reviewer independence: launcher fixture, not authentication',
                 'OS-level isolation from direct SQL or filesystem access: NOT_ENFORCED',
                 'real Git dirty-snapshot and merge intentions: fixture fields only (T20)',
                 'owner task closure: deliberately never called by this mockup'):
        print('  - ' + line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
