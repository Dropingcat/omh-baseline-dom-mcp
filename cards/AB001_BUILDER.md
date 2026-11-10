# AB001 — технологическая карта разработчика исполняемого макета

## Роль

Разработчик/worker. Не ресерчер, не процессный аудитор и не принимающий. Исполняется native Hermes general worker после разрешённого fallback OpenCode. Контракты harness: docs/CODERS/15_GENERAL_HANDS.md (scope/артефакты/реальное исполнение), 03_ACCEPTANCE.md (чек-лист фактов), 08_ANALYST_RESEARCHER_CONTRACT.md — материал уже пройден, не повторять research. Следовать test-driven-development и incremental-implementation в вертикальных срезах. Запрет удаления существующего кода и запрет Git commit имеют приоритет над generic skill defaults.

Ветка разработки логическая AB, задача AB001. Это не утверждение о смене Git ref; текущую physical branch не менять. Создаваемые synthetic claims имеют собственные owner-provided AA/AB markers, а не все автоматически AB только из роли разработчика.

## Слова заказчика — дословно

естественно отда база   но предусмотри внутри на каждом калйме маркер ветки. пердлагаю запустить ресерчера и аналитика для закрытия вопросов  которые ты сформулировал и собрать  начальные документы и макет- создай директорию проекта в харнесс и приступай к планироавинию и сборке мактеа используй карты технологические для субагентов

Разрешённый fallback — дословно:
проверь три модели GLM DEEPSEEC FLINT  по порядку  если ни одна не сработает то через субаентов гермес с правилами  из харнесс

## Вход — прочитать полностью

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.
- P/REQUIREMENTS.md — первичные слова, выше проектных решений.
- P/docs/SPEC.md и P/docs/IMPLEMENTATION_PLAN.md — конкретный scope и последовательность.
- P/research/AA002_RESEARCH.json — normative storage_contract, digest_contract, type_contract, acceptance_matrix T01–T20, golden_vectors.
- P/research/AA002_RESEARCH.md — детали, особенно set/ordered array правила и minimal SDK path.
- P/analysis/AA001_ANALYSIS.json — baseline_traceability/исходные проверки.
- P/docs/acceptance/AA001_HANDOFF.md и AA002_HANDOFF.md — границы prior evidence.
- Точные SDK исходники/сигнатуры при необходимости, не повторять глобальную разведку.

## Требуемый результат

Рабочий локальный стенд, не HTML-картинка и не stub: SQLite ядро, append-only history, персистентные candidates/reviews/admissions, mandatory claim origin_branch/origin_version, scoped projections/YAML, actual stdio MCP server/client test. Внешние OMH/Git/issuer строго simulation. Production unknown trust fail-closed. Один demo-module запуск создаёт реальные безопасные artifacts, объясняет результат и остаток.

Выполняй 6 vertical slices IMPLEMENTATION_PLAN.md последовательно, каждый red→green. На первых 1–2 поведениях сохрани реальный RED output; не подменять техническую import ошибку доказательством проверки бизнес-инварианта. Во время разработки выполняй реальные small checks, не откладывай первый прогон на конец.

Особенно не потерять:
- Exact raw bytes, no normalization; restricted canonical JSON (NOT JCS), reject duplicate keys/coercion/floats; stable UUID and local_id reorder semantics.
- Independent demo reviewer назначается injected fixture context, не tool args; self/helper/forged unknown identity denied; demo label не production.
- Atomic admission включает facts/events/CAS/receipt/idempotency/outbox. Dedupe до OCC для lost response. Actual two-process contention/barrier and process death/reopen before/after commit. Блокировку/сбой не имитировать нарисованными результатами.
- Append link/comment/property/applicability/archive/replacement проходит gate; old rows immutable through API and ordinary SQL triggers.
- AA archive не AB; source origin неизменен. Trace реально выводит coverage/stale/conflict/pending причины; incomplete scope UNKNOWN; no automatic owner close.
- Outbox failure/ambiguous/target read-back; historical scoped deterministic YAML at exact revision; no direct caller path.
- MCP handshake реально subprocess. Model-facing context/principal role запрещены. Сервер launch args --simulation/fixture-role — доверенный тестовый adapter и явное ограничение, не auth-претензия.

## Scope записи

Только P/mockup/**, P/tests/**, P/runtime/**. README запуска — P/mockup/README.md. Source harness и все исходные документы/analysis/research/cards read-only. Можно создать tests helpers и fixtures; никаких сетевых listeners, auto-fetch и live adapter calls.

Никаких .env/auth/personal DB/transcripts, secrets, package installs, edits plugins/config/registry/.kanban.db; никаких branch/checkout/worktree/commit/merge/push. Терминальные записи в source создавай стандартными file tools, не shell heredoc. Не удалять существующий код; новые исправления только целевые изменения. Не делегировать.

## Инструменты и среда

skill_view (test-driven-development/incremental-implementation), read_file/search_files, write_file/patch, terminal для Python/pytest/demo и stdio subprocess. Interpreter exact E:/opencode_harness_portable/.venv/Scripts/python.exe; Python3.11.15, mcp1.30.0, PyYAML6.0.3, pytest9.1.1 уже наблюдались. Никакого pip/uv install. TMPDIR/TEMP/TMP и pytest basetemp только внутри P/runtime/. Не использовать system temp и реальные БД. -B / no cacheprovider; pycache при необходимости только runtime/.

## Финальные команды — реально выполнить

Из P:
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.demo

README должен позволять повторить из чистой synthetic run directory. Демо не перезаписывает прежние артефакты без явного разрешённого reset (предпочтительны новые run dirs).

## Выход

- Source + tests + fixtures + mockup/README.md.
- P/runtime/AB001_RESULT.md и .json: status PASS|PARTIAL|BLOCKED, actual files, commands/exit codes, per_case T01–T20[{action,expected,actual,evidence_paths,status}], not_implemented[], security_limits[], known_failures[], demo_artifact_paths[]. Это self-report, не APPROVE.
- P/runtime/logs/AB001_* реальные логи RED/GREEN/full tests/demo/MCP/fault tests. Если transport logger не может сохранить exact IDs — отметь ограничение и не выдумывай JSONRPC transcript.

Проверить JSON и пути результатов. В финальном ответе точные команды, фактический результат и что ещё НЕ сделано. Unit pass не заменяет physical fault/concurrency/transport evidence. Не печатать огромные исходники/логи в ответ.

## Дополнение AB001-r2 (оркестратор, после фактического прогона)

Оркестратор сам прогнал `pytest tests -q` из P: **15 passed, 13 failed**. Это фактическое состояние, не самоотчёт.

Причина 13 падений: тесты создают каталог через pytest `tmp_path` (C:/Temp/...), а `Service.__init__` требует каталог внутри `P/runtime`. Падает на `ValueError: RUNTIME_PATH_REQUIRED`.

Требования к исправлению:
- Ограничение пути **не ослаблять** (никакого «разрешить любой каталог»). Исправить тестовый fixture: рабочий каталог создаётся внутри `P/runtime/tmp/<уникальное имя>` и очищается тестом.
- Не подменять падение бизнес-инварианта техническим исключением и не помечать тест skip ради зелёного статуса.

Отсутствующие файлы по карте (проверено `find`): нет `mockup/server.py` (stdio MCP), нет `mockup/demo.py`, нет `mockup/README.md`. Карта требует реальный MCP handshake и demo-прогон — их нужно создать, а не объявлять существующими.

Маркер ветки на клайме (требование заказчика, подтверждено): поле `claims.origin_branch` есть в схеме, но проверка обязана подтвердить, что маркер реально выходит наружу в каждом из мест: снимок ветки, экспорт YAML, история/trace, и что маркер нельзя изменить событием `property`. Тест на это — обязательный.

Выход дополняется: точный список исправленных падений, фактический exit code полного прогона, пути созданных server/demo/README и лог MCP handshake.

## Дополнение AB001-r3 (после вердикта AC001 REQUEST_CHANGES)

Вердикт AC001 принят как рабочая обратная связь: 1 critical, 2 major, 5 minor. Код макета сдаётся повторно. Verdict — не приказ «переделать всё», а точный список дефектов.

Обязательные исправления:

1. **F1 критический — ложный READY.** `mockup/projections.py:10-14`: вид `applicability` пересоздаёт запись клайма (`claims[cid]=dict(...)`) и обнуляет `archived` и `properties`. Репродукция: архив опоры → `applicability` в ту же ветку → `archived=false`, `reasons=[]`, `ready_for_owner_review=true`. Это и есть запрещённое ложное закрытие.
   Требование: состояние клайма накапливается по истории; `applicability` не сбрасывает `archived` и не теряет свойства. Нужен регрессионный тест ровно на этот порядок событий: после архивирования и последующего applicability клайм остаётся архивированным, а trace не выдаёт готовность.
2. **F2 major — неполная MCP-поверхность.** SPEC.md:46 требует 10 инструментов; в `mockup/server.py` семь. Добавить `dom_append`, `dom_query`, `dom_resume`, `dom_sync_status` (и путь подтверждения outbox, если он нужен для `dom_sync_status`). Без этого `ready_for_owner_review` через MCP недостижим: `SYNC_PENDING` нечем закрыть. Запрет на arbitrary SQL/update/delete/fetch/path tools сохраняется; role/principal в аргументы не добавлять.
3. **Minor — `trace('master')` для запрещённого principal** падает `KeyError` вместо `SCOPE_DENIED`.
4. **Minor — цепочка хешей пишется, но не проверяется.** Добавить проверку `previous_hash`/`event_hash` по ветке и показывать её результат в trace; тест: прямая вставка поддельного события в БД обнаруживается проверкой. Триггеры UPDATE/DELETE не считаются достаточной защитой.
5. **Minor — `idempotency` без `work_ref`:** ключ идемпотентности должен быть ограничен работой, а не только операцией и ключом.
6. **Minor — обрыв агрегации ошибок на неизвестном `content_type`:** отклонение должно попадать в список ошибок как `INVALID_TYPE` для конкретного item, а не прерывать разбор.
7. **Minor — расхождение колонок `claims` с контрактом:** привести к контракту либо зафиксировать явное соответствие в README/спецификации; не молчать.

Не требуется и запрещено: «чинить» реальные OMH/Git/issuer адаптеры, ставить skip, ослаблять тесты или ограничение `RUNTIME_PATH_REQUIRED`, менять oracle. После исправлений — полный прогон, демо, обновление README со списком инструментов и повторный self-report `runtime/AB001_RESULT.*` (статусы честные, self-report не APPROVE).

## Дополнение AB001-r4 (после AC001-R2 REQUEST_CHANGES, AC002 APPROVE)

AC002 дал APPROVE с 7 minor; AC001-R2 нашёл **новый critical N1**. Исправляется только перечисленное.

1. **N1 critical — потеря снимка зависимостей клайма.** `mockup/projections.py:16,29`: `_materialize(...)` берёт `dependencies` и `review_id` из пакета события, поэтому при шаринге через `applicability` клайм в целевой ветке получает зависимости пакета шаринга, а не свои. Следствие: `STALE_CHECK` в целевой ветке не срабатывает, `trace` отдаёт `ready=true` при устаревшей опоре; после `exclude` источник становится `ready=true` с пустыми `blockers`.
   Требование: снимок зависимостей и `review_id` привязываются к клайму в момент допуска (иммутабельно, в той же транзакции) и используются проекцией в любой ветке. Событие `applicability` не поставляет зависимости клайма.
   Обязательный регрессионный тест до фикса: клайм с `dependencies={'AA':0}` допущен в `AA`, шаринг в `AB`, `AA` уходит на следующую ревизию → в `AB` у клайма остаются `{'AA':0}`, `trace('AB')` содержит `STALE_CHECK`, `ready=false`; после `exclude` `AA` master не готов.
2. **N2 minor** — README: убрать утверждение, что обнаруживается любая прямая вставка события. Обнаруживается наивная (без пересчёта хеша) и разрыв цепочки; самосогласованная подделка требует внешнего checkpoint и в макете не покрыта.
3. **M1 minor** — `demo.py`: `--reset` только для каталога, созданного этим демо (`demo.json` с ожидаемой сигнатурой); сам `runtime/runs` и чужие каталоги — отказ. Прежние прогоны не удалять.
4. **M2 minor** — неизвестный инструмент: структурированная ошибка в контракте MCP, недостижимый код `UNKNOWN_TOOL` убрать или сделать достижимым.
5. **M4 minor** — `storage.py`: заменить `assert` на явные проверки с отказом; поведение не должно зависеть от `python -O`.
6. **M5 minor** — `--directory`, указывающий на файл: чистый отказ вместо трейсбека; взаимоисключающие `--simulation/--no-simulation` отклонять.
7. **M7 minor** — `tests/test_bytes_types.py:29` не должен зависеть от `research/AA002_RESEARCH.json`: тест обязан быть самодостаточным (мини-fixture внутри теста), без skip и без ослабления проверки.

Запрещено: ослаблять тесты, ставить skip, менять oracle, трогать `RUNTIME_PATH_REQUIRED`, расширять область записи. После фикса — полный прогон, демо, повторный self-report с честными статусами.

## Дополнение AB001-r5 (после AC001-R2: REQUEST_CHANGES, R2-1 major)

Вердикт ревьюера: N1 исправлен (подтверждено его пробами), но найден новый дефект того же класса.

**R2-1 (major) — иммутабельность обходится `INSERT OR REPLACE`.** Проверено оркестратором независимо, `runtime/tmp/probe_replace.py`:

```text
BEFORE deps: {"AA":0}
REPLACE_ACCEPTED=yes
AFTER deps: {}
PROJECTED deps: [{}]
```

Причина: неизменяемость держится на триггерах `BEFORE UPDATE`/`BEFORE DELETE`. В SQLite `INSERT OR REPLACE` при конфликте PK удаляет строку и вставляет новую, а при выключенных `recursive_triggers` триггер `DELETE` не срабатывает. Итог: снимок зависимостей переписывается на `{}`, проекция снова даёт `ready=true` — ложная готовность класса N1, молча. Тем же оператором переписывается `claims.origin_branch`.

Требования к исправлению:
1. Закрыть `INSERT OR REPLACE`/`INSERT OR IGNORE`-подмену для всех неизменяемых таблиц (`binding`, `candidates`, `claims`, `claim_snapshots`, `events`, `reviews`, `transactions`, `idempotency`, `outbox`, `delivery_events`). Допустимые способы: `BEFORE INSERT` guard, который отказывает при существующем PK, либо `PRAGMA recursive_triggers=ON` вместе с отказом в `DELETE`-триггере; выбор обосновать в README.
2. Обязательный red-тест до фикса: `INSERT OR REPLACE` по `claim_snapshots` и по `claims` отклоняется, проекция и trace после попытки не меняются (`ready` остаётся прежним, маркер ветки прежний). Сохранить реальный вывод падения.
3. Проверить, что штатный путь допуска (обычный `INSERT`) продолжает работать и что миграции/инициализация чистой базы не сломаны.

Не трогать: сам протокол допуска, область записи, ограничение `RUNTIME_PATH_REQUIRED`, оракулы существующих тестов.

После фикса: полный `pytest` (реальный exit code), демо, обновление `runtime/AB001_RESULT.*` (revision `AB001-r5`), отметка в README о выбранном способе защиты от REPLACE.

## Бюджет и развилки

Не переусложнять. Малые модули/простые функции, без event bus/framework/нового planner. Production gaps Q01/Q02/Q08 не пытаться «чинить» за счёт исходников/ключей/новых сервисов. Технические решения в scope выводить из уже готового AA002; невозможный пункт явно PARTIAL и конкретный следующий шаг, а не молча сокращать контракт. При исключении в тесте найти причину, не ослаблять oracle ради зелёного статуса. В конце закрыть все дочерние тестовые процессы.
