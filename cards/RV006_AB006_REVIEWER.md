# RV006 — reviewer: видимость незавершённого (W1) на версии `c26812b3`

Роль REVIEWER. Проверяешь соответствие контракту RS007 и отсутствие регрессий, а не «нравится/не нравится». `product_acceptance=false`, долги не закрываешь.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env.

## Версия
`c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505` (16 файлов). Метод: `sha256(json.dumps({'mockup/<posix>': sha256}, sort_keys=True))`. Пересчитай сам.

## Входы
`cards/AB006_PENDING_VISIBILITY_WORKER.md`, `cards/AB006_CONTINUE_02.md`, `artifacts/WORKER_AB006.json`, `reports/WORKER_AB006.md`, `docs/SCHEMA_CHANGE_AB006.md`, `runtime/AB006/**`, контракт `runtime/RS007/answers/answers_contract.json` + `answers_leak.json` + `answers_checks.json`, `docs/DECISION_BRIEF_2026-11-08.md` (O2).

## Что проверить
1. **Контракт**: коды `NO_PENDING`/`PENDING_PRESENT`; поля `status/count/items/has_more`; item-поля ровно по контракту; `limit` 1..500 и `after` формата `branch:id` с типизированным `REJECTED`, без raw-исключений.
2. **Точность**: `count` — точное число in-scope незавершённых, не зависит от страницы; admitted исключён; deps вне гранта исключены.
3. **Ключевое**: `count` не является exists-oracle — при суженном гранте он не должен позволять вывести наличие скрытых строк. Проверь на нескольких усечениях гранта.
4. **Утечки**: `items` не содержат payload-текста, чужих идентификаторов, производных счётчиков; проверить на кадрах.
5. **Миграция**: `user_version`-гейт, `MIGRATION_REQUIRED` вместо тихой перестройки, идемпотентность, 39 immutable-триггеров, два индекса.
6. **Регрессия AB005**: `NO_SUCH_BRANCH` и привязка `idempotency` (L1 до кеша, binding, `result_scope ⊆ grant`) продолжают работать — прогони хотя бы по одному сценарию каждого.
7. **Недополнение страницы**: `has_more` = предфильтровый `limit+1`; подтверди, что это документировано и не выдаёт ложного «больше нет» там, где `count` больше страницы.

## Свои пробы
Минимум по одному собственному сценарию на пункты 1–6 в `runtime/RV006/`, свой лончер, свои фикстуры, сырые кадры. Не переиспользовать скрипты worker'а как есть.

## Выходы
`artifacts/REVIEWER_AB006.json` (`decision`, `checks[]`, `evidence_refs[]` с sha256, `own_runs`, `not_checked[]`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/REVIEWER_AB006.md`, `runtime/RV006/**`.

## Границы
Read-only по продукту. Без Git/install/платных/субагентов. Ориентир 30 вызовов. При обрыве — continuation той же роли с точным остатком.
