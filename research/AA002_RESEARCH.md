# AA002 — исследование и минимальный контракт DOM ↔ OMH

**Статус: PARTIAL.** Исследовательский handoff подготовлен, не реализация и не независимая приёмка. Ветка работы **AA**, версия **AA002-research-v1**; `R-C01`…`R-C12` — отдельные ID исследовательских клаймов. В JSON у каждого результата явно указаны `origin_branch` и `origin_version`. Физическая Git-ветка при чтении: `feature/b1-t2-core-config`, HEAD `a36126c8879db64f630d293193796ea08b1d305e`; checkout не выполнялся.

**Итог:** ANSWERED — Q03/Q04/Q05/Q06/Q07/Q09/Q10/Q12; OPEN — Q01/Q02/Q08; NOT_TESTED — Q11. ANSWERED означает достаточный исследовательский ответ/выбранный контракт, **не прохождение будущих функциональных тестов**. Первичные локаторы находятся в `AA002_SOURCE_LEDGER.json`; ссылки S/P/X ниже — его ID. Пользовательские требования в `../REQUIREMENTS.md` имеют приоритет над предложениями этого отчёта.

## 1. Выбранный минимум и границы

Одна authoritative SQLite-база на существующую внешнюю работу OMH; AA и AB — логические веточные представления в ней. DOM не создаёт задачи, канбан, loop или собственный реестр глобальных работ. В макете owner adapter даёт **синтетическую ссылку на уже существующую работу/задачу**, явно `simulation=true`, две сессии открывают ту же привязку. Иная работа не проходит scope. AA001 — код задачи AA+001, а не ID клайма и не Git ref. Основание: REQUIREMENTS:19–46,69–88 [S01–S03].

Реальными в будущей реализации должны быть SQLite commit/rollback/OCC/idempotency/reopen, byte preservation, строгий валидатор, scoped projections, YAML export и **отдельный stdio MCP subprocess handshake**. Mock допустим только для внешних OMH/Git ports и host identity test adapter. Доступ к настоящим пользовательским данным, изменение live-плагинов и включение сервера в Hermes не нужны.

Admission: `REJECTED` → `RECORDED_CANDIDATE` → отдельная review receipt → `DEMO_ADMITTED` в simulation. Защищённый production путь без доказанного host capability issuer возвращает `INDEPENDENCE_NOT_ENFORCED`, а не принимает demo receipt за независимую приёмку. Формальный PASS и успешный вызов инструмента не означают истинность утверждения [S03,S06–S08].

### Отвергнутые альтернативы

- Session/todo index/checkpoint как global-work ID: не доказывают долговечный owner ID.
- Второй планировщик/реестр задач, полный workflow Agora или запись статусов через baseline_tracker: нарушают ownership и недостаточны для admission.
- Копия DB на Git-ветку и merge SQLite-файлов: противоречат одной базе, не решают семантический merge.
- K0 JSONL как authoritative admission store: типизированный журнал полезен, но нет общей SQLite-транзакции claims/receipt/outbox.
- Полный JCS через установку новой зависимости: установка запрещена; для минимального макета достаточен явно ограниченный версионированный формат **не JCS**.
- Хеш вместо transaction/OCC, caller-supplied reviewer_id вместо identity, SDK coercion вместо полной validation: недостаточно.

## 2. Ответы Q01–Q12

### R-C01 / Q01 — OPEN

**Исходный вопрос:** Какой существующий OMH ID связывает одну глобальную работу и задачу через новую сессию, перестановку todo и checkpoint, без второго реестра?

Найден более подходящий существующий порт, чем session todo: `tools/loop_tool.py:132–135` объявляет `linked_goal_id` как existing goal ledger id; `:78–95` — `loop_id/expected_revision/mutation_id`. `loop_bridge.py:93–118` прямо говорит и реализует границу: loop переживает сессию, любая сессия/CLI может продолжить его; session gate не ownership и не attribution. Handler/bridge ведёт к `omh.workflows.loop_operations.LoopOperationRequest` и `loop_operation_envelope` [S04–S05].

**Не подменять:** `WorkflowRecord` содержит workflow/active/session_ref, fingerprint привязан к сессии [S09]; checkpoint случайный и хранит model declaration [S08]. Ни один из них не считать глобальным task ID.

**Предложение mapping:** `{authority:'omh', authority_namespace:host_bound_store_ref, goal_id:existing_linked_goal_id, loop_id:optional_existing_loop, task_ref:owner_assigned_existing_ref}` → ровно одна DOM binding/DB. Namespace нужен для различения одинаковых ID в разных owner stores, не произвольного model path.

**Не закрыто evidence:** первичный core `goals/ledger` с create/read/lifetime goal ID и существующая долговечная task_ref не найдены в bounded разрешённом поиске; `find_spec('omh')=None` в harness Python и текущем Hermes interpreter [P04]. Это **не доказательство отсутствия пакета у всех процессов**. Plugin metadata сообщает version 3.0.0 и upstream SHA `021e5c63d976b4e0faf9cfc7d608701d98fe1722`, но не даёт core source root [S24]. Файлы `loop_operations.py/goal_ledger.py` и `goals/ledger.py` в проверенных source/cache/harness locations не найдены; личные записи не исследовались.

**Следующее действие:** родитель локализует/предоставляет разрешённый OMH core source root; прочитать создание и lookup goal/task, затем отдельным разрешением exact read-back. До этого live binding → `OMH_BINDING_UNVERIFIED`. Synthetic макет не блокируется; linked_goal_id schema сам по себе ещё не верифицированный глобальный контракт.

### R-C02 / Q02 — OPEN

**Исходный вопрос:** Как host назначает неподделываемую identity/capability автора и отдельного принимающего для конкретного digest?

Реальное локальное API: `handler(args, **kwargs)`; `host_session_id` читает только `kwargs.session_id`, не args [S06]. `team_tool.py:81–102` блокирует board worker и known delegated helper, `:103–106` создаёт host-session-bound TeamContext [S07]. Однако это team enforcement, не issuer reviewer capabilities нового DOM. Loop разрешает любую host session, а session_binding не является долговечным attribution record [S05].

**Достаточный demo контракт:** host adapter вне model args назначает `{principal_id,root_principal_id,capabilities,work_scope,branch_scope,trust_mode:'simulation'}`. Авторские корневые identity и reviewer root должны отличаться; `review` capability принадлежит адаптеру, не строке role. Receipt связывается с exact candidate digest, dependency snapshot digest, expected branch revision, policy digest, verdict/findings и reviewer capability proof. Caller `reviewer_id/role/author` в пакете не доверять; неизвестные privileged поля отклонять.

Self-admit, helper с тем же root, forged reviewer, unknown host и изменение digest после review — отказы. Только demo principal B принимает demo principal A, маркировка `simulated=true/DEMO_ADMITTED`. Настоящий host issuer, полномочия разных клиентов и host-E2E отсутствуют; поэтому вопрос production identity остаётся OPEN. Требуется отдельный host capability contract, не просто два MCP-соединения.

### R-C03 / Q03 — ANSWERED, статически + одна безопасная проба

**Исходный вопрос:** Что из K0 schemas/journal, K3 render_contract и role validators существует в актуальных разрешённых исходниках и реально связано с входом Hermes?

| Компонент | Найденное evidence | Подключено к текущей DOM/Hermes | Реально выполнено |
|---|---|---|---|
| K0 Journal/schemas | `mp/k0/journal@752ea701…:harness_context/journal.py:93–122`; schema tree [S10] | Не доказано; в текущем HEAD нет harness_context | read-only git show/ls-tree, не запуск |
| K0 ports/schema | `mp/int@8a9f8f95…:harness_context/ports.py:19–27,87–108` [S11] | Есть typed plan/contract/... joint; provider отдельно | Статическое чтение |
| K3 M5 render_contract | `mp/k3/m5-contracts@aafa0af…` не имеет `harness_context/contracts`/renderer в проверенном tree; log по этому пути пуст [P04] | Не доказано; ветка пока базовая | read-only tree/log, не утверждение обо всех файлах/ветках мира |
| K3 M6 build_packet | `mp/k3/m6-inject:harness_context/packet/__init__.py`, symbols build_packet/build [S12] | Сборка вызывает contract port, не реализует renderer | Статическое чтение полного файла |
| Role validator | `scripts/code-factory/contract_validator.py:248–280` [S13] | Семь существующих ролей; analyst/researcher в реестре нет | Чистый вызов `validate('researcher',{})` → `['unknown agent_type: researcher']` [P02] |

Мастер-план K0/K3/K4 и §6–8, документ dynamic routing прочитаны; PROPOSED нельзя превращать в wired/runtime PASS [S16–S17]. Исходная F07 ограничена верно: K0 существует **в других refs**, но не в текущем source root. Не переносить код и не менять branch state. Макет не должен ждать неперенесённый K3: использовать простой строгий предметный validator, не маскировать роль researcher как worker.

### R-C04 / Q04 — ANSWERED как выбранная спецификация

**Исходный вопрос:** Как обеспечить стабильный claim ID и неизменяемые origin_branch/origin_version, отличая AA001, DOM branch и Git ref при применимости и архивировании?

Server-minted UUID4 `claim_id`, уникальный в work DB, не зависит от позиции, текста, task code или branch/ref. Каждая immutable запись непосредственно содержит `origin_branch` и `origin_version` — version/snapshot артефакта, включая dirty snapshot, а не обязательное притворное Git commit [S01–S03]. Идемпотентная квитанция возвращает прежние IDs; collision в уникальном ключе откатывает операцию и выдаёт новый ID до ответа. Перестановка представления не перенумеровывает claims. Повторное применение AA→AB добавляет applicability link; архив AA не архивирует AB; исправление тела — новый UUID + replacement relation.

Новые коды резервирует **владелец OMH**, а не DOM registry: две uppercase ASCII буквы и дочерний 001..999; existing codes не переиспользовать. В макете AA/AB предоставлены fixture owner. Исчерпание → `CODE_SPACE_EXHAUSTED` и решение владельца, без автоматического изменения формата/переименования AA001. Это предложение распределения, не выполненная операция owner. Fixtures collision/replay/reorder/archive/merge ещё NOT_RUN.

### R-C05 / Q05 — ANSWERED, runtime storage NOT_TESTED

**Исходный вопрос:** Каково атомарное множество изменений допуска и поведение при двух writers, stale review, потерянном ответе и сбое между DB commit/outbox delivery/export?

Выбор и fault matrix — §3 и §7 ниже, машинно также `storage_contract/acceptance_matrix` JSON. SQLite primary docs подтверждают один writer и `BEGIN IMMEDIATE/SQLITE_BUSY`, FK надо явно включать на каждом connection [S19–S20]; библиотека реально доступна [P01]. Это **не выполненная транзакционная проба**. baseline_tracker read/replace/status нельзя использовать как admission или master-ready [S14].

Критическая деталь: idempotency lookup/mismatch проверяется **до OCC** в короткой writer transaction. Иначе lost-response replay получил бы stale revision вместо прежней успешной receipt. Review выполняется вне transaction; его bindings проверяются вновь внутри. Все facts/events/head/receipt/idempotency/outbox intents admission атомарны. Внешние OMH/Git и YAML delivery — после commit, с pending/ambiguous и read-back, не распределённая exactly-once transaction.

### R-C06 / Q06 — ANSWERED; raw hash probe PASS, canonical/DB NOT_TESTED

**Исходный вопрос:** Как хранить точные исходные байты текста/кода/цитаты отдельно от search-проекции и определить версионированный digest без потери Unicode, переводов строк и научных чисел?

`body_raw BLOB`, strict canonical base64 на wire, `body_sha256=SHA256(raw)` по `body-raw/v1`; type/media/encoding/base64 фиксируются в envelope digest. Source bytes/quote и agent interpretation отдельны; search — disposable projection. Никаких trim/NFC/NFD/CRLF/URL нормализаций исходника. OCR/extractor provenance сохраняется, hash OCR не подтверждает точность PDF-цитаты [S02–S03,S15].

Выбран **dom-c14n/v1, не RFC8785 JCS**: validated restricted JSON → `json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')` на Python3.11. Допустимы ASCII schema keys, точные Unicode string values без lone surrogates, null/bool, metadata integers 0..9007199254740991, lists/objects. Reject floats/NaN/Infinity, duplicate object keys, unknown fields. Научные числа/единицы/uncertainty — exact strings, не float. RFC8785 действительно требует IEEE754 и рекомендует строки для большей точности; Unicode не нормализует, ключи сортирует по UTF-16, поэтому не называть Python sort_keys полной JCS [S21].

**Порядок:** в validated canonical object `items` сортировать по уникальному `local_id`, applicability set — по branch, dependency vector — по stable dependency ref; это только структурный порядок, не изменение raw bytes. Семантически упорядоченные массивы (например, шаги вывода) сохраняют порядок. Таким образом reorder batch items с теми же local IDs даёт тот же intent digest/IDs; замена содержимого под одним local_id — mismatch. Пакетная schema обязана явно отличать set-подобные массивы от ordered.

Intent digest связывает owner binding/task, scope/branch, stable author/root, operation, schema/policy/version, expected branch rev, exact dependency versions/digests, local IDs, bodies/sources/locators и reason. Не включает session/tool_call/server time/server-minted IDs/idempotency key. Key всё равно scope-limited и хранит digest. Review — отдельная immutable receipt на candidate digest/snapshot/revision/policy; не циклическая часть исходного candidate.

Реальная безопасная проба P03 вычислила SHA256 шести **literal byte vectors**. Их hex/hashes полностью в JSON `golden_vectors`; LF/CRLF, trailing whitespace, NFC/NFD дают разные hashes. `1.2300e-40 mol/L` хранится без потери лексемы. Canonical-envelope expected vectors, DB roundtrip и cross-session replay ещё должен выполнить воркер; raw hashes их не заменяют.

### R-C07 / Q07 — ANSWERED как точный входной контракт

**Исходный вопрос:** Какие обязательные поля различают цитату, авторское решение, формулу, код, данные и концепт и как вернуть все нарушения безопасно?

Общие поля: external work/task ref, branch, expected branch revision, schema version, policy digest, operation, idempotency key, unique item local_id, type, body_b64, media/encoding, reason, applicability. Server назначает principal/root/time/claim_id; per-claim origin_branch берётся из проверенного write scope, origin_version — из валидированного artifact/version snapshot.

| Тип | Дополнительные обязательные данные | Минимальный отрицательный fixture |
|---|---|---|
| quote | immutable source ref, snapshot digest, page/span/line/byte locator, exact fragment bytes, extraction provenance при OCR | missing locator / snapshot / несовпадающий source fragment |
| decision | attribution, rationale, explicit assumptions/alternatives (пустые списки допустимы), applicability | missing rationale/assumptions declaration; **нет DOI — не ошибка** |
| formula | exact expression, notation, assumptions, units или explicit dimensionless, derivation refs либо author derivation | missing assumption declaration/unit/symbol definition |
| code | repository ref, relative path, language, snapshot digest, range; dirty artifact manifest при dirty | missing snapshot/path/range |
| data | artifact ref+digest, method, column schema, numeric units или explicit dimensionless, provenance | missing method/unit/digest |
| concept | definition, scope, assumptions, attribution/origin, external derivation refs при наличии | missing definition/scope |
| text | factual/interpretation; factual evidence refs+locators; собственная интерпретация с attribution/assumptions | unsupported factual text / смешанная source quote и interpretation |

Сначала authorization envelope/scope без раскрытия чужих объектов; затем собрать **все разрешённые** ошибки типов/полей. Ответ: `REJECTED, accepted_count=0, rejected_local_ids, errors[{local_id,path,code,required,fix}]`; без raw values, секретов, чужих object IDs/counters. Ни candidate/admitted rows, ни baseline rev/export при invalid batch не меняются; безопасные rejection metadata можно записать отдельно. Конкретные error codes/type matrix — JSON. Исходники FastMCP:295–324 отключают low-level input validation ради ad hoc conversion [S23]; поэтому domain strict validator обязателен, включая отказ bool-as-int/строковых чисел там, где schema требует integer. Наличие SDK не гарантирует агрегирование предметных ошибок [S02–S03,S15].

### R-C08 / Q08 — OPEN для полного live контракта

**Исходный вопрос:** Какая фактическая OMH операция принимает evidence/result и как подтверждается доставка, не закрывая задачу автоматически?

Найден точный surface: `omh_loop(action='queue_observe', loop_id, queue_id, expected_revision, mutation_id, evidence_refs, summary)`; `loop_tool.py:183–199,222–234` → `loop_bridge.py:275–285` → core operation envelope [S04–S05]. Это evidence **существующего prepared queue item**, не доказанный универсальный task result port. Не создавать loop/queue ради удобства DOM и не подменять queue_id любым task ID. `feedback(observed_artifacts)` слишком общий для exact-target acknowledgement; completion dossier — model declaration [S08].

Будущий owner port: `attach_evidence(existing_target,tx_id,revision,snapshot_digest,evidence_refs,intent_key)` + `read_target(existing_target)`. Target missing/unavailable → pending. Ack только после чтения **того же** target с matching tx_id/digest/ref, не по tool return `ok`. В fixture OMH никогда не вызывает close/complete. Core queue_observe/status fields, permissions и live delivery/read-back ещё не подтверждены; OPEN не закрыт названием handler. Следующий шаг — разрешённые core исходники, затем отдельный live write gate. Dedupe/read-back pattern Agora полезен, но его статусы/workflow не заимствовать [S18].

### R-C09 / Q09 — ANSWERED: API-only scope, OS isolation NOT_ENFORCED

**Исходный вопрос:** Какие scope гарантии достижимы в текущем локальном runtime и как ограничить обход MCP через terminal/read_file/YAML/БД?

В доступном наборе есть terminal/read_file с прямыми путями. Это уже достаточная причина **не обещать** OS isolation через MCP ACL; реальные пользовательские файлы для доказательства обхода читать не требуется. В этом проходе `runtime_isolation=NOT_ENFORCED`, а synthetic API scope tests демонстрируют только поддерживаемый API [S03].

Production: отдельная OS identity сервиса владеет DB/полным YAML/ключами и capability issuer; executor не имеет прямого доступа и не может mint review capability. Контекст work/branch/capability назначает host. Фильтры до graph/search/history/export/count/outbox/error, не после выдачи модели. Foreign/missing ID — единый безопасный SCOPE_DENIED, не oracle существования. Restricted master context даёт readiness UNKNOWN.

Secret до admission → safe rejection без payload в логах. Уже admitted secret → privileged quarantine marker и прекращение serving/export/cache → notify/rotate → отдельно разрешённая retention/purge remediation с аудитом. Append-only не обязывает распространять секрет, но не разрешает тихо переписать цитату. Admin файла/сервера не считается побеждённым; hash chain без внешнего checkpoint не обнаруживает надёжно полный rewrite/rollback [S03,S25].

### R-C10 / Q10 — ANSWERED как pure projection contract

**Исходный вопрос:** Как вычисляется остаток глобальных обязательств и смысловая сходимость master при archived claims, branch exclusion, stale evidence и pending outbox?

На точной admitted revision вход: owner requirement refs/criteria/policy + required branches. Для каждого requirement/branch вычислить active applicable admitted claims → current checks на exact claim/dependency/policy snapshot. Результат строки: `requirement_ref,branch,claim_refs,check_refs,reasons[{MISSING_COVERAGE,STALE_CHECK,ARCHIVED_SUPPORT,CONFLICT,BRANCH_NOT_CONVERGED,EXCLUSION_NOT_AUTHORIZED,SYNC_PENDING}]`. Блокировки можно иметь одновременно, не прятать одну другой.

Архивный или неприменимый claim не покрывает active criterion; accepted replacement с current check может покрыть. AA archive не убирает применимость AB. Exclusion только отдельное admitted owner-authorized decision с rationale/revision, не исчезновение обязательства из истории. Demo checks считаются только в simulation projection и не превращаются в production independent evidence.

`master_ready` требует: все required criteria покрыты current checks; required branches семантически сведены либо authorized excluded; нет unresolved обязательных conflicts; required OMH/export intents ack. Вход не содержит полного authorized master scope → UNKNOWN, не true. Git textual merge и локальные task done не являются свидетельствами покрытия. Выход DOM максимум `ready_for_owner_review`; закрытие только OMH [S01–S03,S08,S14–S15]. Матрица контрпримеров T15–T18 ниже обязательна; вычислитель ещё не написан.

### R-C11 / Q11 — NOT_TESTED transport, API probe PASS

**Исходный вопрос:** Какой минимальный настоящий MCP handshake докажет обнаружение tools, validation и scoped вызов DOM, не выдавая in-process mock за transport?

Установленный SDK реально импортирован: mcp **1.30.0**, latest protocol **2025-11-25**. Инспектированы `ClientSession(read,write,...)`, `stdio_client(StdioServerParameters,...)`, `initialize/list_tools/call_tool`, `FastMCP.run(transport='stdio')` и tool decorator [P01]. `client/session.py:160–209` отправляет initialize, проверяет supported protocol, отправляет `notifications/initialized` [S22]; `FastMCP.run` синхронный, внутри запускает anyio [S23].

Будущий реальный test: `async with stdio_client(params) as (read,write)` → `async with ClientSession(read,write)` → `await initialize()` → `await list_tools()` → scoped `call_tool` на fixture binding, invalid envelope и forbidden branch. Server запускается отдельным subprocess exact harness Python; explicit minimal environment/cwd, только synthetic paths, stdout только JSONRPC, diagnostics stderr. Log хранит actual negotiated protocol/serverInfo/tools capability, returned tool inputSchema, request/response IDs и ответы/отказы. Если `_meta` нужен correlation — он не является identity capability.

Серверы и прототип в AA002 запрещены: **initialize/list/call не выполнялись**. MCP lifecycle URL дал timeout, повтор не делался [X01]. SDK tag README получен, но нужных client snippets не содержал [X02]; API evidence взят из локального первичного SDK, не из догадки. In-process unit test не даёт ярлык MCP-connected; включение в Hermes — отдельный gate и вне макета.

### R-C12 / Q12 — ANSWERED, real Git mutations NOT_IMPLEMENTED

**Исходный вопрос:** Какой минимальный Git port безопасно описывает dirty snapshot, проверку merge и намерения create/merge без реальных изменений текущего репозитория?

Fixture `describe_snapshot(repo_ref,dom_branch)` возвращает repository_id/worktree_ref/git_ref/head_commit/dirty/artifact_manifest/artifact_digest. Manifest — sorted relative path + byte digest + mode/deleted; raw snapshot с allowlist без секретов, path traversal запрещён. Dirty content не приписывается HEAD; artifact digest по отдельному manifest contract.

`plan_create_branch(base_snapshot,proposed_ref,intent_id)` и `check_merge(source_snapshot,target_snapshot)` возвращают `simulation=true`, точные input snapshots/textual feasibility и отдельное semantic UNKNOWN/CONFLICT. `execute_create/commit/merge` → **NOT_IMPLEMENTED**, без subprocess side effects. Semantic merge лишь добавляет applicability/conflict-resolution links, origin не меняется. Реальные действия только в отдельно разрешённом disposable repo [S01,S03]. В AA002 выполнены только read-only Git branch/log/show/ls-tree/rev-parse [P04].

## 3. Нормативный storage/admission контракт для воркера

Это **предложение для реализации**, не текущая БД. Полные поля и constraints — JSON `storage_contract`.

- Путь DB выбирает server из owner binding, не model args. `journal_mode=DELETE`, `synchronous=FULL`, `foreign_keys=ON` на каждом connection, bounded `busy_timeout=2000ms`; PRAGMA results проверить. WAL не нужен минимальному локальному стенду; shared network DB не предусматривается.
- Tables: singleton binding; branch_heads (производный mutable CAS); immutable candidates/claims/reviews/events/transactions/idempotency/outbox intents; append delivery_events. Sources/links/comments/properties/applicability/archive/replacement представлены immutable типизированными events/records с FK; при материализации отдельными таблицами инварианты те же.
- Claims: `claim_id PK`, body BLOB/hash/type/media/encoding, обязательные `origin_branch/origin_version`, candidate/tx/source provenance. **Каждый** claim сохраняет эти origin поля при любом экспорте/переносе/слиянии.
- Все добавления link/comment/property содержат собственный ID, claim ref, host actor/root, server UTC time, context/version/revision, reason; исправление — supersedes ref. Исторические строки не менять. Триггеры запрещают UPDATE/DELETE immutable tables через ordinary connection; это не защита от DB-file admin.
- Unique: `(work_ref,operation,idempotency_key)` с intent_digest и сохранённым canonical result; `(branch,admitted_revision)`; global sequence PK; `(tx_id,outbox_kind,target_ref)`; event/review/claim IDs. Scope dedupe не session/tool_call.

**Admission transaction:** `BEGIN IMMEDIATE` → scoped idempotency lookup; same digest возвращает сохранённый результат, other digest конфликт → revalidate trusted capability/root separation/policy/candidate/snapshot/exact dependency versions/expected branch revision → insert immutable facts and append events/links → CAS branch head, allocate monotone global seq → transaction receipt/idempotency result/outbox OMH+export intents → `COMMIT`. Исключение до commit → явный `ROLLBACK`. После commit прочитать по tx_id actual revision/digest/receipt, только затем отвечать. Медленная semantic review/network/Git/export не внутри writer lock.

Candidate record — отдельная короткая transaction с собственным business idempotency; не increments admitted rev и не даёт coverage. Amendment/applicability/exclusion/archive — не привилегированный обход review: те же scoped validation/admission gates.

**Concurrency:** две AA записи rev0 → одна AA rev1, другая explicit conflict после busy handling. Retry из-за BUSY bounded и заново проверяет prerequisites. Изменение AB не должно автоматически stale AA, если exact dependency vector не менялся; общая последовательность событий одна. Обновление общей значимой зависимости инвалидирует receipt даже при неизменной AA head.

**После commit:** outbox intents durable. Deliver OMH evidence/read exact target, затем append ack. Failure → pending; side effect before ack → ambiguous/reconcile, не обещание external exactly-once. YAML экспорт — deterministic revision/scope snapshot, temporary write+replace, затем read-back digest/revision и ack. Ошибка экспорта не отменяет successful DB commit. Resume показывает committed tx, pending/ambiguous delivery и export, не только последний текст агента.

## 4. Рекомендуемый API и файлы (не созданы)

MCP tools: `dom_init`, `dom_resume`, `dom_submit`, `dom_review`, `dom_admit`, `dom_append`, `dom_query`, `dom_trace`, `dom_export`, `dom_sync_status`. Host context/capability не передаётся model аргументом. Read/query/trace/export всегда scope/revision-bound. Init без contract/binding/scope не создаёт пользовательскую БД/экспорт; repeat init несовместимого binding → conflict, не overwrite. Query admitted по умолчанию не видит candidate; candidate reviewer read отдельный authorized scope. Export возвращает разрешённый server handle/digest, не arbitrary model path.

`dom_review/admit` могут работать только в явно заданном **simulation fixture mode**; production без host issuer fail-closed. `dom_append` не позволяет body mutation и не обходит admission для содержательных поправок. Sync tool показывает/обрабатывает только разрешённые pending intents, не закрывает задачи.

Предлагаемая раскладка:

- `mockup/dom_contract.py` — strict schema/type/error aggregation + frozen digest contract;
- `mockup/storage.py` — migrations/constraints/triggers/OCC/idempotency/transactions;
- `mockup/admission.py` — candidate/review/bindings/demo gates;
- `mockup/projections.py` — branch snapshot/trace/residual/YAML;
- `mockup/ports.py` — injected IdentityPort/OMHPort/GitPort + explicit simulated result types;
- `mockup/server.py` — thin SDK stdio tools, no live Hermes integration;
- `mockup/fixtures/*.json` — synthetic owner contracts/types/fault scenarios;
- `tests/test_dom_contract.py`, `test_storage_faults.py`, `test_bytes.py`, `test_scope_trace.py`, `test_mcp_stdio.py`, `mockup/README.md`.

Ни один из этих файлов не создан AA002; единственные записи — три research outputs.

## 5. Что действительно выполнено

| Проверка | Наблюдение | Граница вывода |
|---|---|---|
| Harness interpreter/import/version | Python 3.11.15; yaml/mcp/pytest find_spec True; PyYAML 6.0.3, mcp 1.30.0, pytest 9.1.1, sqlite library 3.53.1 | Доступность зависимостей, не работа storage/server |
| SDK API signatures, StdioServerParameters construction | ClientSession/stdio_client/FastMCP API прочитаны; params command/args/cwd приняты Pydantic | Не открывался subprocess, transport handshake NOT_TESTED |
| Role validator pure call | unknown researcher → `['unknown agent_type: researcher']` | Никакого dispatcher/handler side effect |
| Literal byte hashes | Шесть raw vectors рассчитаны hashlib, outputs в JSON | Не канонический envelope/product DB test |
| Read-only source/git inspection | K0 в другой ветке найден; M5 renderer в проверенном ref не найден; M6 packet найден | Не merge/checkout/import веточного runtime |
| Official source reads | SQLite transaction/FK, RFC8785, Hermes llms index HTTP200 | Первоисточники, не доказательство live DOM guarantee |

`web_extract` не смог извлекать страницы: search-only backend. Разрешённый альтернативный urllib fetch получил SQLite/RFC/Hermes; MCP lifecycle timeout один раз, не повторялся. SDK tagged README HTTP200, искомые client fragments NOT_FOUND; он не использован как мнимое доказательство. Не устанавливались пакеты и не вызывались OMH handlers.

## 6. Blockers vs deferred production

**Для разработки synthetic макета внешнего blocker нет.** Минимальный контракт выбран; source gaps не повод остановить весь макет.

**Для приёмки исполняемого макета блокируют:** ещё не существующая реализация и реальные T01–T20 DB/type/digest/trace/MCP tests; exact canonical-envelope vectors; независимый review результата. Research handoff их не заменяет.

**Для production/live блокируют отдельно:**
1. Q01: core goals/ledger create/read/lifetime и подтверждённая owner task mapping. Найден linked_goal_id/loop surface, но полного source proof нет.
2. Q02: trusted capability issuer/reviewer separation с реальным host-E2E, не строки role.
3. Q08: полный core evidence operation/permissions/target read-back, отдельное разрешение write.
4. Q09: OS/file/tool sandbox; сейчас NOT_ENFORCED.
5. Q12: отдельное разрешение Git create/commit/merge и disposable repo.
6. External checkpoint/signing/rollback resistance и privileged secret remediation; вне минимальной демонстрации.

Пользователь решает разрешения live operations и модель угроз/OS identity, **не имена существующих handlers**. Q01/Q08 требуют source lookup, не перекладываются на него как архитектурное голосование.

## 7. Воспроизводимая приёмочная матрица будущего воркера

Все T ниже **NOT_RUN**, кроме частичной raw hash пробы T10. Полные fixtures/oracles и question IDs — JSON `acceptance_matrix`. Каждому прогону сохранить command, exit code, synthetic paths, before/after revisions, tx IDs и read-back SQL/JSON evidence без секретов. Нельзя подменять DB tests memory fake. Условные команды ниже — для будущих файлов, не сообщение об исполнении.

| IDs | Input/failpoint | Обязательный oracle |
|---|---|---|
| T01–T02 | init incomplete; W1 S1/S2; W2; self/helper/forged/unknown identity | no invalid DB; one resumed binding; scoped refusal; demo ≠ independent production |
| T03–T04 | два **процесса**, barrier на AA rev0; independent AB; shared dependency moves | одна AA commit; второй conflict, нет потерь/partial rows; unrelated AB допустим; shared stale rejected |
| T05 | после review изменить digest/policy/AA rev/dependency отдельно | stale/digest refusal, admitted rev/rows прежние |
| T06 | kill worker after facts before receipt; непосредственно before COMMIT; reopen actual DB | admission facts/events/head/receipt/idempotency/outbox целиком rollback; ранее записанный candidate может остаться |
| T07 | kill after COMMIT before response, restart new session; same key/digest; altered digest | одна tx, прежние receipt/IDs; mismatch отказ; dedupe до OCC |
| T08 | OMH unavailable; send succeeded before local ack; restart | admission есть, pending/ambiguous видны; exact target reconciliation, нет новой DOM tx/автозакрытия |
| T09 | export unavailable, then retry; crash after rename before ack | DB committed; deterministic export/read-back и ack, не ложный rollback |
| T10–T11 | raw LF/CRLF/NFC/NFD/space/decimal + supplementary Unicode; float/duplicate keys/lone surrogate; UUID collision/reorder/replay | exact bytes/digests, canonical item-key order, invalid input reject; IDs/origin неизменны, AA archive не AB |
| T12 | все 7 типов valid и respective missing fields; combined invalid batch | valid→candidate; все безопасные errors; accepted_count0/no new rows; decision без DOI valid |
| T13 | API/ordinary SQL UPDATE/DELETE immutable body/link/comment/property; append correction | mutation denied, raw/history intact; append полный provenance |
| T14 | foreign scope search/graph/history/trace/YAML/error/count/outbox | filter до traversal, нет foreign existence oracle; только API guarantee |
| T15 | R1 current covered, R2 missing при всех local done | residual R2=MISSING_COVERAGE, master false, no close |
| T16 | sole supporting claim archive AA, still AB; stale check; accepted replacement | AA теряет coverage, AB не молча; stale не считается, current replacement восстанавливает |
| T17 | textual merge true + semantic contradiction; unapproved/approved exclusion | conflict blocks; exclusion только owner-authorized admitted decision |
| T18 | всё covered, но required sync/export pending → matching ack; limited master scope | pending blocks; ack→ready_for_owner_review; limited→UNKNOWN; no close |
| T19 | **real subprocess** initialize/list/call + invalid/scoped denied | negotiated metadata/schema + correlated JSONRPC log; stdout protocol only; strict errors |
| T20 | dirty artifact A/B при одинаковом HEAD; create/merge intentions | разные artifact digest; simulation=true; real execute NOT_IMPLEMENTED; repo не меняется |

Будущие команды из project root, exact interpreter:

```text
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests/test_dom_contract.py tests/test_bytes.py -q
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests/test_storage_faults.py -q
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests/test_scope_trace.py tests/test_mcp_stdio.py -q
```

Матрица fault injection должна параметризовать названные до/после commit/outbox/export точки; наличие теста с подходящим именем без физических прерываний/reopen не PASS. Эти проверки уточняют исходные AA001 AC01–AC15, а не отменяют их.

## 8. Безопасное воспроизведение реально выполненных API-проб

Ниже только import/introspection/pure operations, без сервера/установки/пользовательской БД. Запускать exact `E:/opencode_harness_portable/.venv/Scripts/python.exe -B -c` с указанными Python expressions:

```python
import sys, importlib.util, importlib.metadata as md, inspect, sqlite3
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP
print(sys.version, sqlite3.sqlite_version)
print({x: bool(importlib.util.find_spec(x)) for x in ('yaml','mcp','pytest')})
print({x: md.version(x) for x in ('mcp','pytest','PyYAML')})
for x in (stdio_client, ClientSession, ClientSession.initialize,
          ClientSession.list_tools, ClientSession.call_tool, FastMCP.run, FastMCP.tool):
    print(x.__name__, inspect.signature(x))
print(types.LATEST_PROTOCOL_VERSION)
print(StdioServerParameters(command='python', args=['-B','server.py'], cwd='E:/sandbox').model_dump())
```

Raw hash probe (не implementation canonicalizer):

```python
import hashlib
vectors = {'lf': b'A\n', 'crlf': b'A\r\n', 'space': b'A \n',
           'unicode_nfc': 'é'.encode(), 'unicode_nfd': 'e\u0301'.encode(),
           'decimal': b'1.2300e-40 mol/L'}
print({k: (v.hex(), hashlib.sha256(v).hexdigest()) for k,v in vectors.items()})
```

Validator pure probe: import через `importlib.util.spec_from_file_location` exact `scripts/code-factory/contract_validator.py`; вызвать только `validate('researcher',{})`, не `main`/dispatcher. Read-only refs: `git -C E:/opencode_harness_portable show mp/k0/journal:harness_context/journal.py`, `show mp/int:harness_context/ports.py`, `show mp/k3/m6-inject:harness_context/packet/__init__.py`. Никаких checkout/worktree/merge.

## 9. Scope и выдача

Обязательные входы AA002 прочитаны полностью (master-plan — K0/K3/K4 и §6–8 диапазонами); AA001 JSON даёт **канонические 12 question texts**, сохранённые без перефразирования в `original_question`. Факты кода, pure probes, предложения и NOT_RUN различены. Общие root-level отчёты/реестры контракта 08 не изменялись: проектная карта явно переопределяет пути. Исследователь не создавал TD/APPROVE и не принимал собственный результат.

Единственные выходы:

1. `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/research/AA002_RESEARCH.md`
2. `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/research/AA002_RESEARCH.json`
3. `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/research/AA002_SOURCE_LEDGER.json`

Перед handoff выполняется read-only структурная проверка: exact question coverage/text, unique IDs, разрешённые verdicts, evidence refs, mandatory origin schema, hashes и соответствие записанных путей. Это проверка артефактов исследования, не E2E DOM и не независимая приёмка.
