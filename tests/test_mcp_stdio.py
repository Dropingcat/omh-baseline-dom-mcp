"""Real stdio MCP transport tests.

Every test here spawns ``python -m mockup.server`` as an actual child process.
The SDK client path proves handshake/list/call; the raw path proves that stdout
carries protocol frames only and that request ids are correlated on the wire.
"""
import asyncio
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

import mcp.types as types
import yaml
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from mockup.fixtures import WORK, POLICY, package

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'runtime' / 'logs'
TMP = ROOT / 'runtime' / 'tmp'
PASSED_ENV = ('SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATH', 'PATHEXT', 'USERPROFILE',
              'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'SYSTEMDRIVE', 'NUMBER_OF_PROCESSORS')
TOOL_NAMES = {'dom_init', 'dom_resume', 'dom_submit', 'dom_review', 'dom_admit', 'dom_append',
              'dom_query', 'dom_trace', 'dom_export', 'dom_sync_status',
              # documented extras: spec-permitted outbox delivery + query alias
              'dom_sync', 'dom_snapshot',
              # TD-DOM-22.3: claim-entry block now exposed in the strict profile too
              'dom_describe', 'dom_start', 'dom_claim', 'dom_update', 'dom_find'}
# SPEC.md:46 normative list; every one of these must exist on the wire.
SPEC_TOOLS = {'dom_init', 'dom_resume', 'dom_submit', 'dom_review', 'dom_admit', 'dom_append',
              'dom_query', 'dom_trace', 'dom_export', 'dom_sync_status'}


def child_env():
    LOGS.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in PASSED_ENV}
    env.update(PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE='1', TEMP=str(TMP), TMP=str(TMP))
    return env


def server_argv(directory, role, simulation=True):
    return [sys.executable, '-B', '-m', 'mockup.server', '--directory', str(directory),
            '--role', role, '--simulation' if simulation else '--no-simulation']


def parameters(directory, role, simulation=True):
    return StdioServerParameters(command=sys.executable, args=server_argv(directory, role, simulation)[1:],
                                 env=child_env(), cwd=str(ROOT))


def payload_json(**overrides):
    data = package(**overrides) if overrides else package()
    return json.dumps(data)


def text(result):
    return json.loads(result.content[0].text)


def test_handshake_list_and_refusals(tmp_path):
    LOGS.mkdir(parents=True, exist_ok=True)
    errlog = open(LOGS / 'AB001_mcp_server_stderr.log', 'a', encoding='utf8')

    async def scenario():
        async with stdio_client(parameters(tmp_path, 'reviewer'), errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                listed = await session.list_tools()
                before_init = await session.call_tool('dom_snapshot', {'branch': 'AA'})
                foreign = await session.call_tool('dom_snapshot', {'branch': 'ZZ'})
                smuggled = await session.call_tool('dom_snapshot', {'branch': 'AA', 'role': 'owner'})
                return dict(protocol=initialized.protocolVersion,
                            server=dict(name=initialized.serverInfo.name, version=initialized.serverInfo.version),
                            capabilities=initialized.capabilities.model_dump(exclude_none=True),
                            tools=[t.name for t in listed.tools],
                            schemas={t.name: t.inputSchema for t in listed.tools},
                            before_init=(before_init.isError, text(before_init)),
                            foreign=(foreign.isError, text(foreign)),
                            smuggled=(smuggled.isError, text(smuggled)))

    try:
        evidence = asyncio.run(scenario())
    finally:
        errlog.close()
    (LOGS / 'AB001_mcp_handshake.json').write_text(json.dumps(evidence, indent=1, sort_keys=True), encoding='utf8')

    assert evidence['protocol'] == types.LATEST_PROTOCOL_VERSION
    assert evidence['server']['name'] == 'omh-dom-mockup'
    assert 'tools' in evidence['capabilities']
    assert set(evidence['tools']) == TOOL_NAMES
    assert SPEC_TOOLS <= set(evidence['tools'])
    for name, schema in evidence['schemas'].items():
        assert schema['type'] == 'object', name
        assert not ({'role', 'principal', 'simulation', 'capabilities'} & set(schema.get('properties', {}))), name
    # not initialized yet: domain refusal, not an exception
    assert evidence['before_init'][0] is False and evidence['before_init'][1]['status'] == 'NOT_INITIALIZED'
    # foreign scope is denied before traversal
    assert evidence['foreign'][1]['status'] == 'SCOPE_DENIED'
    # a caller-supplied identity argument is refused, never honoured
    assert evidence['smuggled'][0] is True and evidence['smuggled'][1]['status'] == 'INVALID_ARGUMENTS'


def test_two_role_flow_over_stdio(tmp_path):
    async def author():
        async with stdio_client(parameters(tmp_path, 'author')) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                initialized = text(await session.call_tool('dom_init', {'external_work_ref': 'demo:existing-work-W1',
                                                                        'policy_digest': _policy()}))
                candidate = text(await session.call_tool('dom_submit', {'payload_json': payload_json()}))
                empty = text(await session.call_tool('dom_snapshot', {'branch': 'AA'}))
                coerced_payload = package()
                coerced_payload['expected_branch_revision'] = '0'
                coerced = await session.call_tool('dom_submit', {'payload_json': json.dumps(coerced_payload)})
                self_review = text(await session.call_tool('dom_review', {'candidate_id': candidate['candidate_id'],
                                                                          'intent_digest': candidate['intent_digest']}))
                return dict(initialized=initialized, candidate=candidate, empty=empty, self_review=self_review,
                            coerced=(coerced.isError, text(coerced)))

    async def reviewer(candidate_id, digest, key):
        async with stdio_client(parameters(tmp_path, 'reviewer')) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                review = text(await session.call_tool('dom_review', {'candidate_id': candidate_id, 'intent_digest': digest}))
                admitted = text(await session.call_tool('dom_admit', {'candidate_id': candidate_id,
                                                                      'review_id': review['review_id'],
                                                                      'idempotency_key': key, 'intent_digest': digest}))
                snapshot = text(await session.call_tool('dom_snapshot', {'branch': 'AA'}))
                trace = text(await session.call_tool('dom_trace', {'branch': 'master'}))
                exported = text(await session.call_tool('dom_export', {'branch': 'AA'}))
                return dict(review=review, admitted=admitted, snapshot=snapshot, trace=trace, exported=exported)

    first = asyncio.run(author())
    assert first['initialized']['status'] == 'INITIALIZED'
    assert first['candidate']['status'] == 'RECORDED_CANDIDATE'
    assert first['empty']['claims'] == []
    assert first['self_review']['status'] == 'INDEPENDENCE_NOT_ENFORCED'
    assert first['coerced'][0] is False
    assert first['coerced'][1]['status'] == 'REJECTED'
    assert any(e['code'] == 'INVALID_TYPE' and e['path'] == '$.expected_branch_revision'
               for e in first['coerced'][1]['errors'])

    second = asyncio.run(reviewer(first['candidate']['candidate_id'], first['candidate']['intent_digest'], 'mcp-admit-1'))
    assert second['review']['status'] == 'DEMO_REVIEWED'
    assert second['admitted']['status'] == 'DEMO_ADMITTED'
    claim = second['snapshot']['claims'][0]
    assert claim['origin_branch'] == 'AA' and claim['origin_version'] == 'synthetic-artifact-v1'
    assert second['trace']['origins'][claim['claim_id']]['origin_branch'] == 'AA'
    assert second['exported']['status'] == 'EXPORTED'
    document = yaml.safe_load((tmp_path / second['exported']['handle']).read_text(encoding='utf8'))
    assert document['claims'][0]['origin_branch'] == 'AA'


def test_launch_without_simulation_is_fail_closed(tmp_path):
    async def scenario():
        async with stdio_client(parameters(tmp_path, 'reviewer', simulation=False)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return text(await session.call_tool('dom_init', {'external_work_ref': 'demo:existing-work-W1',
                                                                 'policy_digest': _policy()}))

    refused = asyncio.run(scenario())
    assert refused['status'] == 'OMH_BINDING_UNVERIFIED'
    assert not (tmp_path / 'dom.sqlite3').exists()


def test_raw_stdout_is_protocol_frames_only(tmp_path):
    LOGS.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(server_argv(tmp_path, 'author'), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, cwd=str(ROOT), env=child_env(), text=True,
                               encoding='utf8', bufsize=1)
    frames = queue.Queue()
    stderr_lines = []

    def pump():
        for line in process.stdout:
            frames.put(line)
        frames.put(None)

    def pump_err():
        for line in process.stderr:
            stderr_lines.append(line.rstrip('\n'))

    threading.Thread(target=pump, daemon=True).start()
    threading.Thread(target=pump_err, daemon=True).start()
    requests = [
        {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
         'params': {'protocolVersion': types.LATEST_PROTOCOL_VERSION, 'capabilities': {},
                    'clientInfo': {'name': 'raw-probe', 'version': '0'}}},
        {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
         'params': {'name': 'dom_snapshot', 'arguments': {'branch': 'AA'}}},
    ]
    responses = {}
    raw_lines = []
    try:
        for request in requests:
            process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        deadline = time.time() + 60
        while time.time() < deadline and len(responses) < 3:
            line = frames.get(timeout=max(0.1, deadline - time.time()))
            if line is None:
                break
            raw_lines.append(line.rstrip('\n'))
            document = json.loads(line)
            assert document.get('jsonrpc') == '2.0'
            if 'id' in document:
                responses[document['id']] = document
        assert sorted(responses) == [1, 2, 3], responses
    finally:
        try:
            process.stdin.close()
        except OSError:
            pass
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    assert process.poll() is not None
    assert len(raw_lines) >= 3
    initialized = responses[1]['result']
    assert initialized['serverInfo']['name'] == 'omh-dom-mockup'
    assert initialized['protocolVersion'] == types.LATEST_PROTOCOL_VERSION
    listed = responses[2]['result']['tools']
    assert {t['name'] for t in listed} == TOOL_NAMES
    called = json.loads(responses[3]['result']['content'][0]['text'])
    assert called['status'] == 'NOT_INITIALIZED'
    transcript = dict(argv=server_argv(tmp_path, 'author'), requests=requests, responses=responses,
                      stdout_frames=raw_lines, stderr_tail=stderr_lines[-20:], exit_code=process.returncode)
    (LOGS / 'AB001_mcp_transcript.json').write_text(json.dumps(transcript, indent=1), encoding='utf8')
    (LOGS / 'AB001_mcp_handshake.log').write_text(
        '\n'.join(['# raw stdio MCP transcript (ids 1,2,3 correlated on the wire)'] +
                  [json.dumps(r, sort_keys=True) for r in requests] +
                  ['# stdout frames'] + raw_lines), encoding='utf8')


def _policy():
    from mockup.fixtures import POLICY
    return POLICY


def test_unknown_tool_is_a_structured_error(tmp_path):
    """M2: an undeclared tool name is a structured refusal, not ``repr(KeyError)``."""

    async def scenario():
        async with stdio_client(parameters(tmp_path, 'author')) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool('dom_delete_everything', {'branch': 'AA'})
                return result.isError, text(result), result.structuredContent

    is_error, payload, structured = asyncio.run(scenario())
    assert is_error is True
    assert payload['status'] == 'UNKNOWN_TOOL'
    assert set(payload['error']) == {'code', 'tool', 'message'}
    assert payload['error']['code'] == 'UNKNOWN_TOOL'
    assert payload['error']['tool'] == 'dom_delete_everything'
    assert structured is not None and structured['error']['code'] == 'UNKNOWN_TOOL'
    assert not (tmp_path / 'dom.sqlite3').exists()


def test_server_refuses_file_directory_and_conflicting_simulation_flags(tmp_path):
    """M5: a file passed as ``--directory`` and both simulation flags are clean refusals."""
    target = tmp_path / 'not-a-directory.txt'
    target.write_text('x', encoding='utf8')
    as_file = subprocess.run(server_argv(target, 'author'), cwd=str(ROOT), env=child_env(),
                             capture_output=True, text=True, encoding='utf8', timeout=60)
    assert as_file.returncode == 2, (as_file.stdout, as_file.stderr)
    assert 'REFUSED' in as_file.stderr and 'Traceback' not in as_file.stderr
    assert as_file.stdout == ''

    conflicting = subprocess.run([sys.executable, '-B', '-m', 'mockup.server', '--directory', str(tmp_path),
                                  '--role', 'author', '--simulation', '--no-simulation'],
                                 cwd=str(ROOT), env=child_env(), capture_output=True, text=True,
                                 encoding='utf8', timeout=60)
    assert conflicting.returncode == 2, (conflicting.stdout, conflicting.stderr)
    assert 'not allowed with' in conflicting.stderr and 'Traceback' not in conflicting.stderr


def test_ready_for_owner_review_is_reachable_over_mcp(tmp_path):
    """F2: a pure MCP client must be able to drive pending outbox to ack.

    Two real child servers (author + reviewer) over stdio; every mutation goes
    through a tool call.  ``dom_sync`` is the only path that clears
    ``SYNC_PENDING``, and ``dom_append`` must not admit anything by itself.
    """
    from mockup.fixtures import item, amendment

    async def scenario():
        async with stdio_client(parameters(tmp_path, 'author')) as (ar, aw):
            async with ClientSession(ar, aw) as author:
                await author.initialize()
                async with stdio_client(parameters(tmp_path, 'reviewer')) as (rr, rw):
                    async with ClientSession(rr, rw) as reviewer:
                        await reviewer.initialize()
                        record = {'steps': []}

                        def note(label, value):
                            record['steps'].append({'step': label, 'value': value})
                            return value

                        async def admit(tool, payload, key):
                            recorded = text(await author.call_tool(tool, {'payload_json': json.dumps(payload)}))
                            assert recorded['status'] == 'RECORDED_CANDIDATE', recorded
                            reviewed = text(await reviewer.call_tool('dom_review',
                                                                     {'candidate_id': recorded['candidate_id'],
                                                                      'intent_digest': recorded['intent_digest']}))
                            assert reviewed['status'] == 'DEMO_REVIEWED', reviewed
                            admitted = text(await reviewer.call_tool('dom_admit',
                                                                     {'candidate_id': recorded['candidate_id'],
                                                                      'review_id': reviewed['review_id'],
                                                                      'idempotency_key': key,
                                                                      'intent_digest': recorded['intent_digest']}))
                            assert admitted['status'] == 'DEMO_ADMITTED', admitted
                            return recorded, admitted

                        note('init', text(await author.call_tool('dom_init', {'external_work_ref': WORK,
                                                                              'policy_digest': POLICY})))
                        _, first = await admit('dom_submit', package(), 'mcp-ready-1')
                        claim = first['claim_ids']['one']
                        await admit('dom_submit', package('mcp-ready-2', revision=1,
                                                          items=[item('two', requirements=['R2'])]), 'mcp-ready-2')
                        await admit('dom_submit', package('ab', 'AB',
                                                          items=[item('ab', branches=['AB'],
                                                                      requirements=['R1', 'R2'])]), 'mcp-ready-3')
                        appended = await admit('dom_append', amendment('mcp-conv-aa', '', 'converge', {}, 2),
                                               'mcp-ready-4')
                        note('append_returns_candidate', appended[0])
                        await admit('dom_append', amendment('mcp-conv-ab', '', 'converge', {}, 1, 'AB'),
                                    'mcp-ready-5')

                        before = note('trace_before_sync', text(await reviewer.call_tool('dom_trace',
                                                                                        {'branch': 'master'})))
                        assert before['ready_for_owner_review'] is False, before
                        assert 'SYNC_PENDING' in before['blockers'], before
                        note('sync_status_pending', text(await reviewer.call_tool('dom_sync_status',
                                                                                 {'branch': 'AA'})))
                        note('sync_aa', text(await reviewer.call_tool('dom_sync', {'branch': 'AA'})))
                        note('sync_ab', text(await reviewer.call_tool('dom_sync', {'branch': 'AB'})))
                        note('sync_status_ack', text(await reviewer.call_tool('dom_sync_status',
                                                                             {'branch': 'AA'})))
                        after = note('trace_after_sync', text(await reviewer.call_tool('dom_trace',
                                                                                      {'branch': 'master'})))
                        note('query_historical', text(await author.call_tool('dom_query',
                                                                            {'branch': 'AA', 'revision': 1})))
                        note('resume', text(await author.call_tool('dom_resume', {'branch': 'AA'})))
                        note('claim_id', claim)
                        return record

    evidence = asyncio.run(scenario())
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / 'AB002_mcp_ready.json').write_text(json.dumps(evidence, indent=1, sort_keys=True), encoding='utf8')
    steps = {step['step']: step['value'] for step in evidence['steps']}

    assert steps['init']['status'] == 'INITIALIZED'
    assert steps['append_returns_candidate']['status'] == 'RECORDED_CANDIDATE'
    assert steps['trace_before_sync']['readiness'] == 'NOT_READY'
    assert all(intent['state'] == 'pending' for intent in steps['sync_status_pending']['intents'])
    assert steps['sync_aa']['status'] == 'SYNCED' and steps['sync_ab']['status'] == 'SYNCED'
    assert all(intent['state'] == 'ack' for intent in steps['sync_status_ack']['intents'])
    assert steps['trace_after_sync']['ready_for_owner_review'] is True, steps['trace_after_sync']
    assert steps['trace_after_sync']['blockers'] == [], steps['trace_after_sync']
    assert steps['trace_after_sync']['chain']['status'] == 'CHAIN_OK'
    assert steps['trace_after_sync']['owner_close_called'] is False
    assert steps['query_historical']['revision'] == 1
    assert len(steps['query_historical']['claims']) == 1
    assert steps['resume']['status'] == 'RESUMED'
    assert steps['resume']['trace']['ready_for_owner_review'] is True
