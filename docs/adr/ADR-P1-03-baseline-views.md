# ADR-P1-03. `baseline_view` и `branch_event_view`

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p1-version-baseline`
- Долг: TD-DOM-40
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P1.3, D3

## Контекст

Baseline не должен быть материализованной таблицей: источник истины —
append-only `events`. Для baseline-чанков нужен branch-local номер только по
claim-событиям, а для recall — номер любого события, потому что archive и
replacement тоже меняют состояние и должны иметь границу воспроизведения.

## Решение

Две SQL-view в `storage.DDL`, создаваемые идемпотентно:

- `baseline_view` — только `kind='claim'`:
  `branch, seq, claim_id, prev_seq, chunk_hash, revision`;
  `seq = ROW_NUMBER() OVER (PARTITION BY branch ORDER BY seq)`,
  `prev_seq = seq - 1`, `chunk_hash = event_hash`.
- `branch_event_view` — все события:
  `branch, event_seq (глобальный), seq (branch-local), event_id, claim_id,
  kind, revision, chunk_hash, prev_seq`.
- `chunk_hash` — существующий `events.event_hash`, не случайный хеш и не хеш
  от payload на лету.

## Последствия

- Baseline детерминирован и пересчитывается из журнала.
- Recall может остановиться перед archive/replacement, не теряя границу.
- Материализация не нужна; при росте журнала появится benchmark (D3).
- Схема БД не меняется, v4 не требуется (см. ADR-P1-00).

## Проверка

- `test_baseline_view_is_deterministic_claim_chunks`: три claim-события дают
  `seq 1..3`, `prev_seq 0,1,2`, `chunk_hash == events.event_hash`, повторный
  запрос не меняет результат.
- `test_recall_replays_branch_events_and_stops_before_archive` использует
  `branch_event_view` для границ.
