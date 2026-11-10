# RESEARCHER RS007 — W1: незавершённая работа (видимость + континуация без подсказки)

Роль: RESEARCHER RS007 (CONT-01). Статус: **COMPLETED** (прототип зелёный, ответы и валидатор на диске).
Продукт read-only (`mockup/*` не тронут, receipt `product_files_modified=[]`), сеть=false, applied=false.

## 0. Подозревал → проверил → оказалось

| # | Подозревал | Проверил (чем) | Оказалось |
|---|---|---|---|
| 0.1 | «Одна правка порядка параметров → зелёный» (гипотеза CONT-0) | Запуск proto после фикса порядка; разбор checks каждого результата | Правка порядка — необходимая, но НЕ достаточная. Вскрылись ещё 3 дефекта: count включал admitted (c0) → count≠items; leak-скан сканировал собственный argv драйвера (forbid-значения из CLI = самофлагирование); гейт `all(v is True)` ломался на int-полях visible_count/count. Зелёный = 4 правки, не 1 |
| 0.2 | pos1 должен выдать все DEMO_ADMITTED и count=0 после | Чтение admission.py:208-256 (admit: требование head==expected_branch_revision) | Два кандидата на одну ревизию (1): admit второго неизбежно REVISION_CONFLICT по построению. Честный зелёный = 1 допуск + 1 выданный метаданными конфликт (expected 1 / head 2), final count=1. Не форсировать |
| 0.3 | Страницы perf «работают» | page_items_bytes в scenarios.json | Были пустыми (2 байта): фикстура помещала admitted-строки в НАЧАЛО keyset-порядка, первые 51 строки все пропускались. Оказалось: admitted перенесены в конец — страницы живые (20121 B), индексы v2 = 10.72× (16481 мс → 1538 мс на 100k) |
| 0.4 | Idempotent replay «просто не дублирует запись» | tx_id par1 vs par2 | Физически: par1.tx_id == par2.tx_id == 3ade0d30… — возвращается СОХРАНЁННЫЙ receipt (dedupe), вторая транзакция не создаётся; параллельно (2 потока) tx_total=1, claims_total=1, head=1 |

## 1. Прототип (runtime/RS007/prototypes/)

Сборка: `python -E rs007_prototype.py` (фикс: параметры `?` в порядке текста — подзапросы `work,work` → `IN(ветки)` → `after` → `limit+1`). Драйвер беспамятного клиента `drivers/fresh_client.py` в новом интерпретаторе (`-E -I`, ни одного candidate-id в argv).

| Сценарий | rc | visible | count | Смысл |
|---|---|---|---|---|
| neg1_foreign_grant_AB | 0 | 1 | 1 | чужой грант: только своя ветка (C3); C0..C2,C4 невидимы |
| neg2_narrowed_grant_AA | 0 | 2 | 2 | суженный грант: C4 (deps {AB}) скрыт целиком, без маркеров |
| neg2b_full_grant_AA_AB | 0 | 4 | 4 | полный грант: C4 виден метаданными, текст не возвращается |
| pos1_memoryless_continuation | 0 | 2 | 2 | **без подсказки**: 1×DEMO_ADMITTED + 1×REVISION_CONFLICT (expected 1/head 2), final=1 |
| empty_no_pending | 0 | 0 | 0 | NO_PENDING — завершённое не выдаётся |
| par_same_key_first / second_replay | 0 | 1/0 | 1/0 | повтор ключа → тот же receipt, та же tx |
| par_fresh_key_second_conflict / second | 0 | 1/0 | 1/0 | fresh key после сдвига head → REVISION_CONFLICT |
| par_threaded_same_key | — | — | — | 2 потока: оба DEMO_ADMITTED, tx_total=1, claims_total=1, head=1 |

`after_pos1`: pending AA = 1 (stale C2), `expect_1_stale_c2_conflict=true`.

## 2. Perf (пересчитаны после фикса; страницы живые)

| N | page50, мс | page50+after, мс | count (точный pending), мс | resume, мс | resume+page, мс |
|---|---|---|---|---|---|
| 1 | 1.96 | 2.03 | 0.90 | 3.94 | 5.90 |
| 1k | 15.84 | 15.45 | 19.82 | 4.27 | 20.11 |
| 100k | 1537.84 | 1539.15 | 674.13 | 4.82 | 1542.66 |

100k без индексов v2: **16481.45 мс** (10.72× медленнее) → миграция v2 обязательна с ~1k. Страница 50 ≈ 20121 B метаданных.

## 3. Ответы (runtime/RS007/answers/)

- **taxonomy** — 7 видов незавершённого, SQL-предикаты; question2: no-locks/no-race/no-false-abandoned (без heartbeat «брошено» не выдаётся).
- **leak** — LEAK-1..6; политика: in-scope метаданные показываются, текст не возвращается вовсе; out-of-grant невидим (анти-exists-oracle).
- **options** — A (resume-расширение): страница-цена 1.96/15.84/1537.84 мс на 1/1k/100k, count 0.90/19.82/674.13, resume ≈ 4 мс; B отдельный инструмент (нарушает «без подсказки»); C материализация (только при жёстких SLA >100k); D журнал (не нужно без аудита); E внешний журнал (единственный для «вне базы», решение NU-AU006-01). **Вердикт: A** (условия: ≤ ~100k; индексы v2 обязательны; B — дополнение; E вне W1).
- **contract** — коды NO_PENDING/PENDING_PRESENT (страничный признак; глобальный факт — count); 13 полей item (candidate_id, intent_digest, state, branch, operation, origin, dependencies, expected_branch_revision, payload_length, idempotency_key, review_id, age_seconds); пагинация keyset (branch,id) «branch:id», has_more из limit+1; миграция v2 (created_at + idx_idempotency_candidate + idx_claims_candidate, legacy → age отсутствует); «вне базы» вне W1.
- **checks** — POS1 (беспамятная континуация), POS2 (idempotent replay: same tx_id), POS3 (параллель: 1 запись), NEG1..5 (чужой грант, суженный грант, метаданные-без-текста, NO_PENDING, fresh-key conflict), perf-контроли — каждый с физическим файлом `results/*.json`.

## 4. Валидация

`validate_rs007.py` → **PASS 50/50, exit 0**; `validation_receipt.json` (validator sha256 `7977f901…`). Проверено: rc=0 ×9, visible, потоковый контроль, same-tx replay, живые страницы perf, ускорение индексов, live-пробы w1 (1/PENDING_PRESENT) и w3 (0/NO_PENDING), leak-контроли, ключи всех ответов, отсутствие debug_probe*/__pycache__.

## 5. Границы

Продукт/тесты/tech_debt/конфиги/живой OMH не тронуты (read-only импорты mockup). Конвенция admit без энфорса `decision!='approve'` — наблюдение вне W1. `applied=false`, `product_acceptance=false`, `is_approval=false`. Запись только в `runtime/RS007/**`, `artifacts/RESEARCHER_RS007_UNFINISHED.json`, `reports/RESEARCHER_RS007_UNFINISHED.md`.
