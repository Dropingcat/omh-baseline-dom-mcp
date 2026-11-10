# RS006 — Researcher по находкам AU005 (F-01…F-04) и сверке плана

Роль: RESEARCHER. Задача: RS006. Статус: COMPLETED (валидатор PASS, 8/8 вопросов).
`product_acceptance=false`, `is_approval=false`; ничего не применено к продукту/tests/tech_debt/OMH.

## 0. Подозревал → проверил → оказалось (первым)

| Подозрение | Проверил | Оказалось |
|---|---|---|
| L2 в исходном тексте оркестратора (docs/F02_IMPLEMENTATION_OPTIONS) работает как написано | Воспроизвёл на прототипе сценарий legacy-строки + повторного remember() при старом PK (work,op,key) | **Дыра**: «NULL-привязка → отказ; повторная легальная операция выполняется заново» невыполнимо — remember() упадёт в UNIQUE/IMMUTABLE на том же ключе. Нужен расширенный PK (work, operation, key, scope_digest): legacy-строка (scope_digest='') инертна и не блокирует новый admit (s8: BINDING_UNKNOWN + fresh-key ADMITTED + legacy intact). |
| Строгое равенство scope_digest в L2 сохраняет законное восстановление | Сценарий s6: сужение гранта {AA,AB}→{AA}, кандидат AA, deps {} — квитанция безопасна | **Строгий вариант ломает восстановление** (SCOPE_DENIED); пермиссивное правило result_scope ⊆ grant отдаёт REPLAY с 0 новых фактов. Арбитр — область операции, не снимок гранта. |
| confirmed()-скип в F-01 можно починить «просто добавить receiver в payload outbox при admit» | Чтение полного пути admit→sync | **Неверно**: receiver и view_scope известны только в момент sync (грант меняется между admit и sync) — identity обязан создаваться при доставке (delivery_acks v2), а не в outbox. |
| view_scope можно публиковать списком веток в ack/status | Модель видимости RS005 (exists-oracle класс) | **Нельзя**: список раскрывает факт выдачи union-гранта; публикуется sha256(sorted(branches)) — fingerprint байт нейтрален. |
| AB-replay с AA-кандидатом закрывается одним L1 | Прототип s2 | **Да**: DIGEST_MISMATCH до кеша; AB-кандидат → SCOPE_DENIED; binding (s4b) ловит даже случай равного digest. |
| RV003/AU003 где-то есть под другим именем | Re-search по artifacts/reports/cards/docs на текущем дереве | **Нет**: 0 артефактов; найденные вхождения — служебные runtime-файлы (.smoke/.diag/.pytest_cache). RV004/AU004/AU005 — AB004-fix scope, не эквивалент. |
| «O3 — только наблюдение» у оркестратора может оказаться правдой | continue01_verified.json:O3 + findings_map | **Неточно**: O3 физически воспроизведён (5fadbab7…/113628b8…, два PID, SQL ack) — CONFIRMED-дефект. |
| Мой прототип заработает с первого прогона | Прогон | **Нет**: 7 итераций исправлений (Windows file-lock rmtree → per-scenario dirs; незакоммиченные submit/review сносились rollback'ом; упущенное return в f01_scenarios; дыра в lost-reply модели — теперь read-back-первый). Итог: ALL_ASSERTS_PASSED, receipt sha256 `954105cb…`. |

## 1. F-02 — финальная форма L1+L2 (Q-F02-01, Q-F02-02)

Направление L1+L2 согласовано заказчиком; окончательная форма (с двумя исправлениями к предложению оркестратора):

1. **Порядок в admit()**: `candidate()` scope-check (кандидат+deps; SCOPE_DENIED до кеша) → **L1**: `row['digest'] != intent_digest` ⇒ `DIGEST_MISMATCH` (до dedupe) → **L2** dedupe с binding → прежние review-проверки (STALE_REVIEW/REVISION_CONFLICT) → remember с binding.
2. **Миграция idempotency**: новые колонки `candidate_id, review_id, branch, scope_digest, result_scope`; **PK ⇒ (external_work_ref, operation, key, scope_digest)** (пересоздание таблицы + immutable-триггеры в одной транзакции, user_version-гейт). Legacy-строки (scope_digest='', binding NULL): читаемы, инертны, никогда не выдаются (`IDEMPOTENCY_BINDING_UNKNOWN`), повторная операция — только с новым ключом.
3. **Replay разрешён** только при: строка с тем же ключом; binding (candidate_id, branch, review_id) совпал; digest совпал; **result_scope = {candidate.branch} ∪ deps ⊆ текущий grant**. Replay создаёт 0 новых фактов.
4. **Грант сужен-восстановлен**: сужение с видимой областью операции — REPLAY (законное восстановление); сужение с out-of-scope областью — SCOPE_DENIED; восстановление гранта — прежний идемпотентный повтор.
5. **submit-совместимость**: submit/append в том же idempotency, привязка scope_digest и result_scope из payload; операции разделены префиксом principal.
6. **Влияние**: dom_review не меняется (review_id входит в binding); dom_admit — новые коды отказов (DomainError {status}); dom_sync/export — вне F-02.

**Capability-модель (Q-F02-02)**: (key,digest) — знание, не capability. Capability = грант + scope-проверка кандидата + binding-совпадение + result_scope ⊆ грант. Легальны: потерянный ответ (тот же key+digest+candidate+review), launcher-initiated replay в том же scope, recovery по журналам при полной видимости операции. Нелегальны: чужой кандидат, narrowed-grant раскрытие, «логи == право на receipt».

**Прототип** (runtime/RS006/prototypes/rs006_f02_f01_prototype.py): s1 дефект воспроизведён (CACHE_HIT, branch=AB); s2 exploit → DIGEST_MISMATCH; s3 lost-response → REPLAY, 0 фактов, 1 строка; s4/s4b foreign candidate → BINDING_MISMATCH, tx=1; s5 review mismatch → REVIEW_MISMATCH, новый key → ADMITTED; s6 permissive REPLAY vs strict SCOPE_DENIED; s7 SCOPE_DENIED; s8 legacy → BINDING_UNKNOWN + fresh ADMITTED + legacy intact. Receipt sha256 `954105cb…`.

## 2. F-01 — модель view/receiver-aware delivery identity (Q-F01-01, Q-F01-02)

- **Identity = (intent_id, receiver, view_scope_digest, source_revision, delivered_byte_hash)**: receiver — principal процесса sync; view_scope — frozenset(context.branches) на момент sync; source_revision — intent.revision; delivered_byte_hash — sha256 фактически приложенных байт.
- **Хранение**: delivery_acks v2 (колонки receiver/view_scope_digest/fingerprint/source_revision, `UNIQUE(intent, receiver, view_scope_digest, fingerprint)`); observations остаются первоисточником байт.
- **Старые receipts**: legacy-строки читаемы/верифицируемы, не переписываются, не удовлетворяют новому identity-поиску (M5).
- **AA-проекция vs полный пакет**: разные (view_scope_digest, fingerprint) у ack; AA-ack никогда не засчитывается за union-ack (M1).
- **Передоставка под расширенным грантом**: sync пересчитывает проекцию; скип — только при точном совпадении (receiver, view_scope, fingerprint) с текущими байтами (M1/M2/M6); explicit export не мутирует ack (M4); lost-reply — ровно одна физическая запись (M3); два receiver — две ack (M7).

## 3. Порядок worker-срезов

WS-F04-TYPED-ABSENCE (1, низкий риск) → WS-F02-ADMIT-BINDING (2, после Q-F02-01) → WS-F01-DELIVERY-IDENTITY (3, после Q-F01-01/02) → WS-F03-SCOPE-POLICY (4, после Q-F03-01); WS-RV003-AU003-MATERIAL-REVIEW — параллельно (процесс-роль). **F-02 и F-01 не засчитываются друг за друга** (раздельные приёмки, раздельные негативные наборы, разные объекты). Детали: runtime/RS006/planning_RS006.json.

## 4. Негативные наборы

- **F-02: N-F02-1..11** (≥8: narrowed-replay, AB-кандидат, lost-response positive, digest/binding mismatch, review mismatch, narrow-restore, другой principal, legacy, race, no-side-effects, truncated DB) — ожидание + физический факт.
- **F-01: NEG-01..09** (sequential/reversed widening, lost-reply, scope-change-без-доставки, explicit export, revision change, два receiver, legacy, fault gates) — физические факты: строки delivery_acks/observations, sha256 YAML-файлов, target_writes.jsonl.

## 5. Остальные вопросы

- **Q-F03-01**: политика — удаление (не маскирование) значений веток вне гранта в `ClaimItem.applicability`, `excluded_branches`, exclude-событиях; origin_* (O2) не трогаются; никаких маркеров скрытия (exists-oracle); immutable данные не переписываются. Рекомендован фильтр на уровне public_dto (schema), вариант C (тип отсутствия) отклонён.
- **Q-F04-01**: typed absence `NO_SUCH_BRANCH` для granted-but-absent на query/resume/sync_status/sync; out-of-grant остаётся SCOPE_DENIED (неразличимо); штрафные пути: не создавать ветку, не оставлять ложный SYNCED, не показывать TypeError.
- **Q-PL003-01**: подтверждено отсутствие RV003/AU003 (0 артефактов; повторная проверка в этом срезе); контракт ролей: RV003 = независимый REVIEWER материала SEC003+QA003 на текущем digest; AU003 = независимый негативный AUDITOR после RV003, свои новые условия; RV004/AU004/AU005 не засчитываются; вердикты не выдумывать.
- **Q-ORCH-01**: O3 — CONFIRMED-дефект (не наблюдение); O2 provenance легален (цитата REQUIREMENTS.md:145-148); AU005 — не приёмка продукта (product_acceptance=false, AB004 delta REQUEST_CHANGES); UNVERIFIED-остаток — только известные границы среза (live OMH, граф/K1-K3, тайминг).

## 6. Что упустили заказчик/оркестратор

1. Старый PK idempotency делает «повтор после legacy-отказа» невозможным (нужен расширенный PK).
2. Строгое равенство scope_digest ломает законное восстановление при безопасном сужении (арбитр — result_scope ⊆ grant).
3. Публичный view_scope — только digest (список = exists-oracle).
4. F-01 требует смены UNIQUE ключа delivery_acks (несколько проекций на один intent).
5. F-04: явная граница NO_SUCH_BRANCH (granted) vs SCOPE_DENIED (out-of-grant) не была оговорена.
6. Q-F02-02: capability-модель не была оформлена как контракт.
7. F-03: явная politica для списков не была в картах до Q-F03-01.
8. RV003/AU003: контракт ролей отсутствовал в frozen delta (дан в этом срезе).

## 7. Записи

- artifacts/RESEARCHER_RS006_AU005_FIXES.json
- runtime/RS006/: first_artifact.json (PARTIAL), answers_f02/f01/other.json, planning_RS006.json (срезы+негативы+упущено), validate_rs006.py, validation_receipt.json, prototypes/ (rs006_f02_f01_prototype.py, receipt/rs006_prototype_receipt.json sha256 954105cb…, fixture/, target_writes.jsonl), sources/stripe_idempotent.html (sha256 5331a337…; AWS — NOT_SNAPSHOTTED, TLS reset)
- Внешние источники: https://stripe.com/docs/api/idempotent_requests (снапшот 2026-11-08)

Границы соблюдены: продукт/tests/tech_debt/конфиги/живой OMH не тронуты; Git/install/платные/субагенты/секреты/сеть из кода — нет; applied=false.