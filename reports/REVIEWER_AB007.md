# RV007 — повторное ревью AB007 (пагинация) на версии `3cd21d96`

**Вердикт: CONFORM.** Все три находки RV006 (F1/F2/F3) закрыты, регрессии RS007/AB005 нет, `AU008-A-01` (недополнение) закрыт. Продукт **не принят** (`product_acceptance=false`) и не является одобрением — это пункт повторного ревью.

Продукт read-only; все записи — `runtime/RV007/**`, `artifacts/REVIEWER_AB007.json`, `reports/REVIEWER_AB007.md`.

---

## 1. Версия и дифференциальная проверка

Digest `3cd21d96ff2f83f014f00c3fdf5b21c6ef94c26525385ef6a014365387d8aad0` пересчитан **независимым** скриптом RV007 (не worker'овским): совпадает, 16 файлов.

Против `runtime/AU008/snapshot_c26812b3/**` пофайловым `cmp`: изменён **ровно `mockup/admission.py`** (DIFF), остальные 15 `mockup/**/*.py` идентичны (SAME). Совпадает с заявлением worker'а.

## 2. F1 — валидация курсора `after`

| after | результат |
|-------|-----------|
| `''` | REJECTED |
| `:x` | REJECTED |
| `AA:` | REJECTED |
| `AA:x:y` | REJECTED |
| `AA` | REJECTED |
| `123` (int) | REJECTED |
| `None` | RESUMED |
| `AA:<valid-uuid>` | RESUMED |

Проверено **двумя путями**: через guarded `Service.resume` (Python-обёртка) и через **сырой MCP stdio frame** (собственный клиент, initialize → tools/list → tools/call `dom_resume`). На проводе все мусорные курсоры → `REJECTED`, `valid`/`no_after` → `RESUMED`. Пустые компоненты и отсутствие `:` больше не проходят — F1 закрыт.

Примечание: `AA :x` (с пробелом) остаётся `RESUMED` — это осознанно задокументированное поведение (SCHEMA_CHANGE_AB007 §5), возвращает только in-грант строки (branch AB в гранте), чужое не раскрывает. Зафиксировано как fact/info, не уязвимость.

## 3. F2 — инвариант полного обхода

Инвариант «при `count>0` union страниц keyset-walk == полное видимое множество, каждая строка ровно один раз, без застревания» проверен на **5 собственных walk-ах** (суженный AA l1/l2, полный AA,AB l1/l2, AB l1):

```
walk_aa_limit1: union==ref dupes=0 stuck=false empty_midwalk=false last_has_more=false  PASS
walk_aa_limit2: union==ref dupes=0 ... PASS
walk_full_limit1: union==ref dupes=0 ... PASS
walk_full_limit2: union==ref dupes=0 ... PASS
walk_ab_limit1: union==ref dupes=0 ... PASS
```

Реализовано выбранным путём «фильтры видимости в SQL до LIMIT»: страница всегда наполнена видимыми строками, пустой mid-walk страницы при `count>0` не возникает, курсор от последнего элемента всегда продвигает. F2 закрыт.

## 4. F3 — `has_more` не сигналит о скрытых строках

В гранте AA, где в ветке AA существует deps-foreign кандидат c4 (`4f0ce33c…`), скрытый по зависимостям:
- `limit=2` при ровно 2 видимых строках → `has_more=FALSE` (не выдаёт существования скрытой строки) — F3 закрыт.
- `limit=1` → `has_more=TRUE` (это корректно: следующая **видимая** строка есть).
- **c4 никогда не появляется в items** на гранте AA (и не даёт счётчик).
- w3 (только admitted-кандидат) → `count=0`, `NO_PENDING` — завершённое не выдаётся.

## 5. Нет поведения вне контракта

- `next_cursor` **отсутствует** на сыром проводе: `top_keys == {count,has_more,items,page,status}`, `page == {after,limit}` точно (контракт RS007 сохранён, новое поле не введено).
- Чужой `branch:id` курсор не раскрывает ино-грант данные (проверено `AA :x` и полные walk-и: все возвращаемые branch ∈ грант).
- Пустая страница при `count>0` в mid-walk невозможна (все walk `empty_midwalk=false`).

## 6. Регрессия RS007 + AB005

- Контракт: top/page keys точны, статусы ∈ {NO_PENDING, PENDING_PRESENT}, состояние ∈ {AWAITING_REVIEW, REVIEWED}, item-поля metadata-only.
- Границы `limit`: `1`/`500` OK, `0`/`501`/`'3'`/`true` → REJECTED.
- **Анти-oracle count**: `AA=2, AB=1, AA_AB=4` — каждое равно перечислимой мощности полного видимого множества (count не зависит от страницы).
- admitted исключён; payload-текст/`body_b64`/`source_ref`/`"payload"` не утекают.
- `NO_SUCH_BRANCH` (granted-but-absent `CC`), `SCOPE_DENIED` (вне-грант `AB` при гранте AA), `DIGEST_MISMATCH` (review и admit с неверным digest) — целы.
- **Миграция v2 идемпотентна**: legacy `init` OK, повторный `init` OK, снапшот схемы (uv=2, колонки candidates с `created_at`, 2 индекса, 39 immutable-триггеров) идентичен после рерана.

## 7. AU008-A-01 (недополнение при limit=2) — закрыт

Воспроизведён прежний сценарий на фикстуре `w6` (ветка AA, суженный грант): раньше `limit=2 → items=1` (недополнение). Теперь `limit=2 → items=2, count=2, has_more=false` — страница полностью наполнена. `closed_no_underfill=true`.

---

## Итог

| Пункт | Результат |
|-------|-----------|
| digest 3cd21d96 + diff (только admission.py) | PASS |
| F1 курсор → REJECTED / RESUMED (Python + raw MCP) | PASS |
| F2 полный walk-инвариант (5 комбинаций) | PASS |
| F3 has_more не сигналит о скрытых | PASS |
| нет поведения вне контракта (нет next_cursor, page keys exact, чужое не раскрывается) | PASS |
| регрессия RS007 + анти-oracle count + admitted + текст + NO_SUCH_BRANCH/SCOPE_DENIED/DIGEST_MISMATCH + миграция v2 | PASS |
| AU008-A-01 закрыт | PASS |

`product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`.

Наблюдения (не блокеры): `AA :x` (пробел) принимается как keyset-позиция (осознанно, in-грант, без утечки) — зафиксировано как info.