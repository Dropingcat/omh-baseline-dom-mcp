# AN011 — проект объявляет требования и ветки (H7)

## 0. Что проверял и что оказалось
**DONE_WITH_LIMITS; product_acceptance=false; is_approval=false.** H7 воспроизведён на частной неизменённой копии. Полный digest исходного продукта: `3cd21d96ff2f83f014f00c3fdf5b21c6ef94c26525385ef6a014365387d8aad0` — совпал с 3cd21d96 из пилота.

- Даже при launch-grant ZX `dom_resume ZX` → **NO_SUCH_BRANCH**; объявляющего инструмента нет → **UNKNOWN_TOOL**; claim с applicability ZX → **REJECTED / INVALID_BRANCH**.
- Более опасная половина: требование CLIENT-ACCEPT в существующей AA **проходит submit → review → admit**, но residual по-прежнему содержит только R1/R2. Набор не только фиксирован: отсутствует проверка принадлежности requirement_refs объявленному реестру. Это слепая зона покрытия, а не честный отказ неизвестному требованию.
- На экспериментальной копии новый проект прошёл объявление ZX + CLIENT-ACCEPT, независимый симуляционный review/admit, claim/review/admit и увидел покрытие в resume. **10 публичных вызовов**, без чтения фикстур, хеширования и сборки envelope/base64 агентом-симулятором. Готовность владельцу осталась false: сходимость и доставку не подделывали.
- Контроли: **38/38** (позитивные и негативные вместе). Это эксперимент, не независимый аудит и не приёмка продукта. Предоставление baseline/grant и аутентификация симулированы; общий H6 остаётся зависимостью AN010.

Сырьё: `runtime/AN011/reproduction_raw.json`, `cold_start_raw.json`, `negative_controls_raw.json`. Критерии сохранены в `criteria.json` **до первого запуска прототипа**; последовательность отражена вызовами инструментов. Это не внешний нотариальный timestamp.

## 1. Источник истины и полномочия
OMH владеет планом, задачами, приёмкой, закрытием и выдаёт исходное намерение с точным branch/task-ref. DOM хранит **допущенную базлайновую проекцию** этого плана и историю её политик. Заказчик выбирает открытые правила. Независимый проверяющий принимает изменение baseline. Автор/LLM-куратор может предложить, но не принять себя. Branch ZX — код ветки заказчика; ZX001 — task reference, не автоматически новая ветка. Прототип не создаёт ни OMH task, ни грант.

Объявление → кандидат с точным digest → чтение проверяющим → независимый review → атомарный admit policy version + head + transaction + outbox. До admit новой головы ZX нет. После изменения политики старые факты сохраняются побайтно, но их покрытие явно noncurrent.

## 2. Корни в коде
- `mockup/fixtures/__init__.py:4-9` — **WORK/TASK/POLICY/package**: One synthetic work/task and a fixed digest encode R1/R2 and AA/AB; not a mutable project registry.
- `mockup/admission.py:74-86,103-110,155-160,218-224,251-253` — **Service.__init__/scope/init/submit/admit**: Grant comes from launch context; all material claims compare against module POLICY/TASK, and outbox targets TASK globally. Declaration authority and branch/task mapping do not exist.
- `mockup/dom_contract.py:77-79,97,119-120` — **validate**: Operations only claims/append; dependencies, applicability and exclude branches explicitly enumerate AA/AB.
- `mockup/storage.py:49-59,126-133` — **Store.initialize**: Binding immutable; only AA/AB heads seeded, no declaration/version tables. Final user_version=2 stamp needs explicit evolution for production policy migration.
- `mockup/projections.py:55-77` — **trace_branch**: Coverage iterates literal R1/R2 and checks only branch-head dependencies, not current criteria policy digest.
- `mockup/dom_contract.py:7,99-120; mockup/admission.py:157-165` — **validate/submit**: requirement_refs only checked as list field; declared membership not checked. CLIENT-ACCEPT claim is admitted in AA but never appears in residual: silent coverage blind spot.
- `mockup/server.py:36-137,247-275; mockup/ports.py:12-24` — **TOOLS/SIGNATURE/main/fixture_context**: No declaration tool or CLI --branches; programmatic Service branches argument is not a model-facing branch creation authority.
- `mockup/admission.py:291-320; mockup/public_dto.py:100-122,135-179` — **Service._trace/public DTO allowlists**: Master convergence assumes AA/AB; new schema/receipt fields must be explicitly added to closed public projection, not merged as arbitrary metadata.

## 3. Четыре варианта разной цены
| Вариант | Изменения и цена (оценка LOC продукта / тестов) | Что покупаем и чем платим |
|---|---|---|
| A0 — не делать | 0 / 0 | Нет миграции, но реальный новый проект не начинает работу; слепая зона requirement_refs остаётся. |
| A1 — reviewed manifest при доверенном запуске | 180–320 / 120–220 | Минимум runtime API; каждое расширение требует доверенного импорта/перезапуска. Нельзя просто менять immutable binding. |
| **A2 — reviewed baseline delta** | **500–850 / 250–450** | Динамический путь в проекте без выдачи прав через модель. Новые версии, CAS, scope-first, отдельная интеграция миграции/DTO/доставки. Рекомендуется для следующего инженерного среза, не считается разрешением внедрения. |
| A3 — специальные claims в control scope | 650–1000 / 350–550 | Общая submit/review/admit модель, но рекурсивный bootstrap, новые типы и риск глобальной служебной ветки-оракула. |

Точные file/function, новые поля/коды, миграции, влияние на H и безопасность **для каждого варианта** заданы в JSON `options[]`. Это оценки, не измеренный production diff. Измеренный эксперимент: +168/−13 строк по 4 файлам частной копии; отдельно harness/отчёты в эту цену не включены.

## 4. Рекомендуемый минимальный жизнеспособный срез
1. Доверенный launcher резервирует точный код одной ветки и task-ref. Пока нет signed namespace capability, сам агент не расширяет grant.
2. `dom_declare_baseline` предлагает одновременно эту ветку и одно требование. Вход включает `expected_policy_digest` (null только для собственного пустого reserved baseline), точный plan-ref и ключ повтора.
3. Проверяющий читает полный разрешённый declaration-кандидат и одобряет точный digest. Admit проверяет distinct root, reviewer, текущий parent policy, collision и идемпотентную привязку. Fork не переписывает победителя.
4. `dom_claim_text` — **экспериментальная интерфейсная заглушка зависимости AN009**, а не проектирование общего H8: только один decision-тип, сервер строит payload. Клайм получает своё объявленное requirement_ref и policy pin.
5. `dom_resume` считает только требования текущей допущенной политики ветки. Старый accepted claim остаётся видимым с происхождением, но при смене policy перестаёт засчитываться; CRITERIA_NOT_CURRENT не исчезает молча.

**Policy:** immutable genesis binding остаётся исходным. Пользовательский token — branch-scoped digest версионированного manifest с parent; внутренний глобальный chain/root не раскрывается узкому grant. Иначе изменение скрытой ветки меняло бы глобальный публичный хеш и становилось сигналом существования. Внутренние зависимости и full head maps не фильтруются в хранилище ради удобства: фильтрация только public view. В прототипе AA/AB остаются legacy v0, ZX получает v1, затем v2. Актуальная accepted поддержка под v1 становится явно noncurrent при v2; old reviewed candidate → STALE_REVIEW.

**Миграция:** production-срез должен сохранить исходные binding/claims/candidates/reviews/created_at, v2 индексы и scope-bound idempotency; добавить append-only registry. Важно: `Store.initialize:133` сейчас безусловно ставит user_version=2. Нельзя объявить v3 и оставить этот код: требуется monotone version gate + отказ несовместимому читателю либо отдельный policy-schema marker. Прототип только добавляет экспериментальные таблицы и проверяет, что v2 marker остаётся 2; **не утверждает реализацию миграции**. Необъявленные legacy requirement_refs сохраняются как факты с явным unmapped blocker, не подгоняются под новые требования.

## 5. Холодный старт: измерение и ограничения
`cold_start.py:actor` получает только RPC и описания инструментов. AST-проверка запрещает импорты, file/hash/base64 helpers в actor. Каждый вызов запускает новый bridge-процесс: восстановление не зависит от Python-памяти. Служебный harness запускает процессы/пишет результаты; это не действие агента. План-текст и выбранное имя требования — пользовательское намерение, branch/task/digest — из ответа describe, все candidate/review IDs — только из ответов DOM.

1. `author:dom_describe` → DESCRIBED
2. `author:dom_declare_baseline` → RECORDED_DECLARATION
3. `reviewer:dom_read_declaration` → DECLARATION
4. `reviewer:dom_review_declaration` → DEMO_REVIEWED
5. `reviewer:dom_admit_declaration` → DECLARATION_ADMITTED
6. `author:dom_describe` → DESCRIBED
7. `author:dom_claim_text` → RECORDED_CANDIDATE
8. `reviewer:dom_review` → DEMO_REVIEWED
9. `reviewer:dom_admit` → DEMO_ADMITTED
10. `author:dom_resume` → RESUMED

Убираются чтение fixture-констант, ручной расчёт policy hash, ручная сборка base64/envelope и правка исходников для нового кода. Исходный путь **невыполним**, поэтому «минус N вызовов» честно не определён. Цена — 10 вызовов, review handoff и доверенное предварительное резервирование. Это scripted simulation, не измерение времени/когнитивной нагрузки настоящего LLM, не MCP wire E2E и не решение H1/H6/H10.

## 6. Негативы, принятые решения, межкарточные стыки
- Чужая существующая и чужая отсутствующая ветка → одинаковый SCOPE_DENIED, grant не растёт; reviewer не читает чужой declaration payload. Скрытая QX меняется, видимый ZX descriptor/token неизменен. Это функциональная эквивалентность; **тайминговую невыводимость не доказали**, L1/L2 механизм сигналов не реализовывали и L3 не добавляли.
- Fork одного ID с другим содержимым блокируется и на resubmit, и при допуске конкурентного кандидата; исходная принятая версия не переписывается. Семантическое/межветочное автообнаружение — не этот прототип.
- Нет review / одинаковый root / подмена digest до replay / чужой task-ref / неизвестное требование — отказ без изменения SQL-строк. Exact retry даёт ту же квитанцию без новых строк.
- Смена критериев не переписывает accepted claims/events и не маскирует устаревание. Добавленный критерий имеет MISSING_COVERAGE. Политический recheck консервативен: все старые branch reviews noncurrent, пока не выбран granular impact.
- Registry UPDATE/DELETE/REPLACE/IGNORE запрещены; injected fault после registry insert откатывает transaction/head/outbox/registry вместе; исходная event chain CHAIN_OK, user_version=2. Ack нет — O3 не объявляется проверенным.
- Первый harness ошибочно требовал именно IMMUTABLE там, где раньше сработал CHAIN_INTEGRITY. Сохранён `negative_controls_attempt1.json`; исправлено ожидание допустимого отказа, **не защита**.

AN009 интерфейс: scoped registry view + provision/template receipt. AN010: типизированный exact candidate view и реальная независимость. AN012: current criteria context и новый review после refresh. Общий master/converge в эксперименте UNKNOWN; никак не заменяет UD-06. Общий RS009 rejection/pending контракт не реализован для policy candidates; не выдаём это за полное ведение backlog.

**Принятые защиты не ослаблены предлагаемым A2.** Самоприёмка и публичный глобальный registry в альтернативах явно помечены как меняющие принятое решение и не реализованы. При недоступности DOM production материальные policy changes обязаны останавливаться; черновики/чтение/внебазовые артефакты разрешены по NU-AU006-01. Этот деградационный слой в прототип не входил.

## 7. Карточки заказчику (не решения аналитика)
### NU-AN011-01 — Authority: reviewed DOM baseline delta from OMH-owned plan
**Что меняется:** OMH initiates branch/task references; DOM records independently admitted baseline projection, not a second plan owner.
**Почему:** A model-facing declaration must not create planning authority or grants.
**Затронуто:** OMH plan/branch task map, DOM declaration review, curator independence
- **A:** OMH-owned intent + independent baseline reviewer admits; recommended.
- **B:** Owner preapproves manifest per launch; no dynamic declaration, lower cost.
- **C:** Author self-admits declarations: changes accepted independent-review decision; not implemented.
**При отказе:** Keep read-only static registry; H7 remains.

### NU-AN011-02 — Exact reserved branch grant or namespace creation grant
**Что меняется:** Who reserves the customer branch code and how server gains its grant.
**Почему:** Declaring ZX cannot authorize access to another work or branch.
**Затронуто:** trusted launcher, grant issuer, restart/hot reload
- **A:** Exact code and task ref reserved by OMH/owner at launch; one restart for future grants; prototype.
- **B:** Signed create-within-namespace capability with explicit issuer, expiry and revision; less redeploy, more security code.
**При отказе:** No automatic grant expansion; branch can be admitted but inaccessible to non-granted agents.

### NU-AN011-03 — Public scoped policy token vs global policy root
**Что меняется:** policy_digest identifies pinned branch criteria version; internal global registry root is not sent to narrow grants.
**Почему:** Rotating one public global hash on hidden declaration is a repeat-query existence signal, even without hidden names.
**Затронуто:** dom_init compatibility, baseline packets, candidate review pins, O1 and anti-oracle
- **A:** Per-branch public version/digest plus internal global append chain; old digest retained as v0. Recommended/prototype.
- **B:** Entire project registry public to every principal; requires separate explicit authorization/declassification decision, not a harmless implementation simplification.
**При отказе:** Keep global digest internal and expose opaque scoped receipt via AN009; API adaptation needed.

### NU-AN011-04 — UD-02: empty baseline and first declaration
**Что меняется:** Whether reserved empty project permits proposing baseline delta without accepted requirements.
**Почему:** Bootstrap cannot require the criterion it is itself creating.
**Затронуто:** AN009 start, coverage readiness, outage reconciliation
- **A:** Explicit NO_BASELINE/nonready; allow only reviewed bootstrap declaration, ordinary claim materialization blocked until admission. Prototype conditional behavior.
- **B:** Reject all material paths until owner imports initial plan manifest; one more provisioning step.
**При отказе:** Report NO_BASELINE; do not infer coverage or allow self-bootstrap.

### NU-AN011-05 — Policy addition: conservative branch recheck or granular impact
**Что меняется:** Which existing reviews become noncurrent after a new requirement.
**Почему:** Old facts must remain readable, but coverage cannot silently use outdated criteria.
**Затронуто:** O1, AN012 stale reasons, revalidation workload
- **A:** Every claim reviewed under earlier branch policy becomes visibly noncurrent; easiest safe default, prototype.
- **B:** Separate per-requirement criteria digests and independently reviewed no-impact mapping retain unaffected support; more complexity.
**При отказе:** Conservative noncurrent, preserve all immutable claim bytes and policy lineage.

### NU-AN011-06 — UD-06: convergence under divergent AA/AB policies
**Что меняется:** No automatic common-policy winner; decide admissible vector of branch policy digests and who reviews convergence.
**Почему:** Meaning/text convergence is curator judgement, not equal hashes or a boolean. Direction LLM curator already accepted; execution remains open.
**Затронуто:** master readiness, criteria_digest, curator union visibility, AN012
- **A:** Retain independent branch versions; curator proposes vector+criteria+evidence, independent reviewer admits; master UNKNOWN until agreed contract.
- **B:** Require coordinated reviewed migration to one shared policy before convergence; more blocking but easier criteria.
**При отказе:** Keep branches nonconverged/UNKNOWN, never close master.

### NU-AN011-07 — Fork detection scope and resolution
**Что меняется:** Same branch+requirement ID with different content is a structural declaration fork; semantic/cross-branch forks remain curator proposals.
**Почему:** A collision must not choose the last writer. Unrelated hidden versions cannot be revealed to a narrow grant.
**Затронуто:** DECLARATION_FORK, curator evidence, L1/L2 policy
- **A:** Exact target-scope identifier/content collision only, retain both proposals; independent resolution required. Prototype.
- **B:** Add asynchronous semantic fork candidates from curator union view; input/model/prompt provenance and independent review required, never L3 query signals.
**При отказе:** Reject conflicting material update; keep original accepted version and both candidate evidences, no silent winner.

## 8. Границы доказательства и следующие гейты
Результат аналитический: прототип работает в изоляции, но worker/reviewer/auditor production-цепочка ещё нужна. Нет реального issuer, сети, Git, живого OMH, платных вызовов или субагентов. Продукт, tests, tech_debt, configs, ORIENT/home не менялись. Не исследованы concurrency/kill, тайминги и полный historical policy export. JSON bridge использует domain outputs; отдельные новые closed DTO/schema и MCP-list маршруты должны быть реализованы и проверены перед вводом. Ни master, ни задача заказчика не закрыты.

Скрипты: `reproduce.py`, `cold_start.py`, `test_prototype.py`, `validate_an011.py`. Повтор контролей: `env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP E:/opencode_harness_portable/.venv/Scripts/python.exe -I runtime/AN011/test_prototype.py negatives_fresh` (имя каталога должно быть новым). Рабочий каталог — P. Cold-start повторно запускать с новым каталогом cold/ через копию runner/bridge либо после явного изолированного reset, не поверх исходного опыта.
