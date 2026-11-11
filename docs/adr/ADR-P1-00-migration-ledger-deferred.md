# ADR-P1-00. Migration ledger отложен до первой v4-схемы

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p1-version-baseline`
- Долг: TD-DOM-37

## Контекст

TD-DOM-37 требует `_migrate_vN + ledger` и DOWN-миграции. P1 закрывает
`commit_ref`, производные версии, baseline-view, recall и diff. Ни один из
этих пунктов не добавляет колонку или таблицу:

- `commit_ref` — поле metadata в JSON, схема БД не меняется;
- `version`/`logical_claim_id`/`supersedes` — производные значения из
  replacement-цепочки, колонок нет (D2);
- baseline — SQL-view;
- recall/diff — чтение существующих `events`/`claims`.

## Решение

Не вводить v4 и ledger в P1. `baseline_view` и `branch_event_view` создаются
идемпотентно через `CREATE VIEW IF NOT EXISTS` в `storage.DDL`, поэтому
существующая БД получает их при следующем `initialize` без `user_version`
bump. Ledger/DOWN вводится вместе с первой реальной v4-миграцией, когда
появится объект, который нельзя создать идемпотентно.

## Последствия

- Нет фиктивной миграции «на будущее» и риска сломать v1/v2/v3.
- TD-DOM-37 остаётся открытым с явным триггером: первая v4-схема.
- View не входит в `IMMUTABLE`-матрицу: это не таблица и не источник истины.

## Проверка

- `tests/test_p1_version_baseline.py::test_baseline_view_is_deterministic_claim_chunks`
  проверяет view на существующей схеме.
- Полный прогон: 90 passed; demo exit 0.
