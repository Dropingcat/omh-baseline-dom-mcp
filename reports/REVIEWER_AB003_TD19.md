# RV004 — независимый review TD-DOM-19 fix

**APPROVE только для TD-DOM-19 на точной версии `08aa9a9b…`. Блокирующих продуктовых находок нет.**
`product_acceptance=false`, `is_approval=false`, `completion_state=completed`. Это не приёмка всей системы, не разрешение закрывать OMH-задачу и не замена следующего независимого аудита.

Основной вердикт: `artifacts/REVIEWER_AB003_TD19.json`.
Собственное evidence: `runtime/RV004/run-aa-7107b/`, манифест — `runtime/RV004/master-manifest.json`, ledger — `runtime/RV004/source-ledger.json`.

## 0. Подозревал → проверил → оказалось (probe-баги и устаревший тест)

Первый прогон меня как ревьюера дал FAIL/тревоги не по продукту, а по дефектам моего собственного проб-хара и одной предсуществующей тестовой заготовке. Всё ниже — **не** продуктовые утечки; после исправления проб-хара прогон зелёный 5/5.

| # | Подозревал | Проверил | Оказалось / исправление |
|---|---|---|---|
| 1 | Поле `reason` в ответе — утечка | RS002 `public_schemas` дословно | `reason` — **легальное** поле RS002, не leak-ключ; убрал из `LEAK_KEYS`. Утечки нет. |
| 2 | На A2-03 БД меняется во время gate | Момент снятия `db_sha` | Хеш снимался **до** внесения порчи (ошибка проб-хара); стал снимать **после** порчи → `db_unchanged=true`. Продукт БД не трогает. |
| 3 | DELIVERY не пишет цель | Ключ цели доставки | Ключ — константа `TASK = demo:existing-task-AA001`, а не угаданный; поправил lookup → `target_written=true`, `writes_unique=true`. |
| 4 | AB-канарейка не видна в union | Кодировка канареек | Канарейки лежат в **base64 `body_b64`**; поправил скан → union видит AB b64-канарейку, `leak_keys=[]`. |
| 5 | Oracle не находит поломку | `event_type` повреждённого события | Тип события — `comment`, а не `append`; поправил oracle → нашёл поломку seq **4**, ветка **AB**, в обеих коррупциях. |
| — | Падает regression-тест | Сравнение `tests/` с baseline | `test_event_chain_is_verified_and_forgery_is_detected` — **предсуществующий** тест на старую утечную форму; `tests/` байт-идентичны baseline (18 файлов), это не регрессия от фикса. |

## 1. Точная версия

- `code_digest = 08aa9a9b978831806bd0ef24fe26f7214ab21b31ca6d2bbe7d27a61bd29bfe6f`, **16** файлов (baseline `715b1ca8…`, 15 файлов).
- Пересчитан мной независимо методом SEC003 (`runtime/AB003/digest_check.py`, read-only) — совпал.
- Изменены ровно `mockup/admission.py` и `mockup/server.py`, добавлен `mockup/public_dto.py`; остальные 13 `mockup/*.py` байт-в-байт равны baseline.
- Целостность worker-evidence: `verify-worker-receipts.json` — **11/11 declared hashes MATCH** (9 receipts + 2 manifests), live digest равен ревьюируемой версии.

## 2. Собственный воспроизводимый прогон (seed 7107)

Чистый env, свой probe `runtime/RV004/rv004_probe.py`, каталог `runtime/RV004/run-aa-7107b/`, все процессы exit 0. Итог **5/5 GREEN**:

- **CHK-A2-01 — LEAK_CLOSED.** Здоровая AA-фиксированная/AB-скрытая фикстура, AA в 2 ревизиях. query/snapshot/trace/resume/sync_status/export/sync — только status-only chain, revisions `{AA:2}`, `leak_keys=[]`, `foreign_rev_keys=[]`, `ab_canary_visible=false`, `text_equals_structured=true`. Export YAML — AA-клайм, без AB, branch-строка на месте.
- **CHK-A2-02 — LEAK_CLOSED.** AA-only chain status-only; union видит `{AA:2,AB:2}` без leak-ключей; sync_status AA — 4 acked intent'а, без чужих веток; chain_head/head_hash/events не выдаются.
- **CHK-A2-03 — GATE_UNIFORM_SAFE.** Две порчи (invalid-utf8, wrong-hash) на disposable-копии, 7 tools × 2 PID. Каждый ответ — точная безопасная Broken-форма (`CHAIN_BROKEN`, `reason=EVENT_SHAPE_INVALID|EVENT_HASH_MISMATCH`, `broken_at_seq=4`, `branch=AB`, `kind=comment`) **без** foreign `broken_event_id`/`head_hash`/`events`. `db_unchanged=true`, новых/изменённых файлов во время gate нет. Oracle независимо нашёл поломку seq 4 AB в обеих коррупциях.
- **CHK-DEL-01 — PASS.** 8 outbox / 4 attempts / 4 observations / 4 acks; observation после attempt; внутренний stamp полный (`chain_head` + revisions `{AA,AB}` + `port_reported`); цель `demo:existing-task-AA001` записана по одному разу на tx, дублей нет.
- **RV004-B-SIDE — PASS.** Прямые AB/ZZ на query/trace/sync_status/sync — `SCOPE_DENIED`; union видит AB-ветку с AB b64-канарейкой, leak-ключей нет.

## 3. Соответствие требованию TD-DOM-19 / RS002

- Public DTO fail-closed: на здоровых поверхностях нет `chain_head`/`head_hash`/`events`/`broken_event_id`/`broken_at_seq`/чужих revisions.
- Глобальный integrity gate отдаёт **одну** точную безопасную Broken-форму без foreign locator на 7 поверхностях.
- Внутреннее доказательство сохранено: `chain_head` + все revisions + `port_reported` во внутреннем observation-stamp; delivery-цепочка ack/observation/attempt цела.
- Оба канала MCP сериализуют один безопасный объект (`text_equals_structured=true`).
- Scope не расширен: новых endpoints/grants нет, `tests/` байт-идентичны baseline (18 файлов), `tech_debt.md` не менялся.

## 4. Coverage / omissions

- **Покрыто:** перечислено в §3 и `per_check` артефакта, каждому чеку назначен receipt с sha256.
- **Omissions (не блокируют review TD19):**
  - **CP-PL-05** REPLACE-проба **не засчитана** — SQL-ошибка в самой пробе (QA003), не результат продукта.
  - **CP-PL-10** busy/read-only подкейсы **NOT_TESTED** (WAL), зафиксировано честно.

## 5. Вердикт и долг

- **decision = APPROVE** — по собственным проверкам, а не по self-report worker'а.
- **Debt recommendation: `closed`** (по существу TD-DOM-19 закрыт на этой версии). **Приёмку долга НЕ выполняю** — закрытие в `tech_debt` есть решение OMH/заказчика; `tech_debt.md` не изменялся.
- `product_acceptance=false`, `is_approval=false`; `completion_state=completed` (все три финальных файла существуют).
- Следующие этапы (verifier-требования, negative-аудитор) — отдельными ролями; мной не запускались.
