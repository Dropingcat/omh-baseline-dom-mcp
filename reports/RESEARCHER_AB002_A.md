# RS002-A — минимальные контракты исправления и хендофф PL003

**COMPLETE_MATERIAL; completion_state=completed; product_acceptance=false.** AU002-A REQUEST_CHANGES сохранён. Это собственный результат ресерчера, не код, не приёмка и не запуск PL003.

## Итог и приоритет

P0 TD19: полный глобальный proof остаётся внутренним; наружу новый типизированный actor-scoped DTO на всех семи gate-поверхностях, включая nested chain и оба MCP канала. Не ждать будущего удачного security-теста, чтобы устранить известную утечку. P1 TD20: отдельный OUT_OF_SCOPE A robustness-срез. P2 TD21: реальные frozen refs в сдаче сейчас, runner enforcement/two-run check позже. Все долги остаются open.

## Реально установлено и пределы

Исходные JSON/MD аналитика и аудитора, REQUIREMENTS, текущие admission/ports/server/delivery/projections/storage, runner и следующие карты прочитаны. Сохранён первый честный PARTIAL. Собственная команда `E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/RS002_A/inspect_inputs.py` завершилась exit0. Это перепарсинг наследованных файлов, не повтор E2E и не текущий SQL readback.

Перепарсинг: у AA claims те же байты; шесть healthy ответов меняют AB revision и global head, trace/resume count 1→2. В middle evidence 14 ответов, семь tools, два PID раскрывают UUID/seq инъекции; saved physical before/after byte-exact равны. TASK:list: физические таблицы сохраняют два attempt/0 observation/0 ack, после owned correction четыре attempt/2 observation/2 ack и один OMH write. Эти факты принадлежат AU002-A, а не новому продуктовому запуску ресерчера.

Global proof не безопасен лишь потому, что hash. Не обещается абсолютная неразличимость healthy/broken: глобальная блокировка обязана оставаться видимой. Привилегированный endpoint отсутствует; reviewer/owner не admin-capability. Исторический ack при read_at не означает вечную доступность цели.

## Public / internal / privileged — закрытая таблица полей

| Поле | Public healthy | Public broken | Internal / privileged |
|---|---|---|---|
| global proof: chain_head/head_hash, events, seq, broken_event_id, full revisions, reason | "DENY" | DENY | retain full exact verification result and stamp, never destructively redact; only separately authorized local fixture oracle; no public endpoint |
| read_snapshot | {"read_at": "server observation time; only documented healthy differential exception", "revisions": "map of response branches intersect launch grants -> head in same verified SQLite snapshot; not all global heads", "integrity_status": "CHAIN_OK only after full global verification; not proof of external checkpoint"} | ABSENT: cannot label corrupted snapshot verified | read_at + global chain_head + ALL revisions + port_reported for delivery binding; full stamp only inside protected oracle |
| trace.chain; resume.trace.chain | {"status": "CHAIN_OK"} | ABSENT; use uniform refusal | full chain retained; exact internal chain if independently authorized |
| branch/claim/event/review/intent/observed refs and branch-local revision | "only schema-defined refs independently authorized by selected branch/object scope; not global sequence" | ABSENT | full internal relations; locator control separately from actor |
| YAML handle/sha256, claim raw_sha256, candidate intent_digest | "only hash of already permitted scoped content; no input containing global chain/hidden membership" | ABSENT | retain exact byte proof; full files as protected evidence |
| new correlation token | "ABSENT" | ABSENT | not needed in minimum fix; future random per-request non-derived token needs protected routing; never UUID/hash surrogate |
| origins on broken response; error.reason; raw exception/path/payload | "no raw exception; normal origins only under typed branch scope" | ABSENT | exact failure reason retained only in protected evidence; exact reason/locator through local operator oracle only |
| unknown/untyped keys at any structural depth | "DENY or fail closed PUBLIC_PROJECTION_INVALID without values" | DENY | may remain in internal object; do not equate privileged with unrestricted logs |

Минимальная safe refusal (предложение, ещё не в продукте):
```json
{
  "status": "CHAIN_BROKEN",
  "readiness": "NOT_READY",
  "ready_for_owner_review": false,
  "blockers": [
    "EVENT_CHAIN_BROKEN"
  ],
  "simulated": true
}
```
Никаких chain/read_snapshot/origins/reason subtype/token. Внутренний failure сохраняет точный locator для отдельного доверенного fixture oracle. Не писать его в общие логи/stderr/экспорт. Новый live diagnostic канал и его полномочия — отдельное needs-user, не условие немедленного удаления запрещённой выдачи.

### Allowlist каждого MCP инструмента

| Tool | Healthy | CHAIN_BROKEN |
|---|---|---|
| dom_query | Snapshot + read_snapshot:ReadSnapshot | Broken exactly; no snapshot/chain/origins/exports |
| dom_snapshot | identical alias of dom_query | Broken exactly; no snapshot/chain/origins/exports |
| dom_trace | Trace + read_snapshot:ReadSnapshot; missing master grants -> UNKNOWN minimal Trace, revisions={} | Broken exactly; no snapshot/chain/origins/exports |
| dom_resume | Resume(snapshot:Snapshot, trace:Trace, sync:SyncStatus, read_snapshot:ReadSnapshot) | Broken exactly; no snapshot/chain/origins/exports |
| dom_sync_status | SyncStatus + read_snapshot:ReadSnapshot | Broken exactly; no snapshot/chain/origins/exports |
| dom_export | Export + read_snapshot:ReadSnapshot; bytes are scoped Snapshot only | Broken exactly; no snapshot/chain/origins/exports |
| dom_sync | Sync; authorized admit capability, global gates before attempt/effect/observation/return | Broken exactly; no snapshot/chain/origins/exports |
| dom_init | Initialized | Not emitted on current paths (no integrity_gate here); if introduced, Broken only, never raw proof |
| dom_submit | Candidate | Rejected | Not emitted on current paths (no integrity_gate here); if introduced, Broken only, never raw proof |
| dom_append | Candidate | Rejected; same submit path | Not emitted on current paths (no integrity_gate here); if introduced, Broken only, never raw proof |
| dom_review | Reviewed | Not emitted on current paths (no integrity_gate here); if introduced, Broken only, never raw proof |
| dom_admit | Admitted | Not emitted on current paths (no integrity_gate here); if introduced, Broken only, never raw proof |

Все structural schemas закрыты рекурсивно. JSON содержит точные поля `public_schemas`, metadata по типу и append value по kind. Разрешённые user-data slots не несут server proof и не меняются ради redaction. Неизвестная структура/неавторизованный структурный ref — безопасный отказ, не raw dump и не тихая подмена immutable claim. Существующую политику applicability/sharing не переопределять; недостающий контракт делит будущий scope, не разрешает скрытый доступ. Отсутствующие master grants дают UNKNOWN и пустой revisions, а не раскрытие всей карты голов.

## Ответы по точным вопросам

### Q-A2-01

Как разделить полный внутренний integrity stamp и actor-scoped публичную проекцию healthy-ответа так, чтобы ни read_snapshot.revisions/chain_head, ни trace.chain и resume.trace.chain не раскрывали скрытую ветку, сохранив verified read snapshot и внутреннюю привязку delivery evidence?

**Механизм / минимальный working contract:** Typed FullIntegrityProof never serialized; PublicDTO built from explicit recursive allowlist under immutable launch grants, same SQLite read context; serializer receives DTO only. Do not redact the internal stamp in place.

**Развилка:** Single recursive denylist/redactor is smaller but rejected: unknown future fields and nested chain aliases escape; scoped cryptographic token optional later, not minimal fix.

**Почему:** Scope cannot be restored by hiding only AB revisions: full head/count and nested chain remain foreign-dependent. A fresh DTO has no reference to the full proof, while internal SQL observation retains global chain/read snapshot and ack binding. Same c prevents verifier/projection TOCTOU; this does not promise a new branch/master-readiness policy.

**Последовательность:**
- Authorize request branch/work and capability first. Compute full global proof and full revision vector on same c.
- On healthy gate build scoped body and public stamp (response branches intersect grants); trace.chain only status. Nested resume calls same DTO builders.
- Sync keeps global gates and complete internal stamp at observation insert, exact binding/confirmed untouched. Export raw scoped snapshot with no global proof included.
- Build one public object and serialize it identically to MCP text and structuredContent; no proof dict merge at any depth. Unknown structural key/unauthorized structural ref -> fixed safe projection failure, not raw value dump.

**Поля / состояния:**
```json
{
  "field_table_ref": "field_tables",
  "tool_table_ref": "tool_output_allowlists",
  "recursive_schemas_ref": "public_schemas",
  "dynamic_rules": "branch maps restricted to explicitly requested/authorized response scope, not all grants by default. For limited master UNKNOWN, revisions={} and no chain count. Snapshot revision can be historical; public revisions is verified head, distinguished from body revision. Omit global hashes even for union actors in this uniform public contract; a union actor is not diagnostic-admin.",
  "scoped_token": "not added: branch revisions plus read_at suffice for public metadata; no SHA of global proof, no stable hidden-change surrogate. Export sha hashes only permitted bytes.",
  "cross_scope_content": "Existing authorized applicability is not redefined here. All structural origin/dependency/applicability refs require established object-sharing authorization; ambiguous cross-scope record must safely refuse projection rather than silently rewrite immutable body or grant foreign access. New sharing policy requires user decision; full cross-branch sharing audit remains PL003 GAP."
}
```

**Action → expected → physical facts (все proposed/not_tested):**
- Действие: AA-only actor, AA фиксирована; B actor меняет hidden AB, B positive control; шесть healthy outputs и новый PID, плюс permitted sync actor с теми же AA grants.
  Ожидание: Permitted содержимое сохраняется, запрещённые revisions/count/head/IDs не появляются ни в text, ни structured/nested outputs; direct AB по-прежнему denied. Sync-вариант новый, не заявлен как уже исполненный healthy audit.
  Физический oracle: Raw MCP field-level differential с исключением документированных read_at, positive AB control, точные AA bytes и readback/SQL observation→attempt→intent; gate остаётся глобальным.
- Действие: Inspect export YAML bytes and allowed receipts plus public logs while AB changes and AA remains fixed
  Ожидание: permitted bytes stable; no full proof serialization, no mutated INTERNAL stamp
  Физический oracle: raw text==structured DTO semantic equality, exact YAML hash/readback; SQL snapshot retains global chain_head/full revisions; observation→attempt→intent→ack joins and raw hash/size

**Наследованные физические факты:** Inherited six surfaces: same AA claims, revisions.AB 0→1 and chain_head change; nested trace/resume events 1→2. Own reparse saved in evidence_extract.json. No new healthy scoped sync.

**Риски:**
- Compatibility: removal of diagnostic fields is an intentional confidentiality fix, document schema change, not a reason to preserve leak.
- Only read_at excluded in healthy fixed-state differential; do not excuse head/count/UUID/hash with a broad volatile-field mask.
- Timing/global health and external applicability/stale behavior outside no-interference claim; do not declare all channels safe.

**Needs-user:** {"blocker": false, "stop_leak_requires_new_permission": false, "conditional": ["A new public scoped proof token or changed sharing/readiness policy would need separate explicit contract; minimum fix needs neither."]}

**Первичные источники:** mockup/admission.py:90-101,220-277,323-370; mockup/delivery.py:19-36,44-75; mockup/storage.py:100-113; mockup/projections.py:25-77
Evidence ID раскрыты в каталоге ниже и в JSON, не выданы за URL.

### Q-A2-02

Какой минимальный безопасный CHAIN_BROKEN ответ допустим restricted actor при повреждении forbidden AB, и как отдельно сохранить точный привилегированный locator без UUID/seq/count/revisions/глобальных хешей в restricted ответе и без ослабления глобального fail-closed?

**Механизм / минимальный working contract:** Uniform public Broken DTO exactly as listed, identical for bad encoding/hash/forbidden branch; full IntegrityFailure details stay internal. Keep precise verify_chain output for protected local fixture/operator oracle, not a model-facing endpoint.

**Развилка:** New privileged diagnostic transport gated by a dedicated host-issued capability with work/dataset scope, separate storage/retention and denied-by-default routing; not implemented and requires user authorization.

**Почему:** Availability must reflect global fail-closed and therefore healthy/broken responses need not be indistinguishable. Constant blocker conveys required global health without foreign localization. Diagnostic fields cannot be made safe by a role name or a stable hashed locator.

**Последовательность:**
- Global verification fails before projecting claims/exporting/sending.
- Carry full proof internally, return only Broken; never CHAIN_OK/READY or a successful snapshot.
- No public origins, revisions, seq, event ID, total, reason subtype, global hash or correlation key.
- In independent fixture oracle, call/read exact verifier result on disposable DB and match injected event; store only in operator-only evidence location, not stderr shared with restricted caller.

**Поля / состояния:**
```json
{
  "public_broken_exact": {
    "status": "CHAIN_BROKEN",
    "readiness": "NOT_READY",
    "ready_for_owner_review": false,
    "blockers": [
      "EVENT_CHAIN_BROKEN"
    ],
    "simulated": true
  },
  "internal": "full verify_chain including exact reason, event UUID, seq, event total and full stamp",
  "privileged_boundary": "GAP: fixture context only submit/review/admit/owner; no diagnostic capability. Existing runtime has no OS isolation guarantee. Research evidence and oracle are trusted local operator/test assets, not claimed production protected storage. No new admin tool required for P0.",
  "logs": "server operational log only fixed tool/status/simulated/principal from trusted context. Never result/exception/repr(proof). If logger is not private, no locator there. Public exports and tool attachments use same DTO policy.",
  "unexpected_errors": "Known domain failures map fixed enums; unexpected exceptions get generic INTERNAL_ERROR/no raw trace to caller, precise exception only operator-isolated diagnostic. This sanitization never converts effects to no-effect or failure to success.",
  "mcp_isError": "Domain CHAIN_BROKEN can preserve current isError=false domain-response convention (status authoritative); transport errors isError=true. Both content channels contain the same safe object, no SDK raw exception leak."
}
```

**Action → expected → physical facts (все proposed/not_tested):**
- Действие: Middle forbidden AB invalid-UTF8 и отдельно wrong hash на disposable populated копии; AA-only actor, два свежих процесса, семь tools; затем authorized privileged locator control по выбранному контракту.
  Ожидание: Structured refusal, NOT_READY, нет эффекта/exports и forbidden locator; глобальная порча всё ещё блокирует AA. Привилегированный оракул точно находит испорченный event без выдачи его restricted actor.
  Физический oracle: Raw text/structured error scan, target/export/DB before==after, admin oracle к fixture locator, без shared diagnostic handle утечки.
- Действие: Try role=reviewer/owner on AA grants, tool-argument role spoof, and denied access to any proposed privileged channel
  Ожидание: no implicit diagnostic promotion; dedicated capability absent means no public full locator
  Физический oracle: raw MCP refusals and separate exact fixture oracle bytes; no shared handle ID that permits lookup

**Наследованные физические факты:** Inherited 14 responses / 7 tools / 2 PIDs: CHAIN_BROKEN + exact forbidden AB UUID/seq; saved injected-before == after-refusals bytes. New wrong-hash/privileged-channel E2E not executed.

**Риски:**
- No protected live diagnostic channel exists; do not label local runtime filesystem protected from OS/file owner.
- Minimal status permits global availability side signal, not absolute indistinguishability.
- Wrong-hash middle-event E2E still required separately from inherited invalid UTF8.

**Needs-user:** {"blocker": false, "stop_leak_requires_new_permission": false, "conditional": ["Only if adding live diagnostic capability/trust boundary, retention or repair/rewind; none chosen by minimum fix."]}

**Первичные источники:** mockup/admission.py:30-101; mockup/server.py:183-215; mockup/ports.py:12-24
Evidence ID раскрыты в каталоге ниже и в JSON, не выданы за URL.

### Q-A2-03

Какой единый read/attach shape-контракт различает отсутствующий файл/target key и присутствующий TASK со значением list/null/scalar, а также неверный tx record, не нормализуя malformed данные в пустую карту и не меняя чужие keys?

**Механизм / минимальный working contract:** One non-lossy TargetReadResult tagged union; a shared pure shape validator invoked on pre-read and AGAIN under attach lock after reload. Use membership, exact types and enum domain errors; validate owned target and requested tx, preserve opaque unrelated keys.

**Развилка:** Validate all targets on every call: stronger global cleanliness but unrelated malformed data blocks own work and widens scope; not recommended for this owned-key robustness slice.

**Почему:** The lossy {} destroys the fact required to decide whether creation is safe. Shared validation prevents read/attach disagreement and locked revalidation prevents relying on stale pre-read. Independent unknown keys need preservation, not recursive rewriting.

**Последовательность:**
- Decode exact root JSON; distinguish ENOENT from present invalid/empty/unreadable.
- Present root must be dict; target absent tagged; present target must be dict (null not absent).
- Requested tx membership separate from its value. Record exact schema; malformed != valid conflicting != matched.
- Under _locked reload/revalidate; race from absent/valid to invalid/conflicting returns no write. Atomic append only if allowed absence; never coerce or reset.
- After any permitted send actual readback uses same validator; only exact record/bytes may become matched evidence.

**Поля / состояния:**
```json
{
  "state_table_ref": "target_shape_states",
  "domain_error_fields": [
    "code: TARGET_INVALID|TARGET_CONFLICT|TARGET_BUSY|TARGET_UNAVAILABLE",
    "stage: pre_read|locked_attach|post_read",
    "reason: ROOT_SHAPE|DECODE_INVALID|TARGET_SHAPE|TX_RECORD_SHAPE|BINDING_MISMATCH",
    "effect: none_proven_for_attempt|possible"
  ],
  "public_error": "Expose safe code/stage/effect only inside authorized intent outcome; never raw payload, OS path, foreign key name or invalid type repr. Internal diagnostic may retain enum reason.",
  "tx_schema": "record exactly {digest,payload}; payload exactly {tx_id,branch,revision,intent_digest,target_ref}. digest/intents hex64. Equal exact expected is MATCHED; shape-valid different record CONFLICT. Unknown fields in own record require explicit schema-version handling, not silent discard. Other tx/foreign-target values kept opaque; malformed unrelated values not interpreted.",
  "mutation_limits": "Error path target file byte-exact unchanged (lockfile creation is a documented synchronization artifact, not target reset). Success may reserialize outer object but semantic unrelated-key equality and prior tx values required. Caller cannot use correction to delete accepted evidence; fixture owner corrects only disposable own malformed key explicitly."
}
```

**Action → expected → physical facts (все proposed/not_tested):**
- Действие: Fresh и populated target, собственный key отсутствует/{}/[]/null/scalar; присутствуют unrelated keys и existing tx. Для каждого два новых процесса и controlled correction только own key.
  Ожидание: Malformed выдаёт domain error без Attribute/TypeError и без мутации target/ack; отсутствующий key штатно создаётся, валидные и чужие данные не теряются. После явного исправления восстановление.
  Физический oracle: Original bytes при отказе, foreign-key equality, raw MCP, SQL matched/ack false до exact readback, recovery write log без дубликата.
- Действие: Race external replacement between pre-read and locked attach; inject malformed requested tx and unrelated malformed target
  Ожидание: locked revalidation refuses own invalid/conflicting data; unrelated bytes/values not reset, no fake absence
  Физический oracle: target hash unchanged on refusal, foreign-key semantic equality, raw MCP diagnosis, no ack; recovery preserves old tx and one new write

**Наследованные физические факты:** Inherited TASK:list two retries: unchanged target and no observation/ack; correction own key restores one target record/write. Other shapes proposed.

**Риски:**
- OS-lock only coordinates cooperating simulation writers, not malicious file owner.
- Null/scalar/root/record permutations are proposals not observations in current run.
- Strict tx record schema migration must fail domain-safe on unknown version, never reset foreign data.

**Needs-user:** {"blocker": false, "scope": "TD20 requires separately authorized robustness slice; not silently added to A or TD19 worker.", "conditional": ["Changing external format/unknown-version migration or allowing automatic repair needs explicit decision; no such repair proposed."]}

**Первичные источники:** mockup/ports.py:31-82; mockup/admission.py:335-352
Evidence ID раскрыты в каталоге ниже и в JSON, не выданы за URL.

### Q-A2-04

Как согласовать доменное завершение попытки при target shape failure и независимые intents одного sync: что фиксировать как failed/unobserved/ambiguous, когда продолжать YAML, какой aggregate результат вернуть и как повтором не подделать readback/ack?

**Механизм / минимальный working contract:** Add append-only attempt_outcomes (or equivalent typed failure facts) for safe diagnosis/phase/effect certainty, not fake delivery_observations. Keep attempts/real observations/ack triggers unchanged, add immutable/binding guards to new facts. For now preserve fail-stop but make it a truthful domain sync result; propose optional per-intent continuation explicitly.

**Развилка:** Continue independent YAML after OMH pre-effect invalid target: availability improvement only if independence is proven and global gate rechecked. Needs product approval before becoming guarantee; no such guarantee retroactively belongs to A2.

**Почему:** Attempt persistence establishes predecessor, not evidence of external bytes. Outcome certainty is phase-sensitive; catching AttributeError cannot prove rollback after send. Separating failure facts avoids the semantic lie that empty raw is readback and preserves current strong ack binding.

**Последовательность:**
- Durable attempt precedes action/read. Known validation failure before any new effect records TARGET_INVALID and none_proven_for_attempt; prior ambiguous attempts remain ambiguous.
- After send/replace may have happened, any failure is possible-effect/ambiguous. Missing terminal fact after process death is ambiguous, not no-effect.
- No successful observation for empty raw error; failure outcome may exist without observation, matched never true.
- Return structured SYNC_PENDING and authorized per-intent safe diagnosis; subsequent not-started intents remain pending (optionally skipped_due_to_failure).
- New retry starts from exact real pre-read; confirmed old acknowledgements skipped, existing exact target does not write again.
- Integrity/storage inability to prove safety aborts fanout regardless of continuation choice.

**Поля / состояния:**
```json
{
  "state_table_ref": "delivery_transitions",
  "proposed_attempt_outcome": [
    "id",
    "attempt",
    "intent",
    "tx",
    "digest",
    "target",
    "actor",
    "root",
    "server_time",
    "stage",
    "domain_code",
    "effect_certainty"
  ],
  "projection": "Derived safe IntentStatus extension diagnosis:{code,stage,effect} optional; requested branch only. New status reducer pending/failed-pre-effect vs ambiguous is explicit TD20 delta. No global totals or raw diagnosis.",
  "aggregate": "SYNCED iff every required scoped intent has confirmed ack. Any failure/pending/ambiguous -> SYNC_PENDING and ready_for_owner_review=false for sync delivery; trace still applies other existing blockers. Partial YAML ack does not make overall success. CHAIN_BROKEN supersedes aggregate; storage failure remains typed storage error, not fabricated per-intent completion.",
  "continuation_choice": "Conservative minimum: stop after typed target error, YAML pending, no false successful observation. Preferred optional robustness: continue YAML iff no declared dependency on failed OMH intent, same authorized branch/revision, healthy global proof before effect and persistence. Per-intent outcomes accurately show partial completion. Choice must be recorded in next TD20 card.",
  "migration": "Additive migration only; preserve prior attempts/observations/acks and exact binding. No terminal outcome generated for historical missing completion merely from elapsed time; no rewrite of old ambiguous history."
}
```

**Action → expected → physical facts (все proposed/not_tested):**
- Действие: Malformed OMH + pending YAML; два retry процесса; затем owned correction/reconcile; отдельно обрыв после send с uncertain outcome.
  Ожидание: Truthful structured SYNC_PENDING/target diagnosis или согласованный эквивалент, NOT_READY и no false ack. YAML поведение соответствует выбранному контракту; uncertain outcome не маркируется доказанным no-effect.
  Физический oracle: Attempt/observation/ack SQL lineage и server frames, target/YAML before/after, one-write recovery. Отсутствие observation не считать самостоятельным A2 fail.
- Действие: Fail write-log append after actual atomic replace, and kill process after send before readback; retry on fresh process
  Ожидание: possible effect ambiguous, never proven no-effect; fresh exact pre-read reconciles without duplicate write
  Физический oracle: actual target present while no premature ack; SQL attempt/outcome/observation/ack lineage; target/write-log discrepancy retained, not papered over

**Наследованные физические факты:** Saved malformed physical tables: 2 attempts/0 observation/0 ack; final 4 attempts/2 observations/2 acks, one OMH write. This is inherited E2E not current SQL or new E2E.

**Риски:**
- Current schema has no outcomes table and status makes any attempt ambiguous; new projection requires implementation/migration tests.
- One local write under cooperating lock is not universal exactly-once.
- Continuing YAML can conflict with future export/OMH dependency policy; fail-stop safe default retained until decision.

**Needs-user:** {"blocker": false, "for_minimum_fix": false, "proposed_product_choice": {"id": "RS002-DEC-CONTINUE", "state": "NEEDS_USER_BEFORE_NEW_GUARANTEE", "question": "Сделать независимый YAML per-intent continuation обязательным при pre-effect malformed OMH, либо сохранить fail-stop?", "recommended": "Continue only demonstrably independent intents; until authorized, domain-safe fail-stop."}}

**Первичные источники:** mockup/admission.py:307-362; mockup/delivery.py:8-36,44-75
Evidence ID раскрыты в каталоге ниже и в JSON, не выданы за URL.

### Q-A2-05

Какой минимальный immutable evidence reference должен фиксировать run-specific manifest, его hash и source/input lineage, чтобы повтор runner не переназначал evidence прежнего отчёта через shared e2e_manifest.json?

**Механизм / минимальный working contract:** Report stores run identity + final manifest byte hash + exact source/input/env linkage + case and receipt locators. Freeze once, write unique run path without overwrite; progress/latest is only navigation.

**Развилка:** Content-addressed immutable bundles indexed by hash improve deduplication but add tooling; not necessary to stop mutable-pointer reassignment.

**Почему:** Path plus mutable pointer does not identify historical bytes. Hash+frozen lineage makes reassignment/mismatch detectable without requiring Git. Hash alone is consistency, not trusted timestamp/preregistration or adversarial OS immutability.

**Последовательность:**
- Allocate unique run directory, capture source/input/environment before run; immutable seed/grants/injection recorded.
- Keep progress journal separate; include all failures/incomplete cases and receipts.
- Freeze final manifest once under run-specific path, hash exact bytes; store ref/hash outside manifest to avoid circular self-hash.
- Resolver checks manifest and each referenced artifact/version hashes; no fallback to latest on missing/mismatch.
- Second run gets different path; first report still resolves first bundle/hash even if latest changes.

**Поля / состояния:**
```json
{
  "minimum_ref_schema": {
    "schema": "evidence-ref/v1 (proposed, local protected evidence not public MCP metadata)",
    "run_id": "unique allocated once; run-specific directory never reused",
    "manifest": {
      "path": "run-specific frozen manifest path",
      "sha256": "SHA256 of exact final manifest bytes; excludes self-hash",
      "capture": "FINAL_FROZEN; unfinished/failed retained but not PASS"
    },
    "source_lineage": "path->sha256 byte map and digest of specified sorted canonical map; dirty/commit optional only if actually measured, never invent Git revision",
    "input_lineage": "requirements/card/fixture/seed/grants/injection map, exact hashes or explicit unavailable",
    "environment": "actual Python executable/version + OS + installed mcp/PyYAML versions, command argv/cwd; no secrets",
    "case": "case_id+variant+locator (JSON pointer or file:line)",
    "receipts": "paths + hashes for raw frames, process command/PID/exit/grants, before/after readback, recovery and negative findings",
    "resolution": "validate all hashes and lineage before using verdict; no fallthrough to latest; mismatch=MISMATCH not PASS",
    "latest": "optional navigation pointer to run_id/path/hash; not canonical evidence"
  },
  "current_example_ref": "runtime/RS002_A/immutable_reference_example.json",
  "retention": "Never remove previous or failed runs here. Operational WORM/OS write-protection/retention enforcement not implemented; unique create/no-overwrite + hash validation is minimal tooling mechanism.",
  "capture_semantics": "AU manifest hashes in this material are research-time consistency checks linked to auditor fingerprints, not a newly preregistered run or proof all prior report pointers safe."
}
```

**Action → expected → physical facts (все proposed/not_tested):**
- Действие: В будущем D/tooling выполнить два изолированных run и разрешить refs первого отчёта после второго; изменить latest pointer только как штатный эффект нового run.
  Ожидание: Первый bundle/manifest hash и version lineage остаются теми же; mismatched artifact version обнаруживается, не становится PASS.
  Физический oracle: Два run-specific manifests, fingerprints, ref resolution/hash comparison и retention старого bundle. Этот two-run check сейчас не запускался.
- Действие: After two future isolated tooling runs, resolve first ref; alter disposable copy manifest or source-lineage tuple
  Ожидание: old original still resolves; mutated copy rejected MISMATCH, not latest or PASS
  Физический oracle: two unique run manifests and before/after byte hashes + resolved case receipts + source/input map equality

**Наследованные физические факты:** Current code writes shared progress at 397/405/408 and run final at 408. Existing auditor run manifest bytes hashed here, not a two-run retention test.

**Риски:**
- No current two-run product/tooling replay; do not close TD21 on writing schema.
- Hash stored beside editable manifest is not tamper-proof against file owner.
- Latest copy previous-manifest.json is not sole canonical source lineage.

**Needs-user:** {"blocker": false, "for_minimum_refs": false, "conditional": ["Live evidence access/retention/immutability policy beyond local unique run bundles needs separate authorization."]}

**Первичные источники:** mockup/ab002_matrix.py:364-408; tech_debt.md:34-36
Evidence ID раскрыты в каталоге ниже и в JSON, не выданы за URL.

## Shape read + locked attach

| State | Read / locked attach | Domain / effect |
|---|---|---|
| FILE_ABSENT | absence tagged; not {} observation; create own target+tx only after re-read under existing lock | ABSENT; none until atomic replace |
| KEY_ABSENT_ROOT_VALID | root object exists, own target missing (membership test, not .get fallback); preserve other keys; create only own key | ABSENT; new record if allowed |
| TARGET_VALID_TX_ABSENT | own target dict (including {}), requested tx missing; preserve every existing tx and unrelated key, append own tx | ABSENT_TX; one intended append |
| VALID_MATCH | exact record digest/payload and bindings match expected bytes/canonical contract; idempotent no-write; still fresh readback required for ack | MATCHED; no duplicate |
| VALID_DIFFERENT | well-formed requested tx with different digest/payload/binding; no overwrite | TARGET_CONFLICT; none |
| ROOT_INVALID | existing list/null/scalar, bad JSON, duplicate keys or invalid encoding; same validator returns invalid; never replace with {} | TARGET_INVALID / ROOT_SHAPE|DECODE_INVALID; none if before effect |
| TARGET_INVALID | own key present but list/null/scalar/bool; empty file is DECODE_INVALID not FILE_ABSENT; same validator under lock | TARGET_INVALID / TARGET_SHAPE; none if before effect |
| TX_RECORD_INVALID | requested tx present as null/list/scalar or malformed dict; never treat null as absence; strict digest:string hex64, payload dict with tx_id/branch/revision/intent_digest/target_ref; type(revision)=int not bool; no extra record/payload fields in simulation v1 | TARGET_INVALID / TX_RECORD_SHAPE; schema-valid wrong binding -> TARGET_CONFLICT; none if before effect |
| UNAVAILABLE_OR_BUSY | I/O/permissions/lock timeout as typed error, not absence; retryable refusal; never reset | TARGET_UNAVAILABLE | TARGET_BUSY; unknown if any replace/send may already have occurred |

## Переходы попыток: без fake observed

| From → action | To | Observation / ack |
|---|---|---|
| pending or ambiguous → commit durable attempt bound to intent/tx/digest/target/actor/root/time | attempt_in_flight | none yet; ack=False |
| attempt_in_flight → validated read or locked validator proves invalid before this attempt effect | attempt_failed_pre_effect; intent pending with TARGET_INVALID | no successful observation; append typed attempt_outcome diagnostic only; ack=False |
| attempt_in_flight → send/replace entered; exception, disconnect, failed post-read or missing completion | ambiguous | unobserved or unmatched only if bytes actually read; phase=effect_possible; ack=False |
| attempt_in_flight → actual readback wrong but valid record | conflicting/unmatched (pending) | append exact bytes with matched=0 and verified INTERNAL stamp; ack=False |
| attempt_in_flight → actual exact readback + no explicit ambiguous reply | observed_exact -> bound ack | raw canonical expected or exact YAML + fingerprint,size,read_at,INTERNAL stamp; ack=only protected binding and confirmed() pass |
| attempt_in_flight → explicit ambiguous reply even if exact bytes observed | ambiguous until fresh reconcile (preserve existing conservative behavior) | exact bytes may exist, not force ack in lost-reply attempt; ack=False |
| pending or ambiguous after corrected own key → new process/new durable attempt; pre-read exact existing tx before deciding send | bound ack after real readback; otherwise one allowed append then readback | new real observation; never reuse failure as readback; ack=conditional |
| any → global integrity fails before next effect/observation | CHAIN_BROKEN / NOT_READY; abort fanout | no further effect or fabricated terminal observation; ack=False |

Пока сохранять fail-stop с доменным SYNC_PENDING и YAML pending. Предлагаемый per-intent YAML continuation — отдельный product choice RS002-DEC-CONTINUE; предпочтителен только при доказанной независимости, не ретроактивная гарантия A2. Любая CHAIN_BROKEN/недоказанная безопасность останавливает fanout. Ошибка после send никогда не proven-no-effect. Отсутствие observation само по себе не нарушение A2.

## Worker fix TD19 — контракт, не выполненная правка
- `mockup/admission.py:14-36,90-101,220-277,307-370` — retain internal proof, build public DTO separately for healthy and broken; _trace/resume recurse same builders, master early return scoped; sync observation uses unredacted stamp
- `mockup/server.py:183-215` — serialize one validated PublicDTO into text+structuredContent; typed errors/no raw exceptions; log only safe operational record
- `mockup/delivery.py:19-36,44-75` — retain triggers and confirmed() unchanged semantically; test internal full-stamp/ack links unaffected, no public serialization of snapshots
- `mockup/ports.py:12-24` — do NOT add diagnostic privilege to reviewer/owner or broaden branch grants; ports target robustness separate TD20
- `mockup/projections.py:25-77` — inventory nested schema/authorized refs; no global proof in scoped export; do not rewrite immutable claim data or solve future sharing policy silently
- `tests and isolated worker runtime / mockup README:next card must explicitly authorize these writes` — targeted regression secondary; negative real MCP/process/file/SQL E2E primary and document intentional public-field removals

**Критерии независимой приёмки:**
- AA fixed + AB normal change + AB positive control across six healthy surfaces and permitted AA-only sync; fresh PID; direct AB denied
- Nested inventories and exact safe schemas for text/structured/YAML/logs; omitted/master UNKNOWN variant and explicit union control
- Middle forbidden AB invalid UTF8 AND wrong hash on disposable populated copies, two PIDs/seven tools: refuse/NOT_READY/no effects; separate local exact locator oracle
- Actual readback/SQL observation→attempt→intent→ack and full internal stamp; no fake CHAIN_OK, no redacted internal evidence
- Independent reviewer/auditor on exact changed source version before affected A acceptance; preserve REQUEST_CHANGES until then

**Не расширять:**
- No TD20 robustness code in this card unless separately scoped
- No new live privileged diagnostic endpoint
- No repair/rewind, UD-01..06 selection, B/C/D acceptance, refinement implementation
- No all-channel-safe claim or expanded grants

## PL003 delta — семь точек → checks

Не запускался. Эти семь строк дополняют причинный хендофф, не выдают новый негативный план за готовый. Parent обновляет карту P0; PL003 запускается по поручению пользователя и готовит SEC003→QA003 и OMH delta, parent применяет. Known TD19 не превращается обратно в гипотезу и не откладывается до full security pass.

| Point / check | Исходный evidence state | Механизм / новый discriminating check |
|---|---|---|
| LP-A2-01 / CHK-A2-01 | OBSERVED_EXISTING_EVIDENCE | Forbid full proof anywhere in public DTO; hidden revisions AND hashes are dependencies, not harmless service metadata. Compare six outputs plus permitted AA-only sync across hidden AB admission; same AA bytes, AB control; no broad volatility mask. |
| LP-A2-02 / CHK-A2-02 | OBSERVED_EXISTING_EVIDENCE | Nested chain bypass survives filtering read_snapshot alone. Recursive inventories: trace.chain={status} and resume.trace.chain={status}; no count/head or alias in text/structured exports. |
| LP-A2-03 / CHK-A2-03 | OBSERVED_EXISTING_EVIDENCE | Known diagnostic disclosure remains finding, safe refusal is not successful read. Separate UTF8/hash corruption variants, two PIDs/seven tools, exact refusal schema and no physical effects; trusted fixture oracle separately matches locator. |
| LP-A2-04 / CHK-A2-04 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED | UNKNOWN master early return cannot sanitize previously attached global stamp. Omitted/master AA-only -> safe UNKNOWN + empty scoped revisions; union control has explicit grants, not diagnostic privilege. |
| LP-A2-05 / CHK-A2-05 | OBSERVED_TASK_LIST_ONLY_OTHER_SHAPES_HYPOTHESES | Absent and present-invalid must remain disjoint through locked re-read. Fresh/populated related/unrelated keys, list/null/scalar/tx malformed, membership null check, concurrent replacement, own-key recovery. |
| LP-A2-06 / CHK-A2-06 | OBSERVED_TASK_LIST_SEQUENCE_CONTRACT_PENDING | No successful observation is required for a proven pre-effect failure; possible-effect stays ambiguous. Record selected continuation policy before run; raw frames+SQL lineage and two retries; crash after send; no fake raw/ack, recovery one-write. |
| LP-A2-07 / CHK-A2-07 | KNOWN_DEBT_SOURCE_CONFIRMED_NO_NEW_TWO_RUN_PROBE | Manifest progress pointer is not evidence identity. Two-run retention + tampered-copy mismatch control; first hash/lineage/case receipts remain stable, latest navigation only. |

### GAP для полного негативного плана
- Dedicated selective search/ranking/snippets/count/cursor/cache: absent from TOOLS; GAP/NOT_IMPLEMENTED, never snapshot substitute.
- Branch-filtered snapshot is implemented; dedicated branch SEARCH not implemented.
- Immutable nested refinement API absent; separate research/slice per note, not current five questions.
- Logs/error routing/timing/size/attachments need independent capability inventory, explicit probes/thresholds; NOT_CHECKED here.
- Two-work/extra-branch tests require capability discovery (current fixture work and AA/AB only), not invented APIs.

## Frozen evidence refs

Минимум: unique run_id; immutable final manifest path+SHA256 exact bytes; frozen code/input maps + определённая канонизация; реальная environment/argv/cwd; case ID+variant+locator; raw frame/process/readback/recovery receipts с hashes. Latest только navigation, никаких fallback. Пример реально разрешаемого audit ref: `runtime/RS002_A/immutable_reference_example.json`; он явно помечает неполноту original env linkage и research-time capture. Самохеш manifest не вкладывать в хешируемые байты; hash хранить в ref. Hash проверяет согласованность, не обеспечивает OS WORM или preregistration.

Two-run criterion остаётся NOT_TESTED: второй уникальный run меняет latest, первый report по-прежнему разрешает старый manifest/hash/lineage/case receipts; испорченная disposable копия даёт MISMATCH. Никаких удалений прежних evidence или закрытия всего D.

## Source / claim ledger

| ID | Claim | Primary source / locator | State / verification |
|---|---|---|---|
| RC01 | Global verify and branch_heads inserted into all new public stamps | mockup/admission.py:39-101,220-277,307-370 | SUPPORTED / code / PASS static inspection |
| RC02 | Nested trace chain count/head independent leak; fixed AA vs AB change observed | runtime/AU002_A/run-b944ea96/scope/restricted-before-hidden.json:/trace/chain and /resume/trace/chain versus restricted-after-hidden.json | SUPPORTED / observed_inherited_reparsed / PASS reparse of existing files, product defect remains FAIL |
| RC03 | 14 middle-UTF8 refusals leak AB locator while saved physical snapshots equal | runtime/AU002_A/run-b944ea96/middle/responses.json:[*].response.chain; injection.json and injected-before.json vs after-refusals.json | SUPPORTED / observed_inherited_reparsed / PASS reparse; confidentiality remains FAIL |
| RC04 | No current dedicated privileged diagnostic capability/endpoint | mockup/ports.py:12-24; mockup/server.py:35-118,229-258 | SUPPORTED / code / PASS inventory |
| RC05 | read_target collapses malformed to {}; attach assumes dict and reaches list.get | mockup/ports.py:31-39,64-82 | SUPPORTED / code / PASS static; desired fixed validator NOT TESTED |
| RC06 | TASK:list evidence shows attempts without observations/acks and one-write recovery | runtime/AU002_A/run-b944ea96/malformed-target/after-malformed.json:/tables; final-recovered.json /tables,/writes; responses.json | SUPPORTED / observed_inherited_reparsed / PASS evidence reparse; product domain response FAIL in inherited run |
| RC07 | Current delivery schema binds exact evidence and stamps; status reduces any unconfirmed attempt to ambiguous | mockup/delivery.py:8-36,44-75; mockup/admission.py:315-356 | SUPPORTED / code / PASS static |
| RC08 | Current read context pins verification and output; never replace internal stamp with public one | mockup/storage.py:100-113; mockup/admission.py:323-352 | SUPPORTED / code / PASS static |
| RC09 | Shared manifest updated repeatedly; run-specific final manifest also written | mockup/ab002_matrix.py:364-408 | SUPPORTED / code / PASS static |
| RC10 | New field DTOs and safe error/target/outcome contracts actually work in product | cards/RS002_A_RESEARCHER.md:37-57 (deliverable is research, not implementation) | MISSING / proposed / NOT TESTED |
| RC11 | Selective search and refinement API absent in current MCP inventory | mockup/server.py:35-133; docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md:19-34 | SUPPORTED / code / PASS inventory only |

## Evidence catalogue

| ID | Local source | Locator / SHA256 |
|---|---|---|
| E-A2-01 | `REQUIREMENTS.md` | 31-44 / `2be43b2f8370e7e27df012831496af2d3bb000f66915975d8f24aff3e17310b8` |
| E-A2-02 | `REQUIREMENTS.md` | 46-52 / `2be43b2f8370e7e27df012831496af2d3bb000f66915975d8f24aff3e17310b8` |
| E-A2-03 | `REQUIREMENTS.md` | 82-98 / `2be43b2f8370e7e27df012831496af2d3bb000f66915975d8f24aff3e17310b8` |
| E-A2-04 | `cards/AB002_A_WORKER.md` | 32-42 / `f8fd0b6f737d9e23ac55608d14363599f9ce63806acf8adf638d4163a93ad236` |
| E-A2-05 | `mockup/admission.py` | 39-101 / `1f35db09af7ed738dcb8a5665e10ae23782961267bbf9370e922b69e28eea42e` |
| E-A2-06 | `mockup/admission.py` | 220-277 / `1f35db09af7ed738dcb8a5665e10ae23782961267bbf9370e922b69e28eea42e` |
| E-A2-07 | `mockup/admission.py` | 307-370 / `1f35db09af7ed738dcb8a5665e10ae23782961267bbf9370e922b69e28eea42e` |
| E-A2-08 | `mockup/ports.py` | 31-39 / `c4a48ad22ff7ba24f008b56f05a97acca5351cd518a3f1c64fc4ec07e40d84bc` |
| E-A2-09 | `mockup/ports.py` | 64-82 / `c4a48ad22ff7ba24f008b56f05a97acca5351cd518a3f1c64fc4ec07e40d84bc` |
| E-A2-10 | `mockup/server.py` | 197-215 / `10e0223ccc5a97a6fdb885c07053f97efd29afbad4ab193290e34cd07204cd76` |
| E-A2-11 | `mockup/delivery.py` | 19-36 / `0973b9b6d757a05bcae337a7642ac5d779dd9226167243f7339cc3ec08f5d6a9` |
| E-A2-12 | `mockup/delivery.py` | 44-75 / `0973b9b6d757a05bcae337a7642ac5d779dd9226167243f7339cc3ec08f5d6a9` |
| E-A2-13 | `mockup/storage.py` | 100-113 / `df09acf9406d8113d266a04779be753b1eb4c4c0d81bdd267e717a92271752e0` |
| E-A2-14 | `mockup/README.md` | 298-323 / `f5fc4b0d599d5f7cd2c44454c4019f68bc2860a45b22200a08e3db7e02ef0f1f` |
| E-A2-15 | `runtime/AU002_A/run-b944ea96/scope/restricted-before-hidden.json` |  / `2c02b113d8fa7c549dbb2c3865cdaf745a4310224e52c1ae20cbf73161253105` |
| E-A2-16 | `runtime/AU002_A/run-b944ea96/scope/restricted-after-hidden.json` |  / `80d9b752c63c8194ec1dcd1e7097a60bc2343d9141bd2b1952d622bfa0467008` |
| E-A2-17 | `runtime/AU002_A/run-b944ea96/scope/positive-control.json` | /claims / `d1fc3627832e6695d73468ca2fafe1f836a42c756e86c49f7629c31e0a44b20a` |
| E-A2-18 | `runtime/AU002_A/run-b944ea96/scope/result.json` | /actual/direct_AB_denials / `724524ac250adce98e66b4b17b3ff2a1e52f6a2991384c547b78a159ee757ad6` |
| E-A2-19 | `runtime/AU002_A/run-b944ea96/middle/injection.json` |  / `61787f191a648d01ed1cb0dcce82d75f1180259703717c220fb5f4971c23db61` |
| E-A2-20 | `runtime/AU002_A/run-b944ea96/middle/responses.json` |  / `c0ac8443ed9560b8c754b74f0d27498b63086f11c59289653700438f53079962` |
| E-A2-21 | `runtime/AU002_A/run-b944ea96/middle/injected-before.json` |  / `68b22929b4df6e1a39a3f058294f7cd0ad3201427816c881875b02947f93ec30` |
| E-A2-22 | `runtime/AU002_A/run-b944ea96/middle/after-refusals.json` |  / `68b22929b4df6e1a39a3f058294f7cd0ad3201427816c881875b02947f93ec30` |
| E-A2-23 | `runtime/AU002_A/run-b944ea96/malformed-target/responses.json` |  / `9bf53bba25c71cc30c1004095d398ff0c8135858b3860edf7a973659df64cb85` |
| E-A2-24 | `runtime/AU002_A/run-b944ea96/malformed-target/before-malformed.json` |  / `e247f37cf683924c3f877bea7558e59a9f2c553274453ddb3fd4244c59f30fc3` |
| E-A2-25 | `runtime/AU002_A/run-b944ea96/malformed-target/after-malformed.json` |  / `dd1f0fe8d8c722c832a04f26042e0a92a205f3e48bc01f734fddd9df2748c9c2` |
| E-A2-26 | `runtime/AU002_A/run-b944ea96/malformed-target/final-recovered.json` |  / `fbe2ddaf645b10e8482720439c2e1748946ebe34391dde2dfe83156554cf14b3` |
| E-A2-27 | `runtime/AU002_A/run-b944ea96/malformed-target/result.json` | /actual/proof / `c0e2f683a1aa4ed061e77273b8ec56a3d01ebbe768fe46241e98ea264eac5b90` |
| E-A2-28 | `artifacts/REVIEWER_AB002_A.json` | /per_invariant/A6 / `17d998b0ca183b809dc757e2c3f85169392d18fdf3051865ed0b6d915f391f1c` |
| E-A2-29 | `runtime/RV002_A/independent_probes.py` | 121-152 / `e01f6275d1b4fc141689be1bf8b33e4b9dc543b7ca55f57faa8f47ef478f0be1` |
| E-A2-30 | `mockup/ab002_e2e.py` | 26-35 / `7058d10664de87b53d96c57fad1658233ee74c49618d7644b811914ad02f9061` |
| E-A2-31 | `mockup/ab002_matrix.py` | 150-187 / `d2cb8b342fb593326a1e926e59bc854c86b7095d06357034a4654064bd7b3ee5` |
| E-A2-32 | `mockup/ab002_matrix.py` | 364-408 / `d2cb8b342fb593326a1e926e59bc854c86b7095d06357034a4654064bd7b3ee5` |
| E-A2-33 | `artifacts/REVIEWER_AB002_A.json` | /proposed_debts/0 / `17d998b0ca183b809dc757e2c3f85169392d18fdf3051865ed0b6d915f391f1c` |
| E-A2-34 | `tech_debt.md` | 30-36 / `6c32af2751555ae60b19b2604e7e690e6e13a02de38ccd7fc452230c94e8d317` |
| E-A2-35 | `runtime/RS001_RESEARCH.json` | /questions / `15d1d74f535b3e5579e2e11e542efe972862120f884f945f4749183e04974f7d` |
| E-A2-36 | `runtime/RS001_HANDOFF.md` | 18-35 / `ab961cbae823af5ae4816a1cdb5676074ef81279b7fca0a89e6ab19b944d90c0` |
| E-A2-37 | `templates/NEGATIVE_E2E_SECURITY_CONTRACT.md` | 23-95 / `f21c5b3bff6f8ed5ee698f54e5028d372da7b4314d9c6f99f2b784bb77cd3215` |
| E-A2-38 | `cards/PL003_NEGATIVE_E2E_PLANNER.md` | 1-39 / `b7872350b960245080e4d28e72a4792256dcdd507751d2dac36e517cd592a601` |
| E-A2-39 | `artifacts/AUDITOR_AB002_A.json` | /findings / `d8e238d911b29a4ac64e842e44566b70455247837c5cef66258dc1a8776835f1` |
| E-A2-40 | `reports/AUDITOR_AB002_A.md` | 36-48 / `6a0563877cd720829185b18fca5cbd8a3f1234592eead9d42e2d27d9ff24320d` |
| E-A2-41 | `E:/opencode_harness_portable/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md` | 95-111 / `a659489e85014b394e96ef947b3a0fc9d7bf6a1c1b0dc26eec1dc65f545d79e1` |
| E-A2-42 | `E:/opencode_harness_portable/docs/CODERS/09_FINDINGS_ESCAPE_HATCH.md` | 17-47 / `4672c5ce1e633305e05465d57b757a1ec09e2bbfad00a2435a63caa14308bcf4` |
| E-A2-43 | `E:/opencode_harness_portable/shared/code-factory-process.md` | 101-158 / `10e0fb1ab7af39c5ac948962807021c81fa290590b74e75f9d3e96d223ca9b39` |
| E-A2-44 | `mockup/server.py` | 35-118 / `10e0223ccc5a97a6fdb885c07053f97efd29afbad4ab193290e34cd07204cd76` |
| E-A2-45 | `cards/AN002_A_ANALYST.md` | 42-65 / `fb7148ee125ef6afa4cf6b79070a2b559e31dc3a2191953352f8431f50a4cf53` |
| E-A2-46 | `docs/AB002_PLAN.md` | 11-24 / `129c526751325f328de4811d2580737f2f73a4cd83ad16bcbd14d0e7d25e0a86` |
| E-A2-47 | `runtime/AU002_A/verification.json` |  / `6817c6ca2c2b2647529704879584f3aec748ac9e6a80245c79fb5c6d3c512dcb` |
| E-A2-48 | `runtime/AU002_A/run-b944ea96/manifest.json` |  / `97a93c529d338d849001790b5647308b7a15ff61c5cdfbe231332c80399a3a2c` |

## Остаток / UD / непроверенное

Immutable nested child refinement сохранён отдельной будущей исследовательской зависимостью по REQUIREMENTS:19-21,42-43 и docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md:19-34: parent/root/predecessor, admission/CAS/siblings, веточная актуальность, revalidation, ancestry ACL и пагинация. Не расширял текущие пять вопросов и не подменял replacement. UD-01…06, B/C/D, LIVE/auth/Git/checkpoint/OS остаются OPEN.
- All proposed mechanisms not implemented/not_tested in product. No new product MCP E2E, no prototypes claimed PASS.
- New AA-only sync/master differential, hidden-middle wrong-hash, null/scalar/record/race shape cases, new failure outcomes and optional YAML continuation need worker+independent E2E.
- Privileged live channel absent; fixture/operator oracle is not production authorization/OS sandbox.
- Two-run retention and mismatch tooling E2E not executed; references alone do not close TD21.
- Search/refinement/cursor/cache/timing/all-channel confidentiality and B/C/D/LIVE remain GAP/NOT_CHECKED.
- Research fingerprints taken before synthesis, not preregistered before historical auditor run.
- No independent fresh-context/cross-model review or agent dispatch in this restricted researcher role.

## Validation / воспроизведение

- Первый артефакт: `runtime/RS002_A/first_artifact.json` (PARTIAL).
- Read-only reparse: `runtime/RS002_A/inspect_inputs.py`; input hashes / inherited comparison / evidence_extract сохранены.
- Synthesis: `E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/RS002_A/finalize_material.py`.
- Независимая структурная проверка: `E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/RS002_A/validate_material.py`; receipt `runtime/RS002_A/validation.json`. Структурный PASS относится к материалу, не safety/приёмке продукта.
- Глобальные skills не менялись из-за узкого write scope; reusable workflow сохранён в docstrings собственных скриптов.

## НАХОДКИ (эскап-хэтч)

| Уровень | Что | Действие |
|---|---|---|
| L1 | Собственные контракты, refs и validation | Только разрешённые JSON/MD/runtime; без product writes. Первоначально ошибочно раскрыт путь docs/CODERS/shared; корректный первичный shared/code-factory-process.md прочитан. |
| L2 | TD20/TD21 | Отдельные scope и неизменные открытые долги; новых дублей/закрытий нет. |
| L3 | [ESCALATED] TD19 | Parent → узкий P0 fix/review/audit; AU002-A REQUEST_CHANGES сохранён. |
| L3 conditional | RS002-DEC-CONTINUE, live diagnostic rights | Только новый product choice нуждается в решении; не блокирует минимальный отказ от утечки. |

Continuation RS002-A не требуется после успешной проверки обязательных материалов. Следующих агентов ресерчер не запускал.
