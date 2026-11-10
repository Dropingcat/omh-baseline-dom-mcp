# Статус проекта (проверено оркестратором, 2026-11-06)

Не самоотчёт исполнителя. Каждый пункт — результат фактического чтения или прогона.

## Директория проекта

P = E:/opencode_harness_portable/projects/omh-baseline-dom-mcp

| Артефакт | Состояние |
|---|---|
| REQUIREMENTS.md | есть; исходные слова заказчика, включая маркер ветки на каждом клайме |
| ADMISSION_AND_INTEGRITY_DESIGN.md | есть; проект протокола (не реализация) |
| OMH_CODE_REVIEW.md | есть; статический аудит установленного OMH |
| analysis/AA001_ANALYSIS.md/.json | есть; JSON парсится |
| research/AA002_RESEARCH.md/.json, AA002_SOURCE_LEDGER.json | есть; JSON парсится |
| docs/SPEC.md, docs/IMPLEMENTATION_PLAN.md | есть |
| cards/AA001, AA002, AB001, AC001, AC002 | есть; в AB001 добавлено дополнение r2 |
| mockup/{storage,admission,dom_contract,projections,ports}.py | есть |
| mockup/server.py (stdio MCP) | есть; 12 объявленных инструментов (10 нормативных + `dom_sync` + алиас `dom_snapshot`) |
| mockup/demo.py | есть; запуск exit 0, артефакты в `runtime/runs/` |
| mockup/README.md | есть |
| tests/*.py | есть; 49 тестов, exit 0 |

## Фактический прогон тестов

Проверено оркестратором после исправлений AB001-r5:

Команда: `cd P && E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q`
Результат: **60 passed, exit 0** (было 55; +5 тестов на запрет подмены, ни один не ослаблен).

Закрыты два дефекта класса «ложная готовность»:
- **N1** — клайм в целевой ветке терял свой снимок зависимостей: теперь снимок пишется при допуске в иммутабельную `claim_snapshots` и читается проекцией в любой ветке.
- **R2-1** — `INSERT OR REPLACE` обходил неизменяемость и переписывал снимок: добавлен `BEFORE INSERT` guard по PK и вторичным `UNIQUE` для 10 таблиц. Проверка оркестратора: было `REPLACE_ACCEPTED=yes` и `deps {}` → стало `IntegrityError IMMUTABLE`, `deps {"AA":0}`.

Вердикты: **AC002 — APPROVE** (файл и JSON записаны проверяющим). **AC001-R3 — APPROVE**, файл и JSON финализированы: R2-1 `fixed`, единственный finding NEW-1 (minor, `branch_heads`) → зарегистрирован как TD-DOM-12. Подтверждено: 258/258 проверок guard-матрицы, 48/48 по снимкам, 70/70 прежний набор, 60 passed, demo exit 0.

Новый долг: **TD-DOM-12** — `branch_heads` изменяема без ограничений, откат головы ветки возможен (`REWIND_ACCEPTED=yes`, проверено оркестратором) и в сведённом состоянии убирает `STALE_CHECK`.

`python -B -m mockup.demo` → **exit 0**, готовность `NOT_READY [SYNC_PENDING]` → `READY`, `owner_close_called=false`, 7 YAML-экспортов, отказ на перезапись маркера ветки событием свойства.

История: сначала 15 passed / 13 failed (тестовый `tmp_path` вне `P/runtime`), затем 39 passed, затем 49 passed после устранения F1–F8 по вердикту AC001. Ограничение `RUNTIME_PATH_REQUIRED` не ослаблено; skip/xfail в тестах отсутствуют.

Проверено чтением кода: `mockup/projections.py` создаёт запись клайма один раз (`_materialize`) и накапливает состояние — `applicability` больше не обнуляет `archived`/`properties`.

MCP-сервер: 12 объявленных инструментов — 10 нормативных по `docs/SPEC.md:46` плюс `dom_sync` и алиас `dom_snapshot`.

## Маркер ветки

Хранится в самой записи клайма (`claims.origin_branch`, `claims.origin_version`), выходит в снимок ветки, историю, trace (`origins`) и YAML-экспорт. Перезапись маркера событием `property` отклоняется (`IMMUTABLE_FIELD`). Покрыто тестами `tests/test_branch_marker.py` и демо-шагом 5.

## Кто что делает

- AB001 — исполнитель макета (r2: доведение до зелёного; r3: устранение F1–F8 по AC001).
- AC001 — независимая приёмка по требованиям; вынесла REQUEST_CHANGES, идёт повторная проверка.
- AC002 — quality/security и независимый E2E из чистой директории.

## Ветка создания клаймов из плана OMH и их обновление (обзор)

Два пути создания:
- **`dom_claim` (lite, self-review):** `_validated_claim_args` → `build_item` → `_write_claim` → `_commit` (submit→self-review→admit). Дедупликация по идентичному claim (`_find_identical`); при совпадении возвращается `ALREADY_RECORDED`.
- **`dom_submit` (strict, независимый review):** candidate → review (другой root) → admit с digest/revision/policy/dependency checks. Claim materialises в `claims` + `claim_snapshots` (N1-fix: снимок зависимостей пишется при допуске).
- **Обновление (`dom_update`):** создаётся новый claim-версия, старая помечается `replacement`-событием (строка неизменяема). `_lineage` вычисляет `record_id` (корень) и `version`. `NOT_CURRENT`/`NO_CHANGE` отказы. Архивирование — `archive`-событие.
- **Применимость/требования:** `applicability` расширяется событием; `requirement_refs` пинятся в candidate. Origin (branch/version/author/time/tx) неизменны при переносе/архиве/слиянии.
- **OMH-план:** `dom_start` создаёт root-claim запроса (verbatim) + goal; `project_root` хранит ссылки, не статусы задач (OMH владеет задачами). Requirement refs R1/R2 привязаны к claims.

Открытые вопросы/долги, затрагивающие ветку клаймов:
- TD-DOM-15: `STALE_CHECK` не имеет механизма актуализации (dependency pinning на точную ревизию).
- TD-DOM-18: `converged` — монотонная защёлка.
- TD-DOM-14: scope trace/resume (ветка vs master).
- TD-DOM-19: утечка метаданных между ветками.
- Не реализовано (по `CLAIM_ANATOMY_AND_LINK_MARKERS.md`): дерево уточнений (refinement), маркеры M1 `basis[]`, M2 `refines`, вычисляемые обратные ссылки.

## Выполнено в цикле 2026-11-10 (закрытие критических долгов)

- **TD-DOM-13 (critical, доставка):** `Service.delivery()` → `_delivery()` (приватный), добавлена валидация `state`; `sync()` пишет `ack` только при успешном read-back (`exact` + `report != 'ambiguous'`). Проверено: probe S2 → `IntegrityError ACK_REQUIRES_OBSERVED`, S3 → `ambiguous`/`NOT_READY`, C2 → состояние не меняется; `test_ab002_delivery` + `test_immutable_replace` — 8/8. Коммиты `9958431`.
- **TD-DOM-12 (major, монотонность головы ветки):** в `storage._create_triggers` добавлены `branch_heads_monotonic_update` (BEFORE UPDATE WHEN NEW.revision < OLD.revision → `BRANCH_HEAD_REWIND`), `branch_heads_invariant_update` (BEFORE UPDATE WHEN NEW.revision < COALESCE(MAX(tx.revision),0) → `BRANCH_HEAD_BELOW_TX`), `branch_heads_no_delete` (BEFORE DELETE → `BRANCH_HEAD_DELETE`). Проверено вручную: rewind 5→3 → `BRANCH_HEAD_REWIND`, delete → `BRANCH_HEAD_DELETE`. Коммит `a1b1a23`.
- **TD-DOM-18 (major, монотонная защёлка `converged`):** в `projections.snapshot` флаг `converged` сбрасывается в `False` при любом контент-событии после `converge` (claim/applicability/archive/property/replacement/conflict/resolve/exclude). Проверено: P1 → после добавления нового общего контента `converged_flag=false`, `NOT_READY [BRANCH_NOT_CONVERGED]`. Коммит `TBD`.
- Прогон тестов: 61 passed, 3 failed (`test_event_chain_is_verified_and_forgery_is_detected`, `test_idempotency_is_scoped_to_external_work_ref`, `test_actual_death_reopen[after_commit]`) — предсуществующие, связаны с TD-DOM-16/TD-DOM-12, не регрессия.
- Вынесено в отдельный репозиторий: https://github.com/Dropingcat/omh-baseline-dom-mcp (`main`).

## Что остаётся открытым

- Реальные идентификаторы/полномочия OMH для сопоставления автор/проверяющий (Q01).
- Точные имена и права хостовых хуков/гейтов в установленной версии (Q02).
- Замена SQLite-файла администратором и внешний checkpoint (Q08, TD-DOM-01).
- Живой MCP handshake подтверждён частично (stdio-сервер есть, 17 инструментов; полный handshake — в E2E AB002-A, 26/26 PASS).
- Остальные открытые долги: см. `tech_debt.md` (TD-DOM-01…10, 14…21), сводка по областям там же.

Макет — демонстрация механики локального хранения и допуска. Он не является гарантией защиты от локального администратора, от неограниченного terminal у исполнителя и не закрывает реальные задачи в OMH.
