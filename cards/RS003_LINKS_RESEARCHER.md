# RS003 — ресерчер: связанный базлайн, вложенные версии клайма и scoped граф

## Роль и принятый scope

РЕСЕРЧЕР отвечает КАК ДОЛЖНО РАБОТАТЬ на вопросы завершённого AN003. Не аналитик заново, не worker, не независимый принимающий. Работа строго после AN003; не запускать других агентов.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.
Нормативы: E:/opencode_harness_portable/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md и 09_FINDINGS_ESCAPE_HATCH.md; E:/opencode_harness_portable/shared/code-factory-process.md. Source requirements первичны; при конфликте указывать цитату/источник, не исправлять исходник.

## Слова заказчика и статусы — не переоткрывать

«да хорошие поедложения- но надо собрать твои и мои и запузырить в агента аналитика и ресерчера по нашиму правилу».

Четвёртое–седьмое уточнения в REQUIREMENTS.md читать полностью и дословно. Последнее подтверждение:
«да именно так и говорил т.е  роительный клайм сверху- а все новые но с этим жи идом в его деревое как бы они новые но кабы они в нем вложены».

СМЫСЛ УЖЕ ПОДТВЕРЖДЁН: родитель сверху, новые неизменяемые записи/версии внутри дерева того же логического клайма. Это не новый needs_user. Инженерная схема logical ID/record-version ID/parent_ref/составной ключ не выбрана. Общий logical ID сам по себе НЕ нарушает неизменяемость; прежнее категорическое утверждение родителя аналитик отверг. Не переименовывать существующие UUID или путать AA11/АА11 (буквальные примеры обсуждения) с AA001 (ярлык задачи).

Расположение keywords не утверждено: ответ «да» на вопрос «или» не выбирает claim/edge/both. Сравнить варианты Q-L-11 и дать один точный выбор заказчику; не останавливать остальные вопросы. UD-02/06, новые trust/retention полномочия, YAML continuation и порядок TD19/SEC003 не выбирать молча. Устранение известной утечки TD19 уже обязательно и не зависит от согласия на новые graph-фичи.

## Проверенный предыдущий этап

AN003 COMPLETE_MATERIAL/completion_state=completed; это материал, НЕ приёмка продукта. Родитель независимо проверил текущие hashes 29 source files и все 12 hashes собственных output files, 14 уникальных exact questions, поля каждого вопроса и 123 допустимых source-line refs, наличие вопросов дословно в отчёте, результат receipt PASS/exit0 и 7 отвергнутых негативных контролей. PASS_MATERIAL_HANDOFF_ONLY. Новый продукт не запускался; REQUEST_CHANGES/product_acceptance=false, долги не закрыты.

Полный вход:
- artifacts/ANALYST_AN003_LINKS.json — ВСЕ разделы, особенно questions_for_RS003: это единственный точный текст Q-L-01…Q-L-14. Переносить exact_question ДОСЛОВНО, не пересказывать и не сокращать.
- reports/ANALYST_AN003_LINKS.md; runtime/AN003/questions.json, source_ledger.json, source_excerpts.json, mechanisms_and_impact.json, analysis_core.json, validation_receipt.json. Ledger S01…S29 даёт реальные paths/lines/current hashes. Exact questions из runtime/questions.json сверить с итоговым JSON, не угадывать форму файла.
- REQUIREMENTS.md, docs/CLAIM_ANATOMY_AND_LINK_MARKERS.md (предложение родителя, НЕ спецификация), docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md.
- Текущий код mockup/dom_contract.py, storage.py, projections.py, admission.py, server.py; по необходимости delivery.py/ports.py. Читать адресные места из analyst ledger, не всю кодовую базу.
- artifacts/RESEARCHER_AB002_A.json (закрытые public/internal/privileged DTO-контракты — proposed, не implemented); runtime/RS001_RESEARCH.json Q-05/06/07 и UD только для соответствующих дельт; не повторять RS001/RS002 исследования.
- runtime/PL003/failure_map.json H-LINK/CP-PL-17, scenario_plan.json SC-H-LINK; docs/FULL_IMPLEMENTATION_PLAN.md, docs/AB002_PLAN.md, cards/AB003_TD19_WORKER_PREPARED.md — ограничения очередности/scope.
- F:/AnalisysDataSet: только файлы, уже перечисленные в AN003 ledger. Идеи/точные функции см. F_reuse аналитика, не читать Inbox/Brain/pdf/личные данные и не сканировать диск.

## Все 14 точных вопросов — обязательный набор

Авторитетный полный текст: artifacts/ANALYST_AN003_LINKS.json#/questions_for_RS003. Проверить IDs/exact_question один-к-одному. Следующие группы — навигация, НЕ замена исходных вопросов:

1. Q-L-01/02/03: accepted_context/context pack, доказуемая цепь persisted→selected→delivered→acknowledged→used; поздние основания vs origin, root/legacy/no-baseline.
2. Q-L-04/05/06/07/08: logical/record IDs и parent, branch-local current accepted leaf и concurrent siblings, typed relations, разные статусы/authority/reopen, точные record/branch/line pins и stale/revalidation.
3. Q-L-09/10: scope-first graph/backlinks/count/rank/n-hop/shared node/cache/cursor; глобальный gate остаётся, DTO закрытый, hidden metadata не выпускаются.
4. Q-L-11/12/13/14: keywords decision; общий source subblock local/external; единый typed tree view/пагинация/миграции; перенос механизмов F без Dataview и float/config ошибок.

## Формат ответа, который можно передать worker

На КАЖДЫЙ exact question:
- mechanism/recommended_minimum: как устроено, состояния/поля/ownership/authority, конкретные data flow/transaction или handoff boundary;
- только существенные альтернативы и почему выбран минимум. Для спорного — таблица tradeoffs, не простыня взаимоисключающих идей;
- primary_sources/evidence: ledger Sxx и path:lines, code vs observed inherited vs proposed vs not_tested; не выдавать статическую проверку за E2E;
- contract/schema: закрытые типы, поля/условия обязательности, domain-safe отказы, совместимость с existing IDs/schema/canonicalization;
- action→expected→physical evidence: конкретный будущий негативный E2E + положительный контроль и failure injection по аналитическому вопросу. Тест не должен считать bool=true доказательством использования/понимания контекста;
- uncertainties/needs_user: инженерное можно рекомендовать, открытое продуктовое оформить отдельной развилкой; unresolved keyword policy не блокирует logical identity и isolation;
- scope_limit/not_implemented. Предложенный код/поля не объявлять implemented.

Уточнения к содержанию:
- Основание не равно происхождение; запретить фабрикацию basis ради nonempty поля. Позднее подтверждение добавляется, прежнее не меняется.
- Принятие кандидата, фактический admit, current/stale, convergence, observed delivery и owner close — разные оси; определить субъекта/доказательства каждого перехода. Указатель «не переоткрывать» не должен консервировать доказанную ошибку. Забывание ведёт к retrieval, не к отмене факта.
- Immutable logical/version identity совместима с общим ID; для ссылок требуется однозначный адрес версии. Пин версии не «магически обновляется». Ветка применимости не даёт grants и не переписывает origin.
- Дерево — typed производный вид событий+версий, stable ordering/постраничный обход/CAS/соседи; unlimited предметная глубина не означает неограниченный ответ или рекурсивный stack.
- В graph применять grants ДО candidate expansion/score/top-k/count/cursor/cache. Shared node не разрешает n-hop в запрещённые ветки. Global failure bit не становится foreign locator. Строгую timing неразличимость без измерений не обещать.
- Locality не означает доверие/право. Immutable URL не делает remote content immutable; hash без retained bytes не доказывает воспроизводимость. Никаких произвольных fetch/path traversal.
- F словари расходятся; .yaml-файлы могут содержать Markdown/JS. parseNumeric/0/отрицательные/units/duplicate tags, strength vs confidence и запрещённые float — реальные пункты для исследования, не копировать как готовый backend.

## Реальные проверки этой роли и ограничения

Главная поставка — исследовательский контракт и будущая E2E-карта, не продукт. При трудном инженерном выборе допустим МАЛЕНЬКИЙ synthetic offline prototype ТОЛЬКО runtime/RS003/**, без импорта write-path продукта/пользовательских БД, без изменения F. Если прототип выполнен — сохранить actual argv/exit/stdout/input hashes; если нет — proposed/not_tested, не fake PASS. Нельзя установками/сетью/новыми services расширять периметр этой роли.

Сформировать минимальные последовательные worker slices и evidence gates, не начинать реализацию, не закрывать TD19/20/21 и не отменять текущий P0. Дать точную подготовленную дельту FULL_IMPLEMENTATION_PLAN/OMH/техкарт, но НЕ править эти файлы/живой OMH самостоятельно. Не создавать второй planner или task board.

## Сдача и защита от ещё одного потерянного финала

ПЕРВЫЙ файл artifacts/RESEARCHER_RS003_LINKS.json: честный PARTIAL с exact 14 IDs и текущим остатком. Не держать весь синтез только в чате до конца. Сохранять ответы партиями по четырём группам в runtime/RS003/**, чтобы продолжение не начинало с нуля. В отчёте MD не дублировать весь JSON.

Финальные свои файлы:
- artifacts/RESEARCHER_RS003_LINKS.json: role/task/status/completion_state/product_acceptance=false, product_verdict=REQUEST_CHANGES; questions[] ровно 14 exact_question из AN003; answers или immutable refs на runtime-фрагменты; decision ledger, схемы, sources/current hashes, uncertainty/needs_user, next_worker_slices, plan_delta_prepared, limits, own_execution, validation_ref, remaining, continuation_required. COMPLETE_MATERIAL относится только к исследованию.
- reports/RESEARCHER_RS003_LINKS.md: что предлагается минимально, таблица logical ID/immutable version/parent/pins/events, общий вид формулы клайма, scoped graph/context-pack, открытые решения и будущие E2E; ссылки на полные ответы.
- runtime/RS003/**: source ledger/current SHA256, ответные блоки, схемы и решения, небольшой prototype при необходимости, validator+validation_receipt.json.

Программная проверка: 14 точных уникальных вопросов из итогового AN003 без потерь, required поля/typed-state tables, локальные source refs/current hashes и output hashes, все path refs разрешены, нет dangling Q/slice/decision, keywords/UD честно открыты, дерево НЕ новый needs_user, no product approval, предложенные E2E не PASS. Добавить отрицательные контроли валидатора (потеря вопроса/неверная версия/сломанный ref/fake approval), сохранить реальные exit codes. Parent будет читать material и сравнивать hashes, не переписывать финал за исследователя.

## Write scope, инструменты, бюджет

Запись ТОЛЬКО P/artifacts/RESEARCHER_RS003_LINKS.json, P/reports/RESEARCHER_RS003_LINKS.md, P/runtime/RS003/**. Source/tests/cards/docs/предыдущие evidence/debts/F read-only. Не Git/install/network/listeners/секреты/paid/live/config/субагенты. Python E:/opencode_harness_portable/.venv/Scripts/python.exe; tools read_file/search_files/write_file/patch/terminal/execute_code. Никаких созданных артефактов в /tmp Windows.

Ориентир 20–26 calls с резервом последних 4 на finish/validation, НЕ жёсткая квота ценой урезания14 вопросов. Первые сохранённые ответы — уже после нескольких адресных чтений, затем каждая партия отдельно. Если объём/лимит/сбой не даёт закончить — собственный PARTIAL с точным остатком для continuation той же роли; не фиктивный COMPLETE. Следующих агентов запускает parent после твоей сдачи.
