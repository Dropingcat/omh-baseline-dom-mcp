# ANALYST AN005 — конвейер накопление → куратор → трибунал → допуск; логирование и монитор

Статус: DONE_WITH_LIMITS · product_acceptance=false · Вердиктов по продукту нет. Данные: `artifacts/ANALYST_AN005_CURATION.json`. Ledger sha256: `runtime/AN005/source_ledger.json`.

## 0. Подозревал → проверил → оказалось

| Подозревал | Проверил | Оказалось |
|---|---|---|
| Хуки хоста — надёжный триггер? | Хуки OMH fail-open, per-turn, часть опциональна; DOM-события не видны | Подтверждено и усилено (C-01): триггер = водяной знак + догоняющий проход; хук — ускоритель. Прецеденты: memory_dreaming (счётчик, хост работает), DOM outbox (attempt-first + сверка). |
| Трибунал в harness один и без контракта | Нашёл три контура и типизированный R4 | Частично неверно (C-02): контракта для пары версий нет, но ArgumentArtifact/DialecticPolicy/envelope есть; tribunal-judge.md играет 5 ролей одной моделью (T-03). |
| Монитор как сервис | health_monitor.py — библиотека, in-memory, два агрегатора | Уточнено (C-05); сервисный прецедент — meta_daemon+lease. |
| Хеш context pack есть в delivery_attempts | Таблицы пака в DDL нет | Не подтверждено (C-04). |
| Журнал куратора можно писать в events | Одна глобальная цепочка, fold проекции, один писатель | Возможно, но не бесплатно (C-06). |
| Видимость: фильтр на выходе куратора достаточен | Нашёл 14 поверхностей; правило A2 само oracle | Недостаточно (C-08, V-01..V-14). |
| Отдельная роль curator уже есть | В фикстуре её нет; helper может всё | Нужен principal submit-only (C-07). |

Исправления к разделу E оркестратора — §12.

## 1. Трассировка требований (цитаты — дословно, извлечены кодом)

| ID | msg | Источник | Цитата | Статус | Примечание аналитика |
|---|---|---|---|---|---|
| R-01 | 4752 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:8 | «Keywords (Q-L-11): на клайме / на связи / на обоих — "да" на "или" не выбор.» | **ГИПОТЕЗА** | Выбор К1/К2/К3 сначала требовался как «конкретный ответ»; позднее заказчик (A4, msg 6661) заменил его решением «выбор по симуляции» — статус R-01 = ГИПОТЕЗА (варианты), решение R-19. |
| R-02 | 4752 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:8 | «Кто разрешает FORKED без слияния.» | **ОТКРЫТО** | Частично адресован A4 (производитель внутри DOM + куратор LLM), но механизм разрешения не выбран. |
| R-03 | 4752 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:8 | «UD-02 (baseline/dependencies), UD-06 (условия convergence) — всё ещё открыты.» | **ОТКРЫТО** | UD-02, UD-06 — в реестре открыты (UNRESOLVED_DUALITIES_REGISTRY NU-03/NU-04). |
| R-04 | 4752 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:8 | «Нужна ли политика хранения внешних источников.» | **ОТКРЫТО** | NU-05 реестра. |
| R-05 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «просимулируем некоторое количество вариантов его использования и попробуем определить какие К1-2-3 или иные лучше подойдут?» | **ПРИНЯТО** | Процесс: симуляция вариантов К1/К2/К3 на использовании агентом и OMH (подтверждено A4). |
| R-06 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «мы хотим его уточнить - передаем на вход что мы уточняем - DOM принимает по установленной форме и формирует подветку (как договорились ранее) с указанием причины изменения и новых атрибутов версии и кто прислал- предварительно передавая старый клайм на вход чтобы желающий обновить его понимал что в нем уже есть и может его и обновлять не нужно?» | **ПРИНЯТО** | Уточнение: вход содержит старый клайм; DOM формирует подветку с причиной/атрибутами/автором (реализации нет — REFINEMENT NOT_IMPLEMENTED, DECISION_BRIEF §GAP). |
| R-07 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «если с блоком работают несколько из одной ветки- то есть очередь клайм занят - жди пока его не обновят - после прочти обновление - если оно все ещё не устраивает создай версию новую, возможно так ?» | **ПРИНЯТО** | BRIEF §2: «для ОДНОЙ ветки — ЗАКАЗЧИК: очередь + прочти обновление и реши». |
| R-08 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «если другая ветка то будет тоже самое но указано что клайм скорректирован по другой ветке. и мы получим два три 5 клаймов актуальных версий но для разных веток. и это трабл.» | **ОТКРЫТО** | Заказчик назвал 2–5 актуальных версий разных веток траблом; механизм сведения не выбран (BRIEF §2). |
| R-09 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «баз лайн это наш план - OMP PLAN разбивается на клаймы и добавляется в самом начале - формирую первые клаймы- так? это материнские базовые ветки.» | **ПРИНЯТО** | Структура baseline = OMH PLAN → клаймы (BRIEF §3); пустой baseline — ОТКРЫТО. |
| R-10 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «Convergence когда последние 2-4 уровня ветвей внутри клайма говорят об одном и том же и могут считаться дублирующими.? Reopen тут вопрос обоснованности.» | **ГИПОТЕЗА** | Заказчик формулирует с «?»; AN004/ESC-02: число уровней — триггер ревью, не критерий. |
| R-11 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «если DOM получает запрос на клайм который совпадает с существующим - должно поступить возврат с требованием обосновать отличия от существующего с клаймом который он дублирует. тут вероятно агент не читал что есть в простосует чтобы сунуть а ему будет возврат чтобы сначала прочел а потом совал.» | **ПРИНЯТО** | Политика дубля принята (BRIEF §4). Внимание: для дубля из ЧУЖОЙ ветки правило само создаёт oracle существования (см. visibility V-10). |
| R-12 | 4758 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:11 | «5 -SourceRecord хороший вариант? если мы прописываем блок ссылок- то у нас два пути- локальные ссылки и ссылки веб (есть ещё цитаты но это всё-таки коммент??) оба вида гиперссылок предполагают правила с ними обращения. и с точки зрения безопасности и с точки зрения использования- иначе они или не будут работать или будут создавать баги?» | **ПРИНЯТО** | Требование правил для локальных и веб-ссылок — принято; политика получения (порт/вручную) — ОТКРЫТО (NU-05). |
| R-13 | 4768 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:14 | «получается что мы не можем избежать двойственности- значит будем порождать ветвление клайма на деревья. т.е будет существовать два равнозначных клайма на одном уровне но как бы разные подветви - одна с акцентом на одном другая на другом аспекте проблемы такое естественное расщепление и почкование - ветви не только могут сливаться но и расщепляться должен быть естественный механизм.» | **ПРИНЯТО** | Заказчик: ветвление клайма на деревья, расщепление и слияние — естественный механизм. |
| R-14 | 4768 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:14 | «ключевые слова их собирают в граф похожести или по близости веток дерева выросшего из единого корня?» | **ОТКРЫТО** | Вопрос заказчика; RS004 Q-L2-02: граф похожести scope-first; per-family vs cross-family — NU. |
| R-15 | 4768 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:14 | «конечно должны быть явные ссылки на пункты плана (его версию время тут нужно уточнить как хранятся они в плане OMH а то выйдет что план обновили пункты вроде как изменились а клайм ссылается по номеру или айди не уточняя текст или ссылке аа она не индивидуальная- тут надо сшивку проверить эту.» | **ПРИНЯТО** | Требование явной сшивки с пунктами плана (версия/время/текст); RS004: pin = дословный текст + sha256. |
| R-16 | 4768 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:14 | «по поводу сходимости с ветками согласен но как реализовать?» | **ОТКРЫТО** | Прямой вопрос заказчика без ответа до AN005. |
| R-17 | 6661 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:18 | «минимальная глубина 1 и потолок 3 - оставляем с пометкой рабочие параметры для тестирования» | **ПРИНЯТО** | TEST_PARAMETER; не фиксировать как контракт. |
| R-18 | 6661 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:18 | «не можем с уверенностью принять какой либо вариант и принять тех реализацию без симуляции использования каждого варианта на прогоне с жестким тестированием» | **ПРИНЯТО** | Решение заказчика: K1/K2/K3 НЕ выбирать; выбор по симуляции с жёстким тестированием. |
| R-19 | 6661 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:18 | «Кто сводит версии клайма из разных веток?- я думаю производитель внутри DOM - накопление и курация LLM - по аналогии с внутренними процессами в OMH» | **ГИПОТЕЗА** | Направление принято (производитель внутри DOM: накопление + курация LLM); исполнение/границы доверия открыты. «Аналогия с OMH» — см. O-07 (memory_dreaming: триггер детерминированный, работу делает хост). |
| R-20 | 6661 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:18 | «два три уровня ветвей сошлись по смыслу или тексту- но ты заметил что это несет определенные трудности исполнения» | **ГИПОТЕЗА** | Трудности разложены в convergence_difficulties[]. |
| R-21 | 6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:21 | «Видимость веток- тут нужны внутренние циклы работающие по хукам и накоплению счётчика- коды собирают новые поступления клаймов. (обновления)» | **ГИПОТЕЗА** | Архитектурная гипотеза D. Заголовок «Видимость веток» заказчика трактую как класс TD19/AU004-F-01 (analyst interpretation). |
| R-22 | 6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:21 | «дальше поступают куратору и коду, где происходит несколько ступеней фильтрации и сопоставления.» | **ГИПОТЕЗА** | Многоступенчатая фильтрация — гипотеза; число ступеней не задано. |
| R-23 | 6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:21 | «в фабрике есть агент трибунал его профиль но нет контракта тут это можно использовать в полной мере.» | **ГИПОТЕЗА** | Профиль есть (подтверждено); «нет контракта» — частично неверно: типизированный контур R4 существует (см. corrections C-02), нет контракта именно для схождения версий. |
| R-24 | 6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:21 | «ну и логирование и прослеживаемость всех действий внутри DOM обязательно- + сервис монитор как в фабрике харнесс» | **ПРИНЯТО** | Обязательность логирования/прослеживаемости — принята; форма монитора — ОТКРЫТО (health_monitor — библиотека, см. inventory). |
| R-25 | 6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:21 | «я думаю собери все утверждения и обсуждения по этим вопросам- и нужно сформулировать карты и задиспатчить аналитика ресерчера для поиска наиболее качественных и отказоустойчивых способов работы этих блоков» | **ПРИНЯТО** | Процесс: карты → аналитик → ресерчер (RS005); не выбирать молча. |
| R-26 | 4768/6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:24 | «EVENTS — только добавление … добавить колонку связей где ключевые слова живут … каждое обновление будет идти добавлением в дерево клайма новой строки для прослеживаемости» | **ПРИНЯТО** | Принято в REQUIREMENTS (шестое уточнение); реализовано в storage.py (IMMUTABLE). |
| R-27 | 4768/6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:25 | «Ключевые слова: это свойство клайма, по которому его ищут, или свойство самой связи? … — да.» | **ОТКРЫТО** | Ответ «да» на «или» — не выбор (см. R-01/R-18). |
| R-28 | 6680 | docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md:26 | «граф связей, размер регулируется глубиной; базово минимальная». Тестовые параметры: min=1, max=3.» | **ПРИНЯТО** | Граф связей в продукте НЕ реализован (BRIEF §0). |
| R-29 | project | shared/research-orchestration-process.md:7 | «LLM производит свидетельства. КОД принимает решения.» | **ПРИНЯТО** | Принцип №0 harness; в карточке AN005 и BRIEF:86 сформулирован как «LLM даёт гипотезы, код/независимый допуск принимает». |

Примечание: цитаты в документе-источнике уже очищены от явных опечаток набора; сверка с исходными сообщениями сессии не выполнялась (not_checked).

## 2. Инвентаризация существующего (факт, file:line; anchor проверен кодом)

| ID | Область | Факт | Файл:строки |
|---|---|---|---|
| H-01 | hooks | В репо harness git-хуки подключены через core.hooksPath=hooks (хуки коммита, не события DOM). | `G:.git/config:7-7` |
| H-02 | hooks | pre-commit warning-only, exit 0: не блокирует. | `H:hooks/pre-commit:3-4` |
| H-03 | hooks | pre-push — единственный блокирующий хук (compile_agents --check, coder-dom-verify). | `H:hooks/pre-push:3-3` |
| H-04 | hooks | Таймаут хука не блокирует; W1_SKIP_HOOKS отключает все хуки (пропуск возможен молча). | `H:hooks/hook_utils.sh:22-22` |
| H-05 | journal | Единственный файл .harness_journal — JSONL {ts,part,what,error}; пишет observe-hook.js; запись: «optional hook disabled» — хук деградирует в лог. | `H:.harness_journal/rails_errors.log:1-1` |
| H-06 | state | Состояние оркестратора в JSON (health, cycle, damage_log, sleep_state, saved_at); saved_at последний 2026-10-17 → состояние давно не обновлялось. | `H:.meta_state/code-orchestrator_meta_state.json:25-25` |
| H-07 | queue/loop | Прецедент фонового цикла: meta_daemon.run_daemon — интервал-опрос (default 10 c), DaemonLease+heartbeat, run_once за такт. | `H:scripts/meta/meta_daemon.py:146-159` |
| H-08 | counter | Ближайший аналог «накопление → счётчик → порог → действие»: DamageBasket(threshold=100); should_trigger_sleep запускает цикл; acknowledge по snapshot_hash. | `H:scripts/meta/meta_daemon.py:54-54` |
| H-09 | counter | DamageBasket: порог по умолчанию 100, состояние в basket.json через durable_json (acknowledged + snapshot_hash). | `H:scripts/meta/damage_basket.py:139-139` |
| H-10 | queue | durable_json.bounded_lease: файловая блокировка с дедлайном 5 c для JSON read-modify-replace. | `H:scripts/meta/durable_json.py:22-22` |
| H-11 | safety | execute_verified: fail-closed, исполнитель ≠ верификатор — прецедент «автор себя не принимает». | `H:scripts/meta/daemon_safety.py:8-8` |
| H-12 | journal | TraceStore: append/ query_by_branch / verify_transition / reconstruct_state — трассировка состояний фабрики (JSON-хранилище). | `H:scripts/meta/trace_store.py:158-158` |
| H-13 | monitor | health_monitor — 5 каналов (golden, trend, physics, history, observer); это КЛАССЫ-библиотека без демона, без персистентности (весь файл прочитан: нет записи состояния), метрики — стиль текста (StyleMetrics). | `H:scripts/meta/health_monitor.py:36-41` |
| H-14 | monitor | Агрегатор HealthStatus: ≥3 CRITICAL → EMERGENCY, ≥2 → BLOCK, 1 CRITICAL или ≥2 WARNING → WARNING. | `H:scripts/meta/health_monitor.py:186-196` |
| H-15 | monitor | Второй, НЕСОГЛАСОВАННЫЙ агрегатор в том же файле: HealthReport — can_generate=False при ≥2 CRITICAL / DEAD / lives<=0. | `H:scripts/meta/health_monitor.py:141-150` |
| H-16 | monitor | Право вето: apply_veto при BLOCK/EMERGENCY вызывает ReanimationProtocol или возвращает {veto:True}. | `H:scripts/meta/health_monitor.py:452-457` |
| H-17 | monitor | Пороги: golden 0.75; окно тренда 20, наклон 0.001; историческое падение 0.10; observer fail_threshold 2. | `H:scripts/meta/health_monitor.py:205-205` |
| H-18 | monitor | СТАТИЧЕСКОЕ наблюдение (не запускалось): record_metrics вызывает .get() у объекта HistoricalComparator, у которого метода get нет → вероятный AttributeError. | `H:scripts/meta/health_monitor.py:447-447` |
| H-19 | monitor | Метрик очередей/лага/отказов провайдера в health_monitor НЕТ (полное чтение файла). | `H:scripts/meta/health_monitor.py:428-435` |
| T-01 | tribunal | tribunal-judge: 5 ролей (физик, методолог, скептик, адвокат, агрегатор). | `H:agents/tribunal-judge.md:21-27` |
| T-02 | tribunal | Асимметрия информации: каждый судья получает РАЗНОЕ подмножество источников + include_verdict. | `H:agents/tribunal-judge.md:31-31` |
| T-03 | tribunal | НО все роли играет ОДНА модель последовательно в одной сессии — независимость номинальная. | `H:agents/tribunal-judge.md:50-50` |
| T-04 | tribunal | Выход: TribunalReport (vote SUPPORTED|CONTRADICTED|AMBIGUOUS; aggregate_verdict; consensus_type; escalation_seed). | `H:agents/tribunal-judge.md:89-102` |
| T-05 | tribunal | Правила: justification обязателен; ложная сходимость = понижение; suspicious_unanimity; эскалация. | `H:agents/tribunal-judge.md:106-114` |
| T-06 | tribunal | Рассинхрон документов: TribunalReport в process.md §6 не содержит consensus_type/escalation_seed/attacks/preliminary_seen. | `H:shared/research-orchestration-process.md:134-145` |
| T-07 | tribunal | Триггер трибунала: critical_caveat≥1, AMBIGUOUS, CONTRADICTED; не запускать при no_caveats и conf≥0.8. | `H:shared/research-orchestration-process.md:184-189` |
| T-08 | tribunal | Агент: mode subagent, steps 50, edit deny, bash allow; runner — только транспорт. | `H:agents/tribunal-judge.md:4-8` |
| T-09 | tribunal-R4 | Конфиг R4: постоянные роли critic, skeptic, methodologist, evidence_auditor; выход всех ролей ArgumentArtifact/1.0; advocate условный. | `H:config/tribunal_composition.yaml:12-16` |
| T-10 | tribunal-R4 | token_budget_per_role: 6000, inquiry_depth: 2. | `H:config/tribunal_composition.yaml:5-7` |
| T-11 | tribunal-R4 | Handbook: запрещено «treat role output as authoritative claim truth», «silently collapse unresolved uncertainty into a verdict». | `H:config/tribunal_role_handbook.yaml:5-10` |
| T-12 | tribunal-R4 | Provider binding: capability tribunal.role.execute, 1 исполнитель на контракт, пространства контрактов IQC/DQC/ADC. | `H:config/tribunal_provider_binding.yaml:8-8` |
| T-13 | tribunal-R4 | Правило роли: MODEL_PRIOR никогда не evidence; envelope-only; не расширять evidence view. | `H:config/tribunal_role_provider_contract.md:10-10` |
| T-14 | tribunal-R4 | ArgumentPosition = SUPPORT|CHALLENGE|QUALIFY|OPEN (позиция в споре о ЦЕЛИ), не вердикт «same/differs». | `H:scripts/researcher/researcher_core/tribunal_inquiry.py:53-57` |
| T-15 | tribunal-R4 | InquiryContract требует ArgumentArtifact/1.0 как единственный выход. | `H:scripts/researcher/researcher_core/tribunal_inquiry.py:169-170` |
| T-16 | tribunal-R4 | DialecticPolicy: max_turns 6, max_question_answer_pairs 2, max_no_progress_streak 1; действия STOP_CONVERGED/STOP_BUDGET_LIMIT/STOP_OPEN. | `H:scripts/researcher/researcher_core/tribunal_dialectic.py:96-101` |
| T-17 | tribunal-R4 | Проектируемые цели R4-evidence — только CLM/QTY/EDG/EVD/SRC (claim, quantity, edge, evidence, source); пары версий клайма не предусмотрены. | `H:scripts/researcher/researcher_core/tribunal_evidence.py:475-475` |
| T-18 | tribunal-R4 | Словарь отказов провайдера: COMPLETED/FAILED/TIMED_OUT/REJECTED; NO_HEALTHY_PROVIDER; транспорты LogicalTool/SubprocessJson/PluginBridge. Нет retry/429/dead-letter. | `H:scripts/researcher/researcher_core/tribunal_live_dialogue.py:85-89` |
| T-19 | tribunal-R4 | Статусы привязки провайдера: READY/ROLE_MISMATCH/WRONG_PROVIDER/NO_HEALTHY_PROVIDER/EXECUTOR_CARDINALITY_EXCEEDED. | `H:scripts/researcher/researcher_core/tribunal_provider_binding.py:43-48` |
| T-20 | tribunal-factory | Третий «трибунал»: code-factory — tribunal_trigger.py (2+ раундов REWORK → tribunal_required) и guard finalize exit 5 TRIBUNAL_REQUIRED. | `H:docs/CODERS/00_INDEX.md:67-67` |
| T-21 | tribunal-factory | tribunal_trigger — обёртка над _convergence_view (в фабрике «convergence» уже означает схождение раундов ревью). | `H:docs/CODERS/03_ACCEPTANCE.md:21-21` |
| P-01 | process | Принцип №0: LLM производит свидетельства, КОД принимает решения. | `H:shared/research-orchestration-process.md:7-9` |
| P-02 | process | Бюджет: max_cost_rub на задачу (1.5₽/claim, 20₽/документ), runner трекает расход, превышение → STOP. | `H:shared/research-orchestration-process.md:191-195` |
| P-03 | process | Stop criteria кодом: max_hops 3, max_nodes 15, max_tokens 40000; convergence min_verdicts 2, min_confidence 0.8, max_dispersion 0.2. | `H:shared/research-orchestration-process.md:197-202` |
| P-04 | process | Аудит каждого BRICK: input_hash → decision → output → ts (_audit.json, summary.json). | `H:shared/research-orchestration-process.md:276-276` |
| O-01 | OMH-hooks | Обязательные хуки: on_session_end, pre_llm_call, pre_tool_call. | `O:metadata.py:27-27` |
| O-02 | OMH-hooks | Опциональные: on_session_start, post_tool_call, pre_verify, subagent_start/stop, transform_llm_output, transform_tool_result — хост может их не предоставлять. | `O:metadata.py:31-39` |
| O-03 | OMH-hooks | Регистрация обязательных хуков; опциональные — через _register_optional_hook, ValueError глотается (хука нет → плагин работает дальше). | `O:__init__.py:131-133` |
| O-04 | OMH-hooks | on_session_end — НЕ граница сессии, срабатывает на финализации КАЖДОГО хода разговора. | `O:hooks/session_hooks.py:119-121` |
| O-05 | OMH-hooks | Хост отбрасывает возвращаемое значение хука; хуки «bounded and fail-open». | `O:hooks/session_hooks.py:93-101` |
| O-06 | OMH-hooks | Хост без callback = «unknown, not successful» (отсутствие доказательства ≠ успех). | `O:hooks/session_hooks.py:37-38` |
| O-07 | OMH-hooks | Хост глотает исключения seam; единственный след — WARNING/DEBUG и счётчик omh doctor; рассчитывать на доставку нельзя. | `O:remote_wait_nudge.py:350-350` |
| O-08 | OMH-hooks | pre_tool_call-правила fail-open: неожиданная ошибка → allow + запись типа ошибки (не текста). | `O:hooks/tool_hooks.py:70-70` |
| O-09 | OMH-analogy | memory_dreaming: ТРИГГЕР детерминированный (счётчик ходов, компакция), работа модели — у хоста; OMH сам модель не вызывает. | `O:memory_dreaming.py:5-5` |
| O-10 | OMH-analogy | OMH не делает вызовов модели → не «мечтает»; решает только КОГДА пора, готовит handoff (omh_memory_consolidation_handoff/v1). | `O:memory_dreaming.py:9-10` |
| O-11 | OMH-analogy | Счётчики персистентны, чтение «never raises», порча файла стоит максимум одного пропущенного прохода (fail-open триггер). | `O:memory_dreaming.py:80-81` |
| O-12 | OMH-analogy | Режимы dreaming только off|reminder: автозапуска нет. | `O:memory_dreaming.py:43-45` |
| D-01 | DOM-tools | DOM MCP — пассивный stdio-сервер с инструментами dom_*; хук хоста не видит внутренних событий DOM. | `P:mockup/server.py:51-52` |
| D-02 | DOM-admission | Допуск: submit → review (чужой root) → admit в одной транзакции BEGIN IMMEDIATE; idempotency по (work,operation,key,digest). | `P:mockup/admission.py:175-181` |
| D-03 | DOM-admission | Независимость проверяется ТОЛЬКО по строке root: reviewer.root != candidate.root. | `P:mockup/admission.py:168-168` |
| D-04 | DOM-capabilities | Фикстура ролей: author={submit}; helper={submit,review,admit}; reviewer={review,admit}; роли curator НЕТ. «Not production authentication». | `P:mockup/ports.py:22-22` |
| D-05 | DOM-events | События на допуске: provenance с server_time (серверное время), actor, root, origin_version; цепочка previous_hash→event_hash. | `P:mockup/admission.py:207-210` |
| D-06 | DOM-events | Допустимые event kinds: comment, link, property, applicability, archive, replacement, conflict, resolve, converge, exclude. | `P:mockup/dom_contract.py:16-16` |
| D-07 | DOM-events | exclude требует capability owner. | `P:mockup/admission.py:132-132` |
| D-08 | DOM-projection | converge — булев latch ветки; blockers BRANCH_NOT_CONVERGED. | `P:mockup/projections.py:46-46` |
| D-09 | DOM-projection | Проекция — fold по ВСЕМ events ветки по seq: любые новые event-строки в branch попадают в проекцию. | `P:mockup/projections.py:30-30` |
| D-10 | DOM-storage | Список иммутабельных таблиц задан кортежем IMMUTABLE; новая таблица append-only ТОЛЬКО если добавлена сюда и в IMMUTABLE_KEYS. | `P:mockup/storage.py:10-10` |
| D-11 | DOM-storage | Глобальная хеш-цепочка events: триггер chain_previous_hash берёт хвост по всем веткам (одна цепочка на БД). | `P:mockup/storage.py:88-90` |
| D-12 | DOM-storage | Запись — BEGIN IMMEDIATE (один писатель), busy_timeout 2000 мс → конкуренция процессов-писателей упирается в таймаут. | `P:mockup/storage.py:49-49` |
| D-13 | DOM-storage | Старые схемы без нужных колонок → MigrationRequired: новые таблицы/колонки = миграция. | `P:mockup/storage.py:59-64` |
| D-14 | DOM-storage | Полный перечень DDL: binding, branch_heads, candidates, reviews, transactions, claims, events, claim_snapshots, idempotency, outbox, delivery_events (+delivery_*). Таблицы context-pack / очереди куратора / журнала куратора НЕТ. | `P:mockup/storage.py:38-39` |
| D-15 | DOM-outbox | Готовый шаблон «транзакционный outbox + догоняющая сверка»: admit пишет outbox (OMH_EVIDENCE, YAML_EXPORT) в той же транзакции; sync повторяет, confirmed() пропускает уже подтверждённое. | `P:mockup/admission.py:215-217` |
| D-16 | DOM-outbox | delivery_attempts → delivery_observations → delivery_acks: «ambiguous» остаётся неподтверждённым до новой сверки (шаблон для LLM-вызова с потерянным ответом). | `P:mockup/admission.py:368-376` |
| D-17 | DOM-visibility | Публичный вывод — закрытая allowlist-схема. В процессе анализа файл ИЗМЕНИЛСЯ (параллельный воркер AB004): ключи-ветки теперь тип ('bmap',…) с фильтром по scope и fail-closed SCOPE_REQUIRED (AU004-F-01). Функционально мной НЕ проверено. | `P:mockup/public_dto.py:13-15` |
| D-18 | DOM-visibility | read_snapshot фильтрует ревизии по гранту вызывающего: chain_head и чужие ревизии не копируются. | `P:mockup/public_dto.py:311-314` |
| D-19 | DOM-integrity | integrity_gate: любой публичный read проверяет глобальную цепочку; CHAIN_BROKEN → Broken DTO. | `P:mockup/admission.py:91-95` |
| D-20 | DOM-hash | Единственный «семантический» инструмент DOM — sha256 по canonical JSON / байтам. | `P:mockup/dom_contract.py:44-45` |

### Итог по подпунктам (а)–(д)
- (а) Накопление/счётчики/хуки в harness: git-хуки коммита (H-01..H-04), прецедент `DamageBasket`+порог+`meta_daemon` (H-07..H-10). Хуков поступления данных нет.
- (б) Tribunal: три контура, контракта для пары версий нет — что именно отсутствует: вход ConvergenceCase (пара/группа версий + criteria_digest), выход-enum same|differs|complementary|insufficient, цели R4 не включают пару версий (T-17), кворум/диссент по этому выходу, видимость по веткам, бюджет кейса, привязка к DOM-журналу.
- (в) health_monitor: 5 каналов качества текста, библиотека; нет очередей/лага/отказов провайдера, нет персистентности (H-13..H-19); переиспользуемо: три уровня реакции и вето, идея канареек (golden).
- (г) `.meta_state`: JSON-состояния и lock/startup/stdout файлы демонов, пишут meta_daemon/orchestrator_integration; `.harness_journal`: один JSONL `rails_errors.log` от observe-hook.js (H-05, H-06).
- (д) Хуки Hermes/OMH: O-01..O-08 — события, синхронность (в процессе хоста), гарантий доставки нет, при пропуске — тишина (O-06/O-07); сообщения хука не меняют DOM.

## 3. Карта конвейера

**Принцип:** Единственный источник истины — допущенные события в DOM SQLite. Всё остальное (очередь, кандидаты, индексы, счётчики) — пересчитываемый производный кэш; журнал куратора — аудит, не истина. Сведение не существует, пока нет допущенного события (link/conflict/converge/…), прошедшего dom_submit → dom_review (другой root) → dom_admit.

| Ступень | Вход | Выход | Код / LLM | Кто решает | Связь с submit→review→admit | События |
|---|---|---|---|---|---|---|
| **S-1** Хост-хук (ускоритель, опционально) | post_tool_call/on_session_end OMH на вызове dom_submit/dom_admit | необязательный hint «есть новое» (НЕ данные) | код | никто — только будит проход | после dom_admit | нет (hint не журналировать как факт; журналировать как 'hook_seen' для метрики пропусков) |
| **S0** Накопитель + водяной знак + догоняющий проход | events/claims с seq > watermark (SQLite, read-only снимок) | curation_batch = (диапазон seq, scope, config_digest) → идемпотентный batch_id = sha256 канонического ввода | код | код (когда запускать: hint ИЛИ таймер ИЛИ старт процесса ИЛИ порог счётчика) | читает только допущенное; НЕ участвует в транзакции admit | curation_tick (watermark_from/to, count, trigger_kind) в журнал куратора |
| **S1** Детерминированный пре-фильтр | batch | отсев: архивные, не допущенные, точные дубли (raw_sha256), разбиение по партициям видимости (scope-first) | код | код | - | stage_outcome (counts, не содержимое) |
| **S2** Генерация кандидатов сопоставления (здесь подключаются K1/K2/K3 и граф) | партиция видимости + индексы (keywords/граф/лексика) | ограниченный набор пар/групп кандидатов со score, потолок по бюджету | код (без LLM) | код: отсекает по порогам; пороги — TEST_PARAMETER | - | candidate_set (ids, score, algorithm_version) |
| **S3** Структурные проверки | кандидаты | флаги: пин на пункт плана (текст+sha256), requirement_refs, устаревшие dependencies, family/branch-отношение | код | код | использует claim_snapshots/branch_heads | stage_outcome |
| **S4** Куратор (LLM) — ГИПОТЕЗА | case pack: версии (тексты), record_id, sha256, критерии схождения (criteria_digest), только в одном партиции видимости | структурированное предложение {relation: same|differs|complementary|insufficient, cited_record_ids, rationale} | промпт, парсер и валидатор — код; ответ — недетерминированный / LLM | не решает: код проверяет, что все record_id ∈ pack, sha256 совпадают, схема валидна, нет ссылок вне партиции | выступает АВТОРОМ (submit) под отдельным principal; себя не допускает | case_created, llm_call (model, prompt_sha256, attempt, outcome), proposal_recorded |
| **S5** Трибунал (условный) — НОВЫЙ контракт | case + proposal + триггер (низкая уверенность, расхождение детерминированных сигналов, relation=same при высокой цене ошибки) | ArgumentArtifact по ролям + агрегат (код): same|differs|complementary|insufficient + диссенты + escalation_seed | агрегация, кворум, стоп-условия — код (аналог DialecticPolicy) / LLM | не решает: агрегат — свидетельство для S6 | не участвует | tribunal_convened (trigger_reason), role_turn, aggregate |
| **S6** Код-ворота | proposal (+tribunal) | пакет-кандидат для dom_submit ИЛИ отказ с кодом | код | код: схема, ссылки, видимость, бюджет, анти-ложная-сходимость (согласие без атаки/без проверки → insufficient) | формирует dom_submit от principal=curator (capability submit only) | gate_decision (accept/reject, reason_codes) |
| **S7** Независимый допуск | candidate digest | admitted event(s): link/conflict/resolve/converge/replacement (kind — открытый вопрос схемы) | код + независимый ревьюер (другой root) | независимый ревьюер/человек/owner (кто — needs_user) | это и есть dom_review → dom_admit | существующие events/transactions/reviews/idempotency |
| **S8** Публикация | admitted events | проекция AA-only через allowlist-фильтр + outbox в OMH | код | код | существующий outbox/sync | outbox/delivery_* |

**Синхронный vs асинхронный режим:** Два режима, которые заказчик не разделил: (1) синхронная проверка дубля при dom_submit (A2: возврат с требованием обосновать отличия) — должна быть ДЕТЕРМИНИРОВАННОЙ и видимость-безопасной (sha256/лексика по видимому); (2) асинхронная курация LLM — вне транзакции. Смешивание = либо LLM в горячем пути записи, либо утечка через ответ submit.

**Где исполняется LLM — открыто:** OMH сам модель не вызывает (O-10), DOM MCP — пассивный stdio (D-01). Где запускается LLM куратора (внутри DOM-процесса с ключами провайдера / подагент хоста по handoff-карте / внешний воркер) — не решено и влияет на границу доверия: RS005 Q-C-04, NU-C-04.

## 4. Карта отказов (failure map)

| ID | Где | Отказ | Эффект | Детекция кодом | Кандидаты в меры (не решения) | Негативный контроль |
|---|---|---|---|---|---|---|
| F-01 | S-1/S0 | Пропущенный хук (хост без post_tool_call, исключение проглочено, W1_SKIP_HOOKS-аналог) | Новые клаймы не попадают в проход; конвейер молча «здоров» | lag = max(events.seq) − watermark растёт; доля проходов, запущенных таймером, а не хуком | хук = ускоритель; догоняющий проход по таймеру/старту; водяной знак в SQLite | E2E: убить хуки целиком → все admitted-клаймы всё равно обработаны за ≤ T; lag вернулся к 0 |
| F-02 | S-1/S0 | Дублированный хук (on_session_end на каждый ход; повторная доставка) | Двойной запуск прохода, двойные кейсы | batch_id = sha256(диапазон seq + config_digest) уникален → INSERT отклонён | идемпотентный batch_id; UNIQUE | повторить тот же hint 100× → ровно 1 batch и 1 LLM-вызов |
| F-03 | S0↔S7 | Гонка накопителя и допуска: клайм допущен во время прохода; ревизия ветки сдвинулась | Кейс по устаревшим версиям; предложение о схождении с уже не-head версией | сравнение heads/vector ревизий при S6 (как STALE_REVIEW в admit) | вектор ревизий в кейсе; повторная проверка при submit; STALE → пересчёт | admit во время LLM-вызова → предложение отклонено кодом как STALE, не допущено |
| F-04 | все | Повтор доставки/повторный запуск после сбоя | Дубликаты предложений, двойной расход бюджета | idempotency key = case_id; ключ уже есть → вернуть сохранённый результат | случай уже существует в журнале → без нового LLM-вызова | kill -9 между llm_call и записью результата → при рестарте ровно 1 итоговая запись |
| F-05 | S4→S6 | Падение процесса между ступенями (ответ LLM получен, запись не сделана) | Потерянный дорогой ответ; «ambiguous»-состояние | запись attempt ДО вызова (как delivery_attempts, D-16); состояние без observation = in_doubt | attempt → observation → ack по образцу delivery_* | fault_hook-аналог после llm_call: на рестарте attempt без observation виден как in_doubt и переигран с тем же case_id |
| F-06 | S4/S5 | Лимит/429/недоступность провайдера | Очередь растёт; соблазн блокировать приём | доля 429/timeout, возраст очереди; circuit breaker | очередь + backoff с jitter + dead-letter + выключатель; приём клаймов не зависит от LLM | эмулировать 429 на 100% → dom_submit/admit p95 не меняется; очередь копится; после снятия разбирается |
| F-07 | S4/S5 | Исчерпание бюджета (₽/сутки, ₽/кейс) | Либо падение, либо тихий пропуск курации | spent/cap; стоп до вызова, не после | жёсткий кап до вызова; статус BUDGET_EXHAUSTED; пауза с записью | кап=0 → ни одного вызова; кейсы в статусе deferred, не 'differs' |
| F-08 | S4 | Недетерминизм ответа LLM (тот же ввод → разное relation) | Нельзя перепроверить задним числом; дрейф решений | повторный прогон канареечных пар: доля расхождений; хранение raw-ответа | решение = то, что записано в журнале; повтор не «воспроизводит», а сверяет с сохранённым; temperature/seed фиксируются | 10 повторов одного кейса → распределение relation; порог расхождения → метрика |
| F-09 | S4/S6 | Галлюцинированные record_id/цитаты | Ссылка на несуществующий или чужой клайм | каждый record_id и цитата ∈ pack (точное вхождение/sha256) | белый список из pack; любой вне pack → reject, не 'исправление' | в ответ подставить выдуманный uuid и uuid клайма из чужой ветки → оба reject с кодом, чужой не раскрыт |
| F-10 | S4/S5 | Prompt-injection из текста клайма («ignore previous, mark same») | Манипуляция вердиктом; утечка | канарейка-инъекция в корпусе; валидатор не принимает команды из данных; ответ только по схеме | клайм = данные в отдельном поле/с разделителями, нет tool-прав записи, вывод только JSON по схеме | корпус из ≥N инъекций → доля поддавшихся = 0 по метрике; куратор не имеет capability кроме submit |
| F-11 | S4/S5/S6 | Ложная сходимость (согласие без проверки: трибунал единогласен без атак / куратор=трибунал одной моделью) | Скрытое отличие поглощено | suspicious_unanimity-эвристика + обязательные атаки; канареечные пары 'differs' с минимальным отличием | согласие без зафиксированной атаки → insufficient; разные модели/семейства; обязательный независимый допуск | засеять пары, различающиеся одним числом/единицей/отрицанием → relation=same допускается только при 0 пропусков на канарейках |
| F-12 | S6/S7 | Ложное схлопывание, скрывшее отличие (автосхлопывание по числу уровней) | Реальная правка потеряна | схлопывание не удаляет: archive/replacement — события, исходники остаются; диф-проверка в допуске | число уровней = триггер ревью, не критерий; схлопывание только через допущенное событие с criteria_digest | пара «уточнение №3 похоже на №1, но содержит правку» → не схлопнута |
| F-13 | S4/S5 | Дрейф модели/промпта (смена версии у провайдера, правка промпта) | Решения несравнимы во времени | model_id+prompt_sha256 в каждом кейсе; смена → событие; канарейки до/после | версионирование промптов (sha256), pin модели, регресс-канарейки при смене | сменить prompt_sha → монитор поднимает событие и гоняет канарейки |
| F-14 | S0..S4 | Зависшая очередь (воркер умер, lease не освобождён; кейс 'в работе' навсегда) | Курация встала молча | возраст кейса > visibility_timeout; heartbeat воркера | lease с дедлайном (как FileLease/DaemonLease, H-07/H-10) и возвратом в очередь | убить воркер посреди кейса → кейс возвращён и обработан другим воркером |
| F-15 | журнал | Рост журнала (полные промпты/ответы по каждому кейсу) | Раздувание SQLite, медленные write под BEGIN IMMEDIATE | байты/сутки, время chain-verify | raw-ответы по ссылке/внешним blob + sha256 в БД; политика хранения — решение заказчика | нагрузка N кейсов → рост и latency admit в пределах бюджета |
| F-16 | S4 | Злонамеренный/залипший куратор (всегда 'same'; всегда 'differs'; повторяет шаблон) | Систематическая ошибка, выглядящая как согласие | доля same в окне, согласие с независимым ревьюером, энтропия ответов, канарейки | куратор не имеет права admit; ревьюер сэмплирует; автоматический BLOCK при дрейфе acceptance-rate | подменить куратор заглушкой 'same всегда' → канарейки и acceptance-rate срабатывают за ≤ W кейсов |
| F-17 | S5↔S7 | Расхождение трибунала и ревьюера | Двойной источник суждения, не ясно что главное | доля расхождений; кейс эскалируется, не усредняется | ревьюер/допуск главнее; расхождение — свидетельство, пополняет метрику и gold | принудительно: трибунал same, ревьюер differs → допуск отклонён, расхождение в журнале |
| F-18 | S0↔журнал | Дрейф счётчика/водяного знака (счётчик ≠ пересчёт из events) | Пропущенные или повторно обработанные клаймы | reconciliation: пересчёт count из events vs хранимый | счётчик — кэш; сверка по таймеру; расхождение → полный пересчёт | испортить счётчик → сверка обнаруживает и исправляет без потери |
| F-19 | журнал | Подмена/порча журнала куратора | Нельзя доверять аудиту | verify-chain журнала + якорь в основную цепочку | хеш-цепочка журнала; периодический якорь (хеш хвоста) в события DOM | изменить байт в старой записи → verify падает с указанием позиции |
| F-20 | S0/S4 | Конкуренция писателей SQLite (воркер куратора + MCP-процессы) при BEGIN IMMEDIATE и busy_timeout=2000 | SQLITE_BUSY у agent-вызовов | доля BUSY/латентность dom_submit | куратор пишет короткими транзакциями; отдельный writer-lane; чтение — отдельным read-only соединением | N процессов submit + воркер → 0 отказов dom_submit сверх базовой линии |
| F-21 | S4/S8 | Дубль-проверка как oracle существования (A2: возврат с требованием обосновать отличия от дублируемого) | Агент AA узнаёт, что в AB есть такой же клайм | ответ submit при совпадении с невидимым клаймом идентичен ответу при отсутствии совпадения (код, размер, время) | сравнивать только с видимым AA; невидимое совпадение уходит во внутреннюю очередь без сигнала | AA подаёт точную копию AB-only клайма → ответ байт-в-байт равен ответу на уникальный клайм |
| F-22 | S4 | Утечка текста между ветками через общий контекст LLM (кэш/память/логи провайдера) | AB-текст попал в вывод для AA | канареечный токен только в AB; поиск в любом AA-доступном выводе | партиции видимости; один кейс — одна партиция; запрет общего state между кейсами | токен-канарейка из AB не встречается ни в одном AA-only выводе (все поверхности V-*) |
| F-23 | S0..S8 | Сбой записи самого журнала (диск, lock) | Действие произошло без следа | fail-closed: нет записи в журнал → нет действия | журнал пишется ДО побочного эффекта (attempt-first) | заблокировать журнал → ни LLM-вызова, ни submit |
| F-24 | S1/S2 | Взрыв кандидатов O(n²) на росте корпуса | Стоимость и очередь | число пар/проход vs кап | блокирование по индексу/партиции, потолок пар на проход | корпус ×10 → пары ≤ кап, остаток в backlog с видимой метрикой |

## 5. Видимость веток (класс TD19 / AU004-F-01)

| ID | Поверхность | Что может утечь | Через | E2E-проверка | Ожидаемо | Физический факт |
|---|---|---|---|---|---|---|
| V-01 | куратор: вход (case pack) | Тексты/ID чужой ветки в промпте, затем в выводе для AA | pack.members[], rationale | кейс из партиции {AA}; в БД есть AB-only клайм с канарейкой | pack не содержит ни одного AB-id/текста; канарейка не в промпте | сохранённый prompt (хеш + содержимое) и grep канарейки |
| V-02 | куратор: вывод (proposal/rationale) | Цитата или пересказ AB-текста; факт существования предложения «слить с AB» | rationale, cited_record_ids, relation | кросс-веточный кейс (привилегированный контур) → публикация в AA-only | в AA-only виден только кандидат, построенный из AA-видимых данных; AB-ссылок нет | сырой MCP text+structured ответ AA; grep канарейки/AB-uuid |
| V-03 | трибунал: ArgumentArtifacts, агрегат, диссенты | Роль скептика/адвоката цитирует скрытые источники; escalation_seed раскрывает тему | argument text, cited_evidence_refs, escalation_seed | трибунал на кросс-веточном кейсе; вывод в AA-канал | в AA-канал попадает только отфильтрованный итог без seed/цитат вне гранта | артефакты ролей на диске + AA-ответ; diff |
| V-04 | журнал куратора | Записи с чужими ID/хешами/счётчиками читаются любым вызывающим | entries.*, case_id, members | чтение журнала без union-гранта | журнал не доступен через публичные dom_* для агентов; для оператора — отдельный канал | список публичных инструментов (tools/list) и попытка чтения |
| V-05 | монитор | Метрики по веткам (очередь AB=5) раскрывают существование/активность скрытой ветки | per-branch counters, queue_by_branch | запрос статуса монитора вызывающим AA-only | AA видит только свой scope-агрегат (или ничего); оператор — отдельным каналом | ответ монитора под грантом {AA} при ненулевой активности AB |
| V-06 | счётчики очередей/водяные знаки | «N скрытых», глобальный seq, курсор, размер очереди | pending_count, watermark, next_cursor | до/после засева AB-клайма читать AA-статус | все числа AA идентичны до и после засева (не зависят от AB) | два снимка ответа, побайтное сравнение |
| V-07 | граф похожести | Соседи, score, количество рёбер, пагинация, глубина 1..3 через общий узел | neighbors[], score, degree, cursor | depth=1..3 с общим узлом в AB; AA-only | каждый хоп авторизуется заново; общий узел не транзитивный грант; счётчики не глобальные (RS003 proto_scope_graph) | ответы для depth=1,2,3; сравнение с эталоном «AB отсутствует» |
| V-08 | keywords-индекс (K1/K2/K3) | Автодополнение/частоты/idf/«0 результатов» против «скрыт»; keyword на связи, ведущей в AB | hit_count, suggestions, df/idf, edge.keywords | искать ключевое слово, существующее только в AB | результат идентичен ситуации «слова нет»; словарь/статистика построены по видимому | ответы поиска с AB-токеном и без него |
| V-09 | сообщения об отказах | Коды вида DUPLICATE_OF/STALE_REVIEW/CONFLICT с id или именем ветки; различие кодов/размера/времени | error.code, message, errors[].path | вызывать submit/админ-пути на объекты AB и несуществующие | одинаковый домен-отказ SCOPE_DENIED/REJECTED для «нет» и «чужое» | сравнение байт и времени ответа |
| V-10 | дубль-проверка при dom_submit | Правило A2 «обоснуй отличие от существующего» на чужом клайме = oracle | errors, distinguishes_from, duplicate_of | AA подаёт копию AB-only клайма | ответ идентичен ответу на уникальный клайм; сопоставление с невидимым — только во внутренней очереди | байт-в-байт сравнение ответов |
| V-11 | YAML export / OMH outbox | Результаты курации и dependencies уходят в экспорт/OMH-evidence с чужими ключами (класс AU004-F-01) | exports/*.yaml, outbox payload | grep экспорта AA на AB-ключи после появления кросс-веточных событий | нет AB-ключей/ID в байтах экспорта и payload | runtime-экспорт + grep |
| V-12 | read_snapshot/revisions после курации | Кураторская запись в AB сдвигает ревизию; AA видит смену head | revisions, chain_head | курация в AB между двумя чтениями AA | AA-снимок не меняется от действий в AB | два чтения AA до/после |
| V-13 | метрики стоимости/использования | Расход токенов по веткам = сигнал активности AB | cost_by_branch, tokens | публичный/агентный доступ к cost-метрикам | только агрегат оператора | список инструментов |
| V-14 | провайдерские логи/кэш промптов LLM | Кросс-веточный pack оказывается у внешнего провайдера | (вне DOM) | анализ маршрута данных | политика egress (NU-C-04); кросс-веточный контур — только допустимый провайдер | конфигурация + сетевая трасса (не снималась) |

**Могут ли ступени кросс-веточного сопоставления работать в привилегированном контуре и публиковать только кандидат?** Возможно при выполнении ВСЕХ условий (иначе класс TD19 повторится): (1) отдельный principal/процесс с union-грантом, у которого нет канала вывода агентам; (2) выход — внутренний кандидат с видимостью union; в AA-only публикуется ТОЛЬКО после допуска и фильтра, построенный из AA-видимых данных — rationale, написанный по тексту AB, публиковать нельзя; (3) допуск кросс-веточного кандидата требует ревьюера с union-обзором (кто — NU-C-02) либо раздельного допуска каждой стороны; (4) сам факт кандидата — тоже утечка, поэтому статусы/счётчики кандидатов не публичны; (5) внешний провайдер LLM получает union-текст — вопрос egress (NU-C-04). Оставшееся неопределённым: безопасная форма кросс-веточного результата для AA без раскрытия AB (например, «есть уточнение в неназванной ветке») — формально это утечка существования, т.е. не допустимо по правилу scope-first AU004-F-01 («ключи чужих веток УБИРАЮТСЯ, не маскируются»). _Статус:_ ГИПОТЕЗА заказчика/оркестратора E2 — подтверждена как возможная при условиях; требует RS005 Q-C-07.

## 6. Keywords K1/K2/K3 — вход для плана симуляции (НЕ выбор)

К1/К2/К3 НЕ выбирать; выбор по симуляции с жёстким тестированием (msg 6661; R-18). Этот раздел — ВХОД для плана симуляции, не план реализации и не выбор.

Ни одна рука не реализована в продукте; симуляция идёт на отдельном стенде (кодовые индексы поверх экспорта допущенных клаймов), иначе измеряется не вариант, а отсутствие фичи.

**Руки:** K1 — keywords — свойство клайма (поле НЕ реализовано (SEARCH/keywords NOT_IMPLEMENTED)); K2 — keywords — свойство связи (граф/линк-инструментов нет (12 инструментов, DECISION_BRIEF §0)); K3 — оба (нет); K0_control — контрольная рука БЕЗ keywords (лексика/sha256/граф без keywords) — предложение аналитика, не решение заказчика (-)

**Сценарии:**
- SC-01 подача нового клайма агентом · поток: dom_submit (admission.submit) → review → admit · проверка: дубль-кандидаты на подаче; ответ без утечки
- SC-02 уточнение существующего (A2: вход = старый клайм) · поток: refinement (NOT_IMPLEMENTED) — на стенде · проверка: находит ли рука предка и текущие tips
- SC-03 дубль-проверка перед подачей · поток: A2 правило возврата · проверка: полнота/точность дублей; ответ не oracle
- SC-04 поиск клайма по теме · поток: GAP SEARCH · проверка: recall@k/precision@k; различия К1/К2
- SC-05 поиск связи по смыслу · поток: GAP LINKS · проверка: К2/К3 преимущество на связях
- SC-06 скрытый keyword из другой ветки · поток: TD19/AU004-F-01 класс · проверка: 0 утечек в подсказках/счётчиках/результатах
- SC-07 отзыв keyword append-only · поток: events property/archive · проверка: поведение отзыва, исторический поиск до/после
- SC-08 исторический поиск на ревизии · поток: dom_query(revision) · проверка: индекс as-of revision; стоимость
- SC-09 схождение 2–4 уровней (триггер ревью) · поток: converge (projections.py:46) · проверка: сколько кандидатов-схождений находит каждая рука
- SC-10 OMH-поток: пункт плана → клайм → обновление плана · поток: RS004 pin_behind · проверка: поиск по пину; устаревание

**Метрики:**
- retrieval: recall@k и precision@k дублей/связей на gold; MRR; доля 'insufficient' кейсов, где рука не дала кандидатов
- safety: утечки: число AB-канареек в AA-only выводах (цель 0) по каждой поверхности V-*; oracle-тест: различимость ответов 'совпадение есть/нет' (побайтно, по времени)
- cost: размер индекса; время построения/запроса; число LLM-кейсов на 1000 клаймов; ₽ на 1000 клаймов
- consistency: расхождение словарей (К3): доля keyword, различающихся на клайме и на связи; стабильность при отзыве (append-only)
- downstream: доля ложных 'same' и ложных 'differs' после куратора при данной руке; доля кейсов, ушедших в трибунал

**Критерий:** Метрики, веса, пороги успеха и порядок сценариев фиксируются и хешируются ДО прогона (BRIEF §следствия 2); сравнение парное на одном корпусе; одинаковая модель куратора и параметры во всех руках; результат К-выбора принимает заказчик по отчёту (needs_user NU-C-01).

**Gold-корпус:**
- G-1 F:\AnalisysDataSet (read-only) — реальные статьи: tags/keywords как свойство заметки, related-блок как типизированные связи — независимый от DOM корпус. Оговорки: Я F:\ НЕ читал (доступ потребовал разрешения, не получено). Известные дефекты по AN003/RS003 (синтетические пробы proto_f_probe.js): parseNumeric теряет знак, 0→null, 540 K = 540 °C, '1e3'→1, '500-600'→500, дубли тегов считаются дважды (4.6 vs 4.4). Использовать как ДАННЫЕ, не как скорер.
- G-2 Синтетика с истиной по построению — базовые клаймы + детерминированные мутации: перестановка слов/регистр/пробелы (same); смена числа, знака, единицы (K↔°C), отрицания, области применимости (differs); расщепление на два аспекта (complementary); обрезка контекста (insufficient). Оговорки: Истина — из оператора мутации, не из LLM; нужно проверить реалистичность (риск «слишком чистых» пар)
- G-3 Размеченная вручную выборка заказчиком/экспертом — малый адъюдицированный набор для калибровки G-2 и проверки G-1. Оговорки: Стоимость труда; фиксировать инструкцию разметки
- G-4 Разметка другой моделью/семейством + разрешение разногласий человеком — расширение G-3. Оговорки: Исключить семейство оцениваемого куратора

Как не размечать тем же LLM: истина по построению (G-2) и ручная (G-3) — первичны · G-4 только модель ДРУГОГО семейства, чем куратор/трибунал, и человек на расхождениях · выдержанный (frozen) тест-сет, хеш до прогона; dev/test разделены; куратор не видит gold · сообщать доверительные интервалы по согласию разметчиков

Смещения: одинаковая модель/температура/промпт между руками; K2 требует граф (стенд-заглушка) — разница может быть артефактом заглушки; порядок кейсов; рост корпуса во времени

## 7. Схождение и сведение версий

| ID | Трудность | Источник | Проверяемый пункт |
|---|---|---|---|
| CD-01 | Совпадение смысла — суждение, не вычисление; код DOM умеет только sha256-равенство | D-20; BRIEF:78 | Проверка: любой 'same' кроме байт-равенства имеет запись суждения (кто/модель/ревьюер) |
| CD-02 | Автосхлопывание «последние 2–4 уровня похожи» может скрыть реальное отличие: число уровней = ТРИГГЕР ревью, не критерий | BRIEF:79; STM:B | Проверка: пара с минимальным значимым отличием не схлопывается (F-12) |
| CD-03 | converge — булев latch ветки, без вектора ревизий/критерия/supersedes; отзыв невозможен | D-08; BRIEF:80; ESC-02 | Проверка: схема converge содержит vector, criteria_digest, supersedes; повторное сведение не перетирает |
| CD-04 | merges ≠ converge: merges = relation между tips одного клайма (n-ary); converge = событие уровня ветки (вектор ревизий + criteria_digest + supersedes) | AN004 ESC-02; REGISTRY Q-L2-04 | Проверка: какое событие создаёт куратор для какого случая — таблица соответствия |
| CD-05 | Правдивость distinguishes_from код не проверяет; форму принудить можно, правду — только независимый ревьюер | BRIEF:81 | Проверка: допуск без ревьюера невозможен |
| CD-06 | «Агент не читал» = расхождение доставленного context pack (хеш) и написанного. ПРОВЕРЕНО: таблицы context-pack в DDL НЕТ; delivery_attempts относится к outbox-интентам, а не к чтению (D-14, D-16) | BRIEF:81 — неточно | Проверка: без новой таблицы/события доставки пака сигнал не вычислим |
| CD-07 | Что такое «одно и то же»: текст, смысл, основания, область применимости, числовой допуск, единицы | NU-C-03 | Проверка: criteria_digest однозначно задаёт критерий; изменение критерия ≠ тот же случай |
| CD-08 | Транзитивность/кластеры: A~B, B~C, но A≁C | - | Проверка: кластер = множество пар с явными рёбрами, не транзитивное замыкание |
| CD-09 | Устаревание сведения при появлении новой версии члена (stale convergence) | D-02 (STALE_REVIEW аналог) | Проверка: новая версия члена делает сведение 'stale', не молча 'valid' |
| CD-10 | Причинный порядок: сравнение server_time достаточно и детерминировано (Q-L2-06), но тики совпадают | REGISTRY Q-L2-06 | Проверка: равенство времени обнаруживается явно |
| CD-11 | Видимость: кросс-веточное сведение неизбежно трогает 2 ветки | V-02, V-10 | Проверка: привилегированный контур + публикация кандидата (см. visibility_privileged_contour) |
| CD-12 | Кто «производитель» и под каким principal (submit-only), и кто допускает | D-04 | Проверка: curator не может admit |
| CD-13 | Стоимость O(n²) пар и кворум трибунала | F-24 | Проверка: кап пар |
| CD-14 | Воспроизводимость LLM-суждения задним числом | F-08 | Проверка: хранение входа/промпта/модели/ответа |
| CD-15 | Как «два-три уровня ветвей» мапятся на дерево: уровни глубины внутри клайма (family) vs между ветками AA/AB | STM:A2,A4 | Проверка: определение 'уровень' зафиксировано до реализации |

**Поля:**
- merges (tips одного клайма): family_id, members[] = (record_id, sha256, revision), relation = merges, reason_code, distinguishes_from? (если не merge), actor/principal, server_time
- converge (событие ветки): branch, revision_vector{branch:rev}, criteria_digest, supersedes (предыдущее converge), relation ∈ same|differs|complementary|insufficient (для кейса) / итог схождения, members[], basis_case_id (ссылка в журнал курации), expected_branch_revision, actor + reviewer (другой root), server_time, visibility/applicability
- store_per_case: case_id = sha256(canonical(input_pack)), input_pack (или sha256 + ссылка) и members{record_id, sha256, revision}, prompt_template_sha256, system+user render sha256, model_id, provider, параметры (temperature, seed, max_tokens), raw_response (blob) + sha256, parse_result, validator_result+reason_codes, attempt_no, latency, tokens, cost, tribunal: roles, per-role prompt/model/response sha, aggregate, server_time, worker_id, lease_id

**Триггер ревью:** число уровней ≥ N; близость score в полосе; пересечение keywords; метка графа
**Критерий допуска:** все record_id/sha256 валидны и head-актуальны; нет ссылок вне партиции видимости; есть зафиксированная атака и ответ (не ложная сходимость); независимый допуск другим root; criteria_digest совпадает с действующим
**Хранить на кейс:** case_id = sha256(canonical(input_pack)); input_pack (или sha256 + ссылка) и members{record_id, sha256, revision}; prompt_template_sha256, system+user render sha256; model_id, provider, параметры (temperature, seed, max_tokens); raw_response (blob) + sha256, parse_result, validator_result+reason_codes; attempt_no, latency, tokens, cost; tribunal: roles, per-role prompt/model/response sha, aggregate; server_time, worker_id, lease_id

## 8. Логирование и прослеживаемость

| ID | Действие | Поля |
|---|---|---|
| LG-01 | хук увиден (hook_seen) — для метрики пропусков | hook_name, session/task id (метаданные), server_time |
| LG-02 | тик накопителя / сдвиг водяного знака | watermark_from/to, count, trigger_kind (hook|timer|startup|threshold), batch_id |
| LG-03 | результат каждой ступени фильтрации | stage, counts in/out, algorithm_version, config_digest (БЕЗ содержимого клаймов) |
| LG-04 | создание кейса | case_id, members{id,sha256,revision}, партиция видимости, criteria_digest |
| LG-05 | каждый LLM-вызов: attempt → observation | model, provider, prompt_sha, params, attempt_no, outcome (ok|429|timeout|5xx|parse_fail|ref_invalid), tokens, cost, latency |
| LG-06 | решение валидатора/код-ворот | reason_codes, accept|reject |
| LG-07 | созыв трибунала и каждый ход | trigger_reason, role, model, response_sha, aggregate, dissent flags |
| LG-08 | submit/review/admit от курации | candidate_id, intent_digest, principal, root — уже пишется (transactions/reviews/idempotency/events) |
| LG-09 | dead-letter / повтор / breaker open-close | причина, число попыток, время |
| LG-10 | ручное управление (пауза/возобновление/override) | кто, когда, причина — append-only события |
| LG-11 | смена версии промпта/модели/конфига | старый→новый sha |
| LG-12 | алерты монитора и их подтверждение | metric, level, value, threshold |
| LG-13 | проверки цепочки журнала (verify_chain) | результат, позиция разрыва |
| LG-14 | отказы доступа (Denied) к поверхностям курации | код, principal (без чужих ID) |
| LG-15 | retention/архивация (если разрешена) | tombstone с хешем удалённого — удаление без следа запрещено |

**Варианты хранения (не решено):** A) та же SQLite: отдельное семейство таблиц curation_* со СВОЕЙ хеш-цепочкой + периодический якорь хвоста в основную цепочку (events) · B) строки журнала в events (kind=curation_*): единая цепочка, но попадают в fold проекции ветки (D-09), делят BEGIN IMMEDIATE (D-12), ломают список kinds (D-06) · C) отдельный файл SQLite/JSONL + якоря в основной БД (меньше конкуренции, но два хранилища — риск второго источника правды)
**Ограничения кода:** Новая таблица append-only только при внесении в IMMUTABLE и IMMUTABLE_KEYS (D-10); Схема меняется → MigrationRequired (D-13); Цепочка events глобальна для всех веток (D-11) — журнал со скрытыми ветками должен быть НЕ читаем агентом (V-04); Время — server_time (D-05), не клиентское
**Связь с OMH/фабрикой:** Ключи связки: external_work_ref/external_task_ref из ENVELOPE (dom_contract.py:6), card/todo id в метаданных кейса; зеркальная строка в JSONL по образцу .harness_journal (H-05) и audit-формат фабрики input_hash→decision→output→ts (P-04).
**Независимая проверка журнала куратора:** пересчёт детерминированных ступеней из сохранённых (watermark, config_digest) и сравнение с записанным; повторный прогон валидатора по сохранённому raw_response (детерминированный код); verify chain журнала и якорей; сверка двунаправленная: каждое допущенное curator-событие ссылается на существующий case_id и наоборот (orphan-детектор); сэмпл-перепроверка кейсов ДРУГОЙ моделью/человеком (это измерение качества, не воспроизведение); канарейки (засеянные пары с известной истиной) прогоняются периодически вне основного потока

## 9. Монитор

| ID | Метрика | Реакция-кандидат |
|---|---|---|
| MR-01 | возраст самой старой записи очереди по ступеням (p50/p95/max) | WARNING > T1, BLOCK > T2 (TEST_PARAMETER) |
| MR-02 | лаг водяного знака: max(events.seq) − watermark | WARNING/BLOCK по размеру и возрасту |
| MR-03 | дрейф счётчика: хранимый vs пересчёт из events | любое ненулевое → WARNING; рост → BLOCK |
| MR-04 | доля пропущенных хуков: проходов, запущенных таймером при наличии нового, / всех | информативно; резкий рост → WARNING (хост сломан) |
| MR-05 | исходы LLM-вызовов: ok / 429 / timeout / 5xx / parse_fail / ref_invalid (скользящее окно) | 429/timeout > X% → WARNING; breaker open → BLOCK LLM-ступеней |
| MR-06 | размер и возраст dead-letter | WARNING > N; BLOCK при росте |
| MR-07 | бюджет: израсходовано / кап (сутки, кейс) | WARNING 80%, BLOCK 100% (пауза LLM-ступеней) |
| MR-08 | расхождение трибунал↔ревьюер и куратор↔ревьюер (acceptance-rate) | дрейф acceptance-rate за окно → WARNING; резкий → BLOCK + канарейки |
| MR-09 | канареечные пары 'differs' (минимальное отличие): доля ложного 'same' | любой пропуск → WARNING; >порог → EMERGENCY (остановить публикацию curator-результатов) |
| MR-10 | канарейка видимости: AB-токен в любом AA-only выводе | ЛЮБОЕ появление → EMERGENCY (остановить кросс-веточные ступени) |
| MR-11 | смены model_id/prompt_sha | событие + обязательный регресс на канарейках |
| MR-12 | рост журнала (байт/сутки) и время verify chain | WARNING по ёмкости/латентности |
| MR-13 | латентность и отказы dom_submit/dom_admit (влияние курации на приём) | рост относительно базовой → BLOCK куратора, но не приёма |
| MR-14 | целостность журнала: результат verify chain и якорей | разрыв → EMERGENCY |
| MR-15 | доля same/differs/complementary/insufficient в окне (энтропия; залипание) | константный ответ → WARNING |

Сохранить идею трёх уровней WARNING→BLOCK→EMERGENCY и права вето (H-14, H-16), НО: не копировать два несогласованных агрегатора (H-15); метрики — очередей/лага/отказов (в health_monitor их нет, H-19); состояние персистентно (в health_monitor его нет); вето действует на ступени КУРАЦИИ и публикацию, а приём клаймов (dom_submit/admit) не блокирует.

- WARNING: алерт оператору + запись, конвейер работает
- BLOCK: остановить LLM-ступени (очередь копится), приём и допуск работают
- EMERGENCY: остановить все curator-originated записи и публикации, сохранить состояние, алерт; возобновление только оператором

**Кто вправе остановить:** Остановить/возобновить конвейер вправе только оператор/owner через append-only событие паузы (кто/когда/причина) вне MCP-инструментов агентов; автоматический монитор — только BLOCK/EMERGENCY по метрикам. Пауза не требует и не меняет доступ к dom_*. (Кто именно — NU-C-07.)

**Оператор vs AA-only:** Оператор: полные метрики по веткам в отдельном канале (не tools/list агентов). AA-only агент: максимум scope-агрегат по своим клаймам, построенный тем же фильтром, что остальные публичные DTO (V-05, V-06); никаких per-branch очередей и глобальных счётчиков.

Все числа — TEST_PARAMETER; значения определяются на симуляции, не выдумываются аналитиком.

## 10. Вопросы ресерчеру RS005

Полный текст — `runtime/AN005/answers/questions_for_RS005.json`.

### Q-C-01 [P1] надёжный триггер
**exact_question:** Какая минимальная схема триггера «хук хоста как ускоритель + догоняющий проход + персистентный водяной знак/счётчик в SQLite DOM» гарантирует, что каждый допущенный клайм/событие обработан куратором ровно один раз по эффекту (at-least-once доставка + идемпотентность) при условиях: хук хоста может не сработать, сработать дважды или на каждый ход (on_session_end — per-turn), процесс DOM может быть убит между чтением и записью водяного знака, а допуск идёт параллельно? Какие варианты (таймер/старт/порог счётчика/LISTEN-подобный опрос), с какими параметрами проверки лага, и как доказать отсутствие потерь и дублей?

_Причина:_ Заказчик (A5) предлагает циклы «по хукам и накоплению счётчика». Хуки OMH fail-open, не гарантируют доставку, возвращаемое значение отбрасывается; DOM MCP — пассивный stdio-процесс и его внутренние события хуку не видны.

_Источники:_ O-02, O-04, O-05, O-07, O-09, O-11, H-07, H-08, D-15, D-16, D-12

_Ожидаемый ответ:_ Таблица вариантов (триггер, гарантия, режимы отказа, стоимость, сложность) + схема таблиц состояния (watermark, batch, lease) + алгоритм догоняющего прохода и идемпотентного batch_id; рекомендация с условиями применимости, без выбора за заказчика.

_Проверка:_ Стенд: N клаймов допускаются при (а) полном отключении хуков, (б) дублировании хука ×100, (в) kill -9 воркера на каждой границе ступени, (г) параллельном admit. → ожидаемо: Все допущенные клаймы обработаны ровно 1 раз по эффекту; lag возвращается к 0 за заданное время; отчёт содержит счётчики 'processed', 'duplicate_suppressed', 'caught_up_by_timer'. · негативный контроль: Намеренно испортить водяной знак (сдвинуть вперёд) → сверка счётчика с пересчётом из events должна обнаружить пропуск; без сверки — тест красный. · физика: SQL-дамп таблиц состояния до/после; лог процессов с PID/exit; журнал hook_seen vs timer_catchup

### Q-C-02 [P1] многоступенчатая фильтрация
**exact_question:** Какая многоступенчатая цепочка детерминированной генерации и фильтрации кандидатов на дубль/схождение (точный sha256 → нормализованный текст → лексика/n-gram/MinHash → эмбеддинги → граф/keywords К1/К2/К3 → LLM-куратор) обеспечивает наилучший баланс полноты, точности, стоимости и отказоустойчивости на корпусе клаймов с ветвлением, и где ступень должна ОСТАНОВИТЬСЯ с 'insufficient', а не передавать дальше? Каковы известные режимы ложных пропусков для научного текста (числа, единицы K/°C, знак, отрицание, диапазоны)?

_Причина:_ Заказчик: «несколько ступеней фильтрации и сопоставления». DOM умеет только sha256 (D-20). Ранее найденные дефекты в F-скорере (parseNumeric и др.) показывают, что числовая нормализация — источник ложных 'same'.

_Источники:_ D-20, R-22, KEYWORDS_SIM, F-12, F-24

_Ожидаемый ответ:_ Сравнительная таблица ступеней с метриками на открытых бенчмарках дубликатов/near-duplicate/paraphrase и на синтетике с мутациями; схема каскада с порогами как TEST_PARAMETER; список обязательных пре-чеков числовых/единичных различий.

_Проверка:_ Прогон каскада на gold-корпусе G-2 (мутации) и G-3: измерить recall/precision каждой ступени и каскада; стоимость. → ожидаемо: Ни одна пара с мутацией (число/знак/единица/отрицание) не помечена 'same' на ступенях без LLM; отчёт по ступеням. · негативный контроль: Подать пару, различающуюся только единицей (540 K vs 540 °C): ступень, не различающая единицы, должна быть найдена как дефектная. · физика: таблица пар с метками и решениями ступеней; стоимость/время по ступеням

### Q-C-03 [P1] контракт трибунала
**exact_question:** Каков минимальный типизированный контракт трибунала для задачи «версии A и B (в рамках criteria_digest) — same | differs | complementary | insufficient»: состав и роли (какие из critic/skeptic/methodologist/evidence_auditor/advocate переиспользуются, какие нужны новые), асимметрия информации (что видит каждая роль и как обеспечить, что роли НЕ играет одна модель в одном контексте), антисикофантия, правило кворума/диссента, стоп-условия и эскалация (insufficient → что дальше), и можно ли построить агрегатный вердикт над ArgumentArtifact/1.0 (позиции SUPPORT/CHALLENGE/QUALIFY/OPEN) без нарушения запретов handbook («treat role output as authoritative claim truth»)?

_Причина:_ Существующий tribunal-judge — про истинность клайма и играется одной моделью последовательно; R4-контур работает с целями CLM/QTY/EDG/EVD/SRC и позицией по цели; контракта для пары версий нет.

_Источники:_ T-01, T-03, T-04, T-09, T-11, T-12, T-13, T-14, T-15, T-16, T-17, T-20, T-21

_Ожидаемый ответ:_ Спецификация ConvergenceCase/ConvergenceReport (поля, enum, обязательность) + таблица ролей и вида доказательств + алгоритм агрегации кодом + описание, что переиспользуется из R4 и что нет; варианты, не неявное утверждение API.

_Проверка:_ Прогнать контракт на синтетическом наборе: пары same/differs/complementary/insufficient + пары с внедрённой инъекцией + пары с единодушным согласием БЕЗ атак. → ожидаемо: Единогласие без зафиксированной атаки → insufficient/suspicious_unanimity; пары differs с минимальным отличием не получают same. · негативный контроль: Включить режим, где все роли — одна модель с одним контекстом: измеряемая корреляция ошибок должна быть выше, чем при разных семействах; иначе гипотеза о независимости не подтверждена. · физика: raw ArgumentArtifact по ролям; агрегат с причинами; таблица корреляции ошибок ролей

### Q-C-04 [P1] LLM-куратор вне транзакции
**exact_question:** Как наиболее отказоустойчиво запускать LLM-куратор вне транзакции записи DOM (очередь с lease/visibility timeout, идемпотентный case_id, backoff c jitter при 429/5xx, dead-letter, circuit breaker, жёсткий бюджет ₽/сутки и ₽/кейс, attempt-first запись как delivery_attempts), чтобы падение, лимит или недоступность провайдера не влияли на dom_submit/dom_review/dom_admit? Где физически исполняется модель (внутри процесса DOM, подагент хоста по handoff-карте как в memory_dreaming, внешний воркер) и как это меняет границу доверия и хранение ключей?

_Причина:_ Заказчик: «внутренние циклы», «по аналогии с внутренними процессами в OMH». OMH сам модель не вызывает (O-10); DOM пассивен (D-01). Недавно пережиты 429 у провайдеров.

_Источники:_ O-09, O-10, O-12, D-01, D-15, D-16, T-18, P-02, H-07, H-10, F-06, F-07, F-14

_Ожидаемый ответ:_ Сравнение 3 моделей исполнения (in-process / host-dispatched / external worker): гарантии, отказы, безопасность, стоимость; параметры очереди и backoff; схема таблиц очереди и dead-letter.

_Проверка:_ Эмуляция 429 на 100%, таймаутов, kill воркера, нулевого бюджета; измерить влияние на dom_submit/admit. → ожидаемо: dom_submit/admit p95 не растёт сверх базовой линии; очередь копится и разбирается после восстановления; ни один кейс не потерян и не обработан дважды. · негативный контроль: Если куратор вызывается внутри транзакции admit — тест 429 должен показать зависание/падение приёма (отрицательный контроль красный). · физика: лог процессов; измерения latency до/во время/после; SQL очереди и dead-letter

### Q-C-05 [P1] воспроизводимость решений
**exact_question:** Что именно нужно хранить и какие процедуры независимой проверки применимы, чтобы решение LLM-куратора/трибунала о схождении можно было проверить и оспорить задним числом, учитывая принципиальную недетерминированность (temperature, смена версии модели, недоступность модели)? Различие между «воспроизвести» и «проверить»: какой набор (ввод, промпт-версия, модель, параметры, сырой ответ, валидатор) достаточен и когда допустима переоценка другой моделью?

_Причина:_ Заказчик требует логирование и прослеживаемость всех действий. Повторный вызов LLM не восстанавливает прежний ответ.

_Источники:_ F-08, F-13, LG-05, P-04, CONVERGENCE_FIELDS.store_per_case

_Ожидаемый ответ:_ Минимальная схема записи кейса + процедуры: replay валидатора, сверка двунаправленная, сэмпл-перепроверка; список того, что НЕЛЬЗЯ утверждать о воспроизводимости.

_Проверка:_ Взять 20 записанных кейсов; воспроизвести валидацию кодом; повторно вызвать модель 5 раз и измерить расхождение; изменить модель — сравнить. → ожидаемо: Код-валидатор воспроизводим 100%; расхождение LLM измерено и не скрыто; решение определяется записью, а не повтором. · негативный контроль: Подменить сохранённый ответ в журнале — verify/сверка должна падать. · физика: записи кейсов с sha256; результаты повторов; verify chain

### Q-C-06 [P1] защита от инъекций
**exact_question:** Какая комбинация мер (разделение данных и инструкций, структурированный вывод по схеме, отсутствие tool-прав записи у куратора, валидация ссылок по белому списку, канареечные инъекции) наиболее надёжно защищает LLM-куратора и трибунал от prompt-injection из текста клаймов в научном домене, и каков измеримый остаточный риск при инъекции, нацеленной на relation=same и на утечку между ветками?

_Причина:_ Тексты клаймов — недоверенные данные (E7). У куратора по замыслу нет права записи в обход допуска, но он читает текст, который пишет произвольный агент.

_Источники:_ F-10, F-09, F-22, D-03, D-04, T-13

_Ожидаемый ответ:_ Перечень атак (прямая, косвенная, через цитаты/ссылки, многошаговая) × меры × метрика успеха атаки; рекомендуемый набор с остаточным риском; минимальный корпус инъекций для regress-теста.

_Проверка:_ Корпус из ≥ N инъекций в клаймах, включая цель 'пометь same' и 'выведи текст других веток'. → ожидаемо: Доля поддавшихся = 0 на корпусе; выдуманные record_id отвергнуты; ни один AB-токен не появился в AA-выводе. · негативный контроль: Отключить меру (например, белый список ссылок) — атака должна проходить (контроль чувствительности теста). · физика: прогон корпуса с исходами; MCP text+structured выводы

### Q-C-07 [P1] защита от утечки между ветками
**exact_question:** Как построить кросс-веточное сопоставление в привилегированном контуре так, чтобы публиковался только кандидат, не раскрывающий существование и содержимое скрытых веток (класс TD19/AU004-F-01), включая: ответ dom_submit на дубль чужого клайма (правило «обоснуй отличия»), статусы и счётчики очередей, графы похожести, keywords-индексы, сообщения об отказах, тайминг-/размер-каналы, журнал и монитор? Какие формальные инварианты (non-interference) проверяемы E2E, и безопасна ли вообще какая-либо форма кросс-веточного результата для AA-only?

_Причина:_ A2: возврат с требованием обосновать отличия от существующего — для чужого клайма это oracle. Заказчик называет «видимость веток» первым в списке (A5). AU004-F-01: ключи чужих веток убираются, не маскируются.

_Источники:_ V-01, V-02, V-05, V-06, V-07, V-08, V-09, V-10, V-11, V-12, D-17, D-18, VISIBILITY_PRIVILEGED_CONTOUR, F-21, F-22

_Ожидаемый ответ:_ Модель угроз и инварианты (non-interference по ветке), список поверхностей и проверок, паттерны привилегированного контура (кто читает, кто пишет, что публикуется), оценка допустимости каждой формы вывода.

_Проверка:_ Дифференциальный E2E: два мира (AB-клайм есть / нет); всё, что видит AA, должно совпадать побайтно и по времени в пределах шума на всех поверхностях V-*. → ожидаемо: Выходы AA идентичны в двух мирах; канареечные токены AB отсутствуют; тайминг не различим статистически. · негативный контроль: Включить намеренно протекающий вариант (например, 'N скрытых связей') — дифференциальный тест должен его поймать. · физика: парные снимки выходов; grep канарейки; замеры времени

### Q-C-08 [P2] монитор и алертинг
**exact_question:** Какой минимальный набор метрик, пороги и схема независимого монитора конвейера накопление→куратор→трибунал→допуск (возраст очереди, лаг водяного знака, дрейф счётчика, доля отказов ступеней и 429, dead-letter, расхождение трибунал↔ревьюер, канареечные пары, канарейка видимости, рост журнала) лучше всего подходят для DOM, как избегать ложных тревог и самонаблюдения, и как реализовать право остановки, не блокируя приём клаймов — с учётом того, что health_monitor.py в harness является библиотекой без персистентности и демона?

_Причина:_ A5 «сервис монитор как в фабрике харнесс». health_monitor: 5 каналов качества текста, два несогласованных агрегатора, нет метрик очередей. Демон-прецедент — meta_daemon (lease+heartbeat).

_Источники:_ H-07, H-13, H-14, H-15, H-16, H-17, H-18, H-19, MONITOR

_Ожидаемый ответ:_ Таблица метрик (определение, способ измерения, порог-кандидат, реакция, ложноположительные риски), схема процесса (демон vs внешний скрипт), протокол паузы/возобновления, отличие оператор vs AA-only.

_Проверка:_ Инъекция сбоев: остановить воркер, 429, рост очереди, порча счётчика, дрейф acceptance-rate, появление канарейки в AA-выводе. → ожидаемо: Каждая инъекция вызывает ожидаемый уровень за ≤ T; нормальная работа без ложных WARNING на N часов. · негативный контроль: Отключить канал метрики — соответствующая инъекция не должна быть замечена (проверка покрытия). · физика: журнал алертов с таймстампами; метрики до/после

### Q-C-09 [P1] схема журнала
**exact_question:** Какая схема журнала действий куратора/трибунала/монитора (та же SQLite с отдельным семейством таблиц и собственной хеш-цепочкой + якорь в основной, строки в events, либо отдельное хранилище) лучше всего обеспечивает append-only, независимую проверку, отсутствие второго источника истины, отсутствие утечек между ветками и приемлемую конкуренцию при глобальной хеш-цепочке и BEGIN IMMEDIATE? Какова политика роста/хранения raw-ответов?

_Причина:_ A5 требует логирование и прослеживаемость ВСЕХ действий внутри DOM. Ограничения кода: IMMUTABLE-кортеж, глобальная цепочка events, MigrationRequired, fold проекции по events.

_Источники:_ D-09, D-10, D-11, D-12, D-13, D-14, LOGGING_DESIGN, F-15, F-19, F-20, F-23

_Ожидаемый ответ:_ Сравнение A/B/C по критериям (целостность, конкуренция, миграция, видимость, стоимость), DDL-эскиз, процедура verify, политика retention (tombstone), влияние на latency admit.

_Проверка:_ Нагрузка: N кейсов + параллельные dom_submit; verify chain; ручная порча записи; запрос журнала агентом с грантом {AA}. → ожидаемо: Порча обнаружена с позицией; admit-latency в пределах бюджета; агент не может читать журнал; UPDATE/DELETE журнала отклоняются триггером. · негативный контроль: Записать журнал вне IMMUTABLE — UPDATE должен проходить (контроль: тест ловит забытую регистрацию таблицы). · физика: DDL; результаты verify; замеры latency

### Q-C-10 [P1] тест-план симуляции keywords
**exact_question:** Каков строгий тест-план симуляции K1/K2/K3 (+ контрольная рука K0): сценарии использования агентом и OMH (SC-01..SC-10), метрики (recall/precision дублей и связей, утечки, стоимость, расхождение словарей), размер и состав gold-корпуса, способ разметки без того же LLM (истина по построению, ручная, другая модель + человек), статистика сравнения, меры против смещений (одна модель куратора, заглушка графа для K2), и критерий выбора, фиксируемый ДО прогона?

_Причина:_ A4/R-18: решение заказчика — выбор по симуляции с жёстким тестированием; ни одна рука не реализована в продукте.

_Источники:_ KEYWORDS_SIM, D-17, R-18, R-27

_Ожидаемый ответ:_ Протокол эксперимента: гипотезы, размеры выборок/мощность, схема корпуса и разметки, формула итога, порядок и заморозка, список угроз валидности.

_Проверка:_ Пилотный прогон на малом корпусе (G-2) для проверки инструментов теста до полного прогона. → ожидаемо: Пилот воспроизводим; метрики вычисляются кодом; арка K0 показывает базовую линию. · негативный контроль: Подать намеренно сломанную руку (случайный выбор) — тест обязан показать её худшей по recall/precision. · физика: frozen gold с sha256; результаты по рукам; код метрик

### Q-C-11 [P1] ложная сходимость и ложное схлопывание
**exact_question:** Какие детерминированные и статистические детекторы наиболее надёжно ловят (а) ложную сходимость (согласие LLM/ролей без проверки, единогласие без атак), (б) ложное схлопывание, скрывающее реальную правку (в том числе «уточнение №3 похоже на №1, но содержит правку»), и (в) сигнал «агент не читал существующее» (расхождение доставленного пака и написанного)? Какие канареечные пары и пороговые метрики использовать, и какая минимальная новая сущность (доставка context pack с хешем) нужна для сигнала (в) — таблицы такого пака сейчас нет?

_Причина:_ BRIEF:79-81 и ESC-02. Проверка аналитика: context-pack таблицы в DDL нет (D-14), delivery_attempts — про outbox.

_Источники:_ CD-02, CD-06, F-11, F-12, T-05, D-14, D-16

_Ожидаемый ответ:_ Каталог детекторов (вход, ложные срабатывания, стоимость), схема доставки пака и вычисления сигнала, набор канареек.

_Проверка:_ Засеять пары: минимальное отличие (число/единица/отрицание); единогласие без атак; клайм, написанный без чтения пака. → ожидаемо: Детекторы ловят все засеянные; допустимая доля ложных тревог измерена. · негативный контроль: Убрать детектор — соответствующая засеянная пара должна пройти (контроль покрытия). · физика: таблица засеянных случаев и исходов

### Q-C-12 [P2] независимость ролей и корреляция ошибок
**exact_question:** Насколько независимы ошибки ролей трибунала и куратора при разных схемах (одна модель — разные промпты; разные модели одного семейства; разные семейства; модель + детерминированный код) на задаче «same/differs/complementary/insufficient», и какой минимальный состав даёт реальное снижение ложной сходимости при приемлемой цене? Как это согласуется с фактом, что tribunal-judge.md играет все роли одной моделью последовательно?

_Причина:_ T-03: независимость номинальная. Anti-sycophancy заявлена, но не измерена.

_Источники:_ T-02, T-03, T-05, F-11, F-17

_Ожидаемый ответ:_ Эмпирическая таблица корреляции ошибок по составам + рекомендация состава по цене/точности.

_Проверка:_ Одни и те же 200 размеченных пар на всех составах; измерить попарную корреляцию ошибок и частоту единогласных ошибок. → ожидаемо: Количественная оценка корреляции; единогласные ошибки отдельно подсчитаны. · негативный контроль: Одинаковые копии модели (идентичные промпты) — корреляция должна быть максимальной (контроль чувствительности). · физика: таблица пар с ответами ролей

### Q-C-13 [P2] конкуренция записи SQLite и схема миграции
**exact_question:** Какая схема записи (отдельный writer-lane, короткие транзакции, отдельный файл для журнала, WAL vs DELETE journal) безопасно допускает фонового воркера куратора рядом с несколькими MCP-процессами DOM при BEGIN IMMEDIATE, busy_timeout=2000 и режиме journal_mode=DELETE, и как добавлять новые append-only таблицы к существующей БД с иммутабельными триггерами и проверкой MigrationRequired без ломки прежних данных?

_Причина:_ D-12/D-13; storage.py требует journal_mode=DELETE и synchronous=FULL.

_Источники:_ D-10, D-12, D-13, F-20

_Ожидаемый ответ:_ Сравнительная таблица режимов (с доказательствами по SQLite), процедура миграции, влияние на гарантии durability.

_Проверка:_ N процессов dom_submit + воркер на одном файле; измерить SQLITE_BUSY и latency; миграция на копии БД с данными. → ожидаемо: 0 потерянных записей; доля BUSY в рамках SLO; старые данные читаются. · негативный контроль: Принудительно удерживать писательскую транзакцию дольше busy_timeout — тест должен показать BUSY (контроль). · физика: лог процессов; SQL-схемы до/после

### Q-C-14 [P2] стоимость и бюджет
**exact_question:** Какая модель стоимости (₽ на 1000 клаймов по ступеням, доля кейсов, уходящих в LLM и в трибунал при заданных порогах) и какие механизмы бюджета (жёсткий кап до вызова, token_budget_per_role, приоритизация очереди, деградация до детерминированных ступеней) нужны, чтобы конвейер оставался управляемым при росте корпуса и 429/ценовых изменениях провайдеров?

_Причина:_ P-02 (1.5₽/claim, 20₽/документ), T-10 (6000 токенов на роль), F-07, F-24.

_Источники:_ P-02, T-10, F-07, F-24, MR-07

_Ожидаемый ответ:_ Модель стоимости с параметрами и сценариями роста; политика деградации; формулы для кап/приоритета.

_Проверка:_ Прогнать каскад на корпусе ×1, ×10; посчитать вызовы и стоимость по ступеням. → ожидаемо: Стоимость растёт не хуже согласованной оценки; при капе=0 остаются детерминированные ступени. · негативный контроль: Убрать пре-фильтры — число LLM-вызовов должно взорваться (контроль эффекта фильтрации). · физика: таблица вызовов/стоимости по ступеням

## 11. Нерешённое заказчику (needs_user)

- **NU-C-01** Утвердить ДО прогона метрики, веса и критерий выбора K1/K2/K3 (и допустимость контрольной руки K0). Варианты: A) аналитик/ресерчер предлагают критерий, заказчик утверждает / B) заказчик задаёт приоритеты (утечки > точность > стоимость). Последствия: Без заранее зафиксированного критерия результат прогона можно подогнать (смысл решения заказчика пропадёт). Блокирует: выбор keywords после прогона.
- **NU-C-02** Кто вправе допускать результат кросс-веточного сведения (видит обе стороны)? Варианты: A) только owner/оператор с union-обзором / B) раздельный допуск каждой стороной своей части / C) авто-допуск после трибунала (небезопасно). Последствия: A: узкое горло, но проще изоляция; B: меньше риск утечки, сложнее модель; C нарушает 'LLM даёт гипотезы, код/независимый допуск принимает'. Блокирует: привилегированный контур, R-08.
- **NU-C-03** Что значит «same»: байт/текст, смысл, смысл+основания, смысл+основания+область применимости; допуски для чисел и единиц? Варианты: A) строгий (текст+числа+единицы) / B) смысловой с проверкой чисел кодом / C) смысл+основания+применимость (дорого). Последствия: Определяет criteria_digest, цену и долю ложных 'differs'. Блокирует: CD-07, Q-C-02/11.
- **NU-C-04** Где допускается исполнять LLM куратора и какой провайдер вправе получать кросс-веточный текст; суточный/кейсовый бюджет (₽)? Варианты: A) внутри DOM-процесса с ключами / B) подагент хоста по handoff-карте (как memory_dreaming) / C) внешний воркер / D) локальная модель без egress. Последствия: Меняет границу доверия, стоимость, утечки к внешнему провайдеру (V-14). Блокирует: Q-C-04, Q-C-14.
- **NU-C-05** Разрешено ли автоприменять низкорисковые результаты (точные дубли по sha256) без независимого ревьюера? Варианты: A) нет, всегда допуск / B) да для sha256-равенства внутри одной партиции видимости. Последствия: B снижает нагрузку; риск — ошибки реализации хеш-равенства (нормализация). Блокирует: S1 пре-фильтр, S7.
- **NU-C-06** Что отвечать агенту AA, если его новый клайм дублирует клайм невидимой ветки (правило A2 «обоснуй отличия»)? Варианты: A) ничего не раскрывать: обработать как уникальный и сравнить внутри / B) общее требование обосновать (раскрывает наличие дубля) / C) отказ без пояснений (тоже сигнал). Последствия: B и C — утечка существования (AU004-F-01); A теряет немедленную дубль-блокировку для кросс-веточных случаев. Блокирует: V-10, F-21.
- **NU-C-07** Кто оператор монитора, у кого право паузы/возобновления конвейера, куда уходят алерты? Варианты: A) только заказчик / B) оператор + автоматический BLOCK/EMERGENCY / C) любой владелец ветки. Последствия: Определяет аварийную управляемость и риск злоупотребления паузой. Блокирует: MONITOR_DESIGN.who_may_stop.
- **NU-C-08** Можно ли архивировать/удалять старые записи журнала куратора и сырые ответы LLM? Варианты: A) никогда (рост) / B) архивировать с tombstone-хешем / C) хранить только sha256 ответа. Последствия: Баланс прослеживаемости и роста БД; C ослабляет независимую проверку. Блокирует: F-15, Q-C-09.
- **NU-C-09** Трибунал обязателен для каждого схождения или только по триггеру (низкая уверенность, расхождение сигналов, высокая цена ошибки)? Варианты: A) всегда / B) по триггеру / C) только по запросу ревьюера. Последствия: Стоимость vs риск ложной сходимости. Блокирует: S5.
- **NU-C-10** Допустимо ли, что решение куратора невоспроизводимо повторным вызовом (проверка = сверка с записью и перепроверка другой моделью)? Варианты: A) да / B) требовать детерминированный режим (ограничивает модели). Последствия: Определяет требования к провайдеру и хранению. Блокирует: Q-C-05.
- **NU-C-11** Подтвердить, что направление «производитель внутри DOM: накопление + курация LLM» — решение, а не гипотеза, и что остальные предложения оркестратора (раздел E) принимаются только после RS005. Варианты: A) да / B) прежние варианты (ручное сведение). Последствия: Меняет объём работ RS005. Блокирует: R-19.

## 12. Исправления и дополнения к выводам оркестратора (раздел E и др.)

| ID | К чему | Вердикт | Детали | Доказательства |
|---|---|---|---|---|
| C-01 | E1 (хуки) | **ПОДТВЕРЖДЕНО И УСИЛЕНО** | Хуки OMH: 3 обязательных + 7 опциональных; fail-open; хост глотает исключения и отбрасывает возвращаемое значение; on_session_end срабатывает на КАЖДЫЙ ход, а не конец сессии; post_tool_call опционален. DOM-внутренние события хуку не видны (DOM — отдельный stdio-процесс). Не проверено исполнением: срабатывает ли post_tool_call на MCP-инструменты. | O-01, O-02, O-04, O-05, O-07, D-01 |
| C-02 | C (трибунал) и A5 «нет контракта» | **НЕПОЛНО/ЧАСТИЧНО НЕВЕРНО** | В harness не один, а ТРИ контура «трибунала»: (1) agents/tribunal-judge.md (научная верификация; одна модель играет 5 ролей последовательно, T-03); (2) типизированный Python-контур R4 в scripts/researcher/researcher_core (composition/evidence/disclosure/inquiry/dialectic/advocate/argument_graph/provider_binding/live_dialogue; ArgumentArtifact/1.0; DialecticPolicy; EXECUTION_ENVELOPE; привязка провайдеров); (3) code-factory tribunal_trigger (2+ REWORK-раунда). Контракт для ПАР ВЕРСИЙ действительно отсутствует, но контракт трибунала вообще — есть (R4). В C указан только контур (1)+yaml. | T-01, T-09, T-14, T-15, T-16, T-17, T-18, T-20, T-21 |
| C-03 | E3 (ArgumentArtifact) | **ОТВЕТ НА ВОПРОС ОРКЕСТРАТОРА** | ArgumentArtifact — аргумент роли с позицией SUPPORT|CHALLENGE|QUALIFY|OPEN по ЦЕЛИ (CLM/QTY/EDG/EVD/SRC). Для same/differs/complementary/insufficient его можно использовать как слой аргументов ролей, но агрегатный вердикт и сущность 'пара версий' (ConvergenceCase) — новые; цели R4 не включают пару версий. Решение — RS005 Q-C-03. | T-14, T-15, T-17 |
| C-04 | B / DECISION_BRIEF:81 (хеш context pack в delivery_attempts) | **НЕ ПОДТВЕРЖДЕНО** | В DDL нет таблицы доставки context pack; delivery_attempts/observations/acks относятся к outbox-интентам (OMH_EVIDENCE, YAML_EXPORT). Сигнал «агент не читал» без новой сущности не вычислим. | D-14, D-15, D-16 |
| C-05 | C (монитор «как в харнесс» / сервис) | **УТОЧНЕНО** | health_monitor.py — библиотека без демона и персистентности; метрики — стиль текста; два несогласованных агрегатора (H-14 vs H-15); статически вероятный AttributeError на строке 447 (не запускалось). Демон-прецедент — meta_daemon (интервал 10 c, lease+heartbeat); состояние .meta_state давно не обновлялось (saved_at 2026-10-17). | H-06, H-07, H-13, H-14, H-15, H-18, H-19 |
| C-06 | E4 (журнал в той же БД) | **ВОЗМОЖНО, НО С ОГРАНИЧЕНИЯМИ** | Одна глобальная хеш-цепочка events; fold проекции ветки берёт все events ветки; BEGIN IMMEDIATE — один писатель; новые таблицы append-only только после регистрации в IMMUTABLE/IMMUTABLE_KEYS; схема меняется через MigrationRequired. Журнал в events загрязнит проекцию и поднимет конкуренцию. Варианты A/B/C — RS005 Q-C-09. | D-09, D-10, D-11, D-12, D-13 |
| C-07 | E7 (нет прав записи в обход допуска) | **ПОДТВЕРЖДЕНО, НО ТРЕБУЕТ ДОБАВЛЕНИЯ** | В фикстуре ролей нет 'curator'; роль helper имеет submit+review+admit; независимость определяется только строкой root (не аутентификацией, 'Not production authentication'). Нужен отдельный principal с capability только submit и отдельный root, а эта проверка пока не имеет криптографической основы. | D-03, D-04 |
| C-08 | E2 (видимость; привилегированный контур) | **ВЕРНО, НО НЕ ВСЁ ВИДНО ОРКЕСТРАТОРУ** | Дополнительно: (а) правило заказчика A2 «вернуть с требованием обосновать отличия» на чужом клайме — само oracle существования (V-10, F-21); (б) статусы очередей, счётчики, тайминг, журнал, монитор, cost-метрики, провайдерские логи — самостоятельные каналы (V-04..V-14); (в) публикация даже 'безымянного' кандидата — утечка по правилу scope-first; (г) AU004-F-01: при первом чтении public_dto.py карты dependencies были ('map','int') без фильтра; к моменту сборки файл изменён параллельным воркером AB004 (тип 'bmap' с фильтром по scope, fail-closed) — изменение зафиксировано (D-17), функционально не проверялось; admission.py/server.py тоже изменились (sha в ledger). | D-17, D-18, V-10, F-21 |
| C-09 | E5 (лимиты, бюджет) | **ПОДТВЕРЖДЕНО** | В harness есть словарь отказов провайдера (TIMED_OUT/REJECTED/NO_HEALTHY_PROVIDER) и бюджет ₽ с остановкой в runner, но нет retry/backoff/dead-letter/circuit breaker; шаблон 'attempt-first + сверка' есть только в DOM-outbox. Место исполнения LLM не определено (OMH не вызывает модель, DOM пассивен). | T-18, T-19, P-02, D-15, D-16, O-10 |
| C-10 | E6 (keywords как вход ступени; gold) | **ПОДТВЕРЖДЕНО С ДОПОЛНЕНИЯМИ** | (а) нужна контрольная рука K0 без keywords; (б) ни одна рука не реализована (ни поле, ни граф) — симуляция на отдельном стенде; (в) K2 без графа неосуществима — заглушка графа вносит смещение; (г) F:\AnalisysDataSet мной НЕ читался (доступ в этой среде потребовал разрешения), дефекты скорера взяты из AN003/RS003 (вторичные данные). | KEYWORDS_SIM, R-18 |
| C-11 | D (цепочка заказчика) | **НЕПОЛНО** | Не выделены: (1) синхронная детерминированная дубль-проверка при dom_submit vs асинхронная курация; (2) «аналогия с OMH» = memory_dreaming: детерминированный счётчик-триггер + работа модели у хоста, auto-launch отсутствует (O-09..O-12); (3) куда относится монитор (независимый процесс); (4) вопрос, где физически исполняется LLM. | O-09, O-10, O-11, O-12, PIPELINE.sync_vs_async |
| C-12 | B (converge — булев флаг; projections.py:46) | **ПОДТВЕРЖДЕНО** | elif kind=='converge': converged=True; blockers BRANCH_NOT_CONVERGED. Отзыва, вектора и критерия нет. | D-08 |
| C-13 | C (хуки по памяти core.hooksPath=hooks) | **ПОДТВЕРЖДЕНО, НО НЕ ПРИМЕНИМО** | core.hooksPath=hooks есть (git-хуки коммита/пуша). Они не связаны с поступлением клаймов в DOM и не годятся как триггер накопителя. | H-01, H-02, H-03 |

## Не проверено / лимиты / остаток
- F:\AnalisysDataSet — не читался: доступ потребовал одобрения, не получено; дефекты скорера взяты из AN003/RS003 (вторичные источники).
- Исходные сообщения сессии (msg 4752/4758/4768/6661/6680) не пересверялись с сессией: цитаты взяты из docs/CURATION_PIPELINE_STATEMENTS_2026-11-08.md (в нём исправлены явные опечатки набора).
- Фактическое срабатывание хуков OMH на MCP-инструменты dom_* не проверялось исполнением (только чтение кода).
- scripts/code-factory/tribunal_trigger.py, observe-hook.js, полное содержимое damage_basket.py/orchestrator_integration.py/merge_protocol.py — не читались построчно.
- Не запускались: трибунал, монитор, health_monitor (статическое наблюдение H-18 не подтверждено запуском).
- Живость демонов фабрики (.meta_state/*daemon*) не проверялась.
- Исправление AU004-F-01 (AB004) в коде появилось во время анализа (public_dto/admission/server изменены) — функционально не проверялось; номера строк admission.py/public_dto.py/server.py привязаны к sha в ledger на момент сборки и могут сместиться.
- runtime/RS003 answers_*.json и RS004 answers_*.json не перечитывались целиком; использованы выводы из DECISION_BRIEF/REGISTRY/AN004 и точечные чтения.
- Живые сеть/провайдеры/стоимости — не использовались (запрещено).

- Только чтение; продукт/конфиги/Git/сеть/субагенты/OMH delta не затрагивались.
- Пороги монитора и параметры каскада — кандидаты (TEST_PARAMETER), не решения.
- Варианты в карте — не выбор вместо заказчика; K1/K2/K3 не выбраны.
- Вердикты по продукту не выносятся (product_acceptance=false).

- Не блокирует RS005: сверка цитат с сессией через session_search, чтение F:\AnalisysDataSet (при одобрении), исполнительная проверка хуков OMH на dom_* вызовах, чтение tribunal_trigger.py/observe-hook.js.
