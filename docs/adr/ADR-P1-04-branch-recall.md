# ADR-P1-04. `dom_recall`: branch-local replay без task_path

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p1-version-baseline`
- Долг: TD-DOM-41
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P1.4

## Контекст

Recall должен воспроизвести состояние ветки до branch-local seq, включая
границу непосредственно перед archive/replacement. `task_path`-фильтр из
аудита опирается на `task_claims`, которых ещё нет до P2. Исторические
`pending`-кандидаты также не восстановимы: candidates/reviews не являются
событиями и не имеют `events.seq`.

## Решение

- `projections.snapshot_at_seq(c, branch, at_seq)` переводит branch-local seq
  в глобальный `events.seq` через `branch_event_view` и фильтрует
  `seq <= global_seq`.
- `at_seq=0` — пустой baseline; `at_seq > head` — `REVISION_OUT_OF_RANGE`.
- `admission.recall(branch, at_seq)` возвращает `active_claims`,
  `archived_claims`, `pending_decisions`, `resolved_conflicts`,
  `related_branches`, `as_of`, `baseline_range`, `read_snapshot`.
- `resolved_conflicts` считается по событиям `conflict`/`resolve` до границы.
- `related_branches` — ветки, получившие `applicability` для активных claim
  до границы, плюс зависимости, кроме текущей ветки.
- `pending_decisions` — `null`: историческое pending не восстанавливается из
  append-only журнала. Поле остаётся в контракте, чтобы P2 могло заполнить
  его, когда кандидаты станут событиями.
- `task_path`/`include_children`/`role` не входят в P1-сигнатуру: membership
  появится вместе с `task_claims` в P2; добавление опциональных аргументов
  не ломает текущих клиентов.

## Последствия

- Recall честно воспроизводит claim-состояние и архив на любой границе.
- Не выдаёт ложное «pending» и не притворяется, что task-фильтр реализован.
- TD-DOM-41 закрыт в P1-scope; task-scoped recall остаётся частью P2.

## Проверка

- `test_recall_replays_branch_events_and_stops_before_archive`: до replacement
  обе версии активны, после — старая в `archived_claims`; `at_seq=0` пуст;
  выход за голову — `REVISION_OUT_OF_RANGE`.
- `test_recall_reports_related_branches_and_resolved_conflicts`: `AB` виден
  через applicability; конфликт появляется в `resolved_conflicts` только
  после `resolve`.
