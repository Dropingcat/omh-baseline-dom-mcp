# AB005 — worker: WS-F04 (типизированное отсутствие) + WS-F02 (L1+L2 в admit)

Два среза в одной сессии, **приёмка раздельная** (не засчитывать друг за друга). Сначала дешёвый независимый WS-F04, затем WS-F02. F-01/F-03 не трогать.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env. Базовая версия кода: digest `1ead2d45…` (16 файлов).

## Входы (читать полностью, не пересказывать себе)
- `runtime/RS006/answers_f02.json`, `runtime/RS006/answers_f01.json`, `runtime/RS006/answers_other.json`, `runtime/RS006/planning_RS006.json` (order, must_not_merge, negative_sets), `runtime/RS006/prototypes/rs006_f02_f01_prototype.py` + `receipt/rs006_prototype_receipt.json` (sha `954105cb…`, ALL_ASSERTS).
- `docs/F02_IMPLEMENTATION_OPTIONS_2026-11-08.md` (исходное предложение оркестратора), `docs/DECISION_BRIEF_2026-11-08.md` (согласованное направление L1+L2).
- `artifacts/AUDITOR_AB004_AU004F01.json` (A-F-02/F-04 факты), `artifacts/AUDITOR_AU006_TASK_BASELINE.json` (контекст, не задача).
- `mockup/admission.py`, `mockup/storage.py`, `mockup/server.py`, `mockup/public_dto.py` — рабочий код.

## Срез 1: WS-F04-TYPED-ABSENCE (сначала)
Находка: granted-but-absent ветка даёт несогласованные ответы (`INTERNAL_ERROR`, пустой `SYNC_STATUS`, ложный `SYNCED`).
Требуется: `query`/`resume`/`sync_status`/`sync` возвращают типизированные статусы: в гранте — OK; вне гранта — `SCOPE_DENIED`; в гранте, но ветки нет — `NO_SUCH_BRANCH`. Никаких raw исключений и никакого ложного `SYNCED`.
Write scope: `mockup/admission.py` (обработка head/отсутствия), `mockup/server.py` только для типизированного статуса.

## Срез 2: WS-F02-ADMIT-BINDING (после среза 1)
Финальная форма от RS006, **с двумя поправками к предложению оркестратора** (обязательны):
1. PK `idempotency` → `(external_work_ref, operation, key, scope_digest)`; старый PK делает невозможным законный повтор после legacy-отказа.
2. Не строгое равенство `scope_digest`, а арбитр **`result_scope ⊆ grant`** при выдаче; строгое равенство ломает законное восстановление после потерянного ответа при безопасном сужении.

Порядок проверок в `admit`: candidate scope → **L1: digest кандидата ДО обращения к кешу** → L2 binding `(candidate_id, review_id, branch, scope_digest, result_scope)` → review-проверки.
Коды: `DIGEST_MISMATCH`, `IDEMPOTENCY_MISMATCH`, `IDEMPOTENCY_BINDING_MISMATCH`, `IDEMPOTENCY_BINDING_UNKNOWN` (legacy), `IDEMPOTENCY_REVIEW_MISMATCH`, `SCOPE_DENIED`.
Миграция: `user_version`-гейт; колонки `candidate_id, review_id, branch, scope_digest, result_scope`; пересоздание immutable-триггеров; legacy-строки — честный отказ, не тихая выдача и не удаление.
Write scope: `mockup/admission.py`, `mockup/storage.py` (только миграция `idempotency`), `mockup/public_dto.py` только если меняется форма receipt.

## Обязательные проверки (физические, не «зелёные тесты»)
Позитивный контроль **N-F02-3**: легальный потерянный ответ (тот же кандидат/ключ/digest/review/грант) → та же квитанция, **без** новых tx/events/outbox; `idempotency=1`; receipt байт-равен.
Негативные: N-F02-1 (AA-кандидат + прежние AB key/digest → `DIGEST_MISMATCH` до кеша, квитанции нет, 2 PID), N-F02-2 (реальный AB-кандидат при гранте AA → `SCOPE_DENIED`), N-F02-4 (тот же ключ, другой digest → `IDEMPOTENCY_MISMATCH`/`BINDING_MISMATCH`), legacy-строка → `IDEMPOTENCY_BINDING_UNKNOWN`, сужение и восстановление гранта, отсутствие побочных эффектов (outbox/attempts/acks не растут).
Прогоны: smoke, e2e до/после на своих seed'ах, SQL-counts до/после, digest кода до/после. Разрушительное — только на изолированной копии БД в `runtime/AB005/`.

## Выходы
`artifacts/WORKER_AB005.json` (два среза раздельно: `slices[]{id, finding, status, write_scope, changed_files[], evidence, negative_results[], digest_before, digest_after}`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/WORKER_AB005.md`, `docs/SCHEMA_CHANGE_AB005.md` (миграция), `runtime/AB005/**` (probe-скрипты, seed'ы, SQL-readback, raw-кадры).

## Границы
Не трогать F-01 (идентичность доставки), F-03, `delivery.py`, OMH, tests, tech_debt, конфиги. Ни один долг не закрывать: TD19 закрывается только после независимых reviewer и auditor. Без Git/install/платных/субагентов/секретов. При лимите/обрыве — continuation той же роли с точным остатком; родитель финал не дописывает. Ориентир 45 вызовов, последние 5 — на артефакт/отчёт/схему.
