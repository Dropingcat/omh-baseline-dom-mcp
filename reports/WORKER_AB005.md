# WORKER AB005 — WS-F04 (типизированное отсутствие) + WS-F02 (L1+L2 в admit)

Роль: WORKER. Статус: **COMPLETED**. `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]` (долги не закрыты, TD19 — только после независимых reviewer+auditor).
Приёмка срезов **раздельная**. Физическое evidence: `runtime/AB005/**` (results JSON, raw MCP frames, изолированные SQLite-БД сценариев, миграционный фикстур на копии).

Digest кода (posix relpath method, 16 файлов):
- базовый: `1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf`
- после F-04: `7615365ed77930f8fe6807b3dde65ba4f1e9c6ee84a73f3038206bdd482e49d7`
- финальный (после F-02): `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7`

---

## Срез 1: WS-F04-TYPED-ABSENCE — статус PASS

Находка AU005-F-04: granted-but-absent ветка (грант `{AA,ZZ}`, ZZ отсутствует) давала
`INTERNAL_ERROR` (query/resume/export/trace), пустой `SYNC_STATUS` и ложный `SYNCED` (sync).

До (f04_before.json): query/resume/export/trace `ZZ=INTERNAL_ERROR`, sync_status `ZZ=SYNC_STATUS(пустой)`, sync `ZZ=SYNCED`; `AB=SCOPE_DENIED`; AA здоров.

После (f04_after.json, тот же грант, те же вызовы, тот же фикстур):
- `query/resume/sync_status/sync/trace/export ZZ = NO_SUCH_BRANCH` — единый типизированный статус на всех поверхностях;
- `AB = SCOPE_DENIED` (неразличимое существование сохранено);
- AA без изменений: `DEMO_ADMITTED/SNAPSHOT/RESUMED/SYNC_STATUS/SYNCED/EXPORTED`;
- `INTERNAL_ERROR` отсутствует; `sync.ZZ != SYNCED`; `trace(master)` при неполном гранте не ломается.

**Реализация** (write_scope: `mockup/admission.py`): единая физическая точка — `Service.head()` (и хелпер `require_branch()`) проверяет `branch_heads` до любых read-операций и бросает `Denied('NO_SUCH_BRANCH')`; `sync_status`/`sync` получили явный `require_branch` (не идут через `head`). `server.py` не потребовался: `guarded` → `{'status': ...}` → `project_tool` уже сериализует как `DomainError {status}` без деталей.

Негативный набор: ZZ-в-гранте ≠ ZZ-вне-гранта (нет widening и нет exists-oracle вне гранта); никаких raw-исключений; нет ложного SYNCED.

## Срез 2: WS-F02-ADMIT-BINDING — статус PASS

**Воспроизведение дефекта** (f02_before.json, до фикса, реальные кадры 3 PID: submit 12436, review 11356, attack 4940):
AB-допуск при полном гранте, затем грант `{AA}`, AA-кандидат + прежние AB `adm-prior`+`intent_digest` →
`DEMO_ADMITTED` c `branch=AB` — кешированная AB-квитанция выдана чужой операции (0 новых фактов, transactions=1).

**Обе поправки RS006 к предложению оркестратора применены:**
1. PK `idempotency` расширен до `(external_work_ref, operation, key, scope_digest)` — законный повтор после legacy-отказа возможен (новая строка с реальным scope_digest не конфликтует с legacy `scope_digest=''`);
2. арбитр выдачи — `result_scope ⊆ grant`, а не строгое равенство `scope_digest` (безопасное сужение не ломает восстановление).

**Порядок admit:** `candidate()` (scope, result_scope) → **L1**: `row['digest']/digest(p) != intent_digest → DIGEST_MISMATCH ДО кеша** → **L2** `dedupe(work, op, key, binding)` → review/STALE-проверки → `remember` с binding `(candidate_id, review_id, branch, scope_digest, result_scope={branch}∪deps)`. Коды: `DIGEST_MISMATCH`, `IDEMPOTENCY_MISMATCH` (defense-in-depth, сохранён), `IDEMPOTENCY_BINDING_MISMATCH`, `IDEMPOTENCY_BINDING_UNKNOWN` (legacy), `IDEMPOTENCY_REVIEW_MISMATCH`, `SCOPE_DENIED`. Submit-строки тоже привязаны (scope_digest+result_scope+кандидат); legacy submit-строки — тот же `IDEMPOTENCY_BINDING_UNKNOWN`.

**Миграция** (`mockup/storage.py`, только idempotency): `user_version`-гейт (0→1), пересоздание таблицы (CREATE v2 → COPY legacy как есть: `scope_digest=''`, binding NULL → DROP → RENAME) в одной `BEGIN IMMEDIATE`, пересоздание immutable-триггеров по новому PK, честный отказ на несостоятельном состоянии (старая схема + user_version≥1 → `MIGRATION_REQUIRED`). Разрушительно — только на копии `runtime/AB005/fixtures/f02/after/legacy-migrated/dom.sqlite3` (старая схема дословно из `runtime/AB005/legacy.py`).

### Негативный набор и позитивный контроль (физические)

| # | Сценарий | Результат |
|---|---|---|
| **N-F02-3** | потерянный ответ: тот же (кандидат, ключ, digest, review, грант) | та же квитанция (byte-equality текста кадра и parsed), **0 новых** tx/events/outbox/attempts/acks/idempotency; idempotency остаётся 2 строки (submit+admit), admit-строка 1 |
| N-F02-1 | AA-кандидат + прежние AB key/digest | `DIGEST_MISMATCH` **до кеша**, квитанции нет; 3 PID raw frames |
| N-F02-2 | реальный AB-кандидат при гранте AA | `SCOPE_DENIED` (candidate() до кеша) |
| N-F02-4 | тот же ключ, другой digest; чужой кандидат с РАВНЫМ digest | `DIGEST_MISMATCH` (L1) / `IDEMPOTENCY_BINDING_MISMATCH`; 0 новых фактов |
| N-F02-5 | mismatched review_id | `IDEMPOTENCY_REVIEW_MISMATCH` |
| N-F02-6 | безопасное сужение → повтор; опасное сужение (AB-dep) → ; восстановление гранта → | повтор OK (0 фактов) / `SCOPE_DENIED` / повтор OK |
| N-F02-7 | другой principal, тот же ключ | 2 независимые operation-строки (`admit:demo-reviewer`, `admit:readerQ`); не переиспользуется |
| N-F02-8 | legacy-строка (миграционный фикстур на копии) | `IDEMPOTENCY_BINDING_UNKNOWN`; строка цела (candidate_id=NULL, scope_digest='', digest сохранён), не переписана; новый ключ → `DEMO_ADMITTED`; immutable-триггер пересоздан (UPDATE→`IMMUTABLE`); user_version=1; колонки v2 |
| N-F02-9 | race: один ключ, два кандидата (идентичные digest) | детерминированно: 1×`DEMO_ADMITTED`, 2-й `IDEMPOTENCY_BINDING_MISMATCH`, 1 строка ключа |
| N-F02-10 | replay не создаёт побочных эффектов | outbox/attempts/acks/facts не растут (дельты 0 по всем таблицам) |
| N-F02-11 | кандидат отсутствует между submit и admit | честный `SCOPE_DENIED` (когда БД инициализирована) / `NOT_INITIALIZED` (когда БД нет), кеш не задет |

## Что изменено
- `mockup/admission.py` — WS-F04: `head()`/`require_branch()` (NO_SUCH_BRANCH), явная проверка в `sync_status`/`sync`; WS-F02: порядок admit (L1 до кеша), `dedupe`/`remember` с binding, `scope_digest()`, submit-binding.
- `mockup/storage.py` — только миграция idempotency: PK `(work,operation,key,scope_digest)`, колонки `candidate_id/review_id/branch/scope_digest/result_scope`, `IDEMPOTENCY_SCHEMA_VERSION=1`, `_migrate_idempotency()` в `initialize()` (user_version-гейт), `IMMUTABLE_KEYS` и DDL.
- `runtime/AB005/**` — пробы, лаунчер, фикстуры, кадры, результаты.
- НЕ тронуты: `delivery.py`, `public_dto.py`, `server.py`, tests, tech_debt, OMH, конфиги. F-01/F-03 не выполнялись (раздельная приёмка). `p_f04.py after` повторно прогнан на финальном digest — PASS (нет регрессии среза 1 от среза 2).

## Границы / not_checked
- Истинно конкурентная гонка двух процессов не гонялась (модель — сериализация `BEGIN IMMEDIATE`, как в продукте; рекомендация RS006 по live-гонке сохранена).
- Полный pytest не запускался: tests вне write_scope (базовый набор 18 тестов не изменён).
- Live OMH/сеть/Git — запрещены картой, не вызывались.
- `REPLAY` как строка статуса не вводился: продукт возвращает кешированную квитанцию (исходный статус `DEMO_ADMITTED`), что соответствует требованию «та же квитанция, 0 новых фактов»; внутренняя метка прототипа осталась в прототипе.
