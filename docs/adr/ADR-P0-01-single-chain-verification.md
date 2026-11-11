# ADR-P0-01. Одно вычисление цепочки на чтение

- Статус: Accepted
- Дата: 2026-11-11
- Ветка: `arch/p0-invariants`
- Долг: TD-DOM-33
- Аудит: `docs/AUDIT_2026-11-11_ARCHITECTURE_ANALYSIS.md` §P0.1

## Контекст

`trace` и `resume` вызывали `integrity_gate(c)` (первый `verify_chain`) и затем
`_trace(c, branch)` (второй `verify_chain`). При росте журнала это удваивало
O(N) проверку на каждом чтении. `query` уже проверял цепочку один раз.

## Решение

`Service.integrity(c)` возвращает пару `(stamp, chain)`; `integrity_gate(c)`
остаётся обёрткой для существующих вызовов. `_trace(c, branch, chain=None)`
принимает уже вычисленную цепочку и не проверяет её повторно. `trace` и
`resume` используют `integrity()` и передают `chain` в `_trace`.

Публичный DTO цепочки не меняется: `public_dto.chain` по-прежнему отдаёт
только `status`; `head_hash`, число событий и локаторы остаются внутренними.

## Последствия

- Одна проверка на `trace`, `resume`, `query`.
- `sync` сохраняет несколько проверок по фазам (перед попыткой, перед записью
  наблюдения) — это отдельная защита, не дублирование одного чтения.
- Прямые вызовы `_trace` без `chain` остаются корректными (проверка внутри).

## Проверка

`tests/test_p0_invariants.py::test_trace_and_resume_verify_chain_once`:
monkeypatch `admission.verify_chain`, счётчик равен 1 для `trace`, `resume` и
`query`.
