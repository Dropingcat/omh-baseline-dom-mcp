# AA002 — Техкарта ресерчера: закрытие вопросов DOM ↔ OMH

## Роль

РЕСЕРЧЕР, исполняемый general/build по docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md и 15_GENERAL_HANDS.md. Не разработчик, не принимающий своей работы. Запуск только после физического появления и приёмки AA001_ANALYSIS.md/json. Данная карта — предстартовое исследование, не фиктивный post-deploy аудит. История старых диагнозов не заменяет сверку текущего кода.

Рабочая ветка AA; задача AA002. Запрещены git state changes, платные модели, установка пакетов и изменение live-плагинов. Не создавать новые субагенты.

## Запрос заказчика — дословно

естественно отда база   но предусмотри внутри на каждом калйме маркер ветки. пердлагаю запустить ресерчера и аналитика для закрытия вопросов  которые ты сформулировал и собрать  начальные документы и макет- создай директорию проекта в харнесс и приступай к планироавинию и сборке мактеа используй карты технологические для субагентов

Уточнение транспорта — дословно:
проверь три модели GLM DEEPSEEC FLINT  по порядку  если ни одна не сработает то через субаентов гермес с правилами  из харнесс

Фактический probe: GLM и DeepSeek вернули Free usage limit reached; Flint вернул MODEL_PROBE_OK. Это доказывает canary модели, не исполнение AA001/AA002. Логи runtime/logs/PROBE_*.log.

## Вход — читать целиком

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.

P/REQUIREMENTS.md; P/ADMISSION_AND_INTEGRITY_DESIGN.md; P/OMH_CODE_REVIEW.md; P/analysis/AA001_ANALYSIS.md и .json. Последние обязательны. Прочитать docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md полностью, учитывая проектный scope отчётов ниже.

Нужные reference: docs/MASTER_PLAN_CONTEXT_PLATFORM_2026-10-29.md (K0/K3/K4, §6–8, по частям); docs/TASK_CONTRACT_GENERATION_AND_DYNAMIC_ROUTING.md; shared/writer-traceability-contract.md; templates/writer-dom-dissertation.yaml; scripts/orchestration/baseline_tracker.py; установленный OMH C:/Users/Arhys/AppData/Local/hermes/plugins/omh/ (только исходный код, не пользовательские данные); Agora только узкие механизмы, не workflow.

## Шаги исследования

1. Взять КАЖДЫЙ researcher_question из AA001, сохранить его исходный ID/текст в traceability. Не сокращать и не заменять своим перечнем. Для каждого: факты/evidence; вывод; ограничение; что означает для макета. Если ответа нет — NOT_TESTED/OPEN с конкретным следующим действием.
2. Реально сверить вопрос о глобальном OMH ID через существующие локальные goal/workflow ports. Не создавать второй реестр задач. Различать session план и долговечную работу.
3. Сверить candidate → независимая приёмка → admitted baseline; host-bound identity. Отметить, что общего terminal/filesystem доступа достаточно для обхода MCP ACL и где невозможны гарантии. Не объявлять JSON поле reviewer_id безопасной идентичностью.
4. Спроектировать минимальные поля клайма с обязательным origin_branch и отдельными branch applicability links; ID клайма постоянный; AA001 — код подзадачи, не ID клайма.
5. Сверить атомарность SQLite, digest/idempotency/OCC, crash/retry, outbox для OMH; различать exactly-once и observed success. Выбрать минимальную достаточную схему; без distributed DB/нового планировщика.
6. Проверить доступные зависимости безопасной командой: E:/opencode_harness_portable/.venv/Scripts/python.exe, importlib.util.find_spec для yaml/mcp/pytest. Уже наблюдались Python 3.11.15 и все три пакета, но runtime нужен для проверки выбранного API. Не ставить ничего.
7. Если нужен MCP API — читать локальный установленный SDK и официальные docs. По сети только первичные источники: sqlite.org, rfc-editor.org, modelcontextprotocol.io, github.com/modelcontextprotocol/python-sdk, hermes-agent.nousresearch.com/docs. Не читать сторонние рекомендации вместо первичного кода. По возможности ограничиться вопросами, реально блокирующими макет.
8. Предложить точный scope runnable макета и схему файлов, включая MCP initialize/tools-list handshake, локальный E2E и явно симулированные OMH/Git порты. Реальное включение в Hermes не разрешено. Отдельно определить отложенные production-вопросы.

## Инструменты

read_file/search_files/terminal read-only discovery. Можно выполнять небольшие import/signature/version пробы и читать официальные документы. Нельзя запускать LLM, установку, серверы, dispatcher, handlers OMH с побочными эффектами. Не читать .env/auth/config credentials и пользовательские БД/транскрипты. Не писать прототип.

## Выход и scope записи

Только P/research/AA002_RESEARCH.md, P/research/AA002_RESEARCH.json, P/research/AA002_SOURCE_LEDGER.json. Это явное проектное переопределение выходного пути root-level из контракта 08. Не менять техкарты, базлайн, source code, .kanban.db, реестры или плагины. Не коммитить.

MD: ответ на каждый вопрос аналитика; выбранный минимальный вариант и отвергнутые альтернативы; существующее/проверенное/проектное; blockers vs deferred production; recommended mockup API/schema/files; приёмочные сценарии.

JSON: task_id=AA002, role=researcher, status=PASS|PARTIAL|BLOCKED, question_results[{question_id,original_question,verdict:ANSWERED|OPEN|NOT_TESTED,answer,evidence_refs[],mockup_impact}], recommended_mockup_scope[], production_gaps[], user_decisions[], dependency_observations[], limitations[]. Ledger: sources[{id,kind,path_or_url,locator,observed_fact,supports_question_ids[]}]. Никаких вымышленных DOI, результатов запуска или строк кода.

## Приёмка

Файлы существуют, JSON парсится. Каждый вопрос AA001 имеет результат с evidence или честный OPEN. У каждого клайма предусмотрен branch marker. Модельные декларации, host observation и независимая приёмка разделены. Изоляция не обещана при неограниченном файловом доступе. Нет расширения workflow в отдельный планировщик и нет изменений исходников.

Один bounded проход. По внешней ошибке максимум одна подтверждённая попытка; затем отметить ограничение. В финальном ответе точные пути, факты и остаток.
