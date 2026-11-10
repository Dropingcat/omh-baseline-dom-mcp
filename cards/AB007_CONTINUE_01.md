# AB007 CONT-01 — записать три артефакта

Код исправлен (`mockup/admission.py`), регрессия проверена, числа замерены. Осталось **только** записать артефакты. Код не менять.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P.

## Версия
`digest_before = c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505`
`digest_after  = 3cd21d96ff2f83f014f00c3fdf5b21c6ef94c26525385ef6a014365387d8aad0`
Метод: `sha256(json.dumps({'mockup/<posix>': sha256}, sort_keys=True))` по 16 файлам. Пересчитай **сам** и сверь; изменён ровно `admission.py`.

## Источники данных
`runtime/AB007/results/probe_before.json`, `probe_after.json`; `runtime/AB007/probes/**`; `runtime/AB007/fixtures/**`.

## Что записать
`artifacts/WORKER_AB007.json`:
- `changed_files` (ожидается ровно `mockup/admission.py`), `digest_before`, `digest_after`, `digest_method`;
- `findings_fixed`: F1 — что теперь отклоняется (`''`, `:x`, `AA:`, `AA:x:y`, `AA`, `123` → `REJECTED`), что разрешено (`None`, валидный `AA:<uuid>`), и что `AA :x` осознанно разрешён как keyset-позиция;
- F2 — корень (фильтр шёл после `LIMIT`), решение (фильтры видимости в SQL до `LIMIT`), инвариант `union == все видимые, пока count > 0`, результаты walk-ов (AA l1/l2, AB l1, full l2, дублей 0);
- F3 — `has_more` теперь после фильтрации, скрытые строки его не раздувают;
- `regression{}`: контракт RS007, admitted исключён, текст не отдаётся, `NO_SUCH_BRANCH`/`SCOPE_DENIED`/`DIGEST_MISMATCH`, миграция v2 идемпотентна, 39 триггеров, 2 индекса;
- `perf{}`: p1k 11.5→14.2 мс, p100k 1534.8→1704.0 мс (+11%, медиана 4 замеров), в границах контракта 10×;
- `known_notes[]`: smoke-баг фикстуры (`claim_ref` должен быть id допущенного claim, не кандидата) — путь продукта не затронут; дисплейный артефакт `probe_before` со `status:"raised"` — факт иной;
- `evidence_refs[]` с путями и sha256; `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`.

`reports/WORKER_AB007.md` — что исправлено, чем подтверждено, отдельный раздел про инвариант пагинации и про то, что F1 признан аудитором не-уязвимостью (принят, но scope-safe), исправлен всё равно — defense in depth.

`docs/SCHEMA_CHANGE_AB007.md` — изменение семантики пагинации: фильтрация до `LIMIT`, `next_cursor` при пустой странице, `has_more` после фильтрации, правила валидации `after`, влияние на стоимость.

## Границы
Только эти три файла. Код, тесты, долги, конфиги, OMH — не трогать. Ориентир 15 вызовов.
