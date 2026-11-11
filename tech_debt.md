# Реестр техдолгов проекта (TD-DOM)

Формат по `docs/CODERS/05_REVIEWER_AUDITOR_TECHDEBT.md`: фиксирует тот, кто нашёл. Статусы: open / in_progress / closed.

| ID | Долг | Severity | Источник | Статус |
|---|---|---|---|---|
| TD-DOM-01 | Нет внешнего checkpoint цепочки событий: самосогласованная вставка события не обнаруживается, откат базы не детектируется | major | AC001-R2 (N2/KF04) | open |
| TD-DOM-02 | Нет инъекции коллизии UUID клайма — поведение при коллизии не проверено | minor | AB001 T11 | open |
| TD-DOM-03 | Реальный Git merge не реализован: слияние веток и неизменность ID при merge не проверены | major | AB001 T17/T20 | open |
| TD-DOM-04 | Падение процесса на стадии `after_rename` не инжектится (KF02) | minor | AB001 | open |
| TD-DOM-05 | `guarded` превращает любой `sqlite3.OperationalError` в `STORAGE_BUSY_OR_UNAVAILABLE`, маскируя битую схему и read-only | minor | AC002 M3 | open |
| TD-DOM-06 | OS-изоляция от прямого доступа к БД и от неограниченного `terminal` у исполнителя не обеспечивается (`NOT_ENFORCED`) | major | AC002, дизайн | open (ограничение макета) |
| TD-DOM-07 | Аллокатор кодов веток «две буквы + три цифры» не реализован: `AA`/`AB` захардкожены в схеме и валидации | major | REQUIREMENTS §4 | open |
| TD-DOM-08 | Живая привязка к OMH и аутентификация исполнителя/проверяющего не реализованы (Q01/Q02) | major | OMH_CODE_REVIEW, AC001 | open |
| TD-DOM-09 | Детерминизм YAML вне этой машины и версии PyYAML не проверен | minor | AC002 | open |
| TD-DOM-10 | `docs/STATUS.md` и карты отстают от кода при быстрых циклах | minor | AC002 M6/KF03 | in_progress |
| TD-DOM-11 | `INSERT OR REPLACE` обходил иммутабельность: снимок зависимостей и маркер ветки перезаписывались, проекция давала ложную готовность. Воспроизведено оркестратором (`runtime/tmp/probe_replace.py`) | **critical** | AC001-R2 (R2-1) | fixed в AB001-r5; ревью AC001-R3: 258/258 guard matrix, APPROVE |
| TD-DOM-12 | `branch_heads` изменяема без ограничений: `UPDATE branch_heads SET revision=0` принимается (проверено оркестратором, `runtime/tmp/probe_heads.py`, `REWIND_ACCEPTED=yes`). При сведённой и синхронизированной ветке откат головы убирает `STALE_CHECK` и даёт ложную готовность. Нужен монотонный `BEFORE UPDATE` и инвариант `branch_heads.revision >= MAX(transactions.revision)`. **AU001 дополнил последствия**: после откатa транзакции ревизий выше головы остаются в БД, но исчезают из проекций; штатный `admit` падает `IntegrityError: IMMUTABLE` наружу из `dispatch` (не доменный статус); `sync` навсегда остаётся `SYNC_PENDING` (`YAML_EXPORT=error`); `submit` отдаёт ложный `SCOPE_DENIED` | major | AC001-R3 (NEW-1) + AU001 (F-AU-08) | **closed** (2026-11-10): добавлены триггеры в `storage._create_triggers`: `branch_heads_monotonic_update` (BEFORE UPDATE WHEN NEW.revision < OLD.revision → BRANCH_HEAD_REWIND), `branch_heads_invariant_update` (BEFORE UPDATE WHEN NEW.revision < COALESCE(MAX(tx.revision),0) → BRANCH_HEAD_BELOW_TX), `branch_heads_no_delete` (BEFORE DELETE → BRANCH_HEAD_DELETE). Проверено: rewind 5→3 → BRANCH_HEAD_REWIND, delete → BRANCH_HEAD_DELETE, invariant держит head ≥ max tx. |
| TD-DOM-13 | Состояние доставки не связано с фактом доставки: `sync` пишет `ack` из `attach()` **до** read-back; `Service.delivery()` — публичный мутатор `delivery_events` без capability/scope/валидации `state`; `delivery_events` принимает `ack` без сверки `(intent,tx,digest)`. Итог: `ready_for_owner_review=true` достижим без единого байта в цели (роль `author` с одной capability `submit`). Воспроизведено: `runtime/AU001/probe3.py` (S2,S3), `probe5.py` (C2). **Подтверждено оркестратором чтением кода**: `admission.py:247` без декоратора и проверок; `admission.py:268-270` пишет в `delivery_events` возвращённое портом состояние (включая `ack`) до сверки `exact`; отзыв ack при неудачном read-back отсутствует | **critical** | AU001 (F-AU-02/03/04) | **closed** (2026-11-10): v2 delivery facts + SQL-триггеры (`delivery_acks` binding, `legacy_ack_refused`); `sync()` пишет `ack` только при `exact` read-back и `report!='ambiguous'`; `Service.delivery()` → `_delivery()` (private) с capability('admit')/scope/state-валидацией, отказ `DELIVERY_ENGINE_ONLY`. Проверено: S2 → `IntegrityError ACK_REQUIRES_OBSERVED`, S3 → `ambiguous`/`NOT_READY`, C2 → состояние не меняется; 8/8 `test_ab002_delivery` + `test_immutable_replace` pass. Отзыв ack — неявный через `confirmed()` re-verify при чтении.) |
| TD-DOM-14 | Веточный `trace`/`resume` отдаёт `ready_for_owner_review=true`, когда `trace('master')` на том же состоянии — `NOT_READY`; scope ответа (одна ветка) нигде не помечен ни в поле, ни в схеме инструмента. Воспроизведено: `runtime/AU001/probe4.py` (B1), `server.dispatch(owner,'dom_trace',{'branch':'AA'})` | major | AU001 (F-AU-01) | open |
| TD-DOM-15 | `STALE_CHECK` не имеет механизма актуализации: зависимость клайма пинится на точную ревизию ветки в иммутабельном `claim_snapshots`, `archive` локальна для ветки, API пересмотра нет. Два режима: `dependencies={}` — проверка не срабатывает никогда (так делает всё демо), пин — блокирует навсегда. Воспроизведено: `runtime/AU001/probe3.py` (S1), `probe6.py` (E1) | major | AU001 (F-AU-07) | open |
| TD-DOM-16 | Проекция не переживает событие с неожиданной формой payload: `snapshot` падает `KeyError`, `trace`/`query` выбрасывают исключение наружу (`guarded` ловит только `Denied`/`OperationalError`), поэтому `CHAIN_BROKEN` не отдаётся. Воспроизведено вставкой события с корректным `previous_hash` и payload без `value` | major | AU001 (F-AU-05) | open |
| TD-DOM-17 | Экспорт YAML не связан с цепочкой/БД: нет `chain_head`, `tx_id`, `event_hash`, поэтому `sha256` подтверждает только целостность файла, а не происхождение; `sync` не гейтит на `CHAIN_BROKEN` (export/sync проходят, блокирует только `trace`) | major | AU001 (F-AU-09/10) | open |
| TD-DOM-18 | `converged` — монотонная защёлка: одно событие `converge` снимает `BRANCH_NOT_CONVERGED` навсегда, включая ревизии, добавленные после решения о сходимости. Воспроизведено: `runtime/AU001/probe_perturb2.py` (P1) | major | AU001 (F-AU-06) | **closed** (2026-11-10): в `projections.snapshot` флаг `converged` сбрасывается в `False` при любом контент-событии после `converge` (claim/applicability/archive/property/replacement/conflict/resolve/exclude). Проверено: P1 → после добавления нового общего контента `converged_flag=false`, `NOT_READY [BRANCH_NOT_CONVERGED]`. |

## Правило

Новый долг получает ID при обнаружении, а не при исправлении. Долг, найденный вне scope задачи, всё равно регистрируется (эскап-хэтч 09, уровень 2). Закрытие — только с указанием проверки, которая это подтверждает.

## Сводка открытых долгов по областям (обновлено 2026-11-10)

Закрыто в этом цикле: TD-DOM-12 (монотонность `branch_heads`), TD-DOM-13 (связь состояния доставки с фактом доставки), TD-DOM-18 (монотонная защёлка `converged`). Ранее закрыто: TD-DOM-11. Остаётся открытым: 25 пунктов (TD-DOM-01…10, 14…17, 19…31), из них TD-DOM-10 — in_progress. Новые: TD-DOM-22…31 (блок внесения клаймов, учёт сращивания с OMH).

По областям (ветки AA/AB общие, если не указано иное):

- **Хранилище/цепочка (общее):** TD-01 (внешний checkpoint цепочки), TD-02 (коллизия UUID), TD-05 (`guarded` маскирует OperationalError), TD-06 (OS-изоляция, ограничение макета), TD-16 (проекция на неожиданный payload).
- **Ветки/сходимость (AA, AB, master):** TD-03 (реальный Git merge), TD-07 (аллокатор кодов веток), TD-14 (scope trace/resume), TD-15 (актуализация STALE_CHECK). (TD-18 закрыт.)
- **Доставка (общее):** TD-19 (утечка метаданных между ветками), TD-20 (malformed target), TD-21 (lineage манифеста).
- **OMH/живая привязка (общее):** TD-08 (живая привязка и аутентификация, Q01/Q02).
- **Блок внесения клаймов (claim-entry, lite/strict):** TD-22 (раздвоенный интерфейс), TD-23 (type-specific required не в Schema), TD-24 (нет diff при update), TD-25 (binding к OMH task), TD-26 (origin_version жёсткий), TD-27 (self-review в convenient-пути), TD-28 (идемпотентность ввода), TD-29 (навигация по версиям), TD-30 (атомарность multi-branch), TD-31 (маркеры связей/refinement).
- **Инфраструктура/качество (общее):** TD-04 (process death after_rename), TD-09 (детерминизм YAML), TD-10 (актуальность docs/STATUS, in_progress), TD-17 (provenance YAML-экспорта).
- **Процесс (общее):** TD-04 входит сюда же.

Красные тесты (не долг, но требуют триажа): `test_event_chain_is_verified_and_forgery_is_detected`, `test_idempotency_is_scoped_to_external_work_ref`, `test_actual_death_reopen[after_commit]`.

## AU002-A — новые наблюдения после RV002-A (append-only)

| ID | Долг | Severity | Источник / условия закрытия | Статус |
|---|---|---|---|---|
| TD-DOM-19 | Новая metadata/diagnostic выдача integrity gate нарушает branch scope: AA-only caller видит AB revision (0→1) на query/snapshot/trace/resume/sync_status/export; при повреждённом среднем AB event получает его запрещённый UUID через `chain.broken_event_id` на семи поверхностях. Прямые AB вызовы при этом SCOPE_DENIED. Не OS-admin bypass: здоровая утечка достижима read-only MCP caller при штатном AB admission; corruption только disposable fixture для второй ветки проверки. | major | AU002-A F-AU002-01, `mockup/admission.py:48-51,90-100`; `runtime/AU002_A/run-b944ea96/scope/{result,restricted-before-hidden,restricted-after-hidden,positive-control}.json`, `middle/{injection,responses,result}.json`. Закрытие: scope-safe snapshot/diagnostics без запрещённых revisions/counts/UUID при сохранении fail-closed integrity и привилегированного локатора; независимый MCP differential test при фиксированной AA и меняющейся AB, затем corruption/restart. Не дубликат TD-DOM-06/08/14. | open |
| TD-DOM-20 | OUT_OF_SCOPE_FINDING, интеграционная устойчивость SIMULATION target: корректный JSON с `TASK: []` проходит read_target как пустой, затем attach вызывает `.get` у list. Два новых MCP процесса получают isError с raw AttributeError вместо доменной target-диагностики. Остаются два durable attempt без observation, YAML не исполняется, повтор без внешнего исправления формы повторяет отказ. Ack/READY НЕ сфальсифицированы; после восстановления owned target key reconcile работает. | major | AU002-A F-AU002-02; `mockup/ports.py:31-39,67-71`, `mockup/admission.py:335-345`; `runtime/AU002_A/run-b944ea96/malformed-target/{responses,before-malformed,after-malformed,final-recovered,result}.json`. Закрытие: явная проверка формы target и безопасная структурированная ошибка; новые MCP процессы на list/null/scalar target не выбрасывают attribute/type ошибки, не создают ложный ack, сохраняют чужие записи; восстановление проверено физически. Это не новая production auth/OS гарантия и не ложный A1/A2 ack. | open |
| TD-DOM-21 | D tooling: зарегистрировано ранее предложенное RV002-A-DEBT-01, без нового дублирующего finding. Общий `runtime/AB002_A/e2e_manifest.json` перезаписывается runner; ссылка без immutable run lineage может адресовать другой прогон. | minor | RV002-A-DEBT-01, `artifacts/REVIEWER_AB002_A.json:proposed_debts`; `mockup/ab002_matrix.py:364-408`. AU002 использует собственный `runtime/AU002_A/run-b944ea96/manifest.json`. Закрытие: immutable run-specific manifest + source/input fingerprints и cross-run lineage вместо shared pointer в сдаче. | open |
## Claim-entry — долги, выявленные при обзоре 2026-11-10

Формулировка с учётом будущего сращивания с OMH (живая привязка, независимый review, единый интерфейс ввода/вывода). Источник: обзор mockup/lite.py (claim/update/find/describe/start), mockup/server.py (LITE_SIGNATURE), docs/CLAIM_ANATOMY_AND_LINK_MARKERS.md.

| ID | Долг | Severity | Источник | Статус |
|---|---|---|---|---|
| TD-DOM-22 | Блок внесения клаймов раздвоен: lite-профиль имеет dom_claim/dom_update/dom_find, строгий — только dom_submit с полным пакетом. Единый интерфейс ввода/вывода для создания клайма отсутствует; при сращивании с OMH нужен один путь с независимым review. | major | claim-entry review | open (analysis done) |
| TD-DOM-23 | Type-specific required-поля (quote→source_ref, decision→
ationale, ormula→expression, code→
epository_ref+
elative_path, data→rtifact_ref, concept→definition, 	ext factual→evidence) не помечены required в JSON Schema dom_claim; валидация только серверная, клиент не обнаруживает контракт. | minor | claim-entry review | open (analysis done) |
| TD-DOM-24 | dom_update не возвращает diff старой/новой версии; нет явного «что изменилось» в ответе. | minor | claim-entry review | open |
| TD-DOM-25 | Claim не связан с идентификатором задачи OMH: 
equirement_refs — произвольные строки (R1/R2), не проверяются против OMH; при живой привязке нужен binding к OMH task/work (TD-DOM-08). | major | claim-entry review, TD-DOM-08 | open |
| TD-DOM-26 | origin_version жёстко задан (lite-v1 / synthetic-artifact-v1); реальный OMH требует версионирование по источнику/ревизии. | minor | claim-entry review | open |
| TD-DOM-27 | dom_claim (lite) саморецензирует (
eview_level=self); независимый review недоступен в convenient-пути. При сращивании с OMH нужен независимый путь для claim-entry. | major | claim-entry review | open (analysis done) |
| TD-DOM-28 | Нет идемпотентности на уровне ввода клайма (внешний ключ); дедупликация только по идентичному содержимому (content-hash). Повтор с другим payload не различается. | minor | claim-entry review | open |
| TD-DOM-29 | Нет навигации по цепочке версий claim (
ecord_id/ersion вычисляются, но нет API «показать все версии / diff»). | minor | claim-entry review | open (analysis done) |
| TD-DOM-30 | Применимость (pplicability) и 
equirement_refs задаются при внесении, но расширение применимости — отдельное событие; нет атомарного «внести клайм сразу в несколько веток». | minor | claim-entry review | open (analysis done) |
| TD-DOM-31 | Маркеры связей M1 asis[], M2 
efines, вычисляемые обратные ссылки (по CLAIM_ANATOMY_AND_LINK_MARKERS.md) не реализованы; дерево уточнений (refinement) отсутствует. | minor | claim-entry review, docs/CLAIM_ANATOMY | open |
## TD-DOM-22 — суб-долги (ветка унификации claim-entry)

Источник: docs/TD22_CLAIM_ENTRY_UNIFICATION_PLAN.md. Статус родительского долга TD-DOM-22: open (анализ/суб-план выполнен, реализация не начата). Поддолги закрываются по мере реализации шагов плана; закрытие — с указанием проверки.

| ID | Поддолг (шаг плана) | Severity | Зависимости | Статус |
|---|---|---|---|---|
| TD-DOM-22.1  **closed** (2026-11-10): claim_entry.py created, lite.py shim, admission/server switched. Tests 61 pass, demo exit 0. |
ind, _rebuild_for_update) из mockup/lite.py в общий модуль mockup/claim_entry.py; lite.py — тонкий re-export. | major | — | open |
| TD-DOM-22.2 | Добавить Service.claim/update/find/describe/start в mockup/admission.py, делегирующие в claim_entry, с profile-dependent review gate (self в lite, independent в strict). | major | 22.1 | open  **closed** (2026-11-10): Service.claim strict submits candidate (RECORDED_CANDIDATE); find/describe work in both profiles; update/start remain lite-only. Verified: strict claim->review->admit->find=1. |
| TD-DOM-22.3 | Подключить dom_claim/dom_update/dom_find/dom_describe/dom_start к strict-профилю в server.py (TOOLS, SIGNATURE, dispatch, STRICT_TOOL_NAMES); обновить 	est_handshake_list_and_refusals и 	est_two_role_flow_over_stdio. | major | 22.1, 22.2 | open  **closed** (2026-11-10): 5 tools added to strict TOOLS; handshake test updated (17 tools); 7/7 mcp_stdio pass. |
| TD-DOM-22.4 | Per-type required-поля в JSON Schema dom_claim (TD-DOM-23): либо two-step schema, либо обогащение dom_describe списками required/optional по типу. | minor | 22.3 | open  **closed** (2026-11-10): REQUIRED_FIELDS table + oneOf in input_schema + per-type required check in strict_arguments + claim_type_examples enriched with required/optional. Tests 61 pass, 7 mcp pass. |
| TD-DOM-22.5 | Идемпотентность на уровне ввода клайма (TD-DOM-28): опциональный idempotency_key в dom_claim/dom_update, проброс в _package/_commit. | minor | 22.1, 22.2 | **closed** (2026-11-10): COMMON_FIELDS + _validated_claim_args принимают idempotency_key (str, optional); _write_claim/_commit и strict claim submit используют его как package idempotency key; dom_update потокнёт в build1/build2. Verified: lite replay same key+content -> ALREADY_RECORDED + same claim_id; lite same key+diff content -> IDEMPOTENCY_MISMATCH; strict replay -> same candidate_id; strict diff -> IDEMPOTENCY_MISMATCH; strict_arguments accepts idempotency_key on dom_claim/dom_update. Tests: tests/test_claim_entry_idempotency.py (6 pass). |
| TD-DOM-22.6 | Навигация по цепочке версий / diff (TD-DOM-29): dom_claim_versions(claim_id) или ersion_chain в dom_find/dom_query; diff в ответе dom_update. | minor | 22.1 | open |
| TD-DOM-22.7 | Независимый review в strict claim-entry (TD-DOM-27): Service.claim в strict отказывает при self-review (INDEPENDENCE_NOT_ENFORCED); проверка тестом. | major | 22.2, 22.3 | open  **closed** (2026-11-10): strict claim submit -> review (root-B) -> admit DEMO_ADMITTED; find=1. |
| TD-DOM-22.8 | Multi-branch атомарное внесение (TD-DOM-30): ranches: [...] в dom_claim. Высокий риск; отложить до OMH binding (TD-DOM-25/TD-DOM-08). | minor | 22.2, TD-DOM-08 | open (deferred) |
| TD-DOM-22.9 | Binding к OMH task/work (TD-DOM-25): 
equirement_refs → OMH task refs. Заблокировано TD-DOM-08. | major | TD-DOM-08 | open (blocked) |
| TD-DOM-22.10 | Тесты + документация: MCP handshake, E2E, SPEC.md tool list, STATUS.md. | minor | 22.3, 22.4–22.9 | open |


## Combat test 2026-11-10 (claim-entry block)

Адверсариальный прогон (15 сценариев) блока внесения клаймов в strict-профиле: все отказы сработали корректно (INDEPENDENCE_NOT_ENFORCED, SCOPE_DENIED, UNKNOWN_TYPE, INVALID_FIELD, EMPTY_TEXT, TEXT_TOO_LARGE, DIGEST_MISMATCH, PROFILE_STRICT). Найдено 1 замечание minor: requirement_refs не валидируются по составу (TD-DOM-32).

| ID | Долг | Severity | Источник | Статус |
|---|---|---|---|---|
| TD-DOM-32 | requirement_refs не валидируются по составу/длине/набору: произвольные строки (включая path-traversal) принимаются и хранятся. Потенциальная stored-injection при выводе в YAML/trace. | minor | combat test 2026-11-10 (A15) | open |

## Архитектурный аудит 2026-11-11 — новые долги и приоритеты

Источник: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md`; исходный аудит `docs/audit/2026-11-11_ARCHITECTURE_AUDIT.txt` (3 619 строк). Решения D1–D6 зафиксированы там же. Прежняя сводка (25 открытых) дополняется; актуальный порядок — ниже.

### Зафиксированные решения

- **D1.** DOM — проекция OMH: `plan_tasks`/`task_claims` — read-only кэш (`source='OMH'`, `synced_at`, `stale`); DOM не владеет статусами.
- **D2.** `version`/`logical_claim_id` — производные из replacement-цепочки; колонки не вводятся.
- **D3.** Базлайн — SQL-view над `events`; материализация только после benchmark.
- **D4.** `commit_ref` — опциональное поле `code`; нужен `OPTIONAL_FIELDS`; hash 40/64 hex.
- **D5.** Drift — явная миссия (`expected` + `constraints`); score = `(missing+changed)/|expected|`; `extra` отдельно; `|expected|=0` → `undefined`.
- **D6.** Два оркестратора: внешний (Hermes, NL→MCP) и внутренний (DOM, доменная оркестрация); LLM-фильтр — за портом, только кандидаты.

### Приоритет 0 — доказанные дефекты (закрывать первыми)

| ID | Долг | Severity | Проверка закрытия | Статус |
|---|---|---|---|---|
| TD-DOM-33 | Двойная `verify_chain` в `trace`/`resume` (`query=1`, `trace=2`, `resume=2`); лишняя O(N) на каждом чтении | major | счётчик вызовов: 1 на запрос; тест | **closed** (2026-11-11): `ADR-P0-01`; `Service.integrity` → `(stamp, chain)`, `_trace` переиспользует; `test_trace_and_resume_verify_chain_once` → trace/resume/query = 1. |
| TD-DOM-34 | `sync` держит read-tx вокруг внешнего I/O; при `journal_mode=DELETE` блокирует писателей до `busy_timeout` | major | slow port + параллельный writer; задержка < 2 с | **closed** (2026-11-11): `ADR-P0-02`; sync/export выносят внешний эффект из транзакции, наблюдение пишется отдельной write-tx после re-check; `test_sync_does_not_hold_a_read_transaction_across_external_io` → writer `DEMO_ADMITTED`, sync `SYNCED`. |
| TD-DOM-35 | Ручной реестр `TOOLS`/`SIGNATURE`/`dispatch` — routing drift; нет теста соответствия | major | drift-тест TOOL↔handler↔signature↔doc | **closed** (2026-11-11): `ADR-P0-03`; единый `HANDLERS`, `tests/test_tool_registry.py` (3 теста). |
| TD-DOM-36 | Нет инварианта «каждый claim имеет snapshot»; ARCH-01 trigger нереализуем в текущем flow | major | SQL-инвариант + helper; ADR | **closed** (2026-11-11): `ADR-P0-04`; `_record_claim` вставляет пару, `claim_snapshot_gaps` — read-only guard; 2 теста. DB-level trigger отложен (Q12). |

**Статус P0 (2026-11-11):** закрыт в `arch/p0-invariants`; ADR-P0-01…04; полный прогон **77 passed, 0 failed**; demo exit 0. Три ранее красных теста триажированы как устаревшие относительно текущих публичных контрактов, не ослаблены.

### Приоритет 1 — ядро (после P0)

| ID | Долг | Severity | Зависимости | Статус |
|---|---|---|---|---|
| TD-DOM-37 | Миграции: `_migrate_vN + ledger` + DOWN; v4 только под конкретную фичу | major | P0 | open (v4 deferred) |
| TD-DOM-38 | `version`/`logical_claim_id` не отдаются в DTO; вывод из `_lineage` (не колонки) | major | P0 | open |
| TD-DOM-39 | `commit_ref` отсутствует; добавление в `TYPE_FIELDS` сделает его обязательным и сломает старые code-клаймы | minor | — | open |
| TD-DOM-40 | Базлайн не представлен: нет `baseline_view` (`seq`, `prev_seq`, `chunk_hash=event_hash`) | major | TD-DOM-38 | open |
| TD-DOM-41 | Нет `dom_recall` (replay до branch-local seq); `pending_decisions`/`resolved_conflicts`/`related_branches` не определены | major | TD-DOM-40 | open |
| TD-DOM-22.6 | Нет навигации по версиям/diff (`dom_claim_versions`, `dom_diff`) | minor | TD-DOM-38 | open |

### Приоритет 2 — проекция плана

| ID | Долг | Severity | Зависимости | Статус |
|---|---|---|---|---|
| TD-DOM-42 | Нет проекции плана OMH: `plan_tasks`/`task_claims` (read-only, `source='OMH'`, `synced_at`, `stale`) | major | D1, P1 | open |
| TD-DOM-43 | Нет `dom_plan_tree`/`dom_task_claims`; root не должен быть хардкодом `П1` | major | TD-DOM-42 | open |
| TD-DOM-54 | Пункты плана идентифицируются по `path`, а не по стабильному `plan_task_id`; нет версий; повторный sync переобновляет записи и ломает `task_claims` | major | D1.1, TD-DOM-42 | open |
| TD-DOM-44 | Материализованное состояние планирования (TD-PLAN-01) — преждевременно; только после benchmark, как кэш с rebuild | minor | TD-DOM-42 | deferred |

### Приоритет 3 — diff/drift/fork

| ID | Долг | Severity | Зависимости | Статус |
|---|---|---|---|---|
| TD-DOM-45 | Drift: нет явной миссии/constraints; формула аудита делит на ноль и штрафует `extra` | major | TD-DOM-42/43 | open |
| TD-DOM-46 | `fork_branch` не реализован; нужна атомарная транзакция, `carry ∩ rewrite = ∅`, `branch_fork_claims` | major | TD-DOM-40 | open |
| TD-DOM-55 | Split/merge плана не обрабатывается: ссылки `task_claims` становятся orphaned без явного relink | major | TD-DOM-54 | open |

### Приоритет 4 — оркестратор

| ID | Долг | Severity | Зависимости | Статус |
|---|---|---|---|---|
| TD-DOM-47 | Нет контракта двух оркестраторов (Hermes outer / DOM inner); риск «второго планировщика» | major | D1, D6 | open |
| TD-DOM-48 | Нет детерминированного дедупа/полноты на внутреннем слое (`DUPLICATE_OF`, `INCOMPLETE` + `missing_refs`) | major | TD-DOM-47 | open |
| TD-DOM-49 | Сессии не персистентны/не изолированы (in-memory sample) | major | TD-DOM-47 | open |
| TD-DOM-50 | `Service` — God Object (TD-STRUCT-01); рефакторинг фасадами, не big bang | major | P1 | open |

### Приоритет 5 — live/fault tolerance

| ID | Долг | Severity | Зависимости | Статус |
|---|---|---|---|---|
| TD-DOM-51 | Нет `IOmhDeliveryPort` (Protocol) и инъекции; `admission.sync` знает о симуляции (TD-INT-01) | major | P0/P1 | open |
| TD-DOM-52 | Нет Merkle/checkpoint для инкрементальной проверки; `branch_heads.last_verified_seq` несовместим с глобальным `events.seq` | major | P0, TD-DOM-01 | open |
| TD-DOM-53 | Нет матрицы retryable/circuit/fallback; `update` без reconciler для `UPDATE_INCOMPLETE` | major | TD-DOM-51 | open |

### Сводка и порядок

- **P0:** TD-DOM-33, 34, 35, 36.
- **P1:** TD-DOM-37, 38, 39, 40, 41, 22.6.
- **P2:** TD-DOM-42, 43, 54; TD-DOM-44 deferred.
- **P3:** TD-DOM-45, 46, 55.
- **P4:** TD-DOM-47, 48, 49, 50.
- **P5:** TD-DOM-51, 52, 53.

Итого новых: TD-DOM-33…55 (23 пункта). Из них P0 — 4, P1 — 5 (+22.6), P2 — 4 (3 + deferred), P3 — 3, P4 — 4, P5 — 3.

### Связь с существующими долгами

- TD-DOM-01 (внешний checkpoint) → TD-DOM-52.
- TD-DOM-03 (Git merge) → TD-DOM-46 + TD-DOM-08.
- TD-DOM-08 (live OMH) → TD-DOM-51.
- TD-DOM-14 (scope trace/resume) → остаётся отдельным; не дублируется.
- TD-DOM-15 (STALE_CHECK) → остаётся; не смешивать с drift.
- TD-DOM-16 (payload KeyError) → частично P0.4 инвариант; отдельный фикс.
- TD-DOM-22.6 → TD-DOM-38/41 (diff/versions).
- TD-DOM-29 → TD-DOM-38.
- TD-DOM-32 (requirement_refs) → остаётся; не дублируется.
