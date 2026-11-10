# HY001 CONT-01 — дописать выходы (та же роль)

Механизм готов и проверен: `verify_run.py` **падает** на волне 1 (9 расхождений: D1, D3 по L1-02 с отсутствующими кадрами и склеенным таймлайном, D4 по L1-03/L1-04) и **проходит** на чистом прогоне `hygiene_selftest/hy-01`. Не переделывать.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P.

## Остаток (ровно три файла + одна проверка)
1. `runtime/LIVE/acceptance_wave2.json` — C1 разделить на **C1a «содержимое чужой ветки не раскрывается»** (текст, идентификаторы, счётчики) и **C1b «происхождение расшаренного клайма раскрывается легально»** (origin_branch как метаданные, в согласии с решением O2); C2–C7 перенести без изменений. `acceptance_wave1.json` не трогать.
2. `artifacts/HYGIENE_WAVE.json` — что изменено в `runtime/LIVE/lib/**`, результат валидатора на волне 1 (9 расхождений с кодами D1/D3_FRAME/D3_INTENT/D3_SPLICE/D4_DOUBT и ссылками на файлы), результат на чистом прогоне (PASS exit 0), и краткое описание selftest-прогонов `hy-01`, `hy-02`.
3. `reports/HYGIENE_WAVE.md` — то же человеческим языком, с таблицей «находка → как теперь ловится».
4. Прогнать `verify_run.py` на `LIVE_WAVE2_RUN_h02.json` и записать результат (был пропущен).

## Границы
Запись только в эти три файла (+ результат прогона валидатора в `runtime/LIVE/`). Историю волны 1 не переписывать. Продукт/tests/tech_debt/конфиги read-only. Без Git/install/платных/субагентов/сети. Ориентир 15 вызовов. `product_acceptance=false`, `is_approval=false`.
