# AB006 — worker: видимость незавершённой работы (вариант A)

Реализация W1 по контракту RS007. Продукт правится **здесь и только здесь**; чужие артефакты read-only.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env. Базовая версия: digest `ca227b17…` (16 файлов) — пересчитать до правок и записать.

## Входы (читать целиком, не пересказывать)
- `runtime/RS007/answers/answers_contract.json` — контракт: коды `NO_PENDING`/`PENDING_PRESENT`, поля (status, count, items, has_more; item: branch, candidate_id, operation, idempotency_key, intent_digest, review_id, state, age_seconds, payload_length, expected_branch_revision, dependencies, origin), пагинация, `migration_v2`, поведение «вне базы».
- `runtime/RS007/answers/answers_options.json` — почему выбран A (расширение `dom_resume`) и числа.
- `runtime/RS007/answers/answers_checks.json` — позитивные/негативные сценарии и физические файлы результатов.
- `runtime/RS007/answers/answers_leak.json` — политика: **метаданные in-scope, текст кандидата не возвращается никогда**.
- `runtime/RS007/prototypes/rs007_pending.py` — референс запроса (включая порядок параметров и index-требование).

## Что сделать
1. **Миграция v2** (`mockup/storage.py`): добавить неизменяемый `created_at` к кандидатам, `user_version`-гейт, `BEGIN IMMEDIATE`, пересоздание immutable-триггеров, идемпотентность повторного запуска. Индексы обязательны: без них на 100k задержка растёт в ~10.7×.
2. **Выдача** (`mockup/admission.py`, `mockup/public_dto.py`): секция pending в `dom_resume` по контракту — точный `count` (in-branch, `deps ⊆ grant`, не admitted), страница `items` только метаданными, `has_more`, `limit`/`after`.
3. **Отсутствие утечек**: `items` не содержат payload-текста; чужой грант не видит ни строк, ни маркеров (анти-exists-oracle: `count` тоже scope-фильтрован).
4. **HTTP/ошибки** (`mockup/server.py`): коды по контракту, никаких raw-исключений.

## Проверки (физические)
- **POS**: новый процесс без памяти (свой launcher, id не передаются) вызывает `dom_resume`/discovery и получает `count>0` + список метаданных; продолжение допускается; при конфликте ревизии — `REVISION_CONFLICT` с полями (expected vs head).
- **NEG**: чужой грант → пусто, без маркеров; суженный грант → только in-scope; admitted не выдаётся; повторный запуск миграции идемпотентен; 100k pending — задержка в пределах, зафиксированных в options.
- SQL-счётчики до/после, digest до/после, сырые кадры, копии БД только в `runtime/AB006/`.

## Выходы
`artifacts/WORKER_AB006.json` (`status`, `changed_files[]`, `digest_before/after`, `evidence[]`, `pos_results[]`, `neg_results[]`, `perf{}`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/WORKER_AB006.md`, `docs/SCHEMA_CHANGE_AB006.md`, `runtime/AB006/**`.

## Границы
Не трогать F-01/`delivery.py`, тесты, tech_debt, конфиги, OMH. Долги не закрывать. Без Git/install/платных/субагентов. При лимите/обрыве — continuation той же роли с точным остатком; родитель финал не дописывает. Ориентир 45 вызовов.
