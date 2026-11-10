# 0. Подозревал → проверил → оказалось

| Подозревал | Проверил | Оказалось |
|---|---|---|
| Old s1 AB-canary hits mean all provenance is a leak | Field-level raw frames + new O2 policy | Shared origin/body is allowed; non-provenance lists separately open, not all O2 closed. |
| s2 D2 proves union-first delivery | Read s2 code + inherited SQL acks | Invalid virgin control: copied S was already synced, and read_all exports before sync. Rebuilt virgin controls in s4. |
| O1 accepted means hide stale to close channel | Read steering/REQUIREMENTS section9 + clean differential | Do not hide. Current stale signal is honest; useful revalidation still missing TD15. |
| s2 negative replay means no receipt leak | AB original returned REVISION_CONFLICT; repeat successful AB admission | Confirmed separate cross-grant receipt replay in two PIDs. |
| s3 summary crash means product injections fail | Read complete raw frames + YAML + SQL | 38 claims/66 events admitted; later wire SYNCED and 132 actual acks. Client timeout/KeyError is harness defect; no fabricated final PID. |
| Gate regression exposes branch through corruption | 6 successful corruptions x2 PIDs x7 tools | 84 exact uniform Broken, no foreign locator, DB byte hash unchanged; NULL injection rejected by SQL. |
| Race test overlapping intervals alone proves mixed revisions | First race reader hit harness bound, saw revision1 only | Failed trial preserved, not PASS; new s6_continue02 sees heads1,2,3 and actual overlap without hits. |
| Branch ZZ granted should work consistently | Actual MCP matrix under trusted AA,ZZ | INTERNAL_ERROR on query/resume vs empty SYNC_STATUS/SYNCED; no raw/private leak. |
| Working resume means entire long-project goal works | Actual APIs + F-USE01..06 + SEARCH-USE01..08 acceptance | Stored baseline/history works. Graph/search, version tree, revalidation, live OMH are GAP, not E2E PASS. |
| Worker changed tests or forged precopy/manifests | Independent hashes/tests baseline/1714 manifest entries | All match, only3 source changes. Time-of-copy chronology not externally provable. |

## 1. Собственный вердикт AU005

**REQUEST_CHANGES. COMPLETE_WITH_LIMITS — завершён текущий ограниченный аудит, не приёмка продукта.**

Версия: `1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf`; 16 Python-файлов. `product_acceptance=false`, `is_approval=false`, `debt_status_changes=[]`.

Фильтр bmap не опровергнут проверенными случаями. Но AB004 как связка «ограниченная проекция → доставка» требует исправлений: F-01. Отдельно подтверждён опасный путь кешированного AB receipt через AA candidate (F-02). Полная цель долгого проекта НЕ готова: отсутствующие функции отмечены GAP, а не PASS.

## 2. Действующие решения заказчика

- **O1:** Accepted requirement: do not suppress staleness or create false readiness. Current honest signal is not itself a defect; recovery gap TD15 remains.
- **O2:** Accepted: available claim always keeps origin. No automatic source-branch access/current-head/dependency exposure. Non-provenance membership/exclude is separate.
- **O3:** Accepted: bind transaction+receiver+source revision+view scope+byte hash. Current code FAILS; not needs_user.
- **search:** Accepted main scenario iterative re-centering. Depth1..3 TEST_PARAMETER per response, not total route. No grant expansion. Graph/search GAP; keyword variants not selected.
- **AU006:** Separate obligation/enforcement audit; do not expand AU005 or consume unfinished conclusions.

Новые решения не применены задним числом к raw evidence: s1/s2 сохранены побайтно. REQUIREMENTS §9/поиск и последние добавления учтены в ledger. Последующий §10 — отдельный AU006; его незавершённые выводы не читались и не использовались.

## 3. Findings (по серьёзности)

### AU005-F-01 — major — AB004 integration / O3 scoped YAML delivery

**Инвариант:** An ack for a restricted view must not certify full delivery; identity binds transaction, receiver, source revision, view scope and delivered byte hash.
**Код:** `mockup/admission.py:293-301,331-347,372-381; mockup/delivery.py:44-65; mockup/delivery.py:8-18`
**Условия:** Virgin simulation DB: AB revision1, AA revision1 claim deps {AB:1}, no acks/exports; two separate copies AA-then-union and union-first.
**Воспроизведение:** s4_continue01.py delivery stage: dom_sync(AA) under {AA}, then dom_sync(AA) under {AA,AB}; compare SQL observations/acks and physical YAML with virgin union-first. Explicit export only AFTER both sync controls.
**Ожидалось:** AA ack says scoped AA projection; union must reconcile/deliver its distinct bytes and receiver/view-bound receipt. A full internal stamp alone is insufficient.
**Фактически:** Both return SYNCED; union-after-AA creates no new file/ack and retains {} dependencies; virgin union-first delivers {AB:1} with different fingerprint. Later explicit union export creates correct bytes but leaves old restricted ack untouched.
**Evidence:** runtime/AU005/s4_continue01/results.json:stages.delivery; runtime/AU005/continue01_verified.json:O3; runtime/AU005/s4_continue01/AA_then_union/dom.sqlite3; runtime/AU005/s4_continue01/union_first/dom.sqlite3
**Долг/граница:** RV005 O3 now physically reproduced; new debt candidate, not duplicate of TD-DOM-13 ack-before-readback. No debt status modified.
**Минимальный полный путь исправления (не выполнен):** View/receiver-aware delivery identity and receipt, with tx/source revision and exact bytes; preserve both projections without treating scoped ack as full; rerun sequential/reversed grant and lost-reply controls. No product fix performed.

### AU005-F-02 — major — OUT_OF_DELTA_SECURITY_FINDING: cross-grant idempotency replay

**Инвариант:** Current launch scope governs every tool result, including cached receipts; candidate/key/digest/receipt must bind to one operation before reuse.
**Код:** `mockup/admission.py:112-117,175-181; mockup/public_dto.py:155-159,374-376`
**Условия:** demo-reviewer previously participated in successful AB admission; same principal now restricted to AA; knows prior AB key/digest (e.g. lost response), has unrelated accessible AA candidate. AB claim was never shared into AA.
**Воспроизведение:** dom_query(AB) -> SCOPE_DENIED. dom_admit(AA_candidate, unrelated review_id, prior_AB_key, prior_AB_digest) -> cached AB receipt. Fresh key with that digest -> DIGEST_MISMATCH. Repeat new PID.
**Ожидалось:** No AB receipt; refuse mismatched binding or scope before returning cached result. Do not imply a new admission.
**Фактически:** PIDs 5248 and 3204 return exact AB DEMO_ADMITTED receipt incl branch AB, revision1, private claim UUID and tx_id; SQL confirms actual AB transaction. Replay creates no new facts.
**Evidence:** runtime/AU005/s4_continue01/replay/frames-84519d44.jsonl; runtime/AU005/s5_continue01/replay/frames-03617a79.jsonl; runtime/AU005/continue01_verified.json:replay
**Долг/граница:** NEW path, distinct from TD19 diagnostics and AU004-F-01 bmap; pre-existing admission path revealed by new conditions. s2 failed-AB-admission probe was not a negative proof.
**Минимальный полный путь исправления (не выполнен):** Bind and authorize cached receipt against requested candidate/intent/current scope before return; test narrowed grants, lost-response recovery, foreign/new keys and mismatched review IDs.

### AU005-F-03 — minor — O2 non-provenance branch-valued fields

**Инвариант:** Always-show-provenance does not authorize unrelated branch memberships/exclusion metadata; existing default scope rule remains outside that exception.
**Код:** `mockup/public_dto.py:71-75,100-105,113-121; mockup/projections.py:25,47,53; mockup/admission.py:277-283`
**Условия:** s1 F2 AA-only read: AA-origin a2 has original applicability [AA,AB]; owner exclusion AA->AB.
**Воспроизведение:** Read dom_query/dom_resume/dom_trace and YAML on AA with AA-only grant; compare exact fields, not all AB token occurrences.
**Ожидалось:** Retain origin of visible b1; unrelated membership/exclusion handling must satisfy scope or separately specified explicit disclosure policy.
**Фактически:** a2 origin AA exposes AB in ClaimItem.applicability; excluded_branches and visible exclude event expose AB. Those fields are not source provenance.
**Evidence:** runtime/AU005/continue01_reconciliation.json:O2_raw; runtime/AU005/s1/F2/frames-8c673884.jsonl
**Долг/граница:** RV005 O2 non-provenance remainder; do not duplicate allowed origin part or claim full O2 closure.
**Минимальный полный путь исправления (не выполнен):** Separate required provenance from membership/exclusion public policy and enforce resulting projection; preserve immutable internal admitted data.

### AU005-F-04 — minor — OUT_OF_DELTA robustness of granted nonexistent branch

**Инвариант:** A granted but absent branch is a typed absence/validation state, not internal processing failure or ambiguous success.
**Код:** `mockup/admission.py:111,230-233,245-251,325-381; mockup/server.py:212-224`
**Условия:** Trusted launcher grant {AA,ZZ}; only AA/AB exist. Invalid trusted grant is a fixture condition, not an attacker-controlled grant escalation.
**Воспроизведение:** s3 grant matrix AA_ZZ: dom_query(ZZ), dom_resume(ZZ), dom_sync_status(ZZ), dom_sync(ZZ).
**Ожидалось:** Consistent typed no-such-branch/invalid-grant result, no raw exception and no grant widening.
**Фактически:** query/resume INTERNAL_ERROR; sync_status empty SYNC_STATUS and sync SYNCED. No private bytes or raw locator disclosed.
**Evidence:** runtime/AU005/s3_continue02/checkpoint_gate.json:grant_matrix.AA_ZZ; runtime/AU005/continue01_verified.json:missing_branch_actual
**Долг/граница:** New robustness candidate related to TD-DOM-07 fixed-branch limitation, not a confidentiality bypass.
**Минимальный полный путь исправления (не выполнен):** Validate trusted grants/branch existence consistently, expose typed absence, keep out-of-grant branches indistinguishable.

## 4. O1: не скрывать устаревание, но обеспечить продолжение

Чистая пара s2: до продвижения AB у R2 нет reasons; после — MISSING_COVERAGE + STALE_CHECK. Содержимое query AA, его head4 и хеш фактов AA прежние; повторное продвижение не сообщает новый номер чужой головы. Это полезный честный сигнал; после нового решения заказчика НЕ finding за сам факт stale. Однако AA-only получает dependencies={} и не имеет рабочего API независимой актуализации скрытого основания. В s4 законный комментарий принят, исходный клайм сохранён, но stale не снимается. Это TD-DOM-15, не новый дублирующий долг. Сделать dependencies={} у нового клайма — не доказанная revalidation и не успех.

## 5. O2: разрешённое происхождение и остальные значения

| Поля/поверхности | Классификация | Основание |
|---|---|---|
| Claim.origin_branch; Claim.origin_version; History.origin_branch; History.origin_version; Trace.origins.*.origin_branch; Trace.origins.*.origin_version; Residual.claim_origins[].origin_branch; Residual.claim_origins[].origin_version | ALLOWED_PROVENANCE | Available/explicitly shared claim retains origin, including AB without AB grant. Origin version is immutable source label, not current branch head. |
| Claim.body_b64; Claim.item.body_b64; Claim.raw_sha256; Claim.item.metadata; Claim.item.reason; History.provenance.value; History.provenance.origin_version; History.provenance.reason; Claim.properties | AVAILABLE_RECORD_DATA_NOT_TOKEN_LEAK | Body/metadata/comments/reasons of explicitly accessible records can contain AB strings. AB shared body is intentional; private AB branch events/properties are not thereby accessible. No blanket raw-token security oracle. |
| ClaimItem.applicability; History.provenance.value.item.applicability | NON_PROVENANCE_SCOPE_EXCEPTION_NOT_GRANTED | AA-origin a2 exposes AB in applicability; not covered by always-show-origin decision. Foreign membership names remain a distinct policy/default-scope finding. |
| Snapshot.excluded_branches; QueryResponse.excluded_branches; Trace.excluded_branches; TraceResponse.excluded_branches; Resume.snapshot.excluded_branches; Resume.trace.excluded_branches; History.provenance.value.value.branch for exclude | NON_PROVENANCE_SCOPE_EXCEPTION_NOT_GRANTED | AA-only sees AB exclusion names, unrelated to source provenance. Owner role string is not proof of unrestricted global authority. |
| Claim.applicable_branches; History.provenance.value.value.branch for applicability | TARGET_BRANCH_RELATION_SCOPED | Explicit target-branch applicability events fold into that branch; observed [AA] in AA and [AB] in AB, not the full source branch. |
| Claim.dependencies; History.provenance.dependencies; ReadSnapshot.revisions | FOREIGN_KEYS_REMOVED | AA-only maps match SQL filtered by launch grant, union retains full maps; no marker/count. |
| Snapshot.conflicts; History.provenance.value.value.conflict_ref; History.provenance.value.value.replacement_ref; History.provenance.value.value.url; History.provenance.value.value.locator; AppendValue.ref | EXPLICIT_VISIBLE_EVENT_REFERENCE_NOT_AUTOMATIC_SOURCE_ACCESS | s1 AA-authored conflict explicitly names private b2 UUID; not a server-discovered locator, not evidence b2 body or AB neighbors were read. replacement restricted to branch-local visible records. Foreign reference/link policy is distinct from permitted provenance; do not call every user-supplied string an unauthorized leak. |
| Admitted.branch; Admitted.revision; Admitted.tx_id; Admitted.claim_ids | FAIL_ON_CROSS_GRANT_REPLAY | Newly proven independent path: AA candidate plus prior AB idempotency key/digest returns AB private receipt before current digest/scope binding. Not permitted origin of an accessible claim. |

В частности, доступный b1 из AB законно несёт origin AB и тело. Отдельный закрытый b2 НЕ materialized в AA. UUID b2 в conflict — строка явно внесённого AA-события, а не доказательство чтения соседей AB. Owner-exclude AA-only→AB физически влияет на master; глобальные полномочия из слова owner не выводятся — отдельный пробел контракта полномочий, не бездоказательное обвинение в эскалации.

## 6. O3: что именно подтверждено

s2 не был надёжным union-first контролем: D1/D2 копировали уже синхронизированный S; read_all создаёт явный export до sync. Поэтому s4 построил новую базу с нулём ack/exports и разделил dom_sync от dom_export.

AA-only sync сохраняет YAML deps={}; virgin union-first — deps={AB:1}. Отпечатки реально разных доставленных байтов отличаются. Union sync после AA-only возвращает SYNCED без нового файла/ack; дальнейший явный union export пишет полные байты, но старый ack не меняет. Это FAIL принятого требования. Полный внутренний stamp (chain_head, AA/AB revisions, port_reported) сохранён — он подтверждает контекст наблюдения, не полноту файла. Actor/root не заменяет получателя/область представления.

Ambiguous→available в новой симуляции восстанавливается: SYNC_PENDING→SYNCED, одна физическая запись в локальную цель и один target record. Это не live OMH и не приёмка задачи.

## 7. purpose_audit — помогает ли вести долгий проект

### F-USE-01 — WORKING_BASELINE_WITH_GRAPH_GAP
- Задача/права: New AA-only process must use explicitly shared AB claim.
- Реальные действия: Fresh PID dom_resume(AA), dom_query(AA,revision3), dom_query(AB); repeat new process after AA comment.
- Полученное основание: Same claim/body/raw hash/review/origin AB/synthetic-artifact-v1; exact branch history restored; AB whole-branch read denied.
- Можно продолжить: Yes for stored baseline; not main graph exploration.
- Минимальный законный шаг: Continue from available shared claim, do not reprove admitted baseline or ask for full AB.
- Evidence: s4 resume_history; continue01_verified.json resume

### F-USE-02 — MANUAL_REPLACEMENT_WORKS_VERSION_TREE_GAP
- Задача/права: AA refinement after concurrent update, independent admission mandatory.
- Реальные действия: Read head -> submit candidate -> competitor link -> review/admit stale -> REVISION_CONFLICT -> reread -> new candidate/review/admit -> replacement.
- Полученное основание: Old A preserved archived; A.1 live; source link/reasons/history kept. Child field REJECTED UNKNOWN_FIELD.
- Можно продолжить: Yes via manual replacement; no complete required version-tree/ContextPack E2E.
- Минимальный законный шаг: Reread conflict, resubmit exact current intent and independently admit; do not label ordinary replacement a family/version implementation.
- Evidence: s4 refine; continue01_verified.json refine

### F-USE-03 — HONEST_STALENESS_WITH_RECOVERY_GAP
- Задача/права: AA-only claim pins hidden AB basis; AB advances.
- Реальные действия: Inherited clean before/after raw frames, then new-process resume, local annotation, resume.
- Полученное основание: Query baseline unchanged; STALE_CHECK and MISSING_COVERAGE R2; NOT_READY; claim retained, visible deps{}.
- Можно продолжить: Cannot finish trusted revalidation alone; a valid annotation does not heal basis.
- Минимальный законный шаг: Authorized independent revalidation/replacement; built-in routing/version flow GAP TD-DOM-15.
- Evidence: s2 O1; s4 stale; continue01_verified.json stale

### F-USE-04 — EXACT_BRANCH_HISTORY_WORKS_VERSION_FAMILY_GAP
- Задача/права: Restore an old shared claim version after further edits/restart.
- Реальные действия: New PIDs dom_query(AA,revision3) before/after admitted AA comment.
- Полученное основание: Historical snapshots equal excluding read timestamp/stamp; raw body hash and origin preserved; version label does not become AB current head.
- Можно продолжить: Yes for exact branch revision, not absent claim-family version routing.
- Минимальный законный шаг: Request explicit historical branch revision via API; no manual filesystem assembly was needed in the agent path.
- Evidence: s4 resume_history; continue01_verified.json resume

### F-USE-05 — FAIL_O3_AND_LIVE_OMH_GAP
- Задача/права: Admitted AA result, change reader AA-only -> union; ambiguous reply recovery.
- Реальные действия: Virgin AA-only sync then union sync; virgin union-first control; separate explicit export; ambiguous sync then available sync.
- Полученное основание: Local ambiguity recovers without duplicate target write. Union-after-AA falsely reuses scoped ack. All targets simulation only; no OMH task acceptance.
- Можно продолжить: Local retry yes; receiver/view-correct delivery no.
- Минимальный законный шаг: Do not treat SYNCED as full payload/task closure; proper view-bound delivery contract is already accepted requirement, not a repeated customer question.
- Evidence: s4 delivery; continue01_verified.json O3

### F-USE-06 — RESTRICTIONS_CLASSIFIED_AND_PURPOSE_GAPS_RETAINED
- Задача/права: Assess every encountered refusal against long-project usefulness.
- Реальные действия: Cross-reference actual refusals, recovery attempts, tools/list and requirements; no nonexistent API invented.
- Полученное основание: Necessary gates distinguished from missing recovery/features and actual delivery obstacle.
- Можно продолжить: Not full-purpose ready: graph/search, version tree, live OMH, revalidation flow absent.
- Минимальный законный шаг: Use restrictions table and SEARCH-USE cases as future acceptance, not forced access/grant removal or new planner.
- Evidence: purpose restrictions table; s4 api_inventory; s5; s6

### GAP полной цели

- **PURPOSE-GAP-01 / GAP: Iterative claim-centered graph/search** — Real tools/list has 12 tools, no graph/search/claim-version neighborhood/readview/route recovery API. Not executed on imaginary APIs.
- **PURPOSE-GAP-02 / GAP: Refinement family/version tree and ContextPack** — Manual new claim + replacement works and preserves old body/link/reasons; parent_claim_id UNKNOWN_FIELD. No family/tips/STALE_PARENT_LEAF/ContextPack mechanism. Outbox delivery_attempts exists physically but is NOT a context-reading-delivery log.
- **PURPOSE-GAP-03 / GAP_AND_EXISTING_DEFECT: Safe usable revalidation of hidden pinned basis** — Honest STALE_CHECK and accepted claim preserved; local AA annotation leaves stale. No built-in authorized revalidation request/flow. Recreating a claim with dependencies={} is not revalidation and must not be called success.
- **PURPOSE-GAP-04 / GAP: Live OMH task/plan binding and evidence delivery** — OMHPort is simulation-only local JSON target. Recovery/no-dup tested only in that mode. DOM has no observed live OMH acceptance; neither SYNCED nor local target closes task.

Основная функция поиска — не «выдать всю AB» и не ограничить весь путь тремя рёбрами. Агент сохраняет вопрос A, получает доступный центр с origin и окружением, выбирает следующий релевантный центр и повторяет. depth=1..3 TEST_PARAMETER локален одному ответу. SEARCH-USE-01..08 из принятой формализации — GAP/unexecuted: дальний ответ через последовательные центры; отвлекающий тупик и оставшийся фронтир; циклы/ромбы и restart; общий AB-клайм без открытия закрытых соседей; смена версий/прав; пагинация/лимит не равны исчерпанию; сравнение К0/К1/К2/К3; поиск не заменяет независимую приёмку. Граф/поиск/keywords/куратор/трибунал не реализовывались.

### F-USE-06: необходимость каждого ограничения

| Правило | Какой риск защищает | Нужный путь | Восстановление / GAP | Вывод |
|---|---|---|---|---|
| SCOPE_DENIED on AB/ZZ outside grant | Private branch access/exists oracle | Continue using shared b1 without full AB | dom_resume(AA) supplies baseline; no grant expansion needed; graph follow-up GAP | NECESSARY_WORKING_FOR_SHARED_BASELINE |
| launch-grant exact matching, no case/Unicode/whitespace normalization | Alias/homoglyph scope bypass | Read canonical authorized branch | Use exact issued branch, never repair supplied token silently; malformed/absent trusted grant needs launcher validation | NECESSARY; AU005-F-04 robustness limit |
| independent submit -> review -> admit; no self-acceptance | Baseline integrity | Admit corrected claim | Separate trusted reviewer works in demo; live issuer/auth GAP TD-DOM-08 | NECESSARY_NOT_A_REASON_TO_REMOVE_CHECKS |
| REVISION_CONFLICT | Concurrent overwrite/lost update | Refine after other writer update | Read actual head, create new key/candidate, independent review/admit; physically succeeds | NECESSARY_WITH_WORKING_RECOVERY |
| UNKNOWN_FIELD on proposed child parent field | Closed schema | Nested accepted clarification with exact lineage | Manual new claim + replacement possible; actual version-family API is GAP | NECESSARY_VALIDATION_BUT_MISSING_REQUIRED_FEATURE |
| STALE_CHECK / CRITERIA_NOT_CURRENT | False readiness on moved source basis | Continue a long project after hidden basis advances | Keep accepted baseline; authorized source revalidation required; no safe built-in request/version route | NECESSARY_SIGNAL_WITH_RECOVERY_GAP TD-DOM-15 |
| SYNC_PENDING after ambiguous reply | False ack without verified reply reconciliation | Return already admitted result without duplication | Retry sync; one physical target write, one record; verified only SIMULATION | NECESSARY_WITH_WORKING_LOCAL_RECOVERY |
| ack skip on later union sync | Intended idempotency/no duplicate delivery | Deliver newly requested full view | Explicit export creates bytes but does not create correct receipt; protocol change needed | UNNECESSARY_OBSTACLE_AND_DEFECT AU005-F-01 |
| CHAIN_BROKEN uniform gate | Untrusted event chain/foreign diagnostic locators | Trusted AA read while any global chain part corrupt | Authorized operator restores verified source/checkpoint; no agent scope bypass. This is an exceptional integrity stop, not a healthy-project workflow | NECESSARY_FAIL_CLOSED |
| PUBLIC_PROJECTION_INVALID on visible malformed values / missing map | Closed public DTO type integrity | Read stored valid records | Normal restricted JSON admission prevents those values; disposable injected damage requires operator investigation, no raw exception detail | NECESSARY_FAIL_CLOSED |
| SCOPE_REQUIRED when direct projection has scope=None | Accidental unscoped serialization | Authorized DTO export | Trusted context grant supplied by current real service; not a user tool scope override | NECESSARY_WORKING |
| Absent graph/search/curator/keywords/tribunal APIs | No implemented restriction to credit | Main question-driven iterative retrieval and controlled convergence | GAP with SEARCH-USE-01..08; do not simulate presence or choose keyword variant silently | MISSING_IMPLEMENTATION_NOT_SECURITY_PASS |

### Фактические вызовы, не произвольная квота

- s4/resume: 9 tools/call; {"dom_admit": 1, "dom_init": 1, "dom_query": 3, "dom_resume": 2, "dom_review": 1, "dom_submit": 1}. tools/list — отдельно от tools/call.
- s4/refine: 24 tools/call; {"dom_admit": 5, "dom_init": 4, "dom_query": 3, "dom_resume": 1, "dom_review": 5, "dom_submit": 6}. tools/list — отдельно от tools/call.
- s4/stale: 7 tools/call; {"dom_admit": 1, "dom_init": 1, "dom_query": 1, "dom_resume": 2, "dom_review": 1, "dom_submit": 1}. tools/list — отдельно от tools/call.
- s4/AA_then_union: 4 tools/call; {"dom_export": 1, "dom_sync": 2, "dom_sync_status": 1}. tools/list — отдельно от tools/call.
- s4/union_first: 1 tools/call; {"dom_sync": 1}. tools/list — отдельно от tools/call.
- s4/ambiguous: 3 tools/call; {"dom_sync": 2, "dom_sync_status": 1}. tools/list — отдельно от tools/call.
- s4/replay: 11 tools/call; {"dom_admit": 4, "dom_init": 2, "dom_query": 1, "dom_review": 2, "dom_submit": 2}. tools/list — отдельно от tools/call.

## 8. Исполнение/независимая проверка

Сводка сохранённых групп (не сумма скопированных файлов):

| Группа | Процессы с receipt | tools/call | exits |
|---|---:|---:|---|
| s1 | 40 | 156 | [0] |
| s2 | 30 | 101 | [0] |
| s4 | 38 | 67 | [0] |
| s5 | 3 | 37 | [0] |
| s6 | 11 | 1018 | [0] |

Gate: 84 вызова, шесть успешно инжектированных вариантов × два PID × семь инструментов. DB unchanged и точный Broken без чужого локатора. NULL payload не инжектирован: SQL NOT NULL сработал; это НЕ восьмой успешный corruption test.
Инъекции: 38 клаймов, 66 событий, 132 ack. YAML safe_load == query без read_snapshot. Все опасные строки остаются данными, не исполняются. Финальный SYNCED виден в raw кадре; whole-script receipt не придуман.
Concurrency: 996 чтений, 966 пересеклись по интервалу с допуском; видны ревизии [1, 2, 3], ошибки/foreign hits пусты; text == structuredContent. Это не статистическая гарантия отсутствия timing-channel.
Процесс: 18 tests hashes совпадают с WORKER_AB002_A baseline; 1714 manifest entries worker совпадают; текущий precopy действительно 08aa9a9b…, live 1ead2d45…, только admission/public_dto/server изменены.

Ошибки собственных проб не спрятаны: s3_continue01 — Windows G_AA/G_aa collision, exit1; s3_continue02 — клиентский timeout перед поздним физическим ответом и KeyError в summary, exit1; s6_continue01 — harness bound, единственная прочитанная ревизия1, exit1. Все исходники/каталоги сохранены; положительный результат приписан только физически подтверждённым новым условиям.

## 9. Что не проверено / границы

- Statistical timing/latency noninterference NOT_CHECKED; logical/status/length and overlap measured, no timing-security guarantee.
- Arbitrary graph/search/version-family/ContextPack behavior GAP, not invented E2E; SEARCH-USE-01..08 unexecuted until implementation.
- Live OMH/auth/OS isolation/Git/checkpoint outside permission and known gaps; no network calls.
- Cross-machine YAML determinism, broad busy/read-only and full pytest not rerun (would write outside allowlist).
- Pre-copy actual time sequence cannot be proven from current hashes; verifies old bytes, not historical timing.
- s3 injection final whole-script PID/exit receipt missing; raw physical response and SQL confirm effect, not invented process success.
- AU006 mandatory pre-task DOM consultation/enforcement explicitly outside this audit; no unfinished AU006 output used.

Продолжение этого scoped-аудита не требуется; для расширения именно аудиторской матрицы — тот же AUDITOR, новые immutable run dirs. GAP продуктовых API не «дотестировать» вымышленными вызовами. Ни долг, ни задача OMH не закрыты.

## 10. Source ledger / manifest / воспроизведение

Точные source hashes и изменения входов — `artifacts/AUDITOR_AB004_AU004F01.json:source_ledger`; исходный freeze — `runtime/AU005/continue01_freeze.json`. Manifest фиксирует все физические AU005 evidence и два финала; verifier читает exact target и hash ledger, не перезапускает кампанию.

Краткая проверка из корня проекта (без Git/сети/установок):

```bash
env -u PYTHONPATH -u PYTHON -u PYTHON_BIN -u PYTHON_VENV -u VIRTUAL_ENV -u PYTHONSCRIPT -u PYTHONHOME E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AU005/final_readback.py
```

Verifier успех означает целостность этих свидетельств и воспроизведённые противоречия, а не APPROVE продукта.

## 11. НАХОДКИ (эскап-хэтч)

- Уровень1: ошибки своих probe исправлены только новыми скриптами/каталогами; не исправлялся продукт.
- Уровень2: AU005-F-01..04 и PURPOSE-GAP-01..04 физически зафиксированы в собственном JSON/отчёте; tech_debt read-only, номера TD не захватывались, статусы не менялись.
- Уровень3 [ESCALATED]: F-01 требует принятого view-bound delivery контракта в реализации; F-02 — отдельного исправления scope cached receipts; owner-exclude — явного контракта полномочий. Новые решения O1/O3/пакет заказчику повторно не задавать.
- AU006 — самостоятельный вектор обязательности сверки, без дублирования его enforcement-аудита.
