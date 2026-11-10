# AU007 — Auditor: negative acceptance of AB005 (WS-F04 + WS-F02)

- **Role**: AUDITOR (task = refute, not confirm)
- **Reviewed version**: `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7` (16 files) — digest independently recomputed and **matches**.
- **Worker claims**: `artifacts/WORKER_AB005.json`, `reports/WORKER_AB005.md`.

## Method
Independent probe harness (`runtime/AU007/au007_probe*.py`) re-using the AB003 raw MCP stdio client
(real subprocesses, real JSON-RPC frames, isolated DBs under `runtime/AU007/runs/`). No product files edited
(read-only on the mockup product). All destructive/negative cases ran on fresh isolated DB copies.

## Results (physical)

### C1 — Original defect, 2 PIDs (must now be `DIGEST_MISMATCH`)
AA candidate pkg submitted under grant {AA}; admit attempted with the prior AB admit-key + AB intent_digest.
- `C1_PID1`: **DIGEST_MISMATCH**, branch=None, no receipt. tx stays 1 (only the legit AB admission).
- `C1_PID2`: **DIGEST_MISMATCH**, branch=None, no receipt.
- Foreign receipt NOT returned on either PID. **PASS.**

### C2 — Bypass attempts
- Reuse AB key with the AA candidate's OWN digest → `IDEMPOTENCY_BINDING_MISMATCH` (L2 binding rejects; no receipt).
- Reuse the submit-style key name in admit → fresh legit `DEMO_ADMITTED` (not an AB receipt; new binding).
- Same AB admit via a different principal → `INDEPENDENCE_NOT_ENFORCED` (own launch root mismatch; separate operation namespace).
- **No path yielded the foreign AB receipt.** **PASS.**

### C3 — Migration (on legacy DB copy)
- Legacy idempotency row preserved as-is: `scope_digest=''`, `candidate_id=NULL`, digest and result bytes **unchanged**.
- `user_version=1` after single init; **1 again** after a second init → **idempotent rerun** confirmed.
- `legacy-key` admit → `IDEMPOTENCY_BINDING_UNKNOWN` (honest refusal, row not rewritten/not deleted).
- Fresh key after migration → `DEMO_ADMITTED`. **PASS.**

### C4 — Immutable triggers after migration (real SQL)
- `UPDATE idempotency ...` → `sqlite3.IntegrityError: IMMUTABLE` (real error, not only "we rebuilt them").
- `DELETE idempotency ...` → `IMMUTABLE`. **PASS.**

### C5 — result_scope ⊆ grant arbiter
- Unsafe narrowing (stored `result_scope={AA,AB}`, grant {AA}) → **`SCOPE_DENIED`**. **PASS.**
- Restore full grant replay → **`DEMO_ADMITTED`**. **PASS.**
- Safe narrowing (AA-only result, replay under {AA}) → **`DEMO_ADMITTED`**, receipt **byte-equal**, **all deltas 0**,
  branch=AA, `leak_outside_grant=false`. **PASS** (reproduced end-to-end in `C5B_safe_narrow`; an early
  `REVISION_CONFLICT` in `C5_SCOPE` was a probe sequencing bug — AA head had already advanced before the
  play candidate was admitted — not a product defect).

### C6 — Positive control (lost-answer replay, SQL before/after)
- first admit `DEMO_ADMITTED`, replay `DEMO_ADMITTED`, **receipt byte-equal**.
- idempotency rows `[2,2]` (submit+admit), **every** delta (transactions, events, outbox, delivery_attempts,
  delivery_observations, delivery_acks, idempotency, candidates, reviews) = **0**. **PASS.**

### C7 — F-04 surfaces (grant {AA,ZZ}: ZZ granted-but-absent)
- ZZ: query/resume/sync_status/sync/trace/export → **NO_SUCH_BRANCH** (all 6).
- AB (out of grant): query/resume/sync_status/sync → **SCOPE_DENIED**.
- `ZZ_dom_sync` != `SYNCED` (no false SYNCED).
- No `INTERNAL_ERROR` anywhere.
- AA healthy: query→SNAPSHOT, sync_status→SYNC_STATUS, sync→SYNCED. e2e admit AA→DEMO_ADMITTED.
  **PASS.**

### Boundaries
- `delivery.py`, `public_dto.py`, `server.py` hashes match the AB004 baseline freeze (not modified by AB005).
- `tech_debt.md`, `tests/` untouched by AB005 write_scope.
- `product_acceptance=false`, `is_approval=false`, no debt status changes (confirmed in artifact).
  **PASS.**

## Destructive probes (on isolated DB copies)
- **Missing idempotency table at start** (`C5D`): `dom_init` recreates the v2 table (`scope_digest` present),
  sets `user_version` — no crash. DB at `runtime/AU007/runs/c5d_no_idem`.
- **Corrupted result (invalid JSON)** (`C5C`): the immutable `UPDATE` guard blocks in-band row corruption
  (`update_blocked_by_guard=IMMUTABLE`); injecting invalid JSON only works after dropping the guard (out-of-band
  DBA), and then an admit replay returns `INTERNAL_ERROR` (fails closed, no detail leak) rather than a typed
  status. DB at `runtime/AU007/runs/c5c_corrupt`.
- **Concurrent two-process**: not independently reproduced — worker's serialized `BEGIN IMMEDIATE` model is
  not treated as proof; recorded in `not_checked`.

## Findings
- **[low]** Corrupt idempotency `result` (invalid JSON) → untyped `INTERNAL_ERROR` on admit replay once the
  immutable `UPDATE` guard is bypassed; fails closed (no data leak) but not a typed status. The guard itself
  blocks in-band corruption.
- **[info]** Principal separation is operation-string namespacing, not cryptographic identity — documented,
  matches worker N-F02-7.

## Verdict
- **Verdict**: `APPROVE` (separate slice verdicts: WS-F04 APPROVED, WS-F02 APPROVED).
- **Status**: `COMPLETE_WITH_LIMITS` (true-concurrency not reproduced; worker evidence files not line-by-line
  sha-cross-checked). All 9 negative-acceptance clauses except the true-race were reproduced and pass.
- **product_acceptance**: `false`. **is_approval**: `false`.

## Where the evidence lives
- `runtime/AU007/au007_probe.py`, `runtime/AU007/au007_probe2.py` (probe scripts)
- `runtime/AU007/results/au007.json`, `runtime/AU007/results/au007_probe2.json` (results)
- `runtime/AU007/runs/**` (per-scenario isolated DBs + raw MCP frames + sqlite readback in A_safe)