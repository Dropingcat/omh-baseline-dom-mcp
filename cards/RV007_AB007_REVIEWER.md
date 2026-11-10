# RV007 — повторное ревью после фикса пагинации (версия `3cd21d96`)

Роль REVIEWER. Проверяешь, что F1–F3 действительно закрыты и ничего не сломано. Продукт read-only.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env.

## Версия
`3cd21d96ff2f83f014f00c3fdf5b21c6ef94c26525385ef6a014365387d8aad0`. Пересчитай сам документированным методом; подтверди, что против `c26812b3…` изменён **только** `mockup/admission.py` (сравни с `runtime/AU008/snapshot_c26812b3/**`).

## Входы
`cards/AB007_PAGINATION_FIX_WORKER.md`, `artifacts/REVIEWER_AB006.json` (F1/F2/F3), `artifacts/AUDITOR_AB006.json` (в т.ч. `AU008-A-01` про недополнение), `docs/SCHEMA_CHANGE_AB007.md`, `runtime/AB007/results/*`, `runtime/AU008/snapshot_c26812b3/**`, контракт `runtime/RS007/answers/answers_contract.json`.

## Что проверить своими пробами
1. **F1**: `after` = `''`, `:x`, `AA:`, `AA:x:y`, `AA`, `123` → типизированный `REJECTED`; `None` и валидный `AA:<uuid>` → `RESUMED`; проверить на сыром MCP-кадре, не только через Python-обёртку.
2. **F2 — инвариант**: при `count > 0` обход по курсору обязан выдать **все** видимые строки ровно по одному разу. Проверить минимум на четырёх комбинациях (суженный грант, `limit=1`, `limit=2`, полный грант): union страниц == полный набор, дублей 0, застреваний (`items=[]` при `has_more=true` без курсора) нет.
3. **F3**: при строках, скрытых по зависимостям, `has_more` не сигнализирует об их существовании; на границе ровно `limit` видимых строк `has_more=false`.
4. **Нет ли нового поведения вне контракта**: `next_cursor` (если появился) не должен раскрывать чужие `branch:id`; пустая страница при `count>0` недопустима.
5. **Регрессия**: контракт RS007 (коды/поля/границы `limit`), точный анти-oracle `count`, admitted исключён, текст не отдаётся, `NO_SUCH_BRANCH`/`SCOPE_DENIED`/`DIGEST_MISMATCH`, миграция v2 идемпотентна.
6. **Закрыт ли `AU008-A-01`** (недополнение страницы при `limit=2`): воспроизведи прежний сценарий — он больше не должен давать пустую страницу.

## Выходы
`artifacts/REVIEWER_AB007.json` (`decision`, `checks[]`, `evidence_refs[]` с sha256, `own_runs`, `findings[]`, `not_checked[]`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/REVIEWER_AB007.md`, `runtime/RV007/**` (свои пробы и сырые кадры).

## Границы
Read-only по продукту. Не переиспользовать скрипты worker'а как есть — минимум одна собственная проба на каждый пункт. Без Git/install/платных/субагентов. Ориентир 30 вызовов; при обрыве — continuation с точным остатком.
