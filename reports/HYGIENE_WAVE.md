# HY001 · волна 2 — гигиена записи прогона

Роль: CONT-01. Задача — зафиксировать выходы после готового механизма
`runtime/LIVE/lib` и не переписывать историю волны 1.

- Машинный отчёт: `artifacts/HYGIENE_WAVE.json`
- Критерии волны 2: `runtime/LIVE/acceptance_wave2.json`
- Результат проверки прогона `hy-02`: `runtime/LIVE/LIVE_WAVE2_VERIFY_h02.json`

(`acceptance_wave1.json` не тронут; `run`/`verify` волны 1 остались как были.)

## Что изменено в `runtime/LIVE/lib/**`

| Файл | Что делает | Зачем |
|---|---|---|
| `runner.py` | W3-слой записи: **один процесс = один таймлайн** (монотонная `seq`, свой `client_id` на процесс). Обрыв пишется строкой `kind=interrupt` (`tool=_reconnect_new_client`, новый `client_id`) в **тот же** `timeline.jsonl`, а не склейкой двух логов. У каждого шага — сырой кадр `raw/step{seq}_{tool}.json` (кроме синтетической строки reconnect). `intent_matches_effect` — **функция(status)** (`OK→true`), не ручное значение. `env_events` структурно: `failpoint` + `ts` + `effect`. | Прямо закрывает D3_FRAME, D3_INTENT, D3_SPLICE, D3_ENV из волны 1. |
| `verify_run.py` | Авто-сверка артефакт ↔ таймлайны/кадры/`summary.json`/копии DOM-баз. Машино-проверяемые коды: D1, D2, D3_FRAME, D3_INTENT, D3_SPLICE, D3_ENV, D4_DOUBT, D4_REFUSAL, D6. Выход: **PASS (exit 0)** без расхождений, иначе список и exit 1. | Заслон перед сдачей: на волне 1 обязан падать, на чистом самопрогоне — проходить. |
| `w2util.py` | `write_summary` пишет `summary.json` со **всеми** полями сценария (doubts, refusals, env_events, missing_frames). `seed_scenario` готовит фикстуру через **два независимых principal** (owner submit → reviewer review/admit) поверх реального MCP + `fixture_snapshot`. | `summary.json` был обязателен (код D1); волна 1 для L1-01 его не записала. |

## Результат валидатора на волне 1

`verify_run.py artifacts/LIVE_WAVE1_RUN.json runtime/LIVE/wave1 --scenarios runtime/LIVE/scenarios_wave1.json`
→ **FAIL, exit 1**, 9 расхождений:

| Код | Кол-во | Сценарий | Находка | Файлы |
|---|---|---|---|---|
| D1 | 1 | L1-01 | `complete`, а `summary.json` на диске нет | `runtime/LIVE/wave1/L1-01/summary.json` (отсутствует) |
| D3_FRAME | 4 | L1-01, L1-02 | у шага таймлайна нет сырого кадра (L1-02: seq1/3/5) | `runtime/LIVE/wave1/L1-0X/raw/step{seq}_{tool}.json` |
| D3_INTENT | 1 | L1-02 | `seq3 DENIED` с `intent_matches_effect=true` против функции (`DENIED→false`) — ручное значение | `runtime/LIVE/wave1/L1-02/timeline.jsonl` |
| D3_SPLICE | 1 | L1-02 | два `exec-*` процесса, а события interrupt/границы нет — таймлайн склеен | `runtime/LIVE/wave1/L1-02/raw/exec-*.jsonl`, `env.log` |
| D4_DOUBT | 2 | L1-03, L1-04 | сомнение из `summary` отсутствует в `doubts` артефакта | `runtime/LIVE/wave1/L1-0X/summary.json` vs `artifacts/LIVE_WAVE1_RUN.json` |

Итого **9** расхождений: D1=1, D3_FRAME=4, D3_INTENT=1, D3_SPLICE=1, D4_DOUBT=2.

## Результат на чистом прогоне

`verify_run.py runtime/LIVE/hygiene_selftest/LIVE_WAVE2_RUN.json runtime/LIVE/hygiene_selftest`
→ **PASS, exit 0**, расхождений 0.

## Прогон `hy-02` (был пропущен — теперь зафиксирован)

`verify_run.py runtime/LIVE/hygiene_selftest/LIVE_WAVE2_RUN_h02.json runtime/LIVE/hygiene_selftest`
→ **PASS, exit 0**. Полный результат: `runtime/LIVE/LIVE_WAVE2_VERIFY_h02.json`.
Что проверено: `kill_process_then_new_client after step 2` → обрыв на шаге 3
(транспортный `MCPError`, `intent_matches_effect=false`) → продолжение **в том же
таймлайне** строкой `kind=interrupt` с новым `client_id=17ae16f0`; у всех шагов
кадры; `env_events` — `failpoint`+`ts`+`effect`; final revision/`claim_origins`
согласованы с DOM-базой.

## Самопроверочные прогоны

- **hy-01** (`hy01_selftest.py`): одна ветка AA, один чистый процесс, свежий
  базлайн, judge доступен. Ожидаемый «правильный» прогон: complete, admit
  независимым reviewer, кадры на шаг, intent — функция(status), `env_events=[]`,
  `summary.json` полный. → PASS.
- **hy-02** (`hy02_selftest.py`): одна ветка AA, failpoint `kill_process_then_new_client
  after step 2`, продолжение через interrupt в том же таймлайне. → PASS.

## Находка → как теперь ловится

| Находка волны 1 | Теперь ловится |
|---|---|
| `complete` без `summary.json` на диске | `D1` в `verify_run.py` (сверка артефакта против диска) |
| У шага таймлайна нет сырого кадра | `D3_FRAME`: для каждого `seq` проверяется наличие `raw/step{seq}_{tool}.json` |
| `intent_matches_effect` — ручное, не по статусу | `D3_INTENT`: сравнивается с функцией `status==OK` |
| Два процесса склеены в один таймлайн без отметки | `D3_SPLICE`: несколько `exec-*` логов требуют строку `interrupt`/env-границу |
| Сомнение появилось в `summary`, но не в артефакте | `D4_DOUBT` (и `D4_REFUSAL` для отказов): ключи из `summary` обязаны быть в `doubts`/`refusals` |
| Нет фиксации failpoint в окружении | `D3_ENV`: настроенный failpoint обязан быть в `env_events` с `ts`+`effect` |
| Расхождение числа шагов / ревизий артефакта и диска | `D2` (шаги), `D6` (ревизии финального снимка vs DOM-база) |
| (новое, целевое) граница процесса на обрыве | сам `runner.py`: строка `kind=interrupt`, новый `client_id`, единая `seq` |

## Критерии волны 2

`acceptance_wave1.json` не менялся. В `acceptance_wave2.json` критерий C1
разделён на два:

- **C1a** «содержимое чужой ветки не раскрывается» — текст/тело, идентификаторы,
  зависимые счётчики чужой ветки;
- **C1b** «происхождение расшаренного клайма раскрывается легально» — для
  клайма, который читатель вправе получить (включая явно расшаренный через
  `applicability`/`shared_from`), `origin_branch`/`origin_version` и те же
  сведения в `Trace.origins`/`Residual.claim_origins` показываются как метаданные
  и не скрываются из-за имени ветки происхождения (решение заказчика O2 от
  2026-11-08, `docs/DECISION_BRIEF_2026-11-08.md`). При этом раскрытие
  происхождения не даёт содержимого исходной ветки и произвольных чужих
  dependencies/head-ревизий/diagnostic locators.

C2–C7 перенесены из волны 1 без изменений.