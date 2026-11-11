# ADR-P1-02. Производные `version`, `logical_claim_id`, `supersedes`

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p1-version-baseline`
- Долг: TD-DOM-38
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P1.2, D2

## Контекст

`dom_update` сначала создаёт новый claim и только потом пишет replacement-
событие. В момент вставки claim родитель (старая версия) ещё не известен,
поэтому хранить `version`/`supersedes` колонками нельзя без второго пакета
`replace` или временно неверного значения.

## Решение

- `_children(c)` даёт карту `old claim -> replacement claim` по событиям
  `kind='replacement'`; `_lineage(children)` — корень цепочки и глубину.
- `supersedes` — непосредственный родитель (`new -> old`), у корня `None`.
- `Claim` DTO и `dom_find` отдают `version`, `logical_claim_id` (корень
  цепочки) и `supersedes`; `dom_claim`/`dom_update` добавляют
  `logical_claim_id` в ответ.
- Колонки не добавляются; схема БД не меняется.
- Используется существующая глобальная карта replacement-событий. Разделение
  цепочек по fork-веткам остаётся задачей P3 (`branch_forks`).

## Последствия

- DTO всегда согласован с `_lineage`; нет дрейфа «колонка vs история».
- История версий доступна без материализации.
- Для веток с независимыми replacement одного claim глобальная карта может
  выбрать первое событие; это известное ограничение до P3.

## Проверка

- `test_version_logical_id_and_supersedes_are_derived`: после update
  `version=2`, `logical_claim_id=root`, `supersedes=old`; старая версия —
  `version=1`, `supersedes=None`.
- `test_claim_versions_follow_the_replacement_chain` проверяет ту же цепочку
  через отдельный инструмент.
