# AB003 / TD-DOM-19 — public schema change (written by Worker)

Aim: stop leaking hidden-branch metadata and diagnostics (chain head / global revisions / foreign event locator) through the allowed MCP response surface, while keeping the global integrity gate and all internal delivery proof. The internal SQL observation stamp is unchanged and still carries `chain_head` + ALL branch revisions; only the **public DTO** projected from the same verified read context is reduced.

Code digest after change: `08aa9a9b978831806bd0ef24fe26f7214ab21b31ca6d2bbe7d27a61bd29bfe6f`
Code digest before change: `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3`

## Removed from the public (client-visible) response schema

| Public surface | Removed | Why |
|---|---|---|
| `read_snapshot` | `chain_head` | exposed the AB-inclusive chain head to AA-only callers |
| `read_snapshot.revisions` | global/branch-scoped leakage (`{AA:N, AB:M}` with M>0 to AA-only) | hidden-branch revision promotion to unauthorized branches |
| any response body | global `events` / global `head_hash` | raw chain internals surfaced through permitted tools |
| `chain.broken_event_id` | foreign event UUID (e.g. `536e6117-…` pre-fix leak) | corrupted middle **AB**-event leaked its forbidden UUID inside an AA-only allowed response |

## Added to the public response schema

| Public surface | Added | Semantics |
|---|---|---|
| `read_snapshot.integrity_status` | `'str'` (`CHAIN_OK` / `CHAIN_BROKEN` / …) | uniform integrity bit — public surfaces no longer carry chain internals |
| gate failure body (Broken form) | `{status, readiness, ready_for_owner_review, blockers, simulated}` | closed `Broken` record: `status=CHAIN_BROKEN`, `readiness=NOT_READY`, `ready_for_owner_review=false`, `blockers=[EVENT_CHAIN_BROKEN]`, `simulated` — identical across both corruption variants; no foreign locator field |
| `read_snapshot` | `{read_at, revisions(scoped), integrity_status}` | public snapshot = timestamp + launch-grant-scoped revisions + integrity status only |
| `chain` (in trace/resume/etc.) | status-only `{'status': str}` | kept for the caller’s health signal; `events`/`head_hash` never published |

## Changed shape (status-only Chain)

`Chain` public record is reduced to `{'status': 'str'}`. The full internal chain (per-event `event_hash`/`previous_hash`, head, revision set incl. AB) is still verified inside the integrity gate and retained in the SQL observation/output for `_trace` internal logs; it is just no longer routed to the client.

## Public read_snapshot contract (final)

```json
{
  "read_at": "<iso-8601 utc>",
  "revisions": {"<granted-branch>": <int>, "...": "..."},
  "integrity_status": "<CHAIN_OK | CHAIN_BROKEN | ...>"
}
```

- `revisions` are scoped to the caller’s launch-time grant: AA-only → `{"AA": N}`; authorized AA+AB (union) → `{"AA":1, "AB":M}`; master/UNKNOWN → `{}` with readiness `UNKNOWN`.
- No `chain_head`, no global head/count/seq, no foreign `broken_event_id`, no diagnostic promotion of union/reviewer/owner branches.
- Text and `structuredContent` serialize the same single public DTO (semantically identical; only `read_at` may differ between renders).

## Delivery / reconcile surface

Public `Sync` / `SyncStatus` keep `{status, simulated, branch, read_snapshot, intents}`; internal observation and intents (OMH_EVIDENCE, YAML_EXPORT) retain full stamps and reach ack without duplicate writes — internal proof preserved.

## Regression note

One pre-existing test (`test_event_chain_is_verified_and_forgery_is_detected`) asserts `trace(...)['chain']['events'] == 1` and now KeyErrors because Chain is intentionally status-only. This failure is the intentional consequence of this schema change, documented and left for reviewer/auditor; it is not masked.