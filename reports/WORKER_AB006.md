# WORKER AB006 — отчёт (CONT-02: запись артефактов из собранных доказательств)

- **Задача**: AB006 CONT-02 — перенести уже собранные доказательства из `runtime/AB006/results/` в три файла: `artifacts/WORKER_AB006.json`, `reports/WORKER_AB006.md`, `docs/SCHEMA_CHANGE_AB006.md`.
- **Статус**: COMPLETED_WITH_SEPARATE_ACCEPTANCE. `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`.
- **Дата**: 2026-11-08T13:23:04+00:00. Код и пробы не менялись; прогоны не переделывались — только read-only подтверждения (digest probe, PRAGMA на fixtures).

## Что сделано (срез AB006: RS007 W1, option A — pending-секция + миграция v2)

Pending-секция (`resume`/`list`, сервисный уровень) переведена на metadata-only выдачу с
scope-фильтрацией по правилу `candidate.branch ∈ grant AND payload.dependencies ⊆ grant`,
admitted-исключением и точным фильтрованным `count` (анти-exists-oracle). В хранилище —
миграция v2: `created_at` у candidates + два join-индекса под admitted-предикат. Всё это
уже было реализовано и проверено в AB006 (прогоны в `runtime/AB006/`); данный континуум
только оформил результаты.

Изменённые файлы ровно четыре (подтверждено диффом против среза AB005-эры
`runtime/AU006/sources/P`, лишних нет): `mockup/admission.py`, `mockup/storage.py`,
`mockup/public_dto.py`, `mockup/server.py`.

## Чем подтверждено (evidence, всё на диске)

- **Digest**: `runtime/AB006/probes/digest_probe.py` → текущий
  `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505` (`matches parent True`);
  состояние после AB005 = `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7`
  (из au007.json + WORKER_AB005.json).
- **Миграция**: `results/checks_summary.json['migration']` — legacy-init OK, user_version 2,
  колонки candidates с `created_at`, оба индекса, 39 immutable-триггеров, повторный запуск
  идемпотентен (`after_first == after_rerun`). Read-only PRAGMA на `fixtures/w1/dom.sqlite3`:
  uv=2, `idx_idempotency_candidate`, `idx_claims_candidate`, 39 immutable-триггеров (из 44
  всего; 5 не-immutable: attempt_binding, observation_binding, ack_binding,
  legacy_ack_refused, chain_previous_hash).
- **Perf** (`checks_summary.json['perf']`): p1k page50 = 14.418 мс (count 500),
  p100k page50 = 1504.595 мс (count 99500), p100k без индексов = 15901.46 мс →
  отношение ≈10.57×; в контрактной границе 10× (потолок 1537.84 мс, measured 1504.595 мс,
  `within_10x=true`); resume+pending комбинированно p1k 16.6 мс / p100k 2185.7 мс.
- **Позитив**: `results/pos1.json` (discover, memoryless continuation: after revision 2,
  claims 1→2; receipts DEMO_ADMITTED + REVISION_CONFLICT→USED_PENDING_REVIEW; SQL-счётчики
  claims 1→2, reviews 2→3, idempotency 6→7, transactions 1→2, events 1→2, candidates 5 без
  изменений) и пагинационный обход 4 страниц без дублей/потерь (count стабилен, has_more
  на последней странице false, покрыты все 4 pending).
- **Негативы**: `results/neg1/neg2/neg2b/neg3.json` + `checks_summary['neg']` — см.
  «Подтверждённые негативы» ниже.
- **Кадры MCP**: `results/frames_full.jsonl` (грант AA,AB → 4 pending-элемента) и
  `results/frames_empty.jsonl` (w3 → `NO_PENDING`, 0 элементов) — реальные JSON-RPC кадры.
- **Age**: legacy-null: кандидат без `created_at` → `age_seconds` отсутствует (не 0);
  pristine w1 → `age_seconds=5` (checks_summary['age']).

## Расхождение digest (обязательный раздел)

Ранние числа из карты `before=3a5f875b…` / `after=3f0af9c4…` **не воспроизводятся**
документированным методом SEC003 (sha256 от отсортированной JSON-карты
`mockup/<posix-relpath> -> sha256` по 16 файлам, `__pycache__` исключён) и признаны
**ошибочными** (нестандартный расчёт — другой набор файлов/канонизации). Цепочка
digest-истории: после AB005 = `ca227b17…` (зафиксирован в au007.json и
WORKER_AB005.json) → текущее = `c26812b3…` (воспроизводится на диске, `matches parent
True`). В артефакте расхождение вынесено в отдельное поле `digest_discrepancy`, в
отчёте — в этот раздел; в SCHEMA_CHANGE_AB005.md и других документах ранние числа не
использовались.

## Недополнение страницы при сужении гранта (обязательный раздел)

`has_more` — **предфильтровый** эвристик `limit+1`: SQL берёт `LIMIT limit+1` ДО фильтров
видимости (deps ⊆ grant, admitted-исключение), поэтому при сужении гранта страница может
вернуть меньше элементов, чем `has_more` обещает (измерено: `count=2, items=0,
has_more=true` — `checks_summary['pos']['underfill_edge_narrowed']`). Это **известное
поведение контракта**, не дефект: `count` остаётся точным (отдельный scope-фильтрованный
pass, анти-exists-oracle), клиент обязан продолжать листать по `has_more`, а не по
наполнению `items`.

## Подтверждённые негативы (сводка)

1. **Чужой грант AB** (neg1): виден 1 элемент только ветки AB; чужие AA-кандидаты,
   deps-зависимый и admitted-кандидат не выдаются; нет ни AA-идентификаторов, ни текста
   тел (`forbid_text "C1 reviewed pre-kill body"` чист).
2. **Суженный AA** (neg2): 2 элемента; кандидат k4 (deps `{AB:0}`, AB вне гранта) скрыт
   целиком — без маркера и текста; `count=2` фильтрован точно.
3. **Полный грант AA,AB** (neg2b): 4 элемента; k4 снова видим; admitted и тексты не
   выдаются.
4. **Пустая очередь** (neg3, w3): `status=NO_PENDING`, `count=0`, `items=[]`.
5. **admitted не выдаётся**: кандидат с admitted-предикатом (EXISTS claims ИЛИ
   idempotency admit-строка) отсутствует в pending даже при полном гранте
   (admitted-кандидат `737b0b8a…`).
6. **count фильтрован** (анти-exists-oracle): neg1 `count=1` при 5 кандидатах в БД —
   счётчик не выдаёт существование чужих/скрытых строк.
7. **items_metadata_only=true** во всех прогонах: только метаданные + `payload_length`,
   тело не отдаётся (`items_carry_body=[]`, `forbidden_text_present=false`).

## Файлы

- Созданы: `artifacts/WORKER_AB006.json`, `reports/WORKER_AB006.md`, `docs/SCHEMA_CHANGE_AB006.md`.
- Прочитаны (не изменены): `cards/AB006_CONTINUE_02.md`, `runtime/AB006/results/*`,
  `runtime/AB006/probes/{digest_probe,run_checks}.py`, `runtime/AB006/probes/run_out.txt`,
  fixtures БД (read-only), `mockup/storage.py`, `mockup/admission.py` (для DDL/кодов).

## Границы

Продукт, тесты, долги, конфиги, OMH — не тронуты. Git/install/платные/субагенты — не
использовались. Ориентир вызовов выдержан.
