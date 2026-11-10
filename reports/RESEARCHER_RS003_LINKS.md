# RS003 — ресерчер: связи, вложенные версии клайма, scoped graph (COMPLETE_MATERIAL)

**Статус:** исследовательский материал по 14 точным вопросам AN003. `product_acceptance=false`, `product_verdict=REQUEST_CHANGES`. Это НЕ приёмка: TD-DOM-19/20/21 открыты, P0 не отменён, ничего не реализовано в продукте. Все имена полей/таблиц/событий ниже — предложение RS003, не утверждённый API.

Полные ответы (механизм, Sxx-источники, схемы, action→expected→physical evidence, uncertainty, scope_limit) — в `runtime/RS003/answers_01_03.json`, `answers_04_08.json`, `answers_09_10.json`, `answers_11_14.json`; индекс и хэши — `artifacts/RESEARCHER_RS003_LINKS.json`. Здесь только сжатый вид.

## 1. Что предлагается минимально

| Вопрос | Минимум |
|---|---|
| Q-L-01 | Два неизменяемых объекта: `AcceptedBasis` (доказательство допуска версии в ветке) и task-scoped `ContextPack` (только разрешённые факты, bytes, принявший, условия, статус проверки, правило reopen). `accepted_context` в техкарте = ссылка `pack_id+digest`, не флаг на клайме. Неполнота — явный `incomplete`/`CONTEXT_NOT_READY` без скрытых ID/счётчиков. |
| Q-L-02 | Ledger с независимыми осями persisted → selected → delivered_observed (или `delivery_unknown`) → acknowledged → used_reported → use_checked. Ack ≠ понимание; use проверяет независимый reviewer. |
| Q-L-03 | Origin / CreationGrounds / поздние EvidenceAttachment раздельно; `grounds_state` обязателен, `grounds[]` может быть пуст; корень, hypothesis, legacy, criterion-без-baseline — явные состояния без выдуманных ссылок. UD-02 OPEN. |
| Q-L-04 | Существующий `claims.id` = record/node ID; sidecar `lineage` добавляет opaque `family_id` + `parent_record_id`. Общий logical ID не нарушает неизменяемость. |
| Q-L-05 | `current leaf` = производная `tips(family, branch, R)`; два допущенных sibling → `FORKED`, без молчаливого победителя; `intent` + `expected_tips_digest` + CAS по ревизии ветки. |
| Q-L-06 | Закрытый словарь `dom-relations/1` из 8 типов; хранится только авторитетное направление; similarity — не ребро и не доказательство. |
| Q-L-07 | Семь независимых осей: admitted / accepted / current / stale / converged / delivered / owner_closed. Reopen — запись с причиной ∈ {new_contradiction, source_correction, changed_conditions} + evidence; «не помню» — не причина. |
| Q-L-08 | Pins: `version` / `revision` / `line`; evidence хранит только первые два; stale — строгий default; pin вне grants → `UNVERIFIABLE_IN_SCOPE` без ревизии; revalidate = новая запись проверки. |
| Q-L-09/10 | ScopedView до count/score/top-k/cursor/cache; ключи кэша и курсоры привязаны к `scope_digest`; публичный global bit — только generic `NOT_READY/CHAIN_BROKEN`. |
| Q-L-11 | Не выбрано — вопрос заказчику (см. §4). |
| Q-L-12 | `SourceRecord`/`SourceEvent`; locality — описание, не доверие; воспроизводимость только при удержанных bytes + hash; без fetch. |
| Q-L-13 | `TreeRow = claim_version | event`; порядок по (revision, id)/(revision, seq); итеративный successor + keyset cursor; `dom/v2` с согласованием версии. |
| Q-L-14 | Из F — идеи, не код: related+anchor → relation+locator; scorer переписать на целых milli-весах; backlink count — по видимым рёбрам; `dom-c14n` не менять. |

## 2. Идентичность и версии (Q-L-04, Q-L-08)

| Понятие | Что это | Меняется? | Публичный адрес |
|---|---|---|---|
| logical / family ID | opaque UUID, выдаёт сервер при допуске корня | нет | `VersionRef.family_id` |
| record / version ID | существующий `claims.id` | нет | `VersionRef.record_id` |
| parent | `lineage.parent_record_id` (FK), только для refinement; цикл невозможен — parent должен уже существовать | нет | `parent_state`: root / ok / unavailable |
| цитата | `QuotePin{record_id, raw_sha256, byte_start, byte_end}` | нет | — |
| линия | `LineRef{family_id, branch}` — динамически разрешается в leaf; доказательством быть не может | вычисляется | всегда с `resolved_record_id` + R |
| ревизия ветки | `RevisionPin{branch, revision}`; `head != pin` ⇒ stale (strict default) | нет | только для granted веток |
| события | `events.seq` / `revision`; порядок по ним, не по времени | нет | `EventRef` |

Отвергнуто: единый `claims.id` у всех версий (нарушает PK/триггеры), составной ключ `(logical, seq)` как identity (даёт ложного «последнего» при concurrent siblings), `root_id` как публичный ID (может раскрыть корень вне видимости). AA11/АА11 и AA001 хранятся как разные opaque-метки и не нормализуются.

## 3. Формула клайма, scoped graph, context pack

```
CLAIM_RECORD  = ⟨ record_id ┃ family_id ┃ parent_ref ┃ ORIGIN ┃ BODY(immutable) ┃ GROUNDS(creation) ┃ TYPE-META ┃ SourceRecord* ⟩
EVENTS*       = comment | property | relation(typed, pinned) | applicability | archive | reopen_request | review | converge | …
DERIVED       = tips/current_leaf(branch,R) ; StateVector(7 осей) ; tree rows ; backlinks/neighbors/counts/rank   ← только из ScopedView
CONTEXT_PACK  = { binding(work,task,card,run,recipient), read_view, facts[AcceptedItem+AcceptedBasis], completeness, reopen_policy } + digest
```

Граница graph: `Context(grants) → единый read snapshot → ScopedView(visible_records, visible_edges) → traversal/count/score/top-k/cursor/cache → closed DTO → оба MCP-канала/YAML/log`. Внутренний полный proof остаётся; наружу — generic `NOT_READY/CHAIN_BROKEN`. Shared node читается, но не расширяет n-hop в запрещённые ветки.

## 4. Открытые решения (не выбраны RS003)

| ID | Что | Блокирует |
|---|---|---|
| NU-01 | **Keywords:** «Ключевое слово — метка для поиска САМОГО КЛАЙМА (К1), метка КОНКРЕТНОЙ СВЯЗИ (К2) или нужны ОБА независимых набора (К3)? Ответ — К1/К2/К3; «да» не принимается.» | только поле/индекс/search keywords |
| NU-02 | Кто выбирает между двумя независимо допущенными смыслово конкурирующими siblings без merge (default: остаётся FORKED) | автоматическое разрешение fork |
| NU-03 | UD-02 — dependencies/baseline, строгость revalidation | политику пустых dependencies |
| NU-04 | UD-06 — субъект/критерии сходимости, закрытие reopen | converge-политику |
| NU-05 | Retention/retrieval внешних источников | acquisition-порт для external |

Дерево (родитель сверху, вложенные неизменяемые версии) — **не** новый needs_user: смысл подтверждён заказчиком, выбор ключа инженерный. Устранение TD19 обязательно и не зависит от согласия на graph-фичи. TD19 vs SEC003 порядок и YAML continuation не выбирались.

## 5. Будущие E2E (все NOT_TESTED в продукте)

- Q-L-01/02: PID1 допускает A; PID2 продолжает A.1 по карточке с pack; независимый reviewer сверяет результат с A; «недоступный» vs «несуществующий» предок дают одинаковый ответ; kill до dispatch/после delivery до ack.
- Q-L-04/05: корень + 2 уточнения; два процесса на одного родителя → FORKED; kill до/после commit; archive листа не повышает родителя.
- Q-L-06/08: неизвестный type / endpoint kind / чужой endpoint / reverse-дубль без частичных строк; движение ветки → `pin_behind`; revalidate добавляет запись.
- Q-L-09/10: fixed AA, скрытый AB 0 vs 8 связей (L1–L8) + positive control union; warm union cache; чужой cursor; отзыв grants; рестарт; timing как измеренный residual risk.
- Q-L-13: цепь 20k+, siblings, события одной ревизии, циклический/чужой parent, разные grants, старый клиент.
- Q-L-12/14: synthetic source fixtures; scorer на 0/отрицательных/единицах/дубликатах тегов, malformed config.

Слайсы W0…W8 с зависимостями и gates — `artifacts/RESEARCHER_RS003_LINKS.json#/next_worker_slices`. Порядок: W0 (AB003 TD19) → W1 identity → W2/W3/W7 → W4 → W5 → W6 → W8. Подготовленная дельта планов (не применена) — `#/plan_delta_prepared`.

## 6. Что реально выполнено RS003

| Что | Результат |
|---|---|
| Сверка `answers_01_03.json` с `exact_questions.json` и AN003 | ID/порядок/формат совпали; принят без изменений |
| `proto_scope_graph.py` (in-memory SQLite, синтетика) | 17/17 проверок; наивная пост-фильтрация показала утечку total — оракул способен падать; прогон выявил, что глобальный autoincrement id в cursor раскрыл бы пропуски (исправлено, первый запуск упал — честно записан) |
| `proto_tree_pager.py` | 11/11; цепь 20 000 без рекурсии; без дублей/пропусков; R-pinning курсора НЕ проверен |
| `proto_f_probe.js` (чистые функции F read-only, синтетика) | `parseNumeric('-5 °C')=5`, `0`→null, `540 K = 540 °C`, `'1e3'→1`, `'500-600'→500`; дубликаты тегов считаются дважды (4.6 vs 4.4); score — float; без cfg `TypeError` |
| `proto_int_scorer.py` | integer-only scorer: знак/0/единицы/дубли/конфиг-отказы; не backend |
| `validate_rs003.py` + 19 негативных контролей (`negative_controls.json`) | см. `runtime/RS003/validation_receipt.json` |

Прототипы проверяют алгоритмы на синтетике; они НЕ продуктовый E2E, MCP, OMH или Git. Timing не измерялся. Реальный OMH task/card/run адаптер не исследовался. F только читался.
