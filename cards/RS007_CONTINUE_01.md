# RS007 CONT-01 — довести W1 до артефактов (та же роль)

Продолжение после лимита итераций. Анализ и таксономия **готовы**, прототип в одной правке от зелёного. Не переписывать сделанное.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env.

## Уже на диске (проверено)
- `runtime/RS007/first_artifact.json` (PARTIAL), `answers/answers_taxonomy.json` (7 видов + SQL-предикаты), `answers/answers_leak.json` (политика: метаданные in-scope, текст не возвращается, анти-exists-oracle).
- `prototypes/rs007_pending.py`, `drivers/fresh_client.py`, `rs007_prototype.py`, `results/*.json`, `receipt/`.

## Точный остаток
1. **Одна правка порядка параметров** в `prototypes/rs007_pending.py` (~стр. 80–92): параметры должны идти в порядке появления `?` в тексте — сначала подзапросы (`work`, `work`), затем `IN (ветки)`, затем `after` (если есть), затем `limit+1`. Сейчас `sorted(grant)` передаётся первым, из-за чего `IN (?)` получает `work` → `visible=0`.
2. Перезапустить `python -E prototypes/rs007_prototype.py`; добиться `rc=0` по всем сценариям: `pos1` (новый процесс без памяти находит незавершённое **без подсказки**), `neg1/neg2/neg2b` (чужие/суженные гранты — ноль без маркеров), `empty` (`NO_PENDING`), `par*` (`REPLAY`/`REVISION_CONFLICT`). Пересчитать page-замеры perf после фикса (count'ы уже корректны).
3. Удалить `prototypes/debug_probe*.py` и `__pycache__`.
4. Записать `answers/answers_options.json` — пять вариантов (A resume-расширение, B отдельный инструмент, C материализация, D журнал, E внешний журнал) с числами: цена чтения, стоимость на 1/1k/100k, задержка `resume`, миграция, риск утечки, поведение при недоступной базе; вердикт с условиями применимости.
5. `answers/answers_contract.json` — коды (`NO_PENDING`, `PENDING_PRESENT`), поля (branch, candidate_id, operation, idem_key, digest, age/created_at, has_more), пагинация `limit`/`after`, миграция v2 (`created_at`), что делать с «вне базы».
6. `answers/answers_checks.json` — позитивный и негативные контроли с физическими фактами (файлы результатов).
7. `validate_rs007.py` + `validation_receipt.json` (exit 0 обязателен), затем `artifacts/RESEARCHER_RS007_UNFINISHED.json` и `reports/RESEARCHER_RS007_UNFINISHED.md` (раздел 0 «подозревал → проверил → оказалось» первым).

## Границы
Продукт/tests/tech_debt/конфиги/живой OMH/чужие artifacts — read-only; запись только `runtime/RS007/**`, `artifacts/RESEARCHER_RS007_UNFINISHED.json`, `reports/RESEARCHER_RS007_UNFINISHED.md`. Без Git/install/платных/субагентов/сети/секретов. `product_acceptance=false`, `is_approval=false`. Ориентир 25 вызовов: если не хватает — сначала артефакт и отчёт с честным остатком, потом стоп.

## Отчёт родителю
rc прототипа, число пройденных сценариев, sha256 артефакта и receipt, остаток если есть.
