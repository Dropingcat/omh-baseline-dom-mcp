# RV006 — ревью W1 (AB006) на версии `c26812b3`

Роль REVIEWER. `product_acceptance=false`, `is_approval=false`, долги не закрывались.
Версия: `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505` — **пересчитана
собственным скриптом** (`runtime/RV006/probes/digest_check.py`, метод
`sha256(json.dumps({'mockup/<posix>': sha256}, sort_keys=True))`, 16 файлов) — **совпадает**.

## Вердикт

**CONFORM_WITH_FINDINGS** — контракт RS007 W1 выполнен по всем основным осям; 40/42
собственных проверок PASS. Два FAIL сводятся к одному корню (F1). Найдено 3 замечания
(F1..F3), ни одно не блокирует контракт, но F2 — реальная liveness-дыра пагинации.

## Что проверено (собственные пробы, runtime/RV006/)

| Ось | Результат |
|---|---|
| Контракт: коды/поля | PASS — `PENDING_PRESENT`/`NO_PENDING` (страничный признак), top-level ровно `status/count/items/has_more/page`, item = ровно 11 полей + опциональный `age_seconds` (12 ключей в сыром кадре); fail-closed проекция |
| `limit` 1..500, `after` | PASS для `limit=0/501/True/'5'`, `after` без `:`/int → типизированный `REJECTED`, без raw-исключений. **FAIL (F1)**: `after=':x'` и `after='AA:'` (пустые компоненты) принимаются как `RESUMED` |
| Точность `count` | PASS — независим от страницы (равен при `after=null`, после последнего item, за концом keyset); admitted исключён; deps вне гранта исключены (грант AA: count=2 при 5 строках в БД; AA,AB: count=4) |
| Анти-oracle | PASS — `count` == полная перечислимая мощность на 3 усечениях гранта; скрытые строки не дают ни items, ни счётчиков. Наблюдение F3: `has_more` (предфильтровый) — слабый exists-сигнал, задокументирован |
| Утечки | PASS — ни одного payload-текста (5 маркеров тел) и ни одного чужого id в items на грантах AA/AB/AA,AB и в сыром MCP-кадре |
| Миграция | PASS — user_version-гейт: uv≥2 без `created_at` → `MIGRATION_REQUIRED` без перестройки (физически: колонка не добавлена); legacy uv<2 мигрируется; идемпотентность (снапшот схемы после повторного init идентичен); 39 immutable-триггеров (44 всего), 2 индекса — read-only PRAGMA; legacy NULL `created_at` → `age_seconds` отсутствует (не 0) |
| Регрессия AB005 | PASS — `DIGEST_MISMATCH` до кеша (неверный digest на кешированном ключе → не replay); binding (`IDEMPOTENCY_REVIEW_MISMATCH`, `IDEMPOTENCY_BINDING_MISMATCH`); `result_scope ⊆ grant` (dedupe-гейт Denied на {AA,AB}→{AA}); `NO_SUCH_BRANCH`; idempotent replay = тот же tx |
| Недополнение страницы | PASS_WITH_FINDING — `has_more` = предфильтровый `limit+1` подтверждён кодом и кадрами (limit=2 → 1 item, has_more=true, count=4) и документирован (SCHEMA_CHANGE_AB006 §8, контракт, артефакт worker'а). НО: при `items=[]+has_more=true` клиенту нечем продолжить (F2) |

## Findings

- **F1 (low, contract_codes)** — валидация `after` проверяет только наличие `:`;
  `':x'` и `'AA:'` проходят как `RESUMED`. Контракт требует `branch:id` с типизированным
  `REJECTED`. Фикс: проверять оба компонента непустыми.
- **F2 (medium, page_underfill_liveness)** — при `items=[]` и `has_more=true` курсор
  берётся из items, которых нет: повторный запрос возвращает идентичный кадр
  (`identical_frame=true`), видимые кандидаты могут быть **недостижимы** keyset-обходом
  при суженном гранте (walk limit=1 на g1 застревает после первого item). Документированное
  «листай по has_more» невыполнимо без курсора. Фикс: отдавать курсор из последней
  предфильтровой строки (`page.next_after`) или фильтровать до LIMIT.
- **F3 (low, observation)** — `has_more` (предфильтровый limit+1) сам по себе является
  слабым exists-сигналом о скрытых in-branch строках. Не противоречит карте (анти-oracle
  требуется для `count` и выполнен), задокументирован в §8.

## Собственные пробы

- `runtime/RV006/probes/rv006_own_probes.py` → `results/own_probes.json` (42 проверки,
  sha256 `fdccf581…`), фикстуры `runtime/RV006/fixtures/g1..g5` (свои, через продукт-API +
  точечный raw SQL для недостижимых через API форм).
- `runtime/RV006/probes/rv006_raw_frames.py` → `results/frames_raw.jsonl` (3 сырых MCP-кадра,
  sha256 `c67bb16a…`): pending metadata-only, underfill в кадре, `forbidden_text_in_pending=[]`.
- `runtime/RV006/probes/digest_check.py` → пересчёт digest (совпал).

## Границы

Продукт read-only (mockup/**, docs/** не тронуты); записи только в
`artifacts/REVIEWER_AB006.json`, `reports/REVIEWER_AB006.md`, `runtime/RV006/**`.
Git/install/сеть/субагенты не использовались. Долги не закрывались.