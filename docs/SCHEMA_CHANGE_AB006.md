# SCHEMA_CHANGE_AB006 — миграция схемы v2 (candidates: `created_at` + join-индексы; pending-секция RS007 W1)

Срез: AB006 (RS007 W1, option A) — pending-секция сервисного уровня (metadata-only,
scope-фильтр, admitted-исключение) + хранилищная поддержка для неё.
Версия кода после миграции: digest `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505`
(поле `digest_discrepancy` в артефакте фиксирует, что ранние числа `3a5f875b…/3f0af9c4…`
не воспроизводятся документированным методом и ошибочны).
Изменённые файлы: `mockup/admission.py`, `mockup/storage.py`, `mockup/public_dto.py`, `mockup/server.py` (ровно четыре, подтверждено диффом против `runtime/AU006/sources/P`).

## 1. Цель

Pending-секции нужны: (а) признак «когда кандидат был создан» без чтения payload
(`created_at`, рождается при admit/submit), (б) быстрые join-предикаты
«есть ли claim/прошёл ли admit» по `claims` и `idempotency` без полного скана.
Миграция аддитивная и идемпотентная; legacy-строки не теряют данные.

## 2. Новая схема (миграция v2; `CANDIDATES_SCHEMA_VERSION = 2`)

```sql
ALTER TABLE candidates ADD COLUMN created_at TEXT;                        -- NULL для legacy-строк
CREATE INDEX IF NOT EXISTS idx_idempotency_candidate ON idempotency(candidate_id);
CREATE INDEX IF NOT EXISTS idx_claims_candidate ON claims(candidate);
```

- `candidates.created_at` — рождается при admit/submit (birthmark); legacy-строки
  остаются `NULL`, `age_seconds` для них в pending-секции **опускается, никогда не 0**.
- Индексы — join-ключи admitted-предиката: `EXISTS(claims.candidate)` и
  `EXISTS(idempotency.candidate_id + operation LIKE 'admit:%')`.
- Триггеры и таблицы — без изменений; idempotency остаётся в layout WS-F02 (AB005).

## 3. Порядок и идемпотентность (в `Store.initialize()`)

1. Проверка обязательных таблиц/колонок → несовместимый legacy → `MIGRATION_REQUIRED`.
2. WS-F02: при отсутствии `scope_digest` у `idempotency` — миграция idempotency v2
   (гейт `user_version < 1`, `BEGIN IMMEDIATE`, rebuild + перенос строк как legacy-inert).
3. `executescript(DDL + DELIVERY_DDL)` + пересоздание immutable/chain-триггеров.
4. **Миграция v2**: если у `candidates` нет `created_at`:
   - гейт: `user_version >= 2` → `MIGRATION_REQUIRED` (монотонный уровень — молчаливая
     перестройка невозможна);
   - `BEGIN IMMEDIATE` → все три стейтмента `MIGRATION_V2_DDL` → commit;
   - защитное пересоздание триггеров (`IF NOT EXISTS` — на случай future table-rebuild).
   Если `created_at` уже есть (свежая БД или повторный запуск) — гарантируются только
   индексы (`MIGRATION_V2_DDL[1:]`, `IF NOT EXISTS`).
5. binding/branch_heads. 6. `PRAGMA user_version = 2`.

**Идемпотентность подтверждена**: `after_first == after_rerun` (user_version 2,
колонки с `created_at`, оба индекса, 39 immutable-триггеров; `checks_summary.json['migration']`,
rerun status OK).

## 4. Триггеры и индексы (физически, read-only проверка на `fixtures/w1/dom.sqlite3`)

- 39 immutable-триггеров = 3 (UPDATE/DELETE/INSERT) на каждую из 13 таблиц:
  10 в `IMMUTABLE` (`binding, candidates, claims, claim_snapshots, events, reviews,
  transactions, idempotency, outbox, delivery_events`) + delivery `attempts/observations/acks`.
- Всего 44 триггера: +5 не-immutable (`attempt_binding`, `observation_binding`,
  `ack_binding`, `legacy_ack_refused`, `chain_previous_hash` — chain-гард событий).
- Индексы: `idx_idempotency_candidate (idempotency.candidate_id)`,
  `idx_claims_candidate (claims.candidate)`.
- Обновлённая БД: `user_version = 2`, колонки `candidates`: `id, digest, payload, author, root, branch, created_at`.

## 5. Новые поля/статусы pending-секции (`admission._pending_page`)

Элемент `items[]` (metadata-only, тело никогда не отдаётся):

```text
candidate_id, intent_digest, state, branch, operation,
origin {author, root}, dependencies, expected_branch_revision,
payload_length, idempotency_key, review_id, age_seconds (только если created_at есть)
```

- `state` — выводится без LLM: `AWAITING_REVIEW` / после review `REVIEWED`, либо
  `REJECTED` (последний review `decision != 'approve'`).
- Контейнер: `status` ∈ {`PENDING_PRESENT`, `NO_PENDING`}; `count` — точный и
  scope-фильтрованный (отдельный pass — анти-exists-oracle); `has_more` —
  предфильтровый эвристик `limit+1`; `page {after, limit}` (keyset по `(branch, id)`).
- Правило видимости: `candidate.branch ∈ grant` И `set(dependencies) ⊆ grant`; иначе
  элемент скрыт полностью (без маркера). Admitted-предикат
  (`EXISTS claims.candidate` ИЛИ admit-строка idempotency) исключает завершённые кандидаты.

## 6. Коды

- `MIGRATION_REQUIRED` — typed отказ (`MigrationRequired`) на несовместимом legacy:
  отсутствуют обязательные таблицы/колонки, либо уровень `user_version >= 2` без
  `created_at` (никогда не молчаливая перестройка).
- `NO_PENDING` / `PENDING_PRESENT` — статусы pending-контейнера.
- Существующие коды admit-пути (DEMO_ADMITTED, REVISION_CONFLICT, SCOPE_DENIED и т.д.)
  не менялись.

## 7. Физическое подтверждение

- `fixtures/legacy-src/dom.sqlite3` → мигрировано: uv=2, `created_at`, оба индекса;
  `legacy-null/dom.sqlite3` — legacy-кандидат без `created_at` → `age_seconds` отсутствует.
- `fixtures/w1|w1_pos|w3/dom.sqlite3` — рабочие БД, uv=2 (read-only PRAGMA проверен).
- `results/checks_summary.json` — migration (idempotent), perf (индексы в границе 10×:
  p100k 1504.6 мс против 15901.5 мс без индексов, ≈10.57×; p1k 14.4 мс), pos/neg матрица.
- `results/frames_full.jsonl` (4 pending), `results/frames_empty.jsonl` (`NO_PENDING`) —
  реальные MCP-кадры.

## 8. Известное поведение контракта (не дефект)

При сужении гранта `has_more` (предфильтровый `limit+1`) может обещать больше, чем
вернёт страница (измерено: `count=2, items=0, has_more=true`); `count` при этом точен.
Клиент листает по `has_more`.

## 9. Вне scope

`tests/`, OMH, конфиги, live-сеть/Git — не менялись (см. границы карты AB006).
