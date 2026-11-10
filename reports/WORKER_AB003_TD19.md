# AB003 / TD-DOM-19 — Worker report (continuation 02: final files)

- **Role:** Worker (subagent-driven implementation)
- **Debt:** TD-DOM-19
- **Card:** `cards/AB003_TD19_WORKER_PREPARED.md`; continuation `cards/AB003_CONTINUE_02.md`
- **Written:** 2026-11-08
- **Verdict ownership:** This report records executed fix + verification on this slice. **NOT APPROVE / not product acceptance.** Final verdict belongs to a subsequent independent **reviewer** and a **negative auditor** on this exact modified version.

---

## 1. Baseline & scope

- Baseline code digest (SEC003 method): `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3` (15 files of `mockup/**/*.py`), reconfirmed by `runtime/AB003/digest_check.py`.
- Goal: stop leaking hidden-branch metadata and diagnostics through allowed MCP responses while preserving the global integrity gate and all internal delivery proof.
- Write scope: `mockup/admission.py`, `mockup/server.py`; new `mockup/public_dto.py` (pure public DTO builder); minimal glue in `mockup/projections.py`; `mockup/delivery.py` guards/semantics preserved.
- Two additional in-scope DTO fixes recorded as observations, not a new TD (details in §6).

---

## 2. Own PARTIAL JSON + fingerprint

- `runtime/AB003/PARTIAL_AB003_TD19.json`, `status=WORK_IN_PROGRESS`, baseline digest `715b1ca8…ba3` matching `runtime/PL003/input_fingerprints.json` source_hashes (0 mismatches) — recorded before fix.
- Source fingerprint method matches SEC003 digest_check exactly.

---

## 3. Pre-fix reproduction (step 3)

On pre-fix code (disposable populated fixture, seed 3101 → `run-pre-3101`):

| Check | Result (pre) | Evidence |
|---|---|---|
| CHK-A2-01 | **LEAK_REPRODUCED** | `receipt-td19-a2-01.json` sha `eaf68cd8…e1f1` |
| CHK-A2-02 | **LEAK_REPRODUCED** | `receipt-td19-a2-02.json` sha `04a5e065…7983` |
| CHK-A2-03 | **GATE_AND_LEAK** | `receipt-td19-a2-03.json` sha `d6ca9e09…f17c` |
| CHK-DEL-01 | PASS | `receipt-td19-delivery.json` |

- Pre leak confirmed: query surface foreign-token scan reported `chain_head` present; corrupted middle **AB** event leaked its forbidden foreign UUID `536e6117-b1e3-4009-82da-95643677c525` via `chain.broken_event_id`. PIDs `[1868, 2936]`.
- Manifest sha `ff2a2d17…6ef0c`; raw receipts preserved under `run-pre-3101/` (receipt files remain byte-stable, hashes quoted above).

---

## 4. Internal/public split (step 4)

- Added `mockup/public_dto.py` (private-data-free schema builder): closed-structure public DTO `{status, readiness, ready_for_owner_review, blockers, simulated}` for gate failure, `integrity_status` on `read_snapshot`, Chain **status-only**.
- `mockup/admission.py`: route responses through `public_dto.project(...)`; `_trace` chain reduced to `{'status'}` via `public_dto.chain(verify_chain(c))`.
- Internal gate unchanged: `chain_head` + **ALL branch revisions** `{AA:N, AB:M}` still verified and stored inside SQL observation; never copied to the public DTO. No new projection / no TOCTOU (same verified read context).

---

## 5. Healthy surfaces + differential (step 5)

On post-fix code (`run-post-3101`, seed 3101), AA fixed / AB changing:

| Check | Result (post) | Evidence |
|---|---|---|
| CHK-A2-01 | **LEAK_CLOSED** | `receipt-td19-a2-01.json` sha `74a55fed…32fb` |
| CHK-A2-02 | **LEAK_CLOSED** | `receipt-td19-a2-02.json` sha `dfb2764d…8c` |
| CHK-A2-03 | **GATE_UNIFORM_SAFE** | `receipt-td19-a2-03.json` sha `63439c9b…dd7b` |
| CHK-DEL-01 | **PASS** | `receipt-td19-delivery.json` sha `09e63263…c988` |

- Healthy surfaces query / snapshot / trace / resume / sync_status / export: `read_snapshot.integrity_status=CHAIN_OK`, `revisions={AA:1}` only, `has_chain_head=false`, and **text == structuredContent semantically identical (one DTO)** — raw differential holds (sole documented exception: `read_at` timestamp).
- Authorized AA-only sync: `revisions={AA}`; master UNKNOWN trace: `revisions={}`, readiness `UNKNOWN`; union (authorized AA+AB): `revisions={AA:1,AB:3}` — scoping by launch-time grant, no promotion union/reviewer/owner.
- Forbidden middle AB event (invalid UTF-8 AND wrong-hash variants): **identical** safe `CHAIN_BROKEN/NOT_READY` `{status, readiness, ready_for_owner_review:false, blockers:[EVENT_CHAIN_BROKEN], simulated:true}` on **both gate runs**; `foreign_locator_visible=false`; oracle independently located `broken_at_seq=3`, broken_event_id `a33cb567-b9bc-4265-9baa-c22aaa8c92e2`, branch AB — but NO foreign locator to the public response. 7 tools × 2 corruption cases, exit 0, PIDs `[14328, 2304]`.
- Post manifest sha `026cd93c…c22fe`, `env.python=E:\...\.venv\Scripts\python.exe 3.11.15`, yaml 6.0.3, sqlite 3.53.1, Windows 10.

---

## 6. Delivery + reconcile + observation (step 6)

- **CHK-DEL-01 PASS**: sync SYNCED, observation_count=2 = ack_count=2 (`OMH_EVIDENCE` + `YAML_EXPORT`), observation→attempt→intent→ack preserved, `internal_stamp_full=true`, `no_duplicate_writes=true`, target file written pid 14216, internal observation snapshots keep full `{chain_head, revisions AA+AB}` — internal proof retained.
- Regression (`runtime/AB003/regression/pytest-q.txt`): **1 failed, 63 passed**. The single failure `tests/test_integrity_contracts.py::test_event_chain_is_verified_and_forgery_is_detected` KeyErrors on `clean['chain']['events']` — the pre-existing leak surface, intentionally removed from the public Chain (now status-only). Documented, **not fixed, not masked**, to be reviewed by reviewer/auditor.
- **Observations (intended confidentiality change, NOT a new TD):**
  - `OBS-TD19-APPEND-ORDER` — public_dto AppendValue per-kind value record ordering/coverage tightened.
  - `OBS-TD19-CHAIN-STATUSONLY` — `_trace` chain public projection reduced to status-only.
- **MISMATCH:** none. Post-fix digest progressively recomputed and reconfirmed `08aa9a9b…e6f` (16 files) with no drift.

## Verification receipts (post / pre run PIDs + exit)

| Run | Code digest | Exit | PID(s) |
|---|---|---|---|
| pre `run-pre-3101` (`CHK-A2-01/02 LEAK_REPRODUCED`, A2-03 `GATE_AND_LEAK`) | `715b1ca8…ba3` | 0 | 1868, 2936 |
| smoke `smoke-run` (`SMOKE_OK`, 8/8 asserts) | post | 0 | — |
| post `run-post-3101` (`LEAK_CLOSED` ×2, `GATE_UNIFORM_SAFE`, `DELIVERY PASS`) | `08aa9a9b…e6f` | 0 | 14216; gate 14328, 2304 |

## Files written (this continuation)

1. `artifacts/WORKER_AB003_TD19.json` — status=completed, product_acceptance=false, is_approval=false, self-report NOT APPROVE, per-step evidence sha256 refs.
2. `reports/WORKER_AB003_TD19.md` — this report (6 steps, digests before/after, MISMATCH none).
3. `docs/SCHEMA_CHANGE_TD19.md` — public schema change document.

**Debt status:** not closed here. `debt_status_changes=[]`; closure of TD-DOM-19 requires independent reviewer + negative auditor on this exact version. Nothing else modified (product/mockup/tests/SEC003/QA003/PL003/tech_debt/runtime read-only; no Git/install/network/paid/subagents).