# AN002-A — причины REQUEST_CHANGES и точечный хендофф RS002-A

**COMPLETE_MATERIAL; completion_state=completed. Только материал аналитика, не приёмка продукта.**
JSON: `artifacts/ANALYST_AB002_A.json`. Структурная проверка: `runtime/AN002_A/validation.json`.

## 1. Вывод и границы

TD-DOM-19 — major, in-scope A6+ACL: проверка разрешённой ветки не ограничивает новые metadata/diagnostic поля всего ответа. TD-DOM-20 — major, out-of-scope A: чтение внешней цели стирает различие отсутствующего ключа и неверного nested типа, а attach предполагает dict. TD-DOM-21 — minor, уже известный RV002-A-DEBT-01 о mutable evidence pointer; не причина первых двух и не дубликат finding.
RV002-A APPROVE ограничен прежними комбинациями A. AU002-A REQUEST_CHANGES — вход этого анализа, не отменён. Корректные delivery facts не компенсируют confidentiality defect. Материал для анализа взят из реальных файлов; никаких новых E2E, изменений кода или закрытия TD.
Task card прямо назначает анализ после REQUEST_CHANGES; общее APPROVE-only правило §3 контракта 08 не применяется как запрет этого remediation handoff и не превращается в разрешение deploy. Пути отчётов следуют карте проекта и shared process.

## C-A2-01 · TD-DOM-19 · major

**Scope:** IN_SCOPE A6 + preserved ACL. **Класс:** Unscoped derived metadata / diagnostic information flow across the authorization boundary; internal proof-public response conflation.

**Симптом.** AA-only MCP caller при неизменных AA claims видит AB revision 0→1 на шести ответах. При broken среднем AB event получает запрещённый UUID и глобальные seq/count. Прямые AB вызовы отклоняются.

**Причина.** Scope авторизует запрошенную ветку, но не замыкает область данных всего response envelope. integrity_gate использует глобальную проверку как одновременно внутренний доказательный stamp и готовую публичную проекцию. Все branch_heads и общий chain_head добавляются уже после scope-проверки; verify_chain возвращает глобальные локаторы без классификации по полномочиям.

**Путь причины:**
- scope(branch) в query/status/export/resume проверяет AA и работает; сам guard не обойдён.
- verify_chain SELECT всей events обязателен для текущей глобальной цепи; сам по себе не причина disclosure.
- integrity_gate:92-93 собирает revisions всех веток и global chain_head; :98-100 вставляет необработанный chain в IntegrityFailure.
- _trace:262,270 отдельно возвращает global chain; resume:369 вкладывает этот trace. Фильтр только read_snapshot.revisions оставит healthy count/head канал.
- guarded:34 и MCP serializer:213-215 возвращают эти поля caller в text и structuredContent; origins scoped на :96-97, но соседние chain/stamp этим не защищены.

**Нарушенная граница.** Авторизация запрошенного объекта != авторизация всех derived fields. Конфиденциальность ветки/объекта охватывает metadata и диагностику, а не только plaintext claims.

**Root vs symptom.** Root — отсутствие отдельного actor-scoped output-контракта для integrity evidence; AB revision, UUID, seq/count/head — разные симптомы одного класса. Не причина: необходимость глобальной проверки, плохой claim-body filter, OS-admin, fixture auth или TD-DOM-14 branch/master readiness.

**Почему прежний review не остановил:** RV corruption проверял status, exact seq/reason, NOT_READY и неизменные байты через MCP helper без branch-grant параметра; его default reviewer-контекст не создаёт AA-only vs hidden AB differential. Runner spoof проверяет запрещённую ZZ/role, а не разрешённый AA envelope при changing AB. A6/Q-09/Q-11 oracle требовал локатор, не различая аудиторию.
Перенос критерия «диагностика содержит locator» в общий oracle без второй оси «кто имеет право видеть locator». Успешный fail-closed был ошибочно достаточным для A6 при сохранённой общей ACL-обязанности.
**Предел вывода:** Это вывод из сохранённых сценариев/условий, не утверждение о мотивах reviewer и не доказательство отсутствия любых иных непрочитанных проверок.

**Минимальная последовательность.** Одно общее work, AA-only actor, принята AA1. Снять query/snapshot/trace/resume/status/export; независимый AB actor штатно допускает AB1; повторить AA и positive AB control. Отдельно на копии повредить средний AB event и открыть два AA-only MCP процесса: refuse без выпуска, но без foreign locator.

**Физические факты.** Перепарсены сохранённые before/after и positive control: claims AA совпадают, все шесть chain_head меняются, trace.chain.events 1→2 и resume.trace.chain.events 1→2. Middle: 14 отказов, семь tools, два PID, во всех UUID инъекции AB seq2; before/after physical JSON совпадают.

**Уверенность:** high; Current code path plus immutable auditor response differential and reparse; no new E2E.
**Неизвестно:** Привилегированный diagnostic transport/role не выбран. Timing, все logs/search/cursors и plaintext body leak не доказаны.

**Ограничение следующего решения.** Сохранить глобальный gate и snapshot consistency. Разделить internal proof и публичную actor-scoped проекцию на всех вложенных выходах. Не объявлять CHAIN_OK/READY ради сокрытия чужой порчи. Минимальный статус блокировки может раскрывать общую недоступность: абсолютная indistinguishability healthy/broken не обещается; explicit safe health contract нужен RS002-A.

**Evidence:** E-A2-03, E-A2-04, E-A2-05, E-A2-06, E-A2-07, E-A2-10, E-A2-14, E-A2-15, E-A2-16, E-A2-17, E-A2-18, E-A2-19, E-A2-20, E-A2-21, E-A2-22, E-A2-28, E-A2-29, E-A2-30, E-A2-31, E-A2-35.

## C-A2-02 · TD-DOM-20 · major

**Scope:** OUT_OF_SCOPE A; SIMULATION external nested target robustness. **Класс:** Lossy validation / absent-invalid conflation at an external data boundary, compounded by exception escape and sequential fail-stop fanout.

**Симптом.** Два новых MCP процесса на TASK=[] получают isError с raw AttributeError без domain status; OMH intent ambiguous, YAML pending. Нет false ack/READY.

**Причина.** Port валидирует только внешний JSON object. read_target сводит отсутствующий target и присутствующий malformed nested value к одинаковому {}. attach заново читает сырой nested value и предполагает dict, вызывая .get у list. Read и write paths не имеют единого shape-контракта.

**Путь причины:**
- ports._load:31-35 проверяет лишь корневой dict, не форму target.
- read_target:38-39 превращает TASK:list в {}, pre-read видит отсутствие tx и переходит к attach.
- attach:67-71: store.get(target,{}).get(tx) на list выбрасывает AttributeError до target write.
- admission:335-345 ловит OSError/ValueError, не AttributeError; guarded:30-36 тоже не переводит его в доменный статус; server:199-209 ловит только ToolInput. Сохранённый wire показывает SDK generic error, а не domain response.
- Attempt уже committed на :315-319. Observation :348-356 не достигается; ORDER BY revision,kind даёт OMH_EVIDENCE перед YAML_EXPORT, исключение прерывает весь for. Повтор в новом процессе заново встречает ту же внешнюю форму.

**Нарушенная граница.** Недоверенное внешнее состояние должно быть явно валидировано до интерпретации/мутации. Файл отсутствует, key отсутствует и key присутствует неверного типа — разные состояния. Владение своим key не разрешает reset всего target store.

**Root vs symptom.** Root — разрыв nested shape validation между чтением и attach; raw exception и блокировка следующего intent — последствия. Просто catch AttributeError скроет неверную семантику {} и не даст ясного контракта. Два attempt без observation сами по себе не нарушение A2: predecessor durable, ack не создан. YAML-isolation desired robustness, не уже установленная formal A-гарантия.

**Почему прежний review не остановил:** RV/runner target вариации покрывали available/unavailable/liar/ambiguous/crash-after-send и корректные populated target; malformed nested TASK:list не включён. Корневой JSON-валидатор создаёт ложное ощущение валидации всей цели.
Fault modes адаптера и протокол ack проверялись, но внешний shape не был отдельной осью initial conditions; transport exit0 не оракул доменного отказа.
**Предел вывода:** Нельзя из этого вывести производственную auth-уязвимость или факт испытания null/scalar/всех иных layouts.

**Минимальная последовательность.** Один admitted pending AA tx; собственный TASK=[] и unrelated target. Два свежих процесса resume→sync→status/trace. Затем исправить только owned key до {}, reconcile новым процессом и физически прочитать store/write log/ack связи.

**Физические факты.** Сохранённые PIDs 11740/7796: одинаковый raw list.get error; after-malformed counts attempts=2, observations=0, acks=0 и target bytes без изменений. Recovery counts observations=2, acks=2, один OMH write/target tx, unrelated target сохранён.

**Уверенность:** high_for_TASK_list; Port source and wire/physical evidence converge; owned-key recovery isolates cause.
**Неизвестно:** Null/scalar/nested tx-record layouts, dynamic concurrent replacement и политика продолжения остальных intents не испытаны здесь.

**Ограничение следующего решения.** RS002-A определяет общий валидатор и честный результат invalid/unavailable/ambiguous; blanket swallow, silent reset target, перезапись неизвестных ключей, фиктивное observed=matched или ack запрещены. Решение о per-intent continuation предложить явно, не выдавать за существующую норму.

**Evidence:** E-A2-04, E-A2-07, E-A2-08, E-A2-09, E-A2-10, E-A2-11, E-A2-12, E-A2-13, E-A2-23, E-A2-24, E-A2-25, E-A2-26, E-A2-27, E-A2-32, E-A2-36, E-A2-39, E-A2-40.

## C-A2-03 · TD-DOM-21 · minor

**Scope:** Known RV002-A-DEBT-01 / future D tooling, not a new product finding. **Класс:** Mutable evidence-reference / run identity conflation.

**Симптом.** Shared runtime/AB002_A/e2e_manifest.json перезаписывается при следующем run; голая ссылка не определяет прежний набор кейсов.

**Причина.** Имя текущего указателя смешано с идентичностью immutable evidence. Run-specific manifest есть, но shared pointer также используется для progress и может попасть в отчёт без frozen lineage.

**Путь причины:**
- ab002_matrix:366 создаёт новый run; :397,405,408 обновляют shared pointer, :408 сохраняет run-specific manifest.
- Повтор меняет shared target; старый отчёт без manifest hash/source-input linkage начинает указывать на другой run.

**Нарушенная граница.** Evidence точной версии/запуска != актуальное состояние global progress pointer.

**Root vs symptom.** Не причина TD19/20, не доказанная порча данных продукта или ложность immutable auditor evidence. Это независимый риск доказательной базы; не новый TD и не повод повторять весь аудит.

**Почему прежний review не остановил:** Не пропущен: reviewer нашёл и предложил RV002-A-DEBT-01; auditor зарегистрировал TD-DOM-21 и использовал собственный run-specific manifest.
Оставался proposal из-за write scope reviewer; регистрация сделана auditor.
**Предел вывода:** Не установлена фактическая подмена текущих audit evidence; такой вывод был бы необоснован.

**Минимальная последовательность.** В будущем tooling-check выполнить два изолированных run и убедиться, что первый manifest+hash остаётся адресуемым, независимо от shared latest pointer.

**Физические факты.** Исходник runner явно сохраняет обе ссылки; RV proposed_debts и tech_debt.md сопоставляют прежний proposal с TD21; auditor manifest run-b944ea96 не является shared pointer.

**Уверенность:** high_for_pointer_design; Current runner source and explicit prior debt registration.
**Неизвестно:** Новый two-run E2E tooling replay не выполнялся; глобальная пригодность всех исторических report pointers не проверена.

**Ограничение следующего решения.** Закреплять run-specific manifest/hash и source/input fingerprints в будущей сдаче. Не удалять старые runs, не переименовывать TD и не закрывать debt только этим анализом.

**Evidence:** E-A2-32, E-A2-33, E-A2-34, E-A2-48.

## Приоритет и последовательность

- **P0 / TD-DOM-19 (major):** RS002-A scoped-output/diagnosis contract -> updated worker fix card -> independent review/audit; do not defer existing leak to PL003 or accept affected A.
- **P1 / TD-DOM-20 (major):** RS002-A target shape + failure boundary contract, orchestrator schedules explicit out-of-scope robustness slice; no silent widening of A and no debt disappearance.
- **P2 / TD-DOM-21 (minor):** Keep immutable refs in handoff now, research minimal D lineage contract; no new duplicate debt or acceptance claim.

Parent dispatches RS002-A with this JSON+MD and exact Q-A2-01..05; research resolves only these deltas. Then parent prepares updated worker card for TD19 and separately scopes TD20; independent fix/review/audit. PL003 -> SEC003 -> QA003 remains sequential mandatory after analyst→researcher part/current updated cycle card, not executed here.

Новых решений пользователя для прекращения запрещённой metadata выдачи сейчас не требуется. UD-01…06 остаются OPEN. Новый privileged live channel, repair или обязательную per-intent гарантию нельзя выбирать молча: researcher обязан отдельно обозначить зависимость.

## Вопросы для RS002-A — ограниченная дельта

Не повторять все Q-01…15 RS001. Каждый ответ: механизм/полевая схема, причина выбора, source ledger, точные action→expected→physical факты, ограничения и needs-user при реальной зависимости. Предложение не считать работающим кодом.

### Q-A2-01

Как разделить полный внутренний integrity stamp и actor-scoped публичную проекцию healthy-ответа так, чтобы ни read_snapshot.revisions/chain_head, ни trace.chain и resume.trace.chain не раскрывали скрытую ветку, сохранив verified read snapshot и внутреннюю привязку delivery evidence?

**Связь:** F-AU002-01, TD-DOM-19; R-ACL, R-INTEGRITY, R-DELIVERY.
**Точки:** `mockup/admission.py:90-101`; `mockup/admission.py:220-277`; `mockup/admission.py:323-370`.
**Ожидаемый контракт:** Field-level allowlist по launch-time grants для каждого top-level/nested выхода; внутренние global proof и observation facts не теряют привязку. Global hash нельзя считать безопасным только потому, что это hash. Query/snapshot alias, trace/resume, status/export и sync перечислены отдельно; формат scoped token, если нужен, только предложить с семантикой, не подменять им global доказательство.
**E2E action:** AA-only actor, AA фиксирована; B actor меняет hidden AB, B positive control; шесть healthy outputs и новый PID, плюс permitted sync actor с теми же AA grants.
**Expected:** Permitted содержимое сохраняется, запрещённые revisions/count/head/IDs не появляются ни в text, ни structured/nested outputs; direct AB по-прежнему denied. Sync-вариант новый, не заявлен как уже исполненный healthy audit.
**Physical oracle:** Raw MCP field-level differential с исключением документированных read_at, positive AB control, точные AA bytes и readback/SQL observation→attempt→intent; gate остаётся глобальным.
**Почему это новое:** Не повторяет Q-11 о местоположении gate: gate уже работает; нужен контракт публикации его побочных полей.
**Evidence:** E-A2-05, E-A2-06, E-A2-07, E-A2-15, E-A2-16, E-A2-17, E-A2-18.

### Q-A2-02

Какой минимальный безопасный CHAIN_BROKEN ответ допустим restricted actor при повреждении forbidden AB, и как отдельно сохранить точный привилегированный locator без UUID/seq/count/revisions/глобальных хешей в restricted ответе и без ослабления глобального fail-closed?

**Связь:** F-AU002-01, TD-DOM-19; R-ACL, R-INTEGRITY.
**Точки:** `mockup/admission.py:48-70`; `mockup/admission.py:90-100`; `mockup/admission.py:30-36`; `mockup/server.py:197-215`.
**Ожидаемый контракт:** Таблица public/privileged/internal диагностических полей; права admin locator не выводить из имени reviewer/owner и не расширять actor grants. Если защищённого диагностического канала ещё нет — назвать GAP и предложить безопасную схему, не изобретать реализованный endpoint. Статус общей блокировки допускается как обязательный health signal; строгая неразличимость healthy/broken при глобальном gate не обещается. Correlation token, если предлагается, не должен быть стабильным foreign ID/hash surrogate.
**E2E action:** Middle forbidden AB invalid-UTF8 и отдельно wrong hash на disposable populated копии; AA-only actor, два свежих процесса, семь tools; затем authorized privileged locator control по выбранному контракту.
**Expected:** Structured refusal, NOT_READY, нет эффекта/exports и forbidden locator; глобальная порча всё ещё блокирует AA. Привилегированный оракул точно находит испорченный event без выдачи его restricted actor.
**Physical oracle:** Raw text/structured error scan, target/export/DB before==after, admin oracle к fixture locator, без shared diagnostic handle утечки.
**Почему это новое:** Q-09/Q-11 требовали locator, но не адресата. Новый вопрос устраняет противоречие locator vs branch confidentiality, не выбирает rewind/repair.
**Evidence:** E-A2-05, E-A2-10, E-A2-19, E-A2-20, E-A2-21, E-A2-22, E-A2-28, E-A2-29, E-A2-35.

### Q-A2-03

Какой единый read/attach shape-контракт различает отсутствующий файл/target key и присутствующий TASK со значением list/null/scalar, а также неверный tx record, не нормализуя malformed данные в пустую карту и не меняя чужие keys?

**Связь:** F-AU002-02, TD-DOM-20; R-DELIVERY, R-IMMUTABLE.
**Точки:** `mockup/ports.py:31-39`; `mockup/ports.py:64-82`; `mockup/admission.py:335-345`.
**Ожидаемый контракт:** State table absent/valid/invalid/unavailable/conflicting с явным domain diagnosis; чтение и locked attach применяют согласованную проверку nested shape. Запрещены silent reset/auto-coercion/удаление unknown data и ложный ack; сохранять evidence причину без raw payload/path. Валидатор/ошибка — предложенный механизм для out-of-scope обязательства, не исправление A заочно.
**E2E action:** Fresh и populated target, собственный key отсутствует/{}/[]/null/scalar; присутствуют unrelated keys и existing tx. Для каждого два новых процесса и controlled correction только own key.
**Expected:** Malformed выдаёт domain error без Attribute/TypeError и без мутации target/ack; отсутствующий key штатно создаётся, валидные и чужие данные не теряются. После явного исправления восстановление.
**Physical oracle:** Original bytes при отказе, foreign-key equality, raw MCP, SQL matched/ack false до exact readback, recovery write log без дубликата.
**Почему это новое:** Не повторяет общий Q-01 о readback: уточняет доверенную форму самого readback источника, выявленную TASK:list.
**Evidence:** E-A2-08, E-A2-09, E-A2-23, E-A2-24, E-A2-25, E-A2-26, E-A2-27, E-A2-40.

### Q-A2-04

Как согласовать доменное завершение попытки при target shape failure и независимые intents одного sync: что фиксировать как failed/unobserved/ambiguous, когда продолжать YAML, какой aggregate результат вернуть и как повтором не подделать readback/ack?

**Связь:** F-AU002-02, TD-DOM-20; R-DELIVERY, R-INTEGRITY.
**Точки:** `mockup/admission.py:307-362`; `mockup/admission.py:30-36`; `mockup/server.py:197-215`; `mockup/delivery.py:44-75`.
**Ожидаемый контракт:** Разделить ошибку доказанно до эффекта и ошибку с возможным эффектом; durable attempt не равен observed. Нельзя сохранять пустой raw как успешное наблюдение. Дать допустимые transition/aggregate states и явное предложение per-intent isolation либо fail-stop с rationale. YAML continuation — запрошенная robustness-доработка, не ретроактивная A2-гарантия; если нужен новый product choice — отдельно эскалировать, не выбирать молча.
**E2E action:** Malformed OMH + pending YAML; два retry процесса; затем owned correction/reconcile; отдельно обрыв после send с uncertain outcome.
**Expected:** Truthful structured SYNC_PENDING/target diagnosis или согласованный эквивалент, NOT_READY и no false ack. YAML поведение соответствует выбранному контракту; uncertain outcome не маркируется доказанным no-effect.
**Physical oracle:** Attempt/observation/ack SQL lineage и server frames, target/YAML before/after, one-write recovery. Отсутствие observation не считать самостоятельным A2 fail.
**Почему это новое:** Не переделывает общий автомат Q-02/Q-03: узкий новый переход внешней shape-ошибки и граница отказа fanout.
**Evidence:** E-A2-07, E-A2-10, E-A2-11, E-A2-12, E-A2-23, E-A2-25, E-A2-27, E-A2-36, E-A2-40.

### Q-A2-05

Какой минимальный immutable evidence reference должен фиксировать run-specific manifest, его hash и source/input lineage, чтобы повтор runner не переназначал evidence прежнего отчёта через shared e2e_manifest.json?

**Связь:** TD-DOM-21; R-EVIDENCE, R-NEGATIVE-E2E.
**Точки:** `mockup/ab002_matrix.py:364-408`; `artifacts/REVIEWER_AB002_A.json#/proposed_debts/0`; `tech_debt.md:36`.
**Ожидаемый контракт:** Сдача адресует immutable run manifest+hash+fingerprints; latest pointer допустим только для progress/navigation, не sole evidence. First/failed run и прежние evidence сохраняются; existing TD21 без дубликата.
**E2E action:** В будущем D/tooling выполнить два изолированных run и разрешить refs первого отчёта после второго; изменить latest pointer только как штатный эффект нового run.
**Expected:** Первый bundle/manifest hash и version lineage остаются теми же; mismatched artifact version обнаруживается, не становится PASS.
**Physical oracle:** Два run-specific manifests, fingerprints, ref resolution/hash comparison и retention старого bundle. Этот two-run check сейчас не запускался.
**Почему это новое:** Новый узкий tooling вопрос из уже замеченного reviewer proposal; не повтор исследования A или полный новый D план.
**Evidence:** E-A2-32, E-A2-33, E-A2-34, E-A2-48.

## PL003: реальные точки должны стать checks

Это вход планировщику, НЕ готовый PL003 plan и НЕ исполнение SEC003/QA003. Перед запуском перепривязать строки к актуальному fingerprint. Наблюдаемое не превращать обратно в гипотезу; предполагаемые расширения не объявлять finding.

| Point → check | Статус / долг | Источник и путь | Что ломать / oracle |
|---|---|---|---|
| LP-A2-01 → CHK-A2-01 | OBSERVED_EXISTING_EVIDENCE; TD-DOM-19 | mockup/admission.py:90-101; mockup/admission.py:220-246; mockup/admission.py:273-277; mockup/admission.py:364-370; AA scope -> global integrity stamp -> public read_snapshot | AA fixed / hidden AB changes; scan revisions and chain_head on six surfaces + authorized scoped sync. Oracle: AB positive control + field-level raw MCP differential; no filesystem access for caller |
| LP-A2-02 → CHK-A2-02 | OBSERVED_EXISTING_EVIDENCE; TD-DOM-19 | mockup/admission.py:256-270; mockup/admission.py:369; verify_chain -> _trace.chain -> trace and resume.trace | После фильтра stamp продолжать искать events/head_hash в nested chain; existing frames показывают 1→2 при fixed AA. Oracle: Отдельный nested field inventory, fixed AA + AB positive control |
| LP-A2-03 → CHK-A2-03 | OBSERVED_EXISTING_EVIDENCE; TD-DOM-19 | mockup/admission.py:48-70; mockup/admission.py:94-100; mockup/admission.py:30-36; mockup/server.py:213-215; broken foreign event -> IntegrityFailure -> text and structuredContent | Middle hidden AB corruption/restart on seven tools: retain global refusal, no foreign UUID/seq/count/revisions; admin locator separate. Oracle: Raw error field scan + exact physical before==after + admin diagnosis |
| LP-A2-04 → CHK-A2-04 | SOURCE_DERIVED_HYPOTHESIS_NOT_EXECUTED; TD-DOM-19 | mockup/admission.py:248-258; mockup/admission.py:364-370; omitted branch -> master trace UNKNOWN early return, but outer integrity stamp attached first | AA-only dom_trace without branch/master plus resume nested output; UNKNOWN не считать доказательством отсутствия metadata leakage. Oracle: Current entrypoint inventory + positive union control + hidden-AB differential; no new finding before execution |
| LP-A2-05 → CHK-A2-05 | OBSERVED_TASK_LIST_ONLY_OTHER_SHAPES_HYPOTHESES; TD-DOM-20 | mockup/ports.py:31-39; mockup/ports.py:64-71; external JSON -> read normalization -> raw locked attach | Absent vs list/null/scalar/current tx malformed; unrelated keys survive; no silent reset; locked reread same contract. Oracle: Raw MCP + exact target bytes + foreign key equality before/after and controlled recovery |
| LP-A2-06 → CHK-A2-06 | OBSERVED_TASK_LIST_SEQUENCE_CONTRACT_PENDING; TD-DOM-20 | mockup/admission.py:312-357; mockup/server.py:197-215; mockup/delivery.py:68-75; durable attempt -> uncaught exception -> observation not reached -> YAML later intent starved | Two fresh retries and correction; domain status/partial delivery/ambiguous truthfulness, then crash after possible effect. No fallback ack. Oracle: SQL attempt/observation/ack links, write count, raw isError vs structured status; YAML outcome after research decision |
| LP-A2-07 → CHK-A2-07 | KNOWN_DEBT_SOURCE_CONFIRMED_NO_NEW_TWO_RUN_PROBE; TD-DOM-21 | mockup/ab002_matrix.py:364-408; report -> shared mutable manifest pointer -> subsequent run | Immutable source/input/manifest lineage after second run; latest pointer not canonical evidence. Oracle: Run-specific manifest/hash and frozen source/input tuple; retain earlier failures |

Особенно не потерять `trace.chain` и `resume.trace.chain`: current wire уже показывает count 1→2 и смену head, даже если новый фикс удалит AB только из revisions. `dom_trace` без branch/master при AA-only — пока source-derived гипотеза: UNKNOWN body не очищает заранее сформированный stamp. Text и structuredContent сериализуют один result; оба канала входят в oracle.
PL003 обязан охватить запись, чтение, append-only обновление, выборочный и веточный поиск, export/status/errors, restart/concurrency/recovery. В прочитанном TOOLS нет отдельного selective-search/refinement API: GAP/NOT_IMPLEMENTED, а не PASS через snapshot. Логи/cursors/timing — ещё не доказанные каналы; создать конкретные hypotheses, не писать «всё течёт».
Порядок: завершённый AN002-A → RS002-A → обновлённая карта текущего цикла; PL003 → SEC003 → QA003, с findings SEC в QA и независимой приёмкой по фабрике. Известный TD19 должен получить fix/recheck, а не отсрочку под предлогом будущего security cycle. OMH delta готовит planner и применяет parent; этот анализ ничего в OMH не менял.

## Deferred context: дерево уточнений

`deferred_to_researcher`, не реализовано и не исполняемая часть A. REQUIREMENTS §1 четвёртое уточнение и §3: новый дочерний immutable claim на уровень ниже, без предметного предела глубины; актуальность только после независимого допуска; параллельные дочерние узлы и revalidation требуют дальнейшего исследования. Не подменять деревом existing replacement и не смешивать с пятью defect questions.

## Проверка, пределы и доказательная база

Сначала действительно записан минимальный PARTIAL; его копия `runtime/AN002_A/first_artifact.json`. Собственный read-only extract: `runtime/AN002_A/evidence_extract.json`; analysis-time hashes: `runtime/AN002_A/input_hashes.json`; frozen comparison: `runtime/AN002_A/frozen_comparison.json`. Все 42 текущих fingerprints совпали с сохранённым AU snapshot. Это проверка текущих байтов, не новый аудит или E2E.
Команды фактической обработки:

```text
E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AN002_A/inspect_inputs.py
E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AN002_A/finalize_material.py
```

Первый extract выполнен exit0. Вторая команда строит финальные файлы и проверяет coverage/IDs/required fields/local locators/hashes/MD consistency; её receipt — validation.json. Структурный PASS не доказывает product safety и не закрывает долг. Raw wire/physical evidence принадлежит AU002-A, а не выдан за новые analyst subprocess.
Важное уточнение входа: старое поле expected в malformed-target/result.json желает сохранённое наблюдение и продолжение YAML; финальный auditor JSON+MD явно сужает это до desired robustness, не формальной per-intent гарантии A. Вопрос Q-A2-04 сохраняет именно эту границу.

### Непроверено

- No fresh product E2E in this analyst role; existing immutable frames reparsed and current source/frozen hashes checked.
- Privileged diagnostic routing/authorization and safe health-signal schema are proposed research deliverables, not existing tested functionality.
- Healthy AA-only sync and omitted/master branch differential are source-derived extensions, not newly observed runs.
- Null/scalar/tx-record malformed target, concurrent external replacement and chosen per-intent continuation behavior not executed.
- Search/ranking/count/snippets/cursor/cache/log/timing channels not accepted; TOOLS inventory has no dedicated selective search or refinement API, PL003 must mark GAP rather than substitute snapshot.
- No two-run tooling replay, full Cartesian security, LIVE OMH/Git/auth/issuer/OS sandbox/external checkpoint or B/C/D acceptance.
- Analysis-time hashes are not preregistered source fingerprints; historical audit run provenance remains auditor-owned.
- No fresh-context or cross-model review: non-interactive subagent, agent dispatch prohibited; bounded self-questioning only.

Cross-model skipped: non-interactive subagent context; запуск других агентов запрещён. Self-challenge — degraded, не независимый fresh-context review. Самопроверка отвергла ложные выводы: глобальный verifier не причина disclosure; TD20 не false ack; TD21 не опровергает immutable evidence; healthy/broken hidden branch не обязаны давать одинаковую доступность при сохранённом глобальном gate.
Универсальные workflow/skills не менялись из-за узкого write scope. Воспроизводимый локальный приём анализа сохранён в inspect_inputs.py/finalize_material.py и их docstrings; никаких diagrams/network/paid вызовов.

## Coverage

| Вход | Причина | Вопросы | Planner points | Итог |
|---|---|---|---|---|
| F-AU002-01 / TD-DOM-19 | C-A2-01 | Q-A2-01, Q-A2-02 | LP-A2-01, LP-A2-02, LP-A2-03, LP-A2-04 | causally_analyzed_not_fixed |
| F-AU002-02 / TD-DOM-20 | C-A2-02 | Q-A2-03, Q-A2-04 | LP-A2-05, LP-A2-06 | causally_analyzed_registered_out_of_scope_not_fixed |
| known prior proposal / TD-DOM-21 | C-A2-03 | Q-A2-05 | LP-A2-07 | known_prior_debt_role_explained_not_closed |

## Evidence catalogue

| ID | Local source | Locator |
|---|---|---|
| E-A2-01 | `REQUIREMENTS.md` | 31-44 |
| E-A2-02 | `REQUIREMENTS.md` | 46-52 |
| E-A2-03 | `REQUIREMENTS.md` | 82-98 |
| E-A2-04 | `cards/AB002_A_WORKER.md` | 32-42 |
| E-A2-05 | `mockup/admission.py` | 39-101 |
| E-A2-06 | `mockup/admission.py` | 220-277 |
| E-A2-07 | `mockup/admission.py` | 307-370 |
| E-A2-08 | `mockup/ports.py` | 31-39 |
| E-A2-09 | `mockup/ports.py` | 64-82 |
| E-A2-10 | `mockup/server.py` | 197-215 |
| E-A2-11 | `mockup/delivery.py` | 19-36 |
| E-A2-12 | `mockup/delivery.py` | 44-75 |
| E-A2-13 | `mockup/storage.py` | 100-113 |
| E-A2-14 | `mockup/README.md` | 298-323 |
| E-A2-15 | `runtime/AU002_A/run-b944ea96/scope/restricted-before-hidden.json` | whole JSON |
| E-A2-16 | `runtime/AU002_A/run-b944ea96/scope/restricted-after-hidden.json` | whole JSON |
| E-A2-17 | `runtime/AU002_A/run-b944ea96/scope/positive-control.json` | /claims |
| E-A2-18 | `runtime/AU002_A/run-b944ea96/scope/result.json` | /actual/direct_AB_denials |
| E-A2-19 | `runtime/AU002_A/run-b944ea96/middle/injection.json` | whole JSON |
| E-A2-20 | `runtime/AU002_A/run-b944ea96/middle/responses.json` | whole JSON |
| E-A2-21 | `runtime/AU002_A/run-b944ea96/middle/injected-before.json` | whole JSON |
| E-A2-22 | `runtime/AU002_A/run-b944ea96/middle/after-refusals.json` | whole JSON |
| E-A2-23 | `runtime/AU002_A/run-b944ea96/malformed-target/responses.json` | whole JSON |
| E-A2-24 | `runtime/AU002_A/run-b944ea96/malformed-target/before-malformed.json` | whole JSON |
| E-A2-25 | `runtime/AU002_A/run-b944ea96/malformed-target/after-malformed.json` | whole JSON |
| E-A2-26 | `runtime/AU002_A/run-b944ea96/malformed-target/final-recovered.json` | whole JSON |
| E-A2-27 | `runtime/AU002_A/run-b944ea96/malformed-target/result.json` | /actual/proof |
| E-A2-28 | `artifacts/REVIEWER_AB002_A.json` | /per_invariant/A6 |
| E-A2-29 | `runtime/RV002_A/independent_probes.py` | 121-152 |
| E-A2-30 | `mockup/ab002_e2e.py` | 26-35 |
| E-A2-31 | `mockup/ab002_matrix.py` | 150-187 |
| E-A2-32 | `mockup/ab002_matrix.py` | 364-408 |
| E-A2-33 | `artifacts/REVIEWER_AB002_A.json` | /proposed_debts/0 |
| E-A2-34 | `tech_debt.md` | 30-36 |
| E-A2-35 | `runtime/RS001_RESEARCH.json` | /questions |
| E-A2-36 | `runtime/RS001_HANDOFF.md` | 18-35 |
| E-A2-37 | `templates/NEGATIVE_E2E_SECURITY_CONTRACT.md` | 23-95 |
| E-A2-38 | `cards/PL003_NEGATIVE_E2E_PLANNER.md` | 1-39 |
| E-A2-39 | `artifacts/AUDITOR_AB002_A.json` | /findings |
| E-A2-40 | `reports/AUDITOR_AB002_A.md` | 36-48 |
| E-A2-41 | `E:/opencode_harness_portable/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md` | 95-111 |
| E-A2-42 | `E:/opencode_harness_portable/docs/CODERS/09_FINDINGS_ESCAPE_HATCH.md` | 17-47 |
| E-A2-43 | `E:/opencode_harness_portable/shared/code-factory-process.md` | 101-158 |
| E-A2-44 | `mockup/server.py` | 35-118 |
| E-A2-45 | `cards/AN002_A_ANALYST.md` | 42-65 |
| E-A2-46 | `docs/AB002_PLAN.md` | 11-24 |
| E-A2-47 | `runtime/AU002_A/verification.json` | whole JSON |
| E-A2-48 | `runtime/AU002_A/run-b944ea96/manifest.json` | whole JSON |

## НАХОДКИ (эскап-хэтч)

| Уровень | Что | Действие |
|---|---|---|
| L1 | Собственные материал/JSON/validator | Только разрешённые файлы, структурная сверка; product не исправлялся. |
| L2 | TD-DOM-20 и TD-DOM-21 | Причины/границы переданы RS002-A и PL003; существующая регистрация сохранена, новых дублей/закрытий нет. |
| L3 | [ESCALATED] TD-DOM-19 | Parent/RS002-A → factory fix/review/audit; REQUEST_CHANGES не снят. |

Продолжение AN002-A не требуется при успешной structural validation; COMPLETE_MATERIAL относится только к хендоффу. Код, tests/docs/cards/debts/plugins и все прежние evidence read-only.
