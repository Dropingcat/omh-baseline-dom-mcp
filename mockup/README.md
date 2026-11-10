# DOM ↔ OMH — исполняемый синтетический макет

## Текущий срез AB002-A / continuation C2 (2026-11-07)

Это self-report разработчика, **не независимая приёмка** (`is_approval=false`).
Ниже разделы AC001/AB001 — история соответствующих сдач, а не новое доказательство.
Точный новый результат: `runtime/AB002_A/e2e_manifest.json`,
`artifacts/WORKER_AB002_A.json`, `reports/WORKER_AB002_A.md`.

На исходниках, отпечатки которых сохранены в `command-C2-2ce0fd8d/`:
**26/26 SIMULATION E2E PASS**, полный процесс завершился с exit 0;
финальный pytest — **64 passed / exit 0**, demo — **exit 0**.
Это не full-system READY: LIVE OMH=NOT_TESTED, срезы B/C/D и UD-01…06 открыты.

### Повторение без удаления прежних прогонов

Из `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp`:

```bash
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.ab002_e2e
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q --basetemp=runtime/AB002_A/pytest-final-C2
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.demo
```

При повторении pytest задайте новое имя basetemp, чтобы pytest не очищал старый каталог.
E2E всегда создаёт новый `runtime/AB002_A/matrix-<hex>/` и сохраняет предыдущий
manifest внутри него. У runner нет case-filter CLI: `--help` объявляет только
`--baseline`; **не запускайте baseline на новых исходниках** — старое ложное ack
уже зафиксировано в `baseline-a668de14/` на прежней версии.
Для долговечной квитанции команды/exit/PID/stdout/stderr и before/after fingerprints:

```bash
E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AB002_A/run_command_c2.py -m mockup.ab002_e2e
```

Выделяйте E2E минимум 600 секунд tool timeout; при более долгом запуске —
tracked background process, не короткий timeout и не успех по отдельным строкам.
Варианты: E0; E1 (пустая/существующая); E2; E3/E4 (до/после rename);
E5 (второй процесс держит lock); E6 (недоступная/лгущая цель, lost reply,
смерть после send); E7/E8; E9 (hash/envelope, AA и AA+AB); E10;
binding negatives; E12 (pending/ambiguous, два процесса); A7 (corrupt/read-only/
unavailable); A9 (legacy additive/incompatible).
E11/S4 revalidation, LIVE и полный декартов набор стартов намеренно не объявлены PASS.

### Протокол, схема и ограничения A

`runtime/AB002_A/protocol.md` фиксирует последовательность:
immutable outbox → durable attempt/reconcile → точный read-back → immutable
observation → связанный ack. `delivery_attempts`, `delivery_observations`,
`delivery_acks` добавлены к прежним таблицам. Ack ссылается на наблюдение,
intent/tx/digest/target; shape/binding проверяются SQL-триггерами и read-validator.
Ответ `attach='ack'` сам по себе ничего не подтверждает. Legacy state не даёт ack.
Метод `Service.delivery()` отказывает caller-supplied state; MCP tool `delivery`
не опубликован. Приватность метода не считается production authentication.

Повтор после смерти процесса сначала сверяет конечную цель; локальная цель
использует OS file lock и tx/digest-idempotency. Это **не универсальный exactly-once**.
Внешняя операция не выполняется внутри SQLite write-транзакции. Проверенный
read snapshot удерживается через side effect; observation содержит read_at,
chain_head и revisions. Это может временно блокировать concurrent writer и дать busy.
Ack доказывает факт в момент наблюдения, не вечную доступность цели.

query/trace/resume/export/sync/sync_status проверяют hash и форму конверта
на согласованном срезе. Повреждение → CHAIN_BROKEN с локатором и NOT_READY,
без KeyError и без нового экспорта/доставки. Repair/rewind не реализованы.
Совместимая legacy DB до явного dom_init даёт MIGRATION_REQUIRED; dom_init
выполняет additive installation с сохранением прежних фактов и legacy delivery rows.
Несовместимая схема получает MIGRATION_REQUIRED, без reset/DROP исходной БД.

E10 требует конкретного SQLITE_CONSTRAINT_TRIGGER и точного unchanged read-back
всех строк/файлов/хеша БД, включая REPLACE/IGNORE/UPSERT и secondary UNIQUE.
При replay events предыдущий hash не равен current head: CHAIN_INTEGRITY может
сработать раньше duplicate guard; принимается только этот обоснованный отказ,
а не любое исключение. Новый E10 содержит 88 SQL-проб; binding — ещё 23.
На Windows C2 обнаружил незакрытый readback SQLite handle: исправлен явный close,
с RED/GREEN-регрессией. Directory-path отказ возвращает точный extended code
SQLITE_CANTOPEN_ISDIR=526; oracle требует допустимую пару code/name, не catch-all.

Production identity/issuer, OS-изоляция, внешний checkpoint и защита от file-owner/
in-process злоумышленника или лгущего read-back не доказаны. Offline-аутентичность
новой упаковки YAML, branch/master ready API, convergence/revalidate — не закрыты A.
Требование вложенных immutable уточнений из REQUIREMENTS §1.4/§3 —
**deferred_to_researcher**, без реализации или молчаливого выбора семантики.


Локальный стенд для контракта DOM (append-only утверждения с маркером ветки) и
MCP-транспорта поверх него. Это **не** production-сервис и **не** HTML-макет:
всё, что описано ниже, реально исполняется на локальном SQLite и реальном
stdio-процессе MCP.

Внешние системы (OMH evidence target, Git, issuer, аутентификация) — только
simulation. Никаких сетевых слушателей, установок пакетов и обращений к живым
сервисам нет.

## Требования

- Интерпретатор: `E:/opencode_harness_portable/.venv/Scripts/python.exe`
  (Python 3.11.15, `mcp` 1.30.0, `PyYAML` 6.0.3, `pytest` 9.1.1 — уже стоят).
- Никаких `pip`/`uv install`.
- Все изменяемые файлы — только внутри `P/runtime/`. Каталог прогона должен
  лежать в `P/runtime`, иначе сервис отказывает `RUNTIME_PATH_REQUIRED`
  (это продуктовое правило, а не ограничение тестов).

```
P = E:/opencode_harness_portable/projects/omh-baseline-dom-mcp
```

## Быстрый старт: один прогон демо

```bash
cd E:/opencode_harness_portable/projects/omh-baseline-dom-mcp
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.demo
```

Демо создаёт **новый** каталог `runtime/runs/run-<UTC>-<hex>/` и в нём реальные
артефакты:

| Путь | Что это |
|---|---|
| `dom.sqlite3` | SQLite: binding, candidates, reviews, transactions, claims, claim_snapshots, events, idempotency, outbox, delivery_events |
| `exports/AA-<rev>-<sha256>.yaml` | детерминированный scoped-экспорт ветки на точной ревизии |
| `omh-target.json` | simulation-цель внешней доставки (read-back по `tx_id` + digest) |
| `demo.json` | машинный итог: admissions, denials, trace, markers, artifacts |

В stdout печатается ход прогона, итог (`READY`, `owner_close_called=false`) и
раздел `REMAINDER` — что сознательно не реализовано.

Свой каталог (внутри `runtime/`) и повторное использование:

```bash
... -m mockup.demo --output-dir runtime/tmp/demo-a          # новый пустой каталог
... -m mockup.demo --output-dir runtime/tmp/demo-a --reset  # только свой прошлый прогон
```

`--reset` разрешён **только** для каталога, который создало это же демо: внутри
лежит `demo.json` с `tool: "mockup.demo"`, `simulated: true` и `run_directory`,
совпадающим с самим каталогом. Всё остальное — отказ `REFUSED` без удаления:

- сам `runtime/runs` (общий корень прогонов) и `runtime/`;
- чужие каталоги, рукописный/скопированный `demo.json` без совпадающей подписи;
- непустой каталог без `--reset`.

Прежние прогоны не удаляются: reset трогает только целевой каталог. Путь,
указывающий на файл, отклоняется (`REFUSED ... is not a directory`).

## Тесты

```bash
cd E:/opencode_harness_portable/projects/omh-baseline-dom-mcp
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q
```

`tests/conftest.py` переносит pytest-фикстуру `tmp_path` в
`runtime/tmp/<имя-теста>-<hex>/` и удаляет её после теста; `TEMP/TMP/TMPDIR`
сессии тоже указывают в `runtime/tmp`. Проверка `RUNTIME_PATH_REQUIRED` при этом
не ослаблена.

Физические тесты (не unit-моки):

- `tests/test_storage_faults.py` — два реальных процесса с `multiprocessing.Barrier`
  на одной ревизии; смерть процесса (`os._exit(71)`) на `after_facts`,
  `before_commit`, `after_commit` с последующим переоткрытием БД.
- `tests/test_mcp_stdio.py` — реальный `python -m mockup.server` subprocess:
  SDK-клиент (`initialize`/`list_tools`/`call_tool`) и «сырой» JSON-RPC обмен с
  корреляцией id 1/2/3; проверяется, что stdout содержит только protocol frames.
- `tests/test_demo.py` — запускает `python -m mockup.demo` как процесс и
  проверяет физические артефакты, отсутствие перезаписи и `--reset`.
- `tests/test_branch_marker.py` — маркер ветки в снимке, YAML, trace, history и
  невозможность его переписать событием `property` или обычным SQL.

## MCP-сервер

Сервер — обычный stdio-MCP на `mcp.server.lowlevel`, stdout только JSON-RPC.

```bash
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.server \
  --directory runtime/runs/manual-1 --role reviewer --simulation \
  --log-file runtime/logs/manual_mcp.jsonl
```

- `--directory` обязателен, должен резолвиться внутри `runtime/` и быть
  каталогом; путь на файл — чистый `REFUSED` с exit 2, без трейсбека.
- `--role author|helper|reviewer|owner` — **launch-time** fixture identity.
- `--simulation` / `--no-simulation` взаимоисключающие: передать оба — ошибка
  разбора аргументов (exit 2). Без simulation любой `init` отказывает
  `OMH_BINDING_UNVERIFIED` (fail-closed).
- `--log-file` — JSONL диагностика (только внутри `runtime/`); stdout не
  используется для логов.

Инструменты (нормативный список `docs/SPEC.md:46` — все десять присутствуют):
`dom_init`, `dom_resume`, `dom_submit`, `dom_review`, `dom_admit`, `dom_append`,
`dom_query`, `dom_trace`, `dom_export`, `dom_sync_status`.

Дополнительно объявлены два инструмента, которых нет в нормативном списке:

- `dom_sync` — исполнение синтетического outbox (YAML-экспорт + simulated OMH
  attach с read-back). `SPEC.md:46` прямо допускает отдельный `dom_sync` для
  synthetic outbox; без него MCP-клиент не может закрыть `SYNC_PENDING` и
  `ready_for_owner_review` недостижим по протоколу.
- `dom_snapshot` — совместимый алиас `dom_query` (тот же результат и схема),
  оставлен, чтобы не ломать существующих клиентов и тесты.

| Инструмент | Аргументы | Что возвращает |
|---|---|---|
| `dom_init` | `external_work_ref`, `policy_digest` | `INITIALIZED` \| `SCOPE_DENIED` \| `POLICY_MISMATCH` \| `OMH_BINDING_UNVERIFIED` |
| `dom_resume` | `branch` | `RESUMED` + `snapshot`, `trace`, `sync` (три вложенных ответа) |
| `dom_submit` | `payload_json` | `RECORDED_CANDIDATE` (+`candidate_id`,`intent_digest`) \| `REJECTED` (+`errors[]`) |
| `dom_review` | `candidate_id`, `intent_digest` | `DEMO_REVIEWED` (+`review_id`) \| `DIGEST_MISMATCH` \| `INDEPENDENCE_NOT_ENFORCED` |
| `dom_admit` | `candidate_id`, `review_id`, `idempotency_key`, `intent_digest` | `DEMO_ADMITTED` (+`tx_id`,`revision`,`claim_ids`/`event_ids`) \| `REVISION_CONFLICT` \| `STALE_REVIEW` \| `IDEMPOTENCY_MISMATCH` |
| `dom_append` | `payload_json` (operation=`append`) | `RECORDED_CANDIDATE` — только кандидат; нужен `dom_review` + `dom_admit`, это не обход приёмки |
| `dom_query` | `branch`, опц. `revision` | `SNAPSHOT` (+`claims`,`history`,`conflicts`,`converged`,`excluded_branches`) \| `SCOPE_DENIED` |
| `dom_trace` | опц. `branch` (по умолчанию `master`) | `TRACE` \| `ready_for_owner_review` (+`residual`,`origins`,`blockers`,`chain`,`owner_close_called=false`); ограниченный scope → `UNKNOWN` |
| `dom_export` | `branch`, опц. `revision` | `EXPORTED` (+`handle`,`sha256`,`revision`) \| `EXPORT_PENDING` \| `SCOPE_DENIED` |
| `dom_sync_status` | `branch` | `SYNC_STATUS` (+`intents[{intent_id,kind,tx_id,revision,state}]`), только чтение |
| `dom_sync` | `branch` | `SYNCED` \| `SYNC_PENDING` (+ те же `intents` через `dom_sync_status`) |
| `dom_snapshot` | = `dom_query` | алиас |

Полный путь «pending → READY» по протоколу: `dom_admit` → `dom_trace`
(`SYNC_PENDING`) → `dom_sync` по каждой ветке → `dom_sync_status` (все `ack`) →
`dom_trace` (`ready_for_owner_review=true`, `owner_close_called=false`). Это
исполняется в `tests/test_mcp_stdio.py::test_ready_for_owner_review_is_reachable_over_mcp`,
evidence — `runtime/logs/AB002_mcp_ready.json`.

Ни один инструмент не принимает `role`, `principal`, `simulation` или
`capabilities`: попытка передать их даёт `INVALID_ARGUMENTS` (isError), а не
тихое повышение прав. Неизвестное имя инструмента — структурированная ошибка
`{"status":"UNKNOWN_TOOL","error":{"code","tool","message"}}` (isError), а не
исключение транспорта. Аргументы связываются строго по типам, без приведения
(`expected_branch_revision: "0"` — это `REJECTED`/`INVALID_TYPE`, а не `0`).

Минимальный клиент:

```python
import asyncio, json, sys
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=['-B', '-m', 'mockup.server', '--directory', 'runtime/runs/manual-1',
              '--role', 'author', '--simulation'],
        cwd='E:/opencode_harness_portable/projects/omh-baseline-dom-mcp')
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            info = await session.initialize()
            print(info.protocolVersion, info.serverInfo.name)
            print([tool.name for tool in (await session.list_tools()).tools])
            snapshot = await session.call_tool('dom_snapshot', {'branch': 'AA'})
            print(json.loads(snapshot.content[0].text)['status'])

asyncio.run(main())
```

## Карта файлов

| Файл | Роль |
|---|---|
| `mockup/dom_contract.py` | restricted canonical JSON (`dom-c14n/v1`, не JCS), точные байты, валидатор семи типов и событий |
| `mockup/storage.py` | SQLite DDL, PRAGMA, SQL-триггеры неизменяемости |
| `mockup/admission.py` | единственный путь записи: init → submit → review → admit, OCC, dedupe, outbox, sync, trace, export |
| `mockup/projections.py` | чистые проекции ветки: snapshot + trace (coverage/stale/conflict/pending, origin markers) |
| `mockup/ports.py` | fixture-идентичности (`--role`) и simulation-порт внешней цели |
| `mockup/fixtures/__init__.py` | owner-provided синтетические входы (work/task/policy, пакеты, правки) |
| `mockup/server.py` | stdio MCP-сервер (launch-time trust, strict args) |
| `mockup/demo.py` | один воспроизводимый прогон с реальными артефактами |
| `tests/conftest.py` | pytest `tmp_path` → `runtime/tmp`, `TEMP/TMP` → `runtime/tmp` |
| `tests/test_dom_contract.py` | агрегированные безопасные ошибки валидации |
| `tests/test_bytes_types.py` | семь типов, restricted JSON, golden raw-векторы, set/ordered массивы |
| `tests/test_admission.py` | кандидат ≠ принятое; независимый demo-reviewer; персистентность |
| `tests/test_storage_faults.py` | гонка двух процессов, смерть процесса до/после commit, stale review |
| `tests/test_scope_trace.py` | append-события, scope до обхода, immutability, YAML на ревизии, outbox, exclusion |
| `tests/test_projection_state.py` | регрессия F1: архив → `applicability` в той же ветке → клайм остаётся архивным, ложного READY нет |
| `tests/test_claim_snapshot.py` | регрессия N1: зависимости/`review_id` клайма берутся из `claim_snapshots`, а не из пакета `applicability`; `STALE_CHECK` в целевой ветке; иммутабельность снимка через SQL |
| `tests/test_immutable_replace.py` | регрессия R2-1: `INSERT OR REPLACE`/`OR IGNORE`/upsert по неизменяемым таблицам отклоняются (`IMMUTABLE`), снимок и маркер ветки не меняются, `trace` не становится `READY`; штатный `admit` и чистая инициализация работают |
| `tests/test_integrity_contracts.py` | F4 scope-before-trace, F5 проверка хеш-цепочки и поддельного INSERT, F6 work-scoped idempotency, F7 агрегация `INVALID_TYPE`, F8 колонки `claims` |
| `tests/test_branch_marker.py` | маркер ветки во всех выходах + запрет перезаписи |
| `tests/test_mcp_stdio.py` | реальный handshake/list/call, stdout-only протокол |
| `tests/test_demo.py` | процессный прогон демо, его артефакты и границы `--reset` (свой `demo.json`, не `runtime/runs`, не чужие каталоги) |

## Что гарантируется (и проверено физически)

- Exact raw bytes: `raw_sha256` считается по исходным байтам, `body_b64`
  round-trip без нормализации (`\r\n`, NFD, supplementary Unicode различаются).
- Restricted canonical JSON: дубликаты ключей, float/NaN, lone surrogate,
  целые > 2^53 отклоняются; ключи сортируются (это не JCS).
- Кандидат не виден в ветке до `admit`; `admit` — одна транзакция
  (facts + events + head CAS + receipt + idempotency + outbox).
- Dedupe выполняется до OCC: повтор после потерянного ответа возвращает тот же
  `tx_id`/`claim_ids`, изменённый digest — `IDEMPOTENCY_MISMATCH`.
- `reviews`/`claims`/`claim_snapshots`/`events`/`candidates`/`transactions`/
  `idempotency`/`outbox`/`binding`/`delivery_events` защищены SQL-триггерами
  `IMMUTABLE`: `BEFORE UPDATE`, `BEFORE DELETE` и `BEFORE INSERT`-guard, который
  отказывает любой вставке с уже существующим ключом (PK и каждый вторичный
  `UNIQUE`), поэтому `INSERT OR REPLACE`, `REPLACE` и `INSERT OR IGNORE` по
  существующей строке дают `IMMUTABLE`, а строка остаётся байт-в-байт прежней
  (`tests/test_immutable_replace.py`).
- Маркер ветки `origin_branch`/`origin_version` выходит в snapshot, YAML-экспорт,
  history и trace; событие `property` не может его изменить (`IMMUTABLE_FIELD`).
- Scope проверяется до обхода: чужая ветка даёт одинаковый безопасный
  `SCOPE_DENIED` для query/export/trace/sync_status, без счётчиков и утечек.
- Trace выводит причины (`MISSING_COVERAGE`, `STALE_CHECK`, `CONFLICT`,
  `BRANCH_NOT_CONVERGED`, `SYNC_PENDING`); ограниченный scope → `UNKNOWN`;
  закрытие задачи владельцем не вызывается никогда.
- Экспорт YAML детерминирован и адресуется точной ревизией; путь выбирает сервер,
  а не вызывающий; запись атомарна (temp + `os.replace` + read-back).
- Проекция ветки кумулятивна: `applicability` только добавляет связь
  (`applicable_branches`) и не пересоздаёт запись клайма, поэтому `archived` и
  `properties` не сбрасываются, а архивная опора не возвращается в coverage.
- Зависимости клайма и его `review_id` фиксируются в момент **допуска**, в той же
  транзакции, отдельной иммутабельной строкой `claim_snapshots` (PK `claim_id`).
  Проекция в любой ветке берёт их только оттуда: событие `applicability` несёт
  связь с веткой, но не зависимости клайма, поэтому `STALE_CHECK` срабатывает и
  в целевой ветке (`tests/test_claim_snapshot.py`).
- Хеш-цепочка событий проверяется при чтении: `trace` возвращает `chain`
  (`CHAIN_OK` / `CHAIN_BROKEN` с `broken_at_seq`, `reason`) и добавляет
  `EVENT_CHAIN_BROKEN` в `blockers`. Обнаруживается наивная вставка (без
  пересчёта хеша) и разрыв `previous_hash`; триггер `chain_previous_hash` не даёт
  вставить событие, не продолжающее текущую цепочку.
  **Не покрыто:** самосогласованная подделка — вставка события с корректно
  пересчитанными `previous_hash`/`event_hash` — не обнаруживается, потому что
  проверка опирается на те же хранимые значения. Для этого нужен внешний
  checkpoint цепочки (подпись/якорь вне БД), которого в макете нет; см. KF04 в
  `runtime/AB001_RESULT.json`.
- `idempotency` ограничена работой: PK `(external_work_ref, operation, key)`, как
  в `storage_contract` AA002; один и тот же ключ в другой работе — другой intent.
- `claims` хранит `content_type`, `encoding`, `media_type`, `source_ref`
  колонками (не только в payload BLOB); `source_ref` берётся из
  `metadata.source_ref | artifact_ref | repository_ref`, иначе `''`.
- Валидатор агрегирует ошибки по всем доступным элементам: неизвестный
  `content_type` даёт `INVALID_TYPE` для своего item и не обрывает проверку
  общих полей (bytes, encoding, applicability).

## Почему `BEFORE INSERT`-guard, а не `PRAGMA recursive_triggers=ON`

R2-1 закрыт `BEFORE INSERT`-guard'ом на каждую неизменяемую таблицу, а не
переключением `PRAGMA recursive_triggers=ON`: `INSERT OR REPLACE` разрешает
конфликт PK/`UNIQUE` удалением хранимой строки, и именно этого `DELETE` не видит
`BEFORE DELETE`-триггер. PRAGMA — настройка **соединения**, поэтому она
защищала бы только те соединения, что открыты через `Store.connect()`: любой
клиент, пришедший в файл обычным `sqlite3.connect` (так в базу смотрят
независимые пробы ревьюера и `tests/test_immutable_replace.py`), оставил бы её
выключенной и дыра открылась бы заново. Guard хранится в схеме, поэтому
действует для любого соединения и для любого режима (`REPLACE`,
`INSERT OR REPLACE`, `INSERT OR IGNORE`, upsert). Он проверяет не только PK, но
и каждый вторичный `UNIQUE` (`transactions(branch,revision)`,
`outbox(tx,kind,target)`, `binding(work_ref)`, `events(seq)`/`events(id)`): там
`REPLACE` удаляет строку, вообще не касаясь PK. Отказ — `RAISE(ABORT)` уровня
оператора, поэтому отклонённый `REPLACE` откатывается целиком и оставляет
прежнюю строку нетронутой, а штатная вставка новой строки (в том числе
`delivery_events` с автоинкрементным `seq`) проходит как раньше. Триггеры
создаются в `Store.initialize()`, так что существующая база получает их при
следующем `dom_init`.

## Состояние после вердикта AC001 (повторная сдача)

Все замечания AC001 закрыты кодом и регрессионными тестами; статусы ниже —
фактические прогоны, а не намерения.

| ID | Замечание AC001 | Что изменено | Доказательство |
|---|---|---|---|
| F1 (critical) | `applicability` пересоздавал клайм и обнулял `archived`/`properties` → ложный `READY` | `mockup/projections.py`: `_materialize()` создаёт запись один раз, события накапливаются | `tests/test_projection_state.py` (3 теста), `runtime/AB002/ac001_repro_after.json:f1_*` |
| F2 (major) | MCP-поверхность 7 инструментов вместо 10; `SYNC_PENDING` нечем закрыть | `mockup/server.py`: добавлены `dom_resume`, `dom_append`, `dom_query`, `dom_sync_status`, а также `dom_sync` (разрешён `SPEC.md:46`) и алиас `dom_snapshot` | `tests/test_mcp_stdio.py::test_ready_for_owner_review_is_reachable_over_mcp`, `runtime/logs/AB002_mcp_ready.json` |
| F4 (minor) | `trace('master')` для запрещённого principal → `KeyError` | `admission.trace` проверяет scope до обхода, `sync_status().get('intents',[])` | `tests/test_integrity_contracts.py::test_trace_for_forbidden_principal_is_scope_denied` |
| F5 (minor) | цепочка хешей не проверялась, произвольный `INSERT` в `events` | `admission.verify_chain` в `trace.chain` + триггер `chain_previous_hash` | `tests/test_integrity_contracts.py::test_event_chain_is_verified_and_forgery_is_detected`, `::test_event_insert_must_extend_the_stored_chain` |
| F6 (minor) | `idempotency` без `work_ref` | схема `PK(external_work_ref, operation, key)`, `dedupe`/`remember` привязаны к работе | `tests/test_integrity_contracts.py::test_idempotency_is_scoped_to_external_work_ref` |
| F7 (minor) | обрыв агрегации на неизвестном `content_type` | `dom_contract.validate` не делает `continue` до общих проверок | `tests/test_integrity_contracts.py::test_unknown_content_type_does_not_abort_error_aggregation` |
| F8 (minor) | `claims` хранил `content_type/encoding/media/source` только в payload | колонки добавлены в DDL и в `INSERT` | `tests/test_integrity_contracts.py::test_claims_columns_match_storage_contract` |

Расхождения с нормативным списком инструментов, которые остаются осознанно:
`dom_snapshot` — алиас `dom_query` (не удалён, чтобы не ломать существующих
клиентов), `dom_sync` — отдельный инструмент исполнения outbox, разрешённый
`SPEC.md:46`. Оба перечислены выше и в `runtime/AB001_RESULT.*`.

## Состояние после AC001-R2 / AC002 (сдача AB001-r4)

AC001-R2 дал REQUEST_CHANGES из-за нового critical N1; AC002 дал APPROVE с 7 minor.
Ниже — что изменено и чем это проверено. Статусы — фактические прогоны.

| ID | Замечание | Что изменено | Доказательство |
|---|---|---|---|
| N1 (critical) | `_materialize()` брал `dependencies`/`review_id` из пакета события, поэтому при `applicability` клайм в целевой ветке получал зависимости пакета шаринга и `STALE_CHECK` не срабатывал | новая иммутабельная таблица `claim_snapshots` (PK `claim_id`, триггеры `IMMUTABLE`), запись в транзакции `admit`; `projections._materialize()` читает снимок только оттуда, `applicability` несёт только связь с веткой | `tests/test_claim_snapshot.py` (2 теста), RED до фикса — `runtime/logs/AB001_r4_red_n1.log`, GREEN — `runtime/logs/AB001_r4_green_n1.log` |
| N2 (minor) | README утверждал, что обнаруживается любая прямая вставка события | раздел про хеш-цепочку переписан: наивная вставка и разрыв обнаруживаются, самосогласованная подделка — нет, нужен внешний checkpoint | этот README, `runtime/AB001_RESULT.json:KF04` |
| M1 (minor) | `--reset` удалял сам `runtime/runs` и чужие каталоги | `demo.demo_marker()`: reset только для каталога с `demo.json` этого демо (`tool`, `simulated`, совпадающий `run_directory`); `runtime/`, `runtime/runs`, файлы и чужие каталоги — `REFUSED`, прежние прогоны не удаляются | `tests/test_demo.py::test_reset_is_limited_to_this_demos_own_run_directory` |
| M2 (minor) | неизвестный инструмент давал `repr(KeyError)`, а `raise ToolInput('UNKNOWN_TOOL')` был недостижим | `dispatch()` проверяет имя до разбора аргументов; ошибка структурированная (`status`, `error.code`, `error.tool`, `error.message`) в тексте и `structuredContent` | `tests/test_mcp_stdio.py::test_unknown_tool_is_a_structured_error` |
| M4 (minor) | инварианты PRAGMA держались на `assert` и исчезали под `python -O` | явные проверки с `RuntimeError('PRAGMA_*')`/`JOURNAL_MODE_NOT_DELETE` | `tests/test_integrity_contracts.py::test_storage_invariants_are_explicit_not_assertions` |
| M5 (minor) | `--directory` на файл давал трейсбек; `--simulation` и `--no-simulation` вместе принимались | проверка «существует и не каталог» → `REFUSED` exit 2; флаги в `add_mutually_exclusive_group` | `tests/test_mcp_stdio.py::test_server_refuses_file_directory_and_conflicting_simulation_flags` |
| M7 (minor) | `test_bytes_types.py` зависел от `research/AA002_RESEARCH.json` | golden-векторы встроены в тест и сверяются независимо через `hashlib.sha256`; без `skip` | `tests/test_bytes_types.py::test_golden_raw_vectors`, прогон без `research/` |

M3 и M6 из AC002 не входили в задание r4: M6 (`docs/STATUS.md`) вне области
записи AB001, M3 (`guarded` маскирует битую схему под `STORAGE_BUSY_OR_UNAVAILABLE`)
остаётся известным ограничением.

## Явные ограничения (не выдавать за production)

- `simulation=true` во всех ответах; OMH/Git/issuer — fixture, не интеграция.
- Идентичность и независимость ревьюера — fixture запуска (`--role`), не
  аутентификация. Модель не может их подделать через аргументы инструмента, но
  это не доказывает host identity.
- OS-изоляция отсутствует: прямой доступ к SQLite/файлам в обход MCP не
  предотвращается — `NOT_ENFORCED`.
- Реальные Git-мутации (dirty snapshot, merge intentions) не выполняются:
  только fixture-поля и `NOT_IMPLEMENTED`-описание (T20).
- Протокол проверен на одной версии SDK (`2025-11-25`); другие транспорты
  (HTTP/SSE), авторизация MCP и multi-tenant изоляция не реализованы.
- Стенд не является APPROVE: отчёт `runtime/AB001_RESULT.{md,json}` — self-report
  разработчика.

## Диагностика

- `ValueError: RUNTIME_PATH_REQUIRED` — каталог прогона вне `runtime/`.
- `NOT_INITIALIZED` — сначала вызовите `dom_init` в этом каталоге.
- `SCOPE_DENIED` — ветка/работа вне контекста запуска (это ожидаемо).
- `STORAGE_BUSY` — SQLite busy/locked по фактическому primary code;
  `STORAGE_CORRUPT` — corrupt/not-a-database; `STORAGE_READ_ONLY` — read-only;
  `STORAGE_UNAVAILABLE` — недоступное хранилище (включая extended CANTOPEN_ISDIR).
  Ответ содержит sqlite_code/sqlite_name без OS-пути и payload.
- `MIGRATION_REQUIRED` — отсутствующая v2-схема/несовместимая схема; нет silent reset.
- `CHAIN_BROKEN` — hash/форма события нарушены, данные не экспортируются/не доставляются.
- `SYNC_PENDING` — внешняя доставка/экспорт не подтверждены; смотрите
  `sync_status` и повторите `sync`.
