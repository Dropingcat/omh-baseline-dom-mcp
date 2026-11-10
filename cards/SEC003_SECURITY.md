# SEC003 — негативная безопасность/межветочная изоляция

Статус PREPARED / НЕ DISPATCHED. Исполнитель не product worker и не принимающий. Parent проверяет PL003, применяет подготовленную OMH delta и выдаёт dispatch; эта карта не даёт live-разрешений.

## Миссия и слова заказчика — дословно

после  цикла обнови план OMH по тестированию сценариями как записи так и чтения обновления  выборочный поиск - поиск по веткам-  на предмет протечек из дроугих веток. создать через планера план тестирования и предварительный поиск местотказа-  где будет утечки где проблемы- и эти места и становятся  чеками для проверки и симуляций. - нужен прогон спеца по зеопасночти и тестированию - нужен шаблон новый для контракта по этому очень жосткий ядреный  работающия не на положительный результат а с ветором на заваливание и негатив

Опровергать гарантии по реальному пути, не искать зелёный отчёт; допустимо не найти новый дефект, недопустимо выдумывать находку или скрывать known failure. Фабричный порядок PL003 → SEC003 → QA003 → независимый reviewer → негативный auditor. Ни один исполнитель не принимает собственную работу.

## Вход и зависимости

P=`E:/opencode_harness_portable/projects/omh-baseline-dom-mcp`.
Текущий code digest `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3`; это byte fingerprint, не Git revision. На dispatch снять заново все mockup/**/*.py hashes тем же sorted-json методом, схемы и env. Полные обязательные входы:
- `REQUIREMENTS.md`
- `templates/NEGATIVE_E2E_SECURITY_CONTRACT.md`
- `docs/FULL_IMPLEMENTATION_PLAN.md`
- `docs/NEGATIVE_E2E_PLAN.md`
- `runtime/PL003/capability_inventory.json`
- `runtime/PL003/failure_map.json`
- `runtime/PL003/scenario_plan.json`
- `runtime/PL003/input_fingerprints.json`
- `runtime/PL003/support_input_hashes.json`
- `runtime/PL003/omh_plan_delta.json`
- `artifacts/PLANNER_NEGATIVE_E2E.json`
- `reports/PLANNER_NEGATIVE_E2E.md`
- `artifacts/RESEARCHER_AB002_A.json`
- `reports/RESEARCHER_AB002_A.md`
- `artifacts/AUDITOR_AB002_A.json`
- `reports/AUDITOR_AB002_A.md`
- `artifacts/REVIEWER_AB002_A.json`
- `reports/REVIEWER_AB002_A.md`
- `artifacts/ANALYST_AB002_A.json`
- `reports/ANALYST_AB002_A.md`
- `cards/AB003_TD19_WORKER_PREPARED.md`
- `tech_debt.md`
- `mockup/README.md`
- `E:/opencode_harness_portable/docs/CODERS/03_ACCEPTANCE.md`
- `E:/opencode_harness_portable/docs/CODERS/05_REVIEWER_AUDITOR_TECHDEBT.md`
- `E:/opencode_harness_portable/docs/CODERS/07_AUDITOR_DILIGENCE.md`
- `E:/opencode_harness_portable/docs/CODERS/09_FINDINGS_ESCAPE_HATCH.md`
- `E:/opencode_harness_portable/docs/CODERS/10_CHAIN_CONTRACTS.md`
- `E:/opencode_harness_portable/shared/code-factory-process.md`

**Dependency:** completed PL003 material + parent validation/dispatch. AU002-A REQUEST_CHANGES сохранён. P0 worker fix не подменяется этим security run. Нельзя ждать будущего SEC PASS, чтобы считать TD19 настоящим.
## Реальный маршрут и доверенная топология

Только при dispatch родителем. PY=`E:/opencode_harness_portable/.venv/Scripts/python.exe`, CWD=P.
Не запускать глобальный `mockup.ab002_e2e`: его OUT пишет runtime/AB002_A и shared manifest вне своего write scope.
Самостоятельный runner в своём runtime реализует raw stdio MCP initialize → notifications/initialized → tools/list → tools/call с корреляцией request IDs. Реальный server module `mockup.server` и `serve(Service, log_path)`; не fake responses. Стандартная положительная CLI:
`PY -B -m mockup.server --directory <own-run>/fixture --role author --simulation --log-file <own-run>/safe-log.jsonl`.
Это символическая argv с выделенным own-run, НЕ команда, уже выполненная планировщиком.
Для AA-only/AB-only и unknown fixture нужен собственный trusted test launcher в runtime роли: создать `Service(directory, role=..., simulation=True, branches=('AA',))` и вызвать реальный `serve`; caller аргументы не задают Context. У stock CLI нет --branches. Reference read-only `runtime/AU002_A/launch.py`; fault hooks доступны в admission и `mockup.ab002_launcher`, но писать/модифицировать их нельзя. Launcher может только назначить fixture identity, осмысленно pause/fault и реальные exit71 по названной стадии; не подменять ожидаемый ответ/guards/serializer/oracle. Liar mode — явно маркированная fault injection существующего simulation-порта, не достоверный ответ внешней системы.

Одна disposable DB на WORK=`demo:existing-work-W1`, TASK=`demo:existing-task-AA001`, POLICY берётся из актуальной fixture, не перепечатывается выдуманным hash. AA/AB: actor-A read+submit AA, actor-B read+submit AB, reviewer AA review/admit root-B, reviewer-allowed ограничен AA, helper root-A не независим от author, owner root-C только с явными grants, union AA+AB с явным разрешением. Unknown context через trusted launcher получает no positive grants; неизвестный --role stock CLI только launcher refusal, не тест MCP unknown-principal. No-simulation init должен отказать. Два действительных WORK и третья ветка отсутствуют: GAP, а не самовольное редактирование WORK/schema.

Trusted fixture oracle запускается отдельно от actor-A: он знает B canaries/IDs, делает read-only SQL/file reads и сохраняет operator-only receipts в своём run/oracle. Actor-A получает только MCP responses; не передавать ему полную БД, oracle map, путь/handle к foreign bytes. Это логическая граница harness, не сильная OS-изоляция. Агент с terminal/files и OS-admin — отдельные threat models, TD06/08 не оправдывают MCP leak. Не фильтровать stdout после того, как foreign bytes уже попали actor.

## Обязательное собственное покрытие

Точный список — все check_ids `runtime/PL003/failure_map.json` и linked scenarios `runtime/PL003/scenario_plan.json`. На каждый выдать статус, missing API остаётся GAP. Основной фокус SEC: permissions, known TD19, nested DTO/errors, write/reference joins, sharing/history/export/logs; проверить security-sensitive delivery proof. Availability cases передать QA с точными status/омиссиями, не claim что выполнены SEC.
Primary scenarios: SC-LP-A2-01, SC-LP-A2-02, SC-LP-A2-03, SC-LP-A2-04, SC-HP-PL-01, SC-HP-PL-02, SC-HP-PL-03, SC-HP-PL-04, SC-HP-PL-07, SC-HP-PL-11, SC-HP-PL-12, SC-HP-PL-13, SC-HP-PL-14, SC-HP-PL-15, SC-HP-PL-16, SC-H-LINK.
Семь унаследованных LP-A2-01…07 / CHK-A2-01…07 сохраняют state/evidence из RS002 planner_handoff дословно в inherited_point. Все check_id (CHK-A2-01, CHK-A2-02, CHK-A2-03, CHK-A2-04, CHK-A2-05, CHK-A2-06, CHK-A2-07, CP-PL-01, CP-PL-02, CP-PL-03, CP-PL-04, CP-PL-05, CP-PL-06, CP-PL-07, CP-PL-08, CP-PL-09, CP-PL-10, CP-PL-11, CP-PL-12, CP-PL-13, CP-PL-14, CP-PL-15, CP-PL-16, CP-PL-17; CP-PL-01…17) тоже учтены: роль не может забыть не-primary checks, но честно NOT_TESTED с передачей QA/приёмке, а не PASS. Seeds собственных runs `[3101, 3109]`; второй seed меняет начальные данные и order, не повторяет тот же synthetic log.

SEC обязан создать минимум одну собственную source-derived негативную вариацию сверх старой семёрки, например branch-scoped candidate/review replay или applicability/history join; это квота проверочной инициативы, не квота findings. 
H-LINK / CP-PL-17 / SC-H-LINK (новое требование заказчика, «Пятое уточнение», REQUIREMENTS.md:23-27: связи как в Obsidian — backlinks, соседи карточки, дашборды связей) — канал утечки со статусом GAP-LINKS / NOT_IMPLEMENTED: API нет. Роль обязана заново снять tools/list+AST; если link-sensing поверхности нет — записать GAP со схемными доказательствами, статус не PASS и не NOT_APPLICABLE; если появилась — код изменился, rebind плана через parent до зондирования. Backlink/счётчики/дашборды не раскрывают существование/число/ID объектов запрещённой ветки (differential при фиксированном AA и двух заполнениях скрытого AB). Snapshot-метаданные ссылок не заменяют этот чек.

Недоступный канал (search/cursor/refinement/diagnostic endpoint) нельзя молча пропустить, подделать или заменить snapshot/replacement. Точные GAP IDs остаются в result.
## Oracle, данные и физические квитанции

До негативов положительный контроль: own AA запись через dom_submit→independent dom_review→dom_admit, B-only реально читает B body/source/ID; исходное поле cannot-search помечено GAP, не выдать snapshot за поиск. Генератор seed+case+branch+field создаёт синтетические canaries в body/quote/link/comment/property/code/formula/origin/source/history. CRLF, NFD/Unicode supplementary, shuffled item order, current/stale/archive состояния сохранять точно; никакой PII/секретов. B control повторить после негативов. Неинформативный пустой результат/сломанный positive control => BLOCK.

Каждый case receipt: scenario_id/hypothesis_id/check_id/variant/seed; requirement и frozen source/input/env; actor grants; initial fixture and revision; точная argv/cwd, PID/start/end/exit, handshake/schema; все raw requests+responses без потери text, structuredContent, nested errors, logs/media/attachment fields; injection-stage receipt; expected и actual; independent before/death/after/recovery SQL/files; verdict и omissions. MCP isError/exit0 не означает domain-safe или отсутствие эффекта.

Read-back отдельным verifier, не service projection как единственный oracle: sqlite URI mode=ro + явный close всех handles; ordered rows ВСЕХ таблиц, schema/triggers и DB/file hashes; exact raw claim bytes/IDs/source/links/origin; target JSON и unrelated-key semantic equality, на отказе target byte equality; exports и temp-файлы, write log. На rejected write нет частичных candidates/facts/head/idempotency/outbox/attempts, кроме явно допустимого durable attempt sync (не смешивать этот случай с submit). Metadata global gate read itself не отключать. SQL JOIN ack→observation→attempt→outbox по intent/tx/digest/target; matched=1, raw hash/size/read_at; independently compare target bytes/YAML и full internal stamp. Не редактировать internal proof ради public sanitization. Полный locator порчи хранит отдельный fixture oracle, не restricted logs/text/structured/nested/export.

AA fixed / healthy hidden AB изменяется: рекурсивный field differential, исключение только документированного read_at. Не broad volatile mask, не один grep канарейки: сверять IDs/counts/seq/heads/hash/paths/структурные ссылки; B existence отдельно. При sharing сначала утверждённая object authorization: B origin в явно разрешённом shared claim не автоматически leak; неопределённый declassification contract => BLOCK/needs-user. Global CHAIN_BROKEN/NOT_READY разрешён как safe health signal, foreign locators запрещены. Safe Broken proposed exact {status:CHAIN_BROKEN, readiness:NOT_READY, ready_for_owner_review:false, blockers:[EVENT_CHAIN_BROKEN], simulated:true}; current product ещё не реализует. Timing не обещать: только заданная bounded exploratory серия и jitter control, нет замеров => NOT_CHECKED.

Run evidence: новый уникальный runtime/<ROLE>/run-<seed>-<uuid>/; до исполнения заморозить maps source/input/fixture/grants/injection/env (Python executable/version, mcp/PyYAML/SQLite/OS, без полного env/secrets). На source drift STOP/rebind plan, не смешать PASS ревизий. progress journal отдельно. Финальный manifest create-only в run-specific directory, exact byte hash вынести в own result evidence_ref вне manifest; refs каждого receipt с SHA256, source/input lineage, seed and case JSON pointer. latest только навигация. Missing/mismatch => BLOCK/MISMATCH без fallback. Первый, неудачный, flaky и прерванный run НЕ удалять; WORM/защита OS-owner этим не доказана.
## Строгий итог и границы

Первым собственный минимальный JSON PARTIAL/IN_PROGRESS с exact scope/remaining, копию сохранить first_artifact.json; никакого fake PASS. В финале свой JSON + MD, completion_state=completed только при полном собственном материале; verdict REQUEST_CHANGES/BLOCK/NO_VIOLATION_OBSERVED_IN_SCOPE, не SAFE/secure и не product acceptance. Каждому check ID назначить EXECUTED_NEGATIVE/CONTROL_FAILED/FINDING/GAP/NOT_TESTED с receipts и условиями (это состояния исполнения, не фиктивные тесты PL003). Findings: ID, severity impact-based, violated boundary/prerequisite/minimal repro/seed, expected/actual/raw evidence/source version, existing debt_ref или предложенный новый локальный finding; mitigation suggestion без product fix. TD19/20/21 не дублировать и не закрывать.

Report начинает раздел 0 «подозревал → проверил → оказалось», включая опровергнутые подозрения, known facts и UNVERIFIED; есть отдельный verdict, coverage/omissions/replay/recovery/limitations и НАХОДКИ (эскап-хэтч) уровней 1/2/3. Вне scope finding фиксировать в собственном JSON/MD и передавать parent для реестра — shared tech_debt.md здесь read-only. Нет квоты находок, no skip/xfail/broad-except-pass/fake logs/ответов/скрытых fallback/смены expected задним числом/правки продукта. Нельзя расширять grants, очищать inconvenient evidence, делать self-acceptance, закрывать OMH owner task.

TD19 известная major утечка: future plan/PASS не отменяет обязательный P0 fix cards/AB003_TD19_WORKER_PREPARED.md (не DISPATCHED). TD20 shape list raw AttributeError — finding, не correct refusal; list/null/scalar extension не выдавать за прежнее наблюдение. Базовый shape-failure FAIL_STOP, domain-safe отказ ожидается от будущего fix. Обязательный YAML continuation НЕ СОГЛАСОВАН, RS002-DEC-CONTINUE остаётся NEEDS_USER; не менять expected на continuation без решения. Integrity/storage inability to prove safety останавливает fanout в любом случае. Durable attempt не observation, отсутствие observation после proven pre-effect failure само по себе не A2 defect; after-send uncertain => ambiguous, no fake matched/ack. Partial YAML ack не общая SYNCED/READY.

Не более двух детей одновременно; RPC ≤25s, child ≤90s, role wall ≤1800s, payload ≤64KiB, ≤16 claims/branch, DB ≤16MiB, retained role evidence ≤128MiB, timing 12 randomized paired AA queries/seed после warmup, два seed по карте. Если объём/время/tool budget (120 calls ориентир) исчерпан, остановить только свои зарегистрированные PIDs, закрыть handles, сохранить raw evidence и точный remaining/next action/source/input/seed в continuation.json той же роли; parent НЕ дописывает verdict. Не уменьшать обязательное покрытие ради completed. Unexpected child nonzero/log error сохранить и классифицировать, не swallow. Cleanup только own PID/handles/temp resources после capture; сохранять доказательства, не удалять runs. Не kill-all.

Разрешены local read/search/write/patch/terminal и указанный Python, только собственные disposable fixture/processes. No network/listeners/install/Git/paid calls/real secrets/live user DB/live plugin/config/registry. Продукт, tests, live configs/plugins, researcher/старые evidence/debts — read-only. Не запускать других агентов, не применять OMH delta. Сильный OS sandbox/external checkpoint/live auth/Git/OMH не следуют из simulation. Не claim полного Cartesian coverage, full-system acceptance или all-channel noninterference.

## Разрешённые outputs и сдача

Запись ТОЛЬКО `P/artifacts/SEC003_SECURITY.json`, `P/reports/SEC003_SECURITY.md`, `P/runtime/SEC003/**`. Туда входят собственные launcher/runner/verifier (не product code), own fixture DB/files, `failure_map.json`, `scenario_manifest.json`, `first_artifact.json`, per-run immutable `manifest.json`, `raw-frames.jsonl`, command/PID/exit/env/grants receipts, before/after/recovery, controls, leak_scan, findings, `validation.json`, `continuation.json` при лимите. Все остальные пути read-only, включая PL003 и вторую роль. Не создавать эти будущие артефакты заранее как fake completed.

Свой JSON: role/task/status/verdict/completion_state/product_acceptance=false/is_approval=false/source+input+env fingerprints/scenario_manifest_ref/immutable evidence refs+hashes/checked_suspicions/findings/per_check/controls/coverage/limitations/not_checked/remaining/continuation_required/verified_by_commands/debt_status_changes=[]. Числа parse/count в Python, не вручную. Отдельный verifier проверяет все status/IDs/paths/hash/source/ack bindings и присутствие отчёта; успешный driver exit — не verdict. Финальный результат пишет сам исполнитель. Parent только после readback точного target и validation диспатчит следующее звено.
