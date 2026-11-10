# RS009 — путь записи отказа (W10) — RESEARCHER

`product_acceptance=false`, `is_approval=false`, `applied=false`. Прототип: `runtime/RS009/**`, валидация **31/31 PASS**, `mockup/**` не тронут (read-only, приёмка AB006 на `c26812b3`).

---

## 0. Подозревал → проверил → оказалось

| # | Подозревал | Проверил (чем) | Оказалось |
|---|---|---|---|
| 1 | «Отказ записать нельзя, но проекция готова» | admission.py:203 (review всегда approve), :486-487 (_pending_page) | Write-gap подтверждён (установленный факт, не переоткрывался). **Новое:** `_pending_page` деривирует REJECTED, но **не фильтрует** его из pending — отвергнутое попадает в «нужно действие» и агент будет бесконечно возвращаться |
| 2 | «Если reject-вердикт посадить, admit его допустит» | admission.py:218-224 (admit: digest/policy/snapshot/head — но не decision) | **Дыра подтверждена:** admit не проверяет decision; посаженный reject-вердикт проходит допуск. В прототипе: admit отвергнутого → `CANDIDATE_REJECTED` (новый гейт) |
| 3 | «Переподать с исправлением = новый ключ» | Прототип P3/P4/N10 | Подтверждено: тот же ключ+digest = F-02 replay (отказ в силе); тот же ключ+другой digest = `IDEMPOTENCY_MISMATCH`; новый ключ = новый кандидат, может пройти. Отказ REVISION_CONFLICT не ломает: исправленная подача целится в текущую голову |
| 4 | «Апелляция без перезаписи невозможна» | Прототип P5 | **Возможна:** re-review другим root; last-review-wins; оба вердикта в истории (IMMUTABLE). Тот же ревьюер не может переиграть себя (`REVIEW_ALREADY_DECIDED`) |
| 5 | «Отказ двигает состояние ветки» | Прототип V-HEAD | **Нет:** reject/drop пишут только reviews/drops, головы веток не двигаются (после P1 {AA:0,AB:0}) — DoS на состояние ветки исключён |
| 6 | «Отклонение скрывает работу» | Прототип + IMMUTABLE | **Нет:** кандидат не удаляется, payload читаем, вердикт с кодом+rationale в истории; скрытие потребовало бы DELETE — заблокировано триггерами |

## 1. Контракт отказа

Вердикт (payload таблицы `reviews`, **новая таблица для reject не нужна**):

`decision` (approve|reject) · `reason_code` (закрытый словарь, обязателен iff reject) · `rationale` (1..500, обязателен iff reject) · `comment` (опциональный свободный текст, отдельным полем) · `reviewer` · `root` · `candidate_digest` · `expected_revision` · `server_time` (аддитивное поле — сегодня в payload нет) · `simulated` · `proof_ref`.

**Закрытый словарь** (без `OTHER`, иначе свободный текст просочится в проверяемое поле): `CONTRADICTS_BASELINE`, `INSUFFICIENT_EVIDENCE`, `OUT_OF_SCOPE`, `DUPLICATE`, `STALE_BASIS`. Код вне словаря → `REASON_CODE_UNKNOWN`, строка не пишется. Расширение словаря = изменение константы + миграция проекций.

**Состояния (деривация, без LLM):** `ADMITTED > DROPPED > (последний вердикт: REJECTED | REVIEWED) > AWAITING_REVIEW`. Терминальные для pending: ADMITTED, REJECTED, DROPPED. Полная спецификация — `answers/contract.json`.

## 2. Судьба отвергнутого

- **Читаем:** candidates IMMUTABLE, payload нетронут; история показывает вердикт с кодом+rationale (V-REJ/V-HIST). В established не попадает: claims не создавались (V-NOESTAB).
- **Повторная подача:** тот же ключ+digest → F-02 replay того же кандидата, отказ в силе (V-RESUB-SAME); тот же ключ+другой digest → `IDEMPOTENCY_MISMATCH` (V-IDEM); **новый ключ = новая попытка** → может пройти, старый REJECTED остаётся в истории (V-RESUB-FIXED). Исправленная подача целится в текущую голову, иначе `REVISION_CONFLICT` (поведение не меняется).
- **Апелляция без перезаписи:** re-review другим независимым root; last-review-wins → REJECTED→REVIEWED; оба вердикта в истории; один вердикт на (кандидат, root ревьюера) — анти-флип-флоп и анти-спам (V-APPEAL, V-APPEAL-SAME-REVIEWER). После апелляции старый review_id для admit → `STALE_REVIEW`.
- **Admit отвергнутого:** сегодня дыряв (decision не проверяется); предложено `CANDIDATE_REJECTED` / `CANDIDATE_DROPPED` (V-NEG5/V-NEG11).

## 3. Отказ автора ≠ отказ ревью

| | Отказ ревью (REJECTED) | Отказ автора (DROPPED) |
|---|---|---|
| Кто пишет | ревьюер: root != root кандидата (INDEPENDENCE_NOT_ENFORCED) | автор: root == root кандидата или owner (DROP_AUTHOR_ONLY) |
| Куда | таблица `reviews` (вердикт) | таблица `drops` (маркер, аддитивная, IMMUTABLE) |
| Инструмент | `dom_reject` (fail-closed) | `dom_drop` |
| Перепутать нельзя | разные таблицы + разные root-гейты + разные состояния — разделение в проекции, без LLM | |

**«Брошено»:** только явная запись `dom_drop {candidate_id, reason 1..500}` → `DEMO_DROPPED`; никаких таймаутов-догадок (INFERRED из RS008 — подсказка, не факт). Брошенное не воскресает в pending (V-PEND-DROP) и не выглядит живым.

## 4. Стыки

- **pending (W1):** сегодня `_pending_page` (admission.py:486-487) **включает** REJECTED в pending — агент будет бесконечно возвращаться к отвергнутому. Предложено: фильтр терминальных (ADMITTED/REJECTED/DROPPED) в items **и** count; REVIEWED остаётся (ждёт admit). Проверено: c1/c6 отсутствуют, c5 (REVIEWED) присутствует, count==items (V-PEND-REJ/V-PEND-DROP/V-PEND-REVIEWED/V-COUNT).
- **история (RS008):** dom_reject пишет в reviews → отказ виден с кодом+rationale (V-REJ/V-HIST); drop — с причиной и автором. Отвергнутый не создаёт claims → snapshot его не содержит (V-NOESTAB).

## 5. Варианты и цена

| | A: расширить dom_review | B: отдельный dom_reject | C: оба + dom_drop (**рекомендация**) |
|---|---|---|---|
| Цена | ~90-120 LOC, 0 миграций, 0.5-1 день | ~70-100 LOC, 0 миграций, 0.5-1 день | ~130-180 LOC + аддитивная таблица drops (user_version gate), 1-1.5 дня |
| Полнота | reject пишется | reject пишется; «брошено» — нет | reject + drop + appeal + стыки |
| Риск | **fail-open**: клиенты без decision молча одобряют; approve/reject в одном инструменте | fail-closed; два write-path к «вердикту» (проекция обязана трактовать оба) | три поверхности, каждая узкая и fail-closed |
| Миграция | не нужна (reviews BLOB) | не нужна | reviews: не нужна; drops: аддитивная |
| Совместимость | старые вызовы = approve | dom_review неизменен | dom_review/dom_admit/легаси-approve не меняются (V-LEGACY) |
| Аудит | средний (одно поле различает) | высокий (единственная точка отказа) | максимальный: три события, три автора |

Почему не A: fail-open дефолт противоречит природе отказа. Почему не B: «брошено» остаётся незаписанным. **C реализован в прототипе.**

## 6. Риски

- **INDEPENDENCE_NOT_ENFORCED:** root-гейт перенесён на dom_reject; сам-отказ (V-IND) и самоприёмка (V-SELF-ADMIT) проверены.
- **«Отклонить всё» как скрытие:** отказ не удаляет (IMMUTABLE, payload читаем); словарь+rationale сравнимы; один вердикт на ревьюера; апелляция обратима; головы не двигаются (V-HEAD). Остаточный риск — скоординированные ревьюеры (governance, вне модели).
- **Отказ против чужой ветки:** кросс-веточный отказ легален (ревьюеры кросс-веточны по роли) и прозрачен; чужой грант → `SCOPE_DENIED` (V-NEG4).
- **IMMUTABLE:** триггеры на reviews и drops; UPDATE вердикта → IMMUTABLE (V-IMM); апелляция = новая строка.
- **Свободный текст:** закрытый словарь без OTHER; вне словаря → отказ без записи (V-NEG1).
- **Reject не ослабляет approve:** dom_review не меняется; admit только ужесточается; approve-путь и легаси проверены (V-APPROVE-OK, V-LEGACY).

## Проверки прототипа

`runtime/RS009/validation_receipt.json`: **31/31 PASS**. Сценарий — 37 шагов, 9 кандидатов (P1-P7 + N1-N13): отказ записан и читается (V-REJ/V-HIST); отвергнутое не в pending (V-PEND-REJ); повторная подача по контракту (V-RESUB-SAME/V-RESUB-FIXED/V-IDEM); апелляция без перезаписи (V-APPEAL); сам-отказ → INDEPENDENCE (V-IND); существующие approve не ломаются (V-APPROVE-OK/V-LEGACY); история с кодом причины (V-HIST). Негативы: причина вне словаря (V-NEG1), без rationale (V-NEG2), >500 (V-NEG3), чужой грант (V-NEG4), admit отвергнутого (V-NEG5), drop чужим (V-NEG6), drop допущенного (V-NEG7), IMMUTABLE (V-IMM), IDEMPOTENCY_MISMATCH (V-IDEM), reject dropped (V-NEG11), самоприёмка (V-SELF-ADMIT), повторный вердикт (V-NEG13). Головы двигаются только admit'ом (V-HEAD); суженный грант без маркеров чужого (V-GRANT); только stdlib (V-STDLIB).

## Выходы

- `artifacts/RESEARCHER_RS009_REJECT_PATH.json` (DONE, контракт, судьба, варианты, риски, результаты)
- `reports/RESEARCHER_RS009_REJECT_PATH.md` (этот файл)
- `runtime/RS009/prototype/` `{rs009_lib.py, run_prototype.py}` — зеркало схемы + предложенный сервис, сценарий
- `runtime/RS009/validate_rs009.py` + `validation_receipt.json` — 31/31
- `runtime/RS009/source_ledger.json` — sha256 12 прочитанных файлов продукта
- `runtime/RS009/answers/*.json` — contract, fate_of_rejected, variants, risks, pending_history_junction
- `runtime/RS009/results/*.json` — steps, scenario, pending_full, history_full

## Оговорки

- `mockup/**` не тронут (read-only, приёмка AB006); прототип — предложенная реализация на зеркале схемы, не продуктовая правка.
- «Один вердикт на (кандидат, root ревьюера)» — **новый** инвариант (анти-флип-флоп/анти-спам); на старые строки не влияет (IMMUTABLE), но меняет поведение повторных ревью — решение заказчика.
- Порог «кто может запросить апелляцию» (owner-гейт) — открытый policy-вопрос.
- Словарь без OTHER: ближайший код + нюанс в rationale; обман «в пределах словаря» схемой не ловится (сверка rationale с кодом — вне схемы).
- Первый статус по протоколу — честный PARTIAL (контекст собран, сценарий строился итеративно: REVISION_CONFLICT на устаревшей expected_revision, legacy snapshot_digest, метки фаз голов); финальный статус DONE.