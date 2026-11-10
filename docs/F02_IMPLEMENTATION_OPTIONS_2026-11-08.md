# F-02: варианты технической реализации (scope-bound cached receipt)

Статус: проектные предложения для RS006/AB005. Не реализовано, код не менялся. Версия: `1ead2d45…`.

## 1. Фактическая причина (по коду)

`mockup/admission.py`:
- `112–117 dedupe()` — ищет запись в `idempotency` по `(external_work_ref, operation, key)`; при совпадении `digest` возвращает сохранённый `result` целиком.
- `117 remember()` — пишет `(work, operation, key, digest, result)`; в таблице **нет** ни кандидата, ни ревью, ни ветки, ни области.
- `179–181 admit()` — порядок: `candidate()` (проверяет только ветку кандидата) → **`dedupe()`** → и лишь затем `row['digest']!=intent_digest`.

Отсюда дефект: вызывающий предъявляет **свой AA-кандидат** (ветка в гранте — проверка проходит), но **чужой AB `key`+`digest`**. Кеш срабатывает до сравнения digest кандидата, поэтому возвращается AB-квитанция.

`mockup/storage.py:24` — `idempotency` входит в `IMMUTABLE` с ключом `(external_work_ref, operation, key)`; строки нельзя ни обновить, ни удалить (триггеры). Значит привязку области нужно добавлять **новыми колонками при миграции**, а не правкой старых.

## 2. L1 — перепорядок проверок (минимум, без миграции)

Сравнить digest кандидата с предъявленным **до** обращения к кешу.

```python
with self.store.transaction() as c:
    row,p=self.candidate(c,candidate_id)          # scope(row['branch']) уже есть
    if row['digest']!=intent_digest or digest(p)!=intent_digest:
        raise Denied('DIGEST_MISMATCH')           # ← до dedupe()
    old=self.dedupe(c,'admit:'+self.context.principal,idempotency_key,intent_digest)
    if old: return old
```

Что закрывает: AA-кандидат + AB-digest → `DIGEST_MISMATCH`, квитанция не выдаётся. Настоящий AB-кандидат падает раньше на `candidate()` → `SCOPE_DENIED`.

Цена: 3 строки, без схемы. Риск для легального повтора: нулевой — повтор идёт с тем же кандидатом и тем же digest.

Чего **не** закрывает: если кандидат и digest согласованы, но запись кеша относится к другой области (например, кандидат допущен в AA, а ключ от операции в AB с тем же digest — теоретически при совпадении содержимого и автора). Нужен L2.

## 3. L2 — привязать запись кеша к операции (defence in depth)

Миграция `idempotency` (новые колонки, старые строки → NULL):

```sql
ALTER TABLE idempotency ADD COLUMN candidate_id TEXT;
ALTER TABLE idempotency ADD COLUMN review_id TEXT;
ALTER TABLE idempotency ADD COLUMN branch TEXT;
ALTER TABLE idempotency ADD COLUMN scope_digest TEXT;   -- sha256 отсортированных веток гранта
ALTER TABLE idempotency ADD COLUMN result_scope TEXT;   -- ветка, к которой относится result
```

`dedupe` получает ожидаемую привязку и сверяет её, а не только digest:

```python
def dedupe(self,c,operation,key,d,binding=None):
    r=c.execute('SELECT * FROM idempotency WHERE external_work_ref=? AND operation=? AND key=?',
                (self.context.work,operation,key)).fetchone()
    if not r: return None
    if r['digest']!=d: raise Denied('IDEMPOTENCY_MISMATCH')
    if r['candidate_id'] is None: raise Denied('IDEMPOTENCY_BINDING_UNKNOWN')   # legacy
    if binding and (r['candidate_id'],r['branch'])!=binding:
        raise Denied('IDEMPOTENCY_BINDING_MISMATCH')
    if r['scope_digest']!=self.scope_digest(): raise Denied('SCOPE_DENIED')     # грант сузился
    return json.loads(r['result'])
```

Требования к поведению:
- **Legacy-строки не воспроизводятся молча.** NULL-привязка → типизированный отказ; повторная легальная операция выполняется заново, а не отдаётся из кеша.
- **`scope_digest` считается из фактического гранта** (`sha256('\n'.join(sorted(branches)))`), а не из строки роли.
- **Ничего не переписывать в immutable-таблицах** — только новые колонки/строки.
- `result_scope` пишется при `remember`, проверяется при выдаче: `result_scope ∈ grant`, иначе отказ, а не урезание.

Цена: миграция + 2 функции. Риск: увеличивается число отказов у старых кешей — это ожидаемо и безопасно (повтор вместо тихой выдачи).

## 4. L3 — проецировать кешированный результат (не рекомендую как основное)

На попадании в кеш прогонять `result` через `public_dto` с текущим scope и отдавать урезанную квитанцию.

Почему отклоняю: урезанная квитанция всё равно подтверждает «у вас была операция в AB» — это тот же класс сигнала, что O1. Кроме того, она создаёт ложное впечатление успешного повтора. Если операция не воспроизводима в текущей области — нужен явный отказ, а не косметика.

## 5. L4 — отдельный явный путь воспроизведения (опционально)

`dom_replay(receipt_ref, reason)` с обязательной авторизацией, записью события в append-only журнал и явным указанием, что это воспроизведение, а не новый допуск. Полезно для UI восстановления после потерянного ответа; `admit` при этом никогда не отдаёт результат вне области.

## 6. Рекомендация

**L1 + L2 вместе.** L1 — немедленно (закрывает воспроизведение, ноль миграции), L2 — в том же срезе (не даёт дефекту вернуться через другой путь и покрывает случай совпадающего digest). L4 — только если появится пользовательский сценарий восстановления; L3 не делать.

## 7. Проверки (негативные и положительные)

| # | Сценарий | Ожидание | Физическое доказательство |
|---|---|---|---|
| 1 | AA-кандидат + прежние AB key/digest | `DIGEST_MISMATCH`, квитанции нет | raw frames, 2 PID |
| 2 | Реальный AB-кандидат при гранте AA | `SCOPE_DENIED` (уже работает) | raw frames |
| 3 | Легальный потерянный ответ: тот же кандидат/ключ/digest/грант | тот же receipt, **без** новых tx/events/outbox | SQL counts до/после |
| 4 | Тот же ключ, другой digest | `IDEMPOTENCY_MISMATCH` | raw |
| 5 | Грант сужен, затем восстановлен | отказ → после восстановления повтор разрешён | raw ×2 |
| 6 | Другой principal с тем же ключом | `IDEMPOTENCY_MISMATCH` | raw |
| 7 | Legacy-строка без привязки | `IDEMPOTENCY_BINDING_UNKNOWN`, не выдача | миграционный фикстур |
| 8 | Повтор не создаёт побочных эффектов | outbox/attempts/acks не растут | SQL counts |

Пункт 3 — обязательный положительный контроль: любое исправление, ломающее восстановление после потерянного ответа, недопустимо.

## 8. Связь с F-01

F-02 и F-01 трогают разные объекты: F-02 — кеш допуска, F-01 — идентичность доставки (outbox/ack). Их можно делать в одном срезе, но принимать раздельно: закрытие F-02 не должно засчитываться как закрытие F-01 и наоборот.
