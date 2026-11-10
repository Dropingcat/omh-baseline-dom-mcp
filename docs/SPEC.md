# SPEC — исполняемый макет DOM ↔ OMH

Статус: решение лида для локального synthetic макета в пределах разрешения заказчика. Не production-архитектура, не разрешение live-подключения. Требования REQUIREMENTS.md выше этой спецификации. AA002_RESEARCH.json задаёт детальные контракты storage/digest/types и матрицу T01–T20; это нормативный вход для макета, кроме явных уточнений ниже.

## Цель и результат

Получить реально исполняемое ядро и stdio MCP-сервер: одна локальная SQLite DB, ветки AA/AB, per-claim origin markers, строгий ввод, append-only история, demo independent admission, транзакции/повторы/сбои, scoped YAML и контроль остатка. Один воспроизводимый сценарий должен физически создать БД, внести кандидат, отклонить самоприёмку, принять отдельным demo-reviewer, восстановиться после lost response, добавить комментарий, вывести trace и YAML.

## Что реально, что симулируется

Реально: bytes/base64/hash, validation, SQLite constraints/OCC/rollback/reopen/two-process race, API scope checks, deterministic scoped export, отдельный subprocess MCP initialize/list/call.

Симуляция только: существующий внешний OMH work/task/requirements binding, capability issuer и reviewer principals, OMH target attach/read-back, Git describe/create/merge intentions. Любое положительное admission = DEMO_ADMITTED с simulated=true. Режим production без verified adapter всегда OMH_BINDING_UNVERIFIED или INDEPENDENCE_NOT_ENFORCED. API scope не объявлять OS isolation.

## Неотменяемые инварианты

1. OMH владеет глобальной работой, задачами, критериями и закрытием. DOM хранит ссылки и evidence, не заводит task-status controller.
2. У КАЖДОГО клайма стабильный server UUID claim_id, origin_branch и origin_version. AA001 — label задачи, не ID клайма. Origin не меняется при переносе применимости, архиве или слиянии.
3. Тело/цитаты/старые ссылки/комментарии/записи свойств неизменяемы. Изменение только новой записью с provenance; исправление тела новым клаймом. Mutable допустимы только производные branch heads/индексы, не исторические факты.
4. Comment/link/property/applicability/archive/replacement содержат actor/root, серверное UTC время, версию/ревизию контекста, причину, ref и при исправлении supersedes. Содержательные изменения проходят тот же review/admission, не обход через dom_append.
5. Кандидат не покрывает требования и не виден в admitted snapshot. Формальная корректность не истинность. Review связан с точными candidate/dependency/policy/revision.
6. Новый work_ref не разрешает произвольный путь или базу. Scope проверяется до чтения и обходов. Ошибки не включают чужие значения, секретные payload и existence counters.

## Данные и протокол

Подробные поля: research/AA002_RESEARCH.json storage_contract, digest_contract, type_contract. Выбор ограниченного dom-c14n/v1 явно НЕ JCS. Exact body BLOB, strict canonical base64, scientific values как строки; duplicate JSON keys, floats, lone surrogates, bool-as-integer и неизвестные поля отвергать. Set-подобные arrays сортируются по заданным ключам, семантически ordered массивы не переставляются.

Strict package validator сначала проверяет envelope/auth, затем агрегирует все безопасные ошибки доступных элементов. REJECTED: accepted_count=0, rejected_local_ids, errors[{local_id,path,code,required,fix}], неизменная admitted revision, без candidate/claim rows для invalid input.

Author/reviewer/root/capabilities берутся из injected launcher/test context, не из tool args. Test role mapping фиксирован кодом synthetic adapter; model-facing reviewer_id/role запрещены. Launcher --simulation --fixture-role author|reviewer|owner — только доверенный тестовый стенд, не механизм production аутентификации. В author session привилегированные review/admit fail-closed. Приёмка разными root проверяется в service tests/отдельных fixture contexts; MCP handshake может отдельно проверить author path и отказ privileged tools.

## Транзакции и outbox

SQLite DELETE journal, FULL synchronous, FK ON на каждом connection, bounded busy handling. Проверять PRAGMA фактически. Admission: BEGIN IMMEDIATE → scoped dedupe before OCC → capability+digest+policy+dependency vector+revision recheck → immutable facts/events/links → branch CAS+global sequence → receipt+idempotency+OMH/export outbox → COMMIT. Исключение=rollback. После commit read-back receipt. Idempotency не зависит от session/tool_call; same key/digest возвращает прежние ID/receipt; different digest конфликтует.

Candidate submit тоже atomic/idempotent и не увеличивает admitted branch revision. Изменения AB не stale AA без зависимости. Медленная review/export/network не внутри writer lock. Outbox intents неизменяемы, delivery attempts/acks добавляются. Side effect before ack=ambiguous/reconcile; не exactly-once promise. Экспорт после commit: temp+replace+read-back digest, ошибка оставляет pending.

## Веточные projections и остаток

Owner fixture содержит ссылки R1/R2 на требования и обязательные ветки, не создаёт реестр задач DOM. Trace вычисляет coverage по active applicable DEMO_ADMITTED claims + current demo receipts в simulation scope. Archive AA не убирает AB. Недостаточный master scope → UNKNOWN. Master ready_for_owner_review только при covered criteria, semantically converged/excluded authorized branches, отсутствии conflicts/stale checks и обязательных pending intents. Никогда не вызывать OMH close.

Семантический merge — добавление применимости и явное разрешение conflicts, не перезапись тела. Git fixture имеет dirty artifact digest отдельно от HEAD; execute create/commit/merge возвращает NOT_IMPLEMENTED. Реальные Git операции в текущем repo запрещены.

## Интерфейс макета

Общее ядро service; тонкий server adapter. MCP tools: dom_init, dom_resume, dom_submit, dom_review, dom_admit, dom_append, dom_query, dom_trace, dom_export, dom_sync_status. Допустимо dom_sync отдельным tool для synthetic outbox. Для сохранения duplicate-key detection строгий envelope удобно принимать как payload_json/request_json string; SDK conversion не становится admission validator. Реальный returned tool schema документировать. Не добавлять arbitrary SQL/update/delete/fetch/path tools.

Запуск exact E:/opencode_harness_portable/.venv/Scripts/python.exe. Зависимости уже доступны: mcp1.30.0, PyYAML6.0.3, pytest9.1.1, Python3.11.15; не устанавливать. При несовпадении среды документировать факт, не подменять interpreter. Stdout сервера только JSONRPC, diagnostics stderr.

## Файлы и границы записи

mockup/{__init__,dom_contract,storage,admission,projections,ports,server,demo}.py, mockup/fixtures/, mockup/README.md; tests/; runtime/ для synthetic БД, логов, экспортов и отчётов. Допускается несколько небольших модулей с ясной ответственностью; не строить framework.

Не менять требования/analysis/research, source harness, плагины/конфиги, global registries или Git state. Не коммитить/merge/push. Никаких секретов и реальных личных данных. Не удалять существующий код. Source files только внутри проекта.

## Приёмка

Весь T01–T20 AA002 — конкретные проверки будущего макета. На каждый: action → expected → command → actual evidence → PASS/FAIL/NOT_IMPLEMENTED. Сквозные DB/crash/concurrency/transport проверки обязательны, unit-only не заменяет их. Не считать exception failpoint настоящим process death: T06/T07 требуют terminate/exit дочернего процесса и reopen.

Макет не DONE пока независимый reviewer не проверил требования по коду и фактам, затем quality/security reviewer не провёл собственный прогон. Production gaps Q01/Q02/Q08, OS sandbox/live Git/external checkpoint остаются явно открытыми, но не препятствуют synthetic стенду.
