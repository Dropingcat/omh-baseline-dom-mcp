# RS002-A — ресерчер: безопасный вывод и неверная форма внешней цели

## Роль и вопрос

Ресерчер — КАК должно заработать. Следующее звено после completed AN002-A, не воркер/ревьюер/аудитор/принимающий. Исследовать только новую дельту Q-A2-01…05, не повторять RS001 и не чинить продукт. Сохранить REQUEST_CHANGES по TD19 до реализации/независимой приёмки.

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.

## Слова заказчика — дословно

тогда идем дальше - так же циклами фабрики до полной реализации

делай акцентне на тестики а на е2е прогоны  боевые с вариативностью начальных условий и намеренными попытками вызвать отказ

после  цикла обнови план OMH по тестированию сценариями как записи так и чтения обновления  выборочный поиск - поиск по веткам-  на предмет протечек из дроугих веток. создать через планера план тестирования и предварительный поиск местотказа-  где будет утечки где проблемы- и эти места и становятся  чеками для проверки и симуляций. - нужен прогон спеца по зеопасночти и тестированию - нужен шаблон новый для контракта по этому очень жосткий ядреный  работающия не на положительный результат а с ветором на заваливание и негатив

## Норматив и вход

E:/opencode_harness_portable/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md (§2/5/6.2); shared/code-factory-process.md; 09_FINDINGS_ESCAPE_HATCH.md. Пути от harness.

Приоритет: P/REQUIREMENTS.md → P/artifacts/ANALYST_AB002_A.json (questions_for_researcher С ТОЧНЫМ ТЕКСТОМ Q-A2-01…05) и P/reports/ANALYST_AB002_A.md → auditor JSON/MD и relevant evidence → текущий source. Analytic report содержит field paths, причины, проверки и пределы; читать целиком или страницами, не потерять конец. Auditor: artifacts/AUDITOR_AB002_A.json, reports/AUDITOR_AB002_A.md; reviewer: artifacts/REVIEWER_AB002_A.json; tech_debt.md.

Предыдущее: runtime/RS001_HANDOFF.md и RESEARCH.json только для границ контракта и исключения дублей; не перечитывать 658 строк RS001 без точной причины. docs/AB002_PLAN.md, templates/NEGATIVE_E2E_SECURITY_CONTRACT.md, cards/PL003_NEGATIVE_E2E_PLANNER.md и docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md — последующая очередь.

Текущие места: mockup/admission.py integrity_gate/verify_chain/_trace/resume/guarded; mockup/ports.py read_target/attach; server.py serializer/ошибки; delivery.py observation/ack. Актуальные source lines устанавливаются по коду. Внутренние доказательства не являются публичными полями по умолчанию.

## Проверенный вход/остаток

AN002-A COMPLETE_MATERIAL, product_acceptance=false, 5 уникальных точных вопросов, текущие input/source hashes совпали; JSON/MD/validation есть. Это допуск материала, а не признание причин независимой истиной или исправление.

TD-DOM-19 major IN_SCOPE: AA-only читатель видит healthy hidden AB revision и global hash/count через allowed envelopes; broken AB даёт foreign UUID/seq через diagnostic. Глобальный integrity gate необходим, scope запрошенной AA исправен, ошибка — в полной сериализуемой проекции. Корректно маскировать только revisions недостаточно: trace.chain/resume.trace.chain, text+structuredContent и errors тоже выходы.

TD-DOM-20 major OUT_OF_SCOPE A: read_target смешивает absent с malformed TASK:list; attach вызывает .get у list; raw AttributeError без domain status. До попытки side effect не завершён, no ack/READY; не выдавать отсутствие observation как нарушение A2. Нужен отдельный явно ограниченный robustness-срез.

TD-DOM-21 minor: immutable run-specific manifest hash+source lineage, latest pointer только navigation, старые bundles не исчезают. Исследовать минимальную схему refs, не повторять весь D план.

## Требуемый результат по пяти вопросам

Каждый вопрос сохраняет exact_question ИЗ JSON АНАЛИТИКА, не переписывать его. Ответ: механизм (2 варианта при реальной развилке), рекомендуемый минимальный working contract, почему это даёт указанную гарантию, source/evidence ledger с observed/code/proposed/UNVERIFIED, схема/таблица полей или состояний, действие → expected → физический факт, риски и needs_user. Выбор инженерного способа не требует вновь спрашивать, допустима ли утечка; прекращение запрещённой выдачи уже задано. Новые продуктовые полномочия/политики явно отделить.

### Q-A2-01/02 — приоритет P0

Разделить full internal integrity proof/read snapshot/observation binding от публичного actor-scoped ответа. Определить исчерпывающую allowlist для healthy и CHAIN_BROKEN ответов каждого инструмента и вложенных полей. Global hash, global count/seq, запрещённый UUID/revision не безопасны лишь потому, что служебные.

Глобальная проверка и snapshot consistency сохраняются. Restricted получает truthful blocked/NOT_READY без foreign locator; нельзя выдавать CHAIN_OK/READY ради сокрытия. Global health signal может отражать общую блокировку, но не её запрещённую локализацию; не обещать абсолютную indistinguishability healthy/broken. Привилегированная диагностика требует отдельной реальной capability/trust boundary, не названия reviewer/owner. Если её нет — сохранить полный proof во внутреннем/локальном защищённом oracle и отметить GAP, не изобретать работающий admin endpoint. Не сохранять утечку в logs/export/случайно nested dict.

E2E — AA fixed, изменяем AB, положительный AB control; raw public differential до/после включая sync permitted actor/new process. Затем forbidden middle-event invalid UTF8/hash на disposable populated копии: safe refusal/no effects, privileged oracle находит точную поломку отдельно. Привязка internal ack/digest остаётся проверяемой.

### Q-A2-03/04 — P1

Общий shape контракт read/locked attach: absent root/key vs invalid list/null/scalar/tx record; доменные ошибки без raw payload/path, no silent coercion/reset/удаление чужих ключей. Неправильная форма не пустой target и не successful observation. Transition: proven-before-effect vs uncertain-after-effect, durable attempt, unobserved/ambiguous и честный sync aggregate. Per-intent continuation YAML предложить явно, не объявлять прежним обещанием A.

E2E: populated/fresh, related+unrelated keys, repeated sessions, own correction only и one-write recovery. Отказ форма+unknown outcome не подменяется fake ack.

### Q-A2-05 — P2

Минимальный evidence ref: run identity, immutable manifest hash, code/input/environment linkage и case/receipt locator. Latest pointer не sole proof. Критерий two-run retains original evidence; не закрывать весь tooling долг без реализации/прогона.

## Передача следующему этапу

Готовый узкий контракт worker-fix TD19 (P0) с конкретным списком изменяемых компонентов и негативными E2E, без кода продукта. TD20 отдельно scope/решение, TD21 минимальная часть refs уже в handoff. Подготовить PL003 delta: семь реальных leak points аналитика → hypotheses/checks, прочие поисковые/веточные API GAP, не подменять selective search snapshot-ом. Требование immutable nested refinement оставить будущему research/slice: не расширять нынешние пять вопросов тайно; перечислить сохранённую зависимость.

После завершения этого researcher оркестратор завершает материал текущего цикла, запускает PL003 по поручению заказчика; тот планирует SEC003/QA003 и даёт checks для нового worker. Это не разрешение откладывать TD19 под видом будущей проверки: fix остаётся P0 и affected A не принят.

## Собственные артефакты

ПЕРВЫЙ: artifacts/RESEARCHER_AB002_A.json с честным PARTIAL, scope и remaining; затем дополнить и завершить.
Финальные:
- artifacts/RESEARCHER_AB002_A.json: role/task/status/completion_state, questions[] ровно Q-A2-01…05 с exact_question, механизм/контракты/sources/evidence/checks/risks/needs_user; field/state tables, recommendations/next_slices, planner_handoff, deferred_requirements, unverified/not_implemented. completion завершает материал, НЕ реализацию/приёмку.
- reports/RESEARCHER_AB002_A.md: практический хендофф для планировщика и узкого fix, внутренние/публичные поля и переходы, E2E критерии, остаток/UD.
- runtime/RS002_A/**: source ledger, безопасные локальные прототипы/validation, exact question and finding/debt coverage. Связь evidence ID из analyst раскрывать через evidence_catalog, не выдавать голый ID за URL.

Не закрывать debt на исследовании. JSON парсится, все пять вопросов дословно и уникальны, schema required fields, local evidence refs существуют. Паттерны, только предложенные на бумаге, имеют proposed/not_tested, а не PASS запуска.

## Границы/инструменты/бюджет

read/search/file write/patch/terminal. Python E:/opencode_harness_portable/.venv/Scripts/python.exe. Запись только свои artifacts/RESEARCHER_AB002_A.json, reports/RESEARCHER_AB002_A.md, runtime/RS002_A/**; code/tests/docs/cards/debts/config/plugins read-only. Без Git/install/сети/listeners/paid/секретов/live данных/удаления прежних evidence. Не повторять всю E2E matrix для уже доказанного симптома. Изолированный прототип для трудной гарантии допустим, не fake product success.

Ориентир 12–18 calls, последние 3 зарезервировать на файлы и validation. При cap — continuation этой же роли с точным остатком, parent за тебя не пишет. Planner/worker самостоятельно не запускать.
