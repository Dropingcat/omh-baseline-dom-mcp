# AN009 — холодный старт DOM: H1 / H2 / H3 / H8

## 0. Что проверял и что оказалось

На изолированной побайтовой копии `mockup` воспроизведены все четыре препятствия реальным stdio MCP. **H3 сильнее пилотного описания:** исходный `dom_resume AA` возвращает `RESUMED` даже для базы, которую доверенный стенд привязал к другому work; чтение не проверяет persisted binding. Живая `runtime/ORIENT/home` не открывалась и не менялась.

Рекомендован C: выданный до запуска пакет E1 + проверяемый receipt E2 + scoped `dom_describe` + безопасные подсказки + `dom_draft_claim`. Прототип прошёл холодный сценарий за **7 вызовов** (6 domain + tools/list), **0 чтений исходников**, **0 угадываний параметров**. Инициализация протокола — ещё один RPC, то есть всего 8 RPC requests; уведомление initialized не является запросом. Кандидат виден в pending, **не объявлен допущенным клаймом**.

Пройдены **38 контролей** (включая положительный независимый допуск и 37 негативных/защитных/идемпотентных контролей), 7 примеров типов. Отдельно найден унаследованный дефект: latest-review `REJECTED` остаётся в pending/count. Это не исправлено под видом удобства. Проверка malformed-input `REJECTED` — другая: такая подача действительно не создаёт pending.

Это исследование и ограниченный прототип, **не приёмка продукта и не согласование решения заказчиком**.

## 1. Воспроизведение и корни

| H | Сырой результат | Корень |
|---|---|---|
| H1 | `NOT_INITIALIZED`; неверный work → `SCOPE_DENIED`, оба без next_action | admission.py:82–88; guarded:31–38; public_dto.py:68,372–376 |
| H2 | правильный work + неизвестная policy → `POLICY_MISMATCH`; `dom_describe` → `UNKNOWN_TOOL` | fixtures/__init__.py:4–6; server.py:36–122 |
| H3 | корректная пустая база и чужой work binding дают `RESUMED`, claims=[] | ready:87–90 не проверяет binding; resume:437–454; storage.initialize:124–130 проверяет binding только при init |
| H8 | недостаточный JSON → typed missing fields; metadata={} → четыре ошибки decision | dom_contract.py:6–15,63–121; tools/list описывает лишь строку payload_json |

Доказательства: `baseline_reproduction.json` (включая исходные кадры) и `wrong_project_reproduction.json`. Аналитик читал код/fixtures, симулятор — нет: это разные доверительные стороны.

Версия фиксируется не Git: `a5268c0877cc6ca6accbc714a073acc35efee9688ce0fe79bba6360ca06a6bf8`. Алгоритм: sha256 конкатенации отсортированных `relative_path + NUL + sha256(file) + LF` для всех mockup/**/*.py. `3cd21d96` — историческая метка пилота; при неизвестном исходном алгоритме не объявляю её равной новому digest. `source_ledger.json` фиксирует файлы и неизменность источников.

## 2. Три варианта и цена

| Вариант | Точные изменения | Цена product/tests LOC (оценка) | Эффект/риск |
|---|---|---|---|
| A — ничего не добавлять | никаких | 0/0 | холодный путь блокирован; не исполняет уже принятый E1+E2; не готовый продукт |
| B — пакет, receipt, describe, схемы, help | server.TOOLS/SIGNATURE/dispatch; admission.ready/init/submit/admit; public_dto.RECORDS/project_tool; storage immutable instance/receipt + trusted issuer | 300–480 / 250–400 | убирает поиск кода, но JSON/base64/канонизацию/key/deps агент строит сам; средний риск миграции/DTO |
| C — B + серверный draft, рекомендован | B + claim_draft.draft_claim; typed DraftResponse, metadata schema/примеры; проверки branch/basis до lookup | 520–850 / 450–700 | убирает ручную сборку байтов, не меняет допуск; средне-высокий риск lifecycle/schema drift |

Все оценки инженерные, не измеренная стоимость будущей реализации. Ограниченный endpoint — 141 физических LOC с плотным форматированием; это не оценка production-кода. Полные file/function changes, поля, миграции, влияние на H и утечки перечислены для КАЖДОГО варианта в JSON `options[]`.

B/C: additive версионированные DTO и инструменты; неизменяемые instance и issuance ledger; legacy receipt не выдумывается — доверенный issuer перевыдаёт. Payload dom/v1 не получает чужеродного receipt-поля: receipt отдельный tool argument. Идемпотентные записи не переписываются. A не отменяет E1/E2, а показывает цену отказа от работ.

## 3. Что именно является пакетом базлайна

Не только `work_ref/policy_digest`: пакет обязан содержать accepted исходные клаймы OMH PLAN, plan pins с точными текстами и sha256, их provenance, scoped требования/ветки, baseline revision+digest. Также version/schema/canonicalization, work/task, immutable instance, identity/root/session/grant/capabilities, policy, issuance id/time/expiry/issuer/receipt. Источник каждого поля описан в JSON `baseline_package.fields`.

Пакет выдаёт доверенный launcher ДО запуска (E1). DOM проверяет привязанный receipt при submit/admit (E2). Receipt удостоверяет **выдачу**, не истинность клайма, не подпись автора и не независимое ревью. Проверяются authenticated issuer и совпадение work/task/instance/recipient/root/session/grant/policy/schema/baseline revision+digest, срок/отзыв. Просто совпадающий хеш недоверенного файла не удостоверяет ничего.

Прототип использует публичный синтетический HMAC-ключ и sidecar instance. Это проверка mechanics tamper-binding, **не криптографическая аутентификация**, не production persistence/expiry/revocation. Пакет стенда имеет `NO_BASELINE` и не импортирует настоящий accepted OMH PLAN. Такой пакет не засчитывается как реализованный E1 в продукте.

## 4. Самоописывающие ответы и анти-оракул

- NOT_INITIALIZED → постоянный BINDING_REQUIRED, действие: describe → его init_arguments.
- SCOPE_DENIED → постоянный NOT_AUTHORIZED, действие: свой пакет/issuer; не возвращать ожидаемый чужой work, найденные ветки или различие foreign/missing.
- POLICY_MISMATCH → LAUNCH_POLICY_STALE только после авторизации; сверить scoped descriptor, не вычислять хеш самому.
- REJECTED → сохранить field paths/codes + постоянный переход к схеме/draft. Никакого кандидата/pending при malformed input.
- WORK_BINDING_MISMATCH → выбранный instance не подтверждён; фактический чужой binding не раскрывается.

`dom_describe({})` без параметров поиска: identity/capabilities, только выданный grant, binding, policy/schema, поддерживаемые типы/metadata/условия и примеры. Это не inventory существующих веток. До ответа требуется доверенный launch context; никаких caller-supplied principal/role/work overrides. В production новые records проходят ту же закрытую DTO-проекцию — иначе добавленный help будет отвергнут старым DomainError или появится новая утечка.

L1 — только одна выдача при старте/фиксированное окно, не обновление на каждый describe. В прототипе L1 явно not_implemented, а не выдуманный агрегат. L2 не меняется; L3 отсутствует. Происхождение доступного клайма сохраняется по O2, но из него не следует доступ к исходной ветке/произвольным deps/head. Timing принятие не заявлено: сохранены 50+50 замеров отказа, без заранее согласованного порога это только описательная статистика.

## 5. Сборщик — не обход допуска

Вход: branch, тип, текст, явно заполненная semantic metadata, reason/origin_version/requirement_refs и **явный** basis[]. Сервер берёт служебные поля из доверенного binding, проверяет branch и каждый basis ДО lookup, пинит только явно указанные видимые ревизии, кодирует неизменённые UTF-8 байты в base64, валидирует, canonicalizes dom-c14n/v1 и считает стабильный key/digest. Не сочиняет evidence, rationale/attribution и не выводит зависимости из скрытого графа.

Выход: unsigned пакет, intent_digest, dependencies, привязанный author/root, assembler=server и reviewed=false. Автора связывает исходный normalized submit; сервер не притворяется подписантом автора. Draft read-only и сам ничего не подаёт. Дальше прежние submit → независимый review → admit, включая stale и digest gates.

Повтор одинакового draft при неизменном видимом основании даёт те же байты/key. При изменении основания получится новый пакет; потерянный submit/admit ответ повторяется **точным прежним пакетом**, не регенерацией по новой ревизии. Сохранены L1+L2: неверный digest даже с существующим admit key получает DIGEST_MISMATCH, легальный потерянный ответ возвращает старую квитанцию без новых фактов. Draft pins — снимок, не обещание отсутствия гонки; admission CAS/stale остаются решающими.

## 6. Измеримый холодный старт

Критерии записаны `criteria.json` ДО прогона: <=8 calls, source reads=0, guesses=0; старт → кандидат → увидеть в resume → осмысленный отказ. Свежий subprocess `cold_agent.py` не импортирует mockup, получает только authenticated launch JSON по stdin и wire ответы. Audit hook запрещает открытие mockup/fixtures. Для самого сценария не читает проектные файлы, не считает hash/base64.

1. tools/list.
2. dom_describe из launch.tool_entry; сверить binding с launch.
3. dom_init с describe.init_arguments.
4. dom_draft_claim с grant[0], decision example и заданным текстом.
5. dom_submit точного payload/receipt.
6. dom_resume той же granted ветки: candidate id найден в pending, claims=[] ожидаемо.
7. dom_submit с заведомо неверным schema_version: REJECTED с field errors и help.

Получено 7/8, 0/0, 0/0. Сырой transcript: `cold_start_result.json`. Original path блокирован уже до доступа к рабочим значениям; поэтому «сэкономлено ровно N вызовов» было бы выдумкой. Убраны категории действий: исходники/fixtures, угадывание параметров/схемы, ручные base64/JSON/hash/key/deps. Отдельный детерминированный агент — проверка достаточности интерфейса, не доказательство обобщения на произвольную LLM.

## 7. Контроли и неустранённые риски

38 исполняемых контролей: no-write draft; детерминизм; submit/admit legal retries; changed payload same key; missing/forged receipt; подмена principal/root/grant/policy/task/baseline/instance/session; foreign dependency; existing foreign == absent denial; невозможность probe-input в describe; неизвестная metadata; отказ self-review/author admit; policy hint; wrong work/instance; no-launch E1; hidden-state descriptor equality; explicit basis; independent admission; wrong-hash cached replay; stale admission; E2 admit receipt; malformed REJECTED not pending; O2 provenance; IMMUTABLE update refusal. Примеры всех семи типов проходят валидатор сборщика.

**Унаследованный дефект:** synthetic rejected latest review остаётся в existing pending (count до=1, после=1, item.state=REJECTED). Корень admission.py:514,546–568; доказательство `inherited_defect.json`. Решение заказчика не менять; устранение передать смежной части, не заявлять общий pending contract исправленным.

Не проверены: live auth/host gate/E3, expiry/revocation, настоящий baseline importer, неизменяемость sidecar как DB instance, production closed DTO для новых ответов, сетевые side channels и динамические declarations. Outage-policy не ослабляется: вне базы допустимы чтение/черновики с обязательной регистрацией; материальный допуск требует базы. Сам журнал outage здесь не реализован. O3/delivery engine не тронут, его переаттестация не заявлена.

## 8. needs_user и стыки

**NU-AN009-UD02:** пустой accepted baseline: reject authoring launch до импорта либо выдать NO_BASELINE и разрешить только явно выбранный provisional/draft режим без покрытия/готовности. Меняется содержимое допустимого запуска, а не уже принятый E1 факт выдачи пакета. Если выбора нет — вопрос открыт, production-приёмки empty baseline нет. Последствия/затронутое/отказ и варианты — JSON needs_user[0]. Прототип не выбирает за заказчика.

AN011: интерфейс project_contract(scope, revision) возвращает scoped объявленные requirements/branches и baseline pins. AN009 их описывает, не проектирует объявление. AN010/AN012: candidate read/review и stale remediation здесь не реализованы. Внутренний reviewer в extra controls — доверенная SIMULATION identity, не решение H10.

## 9. Файлы и воспроизведение

- `artifacts/ANALYST_AN009_COLD_START.json` — контракт результата.
- `reports/ANALYST_AN009_COLD_START.md` — этот отчёт.
- `runtime/AN009/{source_ledger.json,criteria.json,baseline_reproduction.json,wrong_project_reproduction.json,cold_start_result.json,negative_controls.json,extra_controls.json,inherited_defect.json,type_examples.json,timing_observation.json,validation_receipt.json}`.
- `runtime/AN009/{prepare.py,transport.py,endpoint.py,cold_agent.py,run_checks.py,extra_checks.py,assemble.py,validate_an009.py}` и собственный snapshot/runtime.

Из project CWD, чистый PYTHON* env, Python=`E:/opencode_harness_portable/.venv/Scripts/python.exe`, ключи `-I -B`: run_checks.py → extra_checks.py → assemble.py → validate_an009.py. prepare.py используется один раз перед прогонами; повтор после финализации переобъявит preregistration и не является историческим доказательством первоначального порядка.

Валидатор проверяет три priced options, прототип+негативы, file:line roots, исходники без изменений и cold steps; 6 мутаций должны отклоняться, включая опцию без цены, рекомендацию без прототипа, прототип без негативов, немаркированное изменение принятого решения и отсутствие current/baseline шагов.
