# PL003 — негативный сценарный план по текущему коду

**COMPLETE_MATERIAL_ONLY**, не тестирование продукта и не SAFE. Product acceptance=false, новых E2E/атак/dispatch нет. Слова заказчика:

после  цикла обнови план OMH по тестированию сценариями как записи так и чтения обновления  выборочный поиск - поиск по веткам-  на предмет протечек из дроугих веток. создать через планера план тестирования и предварительный поиск местотказа-  где будет утечки где проблемы- и эти места и становятся  чеками для проверки и симуляций. - нужен прогон спеца по зеопасночти и тестированию - нужен шаблон новый для контракта по этому очень жосткий ядреный  работающия не на положительный результат а с ветором на заваливание и негатив

## Архитектура и действительный inventory

Fingerprint `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3` подтверждён read-only вычислением; 12 public schemas извлечены AST без импорта/запуска сервера. Полный `runtime/PL003/capability_inventory.json`, exact schemas `runtime/PL003/public_tool_schemas.json`, source hashes `runtime/PL003/input_fingerprints.json`, primary/support inputs `runtime/PL003/support_input_hashes.json`. Python stdlib SQLite/transactions/triggers, mcp stdio lowlevel + anyio, PyYAML safe dump. Environment из реального portable Python, не README: 3.11.15 (main, Jul 18 2026, 17:06:27) [MSC v.1944 64 bit (AMD64)]; mcp 2.3.0, PyYAML 6.0.3.

Public ingress → strict_arguments → dispatch → fixture Context scope/caps → admission/SQL/projections → persistence/export/OMHPort → same result as text+structuredContent. Candidate submit не baseline; независимый review+admit атомарно facts/events/head/outbox. Read transaction удерживает полный integrity check и projection/effect. В SQL есть unscoped ID materialization joins и branch heads для stale/global proof, поэтому scope output не следует только из входного guard. Export fsync+rename+readback; sync durable attempt перед внешним effect, затем independent observed bytes и bound ack. Никаких реализованных search index/ranking/cache/cursor; idempotency — отдельный stored receipt replay. Live OMH/Git/host auth/OS — SIMULATION/NOT_IMPLEMENTED.

| Public tool | Authorization | SQL/effect |
|---|---|---|
| dom_init | work+policy; simulation gate | binding, branch_heads; additive DDL |
| dom_resume | scope(branch), ready, full integrity_gate | nested snapshot+trace+outbox status in one read transaction |
| dom_submit | submit; work/task/branch/dependencies/applicability; check_references | candidates, idempotency |
| dom_review | review; candidate branch/dependencies; distinct author root; exact digest | candidate -> reviews |
| dom_admit | admit; reviewer identity/root/digest/dependencies/revision; references | candidate+review -> facts/events/head/idempotency/outbox atomic |
| dom_append | operation=append; same submit gates | same candidate path; no facts yet |
| dom_query | scope(branch), ready, full integrity_gate | events branch+revision -> claims and claim_snapshots ID joins |
| dom_snapshot | same alias gates | exact alias dom_query |
| dom_trace | scope; master limited UNKNOWN; no owner-close | snapshots -> dependencies/global heads -> residual; full verify_chain |
| dom_export | scope(branch), ready, integrity_gate; server-fixed export path | scoped snapshot -> PyYAML -> unique temp fsync replace readback -> handle/hash |
| dom_sync_status | scope(branch), ready, full integrity_gate | outbox branch -> ack/observation/attempt joins -> status |
| dom_sync | admit+scope(branch); repeated full gate and same read slice through effect | outbox -> durable attempts -> locked target/exports -> observations -> bound ack |

## Фактические GAP — не substitute и не PASS

- **GAP-SEARCH** (GAP/NOT_IMPLEMENTED): No query-text/property/type filtering/limit/offset/ranking/snippets/count/cursor API in TOOLS or route code; snapshot is not search.
- **GAP-BRANCH-SEARCH** (GAP/NOT_IMPLEMENTED): Branch-filtered snapshot EXISTS; dedicated search across/by branches DOES NOT.
- **GAP-REFINEMENT** (GAP/NOT_IMPLEMENTED): No parent/root/predecessor refinement API or current-leaf semantics; replacement archives, not refinement.
- **GAP-MULTIWORK** (GAP/NOT_IMPLEMENTED): WORK/TASK fixed in fixtures; binding id=1; foreign-work rejection possible, two legitimate work contexts unavailable.
- **GAP-BRANCH-ALLOCATOR** (GAP/NOT_IMPLEMENTED): Only AA/AB initialized and validated; no AA001 allocator or third inaccessible branch.
- **GAP-LIVE-AUTH** (GAP/NOT_IMPLEMENTED): Fixture principal/root/grants; no authenticated host binding or live OMH target.
- **GAP-OS** (GAP/NOT_IMPLEMENTED): Agent with terminal/files can bypass MCP; simulation has no OS sandbox; separate from MCP scope checks.
- **GAP-DIAGNOSTIC** (GAP/NOT_IMPLEMENTED): No diagnostic capability/endpoint; trusted local fixture oracle only; owner/reviewer/union not diagnostic-admin.
- **GAP-HISTORY-GET** (GAP/NOT_IMPLEMENTED): History exists inside snapshot; no separate get-by-ID/diff/source-fetch API; metadata links are inert.
- **GAP-CHECKPOINT-GIT** (GAP/NOT_IMPLEMENTED): No external anchor or live Git mutation; fixture GitPort intent NOT_IMPLEMENTED.
- **GAP-LINKS** (GAP/NOT_IMPLEMENTED): No backlink/neighbor/degree/dashboard/graph-view tool in TOOLS; link events carry only inert url+locator metadata (dom_contract link spec); new customer requirement REQUIREMENTS.md section "Пятое уточнение" has no API yet.

History/current and historical branch snapshots реализованы; отдельные history/diff/get/source API отсутствуют. Appendix comment/link/property/archive/applicability/replacement реализованы как кандидаты и review/admit; nested child refinement отсутствует. Full two-WORK isolation не доказать foreign-work rejection. Только AA/AB, третья ветка/allocator GAP. Scoped branch snapshot не selective/branch search. Missing search positive control => GAP, а не пустой безопасный результат.

## Карта отказов и воспроизводимые сценарии

Каждая строка `failure_map.json#/rows` содержит hypothesis_id → invariant/asset/actor/scope → актуальные file:line+SHA256 → boundary/action → check_id → expected/oracle/evidence/mode. `scenario_plan.json#/scenarios` — точные seeds/initial conditions/actions/injection/control/physical facts/recovery/limitations и role-specific variants; основной машинно-читаемый runnable contract, не нарисованный лог. Отсутствующие API явно not_implemented_api.

Known LP-A2 states сохранены байт-семантически из RS002; LP-A2-01/02/03 — TD19 observed, не новые гипотезы и не новые TD; LP-A2-04 source-derived; LP-A2-05 только TASK:list наблюдался; LP-A2-06 наблюдение list с pending choice; LP-A2-07 known TD21 source confirmed, two-run не исполнен. Новые HP-PL source-derived, не findings без прогона. Known TD15/18 retest не повторная регистрация.

| Scenario | Hypothesis → check | Операции | Primary owner | State |
|---|---|---|---|---|
| SC-LP-A2-01 | LP-A2-01 → CHK-A2-01 | read, export/status/error | SEC003 | OBSERVED_EXISTING_EVIDENCE |
| SC-LP-A2-02 | LP-A2-02 → CHK-A2-02 | read | SEC003 | OBSERVED_EXISTING_EVIDENCE |
| SC-LP-A2-03 | LP-A2-03 → CHK-A2-03 | read, export/status/error, restart/concurrency/recovery | SEC003 | OBSERVED_EXISTING_EVIDENCE |
| SC-LP-A2-04 | LP-A2-04 → CHK-A2-04 | read | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-LP-A2-05 | LP-A2-05 → CHK-A2-05 | write, export/status/error | QA003 | OBSERVED_TASK_LIST_ONLY_OTHER_SHAPES_HYPOTHESES |
| SC-LP-A2-06 | LP-A2-06 → CHK-A2-06 | write, export/status/error, restart/concurrency/recovery | QA003 | OBSERVED_TASK_LIST_SEQUENCE_CONTRACT_PENDING |
| SC-LP-A2-07 | LP-A2-07 → CHK-A2-07 | export/status/error | QA003 | KNOWN_DEBT_SOURCE_CONFIRMED_NO_NEW_TWO_RUN_PROBE |
| SC-HP-PL-01 | HP-PL-01 → CP-PL-01 | write, read | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-02 | HP-PL-02 → CP-PL-02 | write | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-03 | HP-PL-03 → CP-PL-03 | append-only update, write, read | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-04 | HP-PL-04 → CP-PL-04 | read, append-only update | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-05 | HP-PL-05 → CP-PL-05 | append-only update, write | QA003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-06 | HP-PL-06 → CP-PL-06 | append-only update, read | QA003 | KNOWN_DEBT_RETEST_NOT_NEW_FINDING |
| SC-HP-PL-07 | HP-PL-07 → CP-PL-07 | read, export/status/error | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-08 | HP-PL-08 → CP-PL-08 | read, write, restart/concurrency/recovery | QA003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-09 | HP-PL-09 → CP-PL-09 | write, export/status/error, restart/concurrency/recovery | QA003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-10 | HP-PL-10 → CP-PL-10 | write, read, restart/concurrency/recovery | QA003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-11 | HP-PL-11 → CP-PL-11 | selective search | SEC003 | GAP_NOT_IMPLEMENTED |
| SC-HP-PL-12 | HP-PL-12 → CP-PL-12 | branch search | SEC003 | GAP_NOT_IMPLEMENTED |
| SC-HP-PL-13 | HP-PL-13 → CP-PL-13 | append-only update, read | SEC003 | GAP_NOT_IMPLEMENTED |
| SC-HP-PL-14 | HP-PL-14 → CP-PL-14 | write, read | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-15 | HP-PL-15 → CP-PL-15 | write, read, export/status/error | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-HP-PL-16 | HP-PL-16 → CP-PL-16 | read, export/status/error | SEC003 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED |
| SC-H-LINK | H-LINK → CP-PL-17 | read, append-only update | SEC003 | GAP_NOT_IMPLEMENTED |

### Минимальные пошаговые процедуры (кроме общих handshake/readback/recovery)

#### SC-LP-A2-01 / CHK-A2-01
- Точка: mockup/admission.py:90-101, mockup/admission.py:220-246, mockup/admission.py:273-277, mockup/admission.py:364-370.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: AA fixed plus normal AB admission; six healthy surfaces query/snapshot/trace/resume/sync_status/export and separate AA-only admit-capable sync; repeat fresh PID.
- Positive: B positive control before/after; normal AA delivery
- Expected: No full global proof/revisions/UUID/head in public outputs; permitted AA data unchanged; only read_at excluded; retain internal full proof.
- Независимый физический факт: AB positive control + field-level raw MCP differential; no filesystem access for caller
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-LP-A2-02 / CHK-A2-02
- Точка: mockup/admission.py:256-270, mockup/admission.py:369.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Recursively inventory trace.chain and resume.trace.chain before/after AB admission; include both MCP channels and aliases.
- Positive: Own AA history still available; B exists independently
- Expected: Nested chain exposes only status under proposed RS002 schema; known TD19 until fixed.
- Независимый физический факт: Отдельный nested field inventory, fixed AA + AB positive control
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-LP-A2-03 / CHK-A2-03
- Точка: mockup/admission.py:48-70, mockup/admission.py:94-100, mockup/admission.py:30-36, mockup/server.py:213-215.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: On two separate populated copies corrupt middle hidden AB payload invalid UTF8 and wrong hash; two fresh PIDs each across query/snapshot/trace/resume/sync_status/export/sync.
- Positive: Healthy copy succeeds; oracle exactly matches injected event; do not weaken global gate
- Expected: Global CHAIN_BROKEN+NOT_READY safe uniform refusal; no data/exports/effects/foreign locator. Exact trusted local locator preserved separately.
- Независимый физический факт: Raw error field scan + exact physical before==after + admin diagnosis
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-LP-A2-04 / CHK-A2-04
- Точка: mockup/admission.py:248-258, mockup/admission.py:364-370.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: AA-only dom_trace omitted and master plus resume AA nested trace; compare explicit union actor. Do not call resume(master) valid because scope denies it.
- Positive: Explicit union trace with AA+AB and separate B existence
- Expected: Limited master UNKNOWN with empty scoped revisions, no global hash/count; union is explicit scope not diagnostic-admin.
- Независимый физический факт: Current entrypoint inventory + positive union control + hidden-AB differential; no new finding before execution
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-LP-A2-05 / CHK-A2-05
- Точка: mockup/ports.py:31-39, mockup/ports.py:64-71.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Fresh/populated target file absent vs own key absent/{}/list/null/scalar/bool; requested tx null/list/scalar/malformed/conflict; unrelated keys retained. Locked reread race valid->malformed on owned fixture.
- Positive: Valid exact matching target and absent own key; unrelated sentinel keys before/after
- Expected: Absent differs from invalid. Domain-safe refusal, unchanged target bytes, no fake ack. Current TASK:list raw AttributeError remains TD20 finding; other shapes hypotheses.
- Независимый физический факт: Raw MCP + exact target bytes + foreign key equality before/after and controlled recovery
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-LP-A2-06 / CHK-A2-06
- Точка: mockup/admission.py:312-357, mockup/server.py:197-215, mockup/delivery.py:68-75.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Malformed own target plus pending YAML; two new retry processes; own-key correction and fresh reconcile; separate crash after send and write-log failure after replace.
- Positive: Normal sync, then recovered own key one target write; unrelated keys unchanged
- Expected: Baseline fail-stop; YAML pending on shape error. Safe domain result is desired fix, raw crash finding. RS002-DEC-CONTINUE not agreed, no mandatory continuation. Possible effect remains ambiguous; no fabricated observation/ack.
- Независимый физический факт: SQL attempt/observation/ack links, write count, raw isError vs structured status; YAML outcome after research decision
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-LP-A2-07 / CHK-A2-07
- Точка: mockup/ab002_matrix.py:364-408.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Specialist-owned runner two unique run dirs, first report resolves frozen manifest hash after second; tamper disposable copy lineage/receipt to force mismatch; latest navigation only. Do not execute global existing matrix that writes outside own runtime.
- Positive: Valid original ref resolves; tampered copy rejected, no fallback
- Expected: First/failed evidence retained and resolvable; mismatched ref rejected; unique create-only manifest and external hash reference. TD21 not closed by planner.
- Независимый физический факт: Run-specific manifest/hash and frozen source/input tuple; retain earlier failures
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-01 / CP-PL-01
- Точка: mockup/server.py:136-180, mockup/admission.py:81-85, mockup/admission.py:118-133, mockup/dom_contract.py:19-39.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Send unknown tool/role/principal/root/capabilities/work overrides; malformed top-level/list/bool revision, duplicate JSON keys, NaN, surrogates, forged work/task, AA aliases aa/AA%00/../AB, mixed dependency/applicability containing AB. Keep size bounded.
- Positive: Valid AA envelope; AB-only control; helper same-root review refused.
- Expected: Strict refusal before protected mutation; no widening; caller-owned echoed tokens are not foreign disclosure. Errors reveal no hidden values.
- Независимый физический факт: Independent all-table rows and target/export bytes before/after plus raw frames. No stored candidate for rejected submit.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-02 / CP-PL-02
- Точка: mockup/admission.py:111-116, mockup/admission.py:155-188, mockup/storage.py:31-38.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: AA actor reuses AB candidate/review IDs, missing IDs, other candidate review, wrong digest/root; reuse same idempotency key across AA/AB grants with identical/changed digests; return to AA after B operation.
- Positive: Independent reviewer root-B admits own AA; same-root helper fails; changed payload mismatch.
- Expected: No foreign receipt from replay cache; no unauthorized review/admit or duplicate facts; same valid retry returns original own IDs.
- Независимый физический факт: Trusted oracle snapshots candidates/reviews/idempotency/transactions/events/outbox; raw denial differential missing vs forbidden; exact own replay receipt.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-03 / CP-PL-03
- Точка: mockup/admission.py:143-161, mockup/admission.py:188-216, mockup/dom_contract.py:89-98.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Append comment/link/property/archive/replacement/applicability using foreign claim_ref, supersedes or replacement_ref; valid AA references then foreign/missing; stale candidate references revalidated at admit.
- Positive: Valid own AA comment, link, property and supersedes; union-only authorized applicability control.
- Expected: Unauthorized reference denied without partial events/outbox; no side-effect before admission. Legitimate permitted applicability tested separately; do not globally forbid authorized sharing.
- Независимый физический факт: Read-only claims/events/claim_snapshots/outbox rows; no-effect hashes after denial; query/resume/export structural refs.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-04 / CP-PL-04
- Точка: mockup/projections.py:20-53, mockup/admission.py:143-154, mockup/projections.py:55-77.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Trusted union admits AB claim then AA applicability with distinct B origin/dependencies; AA-only reads head and historical query, resume, trace, YAML. Add archived/property before repeated applicability.
- Positive: B-only origin exists, AA-only unrelated B denied; permitted sharing positive control and pre-sharing AA snapshot.
- Expected: No unapproved foreign subtree expansion. Authorized sharing may carry explicit B origin: classify with established object-sharing contract, not automatic leak. Ambiguous declassification is BLOCK/needs-user, never silent redaction of immutable content. Preserve archive/properties.
- Независимый физический факт: Independent SQL joins by event branch and claim ID; fixture grant/sharing ledger distinguishes shared object from unrelated B canaries; exact historic original bytes.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-05 / CP-PL-05
- Точка: mockup/dom_contract.py:93-118, mockup/storage.py:66-90, mockup/admission.py:193-209.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Try reserved body/origin properties and append with forged supersedes, duplicate local IDs. Trusted separate SQLite fixture probe attempts UPDATE/DELETE/REPLACE/IGNORE/UPSERT against immutable rows and secondary UNIQUE keys (not actor-A capability).
- Positive: New valid append/admission before and after; all prior immutable rows hash-equal.
- Expected: Original body/quote/source/link/id/origin never overwritten; appended correction retains original history. Exact guards, not arbitrary exception; no bypass via IGNORE.
- Независимый физический факт: Independent hashlib raw bytes and ordered SQL rows before/after each rollback; exact SQLITE_CONSTRAINT_TRIGGER/IMMUTABLE where applicable, document chain guard ordering.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-06 / CP-PL-06
- Точка: mockup/projections.py:55-77, mockup/projections.py:41-47, mockup/admission.py:181-188.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Pin AA claim dependency AB revision, admit AB change, archive AA support then repeated applicability; convergence followed by new accepted work; history read at previous revision.
- Positive: Fully covered/converged/delivered fixture first; fresh independent review rejected if stale; known debts retained.
- Expected: Stale/archived/conflict/pending never silently become accepted support. Current convergence/revalidation guarantees limited by known TD15/18; record observed behavior, no invented revalidation endpoint.
- Независимый физический факт: SQL exact pinned claim_snapshots and heads, trace residuals plus previous/current snapshot bytes; no owner close.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-07 / CP-PL-07
- Точка: mockup/admission.py:273-294, mockup/server.py:183-215, mockup/server.py:229-258.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Export historical/current AA while AB changes; scan handle, YAML and all nested MCP content plus stderr/log; unknown tool names with bounded inert payload; attempt branch path traversal and extra output-path arguments; allow quote containing show AB as DATA only.
- Positive: Allowed export roundtrip; B-only export finds B; stored instruction remains exact data.
- Expected: Only server-fixed scoped export path/hash; foreign refs/proof/diagnostics absent; transport refuses extra args. User instructions/URLs remain inert; no claim of agent-level injection resistance.
- Независимый физический факт: Raw frames both channels recursively, export byte SHA/readback, file-tree delta, log scan; foreign canary inventory withheld from actor-A.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-08 / CP-PL-08
- Точка: mockup/storage.py:100-113, mockup/admission.py:220-226, mockup/admission.py:323-356, mockup/ports.py:40-82.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Two processes: AA reader/export/sync pauses at existing phase boundary while B admission competes; two reviewers race same AA revision; two reconcilers same pending tx. Barrier timestamps must prove actual overlap, not merely ThreadPool start.
- Positive: Uncontended AA/B runs first, retry after releasing barrier succeeds; separate same-branch and cross-branch races.
- Expected: Consistent committed snapshot or typed bounded busy; no mixed foreign metadata, partial admission, duplicate local target write, premature ack. Do not invent linearizability across external files.
- Независимый физический факт: Monotonic barrier journal/PID timing, SQL snapshots/branch heads, exact per-tx target/write counts and observation lineage, raw outputs.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-09 / CP-PL-09
- Точка: mockup/admission.py:210-219, mockup/admission.py:285-294, mockup/admission.py:314-357, mockup/ab002_launcher.py:25-31.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Real exit71 through trusted fault_hook after_facts/before_commit/after_commit, before_rename/after_rename, after_attempt/after_external_send/after_observation; drop reply after committed admit; reopen new PID and resume/retry same key.
- Positive: Same exact flow without fault; every recovered run includes permitted read/write control.
- Expected: Before commit rollback; after commit whole tx. Possible external effect stays ambiguous until actual readback. No duplicate IDs/write, false ack/READY or loss; partial temp is evidence not success.
- Независимый физический факт: PID+exit/crash stage; independent closed-handle SQLite/file snapshots before/death/recovery; matching tx/digest/intents and one-write local count.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-10 / CP-PL-10
- Точка: mockup/admission.py:17-36, mockup/storage.py:44-64, mockup/storage.py:91-113.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Owned copy: second process BEGIN IMMEDIATE lock; mode=ro; invalid DB header; directory at DB path; missing v2 layout and incompatible layout. Never corrupt original or require admin OS changes.
- Positive: Healthy identical copy first; unlocked/valid restored copy resumes; do not repair corrupted original in place.
- Expected: Precise STORAGE_BUSY/CORRUPT/READ_ONLY/UNAVAILABLE/MIGRATION_REQUIRED; no arbitrary-exception PASS or reset. Incompatible init leaves original bytes; explicit compatible init additive only.
- Независимый физический факт: Actual SQLite error code/name, file bytes before/after, preexisting rows retained after additive migration, process cleanup and recovery readback.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-11 / CP-PL-11
- Точка: mockup/server.py:35-133, mockup/projections.py:29-53.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Capture actual tools/list and schemas. If still absent, record GAP-SEARCH and UNKNOWN_TOOL for a clearly labelled nonexistent probe name; do not fabricate a working search. Future API needs exact/partial/empty/broad/type/property filters, limits/offset/sort/count/snippets/cursor tests.
- Positive: AA and B snapshots prove data existence only; search positive control explicitly UNAVAILABLE.
- Expected: GAP/NOT_IMPLEMENTED, never PASS from snapshot or a nonworking positive control. If added code changes fingerprint and requires revised plan before probing search.
- Независимый физический факт: Wire tools/list + AST schema inventory; missing positive search capability is blocking material, not isolation evidence.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-12 / CP-PL-12
- Точка: mockup/server.py:79-117, mockup/projections.py:29-53.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Inventory dedicated branch search separately from snapshot; future variants allowed/forbidden/missing branch, omitted/master/union, mixed list, forged case/encoding alias, foreign cursor/session; scope before ranking/count/snippet expansion.
- Positive: Snapshot AA succeeds and AB denied for A; these controls do not satisfy absent search.
- Expected: GAP-BRANCH-SEARCH while absent; branch-filtered snapshot checked in read cases but never substitutes for branch search.
- Независимый физический факт: Wire schemas and source routes; independent fixture oracle retains B existence.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-13 / CP-PL-13
- Точка: mockup/dom_contract.py:6-17, mockup/projections.py:35-47, docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md:19-35.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Inventory parent/root/predecessor/current-leaf/refinement endpoints. Future matrix foreign parent/cycle/siblings/deep chain/old revision/lineage pagination, current-leaf changes at independent admission and per branch.
- Positive: Existing append/replacement preserves source as separate control, not a refinement PASS.
- Expected: GAP-REFINEMENT; do not call replacement a refinement tree. No product depth limit selected or semantic sibling winner invented.
- Независимый физический факт: Schema absence/source; future oracle exact ancestor bytes + admitted leaf/revision + fork history, withheld foreign lineage.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-14 / CP-PL-14
- Точка: mockup/ports.py:12-24, mockup/server.py:229-258, mockup/fixtures/__init__.py:4-9, mockup/storage.py:28-38.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: AA->AB->AA calls same server with AA-only grants; separate B server then new AA process; reviewer-allowed AA, unknown fixture actor, explicit union actor; attempt work-W2 init/submit and third ZZ branch. In separate threat model test direct file/terminal visibility only on own fixture.
- Positive: B sees B before/after; union explicitly sees both but no diagnostic promotion; no-simulation init fails closed.
- Expected: Caller cannot change launch identity/grants. Foreign work rejected, two legitimate works/third branch GAP. File-owner bypass remains NOT_ENFORCED, not MCP ACL finding or production PASS.
- Независимый физический факт: Trusted launcher receipt principal/root/caps/branches/work per PID; raw responses; target/SQL no foreign mutations; actor A never receives oracle file handle.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-15 / CP-PL-15
- Точка: mockup/admission.py:323-356, mockup/delivery.py:19-36, mockup/delivery.py:44-75.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: After output sanitization candidate fix if ever dispatched, perform own AA scoped sync on populated AA+AB; liar/ambiguous port and negative foreign tx/digest/target bindings in trusted fixture SQL. Do not modify internal stamps or observed raw to pass public leak check.
- Positive: Normal exact delivery and second reconcile one-write; protected negative ack insertion rollback; old facts retained.
- Expected: Public DTO scoped but full internal global chain/head/revisions/read_at and raw evidence retained; ack iff exact bound observation. Lying attach no ack. Historical ack not perpetual target availability.
- Независимый физический факт: Independent SQL ack->observation->attempt->outbox join; recompute fingerprint/size from evidence, exact target bytes/YAML, check full internal stamp separately (not actor-A output).
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-HP-PL-16 / CP-PL-16
- Точка: mockup/admission.py:48-70, mockup/server.py:197-215, mockup/projections.py:29-53.
- Начало: Disposable one-WORK SQLite fixture, AA fixed and populated AB when relevant; no actual secret; grant ledger frozen before call; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Fixed AA and healthy hidden AB sizes 1 vs 8 admitted claims; 12 randomized paired AA queries per seed after warmup; collect monotonic durations and raw size plus logs/media fields. No high-load or network probe.
- Positive: Same-state AA repeat jitter control; positive B existence. No attachment surface currently declared; record exact wire shape and GAP if missing.
- Expected: Content/size differences localized without blanket volatile mask; only documented read_at excluded. Timing exploratory threshold max(5ms,20% median baseline) in repeated pairs triggers investigation, not automatic vulnerability or noninterference PASS. Healthy/broken health signal explicitly allowed.
- Независимый физический факт: Raw frames lengths, paired schedule/timestamps/load notes, independent hidden fixture ledger; no canaries handed to actor; timing NOT_CHECKED unless actually measured.
- Recovery: close affected PID/connections; read physical state, start NEW PID; dom_resume then same-key retry if safe; preserve failed run and all old facts; corrupt copies quarantined, recovery from clean owned backup only.

#### SC-H-LINK / CP-PL-17
- Точка: mockup/server.py:35-133, mockup/dom_contract.py:89-98, mockup/projections.py:20-53.
- Начало: FUTURE API ONLY. Today: no link-sensing tool exists (GAP-LINKS). At dispatch re-capture tools/list + AST; only if a backlink/neighbor/dashboard/graph surface exists AND fingerprint is rebound may variants L1-L8 run; otherwise record GAP and stop.; seeds SEC 3101/3109, QA 4201/4211.
- Действие/инъекция: Future variants (fixed AA, two hidden AB fillings 0 vs 8 links): L1 inbound AB->AA backlinks of an AA card (list+count); L2 outbound AA->AB link ghost/dangling target (ID, title, not-found vs forbidden); L3 neighbor counters/degree on AA card; L4 dashboards/aggregates (totals, orphans, most-connected, clusters, link-type histogram) computed over global set vs AA-visible set; L5 n-hop graph expansion crossing a legitimately shared node; L6 auto-suggested / self-sensing links (similarity) built from hidden text; L7 stale or cached counters after AB archive/applicability/refinement (delta side-channel, cursor/cache reuse across actors); L8 link append AA->forbidden ID must be atomically denied with no partial facts/outbox/backlink row. Scope filter must run BEFORE counts/ranking/expansion/suggestion.
- Positive: Today none can pass: backlink/neighbor positive control UNAVAILABLE. Existing branch-filtered snapshot of AA and B existence are NOT substitutes. Future: B sees B backlinks and union sees both before and after negatives.
- Expected: While absent: GAP-LINKS / NOT_IMPLEMENTED, never PASS and never substituted by snapshot link metadata. When implemented: every backlink, neighbor, counter and dashboard value for actor-A is a pure function of AA-visible set (identical under both hidden AB fillings); no foreign ID/title/count/existence via data, errors, cursor or cache; authorized explicit sharing is carried with explicit origin and treated per sharing contract, not as automatic leak.
- Независимый физический факт: Today: wire schemas + AST (absence is the evidence). Future: trusted privileged fixture oracle holds full link graph; differential of actor-A responses at fixed AA vs two hidden AB fillings (A/B oracle of contract section 5); positive control that actor-B/union legitimately sees its own backlinks.
- Recovery: Future only: close PIDs, read physical state, new PID, compare counters/dashboards with oracle graph; preserve failed runs..

## H-LINK — «самочувствующие связи» (новый канал, NOT_IMPLEMENTED)

Основание: REQUIREMENTS.md «Пятое уточнение» (2026-11-07, строки 23-27; parent-append, см. runtime/PL003/requirements_amendment.json): потеря базлайна агентом и связи в стиле Obsidian — backlinks, соседи карточки, дашборды (прообраз F:\AnalisysDataSet не читался). Гипотеза H-LINK / CP-PL-17 / SC-H-LINK / GAP-LINKS: обратные ссылки, счётчики соседей, степени, агрегаты дашборда, n-hop раскрытие и авто-предложенные связи могут раскрыть существование/число/ID объектов запрещённой ветки. Варианты L1-L8 описаны в failure_map.json#/rows (H-LINK). API нет: чек подготовлен на будущее, execution_state=NOT_EXECUTED, статус NOT_IMPLEMENTED, не PASS. Требуется отдельный план/аналитик по новой функции (по словам заказчика) до зондирования; по замечаниям оркестратора (docs/FULL_IMPLEMENTATION_PLAN.md п.3-4) TD19 P0 идёт ПЕРЕД связями, связи не вводить до закрытия allowlist-DTO; scope-фильтр обязан применяться ДО счётчиков/ранжирования/расширения.

## Rationale и порядок

Не полное Cartesian coverage. Приоритет: fixed AA + healthy changing AB (confidentiality), nested/proof serialization, middle corruption+restart (confidentiality AND integrity AND availability), foreign candidate/ref/history joins (integrity), archive/dependency changes (readiness), malformed own target+populated unrelated keys, concurrency+ambiguous delivery, crash at commit/rename/send and actual recovery. Каждому обязательному write/read/append-only update/selective search/branch search назначены check/scenario либо честный GAP. Role/session change, unknown/union, absent/mixed/encoded branch, old revision, pending/ambiguous, scoped exports и B controls — разные рискованные сочетания, не отговорка отсутствием полного Cartesian.

Parent: validate PL003 material → применить PREPARED OMH delta к существующему плану, не второй board → SEC003 → completed findings/material к QA003 → QA003 своими seeds/new failures → независимые review/audit → factory fix/recheck по findings. Completion SEC, не зелёный PASS, dependency для QA. P0 TD19 worker PREPARED остаётся обязателен отдельно, не defer/waive. Если parent запускает fix до specialists — re-fingerprint и rebind на изменившейся версии с baseline evidence сохранёнными, не приписывать этому плану новый digest. Planner не применяет delta/не запускает роли.
## Реальный маршрут и доверенная топология

Только при dispatch родителем. PY=`E:/opencode_harness_portable/.venv/Scripts/python.exe`, CWD=P.
Не запускать глобальный `mockup.ab002_e2e`: его OUT пишет runtime/AB002_A и shared manifest вне своего write scope.
Самостоятельный runner в своём runtime реализует raw stdio MCP initialize → notifications/initialized → tools/list → tools/call с корреляцией request IDs. Реальный server module `mockup.server` и `serve(Service, log_path)`; не fake responses. Стандартная положительная CLI:
`PY -B -m mockup.server --directory <own-run>/fixture --role author --simulation --log-file <own-run>/safe-log.jsonl`.
Это символическая argv с выделенным own-run, НЕ команда, уже выполненная планировщиком.
Для AA-only/AB-only и unknown fixture нужен собственный trusted test launcher в runtime роли: создать `Service(directory, role=..., simulation=True, branches=('AA',))` и вызвать реальный `serve`; caller аргументы не задают Context. У stock CLI нет --branches. Reference read-only `runtime/AU002_A/launch.py`; fault hooks доступны в admission и `mockup.ab002_launcher`, но писать/модифицировать их нельзя. Launcher может только назначить fixture identity, осмысленно pause/fault и реальные exit71 по названной стадии; не подменять ожидаемый ответ/guards/serializer/oracle. Liar mode — явно маркированная fault injection существующего simulation-порта, не достоверный ответ внешней системы.

Одна disposable DB на WORK=`demo:existing-work-W1`, TASK=`demo:existing-task-AA001`, POLICY берётся из актуальной fixture, не перепечатывается выдуманным hash. AA/AB: actor-A read+submit AA, actor-B read+submit AB, reviewer AA review/admit root-B, reviewer-allowed ограничен AA, helper root-A не независим от author, owner root-C только с явными grants, union AA+AB с явным разрешением. Unknown context через trusted launcher получает no positive grants; неизвестный --role stock CLI только launcher refusal, не тест MCP unknown-principal. No-simulation init должен отказать. Два действительных WORK и третья ветка отсутствуют: GAP, а не самовольное редактирование WORK/schema.

Trusted fixture oracle запускается отдельно от actor-A: он знает B canaries/IDs, делает read-only SQL/file reads и сохраняет operator-only receipts в своём run/oracle. Actor-A получает только MCP responses; не передавать ему полную БД, oracle map, путь/handle к foreign bytes. Это логическая граница harness, не сильная OS-изоляция. Агент с terminal/files и OS-admin — отдельные threat models, TD06/08 не оправдывают MCP leak. Не фильтровать stdout после того, как foreign bytes уже попали actor.
## Oracle, данные и физические квитанции

До негативов положительный контроль: own AA запись через dom_submit→independent dom_review→dom_admit, B-only реально читает B body/source/ID; исходное поле cannot-search помечено GAP, не выдать snapshot за поиск. Генератор seed+case+branch+field создаёт синтетические canaries в body/quote/link/comment/property/code/formula/origin/source/history. CRLF, NFD/Unicode supplementary, shuffled item order, current/stale/archive состояния сохранять точно; никакой PII/секретов. B control повторить после негативов. Неинформативный пустой результат/сломанный positive control => BLOCK.

Каждый case receipt: scenario_id/hypothesis_id/check_id/variant/seed; requirement и frozen source/input/env; actor grants; initial fixture and revision; точная argv/cwd, PID/start/end/exit, handshake/schema; все raw requests+responses без потери text, structuredContent, nested errors, logs/media/attachment fields; injection-stage receipt; expected и actual; independent before/death/after/recovery SQL/files; verdict и omissions. MCP isError/exit0 не означает domain-safe или отсутствие эффекта.

Read-back отдельным verifier, не service projection как единственный oracle: sqlite URI mode=ro + явный close всех handles; ordered rows ВСЕХ таблиц, schema/triggers и DB/file hashes; exact raw claim bytes/IDs/source/links/origin; target JSON и unrelated-key semantic equality, на отказе target byte equality; exports и temp-файлы, write log. На rejected write нет частичных candidates/facts/head/idempotency/outbox/attempts, кроме явно допустимого durable attempt sync (не смешивать этот случай с submit). Metadata global gate read itself не отключать. SQL JOIN ack→observation→attempt→outbox по intent/tx/digest/target; matched=1, raw hash/size/read_at; independently compare target bytes/YAML и full internal stamp. Не редактировать internal proof ради public sanitization. Полный locator порчи хранит отдельный fixture oracle, не restricted logs/text/structured/nested/export.

AA fixed / healthy hidden AB изменяется: рекурсивный field differential, исключение только документированного read_at. Не broad volatile mask, не один grep канарейки: сверять IDs/counts/seq/heads/hash/paths/структурные ссылки; B existence отдельно. При sharing сначала утверждённая object authorization: B origin в явно разрешённом shared claim не автоматически leak; неопределённый declassification contract => BLOCK/needs-user. Global CHAIN_BROKEN/NOT_READY разрешён как safe health signal, foreign locators запрещены. Safe Broken proposed exact {status:CHAIN_BROKEN, readiness:NOT_READY, ready_for_owner_review:false, blockers:[EVENT_CHAIN_BROKEN], simulated:true}; current product ещё не реализует. Timing не обещать: только заданная bounded exploratory серия и jitter control, нет замеров => NOT_CHECKED.

Run evidence: новый уникальный runtime/<ROLE>/run-<seed>-<uuid>/; до исполнения заморозить maps source/input/fixture/grants/injection/env (Python executable/version, mcp/PyYAML/SQLite/OS, без полного env/secrets). На source drift STOP/rebind plan, не смешать PASS ревизий. progress journal отдельно. Финальный manifest create-only в run-specific directory, exact byte hash вынести в own result evidence_ref вне manifest; refs каждого receipt с SHA256, source/input lineage, seed and case JSON pointer. latest только навигация. Missing/mismatch => BLOCK/MISMATCH без fallback. Первый, неудачный, flaky и прерванный run НЕ удалять; WORM/защита OS-owner этим не доказана.
## Строгий итог и границы

Первым собственный минимальный JSON PARTIAL/IN_PROGRESS с exact scope/remaining, копию сохранить first_artifact.json; никакого fake PASS. В финале свой JSON + MD, completion_state=completed только при полном собственном материале; verdict REQUEST_CHANGES/BLOCK/NO_VIOLATION_OBSERVED_IN_SCOPE, не SAFE/secure и не product acceptance. Каждому check ID назначить EXECUTED_NEGATIVE/CONTROL_FAILED/FINDING/GAP/NOT_TESTED с receipts и условиями (это состояния исполнения, не фиктивные тесты PL003). Findings: ID, severity impact-based, violated boundary/prerequisite/minimal repro/seed, expected/actual/raw evidence/source version, existing debt_ref или предложенный новый локальный finding; mitigation suggestion без product fix. TD19/20/21 не дублировать и не закрывать.

Report начинает раздел 0 «подозревал → проверил → оказалось», включая опровергнутые подозрения, known facts и UNVERIFIED; есть отдельный verdict, coverage/omissions/replay/recovery/limitations и НАХОДКИ (эскап-хэтч) уровней 1/2/3. Вне scope finding фиксировать в собственном JSON/MD и передавать parent для реестра — shared tech_debt.md здесь read-only. Нет квоты находок, no skip/xfail/broad-except-pass/fake logs/ответов/скрытых fallback/смены expected задним числом/правки продукта. Нельзя расширять grants, очищать inconvenient evidence, делать self-acceptance, закрывать OMH owner task.

TD19 известная major утечка: future plan/PASS не отменяет обязательный P0 fix cards/AB003_TD19_WORKER_PREPARED.md (не DISPATCHED). TD20 shape list raw AttributeError — finding, не correct refusal; list/null/scalar extension не выдавать за прежнее наблюдение. Базовый shape-failure FAIL_STOP, domain-safe отказ ожидается от будущего fix. Обязательный YAML continuation НЕ СОГЛАСОВАН, RS002-DEC-CONTINUE остаётся NEEDS_USER; не менять expected на continuation без решения. Integrity/storage inability to prove safety останавливает fanout в любом случае. Durable attempt не observation, отсутствие observation после proven pre-effect failure само по себе не A2 defect; after-send uncertain => ambiguous, no fake matched/ack. Partial YAML ack не общая SYNCED/READY.

Не более двух детей одновременно; RPC ≤25s, child ≤90s, role wall ≤1800s, payload ≤64KiB, ≤16 claims/branch, DB ≤16MiB, retained role evidence ≤128MiB, timing 12 randomized paired AA queries/seed после warmup, два seed по карте. Если объём/время/tool budget (120 calls ориентир) исчерпан, остановить только свои зарегистрированные PIDs, закрыть handles, сохранить raw evidence и точный remaining/next action/source/input/seed в continuation.json той же роли; parent НЕ дописывает verdict. Не уменьшать обязательное покрытие ради completed. Unexpected child nonzero/log error сохранить и классифицировать, не swallow. Cleanup только own PID/handles/temp resources после capture; сохранять доказательства, не удалять runs. Не kill-all.

Разрешены local read/search/write/patch/terminal и указанный Python, только собственные disposable fixture/processes. No network/listeners/install/Git/paid calls/real secrets/live user DB/live plugin/config/registry. Продукт, tests, live configs/plugins, researcher/старые evidence/debts — read-only. Не запускать других агентов, не применять OMH delta. Сильный OS sandbox/external checkpoint/live auth/Git/OMH не следуют из simulation. Не claim полного Cartesian coverage, full-system acceptance или all-channel noninterference.

## Evidence планировщика / limits

Свой first PARTIAL сохранён; статическая извлечённая схема и hashes — не MCP tools/list run. `runtime/PL003/validation.json` проверяет IDs/coverage/scopes/paths/hashes, не продукт. `runtime/PL003/manifest_ref.json` указывает frozen run-specific material manifest с exact hash; latest не sole proof. Input fingerprints сняты во время этого планирования, не до прежнего AU E2E. Executed product checks=0. Новые attack findings=0 (не означает нет уязвимостей). TD19/20/21 OPEN; search/refinement/live/OS/Git/checkpoint gaps неизменны; RS002-DEC-CONTINUE не решён. Глобальные skills не менялись по узкому write grant; воспроизводимый workflow сохранён в runtime/PL003 build/validate scripts.
