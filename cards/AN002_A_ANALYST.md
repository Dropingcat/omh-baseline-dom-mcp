# AN002-A — аналитик после REQUEST_CHANGES AU002-A

## Роль и вопрос

Аналитик: ПОЧЕМУ не работает. Не воркер/принимающий/ресерчер. Следующее звено фабрики после законченного auditor. Нельзя немедленно чинить код или заменять весь предыдущий research новой разведкой. Подготовить ограниченный причинный хендофф для RS002-A, затем обновлённый план/техкарта.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.

## Прямые требования заказчика

тогда идем дальше - так же циклами фабрики до полной реализации

делай акцентне на тестики а на е2е прогоны  боевые с вариативностью начальных условий и намеренными попытками вызвать отказ

после  цикла обнови план OMH по тестированию сценариями как записи так и чтения обновления  выборочный поиск - поиск по веткам-  на предмет протечек из дроугих веток. создать через планера план тестирования и предварительный поиск местотказа-  где будет утечки где проблемы- и эти места и становятся  чеками для проверки и симуляций. - нужен прогон спеца по зеопасночти и тестированию - нужен шаблон новый для контракта по этому очень жосткий ядреный  работающия не на положительный результат а с ветором на заваливание и негатив

Полный неизменяемый авторский базлайн: P/REQUIREMENTS.md, включая дерево уточнений (отложено для researcher; не реализовано в A).

## Норматив и входы

E:/opencode_harness_portable/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md (§1/4/6.1), 09_FINDINGS_ESCAPE_HATCH.md, shared/code-factory-process.md. Пути от harness.

P/artifacts/AUDITOR_AB002_A.json и P/reports/AUDITOR_AB002_A.md — читать полностью. Там секция0, две новые находки, физические признаки и границы.
P/artifacts/REVIEWER_AB002_A.json, P/reports/REVIEWER_AB002_A.md — predecessor, не доказательство отсутствия новых дефектов.
P/cards/AB002_A_WORKER.md (A1…A9), docs/AB002_PLAN.md, runtime/RS001_HANDOFF.md и JSON Q-01/02/03/09/11, tech_debt.md.
Source mockup/admission.py (verify_chain/integrity_gate/сериализация), ports.py (read_target/attach), server.py (обработка исключений), delivery.py/storage.py по связям. Достаточно релевантных частей, не читать весь harness заново.
P/templates/NEGATIVE_E2E_SECURITY_CONTRACT.md и cards/PL003_NEGATIVE_E2E_PLANNER.md — будущий сценарный этап, PREPARED, не проведён.

## Зафиксированные факты для анализа

1. F-AU002-01 / TD-DOM-19, major IN_SCOPE A6+ACL: AA-only caller, AA неизменна; другой разрешённый actor добавляет AB. Шесть AA-ответов выдают read_snapshot.revisions.AB=0→1. Прямое чтение AB даёт SCOPE_DENIED. На disposable копии повреждение среднего AB event fail-closed, но ограниченная диагностика выдаёт UUID AB, seq/global count/head.
Evidence: runtime/AU002_A/run-b944ea96/scope/{result,restricted-before-hidden,restricted-after-hidden,positive-control}.json и middle/{injection,responses,result}.json. Симптом healthy metadata не требует SQL/file прав у caller.
Source, прочитанный оркестратором: admission.py:48 глобальный SELECT events; broken() возвращает id/count; integrity_gate:92-93 stamp содержит dict всех branch_heads. Это code-факт, не уже выбранный способ исправления.

2. F-AU002-02 / TD-DOM-20, major OUT_OF_SCOPE A, но обязательство зарегистрировано: nested target current TASK=[] (валидный внешний JSON, неверная форма); read_target считает его пустым, attach вызывает .get у list. Два новых MCP процесса: raw AttributeError/isError без доменного статуса. Два attempt, нет observation/ack; NOT_READY безопасен. После исправления только своего target key фактическое восстановление и unrelated target сохранены.
Evidence: runtime/AU002_A/run-b944ea96/malformed-target/*.json. ports.py:31-39,64-71; admission.py:335-345.

3. TD-DOM-21 minor: зарегистрирован прежний RV002-A-DEBT-01; mutable global manifest не является immutable evidence. Не дублировать finding.

Оркестратор проверил существование своих файлов аудитора, секцию0, все 42 текущих source/input hashes, 13 evidence refs и зарегистрированные TD. Вердикт REQUEST_CHANGES принят как вход, не исправлен как продукт. Качество доставки по прежним комбинациям не аннулируется, но не оправдывает утечку metadata.

## Задача

- По каждой находке: симптом → причина → причинный класс → нарушенный invariant/boundary → фактор, который не поймал прежний review → минимальный сценарий причины → физическое доказательство → уверенность и пределы.
- Разделить конфиденциальность клайма/ветки и глобальную целостность. Проверка всей цепочки внутренне может оставаться необходимой; публичная redaction не должна ослабить integrity или скрыть блокирующее повреждение. Не рекомендовать просто отключить проверку или заменить её успехом.
- Определить, где новые поля/отладочный контекст обходят существующий scope; проверить соседние выходы/ошибки/chain metadata как возможный класс, не делать безусловный вывод «все каналы текут» без evidence.
- Для внешнего target: разделить отсутствие ключа и неверную nested форму, ownership неизвестных keys, raw exception versus truthful pending/ambiguous. Нельзя спасаться silent reset/перезаписью чужого содержимого или фиктивным ack.
- Разделить in-scope fix и out-of-scope обязательство; прежние UD/B/C/D/LIVE не считать выбранными. TD19 не отложить под предлогом будущего security cycle.
- Сформировать небольшое число точных вопросов RS002-A, каждый со стабильным ID Q-A2-xx, exact question, findings/debts, source requirement, expected contract, критерий E2E. Нужны ответы как работает безопасная диагностика/проекция для actor scope и внешний shape validation, а не повтор всех 15 прежних вопросов.
- Сформировать handoff planner PL003 после завершения analyst→researcher части цикла: полученные реальные места утечки должны стать checks, не потеряться в повторном общепроектном списке. Дерево уточнений направить будущему researcher отдельным контекстом, не смешивать с исполняемым fix A.

## Выход и первый результат

Первым: artifacts/ANALYST_AB002_A.json с честным минимальным PARTIAL и исходными находками; затем дополнять.
Финальные: artifacts/ANALYST_AB002_A.json, reports/ANALYST_AB002_A.md, runtime/AN002_A/** (машинная сверка/собственные неразрушающие пробы при необходимости).

JSON: role/task, status PARTIAL|COMPLETE_MATERIAL|BLOCKED, completion_state, input/source hashes, causes[] с evidence и certainty, findings_coverage F-AU002-01/02+TD21, priorities, questions_for_researcher[], requires_user_decision[], unverified[], next_step, planner_handoff, deferred_requirements. COMPLETE_MATERIAL не приёмка продукта.

Программно проверить exact coverage находок/TD, уникальные question IDs, наличие всех required fields и разрешение local refs; итоговая validation только структурная. Не закрывать debt по анализу. Не выдумывать DOI/команды/происхождение.

## Инструменты, границы, лимиты

read_file/search_files, write_file/patch, terminal для JSON/hashes/локальных безопасных проб; Python E:/opencode_harness_portable/.venv/Scripts/python.exe. Scope записи только свои artifacts/ANALYST_AB002_A.json, reports/ANALYST_AB002_A.md, runtime/AN002_A/**. Product/tests/docs/cards/registry/plugin read-only. Не править глобальный tech_debt. Никаких Git-операций/установок/сети/listeners/платных сервисов/секретов/пользовательских баз, удаления старых evidence, расширения actor полномочий.

Ориентир 12–18 calls, последние 3 зарезервировать на финальные файлы/валидацию. Не запускать полный E2E matrix заново для анализа уже доказанного. При cap — continuation этой же роли с точным остатком; parent не допишет за тебя. Ресерчера самостоятельно не вызывать — последовательность контролирует оркестратор.
