# TD-DOM-22: Unification of the claim-entry interface (analysis + sub-plan)

Status: analysis / sub-plan. Not implemented. Depends on TD-DOM-08 (live OMH binding) and TD-DOM-27 (independent review in claim-entry).

## 1. Current state

The claim-entry block is split across two profiles:

| Profile | Tools | Review path | Claim creation |
|---|---|---|---|
| **lite** (`--profile lite`) | `dom_describe`, `dom_start`, `dom_claim`, `dom_update`, `dom_find` (+ resume/query/trace/export/sync) | self-review (`review_level='self'`), single owner identity | `_write_claim` → `_commit` (submit→self-review→admit) inside `mockup/lite.py` |
| **strict** (default) | `dom_submit`, `dom_review`, `dom_admit`, `dom_append`, `dom_query`, `dom_trace`, `dom_export`, `dom_sync*`, `dom_init`, `dom_resume` | independent review (different root) | full package via `dom_submit` (`payload_json`), then `dom_review` + `dom_admit` |

Code locations:
- `mockup/lite.py`: `claim()`, `update()`, `find()`, `start()`, `describe()`, `_write_claim()`, `_commit()`, `_validated_claim_args()`, `build_item()`, `_package()`.
- `mockup/admission.py`: `submit()`, `review()`, `admit()`, `append()`, candidate/admission transaction.
- `mockup/server.py`: `LITE_SIGNATURE`, `LITE_TOOLS`, `dispatch()` routing, `STRICT_TOOL_NAMES`.
- `docs/CLAIM_ANATOMY_AND_LINK_MARKERS.md`: proposed anatomy (not implemented).

Input/output (lite):
- Input: `dom_claim(branch, type, text, ...)` where `...` = COMMON_FIELDS (requirement_refs, reason, origin_version) + type-specific FIELD_TYPES (validated server-side against TYPE_ARGS[type]).
- Output: `CLAIM_ADMITTED` / `ALREADY_RECORDED` with claim_id, record_id, version, branch, type, revision, review_level, origin_version, raw_sha256, next_steps.
- `dom_update(claim_id, text, reason)` → `CLAIM_UPDATED` (new_claim_id, supersedes, record_id, version, revision, review_level, raw_sha256, next_steps).
- `dom_find(query, branch, type, requirement_ref, limit)` → matches.
- `dom_describe()` → schema/examples per type.

## 2. Gap analysis (TD-DOM-22)

1. **Two entry paths, inconsistent contracts.** Lite offers convenient single-claim tools; strict requires assembling a full package (`external_work_ref`, `branch`, `expected_branch_revision`, `items`, `dependencies`, `origin_version`, `reason`, `idempotency_key`). A caller in strict mode cannot create one claim without knowing the package schema.
2. **No claim-entry tool in strict profile.** `STRICT_TOOL_NAMES` does not include `dom_claim`/`dom_update`/`dom_find`/`dom_describe`/`dom_start`. The MCP handshake test (`test_handshake_list_and_refusals`) asserts `set(evidence['tools']) == TOOL_NAMES` (strict set), so adding tools changes the contract and tests.
3. **Review independence differs.** Lite self-reviews (`review_level='self'`); strict requires an independent reviewer (different root). A unified entry must preserve this: convenient path in lite, independent path in strict.
4. **Per-type required fields are server-validated only.** JSON Schema (`input_schema`) lists all FIELD_TYPES for every type; required-ness per type is not expressed (TD-DOM-23).
5. **No OMH task binding at entry.** `requirement_refs` are opaque strings; claims are not bound to OMH task/work refs (TD-DOM-25, TD-DOM-08).
6. **No idempotency key at entry.** Dedup is content-hash only (TD-DOM-28).
7. **No version navigation/diff.** `_lineage` computes record_id/version but no API exposes the chain or a diff (TD-DOM-29).
8. **No multi-branch atomic entry.** Applicability is a separate event; a claim cannot be admitted to several branches atomically (TD-DOM-30).

## 3. Proposed unification

Goal: a single claim-entry API usable in both profiles, where the *review gate* is profile-dependent (self in lite, independent in strict), and the *package construction* is shared.

Design:
- Extract the claim-entry logic (build_item, _validated_claim_args, _write_claim, _commit, update, find) from `mockup/lite.py` into a shared module `mockup/claim_entry.py` (or extend `mockup/admission.py` with `Service.claim`/`Service.update`/`Service.find`/`Service.describe`/`Service.start`).
- In strict profile, `Service.claim` routes through the existing candidate→review→admit pipeline with an independent reviewer, not self-review. In lite profile, it keeps self-review.
- Add `dom_claim`, `dom_update`, `dom_find`, `dom_describe`, `dom_start` to strict `TOOLS` and `SIGNATURE`, backed by the shared implementation.
- Keep `dom_submit`/`dom_review`/`dom_admit` for advanced/batch use.

Profile-dependent review gate:
- lite: `review_level='self'` (single owner).
- strict: requires a reviewer principal distinct from the author root; if none, refuse `INDEPENDENCE_NOT_ENFORCED` (same as today).

## 4. Sub-plan (ordered steps)

1. **Extract shared module** `mockup/claim_entry.py`: move `build_item`, `_validated_claim_args`, `_write_claim`, `_commit`, `claim`, `update`, `find`, `_rebuild_for_update`, `_origin_version_of`, `_claim_info` helpers. Keep `mockup/lite.py` as a thin re-export for backward compatibility (tests import `mockup.lite`).
   - Risk: many internal callers; keep aliases.
   - Verification: existing tests still pass.

2. **Add Service-level claim entry** in `mockup/admission.py`: `Service.claim(branch, type, text, **fields)`, `Service.update(claim_id, text, reason)`, `Service.find(...)`, `Service.describe()`, `Service.start(...)`. These delegate to `claim_entry` but use `self` (Service) for review gating. Lite profile uses self-review; strict uses independent review (refuse if same root).
   - Verification: unit-level smoke.

3. **Wire strict profile tools** in `mockup/server.py`: add the five tools to `TOOLS` (strict) and `LITE_SIGNATURE`-equivalent `STRICT_EXTRA_SIGNATURE`; update `dispatch()` routing; update `tools_for()` (strict now includes them). Update `TOOL_NAMES`/`STRICT_TOOL_NAMES`.
   - Risk: MCP handshake test `set(evidence['tools']) == TOOL_NAMES` must be updated to the new strict set. This is a contract change → update test + SPEC.md tool list.
   - Verification: `test_handshake_list_and_refusals`, `test_two_role_flow_over_stdio`.

4. **Per-type required fields in schema** (TD-DOM-23): extend `input_schema` so that for `dom_claim`, fields in `TYPE_ARGS[type]` that are semantically required (source_ref for quote, rationale for decision, expression for formula, repository_ref+relative_path for code, artifact_ref for data, definition for concept, classification+evidence for factual text) are marked required. Since `additionalProperties: False` and required is per-tool (not per-type), this requires either a two-step schema (type first, then fields) or documenting in `dom_describe`. Recommend: keep flat schema but enrich `dom_describe` output with per-type required/optional lists; optionally add a `dom_claim_schema(type)` helper. (Lower priority; can be split.)
   - Verification: describe output.

5. **Idempotency key support** (TD-DOM-28): add optional `idempotency_key` to `dom_claim`/`dom_update`, threaded into `_package`/`_commit`. Depends on claim-entry refactor.
   - Verification: repeat call returns same claim_id.

6. **Version navigation / diff** (TD-DOM-29): add `dom_claim_versions(claim_id)` or include `version_chain` in `dom_find`/`dom_query` output; add diff in `dom_update` response.
   - Verification: test.

7. **Multi-branch atomic entry** (TD-DOM-30): allow `branches: [...]` in `dom_claim` to admit to multiple branches in one transaction. High risk; defer until OMH binding (TD-25).

8. **OMH task binding** (TD-DOM-25): bind claims to OMH task/work refs. Blocked on TD-DOM-08 (live OMH binding). Defer.

9. **Independent review in strict claim-entry** (TD-DOM-27): ensure `Service.claim` in strict profile refuses self-review. Already enforced by `review()` (INDEPENDENCE_NOT_ENFORCED). Verify via test.

10. **Tests + docs**: update MCP handshake test tool set; update SPEC.md tool list; update `docs/STATUS.md`.

## 4. Dependencies

- TD-DOM-08 (live OMH binding) blocks steps 4/8.
- TD-DOM-27 is addressed by step 9 (no new code beyond routing).
- TD-DOM-23, 24, 28, 29, 30 are independent and can be done in parallel after step 1-3.
- TD-DOM-22 (this plan) is the umbrella.

## 5. Risks

- Changing strict tool surface breaks `test_handshake_list_and_refusals` and `test_two_role_flow_over_stdio` expectations; must update tests in the same change.
- Extracting shared module risks import cycles (`lite` ↔ `admission` ↔ `claim_entry`); design `claim_entry` to depend on `admission.Service` interface only.
- Self-review in lite must remain (single owner); do not accidentally enforce independence in lite.
- No deletion of existing code (project rule); keep `lite.py` as re-export.

## 6. Acceptance criteria

- `dom_claim`/`dom_update`/`dom_find`/`dom_describe`/`dom_start` available in both profiles.
- Strict profile enforces independent review for claim creation (self-review refused).
- All existing tests pass (with updated handshake tool set).
- New tests cover strict claim-entry happy path and self-review refusal.
- MCP handshake test updated and green.
- No regression in E2E (26/26) and demo (exit 0).
- SPEC.md and STATUS.md updated with new tool list.

## 7. Suggested execution order

Step 1 (extract) → Step 2 (Service-level) → Step 3 (wire strict) + tests → Step 9 (independence) → Step 4/5/6 in parallel → Step 7/8 deferred → Step 10 (docs).
"