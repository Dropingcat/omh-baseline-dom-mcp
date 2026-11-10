# AB003 / TD19 — узкий P0 worker fix, PREPARED / НЕ DISPATCHED

> **For Hermes:** Use subagent-driven-development for implementation and separate reviewer/auditor. This card is prepared scope, not observed execution or approval.

**Goal:** прекратить выдачу hidden-branch metadata и diagnostics через разрешённые MCP-ответы, сохранив глобальную проверку и все внутренние delivery proof.
**Architecture:** полный internal proof остаётся неизменным. Public DTO строится отдельно по закрытым структурным схемам и launch-time grants в том же verified snapshot. Оба канала MCP сериализуют один безопасный объект.
**Stack:** существующие Python/SQLite/MCP/PyYAML; без новых зависимостей.

## Базлайн/порядок

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Код до исправления: sha256(sorted JSON map mockup/**/*.py path→sha256)=715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3. Этот digest — source fingerprint, не Git commit.

AU002-A REQUEST_CHANGES; AN002-A/RS002-A completed материал. Родитель подтвердил 5 точных вопросов, 7 planner points, 93 frozen input hashes и все output hashes exit0; это не продуктовая приёмка. TD19/20/21 OPEN. PL003 создаёт проверки; SEC003/QA003 выполняются отдельно. Не ждать будущего общего security PASS для признания TD19 реальным; эта карта — обязательный P0 fix.

## СНАПШОТ ПЕРЕД DISPATCH (2026-11-08, родитель)
- PL003: завершён, принят (542/542 PASS, материал-checked). SEC003: завершён, принят родителем (verify exit0 ok, completion_state=completed, verdict REQUEST_CHANGES, findings [SEC003-F-01]=TD19 reproduction). QA003: завершён, принят родителем (validation passed=true, 26 checks, verdict REQUEST_CHANGES, findings=prior refs TD12/15/18/19/20/21/07, новых debt нет). Оба подтвердили код-диджест 715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3; родитель пересчитал методом SEC003 digest_check — MATCH, 15 файлов, 0 расхождений.
- Находки для учёта в fix (prior refs, НЕ дублировать регистрацией): TD19 ре-наблюдают вложенных SEC003 (F-01) и QA003-F-19-REOBSERVED: read_snapshot.{chain_head,revisions} на 6 поверхностях, trace.chain.events, broken_event_id при коррупции среднего AB-события. CHK-A2-03: глобальный отказ корректен, но broken_event_id = foreign UUID (это и есть цель fix). QA003: REPLACE-проба и busy/read-only подкейсы CP-PL-10 не воспроизведены (WAL), NOT_TESTED честно — не требуют закрытия в этом срезе.
- Findings новых прогонов не скрывать; если fix выявит новые пути утечки помимо TD19 — задокументировать отдельной записью (не как новый TD, а как observation с severity), чтобы ревьюер/аудитор проверили на конкретной версии.

## Слова заказчика — дословно

делай акцентне на тестики а на е2е прогоны  боевые с вариативностью начальных условий и намеренными попытками вызвать отказ

## Полный вход, без пересказа контрактов

REQUIREMENTS.md; artifacts/AUDITOR_AB002_A.json + reports/AUDITOR_AB002_A.md; artifacts/ANALYST_AB002_A.json + reports/ANALYST_AB002_A.md; artifacts/RESEARCHER_AB002_A.json и reports/RESEARCHER_AB002_A.md.

RS002 JSON разделы worker_fix_contract, public_schemas, field_tables, tool_output_allowlists, recursive_schema_rules, payload_metadata_allowlists, append_event_value_allowlists и Q-A2-01/02 читать дословно. Exact question/contract body не сокращать. Уточняющий source truth — текущие admission/server/delivery/ports/projections. Не редактировать сохранённые исследовательские исходники/evidence, чтобы заставить hashes совпасть с будущим кодом.

## Последовательные действия → ожидаемое → физический факт

1. Собственный PARTIAL JSON + fingerprint; воспроизвести исходную TD19 на disposable populated fixture: AA fixed, AB change и положительный AB control. Ожидается прежний FAIL leak; raw MCP/text/structured/nested receipts показывают проблему до правки.
2. Разделить internal proof/public DTO. Ожидается отсутствие full chain head/count/seq/foreign UUID/revisions в публичной структуре; SQL observation сохраняет полный внутренний stamp и bindings. В том же read context, без TOCTOU новой проекции.
3. Все healthy surfaces query/snapshot/trace/resume/status/export + authorized AA-only sync и master UNKNOWN: только разрешённые поля/ветки; no diagnostic promotion union/reviewer/owner. Raw differential fixed AA / changing AB, исключение только documented read_at; текст и structuredContent семантически один DTO; YAML байты scoped.
4. Forbidden middle AB invalid UTF8 И отдельно wrong-hash на копиях; два свежих PID/семь gate tools. Ожидается одинаковый safe CHAIN_BROKEN/NOT_READY без foreign locator и без эффектов. Privileged fixture oracle отдельно точно находит corruption; DB/targets/exports before/after read-back одинаковы. Глобальный gate НЕ отключается ради ACL.
5. Проверить нормальную доставку+reconcile с реальными файлами/SQL/processes: не терять internal stamps, observation→attempt→intent→ack и no duplicate writes. Public projection не редактирует internal stamp в месте.
6. Own JSON/MD, frozen run manifest hash+source/input/environment и raw process/file/SQL receipts; вторичные regression проверки и docs schema changes. Не sole shared e2e_manifest pointer. Worker self-report не APPROVE.

## Scope/границы следующего dispatch

Планируемые изменения: mockup/admission.py, server.py; новый чистый DTO builder допустим после инвентаря; только необходимое glue projections.py; delivery.py guards/confirmed семантически сохраняются. tests/runtime/README — только в следующем явном DISPATCH по этой карте. Эта PREPARED запись сама никому не выдаёт write grant.

Не переписывать произвольные immutable claim/comment/property data slots ради redaction; allowlist относится к серверной структуре, не поиску слов внутри цитаты. Не увеличивать grants. Нет нового live privileged endpoint, repair/rewind, YAML continuation, target robustness TD20, refinement/search/Git/auth/OS/checkpoint/B/C/D в этом срезе. Не менять UD-01…06. Не исправлять тестовый oracle ради зелёного результата. При лимите continuation того же worker, финал пишет сам.

Окончательная приёмка после самостоятельных reviewer → негативный auditor на точной изменённой версии. До этого REQUEST_CHANGES сохраняется.

## Дополнение оркестратора 2026-11-07
Связи/backlinks/соседи (AN003, пока NOT_IMPLEMENTED) в этот срез НЕ входят и не вводятся. Allowlist DTO остаётся закрытым: если позже появятся вычисляемые поля связей, они проходят тот же scope-фильтр ДО выдачи. Не добавлять свободные dict-поля в публичный ответ «на будущее».
