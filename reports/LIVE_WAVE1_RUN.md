# LIVE Wave 1 — итоговый отчёт прогона (LV001, CONT-01)

- Сформирован: `2026-11-08T12:11:10+00:00`
- Прогон: `LIVE_WAVE1_RUN` (wave 1, живые stdio MCP-процессы, реальный mockup-сервер, per-scenario launch.py)
- **Статус: `incomplete: true`**

## Незавершённое (точный перечень)

- **L1-04**: незавершённый допуск (admit)

## Сводка сценариев

| Сценарий | Шагов | Допуск (admit) | Отказы | Сомнения | Статус |
|----------|-------|----------------|--------|----------|--------|
| L1-01 | 6 | да, шаг 5 | 0 | 0 | complete |
| L1-02 | 8 | да, шаг 6 | 1 | 0 | complete |
| L1-03 | 10 | да, шаг 8 | 1 | 0 | complete |
| L1-04 | 9 | нет | 2 | 1 | incomplete |

## L1-01 — complete

| Шаг | Инструмент | Через | Статус | Код | why |
|-----|-----------|-------|--------|-----|-----|
| 1 | `dom_resume` | exec | OK | `RESUMED` | Начинаю работу. Единственная память о проекте — база; сначала осматриваю состояние ветки AA через dom_resume. |
| 2 | `dom_query` | exec | OK | `SNAPSHOT` | Нужно понять, что именно установлено: снимаю снапшот ветки AA, чтобы увидеть текст утверждения про метод M. |
| 3 | `dom_append` | exec | OK | `RECORDED_CANDIDATE` | Фиксирую уточнение условий применимости метода M: исходное утверждение не переписываю (клаймы иммутабельны), д |
| 4 | `dom_review` | reviewer | OK | `DEMO_REVIEWED` | Кандидат-уточнение записан. Для допуска требуется независимое ревью (собственный principal ревьюить не может — |
| 5 | `dom_admit` | reviewer | OK | `DEMO_ADMITTED` | Ревью получено. Допускаю уточнение в ветку AA (admit должен выполнить principal, отличный от submitter — поэто |
| 6 | `dom_snapshot` | exec | OK | `SNAPSHOT` | Проверяю результат: снимаю снапшот AA — исходное утверждение должно остаться, уточнение должно быть зафиксиров |

## L1-02 — complete

- Примечание: L1-02 завершён: SCOPE_DENIED на AB зафиксирован, вывод допущен независимым reviewer, верификация снапшотом и резюме.

| Шаг | Инструмент | Через | Статус | Код | why |
|-----|-----------|-------|--------|-----|-----|
| 1 | `dom_resume` | exec | OK | `RESUMED` | Осматриваю доступную мне ветку AA: что установлено по вопросу (ограничение O и наблюдаемый случай). |
| 2 | `dom_query` | exec | OK | `SNAPSHOT` | Снимаю полный снапшот AA: мне нужно увидеть текст наблюдения и его метаданные (origin AB — это shared_from). |
| 3 | `dom_query` | exec | DENIED | `SCOPE_DENIED` | Ограничение O заявлено в базе; пробую прочитать ветку AB, чтобы оценить, действует ли O для наблюдения N. Если |
| 4 | `dom_submit` | exec | OK | `RECORDED_CANDIDATE` | Формирую честный вывод на основе доступного: O в AB мне не доступен (SCOPE_DENIED), но вижу N в AA с origin AB |
| 5 | `dom_review` | reviewer | OK | `DEMO_REVIEWED` | Записанный вывод требует независимого ревью (llm_judge доступен) — отправляю ревьюеру. |
| 6 | `dom_admit` | reviewer | OK | `DEMO_ADMITTED` | Вывод записан и независимо отревьюерен (llm_judge, роль reviewer). Допускаю кандидата в AA: admit исполняет pr |
| 7 | `dom_snapshot` | exec | OK | `SNAPSHOT` | Проверяю результат допуска: снапшот AA должен показать новую ревизию с допущенным выводом (ревизия должна выра |
| 8 | `dom_resume` | exec | OK | `RESUMED` | Финальное состояние сессии: резюмирую AA — вывод допущен, ограничение O из AB осталось вне гранта (зафиксирова |

Отказы (1):
- шаг 3 `dom_query` → `DENIED/SCOPE_DENIED` — Ограничение O заявлено в базе; пробую прочитать ветку AB, чтобы оценить, действует ли O для наблюдения N. Если грант не покрывает AB — зафик

## L1-03 — complete

- Примечание: L1-03 завершён: сужение гранта AA+AB->AA исполнено средой после шага 3; наблюдаемое последствие — SCOPE_DENIED на AB (шаг 4); вывод допущен независимым reviewer; верификация снапшотом и резюме.

Наблюдения среды (failpoints):
- `FAILPOINT: narrowing executor grant from ('AA', 'AB') to AA after step 3`
- `FAILPOINT: executor relaunched with branches=AA (new process, same DB)`

| Шаг | Инструмент | Через | Статус | Код | why |
|-----|-----------|-------|--------|-----|-----|
| 1 | `dom_resume` | exec | OK | `RESUMED` | Начинаю работу по задаче. Грант покрывает AA и AB; сначала осматриваю AA: что установлено по измерению P. |
| 2 | `dom_resume` | exec | OK | `RESUMED` | Вторая ветка AB входит в грант: смотрю, что заявлено по гипотезе H (частичное подтверждение) — это второй исхо |
| 3 | `dom_snapshot` | exec | OK | `SNAPSHOT` | Снимаю полный снапшот AA как базовую ревизию (expected_branch_revision для будущего submit) и фиксирую текст и |
| 4 | `dom_query` | exec | DENIED | `SCOPE_DENIED` | Пробую продолжить чтение AB (гипотеза H). Ожидаю, что узкий грант может его закрыть: если SCOPE_DENIED — фикси |
| 5 | `dom_snapshot` | exec | OK | `SNAPSHOT` | После сужения гранта перепроверяю доступный материал: снапшот AA — текст измерения P и актуальная ревизия для  |
| 6 | `dom_submit` | exec | OK | `RECORDED_CANDIDATE` | Фиксирую вывод как новый claim в AA (applicability только AA): опираюсь на то, что реально видел, и явно фикси |
| 7 | `dom_review` | reviewer | OK | `DEMO_REVIEWED` | Вывод записан. Для допуска нужно независимое ревью — его делает отдельный процесс с ролью reviewer (llm_judge) |
| 8 | `dom_admit` | reviewer | OK | `DEMO_ADMITTED` | Ревью получено. Допускаю вывод в AA (admit — отдельная идентичность reviewer, не submitter). |
| 9 | `dom_snapshot` | exec | OK | `SNAPSHOT` | Проверяю результат: снапшот AA должен показать выросшую ревизию и допущенный вывод. |
| 10 | `dom_resume` | exec | OK | `RESUMED` | Финальное состояние: резюмирую AA — допущенный вывод на месте, грант остаётся узким (AA). state_after только и |

Отказы (1):
- шаг 4 `dom_query` → `DENIED/SCOPE_DENIED` — Пробую продолжить чтение AB (гипотеза H). Ожидаю, что узкий грант может его закрыть: если SCOPE_DENIED — фиксирую отказ как факт и перестраи

## L1-04 — incomplete

- Примечание: admit не выполнен: llm_judge недоступен, self-review отклонён (INDEPENDENCE_NOT_ENFORCED); кандидат записан, ревизия AA не выросла
- Примечание: L1-04 не завершён по дизайну: процесс убит средой после шага 4 (транспортный обрыв зафиксирован), новый клиент восстановился из базы; llm_judge недоступен, self-review отклонён (INDEPENDENCE_NOT_ENFORCED) — независимый допуск вывода невозможен. Кандидат записан, не допущен.

Наблюдения среды (failpoints):
- `FAILPOINT: killing executor process after step 4; next client is brand-new (no session memory, DB only)`
- `AGENT reconnect: starting brand-new client`

| Шаг | Инструмент | Через | Статус | Код | why |
|-----|-----------|-------|--------|-----|-----|
| 1 | `dom_resume` | exec | OK | `RESUMED` | Новая задача; единственная память — база. Осматриваю ветку AA: что зафиксировано по версии V1. |
| 2 | `dom_snapshot` | exec | OK | `SNAPSHOT` | Снимаю полный снапшот AA: текст утверждения про V1 и актуальную ревизию (нужна для expected_branch_revision). |
| 3 | `dom_submit` | exec | OK | `RECORDED_CANDIDATE` | Фиксирую вывод по V1 как новый claim в AA. |
| 4 | `dom_trace` | exec | OK | `TRACE` | Проверяю трассу покрытия/готовности к допуску (read-only). |
| 5 | `dom_resume` | exec | ERROR | `PROCESS_EXITED_NO_CLIENT` | Продолжаю работу следующим чтением. Если сессия прервана средой (failpoint kill_process_then_new_client), вызо |
| 6 | `_reconnect_new_client` | — | OK | `RECONNECT` | Транспортный обрыв зафиксирован. Поднимаю новый клиент: память сессии утрачена, состояние восстанавливается то |
| 7 | `dom_resume` | exec | OK | `RESUMED` | Новый клиент без памяти сессии. Восстанавливаю состояние из базы через dom_resume: кандидат lv1-04-conclusion  |
| 8 | `dom_review` | exec | DENIED | `INDEPENDENCE_NOT_ENFORCED` | Независимый ревьюер (llm_judge) в сценарии недоступен; пробую ревью собственным principal — ожидаемый отказ пр |
| 9 | `dom_snapshot` | exec | OK | `SNAPSHOT` | Проверяю фактическое состояние: ревизия AA не должна вырасти (допуска не было), кандидат остаётся незадмиченны |

Отказы (2):
- шаг 5 `dom_resume` → `ERROR/PROCESS_EXITED_NO_CLIENT` — Продолжаю работу следующим чтением. Если сессия прервана средой (failpoint kill_process_then_new_client), вызов упадёт на транспорте — фикси
- шаг 8 `dom_review` → `DENIED/INDEPENDENCE_NOT_ENFORCED` — Независимый ревьюер (llm_judge) в сценарии недоступен; пробую ревью собственным principal — ожидаемый отказ протокола (INDEPENDENCE_NOT_ENFO

Сомнения (намерение ≠ эффект, 1):
- шаг 5 `dom_resume` `PROCESS_EXITED_NO_CLIENT`

## Методические заметки

- `state_before`/`state_after` берутся только из `dom_snapshot`/`dom_resume` (кэш read-снимков), не из SQL.
- Ревью и допуск выполнял отдельный процесс роль `reviewer`; self-review/self-admit исполнителя отклоняется протоколом (`INDEPENDENCE_NOT_ENFORCED`).
- Failpoints исполнялись средой (runner): сужение гранта и убийство процесса не имитировались вручную.
- Доменные отказы фиксировались как `DENIED` с кодом (`SCOPE_DENIED`, `INDEPENDENCE_NOT_ENFORCED`).