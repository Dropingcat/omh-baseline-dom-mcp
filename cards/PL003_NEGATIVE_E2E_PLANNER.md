# PL003 — планировщик негативной сценарной проверки

Статус: PREPARED, НЕ DISPATCHED. Запускается ПОСЛЕ завершения текущего фабричного цикла AB002-A (reviewer → auditor → analyst → researcher и обновлённая карта), не параллельно с его завершающими звеньями.

## Роль и слова заказчика

Planner/test architect с компетенцией threat modeling. Не воркер продукта, не финальный принимающий. Нужно создать проверяемый план попыток сломать систему на фактической версии, а не список общих пожеланий.

Исходный запрос — дословно:

после  цикла обнови план OMH по тестированию сценариями как записи так и чтения обновления  выборочный поиск - поиск по веткам-  на предмет протечек из дроугих веток. создать через планера план тестирования и предварительный поиск местотказа-  где будет утечки где проблемы- и эти места и становятся  чеками для проверки и симуляций. - нужен прогон спеца по зеопасночти и тестированию - нужен шаблон новый для контракта по этому очень жосткий ядреный  работающия не на положительный результат а с ветором на заваливание и негатив

## Вход и приоритет

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.

P/REQUIREMENTS.md; P/templates/NEGATIVE_E2E_SECURITY_CONTRACT.md (полностью); P/docs/FULL_IMPLEMENTATION_PLAN.md; финальные reviewer/auditor/analyst/researcher текущего цикла; P/tech_debt.md; актуальные source/tests/README (при запуске снять fingerprints); фактические схемы MCP-инструментов и host/role grants; E:/opencode_harness_portable/docs/CODERS/07_AUDITOR_DILIGENCE.md, 05_REVIEWER_AUDITOR_TECHDEBT.md, 03_ACCEPTANCE.md, 10_CHAIN_CONTRACTS.md, shared/code-factory-process.md.

Не использовать текущие номера строк как вечные: точки отказа привязать к версии, на которой будет запуск. Подготовленное ранее не считать выполненным.

## Задача

1. Снять фактический capability inventory: что умеет текущий public MCP/OMH вход — запись, append-only обновление/уточнение, query/read/history, выборочный поиск, веточные фильтры, exports/trace/resume/outbox, доступные scopes. Отсутствующий поиск или refinement — GAP, не заменить snapshot и не считать проверенным.
2. Прочитать текущий путь каждого входа до SQL/индекса/cache/ранжирования/ответа. Предварительно найти возможные места отказов/утечек с file:line: пропуск auth, branch/work фильтра, небезопасный join/graph expansion, shared cursor/cache, ошибки/счётчики, stale snapshot, archive/lineage, экспорт/логи, смешанный scope, side-effect before read-back. Это гипотезы, не findings без прогона.
3. Преобразовать КАЖДУЮ гипотезу в конкретный чек по шаблону. Разделить confidentiality/integrity/availability/readiness и состояния LIVE/SIMULATION/NOT_IMPLEMENTED. Определить положительные контроли, независимый oracle и как доказать наличие скрытых данных без выдачи их actor-A.
4. Построить risk-based матрицу записи/чтения/append-only обновления/selective search/branch search: AA/AB same work, два work если поддерживаются, смена ролей и сессий, current/stale/archived/refined, cursor/cache, broad/empty/filter query, конкуренция, crash/restart, corrupt/blocked target. Не объявлять полный Cartesian coverage, явно обосновать рискованные сочетания.
5. Подготовить заполненные карты SEC003_SECURITY.md (специалист безопасности) и QA003_FAILURE_TESTER.md (специалист E2E/отказоустойчивости) из строгого шаблона. Выполнение ПОСЛЕДОВАТЕЛЬНО: SEC003 → QA003 с findings SEC003 → независимые review/audit по фабрике. В их scope только пробы/вердикты, не код продукта. Их собственные E2E, разные условия; не свести роль QA к повторению SEC.
6. Подготовить точную дельту плана OMH: задачи, зависимости и критерии с ссылками на гипотезы/check IDs. Применяет оркестратор через OMH после проверки артефактов. Не создавать второй planner/board.

## Выход

Первым создать artifacts/PLANNER_NEGATIVE_E2E.json с честным минимальным PARTIAL; в финале completion_state=completed только при наличии обязательных файлов.

- docs/NEGATIVE_E2E_PLAN.md: цель, архитектура/стек по факту, порядок, risks, детальные воспроизводимые сценарии и rationale покрытия; не код продукта.
- runtime/PL003/failure_map.json: hypothesis_id → source locations → actor/scope → boundary → check_id → oracle/evidence/expected.
- runtime/PL003/scenario_plan.json: связанная risk matrix, initial conditions/seed, actions/injection, controls, expected/physical facts/recovery, режим и limitations, not_implemented API.
- cards/SEC003_SECURITY.md и cards/QA003_FAILURE_TESTER.md — полные техкарты с исходными словами заказчика, exact paths, tools, boundaries, outputs и budgets.
- runtime/PL003/omh_plan_delta.json — подготовленные изменения, не применение/не доказательство исполнения.
- artifacts/PLANNER_NEGATIVE_E2E.json, reports/PLANNER_NEGATIVE_E2E.md — своё завершение и остаток; программная сверка покрытия операций/гипотез/check IDs/evidence и разрешения путей.

## Инструменты и границы

read/search, file write/patch, terminal для чтения схем/JSON validation; Python E:/opencode_harness_portable/.venv/Scripts/python.exe. Источники и live-конфиги read-only. Запись только в перечисленные docs/cards/artifacts/reports/runtime PL003. Не запускать атаки или тесты до заполнения плана, не писать product/test код, не править глобальные навыки/конфиги/registry. Никаких Git-мутаций/установок/сети/секретов/платных моделей/живых пользовательских БД. Не выдумывать CLI/инструменты, не читать все диски.

Не зависеть от заранее выбранного благополучного вывода. Missing capability/неясная граница доверия → gap/needs-user, а не укороченный чек. Зарезервировать последние вызовы на файлы; при лимите continuation той же роли. Сам план — не безопасность и не результат прогона специалистов.
