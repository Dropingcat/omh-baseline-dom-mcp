# Архитектурный анализ аудита 2026-11-11

**Статус:** анализ + зафиксированные решения; реализация не начата.
**Источник:** `docs/audit/2026-11-11_ARCHITECTURE_AUDIT.txt` (3 619 строк, sha256 `AF0991CE...`), `docs/audit/2026-11-11_QUESTIONS_AND_ANSWERS.md` (ответы заказчика от 2026-11-11).
**Метод:** проверка утверждений аудита по коду, а не пересказ. Ссылки на файлы и строки — в тексте.
**Связанные документы:** `REQUIREMENTS.md §2`, `tech_debt.md`, `docs/STATUS.md`, `docs/TD22_CLAIM_ENTRY_UNIFICATION_PLAN.md`.

---

## 0. Краткий вывод

Аудит вырос из каталога рисков в продуктовый проект. Из ~35 пунктов **немедленно actionable только три доказанных дефекта**:

1. двойная `verify_chain` в `trace`/`resume` (`query=1`, `trace=2`, `resume=2`);
2. read-транзакция вокруг внешнего I/O в `sync` (блокирует писателей при `journal_mode=DELETE`);
3. ручной реестр `TOOLS` / `SIGNATURE` / `dispatch` (routing drift).

Остальное — либо новые подсистемы (проекция плана, recall, diff, drift, fork, оркестратор), либо фичи, требующие продуктовых решений. Предлагаемый порядок: **P0** (дефекты) → **P1** (version/baseline/recall) → **P2** (проекция плана) → **P3** (diff/drift/fork) → **P4** (оркестратор) → **P5** (live-порты, Merkle, fault tolerance).

Главный риск аудита: он предлагает **второй источник истины** (колонки `version`/`supersedes`, таблица `baseline`, триггеры, `plan_tasks` как сущность DOM). Ответ заказчика от 2026-11-11 снимает этот риск: DOM — проекция OMH, version/logical_claim_id — производные, baseline — view.

---

## 1. Зафиксированные решения

### D1. DOM — проекция OMH

**Решение:** DOM не владеет планированием и статусами задач. `plan_tasks` и `task_claims` — **read-only проекция/кэш** плана OMH с полями `source='OMH'`, `synced_at`, `stale`. Любая запись статуса в DOM запрещена; статус приходит только из OMH.

**Следствия:**
- `REQUIREMENTS.md §2` не меняется по существу; добавляется уточнение о проекции (см. §1.2).
- `dom_plan_tree`/`dom_task_claims` возвращают `stale` и `synced_at`; при `require_fresh=true` и устаревшей проекции — `PLAN_PROJECTION_STALE`, иначе кэш + предупреждение.
- Домен «задача плана» не дублируется: `plan_tasks` — указатель на OMH-задачу + ссылка на клайм-решение.
- Формирование клаймов по чекпоинтам — зона **внутреннего** оркестратора DOM (D6), но результат проходит тот же путь candidate → review → admit, что и ручной ввод.

**Источник ответа:** `docs/audit/2026-11-11_QUESTIONS_AND_ANSWERS.md` Q1, Q40; ответ 2026-11-11: «DOM это проекция OMH».

### D1.1. Версии пунктов плана и защита от переобновления

**Проблема.** Если ключ проекции — `path`, то переименование/перемещение задачи ломает `task_claims`; если синхронизация переписывает все строки, каждый poll создаёт «переобновление»: новые версии, новые `synced_at`, ложную `stale` и потерю локальных связей.

**Модель:**
- **Идентичность** — `plan_task_id` из OMH (стабильный), а не `path`. `path` — изменяемый атрибут.
- **История** — `plan_task_versions` (append-only): `(plan_task_id, version)`; `version` растёт на любое изменение проекции, включая статус.
- **Текущее состояние** — view `current_plan_tasks` (max version), не отдельная мутируемая таблица.
- **Связи** — `task_claims(plan_task_id, claim_id, role)`: DOM-owned; синхронизация плана их **не трогает**.
- **Семантический отпечаток** — `semantic_digest` (title, description, acceptance_criteria, task_type, required_roles, parent_id). `link_stale` считается по нему, а не по номеру версии: смена статуса не инвалидирует связь, смена смысла — инвалидирует. Список семантических полей — конфигурируемый; `status`, `priority`, `assignee`, `observed_at` в него не входят.

**Единственный писатель статуса** — `project_plan_snapshot`: он копирует статус из OMH-снимка; публичного API «поставить статус» в DOM нет.

**Схема:**
```sql
CREATE TABLE plan_tasks(              -- identity, stable
  plan_task_id TEXT PRIMARY KEY,
  source TEXT NOT NULL CHECK(source='OMH'),
  external_ref TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE plan_task_versions(      -- append-only projection history
  plan_task_id TEXT NOT NULL REFERENCES plan_tasks(plan_task_id),
  version INTEGER NOT NULL,
  path TEXT NOT NULL,
  parent_id TEXT,
  status TEXT NOT NULL,
  title TEXT NOT NULL,
  task_type TEXT,
  source_revision TEXT NOT NULL,
  digest TEXT NOT NULL,
  semantic_digest TEXT NOT NULL,
  archived INTEGER NOT NULL DEFAULT 0,
  observed_at TEXT NOT NULL,
  PRIMARY KEY(plan_task_id, version)
);
CREATE VIEW current_plan_tasks AS
SELECT t.plan_task_id, t.source, t.external_ref, t.created_at, v.archived,
       v.version, v.path, v.parent_id, v.status, v.title, v.task_type,
       v.source_revision, v.digest, v.semantic_digest, v.observed_at
FROM plan_tasks t
JOIN plan_task_versions v ON v.plan_task_id = t.plan_task_id
 AND v.version = (SELECT MAX(version) FROM plan_task_versions
                  WHERE plan_task_id = t.plan_task_id);
CREATE TABLE task_claims(
  plan_task_id TEXT NOT NULL REFERENCES plan_tasks(plan_task_id),
  claim_id TEXT NOT NULL REFERENCES claims(id),
  role TEXT NOT NULL CHECK(role IN ('justifies','implements','validates','documents','depends_on')),
  linked_at_plan_version INTEGER NOT NULL,
  linked_semantic_digest TEXT NOT NULL,
  linked_at TEXT NOT NULL,
  PRIMARY KEY(plan_task_id, claim_id, role)
);
CREATE TABLE plan_projection_state(
  source TEXT PRIMARY KEY CHECK(source='OMH'),
  source_revision TEXT,
  last_checked_at TEXT NOT NULL,
  last_changed_at TEXT,
  snapshot_digest TEXT
);
```

`plan_task_versions` — append-only: `BEFORE UPDATE/DELETE` триггеры → `IMMUTABLE`. `task_claims` — единственная таблица, которую DOM меняет при relink; синхронизация плана её не касается.

**Алгоритм `project_plan_snapshot(snapshot, mode='full'|'partial')`:**
1. Валидация: уникальные `plan_task_id`, parent существует, нет циклов, `source_revision` не старше текущей.
2. `BEGIN IMMEDIATE`.
3. Для каждого пункта:
   - `digest` = canonical JSON **содержательных** полей (path, parent_id, status, title, task_type, ...), **без** `source_revision`/`observed_at`/`synced_at`; `semantic_digest` = canonical JSON семантических (title, description, acceptance_criteria, task_type, required_roles, parent_id), **без** status и метаданных синхронизации.
   - нет в `plan_tasks` → insert identity + version 1.
   - есть, `digest` совпал → **skip** (никаких записей, `observed_at` не меняется).
   - есть, `digest` изменился → insert version `current+1`; `plan_tasks` не переписывается.
   - есть, отсутствует в `full` snapshot → insert version `current+1` с `archived=1` (не delete); при повторном появлении — новая версия с `archived=0`.
4. `plan_projection_state.last_checked_at` обновляется всегда; `last_changed_at` — только если были изменения.
5. `COMMIT`.
6. Идемпотентность: `(source, source_revision)`; повтор → `ALREADY_PROJECTED` без записей.

**Правила против переобновления:**
- не переписывать всю таблицу; только изменённые пункты;
- `digest` не включает метаданные синхронизации; иначе каждый poll = новая версия;
- `observed_at` не двигать, если `digest` не изменился;
- `stale` = `source_revision` отстаёт или `now - last_checked_at > ttl`, а не «пункт обновлён»;
- `task_claims` не трогать при синхронизации плана;
- `link_stale` — по `semantic_digest`, не по `version`;
- архив вместо удаления;
- отклонять старый `source_revision` (`STALE_PROJECTION_SNAPSHOT`).

**Крайние случаи:**
- **Переименование/перемещение:** тот же `plan_task_id`, новая `path`/`parent_id`; версия растёт; ссылки остаются; `link_stale` — только если изменился `semantic_digest` (например, parent).
- **Статус:** новая версия, `semantic_digest` тот же → `link_stale=false`.
- **Удаление:** `archived=1`; ссылки остаются, `plan_archived=true`.
- **Split/merge:** новые `plan_task_id`; старые archived; ссылки **не копируются автоматически** — `ORPHANED_LINKS`, требуется явный relink.
- **Тот же path, новый `plan_task_id`:** новая задача; старую в архив; ссылки не переиспользовать.
- **OMH без стабильного ID:** DOM вводит surrogate `plan_task_id` + `external_ref`; path-изменение без ID трактуется как новая задача (документированное ограничение).

**Тесты:** идемпотентный повтор; status-only → `link_stale=false`; title → `link_stale=true`; rename → links intact; delete → archived; old revision → отказ; split/merge → orphaned; concurrent sync → без дублей; append-only `plan_task_versions` (no UPDATE/DELETE).

### D2. `version` / `logical_claim_id` — производные

**Решение:** не вводить колонки. Оба значения выводятся из цепочки replacement-событий:
- `logical_claim_id` = корень цепочки (`_lineage(...)[0]`);
- `version` = глубина цепочки (`_lineage(...)[1]`).

**Почему не колонки:**
- текущий `dom_update` создаёт новый claim **до** replacement-события (`claim_entry.py:462-482`), поэтому при вставке родитель неизвестен;
- колонка + `_lineage` = два источника истины, которые разойдутся;
- триггер на `claims` не может восстановить родителя без изменения контракта.

**Следствия:**
- `version`, `logical_claim_id`, `supersedes` отдаются в DTO `dom_find`, `dom_task_claims`, `dom_recall`, `dom_update`;
- миграция не нужна;
- если позже понадобится O(1), вводится пакет `replace` с `supersedes` при вставке и consistency-тест против `_lineage`. Это отдельное решение, не текущее.

**Источник ответа:** `docs/audit/2026-11-11_QUESTIONS_AND_ANSWERS.md` Q41–Q42 (там был вариант «новая колонка»); ответ 2026-11-11: «производные». Последний ответ имеет приоритет.

### D3. Базлайн — view

**Решение:** базлайн — **SQL-view** над `events`, а не таблица с триггером.

```sql
CREATE VIEW baseline_view AS
SELECT branch,
       ROW_NUMBER() OVER (PARTITION BY branch ORDER BY seq) AS seq,
       claim_id,
       ROW_NUMBER() OVER (PARTITION BY branch ORDER BY seq) - 1 AS prev_seq,
       event_hash AS chunk_hash,
       revision
FROM events
WHERE kind = 'claim';
```

**Почему:**
- `events` уже содержит порядок и `event_hash`; таблица дублирует истину;
- предложенный аудитом триггер `claims_after_insert` не может заполнить `dependencies`/`review_id` (они из envelope, а не из `claims.payload`) и дублирует существующий INSERT в `claim_snapshots`;
- `chunk_hash` через `randomblob` — не хеш; используем `event_hash`.

**Материализация** — только после benchmark (`EXPLAIN QUERY PLAN` + замер на целевом N), с `rebuild_baseline()` и property-тестом эквивалентности view.

**Источник ответа:** ответ 2026-11-11: «Базлайн view».

### D4. `commit_ref` — опциональный

**Решение:** `commit_ref` добавляется в `TYPE_FIELDS['code']` как **опциональное** поле.

**Форма:**
```json
{"hash": "<40|64 hex>", "branch": "feature/TD-BASE-01", "author": "...", "message": "...", "committed_at": "2026-11-11T18:00:00Z"}
```

**Почему нужен `OPTIONAL_FIELDS`:** `dom_contract.fields()` требует **все** ключи из `TYPE_FIELDS` (`dom_contract.py:66-71`); просто добавить `commit_ref` в `TYPE_FIELDS['code']` нельзя — сломаются существующие code-клаймы без коммита.

**Валидация:** hash — 40 hex (SHA-1) или 64 hex (SHA-256); branch непустой; unknown keys reject; no coercion.

**Источник ответа:** ответ 2026-11-11: «commit_ref — опциональный да».

### D5. Drift — явная миссия, extra отдельно

**Решение:** drift считается только по явной миссии:
```json
{"mission_claim_id": "...",
 "expected": [{"task_path": "П1.1.2", "role": "implements", "content_type": "code"}],
 "constraints": [{"all_of": [{"task_path": "П1.1.2", "role": "implements"}]}],
 "threshold": 0.3}
```

**Формула:**
- `missing = expected − current`;
- `changed = expected`, у которых текущий `raw_sha256` ≠ ожидаемого;
- `extra = current − expected` — **отдельно**, по умолчанию вес 0 (не штрафуем легитимную новую работу);
- `score = (|missing| + |changed|) / |expected|`;
- `|expected| = 0` → `drift_score = null`, `undefined = true`, рекомендация `realign` (без деления на ноль);
- порог конфигурируемый, дефолт 0.3, не хардкод 0.7.

**Constraints:** типизированный JSON-DSL (`all_of`, `any_of`, `none_of`), детерминированный вычислитель, без `eval`. Полный синтаксис — отдельное решение (см. §8).

**Источник ответа:** ответ 2026-11-11: «явный набор expected + constraints; extra в score — на твоё усмотрение». Выбрано: extra вне score по умолчанию.

### D6. Два оркестратора

**Решение:** разделять два уровня, а не выбирать «harness или MCP».

| Уровень | Где | Ответственность | Не делает |
|---|---|---|---|
| **Внешний** (Hermes-агент) | harness | NL → выбор инструментов, диспатч MCP, диалоговая сессия, планирование верхнего уровня | не пишет ledger напрямую; не владеет доменными инвариантами |
| **Внутренний** (DOM MCP) | `mockup/` | детерминированная доменная оркестрация: дедуп, полнота, фильтрация чекпоинтов, формирование клаймов из плана, контекст сессии | не интерпретирует свободный NL; не заменяет OMH-планировщик |

**Контракт:** внешний агент вызывает `dom_start`/`dom_claim`/`dom_submit`/`dom_task_claims`/`dom_recall`; внутренний слой гарантирует инварианты и возвращает `next_steps`. Общее состояние — только ledger (DOM) и план (OMH).

**LLM внутри MCP:** если нужен фильтр по чекпоинтам, он живёт за портом `IClaimExtractionPort`:
- вход — чекпоинт плана + контекст;
- выход — **кандидат** клайма с `provenance` (`model`, `prompt_digest`, `checkpoint_ref`);
- кандидат проходит обычный review/admit; прямой записи в ledger нет;
- детерминированный fallback (ручной/шаблонный) обязателен;
- модель и ключ — конфигурация, не хардкод.

**Источник ответа:** `docs/audit/2026-11-11_QUESTIONS_AND_ANSWERS.md` Q49 + ответ 2026-11-11: «разделял бы оркестраторов — агента внутри Гермеса, который диспатчит MCP, и агента внутри MCP».

### 1.1. Дополнительные ответы из `docs/audit/2026-11-11_QUESTIONS_AND_ANSWERS.md`

| Вопрос | Ответ | Влияние |
|---|---|---|
| Q7 | «нужно готовить нормальные рабочие сшивки» | live-порты — цель P5, не отменяются |
| Q9 | обратная совместимость v1/v2/v3 + append-only — да | миграции только additive; DOWN не удаляет данные |
| Q10 | ADR на каждый пункт + план + тесты | каждый P0/P1-пункт = ADR + тест |
| Q12 | инвариант + helper пока достаточно | DB-level enforcement для ARCH-01 отложен |
| Q13 | денормализация `dependencies`/`review_id` разрешена | возможна, но не в первой итерации |
| Q21 | двойную `verify_chain` убираем | P0.1 |
| Q22 | Merkle — сейчас | P5, после P0 |
| Q26 | retry, иначе журнал + сигнализация | P5 |
| Q27 | lease/locked_by не нужен | outbox без lease |
| Q30 | `_migrate_vN + ledger` | без alembic |
| Q31 | DOWN-миграции — да | при append-only только обратимые схемные шаги |
| Q35 | таблица-реестр | без декоратора |
| Q36 | строгая валидация подтверждена | no coercion/defaults, unknown keys reject |
| Q38 | pydantic разрешён; drift-тест TOOL↔handler↔signature↔doc — да | P0.3 |
| Q62 | порядок P0 подтверждён | см. §7 |

### 1.2. Уточнение границы в `REQUIREMENTS.md §2`

Добавляется абзац:

> DOM хранит **проекцию** плана OMH (read-only cache с `source`, `synced_at`, `stale`), а не собственную иерархию задач. Статусы, приоритеты и назначения остаются в OMH; DOM отображает их и связывает с клаймами. Запись статуса в DOM запрещена.

Это не меняет границу, а фиксирует способ сшивки.

---

## 2. Дельта-анализ аудита

### 2.1. Что действительно дефект (P0)

| Пункт | Доказательство | Действие |
|---|---|---|
| Двойная `verify_chain` | `admission.py:346-368`, `514-534`; замер `runtime/tmp/audit_verify_chain.py`: `trace=2`, `resume=2` | один вызов на запрос, передавать `chain` в `_trace` |
| `sync` держит read-tx во время I/O | `admission.py:457-497`; `journal_mode=DELETE`, `busy_timeout=2000` | вынести I/O из tx; re-check head перед ack |
| Ручной реестр | `server.py:42-140`, `152-167`, `209-249` | единый реестр + drift-тест |
| Нет инварианта claim↔snapshot | `admission.py:290-294` | SQL-инвариант + helper |

### 2.2. Что фича, а не долг

| Пункт | Вердикт |
|---|---|
| BASE-01 базлайн | view, не таблица (D3) |
| BASE-02 recall | replay до seq; реализуемо |
| BASE-03 diff | выравнивание по `logical_claim_id`; реализуемо |
| VER-01 version | производные (D2) |
| VER-02 commit_ref | опциональное поле (D4) |
| DRIFT-01 | явная миссия (D5) |
| FORK-01 | после P1; атомарная транзакция |
| TASK-TYPE-01 | шаблоны выводить из `TYPE_FIELDS`, не хранить копию |
| ORCH-01..03 | два оркестратора (D6) |

### 2.3. Что конфликтует с границей

| Пункт | Конфликт | Решение |
|---|---|---|
| `plan_tasks`/`task_claims` как сущности DOM | `REQUIREMENTS §2` | проекция/кэш OMH (D1) |
| `implementation_status`, `next_action`, `task_blockers`, `task_dependencies` | состояние исполнения плана — OMH | не хранить в DOM или только как projection |
| Автономные исполнители/канбан | запрещены §2 | вне scope |

### 2.4. Что нереализуемо в предложенном виде

См. §5 — 18 конкретных исправлений макетов аудита.

---

## 3. Образцы поведения (reference behavior)

Ниже — сценарии «как должно быть». Они исправляют примеры аудита там, где те противоречат текущему коду.

### OB-1. Обновление клайма и версия

**Дано:** клайм `A` (v1) в ветке `AA`, текущая ревизия 6.
**Когда:** `dom_update(claim_id="A", text="...", reason="...")`.
**Тогда:**
```json
{"status": "CLAIM_UPDATED", "new_claim_id": "B", "supersedes": "A",
 "record_id": "A", "version": 2, "branch": "AA", "revision": 7}
```
**Инварианты:**
- `A` помечен `replacement`-событием → `archived=true`; `B` — текущий.
- `dom_find` показывает `A.is_current=false`, `B.is_current=true`.
- `dom_trace` считает только `B`.
- Базлайн: `seq(A) < seq(B)`; `prev_seq(B)` — предыдущая точка пути, не обязательно `A`.

**Отказы:** повторный `update(A)` → `NOT_CURRENT` с id текущей версии; тот же текст → `NO_CHANGE`; нет `reason` → `INVALID_FIELD`.

**Тест:** обновить, проверить `version`, `supersedes`, `is_current`, отсутствие `A` в readiness; повторить update → `NOT_CURRENT`.

### OB-2. Дерево плана (проекция OMH)

**Дано:** `plan_tasks`: `П1 → П1.1 → П1.1.2`, у каждой есть `claim_id`, `branch`, `status`; проекция синхронизирована.
**Когда:** `dom_plan_tree(root="П1", depth=2)`.
**Тогда:**
```json
{"status": "PLAN_TREE", "root": "П1", "depth": 2,
 "source": "OMH", "synced_at": "2026-11-11T18:00:00Z", "stale": false,
 "tasks": [{"path": "П1", "claim_id": "phase1-root", "branch": "master",
            "status": "in_progress", "claim_count": 12,
            "children": [{"path": "П1.1", "claim_id": "baseline-concept",
                          "claim_count": 5, "children": []}]}]}
```
**Инварианты:** глубина ≤ `depth`; нет циклов; `claim_count` — только текущие клаймы, связанные через `task_claims`; `stale=true`, если проекция старше `synced_at`.

**Отказы:** нет корня → `PLAN_ROOT_NOT_FOUND` (не пустое дерево); цикл → `PLAN_CYCLE`; ветка вне scope → `SCOPE_DENIED`; `require_fresh=true` + stale → `PLAN_PROJECTION_STALE`.

### OB-3. Клаймы задачи

**Дано:** `task_claims` для `П1.1`: `justifies=baseline-concept`, `implements=[baseline-ddl, baseline-migration]`, `validates=baseline-tests`; `П1.1.2` — дочерняя.
**Когда:** `dom_task_claims(task_path="П1.1", include_children=true, role="all")`.
**Тогда:**
```json
{"status": "TASK_CLAIMS", "task_path": "П1.1", "include_children": true,
 "claims_by_role": {
   "justifies": [{"claim_id": "baseline-concept", "version": 1, "is_current": true}],
   "implements": [{"claim_id": "baseline-ddl", "version": 2, "is_current": true},
                  {"claim_id": "baseline-migration", "version": 1, "is_current": true}],
   "validates": [{"claim_id": "baseline-tests", "version": 1, "is_current": true}]},
 "summary": {"total_claims": 4, "by_content_type": {"concept": 1, "code": 3}},
 "baseline_range": {"branch": "AA", "from_seq": 10, "to_seq": 42},
 "as_of": "2026-11-11T18:00:00Z", "stale": false}
```
**Правило приоритета:**
1. Членство — только `task_claims` (поддерево при `include_children=true`).
2. `requirement_refs` и `applicability` — фильтры/метки, **не** членство.
3. `baseline` — порядок, **не** членство.
4. По умолчанию — только текущие версии; `include_history=true` добавляет заменённые/архивные.

**Отказы:** нет задачи → `TASK_NOT_FOUND`; ветка вне scope → `SCOPE_DENIED`.

### OB-4. Возврат контекста на точку базлайна

**Дано:** базовая линия seq 1..20; `X` v1 на seq 10, `X` v2 на seq 15, `X` archive на seq 18.
**Когда:** `dom_recall(task_path="П1", at_seq=12)`.
**Тогда:** `active_claims` содержит `X` v1; `at_seq=16` → `X` v2; `at_seq=19` → `X` отсутствует (архив).
**Инварианты:** результат равен повторному проигрыванию событий `seq<=at_seq`; будущих клаймов нет; `pending_decisions` — только кандидаты, не admitted на момент seq.
**Отказы:** `at_seq > head` → `REVISION_OUT_OF_RANGE`; `at_seq < fork_point` → `BEFORE_FORK_POINT`.

**Важно:** `at_seq` — **branch-local** seq из `baseline_view` (1-based), не глобальный `events.seq`. Для advanced-режима — опциональный `at_event_seq`.

**Тест:** property-based: для случайной последовательности `claim/update/archive` `recall(N)` эквивалентен `replay(events<=N)`.

### OB-5. Сверка двух веток

**Дано:** `AA` и `AB` расходятся от общего предка на seq 5.
**Когда:** `dom_diff(branch_a="AA", branch_b="AB")`.
**Тогда:**
```json
{"status": "DIFF", "comparable": true, "common_ancestor": "claim-5",
 "only_a": ["..."], "only_b": ["..."],
 "changed": [{"logical_id": "claim-3",
              "a": {"claim_id": "A3", "version": 2, "sha": "..."},
              "b": {"claim_id": "B3", "version": 1, "sha": "..."}}],
 "identical": ["..."]}
```
**Инварианты:** выравнивание по `logical_claim_id` (корень цепочки replacement), а не по `claim_id`; `changed` — одинаковый логический, разный `raw_sha256`.
**Отказы:** нет общего предка → `comparable=false`, не ошибка.

### OB-6. Drift от миссии

**Дано:** миссия `M`:
```json
{"mission_claim_id": "phase1-root",
 "expected": [{"task_path": "П1.1.2", "role": "implements", "content_type": "code"},
              {"task_path": "П1.1.4", "role": "validates", "content_type": "code"}],
 "constraints": [{"all_of": [{"task_path": "П1.1.2", "role": "implements"}]}],
 "threshold": 0.3}
```
**Когда:** `dom_drift_check(branch="AA")`.
**Тогда:**
```json
{"status": "DRIFT", "drift_score": 0.0, "threshold": 0.3,
 "missing": [], "changed": [],
 "extra": [{"task_path": "П1.9", "reason": "вне миссии"}],
 "recommendation": "continue", "undefined": false}
```
**Правило:** `missing+changed / |expected|`; `extra` отдельно, вес 0 по умолчанию; `|expected|=0` → `drift_score=null`, `undefined=true`, `realign`.

**Отказы:** нет миссии → `MISSION_NOT_SET`; нарушено constraint → `CONSTRAINT_VIOLATED` с указанием правила.

### OB-7. Форк ветки

**Дано:** `AA`, fork point `P`, `carry=[X]`, `rewrite=[Y]`.
**Когда:** `dom_fork_branch(source="AA", target="AA2", fork_point=P, carry=["X"], rewrite=["Y"], reason="...")`.
**Тогда:**
```json
{"status": "FORKED", "source": "AA", "target": "AA2", "fork_point": "P",
 "carried": [{"source": "X", "target": "X'"}],
 "rewritten": [{"source": "Y", "target": "Y'", "version": 2, "supersedes": "Y"}]}
```
**Инварианты:** атомарная транзакция; `target` не существует; `fork_point` ∈ baseline(source); `carry ∩ rewrite = ∅`; baseline(AA2) начинается с `prev_seq = seq(P)`; `branch_fork_claims` фиксирует оба набора.
**Отказы:** `BRANCH_EXISTS`, `FORK_POINT_NOT_FOUND`, `INVALID_FORK_SET`; сбой в середине → rollback, ветка не создана.

### OB-8. Синхронизация с OMH

**Дано:** outbox-intent, в OMH транзакции нет.
**Когда:** `dom_sync(branch="AA")`.
**Тогда:** `delivery_attempt` записан → `read_target` (miss) → `attach` → `read_target` (exact) → `ack` → `SYNCED`.
**Инварианты:**
- Внешний I/O **не** выполняется внутри read-tx.
- Перед ack — повторная проверка head; если head изменился, результат `ambiguous`, не `ack`.
- Повторный `sync` не дублирует доставку (idempotency + `delivery_facts.confirmed`).
**Отказы:** target недоступен → `TARGET_UNAVAILABLE`, ack нет; crash между attach и ack → `SYNC_PENDING`, retry безопасен.

### OB-9. Дедуп/полнота (внутренний оркестратор)

**Дедуп:** одинаковый нормализованный блок в другой ветке → `DUPLICATE_OF` + существующий `claim_id`, новый клайм не создаётся. Разные `metadata`/`requirement_refs` → новый клайм (это не дубликат, а версия/уточнение).
**Полнота:** блок ссылается на несуществующий claim → `INCOMPLETE` с `missing_refs`; молчаливое отбрасывание запрещено.
**Сессия:** две сессии с разными контекстами не видят контекст друг друга; после рестарта состояние сохраняется (SQLite/harness), а не теряется как in-memory dict.

### OB-10. Архитектурные инварианты (проверяемые)

| Инвариант | Как проверить |
|---|---|
| `trace`/`resume` верифицируют цепочку **один раз** | monkeypatch-счётчик: `query=1, trace=1, resume=1` |
| `sync` не держит read-tx во время I/O | медленный порт + параллельный писатель: задержка писателя < 2 с |
| Каждый инструмент имеет handler + schema + doc | тест по реестру |
| Каждый claim имеет snapshot | SQL: `SELECT count(*) FROM claims c LEFT JOIN claim_snapshots s ON s.claim_id=c.id WHERE s.claim_id IS NULL` = 0 |
| `version`/`logical_claim_id` согласованы с `_lineage` | property-тест: значения DTO совпадают с `_lineage` |
| Базлайн не мутирует | view read-only; попытка записи → SQL error |

---

## 4. Пути реализации

### P0. Немедленные исправления (без схемы)

| # | Что | Файлы | Тест |
|---|---|---|---|
| P0.1 | Один `verify_chain` на запрос: передавать `chain` в `_trace` | `admission.py:346-368`, `514-534` | счётчик вызовов |
| P0.2 | Вынести I/O из read-tx в `sync`; re-check head перед ack | `admission.py:457-497` | slow port + writer |
| P0.3 | Единый реестр `TOOLS`/`SIGNATURE`/`dispatch` | `server.py:42-249` | drift-тест |
| P0.4 | Инвариант «claim ↔ snapshot» + helper | `admission.py:290-294` | SQL-инвариант |

**DoD P0:** 4 теста зелёные; полный прогон **77 passed, 0 failed**; demo exit 0.

**Статус 2026-11-11:** P0.1–P0.4 закрыты в `arch/p0-invariants`; ADR-P0-01…04 (`docs/adr/`); новые тесты `tests/test_p0_invariants.py` и `tests/test_tool_registry.py`. Три ранее красных теста триажированы как устаревшие относительно текущих публичных контрактов (публичный Trace/Broken DTO, `scope_digest` в replay key, L1 digest-first), не ослаблены.

### P1. Ядро: version + baseline + recall

**Статус 2026-11-11:** P1 закрыт в `arch/p1-version-baseline` (кроме TD-DOM-37, отложенного до первой v4-схемы). ADR-P1-00…05 (`docs/adr/`); новые тесты `tests/test_p1_version_baseline.py` (13). Полный прогон **90 passed, 0 failed**; demo exit 0. Реализованы `commit_ref`, производные `version`/`logical_claim_id`/`supersedes`, `baseline_view` + `branch_event_view`, `dom_recall` (branch-scope), `dom_claim_versions`, `dom_diff`. `task_path`-фильтр recall и зависимые от `task_claims` поля отложены до P2; `pending_decisions` честно `null`, потому что кандидаты не являются событиями. Baseline-view не требует v4.

**P1.1. `commit_ref` (optional).**
- Добавить `OPTIONAL_FIELDS = {'code': {'commit_ref': dict}}` в `dom_contract.py`.
- Расширить `fields()`/`validate()`: обязательные — как сейчас, опциональные — только если присутствуют; unknown keys reject.
- Добавить `commit_ref` в `claim_entry.FIELD_TYPES`/`TYPE_ARGS` и в `REQUIRED_FIELDS`? Нет: он опциональный, не в required.
- Тест: code-клайм без `commit_ref` проходит; с валидным — проходит; с невалидным хешем — `INVALID_FIELD`.

**P1.2. Производные version/logical_claim_id.**
- В `claim_entry.find`/`admission.query`/DTO добавить `version`, `logical_claim_id`, `supersedes`.
- Не менять схему; не добавлять колонки.
- Тест: после update `version=2`, `logical_claim_id=root`, `supersedes=old`.
- Property-тест: DTO == `_lineage`.

**P1.3. `baseline_view`.**
- Создать view в `storage._create_triggers`/`initialize` (после таблиц).
- `chunk_hash = event_hash`, `prev_seq` — window function.
- Тест: view для ветки с 3 claim-событиями даёт seq 1..3, prev_seq 0,1,2; `chunk_hash` непустой и детерминированный.

**P1.4. `dom_recall`.**
- `snapshot_at_seq(c, branch, at_seq)` в `projections.py`: фильтр по `events.seq <=` (mapping branch-local seq → global seq через `baseline_view`).
- `admission.recall(branch, task_path, at_seq, include_children, role)`.
- Ответ: `active_claims`, `pending_decisions`, `resolved_conflicts`, `related_branches`, `as_of`, `baseline_range`.
- Тест: replay-эквивалентность; границы `at_seq`; архив.

**P1.5. `dom_diff` / `dom_claim_versions` (TD-DOM-22.6).**
- Выравнивание по `logical_claim_id`; `common_ancestor` — `branch_forks.fork_point` или корень цепочки.
- Тест: две ветки, changed/only/identical.

**DoD P1:** выполнен. P0 зелёный; 12 P1-тестов; ADR-P1-00…05; `commit_ref` и baseline view покрыты; recall/diff/versions зарегистрированы в strict `TOOLS`/`SIGNATURE`/`HANDLERS` и публичных DTO.

### P2. Проекция плана и task claims

**P2.1. Идентичность и версии пунктов плана (D1.1).**
- `plan_tasks` — только идентичность: `plan_task_id` (из OMH), `source`, `external_ref`, `created_at`.
- `plan_task_versions` — append-only история: `(plan_task_id, version)`, `path`, `parent_id`, `status`, `title`, `task_type`, `source_revision`, `digest`, `semantic_digest`, `archived`, `observed_at`.
- `current_plan_tasks` — view max(version); не мутируемая таблица.
- `task_claims` — `plan_task_id` + `linked_at_plan_version` + `linked_semantic_digest`; DOM-owned, синхронизация плана их не трогает.
- `plan_projection_state` — `source_revision`, `last_checked_at`, `last_changed_at`, `snapshot_digest`.
- `project_plan_snapshot` — идемпотентный: skip по `digest`, version+1 только при изменении, archive при отсутствии в full snapshot, reject older `source_revision`.
- `link_stale` — по `semantic_digest`, не по версии.
- Полная схема и алгоритм — §D1.1.

**P2.2. `dom_plan_tree`.**
- Рекурсивный CTE по `parent_id`; глубина ≤ `depth`; `claim_count` — текущие версии через `task_claims`.
- `root` — `plan_task_id` или `path` (resolve to id); не хардкод `П1`.
- `PLAN_ROOT_NOT_FOUND`, `PLAN_CYCLE`, `PLAN_PROJECTION_STALE`.
- `at_version` опционально: historical tree из `plan_task_versions`; по умолчанию current.
- `dom_plan_task_versions(plan_task_id)` — список версий + diff (from/to) по `digest`/`semantic_digest`.

**P2.3. `dom_task_claims`.**
- Рекурсивный CTE по `parent_id`; join `task_claims` + `claims`; фильтр текущих версий клаймов; группировка по роли.
- `link_stale` = `current.semantic_digest != linked_semantic_digest` или `archived=1`; `plan_task_version`, `linked_at_plan_version`.
- `at_plan_version` опционально: только ссылки с `linked_at_plan_version <= at_plan_version` (аудит истории).
- `baseline_range` — min/max `baseline_view.seq`; `stale`, `as_of`; `include_archived` для истории.

**P2.4. Split/merge/orphan.**
- Новые `plan_task_id`; старые archived; ссылки не копируются; `ORPHANED_LINKS` + `next_steps` relink.
- `dom_task_claims` показывает `orphaned_links`.

**DoD P2:** идемпотентный sync; status-only не старит ссылки; rename сохраняет ссылки; delete архивирует; old revision отклоняется; split/merge не теряет ссылки молча; `stale` корректен; статусы в DOM не пишутся.

### P3. Diff, drift, fork

- **Diff:** P1.5; для двух веток — `common_ancestor`, `only_*`, `changed`, `identical`.
- **Drift:** `mission_checkpoints` с `expected`/`constraints` JSON; вычислитель `all_of/any_of/none_of`; `score` по D5; `extra` отдельно; тест на `|expected|=0`.
- **Fork:** одна транзакция; `branch_forks` + `branch_fork_claims(fork_id, source_claim_id, target_claim_id, action)`; `carry` — новые ID с тем же телом; `rewrite` — новая версия с `supersedes`; rollback при сбое.

**DoD P3:** drift не делит на ноль; fork атомарен; diff не путает версии.

### P4. Оркестратор

- **Внешний (Hermes):** контракт инструментов, NL→tool, диалоговая сессия; не пишет ledger.
- **Внутренний (DOM):** дедуп (`_find_identical` + `semantic_hash` как pre-check), полнота (`INCOMPLETE` + `missing_refs`), фильтрация чекпоинтов, `IClaimExtractionPort` для LLM-фильтра.
- **Сессии:** SQLite/harness, TTL, изоляция; не in-memory dict.
- **DoD P4:** дедуп не создаёт дубликат; полнота не молчит; сессии изолированы; LLM-кандидат проходит review.

### P5. Live-порты, Merkle, fault tolerance

- **P5.1 `IOmhDeliveryPort` (Protocol):** `read_target`, `attach`, `verify`; инъекция в `Service`; simulated adapter сохраняется.
- **P5.2 Merkle/checkpoints:** глобальная цепочка `events.seq`; checkpoint `(seq, hash)`; инкрементальная проверка; `branch_heads.last_verified_seq` не использовать как глобальный (несоответствие).
- **P5.3 Retry/circuit/fallback:** матрица retryable; `sync` — retry; `update` — reconciler для `UPDATE_INCOMPLETE`; fallback — кэш + `stale=true`; circuit — после live-портов.

**DoD P5:** live-адаптер проходит contract-тесты; checkpoint не ломает append-only; retry не дублирует.

---

## 5. Исправления макетов аудита

| # | Макет | Проблема | Исправление |
|---|---|---|---|
| 1 | `claims_after_insert` заполняет `claim_snapshots` | `dependencies`/`review_id` — из envelope (`p['dependencies']`, конкретный `review_id`), их нет в `claims.payload`; подзапрос `reviews WHERE candidate=...` вернёт произвольное ревью; плюс дубль существующего INSERT → UNIQUE | Оставить Python-вставку + инвариант; триггер только после денормализации |
| 2 | `baseline ... UNIQUE(branch, claim_id, version)` | `version` — не колонка `baseline`; DDL падает | Убрать или добавить колонку |
| 3 | `chunk_hash` через `randomblob` | Не детерминирован, не хеш | `event_hash`/SHA-256 от canonical payload |
| 4 | `claims.version/supersedes` при вставке | `update` создаёт claim **до** replacement-события; родитель неизвестен | Производные (D2) или новый пакет `replace` |
| 5 | `logical_claim_id = origin_branch + ':' + local_id` | `local_id` по умолчанию `'c1'` у всех `dom_claim` → все клаймы ветки получат один logical id | Корень цепочки replacement или UUID на v1 |
| 6 | `commit_ref` в `TYPE_FIELDS['code']` | Валидатор требует все поля → старые code-клаймы сломаются | `OPTIONAL_FIELDS` + отдельная проверка |
| 7 | `commit_ref.hash` — 40 hex | SHA-256 Git — 64 hex | 40 или 64 |
| 8 | `claim_templates` + `validate_claim_for_task` | Дублирует `TYPE_FIELDS` и strict-валидацию | Выводить из контракта |
| 9 | `plan_tasks`/`task_claims` как сущности DOM | Конфликт с `REQUIREMENTS §2` | Проекция/кэш OMH (D1) |
| 10 | `drift_score = (drifted+missing+new)/len(expected)` | Деление на ноль; `new` штрафует легитимную работу; `is_related_to_mission` не определён | `missing+changed / expected`, `extra` отдельно, `undefined` при пустой миссии |
| 11 | `dom_plan_tree` root=`П1` | Хардкод; нет поведения для пустого плана | Явный root/`project_root`, `PLAN_ROOT_NOT_FOUND` |
| 12 | `UNIQUE(claim_id, path)` | Один decision не может обосновать две задачи | Убрать или документировать ограничение |
| 13 | `dom_recall` поля `pending_decisions`, `resolved_conflicts`, `related_branches` | Нет определения вычисления | Определить или вернуть `null` |
| 14 | `implementation_status`, `next_action`, `task_blockers`, `task_dependencies` | Состояние исполнения плана — OMH | Не хранить в DOM или только projection |
| 15 | `baseline` как таблица | Дублирует `events` + `claim_snapshots` | View (D3) |
| 16 | `claim_variants` | Пересекается с ветками; статус `merged/abandoned` не определён | Отложить до merge-операций |
| 17 | `dom_fork_branch` carry/rewrite | `carry` без `supersedes` теряет связь с источником; `rewrite` требует link при вставке | `branch_fork_claims` + атомарный пакет |
| 18 | Двухфазный `sync` | Если не сохранить verified stamp, ack может быть устаревшим | Захватить head до I/O, сравнить перед ack, иначе `ambiguous` |

---

## 6. Трассировка: аудит → TD → путь → тест

| Аудит | Новый TD | Путь | Тест |
|---|---|---|---|
| TD-ARCH-01 | TD-DOM-36 | P0.4 / P1.4 | snapshot invariant |
| TD-ARCH-02 | TD-DOM-33 | P0.1 | verify counter |
| TD-ARCH-03 | TD-DOM-34 | P0.2 | slow port + writer |
| TD-ARCH-04 | TD-DOM-37 | P1.3 | migration matrix |
| TD-ARCH-05 | TD-DOM-35 | P0.3 | registry drift |
| TD-INT-01 | TD-DOM-51 | P5.1 | port contract |
| TD-PLAN-01 | TD-DOM-44 | P2 (deferred) | materialization equivalence |
| TD-UPD-01 | TD-DOM-38 | P1.2 | derived version |
| TD-STRUCT-01 | TD-DOM-50 | P4 | façade tests |
| TD-BASE-01 | TD-DOM-40 | P1.3 | baseline view |
| TD-BASE-02 | TD-DOM-41 | P1.4 | recall replay |
| TD-BASE-03 | TD-DOM-22.6 | P1.5 | diff |
| TD-VER-01 | TD-DOM-38 | P1.2 | version/logical id |
| TD-VER-02 | TD-DOM-39 | P1.1 | commit_ref optional |
| TD-DRIFT-01 | TD-DOM-45 | P3 | drift zero/extra |
| TD-FORK-01 | TD-DOM-46 | P3 | fork atomic |
| TD-CTX-01..05 | TD-DOM-42/43 | P2 | projection/stale |
| D1.1 (plan item versions) | TD-DOM-54/55 | P2/P3 | idempotent sync / link_stale |
| ORCH-01..03 | TD-DOM-47/48/49 | P4 | dedup/completeness/sessions |
| FAULT-01..03 | TD-DOM-53 | P5 | retry/checkpoint |

---

## 7. Приоритеты и ветки разработки

### 7.1. Приоритеты закрытия

| Приоритет | Что | Почему сейчас | Зависимости |
|---|---|---|---|
| **P0** | double verify, sync tx, registry, snapshot invariant | доказанные дефекты; без продуктовых решений | — |
| **P1** | commit_ref, derived version, baseline view, recall, diff | даёт «возврат к задаче»; минимальная схема | P0 |
| **P2** | проекция плана, версии пунктов, plan_tree, task_claims | требует D1/D1.1 и синхронизации OMH | P1 |
| **P3** | drift, fork, split/merge orphan links | требуют формальной миссии и стабильного version | P2 |
| **P4** | два оркестратора, дедуп, полнота, сессии | отдельная подсистема | P1/P2 |
| **P5** | live-порты, Merkle, retry/circuit | после P0 и стабильного ядра | P0/P1 |

### 7.2. Ветки

| Ветка | Scope | Базируется на | Merge в `main` когда |
|---|---|---|---|
| `main` | docs, анализ, стабильное ядро | — | — |
| `arch/p0-invariants` | TD-DOM-33..36 | `main` | 4 теста + полный прогон |
| `arch/p1-version-baseline` | TD-DOM-37..41, 22.6 | P0 | P1 DoD |
| `arch/p2-plan-projection` | TD-DOM-42/43/54 (TD-DOM-44 deferred) | P1 | P2 DoD |
| `arch/p3-diff-drift-fork` | TD-DOM-45/46/55 | P2 | P3 DoD |
| `arch/p4-orchestrator` | TD-DOM-47..50 | P1/P2 | P4 DoD |
| `arch/p5-live-ports` | TD-DOM-51..53 | P0/P1 | P5 DoD |

**Правила:** одна ветка — один приоритет; ADR на каждый пункт; тесты не ослаблять; 3 известных красных теста триажить до P1 (они не регрессии, но мешают критерию «полный зелёный»).

---

## 8. Открытые вопросы

1. **Constraint DSL:** точный синтаксис `all_of`/`any_of`/`none_of`; нужны ли веса и вложенность. Без него `violates()`/drift не формализуемы.
2. **Checkpoint strategy:** глобальный `(seq, hash)` vs per-branch; `events.seq` глобальный, `branch_heads` — нет. Нужен дизайн Merkle/checkpoint до P5.
3. **JSON Schema:** генерировать из type hints или хранить явно; при явном — drift-тест.
4. **Current version rule:** «последняя по revision» vs «последняя admitted» vs «по ветке по клайму»; `REQUIREMENTS` строка 66 требует утверждённого варианта.
5. **Session storage:** SQLite vs harness; TTL; изоляция.
6. **Drift thresholds:** дефолт 0.3; кто утверждает; нужны ли per-task пороги.
7. **LLM-фильтр:** модель, промпт, provenance, детерминированный fallback; нужен ли он в MVP.
8. **pydantic:** использовать для схем или оставить ручной `strict_arguments`; Q38 разрешает, но выбор не сделан.
9. **Стабильный `plan_task_id` из OMH:** есть ли у OMH неизменяемый ID и версия задачи? Если нет — DOM вводит surrogate + `external_ref`, а смена `path` без ID трактуется как новая задача.

---

## 9. Что дальше

1. **P0 — выполнен 2026-11-11** (`arch/p0-invariants`): 4 теста, ADR-P0-01…04, коммит; 77 passed, demo exit 0.
2. **P1 — выполнен 2026-11-11** (`arch/p1-version-baseline`): commit_ref, derived version, baseline view, recall, diff; ADR-P1-00…05; 13 тестов; 90 passed, demo exit 0. TD-DOM-37 отложен до v4; `task_path` recall — P2.
3. Следующий шаг — синхронизация проекции плана (P2), затем drift/fork (P3).
4. P4/P5 — отдельные планы; не смешивать с ядром.

**Критерий готовности анализа:** решения D1–D6 зафиксированы, tech_debt обновлён, ветки/приоритеты описаны, P0 имеет исполнимый список шагов.
