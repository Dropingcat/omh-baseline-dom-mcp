# ADR-P0-02. Внешний эффект sync вне read-транзакции

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p0-invariants`
- Долг: TD-DOM-34
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P0.2

## Контекст

`sync` держал `store.read()` вокруг `OMHPort.read_target/attach` и записи YAML.
При `journal_mode=DELETE` открытая read-транзакция не даёт писателю выполнить
`COMMIT`; после `busy_timeout=2000` он получает `STORAGE_BUSY`. Медленный или
недоступный OMH блокировал запись в DOM на всех ветках.

## Решение

Для каждого outbox-интента три фазы:

1. **Попытка:** короткая write-транзакция — `integrity_gate`, проверка
   `confirmed`, вставка `delivery_attempts`.
2. **Эффект:** без транзакции — `read_target`/`attach`/read-back или запись
   YAML-файла. Байты YAML готовятся в короткой read-транзакции, файл пишется
   после её закрытия.
3. **Наблюдение:** короткая write-транзакция — повторный `integrity_gate`,
   вставка `delivery_observations`, `ack` только при `exact` и
   `report != 'ambiguous'`.

Outbox-интент и журнал событий иммутабельны; `attach` идемпотентен по
`(target, tx)`. Если процесс умер между эффектом и наблюдением, остаётся
`delivery_attempt` без observation — это сигнал для reconcile, а не ложный ack.

`export` также вынес файловую запись за пределы read-транзакции.

## Последствия

- Writer на другой ветке не ждёт OMH и завершает `admit`.
- Возможен разрыв «эффект выполнен, наблюдение не записано»; он виден как
  pending/ambiguous и закрывается повторным `sync`/reconcile.
- `read_at` наблюдения фиксируется в момент записи, а не до внешнего вызова.

## Проверка

`tests/test_p0_invariants.py::test_sync_does_not_hold_a_read_transaction_across_external_io`:
медленный `OMHPort.read_target` удерживается, параллельный `admit` на AB
возвращает `DEMO_ADMITTED` (до фикса — `STORAGE_BUSY`), затем `sync` — `SYNCED`.
