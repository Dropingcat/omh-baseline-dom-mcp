# AA001 — анализ требований и границ макета DOM ↔ OMH

**Роль:** analyst/general; не разработчик и не принимающий.  
**Статус:** PARTIAL — анализ подготовлен; реальные global-work binding, независимая host identity и интеграция не доказаны. Это не вердикт о готовности продукта.  
**Происхождение аналитических клаймов:** каждый маркер `[AA@v1:ID]` означает `origin_branch=AA`, `origin_version=AA001-analysis-v1`; ID аналитического клайма отделён от AA001. В JSON каждая запись baseline/findings имеет явный `origin_branch`; версия отчёта указана отдельно. Это аналитические записи, не допущенные клаймы новой DOM-базы. Для будущей DOM явные origin branch/version обязательны непосредственно в каждом клайме.  
**P:** `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp`.  
**H:** `E:/opencode_harness_portable`. Все относительные evidence-пути ниже считаются от H. OMH-пути приведены абсолютно.

## 1. Итог и место в общей работе

[AA@v1:S01] Подтверждённый baseline не пересматривается: OMH управляет планом и закрытием; одна база на глобальную работу; стабильный отдельный ID и явные origin branch/version на каждом клайме; исходное тело/цитаты/старые ссылки неизменяемы; комментарии/свойства только append-only с автором, серверным временем, версией и причиной; обязательна независимая смысловая приёмка и транзакционная прослеживаемость. Основания: `P/REQUIREMENTS.md:19–46`; атомарная схема — проектное предложение `:50–55`, а не уже работающая реализация.

[AA@v1:S02] Наиболее опасная подмена — принять наличие writer DOM, todo/checkpoint и JSON-трекера за готовую общую транзакционную базу с приёмкой. Прочитанный код этому не даёт оснований: writer нормализует исходный текст и перенумеровывает ID, research builder редактирует данные на месте, baseline_tracker ставит done по строковым статусам. Конкретные локаторы — F03–F05 ниже.

[AA@v1:S03] **Где я:** AA001, ветка AA; WS/TD-ID и фактическая OMH-задача не установлены, не придуманы. Связь с архитектурой: требования K0 contracts/journal → K3 bounded context/contracts → K4 plan/contract/executor, но DOM обслуживает существующее планирование OMH, не копирует его. Основания: карта AA001:25–39; мастер-план K0/K3/K4. **Остаток нити:** глобальное число открытых WS/TD не измерялось — доступ к реестрам и пользовательским записям запрещён. Локальный остаток представлен вопросами Q01–Q12 и будущими проверками AC01–AC15, не фиктивными счётчиками закрытых задач.

[AA@v1:S04] Следующий полезный шаг родителя: передать ресерчеру этот MD и JSON, сначала Q01/Q02/Q05–Q07/Q10; после evidence зафиксировать контракт макета и отдельную техкарту разработчика. Параллельный ресерч без этой сводки не заменяет зависимую часть цепочки (08_ANALYST_RESEARCHER_CONTRACT.md:48–52). AA001 не запускает делегирование, сервер, CLI моделей или Git-операции.

## 2. Исходные требования заказчика — дословно, без редакторских исправлений

[AA@v1:SOURCE01] **Источник:** `P/REQUIREMENTS.md:9` (первое уточнение). Далее сохранён исходный текст, не аналитическая переформулировка:

> что нам важно- связать  блок планирования OMH  с блоком дерева дум свойствами приписками чтобудут делаться в момент исполнения задачи или подзадачи- полная прослеживаемость с транзакциями( базово ) важно иметь прямую сшивку и хождение туда сюда информации.  и кухи для агента когда он проверяет чт сделано по ветке задачи и что осталось

[AA@v1:SOURCE02] **Источник:** `P/REQUIREMENTS.md:13` (второе уточнение):

> да  мы не плодим самостоятельные сущности делаем  удобный инструмент для  контроля базлайна ГЛОБАЛЬНОЙ работы к которой агент возвращается не раз и не два.  и ведет больше одной ветки разработки. предусмотри  порты для гита и контроля весий и веток разаботки- т.е.  утверждение в какой ветке шло  версия -  сразу предусмотреть генерацию веток  и их слияние - мастер закрывается когда все сшлось - по умолчанию новая ветка   боковая  дочерние номеруюся цифрами  ветки буквами. две буквы три цифры.  у каждого клайма есть айди- как в dom  для писателя  - задачи буду как для кодинга , исследований или писательства.  будет как единая база  информации в нутри задачи дял  суб агентов. где в тех карте на задачу из OMH прописывается  ветка и информация которую он может использвоать. - так же  правила внесения  данных  - ссылки текст.  сами утверждения- участки кода- формулы  решения. концепты-  базово два блока- непосредственно утсверждение - и блоки коментариев и свойсвт . блок утверждения не редактируется ни когда-  он только может быть переведен в арзивное состояние.

[AA@v1:SOURCE03] **Источник:** `P/REQUIREMENTS.md:17` (третье уточнение):

> тюе должна быть цепть независимой приемки- формирование плана сессии OHM -  инициализация агентом DOM ( по аналогии с OHM)   создание файла и базы и записи входящих данных с заданными требованиями от оркестратора ( так ведь происходит в OHM?)  если требования не выполнены  возвращается сообщение чтоне внесено и какие требования ко входу.  - редактирование ЦИТАТ- первой части клайма запрещено это исходник-  ссылок тоже  можно только вносить. поэтому требования к внесению велики . комментарии тоже только добавляются с указанием версии времени  и приыня-  это храниться в свойсвах - дополни и дай критику0 предложи лучший работающий вариант без протечек при необходимости анализ существующих плагинов для заимствования. - по транзаукии ту твероятно хеши нужны как и в томже OHM это реализовано?

[AA@v1:SOURCE04] **Источник:** карта AA001:9–11 и переданный контракт, последующее разрешение:

> естественно отда база   но предусмотри внутри на каждом калйме маркер ветки. пердлагаю запустить ресерчера и аналитика для закрытия вопросов  которые ты сформулировал и собрать  начальные документы и макет- создай директорию проекта в харнесс и приступай к планироавинию и сборке мактеа используй карты технологические для субагентов

[AA@v1:SOURCE05] По переданному контексту разрешение fallback звучало дословно: «проверь три модели GLM DEEPSEEC FLINT  по порядку  если ни одна не сработает то через субаентов гермес с правилами  из харнесс». Факт предыдущих GLM/DeepSeek limit и успешного Flint smoke без содержательных файлов принят только как вход родителя; здесь не перепроверялся. Клиенты моделей и ключи не искались.

## 3. Карта прослеживаемости baseline

| Клайм | Что нельзя потерять | Точное основание | Проверка будущего макета |
|---|---|---|---|
| [AA@v1:B01] | OMH — единственный владелец плана/закрытия; DOM не второй task manager | REQUIREMENTS:19–25,85–88 | AC13, отсутствие close/write статусов со стороны DOM |
| [AA@v1:B02] | Одна база глобальной работы, повторные сессии и параллельные ветки; YAML — производный срез по предложению, не вторая истина | REQUIREMENTS:13,22,38,52 | AC01, AC12 |
| [AA@v1:B03] | У каждого claim отдельный стабильный ID, явные неизменяемые origin branch/version; AA001 = AA + 001, не claim ID | REQUIREMENTS:29,37–38,43–44 | AC10–AC11 |
| [AA@v1:B04] | Тело/цитаты/старые ссылки не изменять и не удалять; добавление новой ссылки отдельно; исправление тела новым claim | REQUIREMENTS:13,17,30–36,59–62 | AC09–AC11 |
| [AA@v1:B05] | Comment/property append-only с автором, серверным временем, revision/version и причиной; архив — событие, не стирание | REQUIREMENTS:17,34,36,61–62 | AC09–AC10 |
| [AA@v1:B06] | Независимая смысловая приёмка отдельно от формальной; полный безопасный отказ неполного ввода | REQUIREMENTS:17,35; DESIGN:29–41 | AC02–AC05 |
| [AA@v1:B07] | Двусторонняя сшивка OMH/DOM и trace требовалось/сделано/проверено/осталось | REQUIREMENTS:9,24–25,84–88 | AC08, AC12–AC13 |
| [AA@v1:B08] | Порты Git/version/create/merge предусмотрены; DOM branch не Git ref; dirty имеет собственный снимок; merge не смысловая приёмка | REQUIREMENTS:13,42–46,69–74 | AC11, AC13; live Git отдельно |
| [AA@v1:B09] | Общее ядро кодинга/research/writing; ограниченный техкартой доступ и правила по типу данных | REQUIREMENTS:13,23,31,46,78–80 | AC02, AC12, AC14 |
| [AA@v1:B10] | Атомарность локального admission, явный конфликт; не общая транзакция с Git/OMH; видны незавершённые операции | REQUIREMENTS:53–55,87–88; DESIGN:35–37,54–65 | AC05–AC08 |

[AA@v1:B11] Обозначение DESIGN здесь и далее означает `P/ADMISSION_AND_INTEGRITY_DESIGN.md`. Его SQLite/outbox/digest схема — **PROPOSED**, не пользовательское утверждение о существующей реализации. Карта не сокращает исходные слова: дословный слой сохранён выше, требования 19–46 прослежены отдельно, инженерные решения 48–92 не повышены до принятого baseline.

## 4. Findings: критичное, недоделанное и риски

### Critical

[AA@v1:F01] **Пробел identity глобальной работы.** В REQUIREMENTS:97 точный OMH-контракт оставлен открытым. OMH completion_store.py:228–260 создаёт checkpoint из session-owned todo, `checkpoint_id` и binding; team_tool.py:93–105 использует host session и durable session. Из этого не следует стабильная глобальная task identity через новые сессии/перестановки todo. Нельзя сделать session_ref, checkpoint_id или индекс пункта глобальным ключом по догадке. **Путь закрытия:** Q01. **Блок:** live binding, не синтетический mock.

[AA@v1:F02] **Независимость и защита от обхода не доказаны.** В `C:/Users/Arhys/AppData/Local/hermes/plugins/omh/tools/team_tool.py:81–102` действительно есть запреты board-worker/delegated-helper и session_required, но нет доказательства разграничения клиентов нового DOM MCP. В DESIGN:39 прямо предусмотрен `INDEPENDENCE_NOT_ENFORCED`, а :73 указывает обход через общие файловые инструменты. Роли строками и caller-supplied reviewer_id недостаточны. **Путь закрытия:** Q02/Q09. **Блок:** защищённый допуск и заявление об изоляции; demo-review разрешён только с явной маркировкой симуляции.

[AA@v1:F03] **baseline_tracker — не журнал допуска и не предикат закрытия master.** Прямое чтение `scripts/orchestration/baseline_tracker.py`: :71–82 превращает ошибку чтения в пустой tracker; :85–91 делает replace одного файла, без OCC/lock всей read-modify-write операции; :154–165 и :118–137 отдельно пишут tracker и task snapshot; :238 заменяет status; :254–262 доверяет переданным merged и ставит done, в том числе при пустом списке веток. Повторный init не сверяет agent/dispatcher (:149–152). Это статические свойства кода, не эксперимент с потерей данных. **Путь закрытия:** Q05/Q10. **Решение:** заимствовать форму checkpoint, не подключать writes этого tracker как вторую систему истины DOM/OMH.

### Major

[AA@v1:F04] **Writer-образец не обеспечивает точность и стабильность.** `templates/writer-dom-dissertation.yaml:56–70` содержит id/text/kind/evidence/verification, но не per-claim origin branch/version. `scripts/writer-core/writer_core/dom_builder.py:198–201` сжимает whitespace; :204–232 назначает `C-{i:03d}` по позиции. Поэтому перенос существующей функции как write path изменит исходные байты и не докажет сохранение ID при переупорядочивании. Читались только указанные части модуля, вывод не распространяется на все его функции. **Q04/Q06; AC09/AC11.**

[AA@v1:F05] **Research builder изменяем и его OK не является истинностью.** `scripts/tools/dom_builder.py:66–82` заменяет citations, sources и text, :93–112 перезаписывает citations из cmap. В :128–142 статус OK вычисляется из наличия списков. Это конфликтует с новой immutable/admission моделью, а не обязательно ошибка старого инструмента в его прежнем назначении. **Q06/Q07; исключить эти команды из DOM записи.**

[AA@v1:F06] **Покрытие бакетов не равно исполняемой приёмке всех ролей.** В `config/bucket_contracts.json:4–109` действительно есть code/research/writing с разными validators/done_when. В `scripts/code-factory/contract_validator.py:248–280` analyst/researcher отсутствуют в VALIDATORS, неизвестный agent_type отвергается, written_by — проверяемая строка данных. Она не аутентифицирует независимого принимающего. **Q03; AA001 не маскировать под worker.**

[AA@v1:F07] **Планируемые K0/K3/K4 не объявлять подключёнными.** Мастер-план:3 имеет статус PROPOSED; :51–62 задаёт schemas/journal; :100–138 задаёт contracts/planning. Прямая read-only проверка `Path('E:/opencode_harness_portable/harness_context').exists()` вернула false. Это означает только отсутствие данного корня здесь, не отсутствие реализации во всех старых ветках/worktrees. Расширенный поиск `*journal*.py` дал нерелевантные каталоги; он не используется как доказательство полноты. **Q03; не обещать ready K0 journal.**

[AA@v1:F08] **OMH completion не выдаёт независимую приёмку.** Прямо перечитан `C:/Users/Arhys/AppData/Local/hermes/plugins/omh/completion_store.py:254–260`: acceptance=`model_declared_accepted`; :263–276 проверяет revision/environment/age; :279–296 оставляет completion.status=`not_verified` даже при complete declarations. **Q01/Q02.** Полезный pattern — exact binding и различение декларации/наблюдения, не готовый ADMIT для DOM.

[AA@v1:F09] **Атомарность, cross-session idempotency и transport новой DOM не испытаны.** DESIGN:3 и :31–37,54–65 описывает будущий протокол. OMH_CODE_REVIEW:13–18,36–40 — статический аудит другого пути egress с identity session/tool-call; здесь эти исходники не перечитывались и не выполнялись. Нельзя переносить exactly-once внешнего эффекта или готовый outbox из факта наличия digest/BEGIN IMMEDIATE. **Q05/Q08/Q11; AC05–AC08.**

[AA@v1:F10] **Сходимость и жизненный цикл пока только специфицируются.** REQUIREMENTS:37–45,72–74,87,96 отличает origin и applicability, подтверждает AA001 и оставляет правила выделения кодов. DESIGN:46–48,80–84 отделяет branch archive от общего claim и merge от приёмки. Смысловые конфликты, влияние архива на зависимости и полнота master требуют проверяемой политики. **Q04/Q10; AC10/AC13.**

### Minor / контрактный риск

[AA@v1:F11] **Общие шаблоны конфликтуют с локальной картой, но приоритет определён.** 08:48–52 ожидает post-audit APPROVE; :111 и :124–136 задают разные общие пути отчётов. shared/orchestration-thread-process:40–71 требует чтение/запись глобального контекста. Карта AA001:5,44–58 специально адаптирует предстартовую роль и разрешает только два project outputs. Поэтому APPROVE не придуман, общие реестры/`.kanban.db` не читались и не менялись; отчёты только в P/analysis. Новые TD-ID не назначались — findings передаются родителю, не регистрируются.

## 5. Карта «существует / подключено / проверено / предлагается»

| Клайм, механизм | Существует | Подключено к новой DOM | Что реально проверено в AA001 | Что предлагается |
|---|---|---|---|---|
| [AA@v1:E01] Writer YAML, claim/evidence/graphs | Да, файл 1–94 | Не доказано | Полное статическое чтение шаблона | Только совместимая экспортная структура + явные origin fields |
| [AA@v1:E02] writer_core claims_to_dom | Да, функции :198–232 | Не доказано | Нормализация и позиционные ID прочитаны, не запускались | Не использовать для immutable bytes/stable IDs |
| [AA@v1:E03] tools/dom_builder mutable commands | Да, :66–112 | Не доказано | Прямое чтение присваиваний | Не давать mutate API на принятую DOM |
| [AA@v1:E04] baseline_tracker | Да, весь модуль | Не доказано; подключать writes не рекомендуется | Статическая сверка read/replace/status/done, без запуска | Только идея checkpoint; собственная строгая storage transaction |
| [AA@v1:E05] bucket contracts | Да, весь JSON | Не доказано | Бакеты и имена validators перечислены в конфиге | Типовые требования поверх единого admission ядра |
| [AA@v1:E06] contract_validator | Да, registry прочитан | Не доказано | Нет analyst/researcher; string written_by ≠ identity | Не обходить неизвестную роль; отдельный согласованный контракт |
| [AA@v1:E07] K0 journal / K3 renderer / K4 universal chain | Целевые пункты плана; harness_context здесь отсутствует | Не доказано | План и точечная проверка пути | Ресерчер локализует существующее до reuse |
| [AA@v1:E08] OMH host guards и completion binding | Да, указанные исходники | Не доказано | Только team:81–102, completion:228–296 | Заимствовать pattern, проверить runtime capability отдельно |
| [AA@v1:E09] OMH egress digest/SQLite receipt | Описано во входном аудите | Не доказано | Вторичное evidence, не новый live прогон | Не путать host-call repeat guard с business idempotency |
| [AA@v1:E10] Новый DOM server / MCP / outbox / независимый ADMIT | В прочитанных документах только предложение | Не доказано | Продуктовый код не создавался, сервер не запускался | Отдельная разработка и AC01–AC15 |

## 6. Проектные решения с уровнем доказательности

[AA@v1:D01] **Baseline, не предложение:** сохранить OMH как владельца существующих задач/закрытия; один DOM baseline на работу; origin branch/version и неизменяемость каждого клайма. Evidence B01–B09. Новая таблица candidates/events/receipts — внутреннее хранение evidence, не новый реестр задач.

[AA@v1:D02] **PROPOSED:** разделить immutable claims/sources/links от append-only comments/properties/applicability/archive и вычисляемых проекций. Новая применимость не меняет origin; старую ссылку не «исправлять» заменой. Ошибка в теле → новый ID + replacement relation + архивное событие без потери. Evidence DESIGN:43–50, REQUIREMENTS:59–65. Для снятия неоднозначности branch archive в макете влияет на applicability, а глобальное архивирование требует отдельной явной операции/политики.

[AA@v1:D03] **PROPOSED:** один writer сервис, SQLite authoritative, YAML scoped export. В одной admission transaction: перепроверка identity/policy/expected branch revision/digest/dependencies, admission event, связи, revision, receipt, outbox. Состояние recorded candidate не admitted baseline; ревизии этих пространств не смешивать. Для общей базы определить branch OCC и глобальный event sequence; не подменять одно другим. Evidence DESIGN:9,31–37,54–61; Q05.

[AA@v1:D04] **PROPOSED:** идемпотентность по global-work/operation/key + digest, а не session/tool-call. Повтор после потери ответа возвращает прежнюю receipt; другой digest конфликтует. OMH delivery и YAML export после commit, состояния pending/ack/retry видны при resume. Нет обещания exactly-once Git/OMH. Evidence DESIGN:35–37,59–65, REQUIREMENTS:55,88.

[AA@v1:D05] **PROPOSED:** зафиксировать versioned digest contract и golden vectors. Хранить оригинальные байты отдельно от search-normalized текста. Не объявлять `sort_keys=True` RFC8785; не превращать формулу/точную десятичную величину в теряющий точность float. Цепочка хешей — контроль связности, не защита от переписи всей локальной базы или rollback без внешнего доверенного checkpoint. Evidence DESIGN:50,54–65; F04.

[AA@v1:D06] **PROPOSED:** fail-closed при неизвестной reviewer identity или scope. Прототип может показать state machine независимой проверки через явно тестовый host adapter, но не получает ярлык реальной независимости. Отдельные capability/OS-права — результат исследования и разрешения, не автоматическое следствие stdio. Evidence DESIGN:23,39,69–78; F02.

## 7. Вопросы ресерчеру — проверяемый контракт

| Клайм/ID | Вопрос | Достаточное evidence | Что блокирует |
|---|---|---|---|
| [AA@v1:Q01] | Какой существующий OMH global-work/task ID долговечен через новую сессию и перестановку todo? | Первичный код создания/lookup/lifetime + synthetic fixtures двух сессий одной работы и разных работ; mapping без второго реестра | Live binding; не mock |
| [AA@v1:Q02] | Как host подтверждает автора и отдельного принимающего для exact digest? | Реальные adapter kwargs/capabilities; негативные self-admit/forged reviewer/delegate fixtures; не строки role | Защищённый ADMIT; не demo state machine |
| [AA@v1:Q03] | Какие K0/K3/K4 и role validators реально есть и связаны? | Точные пути/символы и exists/wired/tested; разрешённая read-only сверка других веток при необходимости; unknown role отвергается | Утверждение reuse готовой цепочки |
| [AA@v1:Q04] | Как распределяются stable claim ID, origin, AA001 и applicability/archive без смешения с Git refs? | Collision/retry/reorder/merge fixtures; ID/origin неизменны; схема кодов и исчерпания диапазона, не переименование AA001 | Финальная ID/branch спецификация |
| [AA@v1:Q05] | Что атомарно при admission и каково поведение race/crash/lost reply? | begin/commit/rollback/unique constraints; fault-injection before/after commit, две конкурентные записи, read-back; идемпотентность новой сессии | Приёмка storage макета |
| [AA@v1:Q06] | Как сохраняются exact bytes и digest без потери Unicode/CRLF/единиц/точных чисел? | Версионированный контракт и golden vectors; повтор одинакового пакета, различие изменённого, старые байты неизменны | Приёмка immutable/digest макета |
| [AA@v1:Q07] | Какие обязательные поля у цитаты, решения, формулы, кода, данных, концепта? | Type→fields/error codes; неполные fixtures; все допустимые errors, accepted_count=0; DOI не выдумывается для авторского решения | Входная негативная приёмка |
| [AA@v1:Q08] | Какой OMH handler принимает evidence/result без автоматического закрытия? | Первичная schema/handler/права, exact-target read-back и transaction correlation; недоступность=pending | Live OMH write; в AA001 не вызывать |
| [AA@v1:Q09] | Какой scope реально enforced и как закрывается обход через файл/terminal/export/trace? | Threat model/OS права/capability boundary без чтения личных данных; error/count/search/trace/export fixtures; карантин утечки отдельно | Production изоляция, не локальные synthetic ACL tests |
| [AA@v1:Q10] | Как вычисляются глобальный остаток и смысловая сходимость при архиве, exclusion, stale evidence, pending outbox? | Requirement→claims→current checks матрица и контрпримеры done локально ≠ master ready, clean Git merge ≠ согласие | Сквозной trace/residual макет |
| [AA@v1:Q11] | Как доказать настоящий минимальный MCP handshake в установленном API? | initialize/tools list/tool call protocol log с version/correlation на synthetic data; разрешённые первичные API docs | Только ярлык MCP-connected |
| [AA@v1:Q12] | Как Git port показывает dirty/artifact snapshot и create/merge intent без изменения текущего repo? | Интерфейс и synthetic fixtures repo/ref/commit/dirty/digest; real create/commit/merge NOT_IMPLEMENTED до отдельного разрешения | Live Git; не mock port |

[AA@v1:Q13] Вопросы blocks_mockup=true в JSON означают **блокируют приёмку соответствующей функции исполняемого макета**, не чтение документов, проектирование или запуск разработчика. Исследователь должен вернуть pass/fail/not-tested по каждому вопросу, первичные локаторы и контрпримеры, а не общую рекомендацию. Если факт можно извлечь из исходников, он не превращается в REQUIRES_USER_DECISION.

## 8. Минимальный scope исполняемого макета — только PROPOSED

[AA@v1:M01] **Окружение:** отдельный sandbox с синтетическими входами, одна global-work binding, одна SQLite БД, логические AA и AB; AA001 трактуется как AA+001, claim IDs отдельны. Mock OMH ref явно синтетический. Не читать/копировать пользовательскую `.kanban.db`, не создавать новую доску или автономных агентов. Evidence: REQUIREMENTS:21–25,37–44, DESIGN:7–9.

[AA@v1:M02] **Последовательность:** init → неполный пакет/полный безопасный отказ → типизированный валидный immutable candidate → независимая demo-review receipt на точные digest/snapshot/revisions → atomic admission → read-back → повтор того же намерения/конфликт → append comment/property/link → перенос применимости AA→AB → scoped YAML/trace/остаток → сбой и resume. Реальный host-неподтверждённый ADMIT остаётся `INDEPENDENCE_NOT_ENFORCED`; demo receipt не production evidence.

[AA@v1:M03] **Минимальная модель данных (предложение):** binding существующей работы; immutable claim body с claim_id/origin_branch/origin_version/content_type/raw bytes/body hash; неизменяемые source/link records с locator/snapshot; candidate и review receipts; append events comments/properties/applicability/archive/replacement; revisions/transactions/idempotency/outbox; производные проекции. Comment/property event содержит author, server_time, version/revision, reason, claim_ref и при исправлении supersedes_ref. Не делать API произвольного SQL/update/delete/файловых путей.

[AA@v1:M04] **Одно ядро:** общий transaction/admission API для code/research/writing; fixtures exact quotation, собственное решение/концепт, код, формула и данные. Обязательность evidence зависит от типа: код — repo/path/snapshot, формула — предпосылки/обозначения, данные — метод/артефакт/единицы, цитата — exact fragment/locator. Нет отдельного DOM-движка для каждого контура. Evidence DESIGN:21–27, REQUIREMENTS:23,31,63–65.

[AA@v1:M05] **Что достаточно mock:** внешний OMH lookup/evidence delivery с pending/read-back квитанциями; Git metadata/create/merge intentions и dirty artifact snapshot; заданный тестовый identity adapter, который доказывает только алгоритм state machine. Реальный SQLite transaction/race/recovery и сохранение bytes/idempotency нельзя заменять нарисованными логами: это обязательные реальные прогоны будущего storage макета.

[AA@v1:M06] **Что требует настоящего MCP:** обнаружение и вызов tools клиентом, initialize/capabilities/tools-list/tool-call/response correlation на установленном stdio transport. In-process Python вызов или успешный JSON fixture не handshake. Внешняя OMH запись/полномочия требуют ещё собственного live gate; handshake сам их не доказывает. Q11/AC15 — отдельный этап, не текущая AA001.

[AA@v1:M07] **NOT_IMPLEMENTED/вне минимального доказательства:** production OMH write и close, реальные Git create/commit/merge текущего проекта, enforcement OS identity/sandbox, подпись и внешний доверенный checkpoint, migration личных DOM/БД, полнотекстовый продуктовый UI, автоматический fetch источников и бесконтрольный импорт YAML. Порты create/merge обязательно предусмотрены в интерфейсе, но мок не выдаётся за их исполнение. Отсрочка реализации не отменяет исходных требований.

## 9. Приёмочные действия и негативный чек-лист

[AA@v1:AC00] Все следующие тесты — **критерии будущей реализации, NOT_RUN в AA001**, не изготовленные результаты. `physical_evidence` для каждого теста дан и в JSON. Принимает независимый агент/родитель, не автор макета.

| Клайм | Действие / отрицательный вход | Ожидаемый результат | Физическое evidence будущего прогона |
|---|---|---|---|
| [AA@v1:AC01] | Init без поля; повтор init и новая сессия | При ошибке нет пользовательской базы/экспорта; повтор не перезаписывает; одна binding | Лог + inventory + read-back |
| [AA@v1:AC02] | Несколько ошибок type/locator/branch/scope в пакете | Все безопасные error paths/local IDs/required fields; accepted_count=0, baseline revision прежняя | Response JSON и before/after ревизия |
| [AA@v1:AC03] | Кандидат после formal PASS | Только RECORDED_CANDIDATE, не admitted snapshot | DB rows + scoped snapshot |
| [AA@v1:AC04] | Самоприёмка, forged reviewer, неизвестная identity | Fail-closed; demo review явно simulation | Назначение/capability и журнал отказов |
| [AA@v1:AC05] | Review одной версии, admission другой; движение policy/dependency | Stale/digest refusal, без partial admission | Receipt, revisions и отсутствие admitted event |
| [AA@v1:AC06] | Два writers одной branch revision, update другой ветки | OCC conflict без тихой потери; политика глобальной sequence явна | Двухпроцессный лог + invariant queries |
| [AA@v1:AC07] | Lost reply после commit, повтор в новой сессии, key с другим digest | Одна operation/прежняя receipt; несовместимый повтор отклонён | Count транзакций + equality receipts |
| [AA@v1:AC08] | Crash до/после commit, delivery до ack, ошибка export | Rollback до commit; после commit admission есть, pending восстанавливается; нет exactly-once обещания | Fault matrix + restart read-back |
| [AA@v1:AC09] | UPDATE/DELETE body/quote/link/comment/property через API и штатный SQL | Отказ, прежние bytes/history сохранены; admin DB вне гарантии | Error/exception + byte equality |
| [AA@v1:AC10] | Новая ссылка/comment/property, replacement и branch archive | Новые записи с полным provenance; старые не исчезли; AB не архивируется молча | Полная история и AA/AB срезы |
| [AA@v1:AC11] | CRLF/Unicode/точные числа, reorder и перенос применимости | Exact bytes, stable ID/origin branch/version на каждом claim, reproducible digest | Golden vector output и сравнение байтов |
| [AA@v1:AC12] | Чужая ветка через YAML/search/trace/history/error/count | Запрещённые сведения не выдаются; snapshot bound revision/digest; runtime обход выделен | Scoped response fixtures |
| [AA@v1:AC13] | Clean mock Git merge при смысловом конфликте; все local done, но requirement open/outbox pending | Trace показывает остаток; master не ready; OMH close не вызван | Coverage report + mock call log |
| [AA@v1:AC14] | Code/research/writing и все типы контента | Единый протокол с типовыми missing fields, без искусственного DOI для решения | Матрица pass/reject per type |
| [AA@v1:AC15] | Отдельный настоящий stdio MCP handshake | initialize/list/call фактически пройдены; mock не объявлен transport | Protocol log с установленной версией |

[AA@v1:N01] Дополнительные обязательные отрицания из DESIGN:86–99: битый source locator/OCR не становится подтверждённым из хеша; успешный Git merge не снимает смысловой конфликт; hash chain без внешнего checkpoint не доказывает обнаружение rollback/усечения; наличие ссылки, поля SUPPORTED/OK, успешного tool return, self-declared accepted, сохранённого текста или закрытой локальной карточки **само по себе не доказательство достоверности или глобальной готовности**. Ввод источника остаётся недоверенными данными, не командой агенту; никакого автоматического fetch в макете.

## 10. Остаток, пользовательские решения и границы доверия

[AA@v1:R01] Технически незакрыто: долговечная OMH identity/lookup, live receipt write/read-back, доверенная reviewer capability, exact digest/типовые validators, branch/archive/conflict policy, atomic storage/outbox/recovery, реальный MCP handshake и runtime isolation. Необходимые способы проверки заданы Q01–Q12 и AC01–AC15; отсутствие результата не маскируется мнением. Полного worker/reviewer/auditor APPROVE и TD-register на входе нет; для адаптированного предстартового прохода это ожидаемая граница, а не выдуманный предыдущий гейт.

[AA@v1:UD01] **REQUIRES_USER_DECISION перед live writes, не блокирует mock:** какие именно OMH операции и Git create/commit/merge разрешены и где изолированный тестовый репозиторий? Право нельзя вывести из исходного кода. Текущий scope запрещает эти действия.

[AA@v1:UD02] **REQUIRES_USER_DECISION после Q02/Q09, не блокирует mock:** распространяется ли защита на исполнителя с прямым файловым доступом/администратора и разрешено ли вводить отдельную OS identity/доверенный адаптер? Исследователь сначала показывает фактически достижимые гарантии; выбор модели угроз/полномочий остаётся пользователю. Не перекладывать на пользователя вопросы об именах реально существующих handlers или полях schema.

[AA@v1:R02] Применён структурированный adversarial проход: покрытие домена — requirements→findings→Q→AC; согласованность — каждое архитектурное предложение снабжено локаторами; специфичность — первичные локальные исходники, а OMH egress явно вторичный аудит. Разнообразие альтернатив библиотек, TRIZ/IFR и стоимостные оценки к этой bounded задаче не применялись и не имитировались. Самопроверка не независимая приёмка. Fresh-context review не запускался: subagent не делегирует. **Cross-model skipped: non-interactive context**; дополнительно карта запрещает внешние LLM/API. Родитель принимает артефакты самостоятельно.

## 11. Фактические проверки и состав выхода

| Клайм | Проверка | Наблюдение | Уровень |
|---|---|---|---|
| [AA@v1:V01] | Прочитать обязательные входы | Все документы карты прочитаны; мастер-план — K0/K3/K4 и §6–8 частями; точное покрытие в inputs_read JSON | Выполнено чтение, не runtime тест |
| [AA@v1:V02] | Сверить actual harness mechanisms | baseline_tracker полностью; writer/research builders и validator точечно; конкретные LOC выше | Статическая проверка |
| [AA@v1:V03] | Проверить существование корней read-only pathlib | harness_root=true, project=true, harness_context=false; analysis отсутствовал до записи | Реальный вывод terminal, exit_code=0 |
| [AA@v1:V04] | Точечно проверить OMH primary code | team_tool.py:60–119 и completion_store.py:220–304 прочитаны | Статическая сверка, не live independence |
| [AA@v1:V05] | Сохранить два отчёта и проверить JSON | Два разрешённых выхода; write_file проверяет запись и JSON syntax; отдельная read-only контрактная проверка выполняется перед возвратом родителю | Не считать прохождением AC01–AC15 |

[AA@v1:V06] Изменения scope: только `P/analysis/AA001_ANALYSIS.md` и `P/analysis/AA001_ANALYSIS.json`. Продуктовый код, конфиги, входы, skills, общие реестры, Git и `.kanban.db` не изменялись этим проходом. Пользовательские записи и секреты не читались. Project_context/kanban_report не запускались, поскольку требуют запрещённого доступа или изменений. Наблюдение ограничено собственными действиями агента, не глобальным аудитом чужих процессов.

[AA@v1:OUT01] **Артефакты для родителя:**
- `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/analysis/AA001_ANALYSIS.md`
- `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/analysis/AA001_ANALYSIS.json`

[AA@v1:OUT02] Точный реестр прочитанных входов и диапазонов, структурированные baseline/findings/questions/scope/checks/missing_inputs и отсутствие наблюдённых запрещённых побочных действий — в JSON. Ни PARTIAL анализа, ни successful JSON parse не означают реализацию, OS-изоляцию, живую OMH запись или принятие baseline заказчиком.
