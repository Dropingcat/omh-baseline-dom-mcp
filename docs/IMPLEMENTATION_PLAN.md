# DOM ↔ OMH Mockup Implementation Plan

> **For Hermes:** Use subagent-driven-development task-by-task. Worker implements, independent reviewer checks spec, then quality/security reviewer. No self-acceptance.

**Goal:** runnable local synthetic DOM/MCP mockup, physically exercised and traceable to REQUIREMENTS.md and T01–T20.

**Architecture:** SQLite append-only facts + derived branch heads, one service write path, trusted simulation adapters, thin stdio MCP. YAML is derivative, OMH remains owner.

**Tech Stack:** exact harness Python3.11.15, stdlib SQLite/hashlib/uuid/json, existing PyYAML/MCP/pytest. No install/config/Git mutation.

## Unit of delivery AB001

Paths are relative to project E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. All source writes assigned to this worker; no concurrent implementer in same paths. Execute as vertical slices, testing each before the next. Do not write all imagined tests first or entire implementation without exercising it.

### Slice 1 — Contract through rejection

Create mockup/dom_contract.py, initial tests/test_dom_contract.py, synthetic fixtures. First runnable failing behavior: malformed package with multiple known violations must return aggregated safe REJECTED and not create DB. Run RED, implement minimal validator/canonicalizer, run GREEN. Add seven content types and exact source byte vectors incrementally. Evidence T01/T10/T12. Freeze examples and expected canonical-envelope digests produced by the actual implementation, not fabricated.

### Slice 2 — Persistent candidate/admission tracer

Create mockup/storage.py, ports.py and admission.py. First test candidate is not admitted; implement init→submit→demo reviewer→admit→read-back. Add fixed test context identities, self/helper/forged/production fail-closed tests; SQLite triggers and immutable raw refs. Evidence T01/T02/T05/T13. Read PRAGMA actual values. No external operations during admission transaction.

### Slice 3 — Replay/race/crash

Create tests/test_storage_faults.py with process entry helpers (Windows spawn-safe). Physical tests: same-key lost reply after COMMIT, changed payload, two processes same branch rev with barrier, process exit before COMMIT then reopen, unrelated branch vs exact dependency. Implement only needed OCC/dedupe/recovery improvements. Evidence T03–T07. Log command/exit/state before/after. Bound waits/joins; child processes never survive test completion.

### Slice 4 — Append events, branches, trace and outbox

Create mockup/projections.py and tests/test_scope_trace.py. Route comment/link/property/applicability/archive/replacement through candidate/review/admit, preserve old records and branch origin. Add synthetic owner requirements+branch convergence policy and pending/ambiguous/ack external target fixture. Export scoped historical revision YAML deterministically to server-fixed path and read back bytes/hash; denied requests cannot create export. Evidence T08/T09/T11/T13–T18/T20. GitPort mutations remain NOT_IMPLEMENTED; describe dirty snapshot and merge intentions work on fixtures.

### Slice 5 — Actual stdio MCP

Create mockup/server.py, tests/test_mcp_stdio.py. Use installed SDK source for APIs. Client stdio subprocess → initialize → list_tools → call dom_init/query/invalid/denied; capture negotiated protocol/serverInfo/schema and correlation from actual transport. Minimal explicit Windows env must include SYSTEMROOT/WINDIR/COMSPEC/TEMP/TMP, PATH and required locator vars; TMP points only project runtime/. Stdout JSONRPC only. Evidence T19, no live registration. Server role/trust assigned at launch; never caller role arg.

### Slice 6 — Reproducible demo and manifest

Create mockup/demo.py (module CLI), mockup/README.md and runtime/AB001_RESULT.{md,json}. One exact command from project root runs a fresh synthetic fixture, creates real DB and YAML, prints trace and output paths; --output-dir limited under runtime/. Existing demo output is not silently overwritten unless explicit reset confined to disposable generated artifacts, never source deletion. Prefer a new run directory per invocation.

Test command from project root:
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q

Demo command (implement and document):
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.demo

Before finish: run compileall with pycache prefix inside runtime/ or -B AST parse, full tests, demo, list physical artifacts. Populate result JSON with actual per-T01–T20 evidence, not test-name claims alone; mark missing honestly. Worker status not independent APPROVE.

## AC001 — Independent specification review

Separate card/agent; read original user words, SPEC, AA002 acceptance matrix and implementation. Test actual paths/invariants, not only unit summaries. No source edits. If REQUEST_CHANGES, return exact gaps to worker and repeat on changed revision. Do not ask worker to approve itself.

## AC002 — Quality/security review

After spec-compliant: separate context reviews schema coercion, privilege forging, scope leakage (query/trace/export/outbox/errors), SQL immutability, stale dependency/replay ordering, digest rules, historical export and process cleanup. Run independent tests+demo from a clean runtime subdirectory. No live endpoints; identify inability to enforce OS identity.

## Parent closure

Run documented demo/test commands, verify report and YAML+DB physical facts and residual. Produce short report: what exists, what was observed, what remains live/production. No Git merge and no master close.
