# AB002-A — техкарта воркера: доставка по наблюдению и гейт целостности

## Роль, место в фабрике, полномочия

Воркер-разработчик, не аналитик/ресерчер/принимающий. После AU001 → AN001 → завершённого RS001 реализует один вертикальный срез A. Порядок после сдачи: reviewer → auditor → analyst → researcher → next worker. Не принимать себя и не закрывать всю систему.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Логическая ветка AB, блок AB002-A; действующий Git ref не менять. Новые клаймы сохраняют собственную ветку происхождения, не выводить её из роли воркера.

## Слова заказчика — дословно

тогда идем дальше - так же циклами фабрики до полной реализации

делай акцентне на тестики а на е2е прогоны  боевые с вариативностью начальных условий и намеренными попытками вызвать отказ

по поводу проверяющих -  и паденя агентов по лимитам - нужно передиспат для продолжения  и наче это  некоретно.. но эт уже на будущее

## Входы, приоритет и инструменты

1. P/REQUIREMENTS.md — прочитать целиком; исходные слова выше предложений.
2. E:/opencode_harness_portable/docs/CODERS/15_GENERAL_HANDS.md, 03_ACCEPTANCE.md, 10_CHAIN_CONTRACTS.md, shared/code-factory-process.md — нормативные контракты harness, пути от корня harness (не от P).
3. P/docs/FULL_IMPLEMENTATION_PLAN.md, P/docs/AB002_PLAN.md, P/docs/REVIEW_PROTOCOL.md, P/docs/SPEC.md.
4. P/runtime/RS001_HANDOFF.md — целиком, особенно срез A, матрица S0…S6/E0…E12 и открытые UD. P/runtime/RS001_RESEARCH.json: точные Q-01/02/03/09/11, next_worker_slices AB002-A; MD §11 уточняет прежние противоречивые рекомендации.
5. P/runtime/AN001_ANALYSIS.json и P/runtime/AU001_AUDIT.md — конкретные дефекты F-AU-02/03/04/05/10, TD-DOM-13/16/17 и классификация ошибок TD-DOM-05.
6. Текущие P/mockup/*.py, tests/, mockup/README.md и runtime/AB001_RESULT.* — текущее поведение, не доказательство его правильности.

Доступны skill_view, read_file/search_files, write_file/patch, terminal. Интерпретатор строго E:/opencode_harness_portable/.venv/Scripts/python.exe (существующие mcp/PyYAML/pytest). Никаких pip/uv install. Подходящие skills: incremental-implementation, systematic-debugging, append-only-evidence-store; E2E первичен, TDD локализует регрессию.

## Требуемый продукт

Рабочий путь через настоящий stdio MCP subprocess: init → submit/review/admit → durable intent → sync → фактическое чтение конечной цели → сохранённое наблюдение → подтверждённая доставка → trace/resume → restart/reconcile. Локальная цель OMH остаётся SIMULATION, но файлы/SQLite/процессы и MCP кадры настоящие. LIVE OMH=NOT_TESTED, если нет разрешённого контракта; не выдумывать ID/права.

### Обязательные инварианты

A1. Ответ attach/send не доказательство доставки. Ack возможен только после успешного read-back точного intent/tx/digest/target и фиксации связанного наблюдения. Лгущий порт, заявивший ack без записи, оставляет pending/ambiguous и NOT_READY.
A2. Единый согласованный протокол попыток: долговечная попытка или reconcile-контекст предшествуют наблюдению; ack ссылается на observed. Не скопировать несовместимые автоматы Q-02/Q-03. Согласовать переходы кратким файлом runtime/AB002_A/protocol.md до реализации. Это инженерный выбор внутри среза, не смена UD.
A3. После потери ответа или смерти процесса после фактической записи — новый процесс сначала сверяется с целью; повтор не дублирует эффект. Не обещать универсальное exactly-once. Не держать SQLite write-транзакцию во время внешней доставки/LLM.
A4. Публичный delivery()/tool не даёт автору/caller возможности вписать ack. Уже действующие capability/scope обязательны. Текущая fixture-identity не становится production auth; in-process злоумышленник вне гарантии, ограничения явны.
A5. Append-only наблюдения и попытки защищены immutable/duplicate-key guard (включая REPLACE/IGNORE/UPSERT); связь intent/observed/ack проверяется схемой/валидатором. Произвольная последняя строка state не должна перекрывать отсутствие доказательства.
A6. Единый integrity gate перед выходом query/trace/resume/export и внешним side effect sync: битый hash или конверт без value → структурированный доменный отказ с локатором, без KeyError, без нового файла/записи цели. Диагностический ответ возможен, READY — нет. Не внедрять выбранную за автора repair/rewind-политику. Проверка и snapshot не должны разъезжаться незаметно при конкурентном изменении; зафиксировать read_at/observed revision в evidence.
A7. Ошибки busy, corrupt, read-only, unavailable различимы по реальному SQLite error code/причине; не раскрывать секретные пути и payload. Не ловить все ошибки как storage busy и не проглатывать corruption.
A8. Происхождение, тело/ссылки/комментарии и исходные снимки клаймов не редактируются. Подлинный маркер ветки виден по всему маршруту. Никакого автоматического закрытия задачи владельца.
A9. Старт с существующей БД: совместимая схема читается/возобновляется; требующая миграции получает честный MIGRATION_REQUIRED или контролируемую сохраняющую историю миграцию с отдельным evidence. Никакого silent reset, DROP/пересоздания исходной БД ради зелёного прогона.

## Scope изменений

Писать только P/mockup/**, P/tests/**, P/runtime/**, P/artifacts/WORKER_AB002_A.json и P/reports/WORKER_AB002_A.md. mkdir допустим. README обновлять P/mockup/README.md. Исходники вне P, live-плагины/конфиги, карты/спеки/исследования/реестр долгов — READ-ONLY. Findings вне scope перечислить с предлагаемым TD, не исправлять попутно.

Запрещены: удаления существующего кода/логов, ослабление guards/oracles, skip/xfail, удаление assert ради зелёного статуса, Git-мутации, сеть/listeners, установки, платные модели, live-OMH операции и пользовательские базы. Временные файлы и basetemp только P/runtime/, pycache не разносить по harness. Деструктивные инъекции только в disposable-копиях внутри выделенного runtime. Не трогать чужие старые run-каталоги.

## Главная приёмка — E2E, не счётчик pytest

Сценарии выполняются через настоящий MCP-клиент/stdio subprocess. Внутренний прямой вызов Service допустим для локализации/инъекции, но не заменяет наблюдение клиентского ответа и реального конечного состояния. Инъекция только launcher/test adapter, не новая model-facing возможность вредить данным.

Обязательные вариации для среза A (точные ожидания из RS001_HANDOFF):
- E0: пустая/существующая БД, AA/AB, полный маршрут до цели и read-back.
- E1/E2: реальная смерть дочернего процесса до/после commit; reopen новым процессом; rollback либо видимые принятые tx/intent без ложного ack.
- E3/E4: смерть до/после rename экспортного файла; после restart факт файла не подменяет наблюдение, восстановление без двойной доставки.
- E5: второй OS-процесс удерживает write lock; клиент видит busy; после release повтор корректен.
- E6: недоступная цель; отдельный лгущий attach, который отвечает ack без записи; trace не готов. Затем восстановить цель и доказать одну запись.
- E7/E8: повтор с иным payload, попытка подмены роли/ветки — структурированный отказ, исходники и цель неизменны.
- E9: повреждённый конверт и отдельно hash на изолированной копии; MCP query/trace/resume/export/sync не падают и не выпускают повреждённое.
- E10: immutable UPDATE/DELETE/REPLACE/IGNORE с read-back прежних точных байтов.
- E12: два процесса одновременно восстанавливают pending/ambiguous; no lost update/no duplicate, согласованные receipts/цель.

E11/новая revalidate-политика и остальные срезы не выполняются молча: оставить NOT_TESTED и назвать UD. Не объявлять 13 кейсов пройденными при частичном покрытии комбинаций. Выполненные и пропущенные сочетания перечислить. Сначала воспроизвести ключевой старый отказ (ложный ack), сохранить фактический baseline, затем реализация/повтор.

## Артефакты и программа сдачи

ПЕРВЫЙ артефакт — P/artifacts/WORKER_AB002_A.json: честный минимальный PARTIAL с scope и remaining, не фиктивный PASS. Обновлять по факту, не оставлять запись результата на последний вызов.

- P/runtime/AB002_A/ — протокол, source/input fingerprints, raw MCP frames, команды/exit/PID, snapshots конечной цели/SQLite до/после и восстановления, логи, вариативные case directories.
- P/runtime/AB002_A/e2e_manifest.json: cases[] с ID/variant, LIVE|SIMULATION, initial state/revision, entrypoint, injection, expected, actual, evidence_paths[], final_readback, recovery, verdict PASS|FAIL|NOT_TESTED; coverage и omissions с причинами. Нельзя PASS по ожидаемому примеру без actual.
- P/artifacts/WORKER_AB002_A.json: роль, task/block/branch, точный scope, fingerprints, changes, commands/exit codes, e2e_manifest_ref, per_invariant A1…A9, not_implemented, not_checked, remaining_UD, security_limits, known_failures, proposed_debts. status PASS|PARTIAL|BLOCKED, is_approval=false.
- P/reports/WORKER_AB002_A.md: краткий handoff reviewer, что реально изменилось, факты E2E/отказов, точные команды воспроизведения и остаток.

Финально реально выполнить E2E-runner (создай воспроизводимую команду в mockup/, без зависимости от временного scratch) и вторично регрессии: из P `E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q --basetemp=runtime/AB002_A/pytest-final`; `... -B -m mockup.demo` как happy path. Не использовать pipe, скрывающий exit code. Дочерние процессы закрыть, не убивать чужие.

## Стоп и продолжение

Не менять за автора UD-01…06 (API branch/master, baseline/stale, rewind/repair, упаковка экспорта, модель угроз identity, смысл convergence). Работа A от них не зависит в текущем периметре. Если возникла настоящая зависимость — PARTIAL и точный блокер, остальное выполнить. При лимите записать точные уже выполненные шаги/пути/остаток; оркестратор передиспатчит эту же роль, не допишет результат за тебя.
