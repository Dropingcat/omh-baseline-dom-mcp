# REVIEWER RV005 — AB005 (WS-F04 + WS-F02) на digest `ca227b17`

Роль: REVIEWER. Вердикт: **APPROVE** (раздельно по двум срезам). `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]` (долги не закрываю; TD19 — только владелец OMH после независимых reviewer+auditor).

Проверяемая версия: `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7` (16 файлов).

---

## 0. Пересчёт digest (обязательный)

Собственный расчёт (sha256 от json.dumps сорт. карты `mockup/<posix-relpath>` → sha256, sort_keys=True) дал ** ровно `ca227b17…`** — совпадает с заявленным. Проба: `runtime/RV005/digest_probe.py` (ключи с префиксом `mockup/`, 16 файлов).

## 1. Неизменность посторонних файлов (обязательная)

Сверка по-файлово с заморозкой AU005 (`runtime/AU005/continue01_freeze.json`, digest `1ead2d45`) и снапшотами AU006:

- Изменены **только** `mockup/admission.py` и `mockup/storage.py` (как заявлено worker'ом).
- Байт-идентичны базе: `delivery.py`, `public_dto.py`, `server.py`, `dom_contract.py`, `ports.py`, `projections.py`, `demo.py`, `fixtures`, все `ab002_*`.
- `tests/`: все 18 файлов байт-идентичны заморозке, новых/удалённых нет.
- `tech_debt.md`: sha256 `6c32af27…` — совпадает с ledger AU005.
- OMH: локальная сторона (delivery.py/ports.py/outbox) не тронута; live OMH запрещён картой — не вызывался.
- Проба: `runtime/RV005/verify_baseline_files.py`.

Диффы изменённых файлов (против снапшота AU006) — `runtime/RV005/admission.diff`, `runtime/RV005/storage.diff`: хирургические, без правок review()/delivery/публичных DTO.

---

## Срез 1: WS-F04-TYPED-ABSENCE — **APPROVE**

Контракт: in-grant OK / out-of-grant `SCOPE_DENIED` / granted-but-absent `NO_SUCH_BRANCH` на query/resume/sync_status/sync; без raw-исключений; без ложного SYNCED.

**Собственный прогон** (`runtime/RV005/results/rv005_f04_own.json`, реальные MCP-субпроцессы через собственный лаунчер `rv005_launcher.py` и клиент `rv005_mcp.py`, кадры в `runtime/RV005/f04/frames-*.jsonl`, grant `{AA,ZZ}`):

| Поверхность | ZZ (в гранте, ветки нет) | AB (вне гранта) | AA (здоровая) |
|---|---|---|---|
| query | `NO_SUCH_BRANCH` | `SCOPE_DENIED` | `SNAPSHOT` |
| resume | `NO_SUCH_BRANCH` | `SCOPE_DENIED` | `RESUMED` |
| sync_status | `NO_SUCH_BRANCH` | `SCOPE_DENIED` | `SYNC_STATUS` |
| sync | `NO_SUCH_BRANCH` | `SCOPE_DENIED` | `SYNCED` |
| trace | `NO_SUCH_BRANCH` | `SCOPE_DENIED` | `TRACE` |
| export | `NO_SUCH_BRANCH` | — | `EXPORTED` |

- `trace(master)` при неполном гранте — `TRACE` (UNKNOWN-путь), не ломается.
- `sync.ZZ != SYNCED` (нет ложного успеха). Ни одного `INTERNAL_ERROR` ни в одном кадре моего прогона.
- Физическая точка: `head()`/`require_branch()` по `branch_heads`; sync/sync_status получили явный `require_branch` (не идут через head). Типизированный статус идёт через существующий `guarded → project_tool` (DomainError `{'status': code}`, public_dto.py:353-357 — файл не менялся), поэтому `server.py` не потребовался — подтверждено диффом.
- Дефект до фикса подтверждён независимым чтением `f04_before.json`: `INTERNAL_ERROR` на query/resume/export/trace ZZ, пустой `SYNC_STATUS`, ложный `SYNCED` — реальная находка AU005-F-04, устранена.

## Срез 2: WS-F02-ADMIT-BINDING — **APPROVE**

Контракт (карта AB005 + DECISION_BRIEF L1+L2 + RS006): порядок candidate → L1 digest ДО кеша → L2 dedupe(binding) → review → remember; PK `(work,operation,key,scope_digest)`; арбитр `result_scope ⊆ grant`; submit тоже привязан; миграция user_version-гейт, `BEGIN IMMEDIATE`, legacy-строки инертны, immutable-триггеры пересозданы; позитивный контроль N-F02-3.

**Позитивный контроль N-F02-3 — собственный прогон (обязательный).** `runtime/RV005` case A:
- повтор admit в свежем PID (тот же кандидат/ключ/digest/review/грант) возвращает **байт-равную** квитанцию (text и parsed);
- дельты по candidates/reviews/transactions/events/outbox/delivery_attempts/delivery_observations/delivery_acks/idempotency — **все 0**;
- idempotency остаётся **2 строки** (submit+admit), admit-строка ключа — 1;
- статус повтора — исходный `DEMO_ADMITTED` (никакой подмены статуса/REPLAY).

**Обе обязательные поправки RS006 подтверждены физически:**
1. PK + `scope_digest`-колонка: схема в storage.py, PRAGMA-readback; legacy-строки копируются как есть (`scope_digest=''`, binding NULL).
2. Арбитр `result_scope ⊆ grant`: собственный сценарий F (`probe_f02_narrow.py`) — admit AA-кандидата при `{AA,AB}` (result_scope `['AA']`), повтор при суженном `{AA}` → **та же квитанция байт-в-байт, 0 дельт**. Опасное сужение закрыто candidate()-scope (SCOPE_DENIED, сценарий B/D и worker N-F02-6).

**Собственные негативы** (`probe_f02.py`, кадры в `runtime/RV005/f02*/frames-*.jsonl`):
- B: чужой кандидат с **байт-равным digest**, тот же ключ → `IDEMPOTENCY_BINDING_MISMATCH`, 0 фактов;
- C: тот же ключ, неверный digest → `DIGEST_MISMATCH` ДО обращения к кешу (L1), 0 фактов;
- D: отсутствующий кандидат → честный `SCOPE_DENIED`, кеш не задет;
- E: миграция на собственной копии старой схемы → `INITIALIZED`, user_version=1, колонки v2, legacy-строка инертна (`''`/NULL/digest сохранён), admit по legacy-ключу → `IDEMPOTENCY_BINDING_UNKNOWN` без перезаписи строки, новый ключ → `DEMO_ADMITTED`, `UPDATE` legacy-строки → `IMMUTABLE`, fail-closed: старая схема + user_version=5 → `MIGRATION_REQUIRED`.

**Проверки не ослаблены:** `review()` диффом не тронут; после cache-miss в admit сохранены STALE_REVIEW / INDEPENDENCE_NOT_ENFORCED / REVISION_CONFLICT; candidate()-scope до кеша. **Нового поведения вне контракта нет:** единственные новые коды — контрактный набор (`DIGEST_MISMATCH`, `IDEMPOTENCY_MISMATCH`, `IDEMPOTENCY_BINDING_MISMATCH`, `IDEMPOTENCY_BINDING_UNKNOWN`, `IDEMPOTENCY_REVIEW_MISMATCH`, `SCOPE_DENIED`, `NO_SUCH_BRANCH`, `MIGRATION_REQUIRED`), сериализуются через тот же pre-existing DomainError-путь; повтор возвращает исходный статус квитанции.

**Evidence worker'а перечитан независимо:** `f02_after_summary.json` all_pass=true (N-F02-1..11); digest-последовательность в результатах (`1ead2d45 → 7615365e → ca227b17`) согласована; миграционный фикстур `fixtures/f02/after/legacy-migrated/dom.sqlite3` перепроверен вручную (v2-колонки, uv=1, legacy-строка инертна с сохранённым digest `1c5948d5…`, триггеры `immutable_idempotency_{UPDATE,DELETE,INSERT}` пересозданы, `UPDATE → IMMUTABLE`); raw-кадры — настоящие JSON-RPC stdio-кадры.

---

## NOT_CHECKED (честный список)

- Истинно конкурентная гонка двух процессов (модель — сериализация `BEGIN IMMEDIATE`; рекомендация RS006 остаётся).
- Полный pytest (tests/ байт-идентичны baseline, но не запускались).
- Live OMH / сеть / Git / установка (запрещены картой).
- N-F02-7 (другой principal, ключ не переиспользуется), N-F02-9 (детерминированная гонка), N-F02-11 (NOT_INITIALIZED-вариант) — проверены worker'ом, мной не повторялись (минимум собственных сценариев на срез выполнен с запасом).
- Множественные заполненные submit-строки одного ключа под разными грантами (pick=rows[0]) — безопасность покрыта result_scope-гейтом по коду, отдельно не гонялось.

## Пробы (runtime/RV005/**)

- `digest_probe.py`, `verify_baseline_files.py` — digest и неизменность файлов.
- `rv005_launcher.py`, `rv005_mcp.py` — собственные лаунчер и клиент (без заимствований у worker'а).
- `probe_f04.py` → `results/rv005_f04_own.json` (sha256 `818e685e…`).
- `probe_f02.py` → `results/rv005_f02_own.json` (sha256 `2c60556f…`).
- `probe_f02_narrow.py` → `results/rv005_f02_narrow_own.json` (sha256 `85bf3a28…`).
- `admission.diff`, `storage.diff` — диффы против baseline-снапшота AU006.

## Границы соблюдены

Read-only по продукту (правки — только `artifacts/REVIEWER_AB005.json`, `reports/REVIEWER_AB005.md`, `runtime/RV005/**`); без Git/install/платных/субагентов/секретов; разрушительное — только на изолированных копиях БД в `runtime/RV005/`. Долги не закрывались.
