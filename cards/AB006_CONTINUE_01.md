# AB006 CONT-01 — довести проверки и артефакты (та же роль)

Код изменён и линт-чист, но **доказательной базы и артефактов нет**. Задача — только они. Код не переписывать, кроме случаев, когда проверка покажет дефект.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P.

## Сначала — расхождение digest (обязательно разрешить до отчёта)
Заявлено `before=3a5f875b…`, `after=3f0af9c4…`. **Ни одно не совпадает с диском.** Родитель пересчитал по документированному методу (`sha256(json.dumps({relpath→sha256}, sort_keys=True))` по 16 `mockup/**/*.py`, posix-пути) и получил:

- **текущее состояние: `c26812b398ef533266ece998df611ff73707abc54b79343bbc32eb84386bd505`**
- состояние после AB005 (подтверждено RV005 и AU007): `ca227b17b67a0d85d71aba6703c3d0910265198a68fe2ea064e4f52faec9f6b7`

Требуется:
1. Найти свой скрипт/метод расчёта и объяснить, почему он дал другие значения (иной набор файлов? иные пути? учёт `__pycache__`? расчёт до финальных правок?).
2. Пересчитать **обе** величины документированным методом и записать их буквально.
3. Если окажется, что между AB005 и AB006 изменились файлы сверх четырёх заявленных (`admission.py`, `storage.py`, `public_dto.py`, `server.py`) — назвать их явно. Это дефект, а не мелочь.
4. В отчёте указать расхождение и его причину отдельным абзацем; не подгонять числа.

## Затем — остаток
1. Перезапустить `runtime/AB006/probes/run_checks.py` (IndexError на limit=1 уже исправлен). Нужны: идемпотентность миграции (legacy-src → `user_version=2`, триггеры, индексы), **perf 1k / 100k / noindex** против границ из `runtime/RS007/answers/answers_options.json`, **сырые MCP-кадры** (`probes/mcp_raw.py` написан, но не вызывался), SQL-счётчики до/после pos1, `checks_summary.json`.
2. Подтвердить негативы: чужой грант (AB), суженный грант, admitted не выдаётся, `NO_PENDING` на w3, anti-exists-oracle (`count` тоже фильтрован), отсутствие payload-текста в `items`.
3. Записать `artifacts/WORKER_AB006.json` (`status`, `changed_files[]`, `digest_before`, `digest_after`, `digest_method`, `digest_discrepancy`, `evidence[]`, `pos_results[]`, `neg_results[]`, `perf{}`, `page_underfill_edge`, `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`), `reports/WORKER_AB006.md`, `docs/SCHEMA_CHANGE_AB006.md`.

## Границы
Не трогать F-01/`delivery.py`/тесты/tech_debt/конфиги/OMH. Копии БД — только `runtime/AB006/`. Без Git/install/платных/субагентов. При лимите — сначала артефакт и отчёт, потом стоп. Ориентир 35 вызовов.
