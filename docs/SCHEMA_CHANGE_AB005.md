# SCHEMA_CHANGE_AB005 — миграция `idempotency` v2 (WS-F02-ADMIT-BINDING)

Срез: WS-F02-ADMIT-BINDING (AU005-F-02, финальная форма RS006 + поправки оркестратора).
Версия кода после миграции: digest `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7`.
Единственная мигрируемая таблица: `idempotency`. Остальные таблицы и их immutable-триггеры не затронуты.

## 1. Цель

Кеш идемпотентности обязан привязываться к ОДНОЙ операции (кандидат, ветка, review, область результата)
и выдавать квитанцию только при полном совпадении binding + `result_scope ⊆ grant`.
Старый PK `(external_work_ref, operation, key)` не хранил привязку и делал невозможным законный повтор
после legacy-отказа (remember() упал бы в UNIQUE/IMMUTABLE).

## 2. Новая схема

```sql
CREATE TABLE idempotency(
  external_work_ref TEXT NOT NULL,
  operation        TEXT NOT NULL,
  key              TEXT NOT NULL,
  scope_digest     TEXT NOT NULL DEFAULT '',   -- sha256(sorted(launch-grant)); '' для legacy
  digest           TEXT NOT NULL,
  result           BLOB NOT NULL,
  candidate_id     TEXT,                       -- NULL только у legacy (pre-migration) строк
  review_id        TEXT,
  branch           TEXT,
  result_scope     TEXT,                       -- JSON-массив sorted({branch} ∪ dependencies)
  PRIMARY KEY(external_work_ref, operation, key, scope_digest)
);
```

Колонки с привязкой: `candidate_id, review_id, branch, scope_digest, result_scope`.

## 3. Миграционная процедура (выполняется в `Store.initialize()`)

1. **user_version-гейт**: `PRAGMA user_version` (0 = старая/непомеченная схема; `IDEMPOTENCY_SCHEMA_VERSION=1` = v2).
   - Старая схема + `user_version >= 1` → `MIGRATION_REQUIRED` (честный отказ, без тихой перестройки).
   - Старая схема + `user_version = 0` → миграция (ниже).
2. **Пересоздание таблицы** в одной `BEGIN IMMEDIATE`-транзакции:
   - `CREATE TABLE idempotency_v2(...)` (схема выше);
   - `INSERT INTO idempotency_v2(work,op,key,scope_digest,digest,result)
     SELECT work,op,key,'',digest,result FROM idempotency` — legacy-строки копируются **как есть**:
     `scope_digest=''`, `candidate_id/review_id/branch/result_scope = NULL`;
   - `DROP TABLE idempotency;` (с нею падают её immutable-триггеры);
   - `ALTER TABLE idempotency_v2 RENAME TO idempotency;`
   - `PRAGMA user_version = 1`.
3. **Пересоздание immutable-триггеров** по новому набору PK-колонок: общий цикл `initialize()` строит
   `immutable_idempotency_{UPDATE,DELETE,INSERT}` на `(external_work_ref, operation, key, scope_digest)`
   (включая R2-1-защиту от INSERT OR REPLACE/IGNORE).
4. Свежие БД создаются сразу в v2 (`CREATE TABLE IF NOT EXISTS`) и помечаются `user_version=1`.

Независимо от `dom_init`, обращение к старой схеме без миграции закрыто fail-closed:
`SELECT ... scope_digest` → `MIGRATION_REQUIRED` через `storage_error`.

## 4. Семантика legacy-строк (после миграции)

- Читаемы и верифицируемы: `digest` и `result` сохранены дословно.
- **Не обслуживаются**: любое обращение по их ключу → `IDEMPOTENCY_BINDING_UNKNOWN` (typed DomainError,
  без деталей, без раскрытия «чьей» это строки).
- **Не переписываются и не удаляются** (immutable-триггеры; `UPDATE` физически отвергнут — проверено).
- Не блокируют новые операции: расширенный PK гарантирует, что legacy (`scope_digest=''`) никогда не
  совпадает с реальным digest гранта, поэтому новый admit/submit с тем же ключом пишет собственную строку.

## 5. Инварианты

- Кеш-хит возвращает квитанцию ТОЛЬКО при: кандидат ≡ binding, review_id ≡ binding, digest ≡ intent,
  `result_scope ⊆ текущий grant`. Иначе — типизированный отказ (ниже).
- Повтор (потерянный ответ) не создаёт новых фактов: tx/events/outbox/delivery_* и строк idempotency не растут.
- Новые коды отказов (DomainError `{status}`, без payload): `DIGEST_MISMATCH` (L1, до кеша),
  `IDEMPOTENCY_MISMATCH` (defense-in-depth), `IDEMPOTENCY_BINDING_MISMATCH`, `IDEMPOTENCY_BINDING_UNKNOWN` (legacy),
  `IDEMPOTENCY_REVIEW_MISMATCH`, `SCOPE_DENIED` (candidate вне гранта / result_scope ⊄ grant).

## 6. Invariant: определение области

- `scope_digest = sha256(canonical(sorted(launch-grant)))` (канонизация как в `dom_contract.digest`).
- `result_scope = sorted({payload.branch} ∪ set(payload.dependencies))`.
- Арбитр при выдаче — `result_scope ⊆ grant`, а не равенство `scope_digest`: безопасное сужение гранта
  (кандидат и его deps остаются видимы) не ломает восстановление после потерянного ответа.

## 7. Физическое подтверждение (runtime/AB005)

- `fixtures/f02/after/legacy-src/dom.sqlite3` — копия БД со старой схемой (DDL дословно в `runtime/AB005/legacy.py`).
- `fixtures/f02/after/legacy-migrated/dom.sqlite3` — результат миграции на копии:
  колонки v2 (`candidate_id, review_id, branch, scope_digest, result_scope`), `user_version=1`,
  legacy-строка `scope_digest=''`/`candidate_id=NULL`/digest сохранён; `UPDATE` → `IMMUTABLE`;
  `legacy-key` → `IDEMPOTENCY_BINDING_UNKNOWN`; новый ключ → `DEMO_ADMITTED`.
- Полная матрица N-F02-1..11 + позитивный контроль N-F02-3: `results/f02_after.json`.

## 8. Где миграция НЕ выполняется

- `tests/`, `delivery.py`, OMH, конфиги — вне scope этого среза (см. карту AB005 и границы).
