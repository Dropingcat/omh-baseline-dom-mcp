# RV005 — reviewer: WS-F04 + WS-F02 на версии `ca227b17`

Роль REVIEWER (H/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md). Проверяешь соответствие реализации карте и контракту RS006, а не «нравится/не нравится». Приёмка срезов **раздельная**: F-04 и F-02 оцениваются отдельно, один не прикрывает другой. Продуктовое решение не принимаешь (`product_acceptance=false`), долги не закрываешь.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env.

## Версия и объект проверки
Код: digest `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7` (16 файлов, метод: sha256 от json.dumps(sorted relpath→sha256, sort_keys)). Изменены заявленно только `mockup/admission.py`, `mockup/storage.py`.

## Входы
`cards/AB005_F04_F02_WORKER.md` (что требовалось), `artifacts/WORKER_AB005.json`, `reports/WORKER_AB005.md`, `docs/SCHEMA_CHANGE_AB005.md`, `runtime/AB005/**` (p_f04.py, p_f02.py, results/, raw frames, legacy-фикстуры), `runtime/RS006/answers_f02.json`, `runtime/RS006/planning_RS006.json` (order, must_not_merge, negative_sets), `docs/DECISION_BRIEF_2026-11-08.md` (согласованное направление L1+L2).

## Что проверить по существу
**WS-F04:** типизированный `NO_SUCH_BRANCH` на query/resume/sync_status/sync/trace/export; `SCOPE_DENIED` вне гранта; нет `INTERNAL_ERROR`; нет ложного `SYNCED`; AA-путь не изменился.
**WS-F02:** порядок `candidate → L1 digest до кеша → L2 dedupe(binding) → review → remember`; PK `(work, operation, key, scope_digest)`; арбитр `result_scope ⊆ grant`; `submit` тоже привязан; миграция `user_version`-гейт, `BEGIN IMMEDIATE`, legacy-строки инертны (`scope_digest=''`, binding NULL), immutable-триггеры пересозданы и реально блокируют UPDATE/DELETE.
**Обязательное:** позитивный контроль N-F02-3 — повтор даёт **байт-равную** квитанцию и нулевые дельты по tx/events/outbox/attempts/acks/idempotency. Если этого нет — REQUEST_CHANGES независимо от остального.
**Отдельно оценить:** не вводит ли фикс нового поведения, которого не было в контракте (например, подмену статуса повтора), и не ослаблены ли проверки `review`.

## Требования к собственной работе
- Пересчитать digest самому, а не поверить артефакту; сверить sha256 evidence-файлов.
- Проверить, что `delivery.py`, `public_dto.py`, `server.py`, `tests/`, `tech_debt.md`, OMH **не изменены**.
- Прогнать свои независимые пробы на изолированной копии БД в `runtime/RV005/` (свои, не переиспользовать скрипты worker'а как есть — минимум один собственный сценарий на каждый срез).
- Различать «не проверял» и «проверил, всё хорошо»: список NOT_CHECKED обязателен.

## Выходы
`artifacts/REVIEWER_AB005.json` (`decision`: APPROVE | REQUEST_CHANGES, `slices[]{id, decision, checks[], evidence_refs[], sha256}`, `own_runs`, `not_checked`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/REVIEWER_AB005.md`, `runtime/RV005/**`.

## Границы
Read-only по продукту; никаких правок кода, тестов, долгов, конфигов. Без Git/install/платных/субагентов/секретов. Ориентир 30 вызовов. При лимите/обрыве — continuation той же роли с точным остатком.
