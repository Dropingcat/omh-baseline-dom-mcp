"""Real stdio MCP server over the synthetic DOM service.

Trust boundary: ``--profile``, ``--role`` and ``--simulation`` are *launch* arguments supplied by
the trusted local launcher (the test harness / demo).  No tool accepts a role,
principal, capability set or work ref override, so a model-facing caller cannot
promote itself.  This is a documented simulation adapter, not authentication:
it proves the protocol path and the domain gates, not host identity.

stdout carries MCP JSON-RPC frames only; diagnostics go to stderr / ``--log-file``.
"""
import argparse
import json
import sys
from pathlib import Path

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from .admission import Service
from . import claim_entry as claim_entry_mod
from . import public_dto

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / 'runtime').resolve()
ROLES = ('author', 'helper', 'reviewer', 'owner')
PROFILES = ('strict', 'lite')
INSTRUCTIONS = ('Synthetic DOM/OMH laboratory. All evidence is simulated; no live '
                'OMH, Git or issuer calls. Identity is assigned at launch, never by a tool call.')
INSTRUCTIONS_LITE = ('Simulated DOM server, lite (local_single_owner) profile. The SQLite database in this directory is real; '
                     'OMH/Git targets are simulated. Cold start: call dom_describe({}), then dom_start({"request": "<customer request>"}), '
                     'then dom_claim per claim, dom_find to look up, dom_update to change a claim (new version), dom_trace for readiness. '
                     'Every refusal carries a hint and next_action. Profile and identity are fixed at launch; no tool argument can change them.')


class ToolInput(Exception):
    """Bad MCP tool arguments. Reported as a structured transport error."""


TOOLS = [
    types.Tool(
        name='dom_init',
        description='Create/verify the work binding in the given run directory. Simulated.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'external_work_ref': {'type': 'string'},
                                    'policy_digest': {'type': 'string'}},
                     'required': ['external_work_ref', 'policy_digest']}),
    types.Tool(
        name='dom_resume',
        description='Resume a branch: scoped snapshot + trace + outbox status + pending-work section in one '
                    'read-only call. pending: exact in-grant count + a metadata-only page (limit/after keyset).',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'},
                                    'limit': {'type': 'integer', 'minimum': 1, 'maximum': 500},
                                    'after': {'type': 'string'}},
                     'required': ['branch']}),
    types.Tool(
        name='dom_submit',
        description='Submit a restricted-JSON candidate package (claims or append events). Not admitted.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'payload_json': {'type': 'string'}},
                     'required': ['payload_json']}),
    types.Tool(
        name='dom_review',
        description='Record an independent demo review of an exact candidate digest.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'candidate_id': {'type': 'string'},
                                    'intent_digest': {'type': 'string'}},
                     'required': ['candidate_id', 'intent_digest']}),
    types.Tool(
        name='dom_admit',
        description='Atomic admission of a reviewed candidate (facts, events, head, outbox).',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'candidate_id': {'type': 'string'},
                                    'review_id': {'type': 'string'},
                                    'idempotency_key': {'type': 'string'},
                                    'intent_digest': {'type': 'string'}},
                     'required': ['candidate_id', 'review_id', 'idempotency_key', 'intent_digest']}),
    types.Tool(
        name='dom_append',
        description='Record an append event batch (comment/link/property/applicability/archive/...) as a candidate. '
                    'It still needs dom_review + dom_admit; it is not an admission bypass.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'payload_json': {'type': 'string'}},
                     'required': ['payload_json']}),
    types.Tool(
        name='dom_query',
        description='Scoped branch snapshot at the head revision or an exact historical revision.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'},
                                    'revision': {'type': 'integer', 'minimum': 0}},
                     'required': ['branch']}),
    types.Tool(
        name='dom_snapshot',
        description='Compatibility alias of dom_query (kept for existing clients; same result schema).',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'},
                                    'revision': {'type': 'integer', 'minimum': 0}},
                     'required': ['branch']}),
    types.Tool(
        name='dom_trace',
        description='Coverage/stale/conflict/pending trace. Readiness only; never closes the owner task.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'}},
                     'required': []}),
    types.Tool(
        name='dom_export',
        description='Deterministic scoped YAML export to a server-fixed path inside the run directory.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'},
                                    'revision': {'type': 'integer', 'minimum': 0}},
                     'required': ['branch']}),
    types.Tool(
        name='dom_sync_status',
        description='Outbox status per intent (pending/attempt/ack/error/ambiguous). Read-only.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'}},
                     'required': ['branch']}),
    types.Tool(
        name='dom_sync',
        description='Deliver the synthetic outbox for a branch (YAML export + simulated OMH attach with read-back). '
                    'Requires the launch-time admit capability; returns SYNCED or SYNC_PENDING.',
        inputSchema={'type': 'object', 'additionalProperties': False,
                     'properties': {'branch': {'type': 'string'}},
                     'required': ['branch']}),
]

LITE_SIGNATURE = {
    'dom_describe': ({}, {}),
    'dom_start': ({}, {'request': str, 'goal': str, 'branches': list, 'adopt': bool}),
    'dom_claim': ({'branch': str, 'type': str, 'text': str}, dict(claim_entry_mod.COMMON_FIELDS, **claim_entry_mod.FIELD_TYPES)),
    'dom_update': ({'claim_id': str, 'text': str, 'reason': str}, {}),
    'dom_find': ({}, {'query': str, 'branch': str, 'type': str, 'requirement_ref': str, 'limit': int}),
}
# dom_start/dom_find accept requests with a missing 'request' so that the refusal can carry a hint
# (a transport-level INVALID_ARGUMENTS cannot); everything else is matched exactly.

SIGNATURE = {
    'dom_init': ({'external_work_ref': str, 'policy_digest': str}, {}),
    'dom_resume': ({'branch': str}, {'limit': int, 'after': str}),
    'dom_submit': ({'payload_json': str}, {}),
    'dom_review': ({'candidate_id': str, 'intent_digest': str}, {}),
    'dom_admit': ({'candidate_id': str, 'review_id': str, 'idempotency_key': str, 'intent_digest': str}, {}),
    'dom_append': ({'payload_json': str}, {}),
    'dom_query': ({'branch': str}, {'revision': int}),
    'dom_snapshot': ({'branch': str}, {'revision': int}),
    'dom_trace': ({}, {'branch': str}),
    'dom_export': ({'branch': str}, {'revision': int}),
    'dom_sync_status': ({'branch': str}, {}),
    'dom_sync': ({'branch': str}, {}),
}


STRICT_TOOL_NAMES = frozenset(t.name for t in TOOLS)
LITE_TOOLS = [types.Tool(name=n, description=claim_entry_mod.compose_description(n), inputSchema=claim_entry_mod.input_schema(n))
              for n in claim_entry_mod.LITE_TOOL_NAMES]
LITE_TOOL_NAMES = frozenset(claim_entry_mod.LITE_TOOL_NAMES)
SIGNATURE.update(LITE_SIGNATURE)


def tools_for(profile):
    return LITE_TOOLS if profile == 'lite' else TOOLS


def argument_hint(name):
    if name not in SIGNATURE:
        return 'Unknown tool. Use tools/list (lite profile: dom_describe).'
    required, optional = SIGNATURE[name]
    return ('Arguments of %s are matched exactly (no unknown keys, no wrong types). Required: %s. Optional: %s. '
            'profile, review_level, principal and work are fixed at launch and cannot be passed.'
            % (name, ', '.join(required) or 'none', ', '.join(optional) or 'none'))


def strict_arguments(name, arguments):
    """Bind arguments exactly: no coercion, no unknown keys, no defaulted identity."""
    if arguments is None:
        arguments = {}
    if type(arguments) is not dict:
        raise ToolInput('INVALID_ARGUMENTS')
    required, optional = SIGNATURE[name]
    allowed = dict(required, **optional)
    if set(arguments) - set(allowed) or set(required) - set(arguments):
        raise ToolInput('INVALID_ARGUMENTS')
    for key, expected in allowed.items():
        if key in arguments and type(arguments[key]) is not expected:
            raise ToolInput('INVALID_ARGUMENTS')
    return arguments


def dispatch(service, name, arguments):
    visible = LITE_TOOL_NAMES if service.profile == 'lite' else STRICT_TOOL_NAMES
    if name not in SIGNATURE or name not in visible:
        raise ToolInput('UNKNOWN_TOOL')
    args = strict_arguments(name, arguments)
    if name == 'dom_describe':
        return service.describe()
    if name == 'dom_start':
        return service.start(args.get('request'), args.get('goal'), args.get('branches'), args.get('adopt', False))
    if name == 'dom_claim':
        extra = {k: v for k, v in args.items() if k not in ('branch', 'type', 'text')}
        return service.claim(args['branch'], args['type'], args['text'], **extra)
    if name == 'dom_update':
        return service.update(args['claim_id'], args['text'], args['reason'])
    if name == 'dom_find':
        return service.find(args.get('query'), args.get('branch'), args.get('type'), args.get('requirement_ref'), args.get('limit', 20))
    if name == 'dom_init':
        return service.init(dict(args))
    if name == 'dom_resume':
        return service.resume(args['branch'], args.get('limit', 50), args.get('after'))
    if name == 'dom_submit':
        return service.submit(args['payload_json'])
    if name == 'dom_review':
        return service.review(args['candidate_id'], args['intent_digest'])
    if name == 'dom_admit':
        return service.admit(args['candidate_id'], args['review_id'], args['idempotency_key'], args['intent_digest'])
    if name == 'dom_append':
        return service.append(args['payload_json'])
    if name in ('dom_query', 'dom_snapshot'):
        return service.query(args['branch'], args.get('revision'))
    if name == 'dom_trace':
        return service.trace(args.get('branch', 'master'))
    if name == 'dom_export':
        return service.export(args['branch'], args.get('revision'))
    if name == 'dom_sync_status':
        return service.sync_status(args['branch'])
    if name == 'dom_sync':
        return service.sync(args['branch'])
    # Declared in SIGNATURE but not routed here: still a structured refusal, never
    # a silent None returned to the caller.
    raise ToolInput('UNKNOWN_TOOL')


def build_server(service, log_path=None):
    server = Server('omh-dom-mockup', version='0.1.0')

    def log(record):
        line = json.dumps(record, sort_keys=True)
        print('[dom-mockup] ' + line, file=sys.stderr, flush=True)
        if log_path is not None:
            with open(log_path, 'a', encoding='utf8') as handle:
                handle.write(line + '\n')

    @server.list_tools()
    async def list_tools():
        return tools_for(service.profile)

    @server.call_tool(validate_input=False)
    async def call_tool(name, arguments):
        try:
            result = dispatch(service, name, arguments)
            public = public_dto.project_tool(name, result, scope=service.context.branches, profile=service.profile)
        except ToolInput as error:
            code = str(error)
            payload = {'status': code,
                       'error': {'code': code, 'tool': name,
                                 'message': 'Tool call refused by the transport contract; nothing was executed.'},
                       'hint': argument_hint(name) if code == 'INVALID_ARGUMENTS' else public_dto.error_help(code, service.profile).get('hint', '')}
            log({'tool': name, 'status': code, 'principal': service.context.principal})
            return types.CallToolResult(
                content=[types.TextContent(type='text', text=json.dumps(payload, ensure_ascii=True, sort_keys=True))],
                structuredContent=payload, isError=True)
        except Exception as error:
            # Fail closed: a projection refusal or any internal fault becomes a
            # fixed typed enum; raw exception details are never serialized to
            # the caller. The operator log carries the exception type only.
            code = 'PUBLIC_PROJECTION_INVALID' if isinstance(error, public_dto.PublicProjectionError) else 'INTERNAL_ERROR'
            payload = {'status': code,
                       'error': {'code': code, 'tool': name,
                                 'message': 'Tool processing refused; no details exposed.'},
                       'hint': public_dto.error_help(code, service.profile).get('hint', '')}
            log({'tool': name, 'status': code, 'principal': service.context.principal,
                 'error_type': type(error).__name__})
            return types.CallToolResult(
                content=[types.TextContent(type='text', text=json.dumps(payload, ensure_ascii=True, sort_keys=True))],
                structuredContent=payload, isError=True)
        record = {'tool': name, 'status': public.get('status'), 'simulated': service.context.simulation,
                  'principal': service.context.principal}
        log(record)
        return types.CallToolResult(
            content=[types.TextContent(type='text', text=json.dumps(public, ensure_ascii=True, sort_keys=True))],
            structuredContent=public, isError=False)

    return server


async def serve(service, log_path):
    server = build_server(service, log_path)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, InitializationOptions(
            server_name='omh-dom-mockup', server_version='0.1.0',
            capabilities=server.get_capabilities(NotificationOptions(), {}),
            instructions=INSTRUCTIONS_LITE if service.profile == 'lite' else INSTRUCTIONS))


def main(argv=None):
    parser = argparse.ArgumentParser(prog='mockup.server', description='Simulated DOM stdio MCP server.')
    parser.add_argument('--directory', required=True, help='run directory inside <project>/runtime')
    parser.add_argument('--role', default='author', choices=ROLES, help='trusted launch fixture identity (ignored by --profile lite)')
    parser.add_argument('--profile', default='strict', choices=PROFILES,
                        help='strict (default, the original behaviour) or lite (local_single_owner: single-call tools, review_level=self)')
    simulation = parser.add_mutually_exclusive_group()
    simulation.add_argument('--simulation', dest='simulation', action='store_true', default=True,
                            help='use the synthetic simulation adapter (default)')
    simulation.add_argument('--no-simulation', dest='simulation', action='store_false',
                            help='fail closed: every init is refused, no live binding exists')
    parser.add_argument('--log-file', default=None, help='optional JSONL diagnostic log inside runtime/')
    args = parser.parse_args(argv)

    directory = Path(args.directory).resolve()
    if not directory.is_relative_to(RUNTIME):
        print('REFUSED: --directory must resolve inside ' + str(RUNTIME), file=sys.stderr)
        return 2
    if directory.exists() and not directory.is_dir():
        print('REFUSED: --directory must be a directory, not a file: ' + str(directory), file=sys.stderr)
        return 2
    log_path = None
    if args.log_file:
        candidate = Path(args.log_file).resolve()
        if not candidate.is_relative_to(RUNTIME):
            print('REFUSED: --log-file must resolve inside ' + str(RUNTIME), file=sys.stderr)
            return 2
        candidate.parent.mkdir(parents=True, exist_ok=True)
        log_path = candidate
    directory.mkdir(parents=True, exist_ok=True)
    service = Service(directory, role=args.role, simulation=args.simulation, profile=args.profile)
    anyio.run(serve, service, log_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
