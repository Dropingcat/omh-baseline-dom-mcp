# ADR-P0-04. Инвариант claim ↔ snapshot

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p0-invariants`
- Долг: TD-DOM-36
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P0.4

## Контекст

`admit` вставляет `claims` и `claim_snapshots` в одной транзакции, но связка
была записана двумя соседними `INSERT` без явного инварианта и без теста.
SQLite-триггер `AFTER INSERT ON claims` не может заполнить `dependencies` и
`review_id`: они приходят из envelope допуска, а не из `claims.payload`.

## Решение

- `Service._record_claim(c, claim_id, ..., p, item, revision, review_id)`
  вставляет claim и snapshot одной парой; `admit` вызывает только его.
- `claim_snapshot_gaps(c)` — read-only SQL-проверка:
  `claims LEFT JOIN claim_snapshots WHERE snapshot IS NULL`.
- DB-level enforcement (триггер/представление) отложен: без envelope-колонок
  он либо не сможет восстановить значения, либо потребует дублирования
  `dependencies`/`review_id` в `claims`. Вернуться к нему при следующей
  миграции, если появится дешёвый способ.

## Последствия

- Инвариант выполняется по построению на единственном пути записи.
- Будущий обход (прямой `INSERT INTO claims`) виден через
  `claim_snapshot_gaps` и тест.
- Схема БД не менялась; миграция не требуется.

## Проверка

- `test_every_claim_has_exactly_one_snapshot` — 2 claims / 2 snapshots,
  `claim_snapshot_gaps == []`.
- `test_snapshot_gap_checker_sees_a_bypassing_insert` — прямой INSERT claim без
  snapshot возвращает `['gap-claim']`.
