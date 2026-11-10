# AU002-A — негативный аудит после RV002-A

## Роль и последовательность

Аудитор, не автор/ревьюер/fixer. Вопрос: ЧТО НЕ РАБОТАЕТ в процессе, интеграции и гарантиях среза A, несмотря на APPROVE reviewer. Работать после собственного completed JSON/MD RV002-A; этот вход проверен оркестратором на существование, 42 текущих fingerprints и 11 evidence refs. Следующий этап после тебя — analyst → researcher, не собственноручные fixes.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Полный норматив: E:/opencode_harness_portable/docs/CODERS/05_REVIEWER_AUDITOR_TECHDEBT.md, 06_PIPELINE_ORDER.md §3.3, 07_AUDITOR_DILIGENCE.md (целиком), 09_FINDINGS_ESCAPE_HATCH.md; E:/opencode_harness_portable/shared/code-factory-process.md. Пути от корня harness.

## Требования заказчика — дословно

тогда идем дальше - так же циклами фабрики до полной реализации

делай акцентне на тестики а на е2е прогоны  боевые с вариативностью начальных условий и намеренными попытками вызвать отказ

по поводу проверяющих -  и паденя агентов по лимитам - нужно передиспат для продолжения  и наче это  некоретно.. но эт уже на будущее

Последнее требование о поиске/утечках записано в cards/PL003_NEGATIVE_E2E_PLANNER.md. PL003 → SEC003 → QA003 запланированы ПОСЛЕ текущего цикла. Не выполнять вместо них весь новый охват и не объявлять его принятым; найденные сейчас утечки регистрировать, в том числе вне scope.

## Входы

P/REQUIREMENTS.md (приоритет исходных слов), cards/AB002_A_WORKER.md (A1…A9), docs/AB002_PLAN.md, docs/FULL_IMPLEMENTATION_PLAN.md, docs/REVIEW_PROTOCOL.md; artifacts/WORKER_AB002_A.json, reports/WORKER_AB002_A.md; artifacts/REVIEWER_AB002_A.json, reports/REVIEWER_AB002_A.md — ОБЯЗАТЕЛЬНО полностью; tech_debt.md и runtime/AU001_AUDIT.* (прежние системные findings); runtime/RS001_HANDOFF.md. Текущее source mockup/ и релевантные tests/.

Поведение нового строгого шаблона templates/NEGATIVE_E2E_SECURITY_CONTRACT.md использовать как отрицательную дисциплину/формат evidence, не расширять текущий delta-verdict до full-system security.

## Уже наблюдалось — не повторять без причины

Worker, parent и reviewer независимо выполнили 26-case raw stdio MCP matrix. RV002-A: 4 новые сценарные вариации, 25 negative SQL, физический read-back 26 своих/26 worker случаев, 48 ack. Source/inputs unchanged, blocking product findings нет. Это основания выбрать НЕдублирующие негативы, не доказательство отсутствия дефектов. Использовать immutable run-specific manifest, не global pointer, который runner перезаписывает.

Reviewer оставил RV002-A-DEBT-01 (minor, D tooling): ссылки на mutable e2e_manifest вместо frozen run-specific refs. Оценить/зарегистрировать, не перепроверять косметически всё дерево. B/C/D, E11/S4, LIVE/auth/OS/checkpoint/refinement остаются open; не заново регистрировать дубль существующего TD без новой поверхности/последствий.

## Секция 0 — до вердикта

На каждое подозрение: что подозревал → конкретное действие/проба → observed → классификация OK / finding / UNVERIFIED. Пустая секция или набор «прочитал/нормально» без попыток опровержения не принимается. Не требовать квоту багов: отсутствие нарушения честно, но только в проверенных условиях.

## Приоритетные НЕработающие состояния

До прогона сопоставить подозрение с кодом/контрактом, записать карту точек в runtime/AU002_A/suspicions.json. Выбрать рискованные места, которые reviewer не атаковал этим порядком событий:

1. Качество доказательства доставки: tx/digest/target/observed связываются, но не допускают ли положительный статус неправильные/legacy/переставленные записи, повтор reconcile, уже существующая чужая цель, удаление/замена цели между проверками? Ack историчен в read_at; не объявлять удаление цели позже нарушением вечной гарантии, которой нет.
2. Пограничная гонка: проверенный snapshot/область, pending из другой ветки, конфликт одновременной доставки, прерывание между durable attempt/observed/ack. Новые комбинации populated/resumed multi-branch, а не точная копия reviewer liar sequence. Реальный MCP и несколько OS PID; статус и физические последствия.
3. Partial failure: обновили одну цель (YAML), вторая недоступна; что видят trace/resume/sync_status и read-back нового процесса; нет ли молчаливого полного SYNCED/READY, потерянной операции или повторного эффекта.
4. Ошибка целостности из середины/legacy snapshot, неожиданный тип/кодировка/схема в enum пути: fail-closed на emitting и диагностике, сохраняется ли доступная безопасная диагностика без исключения и утечки? Не отключать guards в основной БД ради эксперимента; только disposable copy.
5. Различие прав на чтение/запись/доставку: scope enforcement на history/export/outbox/error, скрытые IDs или связь shared клайма. Current fixture boundary не production auth; если check обходит его через unlimited terminal — маркировать иную threat model, а не выдуманный MCP exploit.
6. Report-vs-fact и двойной источник правды: permissions/гарантии README, scope APPROVE, fingerprints/manifest lineage, миграция и повторные сессии. Формальный status или все unit PASS не доказательство физического эффекта. Повреждённая probe/неполный run не PASS.

Минимум две реально разные новые сквозные попытки опровергнуть A, вариации выбираешь по коду; конкретный fixed count не заменяет качество. Не запускать полный matrix только ради ещё одного 26PASS, если есть готовое актуальное evidence и нужны иные условия. Ключевые эпизоды подтвердить независимо своими MCP кадрами/SQL/file before-after/read-back и actual command exits. Обнаруженный critical/major зафиксировать сразу, не расходовать все calls на идеальную красоту отчёта.

## Выход — первый честный, финальный собственный

Запись только:
- artifacts/AUDITOR_AB002_A.json;
- reports/AUDITOR_AB002_A.md;
- runtime/AU002_A/** (пробы, сырые frames, before/after, fingerprint, manifests);
- tech_debt.md — ТОЛЬКО добавление новых найденных TD/уточнений с evidence, не закрытие старых по обещаниям.

Первый артефакт — честный минимальный PARTIAL/BLOCK с секцией 0 (текущие подозрения ещё UNVERIFIED). Это не финальный verdict. Затем заполнить собственные доказательства и завершить.

Итоговый JSON: role/task, verdict APPROVE|REQUEST_CHANGES|BLOCK, completion_state, exact_scope, source/input fingerprints, checked_suspicions[], own_runs/commands/PID/exit, findings[] (id,severity,scope,invariant,source:line,initial_conditions,repro,expected,actual,evidence,TD-ID), proposed/registered debts, out_of_scope[], not_checked, limitations, continuation_required. MD: сначала секция 0, затем вердикт, findings, физические прогоны, остаток и эскап-хэтч. Дельта-APPROVE не закрывает всю систему. Если нет способности безопасно воспроизвести — UNVERIFIED, не фиктивный PASS.

## Инструменты и безопасность

Python E:/opencode_harness_portable/.venv/Scripts/python.exe. File tools/terminal; reference source/docs/card read-only. Писать только перечисленное. Тестовые данные в runtime/AU002_A; стандартный runner может создать свой новый matrix в runtime/AB002_A и global pointer, если он действительно нужен; frozen copy сохранить. Никаких правок product/test/spec, installs, Git-мутаций, сети/listeners, платных моделей, live OMH/рабочих пользовательских БД и секретов, уничтожения старых logs/runs.

Заданные защитные границы не расширять ради удобной пробы. Реальная смерть дочернего процесса только собственного run, PID фиксируется; чужие процессы не останавливать. Timeout для долгого E2E 600 секунд. После прогона закрыть свои subprocess/соединения.

## Бюджет/continuation

Ориентир 20–25 вызовов с резервом последних 4 на TD/verdict/report/проверку путей и JSON. При лимите — продолжение этой же роли с уже собранным evidence и точным остатком; parent не дописывает за тебя. Сначала своё законченное свидетельство, потом следующий analyst; не запускать иных агентов самостоятельно.
