# AB004 / AU004-F-01 — public schema change (written by Worker)

Aim: an MCP caller must not learn the **names (keys)** of branches outside its launch-time grant through the branch-keyed maps `dependencies` (and `revisions`). Rule "scope-first": keys of foreign branches are **removed** from the public output — no mask, no counter, no "hidden" marker. Internal storage, admission, trace stale-check, readiness/blockers, internal integrity proof and the delivery observation stamp are **not** changed.

Code digest before: `08aa9a9b978831806bd0ef24fe26f7214ab21b31ca6d2bbe7d27a61bd29bfe6f` (16 files, SEC003/AB003 method)
Code digest after:  `1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf` (16 files)
Changed files (3 of 16): `mockup/public_dto.py` (main), `mockup/admission.py` (pass the caller grant into the projection; point edits, 10 lines), `mockup/server.py` (1 line). `projections.py`, `delivery.py`, `storage.py`, `ports.py`, `dom_contract.py` — untouched.

## Inventory of `('map', …)` fields in the public schema

| Field | Keys are | Before | After |
|---|---|---|---|
| `Claim.dependencies` | branches | `('map','int')`, unfiltered (**defect**) | `('bmap','int')` — filtered by caller grant |
| `Provenance.dependencies` (in `History[].provenance`, both claim and append events) | branches | `('map','int')`, unfiltered (**defect**) | `('bmap','int')` — filtered by caller grant |
| `ReadSnapshot.revisions` | branches | `('map','int')`; already scoped by the builder `read_snapshot(stamp, scope)` | `('bmap','int')` — same result, now also enforced by the schema layer (defence in depth) |
| `Claim.properties` | user property names (opaque user data, `str→str`) | unchanged | unchanged (not branch-keyed) |
| `Trace.origins` | claim ids | unchanged | unchanged |
| `Admitted.claim_ids`, `Admitted.event_ids` | caller-supplied local ids | unchanged | unchanged |

No other `('map', …)` exists in `RECORDS`. Opaque slots (`ClaimItem.metadata`) are user data and untouched.

## Mechanism

* `public_dto._project(value, spec, path, scope)` — `scope` threaded through every recursive call.
* New spec token `('bmap', V)`: dict keyed by branch; only keys in `scope` are projected and kept, other entries are dropped without being looked at; non-`str` key → `INVALID_KEY`; `scope is None` → fail-closed `PublicProjectionError('SCOPE_REQUIRED')` (never "copy everything").
* `project(obj, name, scope=None)` and `project_tool(name, result, scope=None)`; `scope` = `Service.context.branches` (the **launch grant** — the same set `Service.scope()` enforces; not a tool argument, no new tool/grant).
* `admission.py`: `query`, `resume`, `trace`, `export`, `sync_status`, `sync` pass `scope=self.context.branches`; `server.py` passes `scope=service.context.branches`. Both channels (text and `structuredContent`) serialize the one projected object (second projection in `server.py` is idempotent).
* **YAML export**: `Service._export` now builds the bytes from `public_dto.project(snapshot, 'Snapshot', scope=context.branches)` — the same filtered object as `dom_query`. This also applies to YAML written by `dom_sync` (delivery). Ack check `delivery.confirmed()` only needs `branch`/`revision` from the YAML, so acknowledgement is unaffected.

## Semantics by caller (verified E2E, see runtime/AB004)

| Caller grant | Claim written with deps | Public `dependencies` |
|---|---|---|
| `AA` | `{AA:n, AB:m}` | `{AA:n}` |
| `AA` | `{AB:m}` | `{}` |
| `AB` | `{AA:n, AB:m}` | `{AB:m}` |
| `AA,AB` | `{AA:n, AB:m}` | `{AA:n, AB:m}` (unchanged) |
| `AA` | stored map contains a key `ZZ` outside any grant | `ZZ` (and other foreign keys) dropped |

## What is NOT changed (by design)

* `claim_snapshots.dependencies` and event `payload.dependencies` (hash-chained) keep the **full** maps — verified identical pre/post by SQL read-back.
* `trace_branch` stale check uses the full internal dependencies; `admit` stale-review check, `check_references`, outbox/delivery stamps (`chain_head`, all revisions, `port_reported`) are unchanged.
* Gate: corrupted chain still returns the uniform `Broken` DTO (`status, readiness, ready_for_owner_review, blockers, simulated`) with no foreign locator.

## Observations (not changed, not widened)

1. **Staleness side channel.** `Trace.residual[].reasons` contains `STALE_CHECK` and the stale claim drops out of `claim_refs`; neither names a branch. But for a claim whose AB-only dependency was filtered to `{}` (scenario b, seed 6643), after AB advances the AA-only caller sees `STALE_CHECK` and `claim_refs` shrinks 2→1 while the claim's visible `dependencies` is `{}`. The caller can therefore infer *that the claim depends on something whose head moved*, not *which* branch. This is a residual existence signal; per the task it is not widened here (decision for the owner: accept, or report staleness without a cause only for fully visible dependencies).
2. **Not a map, not in scope:** branch names that appear as list/scalar values (`applicable_branches`, `origin_branch` on a claim shared into the caller's branch by an applicability event, `excluded_branches`, applicability/exclude event values) are unchanged. AU004 X2 (`origin_branch=AB` visible in an AA projection) therefore still reproduces in the regression re-run; it is a separate, previously known AU004 observation, not AU004-F-01.
3. The documented failing test `test_event_chain_is_verified_and_forgery_is_detected` (Chain is intentionally status-only, TD19) is unchanged and still the only failure.

`product_acceptance=false`, `is_approval=false`. Debt is not closed here; closure needs independent reviewer + auditor on this version.
