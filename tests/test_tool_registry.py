"""TD-DOM-35: one registry for tools, signatures, schemas and dispatch."""
from mockup import claim_entry, server

# dom_start's schema requires ``request`` (so a missing value is a typed domain
# refusal), while SIGNATURE keeps it optional so ``strict_arguments`` lets the
# request reach the handler.  This is the only documented exception.
DOCUMENTED_OPTIONAL = {'dom_start'}


def test_every_signature_has_a_dispatch_handler():
    assert set(server.HANDLERS) == set(server.SIGNATURE)


def test_visible_tool_names_match_the_registry():
    assert server.STRICT_TOOL_NAMES == set(server.SIGNATURE)
    # Lite exposes 5 lite-specific tools plus read/export/sync tools whose
    # signatures come from the strict table; every visible name must be routed.
    assert server.LITE_TOOL_NAMES <= set(server.SIGNATURE)
    assert set(server.LITE_SIGNATURE) <= server.LITE_TOOL_NAMES
    assert server.LITE_TOOL_NAMES <= server.STRICT_TOOL_NAMES
    assert {tool.name for tool in server.TOOLS} == server.STRICT_TOOL_NAMES
    assert {tool.name for tool in server.LITE_TOOLS} == server.LITE_TOOL_NAMES


def test_input_schemas_match_signatures():
    for tool in [*server.TOOLS, *server.LITE_TOOLS]:
        required, optional = server.SIGNATURE[tool.name]
        expected = set(required) | set(optional)
        if tool.name == 'dom_claim':
            # Per-type oneOf branches: same properties, required = common + type.
            for typ, branch in zip(claim_entry.TYPES, tool.inputSchema['oneOf']):
                assert set(branch['properties']) == expected, tool.name
                assert set(branch['required']) == set(required) | set(claim_entry.REQUIRED_FIELDS[typ]), tool.name
            continue
        properties = tool.inputSchema['properties']
        assert set(properties) == expected, tool.name
        schema_required = set(tool.inputSchema.get('required', []))
        if tool.name in DOCUMENTED_OPTIONAL:
            assert schema_required == {'request'}, tool.name
            assert set(required) == set(), tool.name
        else:
            assert schema_required == set(required), tool.name
