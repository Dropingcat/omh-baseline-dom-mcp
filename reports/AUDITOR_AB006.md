# AU008 CONT-01 — Auditor report (attacks A4–A10 + latent reclassification)

**Role:** AUDITOR   **Task:** AB006 slice   **Continuation:** AU008-CONT-01
**Audited version (frozen snapshot):** `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505` (16 files)
**Verdict:** REQUEST_CHANGES (2 latent defects + 1 underfill observation; **no active/exploitable security defect** on this slice)
**Status:** COMPLETE_WITH_LIMITS · product_acceptance=false · is_approval=false

---

## 0. Versioning / snapshot integrity (critical)

- The audit ran **entirely against the frozen copy** `runtime/AU008/snapshot_c26812b3/`, never against live `mockup/**`.
- Snapshot digest recomputed at import **inside** the probe and verified:
  `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505` (MATCH).
- **Live `mockup/**` drifted in parallel to `3cd21d96ff2f83f014f00c3fdf5b21c6ef94c26525385ef6a014365387d8aad0`** before the audit closed — the parallel role AB007 landed its pagination fix. The snapshot is unaffected; every result below is on the frozen slice.
- This confirms the freeze was necessary and correct.

---

## 1. Reclassification of prior finding A2 (semantic correction)

Per the correction: **`pending` = unfinished actions; `REJECTED` is terminal and must not appear in pending.** Because `review()` always writes `decision='approve'`, a REJECTED-in-pending path is not exercisable today — it is a **latent defect**, not a PASS.

- **AU008-L-01** (latent, medium)
  - Invariant: pending = unfinished only; REJECTED must not surface in pending.
  - Evidence: `runtime/AU008/results/a2_missed_unfinished.json` → `refused_visible.visible=true, state=REJECTED`.
  - Code: frozen snapshot `admission.py:_pending_page()` **lines 476–487** — only exclusion is `if r['admitted_by_claims'] or r['admitted_by_idem']: continue` (476–477); the `state = 'REJECTED' if (decision != 'approve')` branch (486) appends a refused candidate to pending. No REJECTED exclusion.
  - Manifest: **when a refusal-capable review exists, refused candidates surface in pending.** Forward-looking.

- **AU008-L-02** (latent, medium)
  - Invariant: `admit` must not admit a candidate whose review was a refusal.
  - Code: frozen snapshot `admission.py` **lines 218–224** — `admit` reads the review row (218), checks STALE_REVIEW/INDEPENDENCE/digest/policy/snapshot/head-revision, but **never verifies `r['decision']=='approve'`**. A rejected review would still be admitted. RS009-confirmed locations included.
  - Manifest: forward-looking; today `review()` only ever writes `approve`, so the gap is dormant.

---

## 2. Attacks A4–A10 — results

### A4 — content/claim/dependency leaks — **PASS**
- Pending items expose **metadata only**: fields = `age_seconds,branch,candidate_id,dependencies,expected_branch_revision,idempotency_key,intent_digest,operation,origin,payload_length,review_id,state`.
- No candidate body text in any pending frame; `pending_section_has_no_claim_id=true`; `deps_within_grant=true` (all dependency keys ⊆ grant across full/narrow/AB frames).
- `payload_length` = length of canonical package JSON: equal for equal-length different bodies, never the text itself (`text_not_in_frame`).
- The single token `appended note` appears **only** in the snapshot/trace section as an **admitted** append event value (committed, in-grant, legitimate) — never in a pending item. Observation AU008-O-02.
- Evidence: `runtime/AU008/results/ab/a4_leaks.json` (sha256 `63b09e4056901b7e`).

### A5 — cursor handling — **PASS with observation**
- Broken formats (`''`, no-colon `'broken'`, wrong type `42`) → **typed `REJECTED`**, no raw exceptions.
- `foreign_branch` cursor (`AB:…` under AA grant) → `NO_PENDING` / 0 items (no leak).
- Leaf-id past the last item / non-existent id → scoped rows only.
- **Observation AU008-O-01 (F1 reviewer items confirmed/refuted):** empty-component cursors `AA:` (empty id) and `:x` (empty branch) are **accepted** but **scope-safe** — return only in-grant rows (2 items), never foreign/runaway rows. F1 is **refuted as a security/scope issue**; accepted-keyset leniency noted as a robustness nit only.
- Evidence: `runtime/AU008/results/ab/a5_cursor.json` (sha256 `00b850dbcbef1afb`).

### A6 — limit bounds — **PASS (refusal) + underfill observation**
- `limit=0`, `501`, `-3`, `10**12`, `'10'`, `2.5`, `True` → all **typed `REJECTED`** (no raw exceptions). Cap `[1,500]` enforced.
- `limit=1` → 1 item/page_limit=1; `500` → 2 pages fine.
- **Observation/known edge:** `limit=2` returned **1** pending item when 2 existed (`probes.two: items=1, count=2`, `boundary_ok=false`). Cause: `_pending_page` applies SQL `LIMIT(limit+1)` over **all** branch rows, then filters admitted/deps in Python; page-leading admitted rows consume the LIMIT before the filter → **page underfill**.
- This is the known **W1 pagination underfill edge** (documented in the AB006 work) and is precisely what the parallel role AB007 is fixing in-flight. Recorded as `AU008-A-01` (low) for completeness on this slice; **not double-charged** on top of the in-flight change.
- Evidence: `runtime/AU008/results/ab/a6_limits.json` (sha256 `917c1852d94a9326`).

### A7 — migration — **PASS**
- DB claiming `user_version=2` **without** `created_at` → `MIGRATION_REQUIRED`; **no silent rebuild** (`created_at` absent after refusal, `user_version` stays 2); rerun refuses again (idempotent refusal).
- Legacy `user_version=0` → additive migration: `created_at` added, `idx_claims_candidate` + `idx_idempotency_candidate` created, `user_version=2`; rerun `INITIALIZED` idempotently (counts stable).
- **Immutable after migration:** `UPDATE idempotency` → `IMMUTABLE`, `DELETE idempotency` → `IMMUTABLE`.
- Evidence: `runtime/AU008/results/ab/a7_migration.json` (sha256 `e3e8d7aa1b196451`).

### A8 — regression (F-02 DIGEST_MISMATCH / NO_SUCH_BRANCH) — **PASS**
- Prior legitimate AB admit (key `legacy-ab`) recorded. Then `admit(AA_candidate, AA_review, 'legacy-ab', AB_digest)` → **`DIGEST_MISMATCH`**, **no cached AB receipt** served, all SQL counters unchanged (`f02_counts_stable=true`) — confirms the F-02 L1 digest-before-cache fix holds.
- Granted-but-absent branch `XX` → **`NO_SUCH_BRANCH`** (typed) on both `query` and `resume`; no internal error.
- Evidence: `runtime/AU008/results/ab/a8_regression.json` (sha256 `cadcace728909c1b`).

### A9 — read without side effects — **PASS**
- SQL row counts identical before/after 5 `resume` calls (including a rejected `limit=0` call) across all 12 tracked tables.
- Evidence: `runtime/AU008/results/ab/a9_readonly.json` (sha256 `6785c9d5dfb816b5`).

### A10 — 100k scale — **PASS**
- 100,000 candidates: `count=100000` exact, page `items=500`, `has_more=true`, ids sorted/unique, keyset next-page non-empty with stable `count=100000`, `idempotency_key=None`, page computed in **0.68 s**.
- Evidence: `runtime/AU008/results/ab/a10_scale.json` (sha256 `b519fc9cc483783e`).

---

## 3. Not checked
- **Two-client concurrent write race** on one DB — NOT_CHECKED (only serialized `BEGIN IMMEDIATE` observed, no true concurrency reproduced).
- Full pytest suite (out of scope).
- Live OMH / network / git (forbidden by card).
- Byte-level re-audit of the in-flight AB007 live changes (live mockup at `3cd21d96…`, not audited).

## 4. Boundary / isolation compliance
- Every attack used its own fixture subdir (`w4…w10`, `m7_*`) under `runtime/AU008/runtime/fixtures/`; all SQLite connections opened/closed in short scopes → **no WinError 32** (the prior AU008 run's failure mode). The earlier abandoned run's `WinError 32` was also diagnosed: `purge()` forked *returns* of `mkdir` and lacked gc before retry; corrected.
- Read-only against live product; destructive ops only on copies.
- Probe imports the frozen `snapshot_c26812b3` package, isolated from the parallel edit.

## 5. Files produced
- `runtime/AU008/snapshot_c26812b3/` — frozen copy (digest verified `c26812b3…`).
- `runtime/AU008/probe_abattacks.py` — A4–A10 probe (sha256 `0f1e307224ae73be`).
- `runtime/AU008/results/ab/*.json` — per-attack evidence (a4–a10).
- `artifacts/AUDITOR_AB006.json` — verdict artifact (sha256-bearing own_runs, findings, snapshot manifest).
- `reports/AUDITOR_AB006.md` — this report.