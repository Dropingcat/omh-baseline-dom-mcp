# AB006 CONT-02 — только записать три артефакта

Все доказательства собраны и лежат в `runtime/AB006/results/`. Задача — **перенести их в три файла**. Код и пробы не менять; перезапускать прогоны только если конкретного числа не хватает.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P.

## Источник данных (читать, не пересчитывать заново)
- `runtime/AB006/results/checks_summary.json` (migration, perf, pos, neg, age, mcp_full_grant, mcp_empty)
- `runtime/AB006/results/{pos1,neg1,neg2,neg2b,neg3}.json`, `frames_full.jsonl`, `frames_empty.jsonl`, `run_out.txt`
- `runtime/AB006/fixtures/**` (копии БД)

## Обязательные факты для артефакта (сверять с диском, не выдумывать)
1. **Digest.** Метод документированный: `sha256(json.dumps({'mockup/<posix>': sha256, ...}, sort_keys=True))` по 16 `mockup/**/*.py`.
   - текущее состояние (after): `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505`
   - состояние после AB005 (before): `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7`
   - Ранние числа `before=3a5f875b…` / `after=3f0af9c4…` **не воспроизводятся** документированным методом и признаны ошибочными (нестандартный расчёт). Записать это отдельным полем `digest_discrepancy` с объяснением.
   - Файлов, изменённых сверх четырёх (`admission.py`, `storage.py`, `public_dto.py`, `server.py`), **нет** — подтверждено диффом против `runtime/AU006/sources/P`.
2. **Миграция**: legacy-src → `user_version=2`, `created_at`, индексы `idx_idempotency_candidate`/`idx_claims_candidate`, 39 неизменяемых триггеров, повторный запуск идемпотентен.
3. **Perf**: p1k ~14.4 мс, p100k ~1504.6 мс, p100k без индексов ~15901.5 мс, отношение ≈10.57×.
4. **Негативы**: чужой грант AB — 1 элемент, только AB, ни AA-идентификаторов, ни текста; суженный AA — 2, чужой по deps скрыт; полный — 4; w3 — `NO_PENDING`; admitted не выдаётся; `count` тоже фильтрован (анти-exists-oracle); `items_metadata_only=true`, текст не отдаётся.
5. **SQL-счётчики** pos1 до/после: claims 1→2, reviews 2→3, idempotency 6→7, transactions 1→2, events 1→2, candidates 5 (без изменений).
6. **Особенность**: `has_more` — предфильтровый эвристик `limit+1`, поэтому страница может быть недополнена при сужении гранта, а `count` остаётся точным. Записать как известное поведение контракта.

## Выходы (ровно три файла)
- `artifacts/WORKER_AB006.json`: `status`, `changed_files[]`, `digest_method`, `digest_before`, `digest_after`, `digest_discrepancy`, `migration{}`, `perf{}`, `pos_results[]`, `neg_results[]`, `negative_confirmations[]`, `page_underfill_edge`, `evidence_refs[]`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`.
- `reports/WORKER_AB006.md`: что сделано, чем подтверждено, отдельный раздел про расхождение digest и про недополнение страницы.
- `docs/SCHEMA_CHANGE_AB006.md`: миграция v2 (DDL, порядок, идемпотентность, триггеры, индексы), новые поля pending-секции, коды.

## Границы
Ничего, кроме этих трёх файлов (+ при необходимости пересчёт одного отсутствующего числа в `runtime/AB006/`). Продукт, тесты, долги, конфиги, OMH — не трогать. Без Git/install/платных/субагентов. Ориентир 20 вызовов.
