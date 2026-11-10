# AU002-A — независимый негативный аудит AB002-A

## Секция 0 — подозрение → проверка → наблюдавшийся факт

Карта до прогона: `runtime/AU002_A/suspicions.json`. Собственный immutable run: `runtime/AU002_A/run-b944ea96/manifest.json`.

| Подозрение | Как пытался опровергнуть гарантию | Что оказалось |
|---|---|---|
| YAML ack маскирует отсутствие OMH; повтор после смерти дублирует эффект | Доставленные AA1/AB1 → новые AA2/AB2; AA sync при unavailable; AB реально умер после send до readback; новые процессы восстанавливают разные ветки конкурентно | **OK в этих условиях**: новый AA YAML=ack, OMH=ambiguous, SYNC_PENDING и NOT_READY. AB уже записан в цель, ack ещё отсутствует. В конце 4 tx, 4 writes, 8 привязанных ack; старые claim bytes сохранены. |
| Metadata новой snapshot-проверки выходит за branch scope | AA-only author читает шесть AA surfaces до/после штатного hidden AB admission; отдельный AB-only positive control; прямые AB-вызовы | **F-AU002-01 / TD-DOM-19**: при неизменных AA claims выдаётся AB revision 0→1 во всех шести ответах; прямые AB query/trace/resume/export/status дают SCOPE_DENIED. |
| Некорректная кодировка в середине истории обходит гейт или ломает диагностику | Populated disposable DB copy; средний AB event seq2 заменён invalid UTF8; два новых AA-only процесса, семь output/effect tools | **Fail-closed OK**, 14 CHAIN_BROKEN/EVENT_SHAPE_INVALID, NOT_READY, точные bytes БД/файлов неизменны. **Диагностика нарушает scope**: все ответы раскрывают UUID hidden AB event — тот же TD-DOM-19. |
| Правильный JSON, но неправильный nested target type вызывает отказ всего sync | Existing target с `TASK: []` и отдельным чужим target; два новых MCP-процесса; затем исправление только собственного malformed key | **F-AU002-02 / TD-DOM-20, OUT_OF_SCOPE**: два raw AttributeError на проводе вместо domain status; два attempt, ноль observation/ack, YAML не исполняется. NOT_READY безопасен. После исправления key: одна запись/two ack, чужая цель сохранена. |
| Ссылка на mutable global manifest меняет происхождение evidence | Сопоставил worker/RV refs и runner; для своего audit использовал run-specific manifest | Существующее предложение **RV002-A-DEBT-01 зарегистрировано как TD-DOM-21**, без нового дублирующего finding. |

## Вердикт

**REQUEST_CHANGES; completion_state=completed; continuation_required=false.**

Блокирующее основание — новая выдача A6 `read_snapshot`/integrity diagnostics раскрывает запрещённые branch metadata и object UUID. Корректная доставка в исполненном новом порядке не компенсирует этот дефект области чтения. Отдельно зарегистрирован major вне точной дельты — устойчивость simulation-порта к malformed nested target.

Это аудит интеграции A1…A9 в **SIMULATION**, не полная приёмка системы и не исполнение подготовленных PL003 → SEC003 → QA003. Отчёт не повторяет reviewer matrix и не опирается на pytest-count.

## F-AU002-01 · major · Metadata/diagnostic обход branch read scope

**TD-DOM-19, in-scope A6 + обязательное сохранение ACL.**

- Точки: `mockup/admission.py:48-51,90-100,220-277`; обещанная scope-граница — `mockup/README.md:300-301`, REQUIREMENTS §5.4. На `read_snapshot.revisions` применяется глобальная выборка без ограничения grants; `broken_event_id` из глобального verify_chain возвращается без scope-фильтра.
- Субъект: обычный MCP reader, launch-time author, разрешена только AA. Fixture не объявлена production auth; ограниченный caller не получает terminal/SQL полномочий.
- Минимальный порядок: создать AA → снять AA query/snapshot/trace/resume/sync_status/export → разрешённый другой actor добавляет AB → повторить AA. Привилегированный AB positive control действительно видит hidden claim. Прямые AB обращения от AA-only отклоняются.
- **Expected:** запрещённая AB не выдаёт revisions/counts/object IDs через разрешённый AA-запрос; integrity остаётся fail-closed, но локатор для администратора отделён от ограниченной диагностики.
- **Actual:** в шести ответах AA1 остаётся AA1, а `read_snapshot.revisions.AB` меняется 0→1. В corruption-варианте 14 ответов раскрывают AB event UUID `28ec01b7-af4d-4fdd-937e-ae440d13713b` (seq2). Global chain head/event count тоже не scoped. Утечка healthy metadata не требует никакого повреждения или прямого доступа к БД.
- Impact: наблюдение скрытого прогресса ветки и запрещённого идентификатора объекта при формально работающем branch-denial. Не заявляется plaintext body leak или разгром production auth.

Evidence: `runtime/AU002_A/run-b944ea96/scope/{result,restricted-before-hidden,restricted-after-hidden,positive-control}.json`; `middle/{injection,responses,result}.json`; raw `au-frames-*.jsonl` рядом. Это одна находка с двумя поверхностями, не два TD.

## F-AU002-02 · major · OUT_OF_SCOPE_FINDING: malformed OMH target ломает доменную диагностику

**TD-DOM-20.** Точки: `mockup/ports.py:31-39,64-71`, `mockup/admission.py:335-345`, `mockup/server.py:197-215`.

Существующая цель — valid JSON object, но значение текущего TASK имеет тип list. `read_target` трактует его как пустую карту; `attach` затем выполняет `.get` у list. Два разных процесса, PID **11740** и **7796**, получают настоящий MCP result:

```json
{"content":[{"type":"text","text":"'list' object has no attribute 'get'"}],"isError":true}
```

Нет domain `status`/`structuredContent`; SDK перенёс исключение в error content. Процессы не умерли и завершились exit0 — это **не** корректный доменный отказ только на основании exit0. Физически: два durable attempt, ноль observation/ack, YAML pending/файлов нет, байты target сохранены. Trace остаётся NOT_READY; ложного ack или потери admitted claim не установлено. После восстановления **только своего** malformed key новый reconcile даёт SYNCED, один target write и два проверенных ack, unrelated target сохранён.

**Expected:** проверка формы внешней цели и безопасная структурированная target-диагностика. Прогресс независимого YAML — желаемая robustness-характеристика; не выдаю его за формально уже обещанную per-intent гарантию. Это не обход caller permissions: malformed target подготовлен аудитором только как initial condition в disposable runtime. Не называю отсутствие observation после исключения само по себе нарушением A2: долговечный predecessor сохранился.

Evidence: `runtime/AU002_A/run-b944ea96/malformed-target/{responses,before-malformed,after-malformed,final-recovered,result}.json`, сырые frames рядом.

## Реально исполненное и вторичный read-back

CWD: `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp`.

```bash
E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AU002_A/audit_probes.py
E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AU002_A/verify_evidence.py
```

- Driver PID **5752**, exit0; четыре новые группы завершены: partial recovery, differential scope, middle invalid UTF8, malformed target. Driver exit0 означает завершённый сбор/проверку фактов, **не** product PASS.
- **29** MCP child processes: **28 exit0**, **1 намеренный exit71**. Полные команды/PID/exit/grants — `run-b944ea96/child-process-summary.json`; individual process receipts и frames в case directories. **122** server frames, **2** SDK error frames.
- Отдельный verifier PID **10928**, exit0: перепарсил raw frames; read-only SQL joins ack→observation→attempt→outbox; сверил hashes/size/read_at/predecessor time и реальные target/YAML bytes. Проверены **8** ack partial-race и **2** recovery ack malformed-target; target writes соответственно **4** и **1**.
- Частичный сценарий: YAML был реально доставлен при недоступном новом OMH intent. После AB send actual process death до readback: target уже содержит tx, ack отсутствует. Новые AA/AB процессы делают resume и восстановление без новых дубликатов. Параллельные клиенты стартовали через ThreadPoolExecutor; детерминированный одновременный critical-section overlap barrier не заявляется.
- Middle-copy: 14 structured refusals и byte-exact unchanged; это копия populated БД, внешняя цель в этот case не копировалась. Отсутствие target после исторического ack не трактуется как нарушение вечной гарантии.
- **42** source/tests/REQUIREMENTS/AB002_A-card hashes неизменны до/после; совпали **34** worker-declared hashes. Freeze: `fingerprints-before.json` / `fingerprints-after.json`. Дополнительные входы/нормативы и predecessor JSON/MD хешированы completion-only в `verification.json`, не названы preregistered.
- Все свои children закрыты; отдельный OS lookup: **0** matching launchers. `process-check.json` и `verify-command.json`. Соединения verifier/readback закрываются явно.

## Долги, границы и остаток

В `tech_debt.md` **только append**: TD-DOM-19 (major ACL), TD-DOM-20 (major external target robustness, out-of-scope), TD-DOM-21 (minor, регистрация старого RV002-A-DEBT-01). Прежние TD не закрывались и не дублировались. Для исправлений нужны worker и независимый повтор на новых initial conditions, не обещание аналитика.

Не проверены заново: legacy migrations/все malformed observation layouts; полный Cartesian S×E; B/C/D, E11/S4 и revalidation; UD-01…06; LIVE/auth/OS sandbox/checkpoint/Git; refinement. Prepared PL003/SEC003/QA003 и строгий полный поиск утечек остаются pending. Ни selective search, ни timing side channels, ни все log/export каналы этим узким audit не приняты.

Ack понимается исторически в read_at. Локальный one-write не universal exactly-once. Нет новых critical/ложных ack/READY в исполненных сценариях — это не закрытие старых известных долгов. Product/test/docs/cards/plugins read-only; никаких installs, Git, сети/listeners, live/user DB/секретов/платных сервисов. Глобальные skills не менялись: task write scope этого не допускает; воспроизводимые приёмы сохранены в собственных runtime scripts.

Неудачный write-tool финального JSON отказал из-за требования перечитать initial artifact; файл не менялся, это не product finding. Финал записан после read-back. Старые evidence/logs не удалялись.

## НАХОДКИ (эскап-хэтч)

| Уровень | Что | Действие |
|---|---|---|
| L1 | Собственные probes/evidence/report | Завершены; продукт не исправлялся. |
| L2 | TD-DOM-20; TD-DOM-21 | Зарегистрированы append-only и переданы дальше; не замолчаны как «вне scope». |
| L3 | **[ESCALATED] TD-DOM-19** | Parent → analyst → researcher: REQUEST_CHANGES по новой ACL-поверхности, затем factory fix/review/audit. Reviewer APPROVE не разрешает игнорировать новый отрицательный факт. |

Следующих агентов аудитор не запускал. Continuation AU002-A не требуется. Машинная проверка финальных JSON/MD/refs — `runtime/AU002_A/final-validation.json`.
