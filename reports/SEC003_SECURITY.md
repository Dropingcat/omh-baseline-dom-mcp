# SEC003 — Negative security / inter-branch isolation audit

| | |
|---|---|
| Роль | SEC003 security specialist (не product worker, не принимающий) |
| Code digest | `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3` (пересчитан: 15 файлов, 0 расхождений с `runtime/PL003/input_fingerprints.json`) |
| Вердикт | **REQUEST_CHANGES** (никогда SAFE; не product acceptance) |
| completion_state | completed (полный собственный материал + validation.json на диске) |
| product_acceptance / is_approval | false / false |
| Канонические прогоны | `run-3101-f7fc7e4b`, `run-3109-31020cee` (оба SEED*_EXIT=0, progress 13/13 done) |
| Первый evidence-прогон | `run-3101-85478e2b` (hp-04 с прежним багом; сохранён, не удалён) |

---

## 0. Подозревал → проверил → оказалось

1. **SUS-01: хостовый PYTHONPATH тенит mcp/pydantic и ломает импорты харнесса** (из CONTINUE_02: `ModuleNotFoundError: No module named 'runtime'`).
   - Проверил: чистый запуск `env -i` + venv-питон `-B`, cwd=P; `scenarios.py` вставляет `sys.path.insert(0, P)`, где `P = HERE.parents[1]` (корень проекта); `importlib.util.find_spec` подтвердил, что `runtime.SEC003.engine` и `mockup.server` резолвятся в проектные пути.
   - **Оказалось: опровергнута как дефект продукта.** Механизм импорта харнесса корректен; падение CONTINUE_02 было следствием хостового PYTHONPATH + запуска не из cwd=P. При чистом env оба канонических прогона завершились exit 0.
2. **SUS-02: link-sensing поверхность (H-LINK / CP-PL-17 / SC-H-LINK) может существовать скрыто и лить чужие ссылки.**
   - Проверил: tools/list на wire + AST-инвентарь mockup; зарегистрированных link/backlink/dashboard/sensing тулов нет.
   - **Оказалось: GAP подтверждён.** Поверхности нет (GAP-LINKS / NOT_IMPLEMENTED), записано со схемными доказательствами в `receipt-gaps.json`; статус GAP, не PASS и не NOT_APPLICABLE.
3. **SUS-03: snapshot/query «поиск» может подменить отсутствующий search-канал.**
   - Проверил: GAP-SEARCH / GAP-BRANCH-SEARCH / GAP-REFINEMENT на wire отсутствуют; snapshot использовался только как snapshot.
   - **Оказалось: GAP, snapshot поиском не выдан.**
4. **SUS-04: AA-only read-поверхности отдают скрытые AB revision/chain metadata (гипотеза TD19).**
   - Проверил: полевой дифференциал query/snapshot/trace/resume/sync_status/export при фиксированном AA и мутированном скрытом AB на двух seed; B-only B read контроль; B-контроль повторён после негативов.
   - **Оказалось: подтверждено.** `read_snapshot.revisions = {"AA":5,"AB":7}` и AB-инклюзивный `chain_head` видны AA-only caller'у; повреждённый средний AB event отдаёт запрещённый UUID через `chain.broken_event_id`. Это воспроизведение известного **TD-DOM-19** (не новая регистрация, не закрытие).

---

## Покрытие (24 check_id из runtime/PL003/failure_map.json)

- **EXECUTED_NEGATIVE (12):** CHK-A2-01, CHK-A2-02, CHK-A2-03, CHK-A2-04, CP-PL-01, CP-PL-02, CP-PL-03, CP-PL-04, CP-PL-07, CP-PL-14, CP-PL-15, CP-PL-16.
- **GAP (4):** CP-PL-11, CP-PL-12, CP-PL-13, CP-PL-17 (search/branch-search/refinement/link surfaces отсутствуют; схемные доказательства в `receipt-gaps.json`).
- **NOT_TESTED → QA003 (8):** CHK-A2-05, CHK-A2-06, CHK-A2-07, CP-PL-05, CP-PL-06, CP-PL-08, CP-PL-09, CP-PL-10 (availability/shape-кейсы переданы QA с точными статусами/омиссиями; честно NOT_TESTED, не PASS).
- **Собственная негативная вариация сверх старой семёрки:** SEC-NOV-01 (branch-scoped candidate/review replay + applicability/history join differential; AA fixed, hidden AB mutated) — EXECUTED_NEGATIVE, без новой утечки сверх TD19-поверхностей.

Положительные контроли: AA own submit→review→admit; B-only читает B body/source/ID; B-контроль повторён после негативов.

## Находки (escape hatch)

### SEC003-F-01 — TD-DOM-19 воспроизведён (major, confidentiality)
- **Граница:** branch-scope изоляция: AA-only caller не должен видеть AB revision counts / chain metadata / foreign locators.
- **Минимальное воспроизведение:** AA-only (`role=author`, `branches=AA`) вызывает `dom_snapshot`/`dom_query`/`dom_trace`/`dom_resume`/`dom_sync_status`/`dom_export`: `read_snapshot.revisions` возвращает `{"AA":5,"AB":7}`; `chain_head` включает AB; повреждённый средний AB event утекает своим UUID через `chain.broken_event_id`.
- **Expected:** только AA-метаданные. **Actual:** AB-счётчики и AB-инклюзивный chain_head видны AA-only.
- **Raw evidence:** `receipt-hp-14.json` (`aa_ok/read_snapshot/chain_head`, revisions), `receipt-hp-07.json` (`export_ok/.../revisions {"AA":5,"AB":7}`), `receipt-lp-a2-04.json` (`aa_master_trace`/`union_master_trace` revisions) в обоих канонических run; sha256 в `artifacts/SEC003_SECURITY.json`.
- **debt_ref:** TD-DOM-19 (`tech_debt.md` row 33; `cards/AB003_TD19_WORKER_PREPARED.md` — обязательный P0 fix, не DISPATCHED). **Не дублируется и не закрывается; TD20/TD21 тоже не трогаются; `debt_status_changes=[]`.**
- **Mitigation (без правки продукта):** скоупинг integrity-gate диагностических/metadata полей по branch scope caller'а.

## Омиссии и ограничения

- Timing-атаки: **NOT_CHECKED** (только заданная bounded exploratory серия, без замеров).
- Сильный OS sandbox / external checkpoint / live auth / Git / OMH: вне simulation scope.
- Полное Cartesian покрытие / full-system acceptance: не заявляется.
- Логическая граница trusted oracle ≠ сильная OS-изоляция (агент с terminal — отдельная threat model).
- Никаких реальных секретов/live БД/конфигов/плагинов; только disposable fixture.

## Верификация

- `digest_check.py`: digest совпал, 15/15 per-file hashes без расхождений.
- `manifest_run.py` (create-only): `run-3101-f7fc7e4b` (759 entries), `run-3109-31020cee` (759), `run-3101-85478e2b` (753); точные byte-хаши вне manifest в `evidence_refs`.
- `verify.py` (последним) → `runtime/SEC003/validation.json`: статусы/ID/пути/хеши/evidence refs + присутствие финальных артефактов; реальный exit код.

## Вердикт

**REQUEST_CHANGES** — известная major-утечка TD-DOM-19 воспроизведена на текущем коде; P0 fix обязателен (`cards/AB003_TD19_WORKER_PREPARED.md`, не DISPATCHED). Этот security run не заменяет и не отменяет обязательный fix и не является приёмкой продукта.
