# AU006 — независимый аудит обязательного цикла OMH ↔ DOM

## 0. Сомнительное, что проверено

| Сомнение | Проверка | Результат |
|---|---|---|
| В макете есть read-before-write gate, не замеченный parent? | Own R01/R02 raw MCP plus submit/schema/admit | Нет в проверенном пути; обе ветви admitted. Не обобщать на все сессии. |
| external_task_ref/requirements/deps доказывают контекст? | R03 and R05; SQL references read back | Нет; фиксированный wrong TASK блокируется, неизвестные requirements/evidence допускаются; пропущенный dep не проверяется. |
| Pending/rejected результат блокирует readiness? | R04 material artifact, pending and rejected, no-new-knowledge comment | Нет; READY сохраняется. Реальное закрытие OMH не запускалось. |
| Рестарт теряет candidate или создаёт повтор? | Kill author; new PIDs; SQL; replay and rebase | Данные не потеряны, повтор tx не создаёт дубль; discovery pending через resume отсутствует. |
| Все хуки хоста fail-open, как AN005? | Installed host plugins_dispatch.py + plugins.py + model_tools.py, OMH tool hooks | Слишком широко: pre_tool callback exception/timeout fail-closed; internal OMH rules/home failures can allow, outer dispatch exception falls through; pre_verify is bounded guidance. Источник AN005 уточнён, не повторён на веру. |
| В OMH вообще нет baseline/checkpoint/приёмочных механизмов? | todo_store, todo_tool, completion_store, evidence reducer; harness controller sources | Есть native dossier, evidence windows, prefix guards and factory typed gates; не DOM ContextPack/AcceptedBasis or trusted DOM lifecycle wiring. |
| Наличие passing tool evidence закрывает именно задачу? | Own standalone reducer over disposable SQL fixtures, negative failed/unknown controls | Нет смысловой связи: unrelated pass closes, rejected MCP-only window empty. Это не live host close. |
| Рабочий graph API можно использовать вместо простого query? | Raw tools/list, schema, ITERATIVE spec | Нет среди 12 tools. GAP, не реализован и не симулирован. |

## Вердикт: REQUEST_CHANGES

**Аудит завершён в разрешённом локальном/source-bound scope. Приёмка продукта — false.** Обязательность «OMH → сверка оснований → существенная работа → ведение ветки → независимый допуск/доставка → приёмка OMH» в проверенном контуре не обеспечена. Реальные guards есть, но они проверяют форму/заявленные ревизии/fixture-полномочия, а не полный жизненный цикл. Нельзя заменить это ещё одним prompt «прочитай DOM».

Ревизия mockup: `1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf` (совпала с заданной). Source ledger: `runtime/AU006/source_ledger.json` (55 exact snapshots; каждый с sha256). Псевдонимы P=проект, H=harness, O=установленный plugin/omh, X=установленный Hermes source; абсолютные пути в ledger. Диапазоны ниже привязаны к его хешам, не к будущему live-коду.

### Что действительно исполнено

- Канонический повтор `runtime/AU006/recheck`: 53 / 53 проверок ожидаемых атак/контролей, 17 собственных MCP-процессов. Это PASS корректности воспроизведения, **не PASS продукта/TBO**. Сырые stdin/stdout JSON-RPC, stderr, PID/command/exit и независимые SQL readbacks сохранены.
- Отдельно 5/5 standalone проверок **существующего** OMH evidence-reducer на собственных state.db: `runtime/AU006/host_fixture_recheck/results.json`. Это source-bound fixture, не live session/close.
- Реальный kill после сохранения pending candidate; новое PID, replay, конфликт, ручной reread/rebase и повтор допуска. Один exit=1 — намеренно убитый процесс, остальные MCP exit=0. Все собственные subprocess завершены.
- Первичный прогон сохранён отдельно; после исправления только typing/pipe checks в собственных probes сделан полный повтор на новых disposable fixtures. Drivers frozen до канонического повтора. Product не менялся.

## Исходное поручение — дословно

«и так - остается вопрос-  взаимодейсвтия-  DOM и OMH -   первй этап мы обсудили-  пункты плана  OMH создают базовые ветки клаймов- дальше агент в проессе выполнения задачи обновляет и ведет эти ветки - тут нехватает правила и требования которое обеспечивает обязанность ведения этих веток и  правил   которые регламентируют выполнение новой задачи предварительно сверевшись с калймами связанными с пунктом плана ?  это нужно уточнить и прогнать аудитора  проверь не забыл ли я что то ещё по этому вектору?»

Прямое требование заказчика не равно всем предлагаемым полям TBO. TBO-01..10 — проект регламента; ContextPack/AcceptedBasis/UseReport — проекты RS003, не API. O1/O2/O3 сохранены, повторных вопросов по ним нет.

## TBO-01..10 — матрица

| Правило | Реализовано / проверено локально | Host-связь и остаток |
|---|---|---|
| **TBO-01** Привязка задачи и основания | WORK/TASK/POLICY fixture binding; branch heads; idempotent dom_init for same fixture; Repeated init leaves one binding and two heads; wrong fixture TASK is SCOPE_DENIED | Existing todo and continuation dossier are native OMH, but no traced DOM import/handshake between them; no real plan edited. **GAP:** No OMH item-text/hash/version ingestion or stable task pin; no run binding; real todo uses position+prefix and same-text pairing, not globally stable item identity; roots across real sessions unverified |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-01: `P:mockup/storage.py:54-99; P:mockup/admission.py:119-155; O:todo_store.py:230-281,327-423,880-1076,1138-1157; O:completion_store.py:228-297,350-410; P:mockup/ports.py:1-39,64-82`; evidence: `runtime/AU006/recheck/r01_no_read/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r03_bases/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
| **TBO-02** Предварительная сверка и выдача контекста | dom_query historical snapshots, provenance, resume snapshots; No-read author with pre-existing admitted baseline and explicit-read control both admitted another claim with empty bases | pre_llm_call injects bounded role/todo/status guidance, not DOM task-claim context (O:hooks/llm_hooks.py:488-729). **GAP:** No mandatory context issue/read/use gate; no ContextPack/AcceptedBasis consumer; iterative graph search API absent; receipt cannot prove understanding |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-02: `P:mockup/admission.py:119-155; P:mockup/dom_contract.py:6-17,63-121; P:mockup/server.py:36-134; P:runtime/RS003/contracts.schema.json:3-5,154-376,445-554; P:docs/ITERATIVE_CLAIM_SEARCH_2026-11-08.md:3-53`; evidence: `runtime/AU006/recheck/r01_no_read/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r02_with_read/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
| **TBO-03** Контроль исполнения на доверенной границе | Scope/capability/schema and exact digest checks; same-root review refusal; non-simulation init fails closed; Self-root review and author admission refused; live binding refused; no-read admission passes in fixture | Real pre_tool callback exceptions/timeouts can block at host; OMH rules catch some failures and return allow; outer dispatch errors can also fall through. None of these paths checks DOM baseline; no live hook run. **GAP:** No attested task/run/context admission condition; launch roles are simulation, not identity; terminal/files can bypass MCP |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-03: `P:mockup/admission.py:164-220; P:mockup/ports.py:1-39,64-82; O:hooks/tool_hooks.py:61-116,119-331; X:hermes_cli/plugins_dispatch.py:59-67,275-324; X:hermes_cli/plugins.py:1907-2048; X:model_tools.py:759-794; O:plan_stage_gate.py:156-235`; evidence: `runtime/AU006/recheck/r06_controls/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r01_no_read/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
| **TBO-04** Ведение ветки по существенным изменениям | Immutable candidates/claims/events; reason, author, time and source version; admission outbox; Artifact-only result is invisible to trace; pending candidate not treated as completed branch maintenance | Host file-write evidence is generic activity, not required DOM branch maintenance. **GAP:** No meaningful-update checkpoint/no-op semantics or actual tool-result/artifact-to-branch reconciliation; automatic review is demo-only |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-04: `P:mockup/admission.py:119-155; P:mockup/admission.py:164-220; P:mockup/projections.py:29-77; P:mockup/admission.py:254-283`; evidence: `runtime/AU006/recheck/r04_completion/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
| **TBO-05** Отклонения и конкуренция | Expected branch revision and declared branch dependencies checked inside admission transaction; Revision conflict preserves candidate; explicit AB pin becomes STALE_REVIEW; omitting pin after old AB read admits; manual rebase succeeds | No traced host contract binds actual consumed bases to declared dependencies or handles rebase automatically. **GAP:** Caller can omit actual bases; no claim-version affected-only revalidation; immutable old pin remediation remains TD-DOM-15; no FORKED/refinement API |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-05: `P:mockup/admission.py:164-220; P:mockup/dom_contract.py:6-17,63-121; P:mockup/projections.py:29-77; P:tech_debt.md:12-24`; evidence: `runtime/AU006/recheck/r05_restart_stale/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r05_restart_stale/after_conflict.sql.json`
| **TBO-06** Изменение плана/условий/прав | Provenance fields and static launch grants in fixture | Host todo advance checks current position/prefix; completion dossier compares caller-declared revision/environment. Neither is DOM criterion/grant revalidation. **GAP:** No live plan pin_behind, grant-revocation-after-read, criteria revision or task reassignment enforcement; prefix guard is not full-text revision binding; O2 accepted, not re-opened |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-06: `O:todo_store.py:230-281,327-423,880-1076,1138-1157; P:mockup/ports.py:1-39,64-82; P:runtime/RS003/contracts.schema.json:3-5,154-376,445-554; P:docs/DECISION_BRIEF_2026-11-08.md:97-116`; evidence: `runtime/AU006/source_search.json`
| **TBO-07** Завершение и отсутствие новых знаний | trace reports coverage/currentness/conflicts/convergence/sync; owner_close_called=false; READY-for-review remains true with material unrecorded result, pending candidate, rejected input and uncorroborated no-new-knowledge comment; host reducer fixture closes generic pass/file-write or empty MCP-only window | Todo binds observed tool call ids in time windows; this does not prove command relevance or DOM admission/delivery; checkpoint remains model_declaration/not_verified. **GAP:** No independent result-vs-baseline/no-new-knowledge assessment; no task-scoped pending/rejected disposition at close; no live false-DONE/close test |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-07: `P:mockup/projections.py:29-77; P:mockup/admission.py:254-283; O:todo_evidence.py:9-68,94-98,165-209,248-297,350-427,497-529; O:todo_reconciliation.py:609-710,821-908; O:completion_store.py:228-297,350-410`; evidence: `runtime/AU006/recheck/r04_completion/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/host_fixture_recheck/results.json`
| **TBO-08** Доставка и закрытие | Local atomic outbox, delivery attempts/observations/acks; DOM does not call owner close; Simulated sync readback; trace never called owner close | Delivery and owner acceptance correctly not conflated in mockup; live bridge/independent acceptance gate remains GAP/UNVERIFIED. **GAP:** OMHPort is local JSON target only; no real owner-close consumer tested; O3 full projection receipt correctness owned by AU005, not re-audited here |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-08: `P:mockup/admission.py:324-381; P:mockup/ports.py:1-39,64-82; P:mockup/admission.py:254-283; O:completion_store.py:228-297,350-410`; evidence: `runtime/AU006/recheck/r04_completion/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
| **TBO-09** Сбой и повторная сессия | SQLite durable candidate storage; submission/admission idempotency; scoped resume snapshots/outbox; Actual author process killed; new PID resumes same store; identical submit recovers candidate; conflict preserves it; manual reread/rebase works; repeated admit same tx; payload mismatch refused | Native OMH continuation dossier exists; not a DOM resume/input-use bridge. No provider call required for local DOM reads/admission. **GAP:** Resume does not enumerate pending candidate/payload/key; no pending discovery API; DOM/LLM outage policy and all crash windows not tested |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-09: `P:mockup/admission.py:383-392; P:mockup/server.py:36-134; P:mockup/admission.py:119-155; P:mockup/admission.py:164-220`; evidence: `runtime/AU006/recheck/r05_restart_stale/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r05_restart_stale/resume_after_kill.json`
| **TBO-10** Делегирование и контроль обходов | Fixture server identity fixed at launch; no tool role override; root separation; No-read path, wrong TASK, unknown receipt-field, stale/omitted deps and repeat-key negatives; standalone host reducer sensitivity controls | subagent_start/stop observe lifecycle, never require DOM baseline; no live delegation performed. **GAP:** No explicit child DOM baseline handoff/capabilities tied to parent; foreign task/principal read receipt replay cannot be tested because receipt API absent; actual dispatch/terminal containment unverified |

Источники матрицы (sha256 каждого — в JSON и ledger):
- TBO-10: `P:mockup/ports.py:1-39,64-82; P:mockup/server.py:36-134; O:hooks/tool_hooks.py:61-116,119-331; O:hooks/session_hooks.py:28-80; O:todo_evidence.py:9-68,94-98,165-209,248-297,350-427,497-529`; evidence: `runtime/AU006/recheck/r03_bases/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r06_controls/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/host_fixture_recheck/results.json`

## Находки — что НЕ обеспечивает обязательность

### AU006-F-01 [blocking] Предварительная сверка не является условием submit/review/admit

- Класс: **KNOWN_GAP_RECONFIRMED_NEW_STDIO_PATH**. TBO-02/03/10: before substantive execution, issued task baseline must be checked on a trusted boundary.
- Воспроизведение: R01: seed admitted A in AA rev1 with different process; fresh author init -> submit result B at rev1 with dependencies={} and requirement_refs=[]; reviewer init session -> review -> admit, no dom_query/snapshot/resume. R02 repeats on independent fixture after explicit query.
- Ожидалось: Without required issued/used task baseline the execution/admission path cannot count as compliant.
- Наблюдалось: **Both paths DEMO_ADMITTED at rev2; no-read raw frames contain no baseline read. No input or persisted read condition differentiates the paths. Does NOT establish that all agents never read or understand context.**
- Последствие: Obligation currently rests on agent obedience; valid hashes/independent fixture root do not establish prior context use.
- Prior: AN005 C-04/CD-06, TBO doc §2 (known absence, now direct own wire repro). Это не дублирующая регистрация/закрытие TD.
- Источники: `P:mockup/admission.py:119-155`; `P:mockup/admission.py:164-220`; `P:mockup/dom_contract.py:6-17,63-121`
- Evidence: `runtime/AU006/recheck/r01_no_read/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r02_with_read/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
- Следующий различающий тест: Authorized isolated host E2E: allow discovery/read/recovery, refuse material write without exact task baseline issuance/use basis, then allow current authorized context; record real principal/run. No blanket deny-all gate.

### AU006-F-02 [major] Проверяются заявленные зависимости, но их достаточность обходится пропуском

- Класс: **KNOWN_TD15_AND_BASIS_GAP_NEW_REPRO**. TBO-01/02/05/07: current relevant bases and exact requirement coverage, not just field shape.
- Воспроизведение: R03 unknown requirement R-NOT-IN-PLAN + demo:nonexistent-claim evidence is submitted/reviewed/admitted; missing field rejected. R05 read AB rev0; move AB to rev1; candidate with AB:0 rejected, same workflow omitting dependency admitted.
- Ожидалось: Declared references must be resolvable/adequate or explicitly root/hypothesis/disputed; independent semantic review must not be inferred from schema.
- Наблюдалось: **Unknown bases admitted by demo path. STALE_REVIEW correctly protects a declared pin, but dependencies={} bypasses the stale test; empty requirement_refs also admitted. Not a claim that real independent human review would approve false content.**
- Последствие: Fresh-looking candidate can omit actual known old inputs; fields/policy digest are not a task baseline pin or independent adequacy proof.
- Prior: TD-DOM-15; AN005 CD-05/CD-06; RS003 AcceptedBasis/Grounds are proposals. Это не дублирующая регистрация/закрытие TD.
- Источники: `P:mockup/dom_contract.py:6-17,63-121`; `P:mockup/admission.py:119-155`; `P:mockup/admission.py:164-220`; `P:mockup/projections.py:29-77`
- Evidence: `runtime/AU006/recheck/r03_bases/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r05_restart_stale/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
- Следующий различающий тест: After trusted issuance, test missing/unknown/wrong task/outdated bases separately from valid root inputs and independent dissent. A known wrong fixture TASK refusal is not arbitrary OMH integration.

### AU006-F-03 [major] READY-for-review не учитывает несведённый результат и pending кандидата

- Класс: **NEW_COMPLETION_BOUNDARY_REPRO_WITH_PRIOR_LIMITS**. TBO-04/07: unadmitted/pending/rejected work cannot stand in for completed branch maintenance.
- Воспроизведение: R04: admitted R1/R2 coverage + converge + sync => READY. Write actual disposable new_result.txt without DOM; submit material contradictory pending candidate; attempt incomplete rejected result; append bare no-new-knowledge comment and sync. Query trace/resume between stages; independent SQL.
- Ожидалось: A task close controller must reconcile actual result and every mandatory candidate disposition; pending is not accepted truth.
- Наблюдалось: **At every stage READY-for-owner-review remains true. Final SQL candidates=4, transactions=3, claims=1; pending candidate persists with no admitted tx. Resume does not surface it. owner_close_called remains false: NOT a reproduced real OMH close.**
- Последствие: A host treating READY as sufficient global compliance can miss branch maintenance. Correctness of narrow admitted-fact trace is not enough for task lifecycle obligation.
- Prior: TD-DOM-14 scope and TD-DOM-18 convergence latch are related but distinct; no new TD registered. Это не дублирующая регистрация/закрытие TD.
- Источники: `P:mockup/admission.py:254-283`; `P:mockup/projections.py:29-77`; `P:mockup/admission.py:383-392`
- Evidence: `runtime/AU006/recheck/r04_completion/after.sql.json`, `runtime/AU006/recheck/probe_results.json`
- Следующий различающий тест: Authorized isolated host completion E2E for artifact-only, pending-only, rejected-only, justified no-new-knowledge, and pure self-report; prove exact owner refusal/acceptance and no forged close.

### AU006-F-04 [major] После рестарта pending сохранён в SQL, но не обнаруживается через resume

- Класс: **FUNCTIONAL_RECOVERY_GAP_RUNTIME_CONFIRMED**. TBO-09: recover same work, pending candidates and exact baseline after process loss.
- Воспроизведение: R05 persist candidate, kill author PID, start new author PID, dom_resume(AA), inspect SQL; resubmit with externally retained original payload/key, provoke conflict, reread/rebase new candidate, repeat admission.
- Ожидалось: Resume/discovery should expose authorized pending work and enough recovery identity, not require old client memory.
- Наблюдалось: **SQL retains pending candidate; resume returns snapshot/trace/sync/read_snapshot only, no pending ids/payload/keys. Original key+payload replay recovers same id; manual rebase preserves body; repeated admission returns same tx. No loss of SQL facts was observed.**
- Последствие: Durable storage does not alone solve loss-of-baseline after session restart; without the old key the MCP client has no pending discovery path.
- Prior: REQUIREMENTS §5.5/§6; AN005 D-14 (pending journal scope); TD-DOM-15 revalidation distinct. Это не дублирующая регистрация/закрытие TD.
- Источники: `P:mockup/admission.py:383-392`; `P:mockup/server.py:36-134`; `P:mockup/admission.py:119-155`; `P:mockup/admission.py:164-220`
- Evidence: `runtime/AU006/recheck/r05_restart_stale/after.sql.json`, `runtime/AU006/recheck/probe_results.json`, `runtime/AU006/recheck/r05_restart_stale/after_conflict.sql.json`, `runtime/AU006/recheck/r05_restart_stale/resume_after_kill.json`
- Следующий различающий тест: New isolated client with NO old candidate id/key/payload must discover its authorized pending work, retain candidate through rebase and avoid duplicates. Do not simulate a missing graph/queue API.

### AU006-F-05 [major] Нативный todo-evidence доказывает активность, не выполнение DOM-обязанности

- Класс: **SOURCE_BOUND_STANDALONE_FIXTURE_NOT_LIVE_CLOSE**. TBO-07/08: completion evidence must relate to exact requirement, DOM branch maintenance and delivery, not any successful tool result.
- Воспроизведение: Run actual standalone todo_evidence.py against own disposable state.db: unrelated terminal exit0, failing terminal control, only MCP dom_submit REJECTED, only file_write, absent tool ref. No plugin hooks registered or run.
- Ожидалось: A task-specific completion contract cannot infer baseline reconciliation or DOM acceptance from unrelated exit0/file_write or an unrecognized MCP-only window.
- Наблюдалось: **Reducer returns closed / failed / window_empty / closed / unresolved respectively. EVIDENCE_TOOLS only terminal/write_file/patch; no DOM result binding. In native source, unverified_done_items counts window_empty as closed; completion dossier remains model_declaration and not_verified (a correct limitation).**
- Последствие: Even stronger observed activity evidence does not establish task-relevant check or admitted/delivered DOM result. No claim that a live OMH task was actually closed by these fixtures.
- Prior: todo_evidence.py:53-68 explicitly states time-not-content limitation; AN005 hooks findings narrower. Это не дублирующая регистрация/закрытие TD.
- Источники: `O:todo_evidence.py:9-68,94-98,165-209,248-297,350-427,497-529`; `O:todo_reconciliation.py:609-710,821-908`; `O:tools/todo_tool.py:221-357`; `O:completion_store.py:228-297,350-410`
- Evidence: `runtime/AU006/host_fixture_recheck/results.json`
- Следующий различающий тест: Authorized host run with task-labelled checks and DOM results: an unrelated successful command and rejected/pending MCP operation must not discharge required task-baseline obligations; valid no-new-knowledge stays possible.

## Source-bound host: поправка к AN005 и реальная граница

Нельзя повторять «все хуки fail-open». В текущем `X:hermes_cli/plugins_dispatch.py:59-67,275-324` pre_tool callback timeout/exception даёт block; `X:hermes_cli/plugins.py:1907-2016` читает block/approve и fail-closed human approval. Это настоящий механизм до вызова tools в прочитанном source. Однако `O:hooks/tool_hooks.py:61-116,133-199` сам превращает некоторые ошибки rules/home binding в allow/no actionable directive; `X:model_tools.py:759-794` при исключении самого dispatch логирует и продолжает. `plan_stage_gate.py:156-235` — только установленный awaiting_acceptance на own fresh todo и file edits, не проверка DOM. Не объявлять любую из этих веток доказанной live-политикой без разрешённой пробы.

На завершении `X:agent/turn_stop_gates.py:53-77` вызывает pre_verify лишь при edits/hook/доступном budget; OMH `hooks/verify_hooks.py:59-81` требует coding+paths и возвращает continue-nudge, а при binding failure молчит. Поэтому исследования/писательство/MCP-only работа не покрываются общей обязательной finish-проверкой этой ветки. Native continuation dossier (`completion_store.py`) существует и честно оставляет результат **not_verified**, **model_declaration**, **observed=false**. Нельзя утверждать, что в OMH вообще нет checkpoint, и нельзя приписать этому checkpoint отсутствующий trusted DOM admission/close.

Фабрика тоже не пуста: `H:scripts/code-factory/code_factory_runner.py:144-177` требует provenance/guard для referenced artifacts и PASSED перед finalize; reducer `state_reducer.py:94-125,213-254` вычисляет typed gates. Но inspected start/finalize не связывают DOM baseline read/use/admitted updates/delivery. Reglement хука старта/приёмки в `ORCHESTRATOR_WORKFLOW_AND_CLARIFICATIONS.md:11-46` — обязательное правило, не runtime доказательство. `21_SESSION_AGENT_INTEGRATION_PLAN.md:8-14,103-125` прямо отделяет план от live E2E.

Поиск точных DOM/context marker names в 20 перечисленных source-файлах host/plugin/factory дал 0; его scope и hashes сохранены в `source_search.json`. Это дополнение к traced handler flow, **не доказательство отсутствия во всех host/harness деревьях**. Конфиги, secrets, live state не читались.

## GAP / UNVERIFIED

- **AU006-G-01 P0 — Нет подтверждённого контролирующего host start/write/finish контура DOM** [GAP_SOURCE_BOUND_AND_LIVE_UNVERIFIED]: Traced OMH/hooks/native completion and four factory controller sources contain no DOM context issuance/use/close binding. Real mechanisms exist for other purposes; lexical zero is not proof of absence across every host/harness path. Live configuration, enabled plugins and actual caller path were intentionally not probed.
- **AU006-G-02 P0 — OMH-пункт не пинится как точный снимок; нет автоматической ingest/init корней** [GAP]: Todo item has no stable id; advance checks position+prefix, whole-list pairing by same text. updated_at is not immutable item history. Native dossier freezes scope, but acceptance/revision are declared and no DOM linkage was traced. Fixed WORK/TASK cannot validate arbitrary OMH tasks.
- **AU006-G-03 P1 — Основной iterative claim search, refinement/FORKED и ContextPack — не действующий API** [GAP_NOT_SIMULATED]: Actual tools/list has 12 tools; no graph/neighbor/search/task-start/context receipt/refinement endpoint. SEARCH-USE-01..08 cannot pass on this product. RS003 proposed schema is not runtime code.
- **AU006-G-04 P0 — Principal/run, изменение грантов и subagent baseline handoff не связаны с DOM** [GAP_AND_LIVE_UNVERIFIED]: Static launch identity/scopes in simulation; observer callbacks do not authorize inherited claim-version scope. No receipt to replay across foreign task/principal exists; rejection of unknown fields is not receipt-binding enforcement.
- **AU006-G-05 P1 — Meaningful update/no-op, no-new-knowledge, affected-only revalidation не определены исполнимо** [POLICY_ONLY_AND_KNOWN_TD15_18]: Branch-level dependency hashes and converge latch cannot replace claim-version semantic revalidation. O1 forbids false READY; do not cure stale deadlock by dropping actual pins. Thresholds/checkpoint intervals are research parameters, not selected rules.
- **AU006-G-06 P0 — Доставка в simulation target не есть приёмка живым OMH** [SIMULATION_LIVE_UNVERIFIED]: Local JSON attachment readback was observed; real task evidence attachment, owner acceptance and O3 complete-vs-scoped projection acceptance remain unverified here. AU005 owns O1/O2/O3 security retest; no duplicate full sweep.
- **AU006-G-07 P1 — Политика DOM/LLM outage, repair и полезной работы вне DOM не выбрана** [NEEDS_RESEARCH_NEEDS_USER]: Do not claim blanket fail-open or fail-stop. Read/discovery/repair must remain usable before material-work gate; no false DONE. Scope and restoration/exception approval belong to owner decision.

## Что ещё необходимо формализовать, чтобы DOM помогал работе

1. **Init/идемпотентность:** точный item snapshot и стабильная сшивка при одинаковых текстах, reorder/split/rename; повторная сессия не создаёт новые материнские корни. Локальная idempotent init не доказывает plan ingestion.
2. **Meaningful-update/no-op:** необходимость записи определяется новым основанием/решением/результатом/конфликтом, не счётчиком tool calls. Отсутствие новых знаний допустимо, но сопоставляется с реальным результатом и прежними основаниями независимо.
3. **Use не понимание:** выдача байтов, declaration использованных refs и независимая проверка достаточности — разные стадии; receipt/хеш не доказывает понимание LLM.
4. **Смена плана/прав и affected-only:** не скрывать stale (O1), не перепривязывать по позиции, не сбрасывать все задачи из-за чужого нерелевантного обновления. Нужен путь reread/rebase/revalidation с сохранением кандидата.
5. **Subagent handoff:** parent task/baseline, точные версии, child run и отдельные права, отзыв грантов; callback «child пришёл/вернулся» не является приёмкой результата.
6. **Resume:** durable SQL, видимый pending recovery и память клиента — три разные вещи. Новая сессия не обязана помнить старый idempotency key.
7. **Delivery/acceptance split:** DOM admission, наблюдаемая доставка нужной проекции по O3 и независимая приёмка OMH — разные эффекты; READY-for-review не DONE.
8. **Controlling host / обходы:** карта всех материальных инструментов, включая terminal/files; где нет containment, гарантия policy-only. Не запрещать discovery/read/диагностику/repair до выдачи контекста.
9. **Отказ DOM/LLM/hooks:** сопоставить риск-ограниченные варианты (остановить только материальные изменения; bounded offline journal без DONE; approved exception с reconciliation). Кто разрешает/контролирует восстановление — owner decision после исследования. Не выбирать молча fail-open/fail-stop или интервал checkpoint.

## Вопросы следующему аналитику

- **QA006-01 [P0]** Какой существующий host/dispatch/completion компонент владеет обязательностью TBO и какой точный разрешённый isolated live E2E докажет его вызов до материальной работы и до закрытия? Ожидаемый материал: Trace map tool->host gate->task/run/claim pins->effect->independent close; test both no-context refusal and useful read/repair allowed.
- **QA006-02 [P0]** Как сшить реальный todo без устойчивого item id с immutable текстом/хешем пункта, включая одинаковые тексты, перестановку, split/rename, повторный старт и новую сессию, не пересоздавая план ради предупреждений? Ожидаемый материал: Contract and negative fixtures for exact item snapshot and idempotent plan-root ingestion; compare existing checkpoint rather than replace OMH.
- **QA006-03 [P0]** Какие исполнимые проверки доказывают выдачу точного контекста, declared use и независимую достаточность оснований, не приравнивая receipt/хеш к пониманию? Ожидаемый материал: Separate delivery, acknowledgment, use_report, independent use_checked; bind task/run/principal/source revisions/policy; foreign and stale replay negatives.
- **QA006-04 [P1]** Как основной итеративный поиск сохраняет исходный вопрос, frontier/visited versions и продолжение после лимита/stale/смены прав, не путая локальную depth 1..3 с длиной маршрута? Ожидаемый материал: Existing RS003 contract extension and SEARCH-USE-01..08 experiment plan; K1/K2/K3 only after comparative simulation; no implementation invented.
- **QA006-05 [P0]** Что контроллер сопоставляет с фактическими изменёнными артефактами/решениями, чтобы различить существенное обновление, no-op и обоснованное «новых знаний нет», а pending/rejected не были завершением? Ожидаемый материал: Semantic and deterministic checks separated; task-scoped disposition of candidates and evidence, no claim per tool call.
- **QA006-06 [P1]** Как переутвердить только затронутые точные версии и сохранить работу при конфликте без удаления pin, бесконечного stale и полного перезапуска из-за посторонней ветки? Ожидаемый материал: Alternatives for immutable revalidation/amendment; direct TD-DOM-15/18 regression; distinguish FORKED, pending and accepted.
- **QA006-07 [P1]** Как новый клиент без старых candidate id/key/payload обнаруживает authorized pending и недоставленные операции, продолжает ту же ветку и не создаёт корни/факты повторно? Ожидаемый материал: Resume/discovery contract, loss-of-client-state and process-kill acceptance tests; show existing mechanisms vs GAP.
- **QA006-08 [P0]** Какая граница доверия реально ограничивает terminal/files/direct SQL и переопределение principal/grant, и как передаются отдельные права/основания дочернему агенту? Ожидаемый материал: Threat model, existing sandbox/ACL/dispatch ownership and revocation checks; policy-only wherever no containment.
- **QA006-09 [P0]** Какие независимые критерии закрытия проверяет OMH после DOM admission и доставки, и как он не принимает unrelated exit0/file-write/self-report за TBO-compliance? Ожидаемый материал: Owner acceptance source and authorized real E2E; preserve O3 tx/recipient/source_revision/view_scope/byte_hash; do not ask O1/O2/O3 again.
- **QA006-10 [P1]** Какая риск-ограниченная fault policy оставляет чтение/диагностику/восстановление и разрешённую работу доступными при отказе DOM/LLM/hooks, но запрещает ложное DONE? Ожидаемый материал: Compare fail-stop material changes, bounded offline journal, owner-authorized exception; who controls recovery, how reconciled; thresholds remain research parameters.

## Не проверено и ограничения

- No live host hooks, plugins loading, real OMH task mutation, live acceptance or production identity tests: explicitly prohibited.
- No full AU005 security sweep; O1/O2/O3 receipt scope/provenance leakage fixes not independently re-audited here.
- No graph search/refinement/ContextPack E2E: API absent in inspected mockup; RS003 prototypes not substituted.
- No network, model/curator provider, Git command/install, additional agent, secrets or private user-state read.
- No all-window crash suite or kill during outbox send/commit: actual kill here is after pending submit; existing source mechanisms are not a crash-coverage claim.
- No live fail-open/fail-closed hook fault injection; host execution/configuration of read source may differ and remains UNVERIFIED.
- No exhaustive inventory of every host/harness worktree or controller; source_search scope is explicit and bounded.
- No direct filesystem attack on product/live DB; actual artifact-only write and all SQL fixtures confined to runtime/AU006.

## Находки (эскап-хэтч)

- Уровень 2: F-01..05/G-01..07 зафиксированы здесь и в JSON с source/evidence/prior refs. Product, tests, tech_debt, конфиги и чужой runtime не изменены; **debt_status_changes=[]**. Специальная карта AU006 запрещает запись реестра: новые TD не присваивались и старые не закрывались.
- Уровень 3: [ESCALATED] родителю/следующему аналитику — controlling host, real principal/grants, real OMH close, разрешённая isolated live проверка и fault policy. Родителю не дописывать иной вердикт за AU006.
- Уровень 1: правились только собственные audit probes (typing), затем оба прогона повторены; продукт не исправлялся.

## Выходы и завершённость

- `artifacts/AUDITOR_AU006_TASK_BASELINE.json` — полная матрица, sources/hashes, findings/gaps, вопросы, PID/command/exit.
- `reports/AUDITOR_AU006_TASK_BASELINE.md` — этот отчёт.
- `runtime/AU006/` — first PARTIAL, frozen source/driver ledger, canonical `recheck`, standalone `host_fixture_recheck`, raw frames, SQL readbacks, manifest/verifier.
- `verification.json` проверяет полноту/evidence и неизменность source; это проверка audit package, не product acceptance.

**AU006 continuation_required=false**: разрешённый аудит сдан. Остаток — продуктовые GAP и запрещённые без нового разрешения live-пробы, не замаскированное прохождение. **product_acceptance=false; is_approval=false; verdict=REQUEST_CHANGES.**
