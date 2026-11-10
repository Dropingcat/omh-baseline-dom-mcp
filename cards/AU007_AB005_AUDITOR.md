# AU007 — auditor: негативная приёмка WS-F04 + WS-F02 на версии `ca227b17`

Роль AUDITOR. Твоя задача — **не подтвердить, а опровергнуть**. Ищешь, что осталось недоделанным, что заявлено но не доказано, и где фикс можно обойти. Приёмка срезов раздельная. `product_acceptance=false`, долги не закрываешь.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env.

## Версия
`ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7` (16 файлов). Заявленно изменены только `mockup/admission.py`, `mockup/storage.py`.

## Входы
`cards/AB005_F04_F02_WORKER.md`, `artifacts/WORKER_AB005.json` (заявления), `runtime/AB005/**` (их доказательства), `runtime/RS006/planning_RS006.json` (`negative_sets.f02`, `must_not_merge`), `artifacts/AUDITOR_AB004_AU004F01.json` (что было сломано раньше), `docs/DECISION_BRIEF_2026-11-08.md`.

## Чек-лист негативной приёмки (по каждому — физический факт, не рассуждение)
1. **Повтор исходного дефекта:** AA-кандидат + прежние AB key/digest при гранте {AA} → обязан быть `DIGEST_MISMATCH`, квитанции нет, после вызова нет новых строк claims/transactions. Проверить на **двух разных PID**.
2. **Обход через другой путь:** `submit` + `admit`, разные operation-префиксы, другой principal, тот же key — не должно быть выдачи чужой квитанции.
3. **Миграция:** на копии БД со старыми строками — legacy выдаётся как `IDEMPOTENCY_BINDING_UNKNOWN`, строка **не** изменена и **не** удалена; после легального повтора создаётся новая строка, а не переиспользуется старая; `user_version` корректен; повторный запуск миграции идемпотентен.
4. **Immutable-триггеры:** `UPDATE`/`DELETE` по `idempotency` реально падают после миграции (не только «мы их пересоздали»).
5. **Арбитр `result_scope ⊆ grant`:** безопасное сужение → повтор разрешён; опасное сужение → `SCOPE_DENIED`; восстановление гранта → повтор разрешён. Проверить, что «разрешён» не означает выдачу данных вне гранта.
6. **Позитивный контроль:** законный потерянный ответ → байт-равная квитанция, **нулевые** дельты (tx, events, outbox, delivery_attempts, acks, idempotency). Считать SQL до/после.
7. **F-04:** `NO_SUCH_BRANCH` на всех заявленных поверхностях; отсутствие `INTERNAL_ERROR`; отсутствие ложного `SYNCED`; AA-путь без регрессии; поведение при ветке, которая существует в гранте, но пуста.
8. **Границы:** `delivery.py`, `public_dto.py`, `server.py`, `tests/`, `tech_debt.md`, OMH не изменены; digest совпадает с заявленным; `product_acceptance=false`.
9. **Что не проверено исполнителем и заявлено как проверенное** — искать расхождения между отчётом и рантаймом (признак: файл-доказательство отсутствует или его sha не совпадает).

## Обязательные разрушительные пробы
Только на изолированных копиях БД в `runtime/AU007/`. Проверить поведение при: повреждённой строке `result` (невалидный JSON), `scope_digest=''` у старой строки, отсутствии `idempotency`-таблицы при старте, конкурентном запуске двух процессов на одной БД (последовательная сериализация не считается доказательством — отметить честно, если не воспроизводилось).

## Выходы
`artifacts/AUDITOR_AB005.json` (`verdict`: APPROVE | REQUEST_CHANGES, `status`: COMPLETE | COMPLETE_WITH_LIMITS, `findings[]{id, severity, invariant, repro, expected, actual, evidence}`, `own_runs[]` с sha256, `not_checked[]`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/AUDITOR_AB005.md`, `runtime/AU007/**` (raw frames, SQL readback, copies of DB, verify.py).

## Границы
Read-only по продукту. Ничего не править, не «улучшать», не закрывать долги. Без Git/install/платных/субагентов/секретов/live OMH. Ориентир 45 вызовов. При лимите/обрыве — continuation той же роли с точным остатком.
