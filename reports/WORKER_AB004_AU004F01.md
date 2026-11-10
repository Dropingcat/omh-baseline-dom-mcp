# WORKER AB004 — AU004-F-01 (dependencies maps without scope filter)

Verdict (written by the Worker): **F-01 closed on own E2E; independent review/audit still required.** `product_acceptance=false`, `is_approval=false`, debt not closed.
Continuation 01 of the same role (first run died on the provider, changed nothing). Digest recomputed first: `08aa9a9b…` (16 files) = expected.

## Defect and rule
AA-only caller received `dependencies={AA:n, AB:m}` in `Claim.dependencies` / `Provenance.dependencies` (query, snapshot, resume) and in YAML export bytes; only `read_snapshot.revisions` was grant-filtered. Rule scope-first: foreign branch keys are **removed** (no marker/counter). Internal storage/admission/stale check/delivery stamp unchanged.

## Change (digest `08aa9a9b…` → `1ead2d45373e…`, 3 of 16 files)
* `mockup/public_dto.py`: new spec `('bmap', V)`; `Claim.dependencies`, `Provenance.dependencies`, `ReadSnapshot.revisions` use it; `project()/project_tool()` take `scope`; `scope=None` + bmap → fail-closed `SCOPE_REQUIRED`.
* `mockup/admission.py` (point edits): pass `scope=self.context.branches` in query/resume/trace/export/sync_status/sync; `_export` builds YAML from the filtered public `Snapshot`.
* `mockup/server.py`: `project_tool(..., scope=service.context.branches)`.
* Map inventory: only those three are branch-keyed (details in `docs/SCHEMA_CHANGE_AU004F01.md`).

## E2E (real MCP stdio, own seeds 5521/6643/8817/4409/7931/3377, raw frames, PID/exit, SQL oracle)
PRE = original code (byte-identical private copy `runtime/AB004/precopy`, digest 08aa9a9b), POST = patched tree. Same script `ab004_e2e.py`. Each reader gets its own copy of the run dir. Oracle: SQL `claim_snapshots`/event payload full maps filtered by the grant, compared with every Claim/Provenance map on query/snapshot/resume/query@rev1 and parsed YAML.

| Var | Seed, AA/AB heads | Writer deps | Reader | PRE query deps / YAML | POST query deps / YAML | Verdict |
|---|---|---|---|---|---|---|
| a | 5521, 2/2 | AA:2,AB:2 | AA-only | {AA:2,AB:2} / `AB: 2` | {AA:2} / no AB line | leak → closed |
| b | 6643, 1/2 | AB:2 | AA-only | {AB:2} / `AB: 2` | {} / no dep lines | leak → closed |
| c | 8817, 1/2 | AA:1,AB:2 | union | full | full (unchanged) | no leak, both |
| d | 4409, 1/3 | on **AB** claim AA:1,AB:3 | AB-only (union control) | {AA:1,AB:3} / `AA: 1` | {AB:3} / no AA line (union still full) | leak → closed |
| e | 7931, 1/3 | stored map with foreign `ZZ` (legit ZZ submit is `REJECTED`; ZZ put into `claim_snapshots` of a disposable dir by operator fixture) | AA-only | {AA:1,AB:3,ZZ:4} / `ZZ: 4` | {AA:1} / none | leak → closed |
| f | (a,b,d,e YAML) | – | – | foreign `\bAB\b`/`ZZ`/canary raw+b64 in bytes | 0 lines with foreign branch word, 0 canary tokens in every `exports/*.yaml`; YAML maps == oracle | closed |
| g | 3377, 2/3 | corrupt AB event (invalid-utf8 and wrong-hash variants), 2 PIDs × 7 tools each | AA-only | uniform `Broken` | identical, keys exactly `{status, readiness, ready_for_owner_review, blockers, simulated}`, no locator/oracle event id, DB sha unchanged | TD19 intact |

Counts (from `pre_post_comparison.json`): foreign dict keys on public surfaces 6/6/6/9 → 0; oracle mismatches 6/6/6/6 → 0; internal `claim_snapshots` and event dependency maps identical pre/post in all six; internal delivery stamp after sync still full (`chain_head`, AA+AB revisions, `port_reported`); text == structuredContent on all surfaces; all server processes exit 0.

## Regression (patched tree)
* `pytest -q tests`: 63 passed, 1 failed = the documented `test_event_chain_is_verified_and_forgery_is_detected` only. (A first `pytest -q` from the project root collected `runtime/**` copies and failed to collect – kept as `regress/pytest-q-rootcollect-ERROR.txt`, not a code result.)
* AB003 smoke: `SMOKE_OK`; AB003 e2e post (seed 3101): A2-01/02 `LEAK_CLOSED`, A2-03 `GATE_UNIFORM_SAFE`, DEL-01 `PASS`; RV004 post (7107): same + B-SIDE `PASS`.
* AU004 probe rerun (copy with redirected OUT; original AU004 artifacts untouched): **X1 = LEAK_CLOSED** (`[]`; originally `AB: 2` at YAML lines 9/104), X3 uniform Broken/no locator, X4 internal stamp full + no duplicate writes, X5 no AB canary in YAML.

## Observations (not widened)
1. Staleness side channel: `STALE_CHECK` names no branch, but (scenario b, post) a claim with visible `dependencies={}` becomes stale and `claim_refs` drops 2→1 after AB advances – the AA-only caller can infer that some dependency moved, not which branch. Owner decision.
2. AU004 X2 (`origin_branch=AB` on a claim shared into AA via applicability) still reproduces; it is a value, not a map – out of scope.

## Limits / notes
* pre_v2 ran from a private copy because the product tree was already patched; digest of the copy verified = `08aa9a9b…`. Earlier harness v1 outputs (`pre`, `post_harness_v1`, `pre_first_a_only`) kept; v1 shared one `exports/` between readers, which only mislabelled the "union" reader in post.
* The ZZ case is a fixture injection (API refuses ZZ), so it demonstrates the output filter, not an API write path.
* Files written: the 3 mockup files, `docs/SCHEMA_CHANGE_AU004F01.md`, `artifacts/WORKER_AB004_AU004F01.json`, this report, `runtime/AB004/**` (+ the suite's own `runtime/tmp`).
