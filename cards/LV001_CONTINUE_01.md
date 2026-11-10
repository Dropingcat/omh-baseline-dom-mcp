# LV001 CONT-01 — довести волну 1 (та же роль исполнителя)

Продолжение после обрыва по лимиту итераций. Режим слепоты сохраняется полностью: запрещены `artifacts/**`, `reports/**`, `docs/**`, `cards/**` (кроме этого файла), `runtime/AB00*/**`, `runtime/AU*/**`, `runtime/RV*/**`, `runtime/LIVE/acceptance_wave1.json`.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env.

## Что уже сделано (проверено родителем на диске — не переделывать)
- `runtime/LIVE/wave1/lib/{client,launchlib,runner,seeds}.py` — рабочий каркас.
- **L1-01 завершён**: 6 шагов, `timeline.jsonl` на месте, 22 файла, `dom.sqlite3`/`fixture.db`.
- **L1-02 частично**: 5 шагов (resume → snapshot AA → query AB `SCOPE_DENIED` → submit вывода → review). Нет admit, верификационного snapshot и `summary.json`.

## Точный остаток
1. **L1-02**: `dom_admit` через отдельную идентичность `reviewer`, затем верификационный `dom_snapshot`/`dom_resume`, затем `summary.json`.
2. **L1-03** целиком: фикстура (AA+AB, оба в гранте) → работа по задаче → failpoint `narrow_grant_to_AA` **после шага 3** (исполняется средой, не тобой) → продолжение → `summary.json`.
3. **L1-04** целиком: фикстура (AA), `llm_judge` недоступен, failpoint `kill_process_then_new_client` **после шага 4** → новый клиент без памяти → `summary.json`.
4. **Итоговые артефакты обязательны независимо от того, сколько успел**: `artifacts/LIVE_WAVE1_RUN.json`, `reports/LIVE_WAVE1_RUN.md` с `incomplete: true` и точным перечнем незавершённого.

## Правила среды (иначе прогон недействителен)
- Ревью и допуск выполняет **отдельный процесс** с ролью `reviewer`; исполнитель не может ревьюить и допускать своё (`INDEPENDENCE_NOT_ENFORCED` — это ожидаемое поведение, не ошибка среды).
- `state_before`/`state_after` только из `dom_snapshot`/`dom_resume`, не из SQL.
- Failpoints исполняет среда: сужение гранта и убийство процесса не имитируются вручную.
- Если инструмент ответил `DENIED` обычным ответом (а не `isError`) — фиксируй `status=DENIED` с кодом, не подгоняй под OK.
- Никаких оценок «правильно/неправильно», только `why` и наблюдения.

## Бюджет
Ориентир **60 вызовов** на остаток. Если не хватает — **сначала** допиши `summary.json` по сделанным сценариям и оба итоговых артефакта, и только потом останавливайся. Прогон без артефактов бесполезен, поэтому артефакты важнее полноты сценариев.

## Запись разрешена только в
`runtime/LIVE/wave1/**`, `artifacts/LIVE_WAVE1_RUN.json`, `reports/LIVE_WAVE1_RUN.md`. Продукт, тесты, долги, конфиги — не трогать.
