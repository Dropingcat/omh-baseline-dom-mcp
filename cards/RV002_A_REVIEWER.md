# RV002-A — независимое соответствие AB002-A

## Роль и вопрос

Reviewer, не автор/воркер, не аудитор/аналитик. Вопрос: соответствует ли фактический срез AB002-A исходным требованиям и карте A1…A9. Не менять код и не закрывать всю систему. После твоего файла отдельный auditor проверит, что НЕ работает, с новыми начальными условиями.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.

## Исходные требования заказчика — дословно

тогда идем дальше - так же циклами фабрики до полной реализации

делай акцентне на тестики а на е2е прогоны  боевые с вариативностью начальных условий и намеренными попытками вызвать отказ

по поводу проверяющих -  и паденя агентов по лимитам - нужно передиспат для продолжения  и наче это  некоретно.. но эт уже на будущее

## Входы и приоритет

- P/REQUIREMENTS.md целиком — первичный базлайн, включая дерево уточнений; само дерево deferred_to_researcher и не входит в A.
- E:/opencode_harness_portable/docs/CODERS/05_REVIEWER_AUDITOR_TECHDEBT.md, 03_ACCEPTANCE.md, 10_CHAIN_CONTRACTS.md; E:/opencode_harness_portable/shared/code-factory-process.md. Пути от корня harness, не от P.
- P/cards/AB002_A_WORKER.md — целиком, все A1…A9 и scope; продолжения C1/C2; docs/AB002_PLAN.md, docs/REVIEW_PROTOCOL.md.
- P/runtime/RS001_HANDOFF.md — E2E ожидания S0…S6/E0…E12 и границы UD.
- P/artifacts/WORKER_AB002_A.json, reports/WORKER_AB002_A.md, mockup/README.md и runtime/AB002_A/protocol.md — self-report, не доказательство.
- Source P/mockup/*.py, tests/ — прежде всего delivery.py, admission.py, storage.py, ports.py и MCP server/launcher/runner. Читай релевантные участки по A1…A9; не трать бюджет на повторный аудит всего harness.

## Наблюдаемая сдача (не подменяет твою проверку)

Worker: matrix-61c246ab, 26 PASS, 64 pytest, demo exit0. Оркестратор независимо запустил текущий runner: `runtime/AB002_A/matrix-66e2ca6b`, 26 PASS, exit0; повторный физический read-back 26 конечных состояний совпал; 118 MCP process receipts (112 exit0, 6 намеренных exit71), 111 SQL-проверок. Квитанция parent: artifacts/PARENT_AB002_A_READBACK.json. Это наблюдение оркестратора, НЕ независимая приёмка.

Нынешний source tree digest mockup/**/*.py: 715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3 (метод в parent JSON). Сам сними own fingerprint source/tests/inputs до/после. При смене версии affected evidence перепроверяется.

## Собственные обязательные действия

1. Проверить наличие/валидность всех worker deliverables, соответствие declared scope/fingerprints факту и omissions. Некорректное поле/нет actual → findings, не домысливать PASS.
2. Реально пройти stdio MCP E2E из новой пустой директории в runtime. Можно прогнать полный `python -B -m mockup.ab002_e2e` (timeout600) и далее независимо придумать минимум две точечные пробы через транспорт, не просто повторить скрипт автора. Запуск делает новый run и global manifest; сохраняй свой frozen manifest в runtime/RV002_A. Не запускать --baseline на исправленном коде.
3. Проба лживой доставки: порт отвечает ack без внешней записи, существующая БД/повторная сессия → клиент не получает подтверждённый ack/READY. Затем вернуть цель, restart новым PID, reconcile и read-back: ровно одна корректная запись tx/digest в цели, no duplicate. Подтвердить связь observation/ack прямым read-only SQL, не полагаться на sync-status.
4. Повреждение конверта/хеша на disposable copy → через MCP query/trace/resume/export/sync/sync_status структурированный отказ с локатором; нет нового файла/изменения цели. Выбери дополнительную комбинацию исходного состояния, отличную от автора (например resumed populated AA/AB). Не порти прежние evidence.
5. Выборочная собственная проверка негативных binding: ack без observation, чужой intent/digest/target, REPLACE/IGNORE/UPSERT; конкретная причина отказа плюс exact bytes before/after. Исключение любое-вместо-ожидаемого не является PASS.
6. Чтение кода A1…A9: side effect вне write transaction, no caller-state delivery, read snapshot/TOCTOU, legacy additive не стирает историю, busy/corrupt/read-only различаются, новый снимок/маркер не меняют исходник, owner-close не вызывается. Прямой in-process злоумышленник/админ ОС вне гарантии, не требовать невозможного и не выдавать fixture roles за auth.
7. Убедиться, что не ослаблены guards/oracles. Особое внимание C1 E10: CHAIN_INTEGRITY вместо IMMUTABLE допустим только для доказанного отказа с byte-exact unchanged, не broad except pass. C2 CANTOPEN_ISDIR требует точной пары extended code/name, не arbitrary sqlite exception. Не менять тесты.

Сценарий: начальные условия/ревизия → действия → точка отказа → expected → actual → физический read-back → восстановление → PASS/FAIL/NOT_TESTED. Число unit-тестов не приёмка. E11/revalidation, B/C/D, LIVE OMH/Git/auth/OS/checkpoint и refinement tree остаются явно вне этого delta-verdict.

## Артефакты (только твои)

Первый deliverable P/artifacts/REVIEWER_AB002_A.json — минимальный честный результат с current scope/evidence/remaining, не фиктивный APPROVE. До собственного прогона BLOCK/insufficient_evidence с completion_state=in_progress; этот ранний файл НЕ завершение и затем дополняется.

Финальные обязательные:
- P/artifacts/REVIEWER_AB002_A.json: role/task, verdict APPROVE|REQUEST_CHANGES|BLOCK, completion_state=completed только по факту, exact_scope, source/input fingerprints, per_invariant A1…A9, findings[] (id/severity/repro/expected/actual/evidence), own_runs с commands/exit и case/initial state, not_checked, limitations, proposed_debts.
- P/reports/REVIEWER_AB002_A.md: собственный вердикт и причины, ключевые пробы/факты, находки, остаток.
- P/runtime/RV002_A/**: сырые MCP кадры, PID/exit, frozen manifests, свои read-back/probes; без секретов.

Critical/major неисправен или не проверен в scope → не APPROVE. Нужна структура JSON с честными not_checked, никакой parent-приёмки вместо твоего файла. Findings — новые IDs RV002-A-Fxx; фиксирует нашедший, код не чинить.

## Инструменты, scope и бюджет

Python E:/opencode_harness_portable/.venv/Scripts/python.exe, file tools/terminal. Для реального прогона runner может писать собственный runtime/AB002_A/matrix-* и global manifest; это разрешённая тестовая инфраструктура, но не изменение исходников. Свои ручные записи только три области verdict/report/runtime RV002_A. Никаких product/test/docs/card edits, Git-мутаций, установок, сети/listeners, платных моделей, live-плагинов/пользовательских баз, удаления прошлых evidence. Деструктивные пробы только копия.

Бюджет около 20–25 calls, селективное чтение, 600 секунд на E2E; последние calls на verdict/report и JSON validation. При лимите continuation той же роли с сохранёнными собственными пробами; не просить родителя дописать. Перед сдачей проверить файлы/пути и отсутствие оставленных своих процессов.
