# ADR-P1-01. `commit_ref` как опциональное поле code-клайма

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p1-version-baseline`
- Долг: TD-DOM-39
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P1.1

## Контекст

`TYPE_FIELDS['code']` перечисляет обязательные поля. Если добавить
`commit_ref` туда, каждый старый code-клайм без коммита станет невалидным.
`commit_ref` нужен только тогда, когда код действительно привязан к коммиту.

## Решение

- `dom_contract.OPTIONAL_FIELDS = {'code': {'commit_ref': dict}}`.
- `fields()` принимает `optional`: отсутствующий ключ допустим, присутствующий
  проверяется по типу; unknown keys по-прежнему отвергаются.
- `valid_commit_ref()` требует закрытую форму:
  `hash` — 40 или 64 hex, `branch` — непустая строка; `author`, `message`,
  `committed_at` — необязательные непустые строки; лишние ключи запрещены.
- Lite: `commit_ref` добавлен в `FIELD_TYPES`/`TYPE_ARGS['code']`; ошибка
  формы возвращает `INVALID_FIELD` с `field='commit_ref'`.
- Strict: та же проверка в `dom_contract.validate`; ошибка — `INVALID_TYPE`
  на `metadata.commit_ref`.
- `dom_update` не переносит `commit_ref` в новую версию: новый текст не
  является содержимым старого коммита.

## Последствия

- Старые code-клаймы без `commit_ref` продолжают проходить.
- Коммит нельзя «приклеить» к изменившемуся телу через update; нужен новый
  claim с новым `commit_ref`.
- Схема БД не менялась.

## Проверка

- `test_code_claim_without_commit_ref_still_admits`
- `test_code_claim_with_valid_commit_ref_is_stored`
- `test_invalid_commit_ref_is_refused` (3 формы)
