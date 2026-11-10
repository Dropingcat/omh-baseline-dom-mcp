# AN003 — связи, вложенные версии и защита принятого базлайна



Материал: **COMPLETE_MATERIAL**; completion_state=`completed`. Продукт: **REQUEST_CHANGES**, product_acceptance=false; acceptance=false. Долги не закрыты.



## Вывод



Вложенное дерево уже подтверждено: родитель сверху, новые неизменяемые версии внутри того же логического клайма. Общий логический ID не нарушает неизменяемость сам по себе: нужна однозначная идентичность immutable записи/версии. Схему и имена полей должен сравнить RS003, не подтверждать заново смысл дерева. Ключевые слова остаются needs_user, но не блокируют остальной материал.



Макет сохраняет байты, review/dependency snapshots и историю, но не доставляет связанный принятый базлайн в карту задачи и не контролирует обоснованность переоткрытия. Ссылки/глоссарий/память не доказывают доставку или использование. Причина чужой сессии не установлена: она не читалась.



Backlinks/соседи требуют scope до вычисления, не фильтрацию после глобального score/count. H-LINK — существующий будущий GAP; TD-DOM-19 — ранее наблюдённый открытый долг, не новая репродукция AN003. До независимой приёмки P0 DTO-fix граф не вводить; порядок TD19/SEC003 и YAML continuation не решён этой ролью.



## Продолжение и границы



PARTIAL_FIRST_WRITE at 2026-11-07T13:01:48.587733+03:00; report/runtime absent before this continuation. 2026-11-07 20:10:01; waiting for model response (25691.5s elapsed), cause unknown. Not completed, not a proved seven-hour analysis, not an established iteration cap.

Прежний PARTIAL сохранён побайтно в runtime/AN003/initial_partial.json. Старый Q2 о согласии на дерево больше не открыт. Текущие SHA256 не доказывают равенства прежней ревизии: frozen vector отсутствовал. Продукт/тесты/docs/cards/F read-only; Git/install/network/paid/live/субагенты не использовались.



> да именно так и говорил т.е  роительный клайм сверху- а все новые но с этим жи идом в его деревое как бы они новые но кабы они в нем вложены



`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:33-43` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_CONTINUE_01.md:23-32` (S22)



## Причинный разбор: четыре класса потери базлайна



### C-A — not_delivered [major]

Уверенность: high_for_mockup_gap; unknown_for_other_session.

resume returns scoped snapshot+trace+sync; no task-linked ancestry/basis context pack. A document URL or memory entry does not prove delivery of its relevant fragment.

A.1 can arrive without A's grounds; retrieval repeats discovery rather than recovering the accepted baseline.

User reports repeated loss (S01:25-27), but the other session was not inspected; actual cause there unknown.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:365-370` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:6-17` (S03)

Вопросы: Q-L-01, Q-L-02



### C-B — delivered_without_acceptance_provenance [major]

Уверенность: high_static_only.

The mockup is not wholly without acceptance metadata: claim_snapshots pins dependencies+review_id, admission records author/root/time/reason, trace returns check_refs and stale reasons. It lacks a coherent per-version accepted_context including fact, grounds, acceptor, conditions and reopen policy.

Bare factual text and a review ID do not let a resumed agent distinguish accepted under conditions from candidate, superseded or stale.

No evidence about what acceptance metadata reached the parallel session.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\storage.py:31-36` (S04); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:163-206` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:55-77` (S05)

Вопросы: Q-L-01, Q-L-07



### C-C — delivered_but_not_binding [major]

Уверенность: medium_inference_from_static_scope.

Admission constrains bytes/references/revisions, not an agent's private reasoning. A context package alone cannot guarantee respect for accepted facts.

If the execution/return contract has no requirement to cite the exact accepted baseline and justify divergence, the agent may rediscover A or replace it rhetorically without a controlled state change.

Not a claim that current tools enforce cognition; no live task delivery was exercised.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:174-206` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:40-42` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:104-108` (S01)

Вопросы: Q-L-02, Q-L-07



### C-D — no_explicit_reopen_rule [major]

Уверенность: high_static_gap; policy_proposed.

Conflict/resolve/replacement events exist but no accepted-fact reopen reason taxonomy/authorization or typed refinement transition is defined in the current contract.

Without conditions for reopening, every follow-up can reset the decision instead of extending its immutable lineage. Conversely an unconditional do-not-reopen flag would preserve incorrect/outdated claims.

New contrary evidence, source correction or changed applicability are candidate reasons, not an approved final enum. Forgetting alone warrants retrieving grounds, not changing acceptance.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:89-97` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:41-47` (S05); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:64-65` (S01)

Вопросы: Q-L-07, Q-L-08



## Критика M1–M7 и табличного предложения



### M1 — immutable basis[] in ORIGIN [major]

Grounds must be recoverable, but immutable creation-time grounds are not the whole evolving evidence history, and origin is not justification. Mandatory nonempty basis for every record risks fabricated grounds and blocks genuine root inputs.

Инвариант/граница: Keep recorded grounds immutable; later evidence/corrections append separately with provenance. Distinguish user requirement/observation/hypothesis and explicit missing grounds; do not silently choose mandatory policy.

Реализация: not_implemented.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:32-38` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:7-15` (S03)

Вопросы: Q-L-03



### M2 — immutable refines on child [major]

Fits confirmed nested immutable versions, but logical claim identity and record/version identity must be separated. Common logical ID plus distinct immutable version/record ID can preserve immutability; the orchestrator's blanket claim to the contrary is unsupported. tree_id/record_id/parent_ref are not approved field names.

Инвариант/граница: Parent above; new versions nested within the same logical claim; original bytes unchanged. A record address must identify one immutable version; existing IDs stay unchanged. AA11/АА11 are literal discussion examples, not AA001 task IDs.

Реализация: not_implemented; meaning_confirmed_not_needs_user.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:33-43` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:64-65` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\storage.py:31-36` (S04)

Вопросы: Q-L-04, Q-L-05



### M3 — typed link event, target pin, note, optional keywords [major]

Current link is only url+locator. Typed relations need direction, endpoint type, role, vocabulary version and bounded structured validation; a closed vocabulary is necessary but not sufficient. A semantic supports edge is not a proof. Branch dependency pins are useful precedent, not implemented per-edge version pins.

Инвариант/граница: No hidden target metadata; updates append instead of altering existing links. Similarity suggestions cannot become admitted semantic edges automatically.

Реализация: not_implemented.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:89-98` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:62-65` (S05); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:73-80` (S02)

Вопросы: Q-L-06, Q-L-08, Q-L-11



### M4 — accepted_state derived from review/converge [major]

Do not conflate candidate review, actual admission, current validity, branch convergence, delivery and owner acceptance. A review/converge flag alone cannot show who accepted which content under which dependencies. Demo review is explicitly simulated.

Инвариант/граница: Derive state from admitted version plus exact review/policy/dependency snapshot; preserve previous state and expose stale/unknown rather than falsely current. Do not label proposed fields implemented.

Реализация: partial_primitives_only.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:163-202` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:55-77` (S05)

Вопросы: Q-L-01, Q-L-07, Q-L-08



### M5 — derived backlinks/neighbors/dashboard [critical]

Derived does not mean safe or necessarily never persisted: materialized indexes/caches may be appropriate, but not authoritative. Grants must constrain candidates and accessible edges before counts, scoring, sorting, top-k, pagination and cache lookup/output. Post-filtering leaks through ranks/counts/deltas.

Инвариант/граница: Authorized views must not reveal hidden branch existence/IDs/counts/revisions or changes. H-LINK is a known gap, not a new reproduced defect.

Реализация: not_implemented; security_blocker_for_introduction.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:44-50` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:90-100` (S06)

Вопросы: Q-L-09, Q-L-10



### M6 — sources[] common subblock, local/external, locator/digest [major]

Subblock should be an append-only event/view usable for all content types, not a mutable list inserted into the original claim. local/external is not trust, permission or immutability. An external URL without snapshot leaves remote content unpinned but does not mutate the immutable recorded URL; a digest without retained bytes is not reproducibility. Local files can change too.

Инвариант/граница: Retain exact recorded locator and evidence revision/bytes where permitted; re-fetch and source correction are new events. Avoid secrets, arbitrary path/URL access and unintended fetches.

Реализация: not_implemented; quote/code/data_have_partial_primitives.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:9-15` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:75-80` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:59-60` (S01)

Вопросы: Q-L-12



### M7 — derived branches[] with effective revision [major]

Separate immutable origin from applicability and from access grants. Current projection has applicable_branches, but no per-branch since-revision in that list; it must not be described as complete membership/history or grant. Historical views must not silently use current branch eligibility/pins.

Инвариант/граница: Origin never rewritten; explicit applicability events do not transfer authority, rewrite admission dependencies or automatically move the accepted leaf of another branch.

Реализация: partial_primitives_only.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:4-25` (S05); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:29-53` (S05); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:63-66` (S01)

Вопросы: Q-L-05, Q-L-08, Q-L-09



**AT-01 [minor]** TYPE-META table is abbreviated, not full schema: e.g. quote also requires source_b64 and multiple types require assumptions/attribution. ORIGIN author/time are in admitted event provenance; no claim-level server_time column. Exact field locations matter for DTO review.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:13-18` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:8-15` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:198-206` (S06)



**AT-02 [major]** link/comment remain in snapshot.history provenance but snapshot does not fold them into dedicated link/comment claim fields. Do not say they are lost from storage; do not claim a ready graph/context pack exists.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:29-53` (S05)



**AT-03 [major]** Events and nested versions are distinct immutable records in one derived tree. Stable deterministic order needs branch revision plus an event-order/tie-breaker, not client timestamps alone. Last means latest independently admitted applicable version under an explicit fork policy, not latest candidate globally.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:21-41` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\RESEARCH_NOTE_CLAIM_REFINEMENT.md:19-25` (S07)



**AT-04 [major]** Keyword placement remains needs_user: the answer да to an или question selects neither claim nor edge nor both. Compare choices without stopping independent work; do not ask again about the confirmed nested tree.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:35-43` (S01)



**AT-05 [major]** New fields are not a harmless decoration: validate emits UNKNOWN_FIELD (required=false still an error); submit rejects any error. Update schema/admission/storage/DTO/projections together only in a future authorized worker scope.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:63-74` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:118-126` (S06)



## Применимость F: механизмы, а не обещания README



### F-01

Контейнер с явным интерфейсом, точными anchors и related[]; локальный и глобальный dashboard разделены.

Точные функции: readme architecture; article-template front matter

Переносимо как идея: Структурированный вход и объяснимый scoped context view; links как отдельные append-only записи DOM, не редактируемый front matter.

Не утверждать: README описывает намерение, не ACL enforcement; completeness_score в template допускает manual, не доказана вычисляющая приёмку функция.

Проверка: static_only; not_executed

`F:/AnalisysDataSet/readme.md:12-81` (S11); `F:/AnalisysDataSet/99-Template/article-template.md:30-69` (S16)



### F-02

Контролируемые типы с direction и endpoint/anchor validation rules; два неодинаковых словаря.

Точные функции: relation_type.yaml markdown list v1.0; relation-types.md v1.2 table and rules

Переносимо как идея: Идея versioned vocabulary и точного target anchor; DOM-specific семантика должна быть исследована.

Не утверждать: relation_type.yaml — Markdown с YAML-подобным заголовком, не готовая машинная схема. extends_model/compares_with против extends_method/compares_methods — не один проверенный канон; не нормализовать молча.

Проверка: static_only; not_executed

`F:/AnalisysDataSet/relation_type.yaml:1-39` (S12); `F:/AnalisysDataSet/99-System/relation-types.md:13-18` (S13); `F:/AnalisysDataSet/99-System/relation-types.md:73-127` (S13)



### F-03

getNested, parseNumeric, computeSimilarity: совпадения полей + общие tags + gaussian proximity года + nested parameter comparison + optional confidence penalty; findSimilarArticles получает весь tagged corpus, исключает current, считает score, threshold и sort.

Точные функции: getNested:15-18; parseNumeric:25-29; computeSimilarity:38-103; findSimilarArticles:112-129

Переносимо как идея: Отделимый чистый scorer по уже разрешённому набору, explanation of score и versioned config — гипотеза reuse.

Не утверждать: Не trust/admission/causal support. parseNumeric regex теряет знак и не конвертирует units; truthiness пропускает 0, duplicated tags могут завышать score; глобальный tagged corpus не grants. strength в template и confidence в scorer расходятся. Нужны synthetic tests; ничего не запускалось.

Проверка: static_only; not_executed

`F:/AnalisysDataSet/99-System/similarity-analysis.js:15-136` (S14)



### F-04

Файл similarity-weights.yaml фактически JS: defaultConfig с дробями, top-level await dv.io.load того же пути, object spread loaded, встроенный scorer и dv.table.

Точные функции: defaultConfig:7-35; loader:38-48; inline computeSimilarity:65-117; render:119-149

Переносимо как идея: Только намерение конфигурируемых весов/порогов после явного schema/parser/versioning решения.

Не утверждать: Это не проверенный YAML-config loader: парсинг YAML в данном тексте отсутствует; какой тип реально возвращает dv.io.load здесь не запускалось. Inline scorer не содержит confidence penalty основной JS версии. Float из F не допустим в текущем dom-c14n/v1; не менять canonicalization или выбирать scale/decimal encoding молча.

Проверка: static_only; not_executed

`F:/AnalisysDataSet/99-System/similarity-weights.yaml:1-149` (S15); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:19-43` (S03)



### F-05

runUniversalCards выбирает dv.pages по folder/type, enrichVirtualFields мутирует page virtual fields; backlinkCount суммирует global app.metadataCache.resolvedLinks[source][target]. renderCards применяет filters/search/sort и UI tables; path-keyed window.cardScriptCache хранит UI state.

Точные функции: enrichVirtualFields:753-772; getCardScriptCache:1079-1082; page selection:2887-2893; renderCards:3172-3175

Переносимо как идея: Derived virtual columns и UI sections, не ready server. В данном счётчике считаются link occurrences, не обязательно число уникальных соседних карточек.

Не утверждать: Folder/type фильтр не branch grants; global backlinks не ограничен отобранными страницами. DOM injection/UI APIs/Obsidian globals, cache и update-check нельзя переносить как MCP runtime. Сеть/скрипт не запускались.

Проверка: static_only; not_executed

`F:/AnalisysDataSet/scripts/universal-cards-core.js:751-772` (S17); `F:/AnalisysDataSet/scripts/universal-cards-core.js:1077-1082` (S17); `F:/AnalisysDataSet/scripts/universal-cards-core.js:2887-2893` (S17); `F:/AnalisysDataSet/scripts/universal-cards-core.js:3170-3175` (S17)



## Графовые каналы / TD19 / H-LINK



TD-DOM-19 OPEN (inherited observed finding); use existing ID, no duplicate registration

H-LINK / CP-PL-17 / SC-H-LINK / GAP-LINKS; GAP_NOT_IMPLEMENTED; PL003 NOT_EXECUTED_BY_PL003

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\tech_debt.md:30-36` (S21); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\PL003\failure_map.json:1691-1761` (S10); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:90-100` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md:27-43` (S29)



- **G-01 backlinks and count**: AB→AA reveals hidden source ID/existence/degree even if target is AA. Требование: Apply permissions to both endpoints and edge before list/count/inverse construction. Вопросы: Q-L-09.

- **G-02 neighbors/similarity/ranking/top-k/dashboard**: Hidden content changes visible scores/order/totals/clusters/orphans even after row redaction. Требование: Candidate selection and aggregation over visible subgraph first; scoring/sort/top-k/paging next; no hidden count footer. Вопросы: Q-L-09, Q-L-14.

- **G-03 n-hop/shared node traversal and ancestry**: A legitimate shared node expands into forbidden parents/siblings/neighbors. Требование: Re-authorize each hop and relation; sharing/applicability is not transitive grant; missing context must not reveal number or identity of hidden records. Вопросы: Q-L-01, Q-L-05, Q-L-09.

- **G-04 pins/revision/stale/check age**: Forbidden target revisions and stale bit/delta reveal hidden change. Требование: No hidden revision vectors or comparative freshness derived from forbidden targets in public output; preserve internal proof and strict global gate separately. Вопросы: Q-L-08, Q-L-09.

- **G-05 cache/cursors/invalidation/logs/errors**: Union warm cache or cursor reused by AA; hidden invalidation alters totals/timing; diagnostics expose foreign IDs. Требование: Bind policy/grants/authorized revision scope; reject cross-scope cursor safely; closed error DTO; analyze timing separately rather than claim constant-time. Вопросы: Q-L-10.

- **G-06 graph append and endpoint validation**: Forbidden/not-found difference becomes ID oracle; partial edge/outbox creates hidden mutation. Требование: Atomic authorized validation+admission; generic scope-safe error; no partial graph or delivery writes. Вопросы: Q-L-06, Q-L-09.



trusted context → authorized branch/record/edge set at one read snapshot → relation traversal/count/score/pin projection → closed DTO → both MCP channels/YAML/log policy. Internal chain verification/proof remains full, not redacted in-place.

Do not falsely promise all responses identical despite hidden corruption: AB003 intentionally preserves a global integrity gate and safe generic CHAIN_BROKEN/NOT_READY. Differential no-leak checks for healthy hidden changes must be distinguished from this accepted generic fail-closed bit; foreign locators/revisions/counts remain forbidden.



Будущий oracle (не исполнено): At fixed AA, compare hidden AB 0 vs 8 edges with B/union positive control; compare text/structured/nested/errors/YAML/targets/cursors/cache and before/after SQL; fixture oracle privileged and separate. Missing API remains GAP, not fake PASS.



## Требования к context pack / accepted_context — предложение для исследования



- fact and exact immutable record/version address

- logical claim family and permitted ancestry

- grounds/source quote and exact locator/snapshot

- admission/review evidence and acceptor identity/role

- branch/read revision and dependency/policy/criteria snapshot

- applicability conditions, assumptions and unresolved alternatives

- current/archived/stale/unverified states kept distinct

- authorized reopen reason, authority and evidence

- task/run/card reference and explicit authorized remainder

- pack provenance/digest and delivery receipt separate from content truth



Result cites the exact consumed baseline and scoped revisions; divergence requires new evidence/reopen trail and independent review. Acknowledging receipt is observable; comprehension is not proven by receipt.

Do not fabricate basis or treat hidden/missing ancestry as complete. Safe explicit incomplete context/remainder is not permission to infer hidden ancestors. Research bounded retrieval/pagination and task-specific selection, not a dump of the global graph.



## Точные вопросы RS003



Всего 14. Ниже вопросы, не ответы исследователя. Все проверки — будущие, NOT_EXECUTED в AN003.



### Q-L-01 [P1]

Каков минимальный версионированный контракт accepted_context/context pack для продолжения A.1, который доставляет сам факт A, точное основание, принявшего и доказательство допуска, ревизию/условия применимости, текущий статус проверки и правило переоткрытия, не выдавая чужой контекст?

Почему: Хранение уже есть частично, но resume не собирает причинный пакет по задаче; review_id не равен понятному принятому базлайну.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:365-370` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\FULL_IMPLEMENTATION_PLAN.md:84-89` (S19)

Тип ответа: Таблица полей/владельцев/обязательности/источников + схема вычисления и отказов + связь с OMH task/card/run; варианты, не неявное утверждение API.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** Будущий E2E: сессия 1 допускает A с основанием; новый процесс получает карту A.1; один предок недоступен, затем доступен положительным контролем.

**Ожидаемое:** Разрешённые основания и условия доставлены с точными refs; при недоступности явный безопасный остаток без имени/числа скрытого предка и без ложного complete.

**Физические evidence:** raw task/card payload и MCP text+structured; сохранённый pack с digest/revision; SQL admitted records и grants receipt; отдельные PID/exit.



### Q-L-02 [P1]

Какая проверяемая цепочка отличит persisted/selected/delivered/read-or-acknowledged/used для принятого контекста и потребует от исполнителя ссылки на этот базлайн либо обоснованного отклонения, не обещая доказать внутреннее мышление агента?

Почему: Память и наличие файла не доказывают ни доставку, ни использование; статус delivered не должен стать новым голословным ack.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:25-27` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:104-108` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\FULL_IMPLEMENTATION_PLAN.md:84-89` (S19)

Тип ответа: Последовательность handoff/receipt/result checks с пределом доказуемости и независимым oracle.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** Создать будущие прогоны с опущенным pack, старым pack и правильным pack; исполнитель пытается сдать результат без baseline refs или молча заменить A.

**Ожидаемое:** Контроль выявляет недоставку/устаревание/необоснованное отклонение; receipt не объявляется доказательством понимания; правильный результат проходит независимую проверку.

**Физические evidence:** dispatch и result payloads; digest-bound receipt; отчёт независимого проверяющего; raw reject/accept responses.



### Q-L-03 [P1]

Как отделить неизменяемые основания при создании от поздних append-only подтверждений/опровержений и представить корневой ввод без basis, legacy без записанного основания и criterion-клайм без baseline, не вынуждая агента выдумывать ссылки?

Почему: M1 смешивает origin и justification; RS001 Q-07/UD-02 оставляет reject против NO_BASELINE открытым.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:32-38` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\RS001_RESEARCH.json:93-104` (S08)

Тип ответа: Матрица типов ввода/grounds/status/coverage + варианты политики и точная развилка UD-02.

Неопределённость: mixed_engineering_product; needs_user: UD-02: отказ либо непокрывающая informational запись; не решать повторно без источника

**Действие:** В будущем подать корневую цитату заказчика, гипотезу без оснований, criterion без dependencies, legacy и поздний source correction.

**Ожидаемое:** Никаких фиктивных grounds и ложного покрытия; старый grounds не изменён; поздний evidence добавлен; результат соответствует утверждённой политике.

**Физические evidence:** requests/rejections с field paths; SQL before/after; исторический snapshot; trace coverage.



### Q-L-04 [P1]

Сравни схемы идентичности для уже подтверждённого дерева: общий logical claim ID + уникальный record/version ID (в том числе составной ключ) против уникальных immutable node IDs + общий logical/root ID; как адресовать цитату/версию и parent без изменения прежних IDs и исходника?

Почему: Категорическое утверждение, будто общий claim_id обязательно нарушает immutability, неверно без определения record key; смысл вложенного дерева уже подтверждён.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:35-43` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\storage.py:31-36` (S04); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_CONTINUE_01.md:23-28` (S22)

Тип ответа: Сравнительная таблица ключей, FK, публичного адреса, migration/compatibility и failure cases; имена полей не объявлять утверждёнными.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** Будущая fixture: один логический клайм с двумя допущенными версиями и событием; дубликат record key, ссылка на старую версию, попытка перезаписи исходника.

**Ожидаемое:** Обе версии адресуемы однозначно под тем же логическим клаймом; дубль/перезапись отвергнуты; старая ссылка воспроизводима; AA11/АА11 и AA001 не нормализованы друг в друга.

**Физические evidence:** DDL и migration proposal; SQL keys/FK/integrity receipts; до/после raw SHA256 тел; MCP historical lookup.



### Q-L-05 [P1]

Как определяется последнее актуальное принятое вложенное уточнение в ветке при двух concurrent siblings, reject, archive, переносе применимости и semantic merge, если время кандидата и глубина не дают права молча выбрать победителя?

Почему: Подтверждённая вложенность не определяет concurrency/fork arbitration; исходник нельзя глобально архивировать лишь из-за дочерней версии в другой ветке.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:64-66` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\RESEARCH_NOTE_CLAIM_REFINEMENT.md:19-25` (S07)

Тип ответа: Branch-local state machine + CAS/atomicity/idempotency choices + список только реально продуктовых развилок.

Неопределённость: mixed_engineering_product; needs_user: Если механизмы оставляют смысловую конкуренцию двух independently admitted siblings — явный субъект выбора, не выбор аналитика

**Действие:** Два будущих процесса уточняют одного родителя; один reject, затем оба admissible; kill до/после commit, retry, применимость второй ветке.

**Ожидаемое:** Нет потерь и тихого победителя; candidate не заменяет accepted; старый snapshot и чужой актуальный лист не меняются автоматически; восстановление атомарно.

**Физические evidence:** PID/exit и fault receipts; SQL/version lineage before/after; MCP current/historical tree; readback после рестарта.



### Q-L-06 [P1]

Какой минимальный версионированный словарь typed relations нужен DOM для basis/refinement/support/contradiction/use и каковы direction, endpoint kinds, inverse derivation, supersession и строгая валидация без автоматического превращения similarity в доказательство?

Почему: F содержит разные версии словаря и несовпадающие имена; закрытого списка без семантики/проверки ссылок недостаточно.

Источник: `F:/AnalisysDataSet/relation_type.yaml:10-30` (S12); `F:/AnalisysDataSet/99-System/relation-types.md:13-18` (S13); `F:/AnalisysDataSet/99-System/relation-types.md:106-127` (S13); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:89-98` (S03)

Тип ответа: Небольшая relation matrix + migration/versioning + reject codes + mapping F tokens без молчаливого переименования.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** В будущем подать неизвестный relation type, несовместимые endpoint kinds, несуществующий/чужой endpoint и duplicate reverse edge; допустить валидную связь контролем.

**Ожидаемое:** Строгие безопасные отказы без partial rows; inverse не дублирует authoritative edge; valid control видим только допустимым акторам.

**Физические evidence:** closed schema; raw MCP frames; SQL graph/outbox diff; scoped backlinks output.



### Q-L-07 [P1]

Как раздельно вывести admitted/accepted/current/stale/converged/delivered/owner-closed и кто может переоткрыть принятое при новом противоречии, исправлении источника или изменении условий, не переписывая прежнее решение и не превращая отсутствие воспоминания в reopen?

Почему: M4 review/converge недостаточен; blanket запрет пересмотра тоже неверен; UD-06 не решён.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:163-191` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:55-77` (S05); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\RS001_RESEARCH.json:67-90` (S08)

Тип ответа: Независимые state dimensions и transition table с authority/evidence/reopen reason; продуктовые choices выделены.

Неопределённость: mixed_engineering_product; needs_user: UD-06: субъект/критерии сходимости и область revalidation

**Действие:** Будущий E2E: review без admit; admit без delivery; новая противоречащая версия; забытое основание; revalidate на новой базе.

**Ожидаемое:** Ни review, ни ack не означают owner close; забывание ведёт к retrieval, не молчаливому reopen; новая проверка не редактирует старую.

**Физические evidence:** immutable review/admission/reopen records; trace per-state output; OMH result readback при разрешённой интеграции; historical receipts.



### Q-L-08 [P1]

Как различить pin точной record/version, pin ревизии ветки и ссылку на актуальную линию; когда связь или проверка становится stale и как scoped revalidate добавляет новое основание, не переключая старое доказательство на новый смысл и не раскрывая ревизию запрещённой цели?

Почему: dependencies branch→revision уже есть, но не как link pin; простое head!=pin консервативно и не доказывает содержательного изменения; CHECK_AGED не утверждён.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py:62-71` (S05); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:185-202` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\RS001_RESEARCH.json:80-103` (S08); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:75-80` (S02)

Тип ответа: Pin semantics matrix + temporal/read-snapshot contract + strict-default compatibility + UD-02/06 deltas.

Неопределённость: mixed_engineering_product; needs_user: UD-02/UD-06 остаются OPEN; нельзя ослабить stale до aged молча

**Действие:** Будущие чтения: старая ревизия, новая нерелевантная транзакция, новое смысловое уточнение target; затем grants revoked и independent revalidate.

**Ожидаемое:** Старый snapshot воспроизводим; прежний pin неизменён; актуальность не возникает без проверки; скрытая target revision/stale delta не выдана.

**Физические evidence:** read snapshot vector; SQL edge/dependency history; raw public errors and trace; revalidate proof record.



### Q-L-09 [P0_before_graph_introduction]

Как реализовать и независимо проверить scope-first non-disclosure для graph/backlinks/neighbors/counts/ranking/dashboard/pins и n-hop traversal через явно shared node, сохранив глобальный integrity gate и closed public DTO?

Почему: Это развитие H-LINK CP-PL-17, не новый зарегистрированный TD19; global metadata уже демонстрирует опасную границу.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\PL003\failure_map.json:1691-1756` (S10); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py:90-100` (S06); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md:27-43` (S29)

Тип ответа: Boundary diagram/field allowlists + differential oracle matrix L1-L8 + правила authorized sharing и единственного допустимого global failure bit.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** После появления API: fixed AA, hidden AB 0 vs 8 links, входящие/исходящие/n-hop/similarity и forbidden append; положительный B/union control. Пока API нет — GAP, не PASS.

**Ожидаемое:** AA-visible data/ranks/counts/cursors не меняются от скрытого AB; no endpoint existence oracle; rejected append атомарен. Global CHAIN_BROKEN может блокировать по утверждённому safe contract, но не раскрывает locator/revision/count.

**Физические evidence:** raw MCP text+structured/nested; authorized fixture oracle отдельно; all-table SQL/targets/exports before/after; frozen run-specific manifest+grants/PID/exit.



### Q-L-10 [P0_before_graph_introduction]

Как ограничить cache keys, invalidation, cursor reuse, top-k и вычисление stale видимым подграфом/политикой/grants/revision, чтобы warm union cache или изменение скрытой ветки не меняли ответ AA-only и не утекали через диагностику/логи?

Почему: Фильтрация готового глобального ранжирования недостаточна; F caches keyed by note path не являются security boundary.

Источник: `F:/AnalisysDataSet/scripts/universal-cards-core.js:1077-1082` (S17); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\PL003\failure_map.json:1735-1746` (S10)

Тип ответа: Cache/cursor threat table, invalidation contract и измеримые проверки с явным пределом timing guarantees.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** Будущий union actor греет cache; AA повторяет запрос с union cursor, затем меняются grants и только AB data; повтор после рестарта.

**Ожидаемое:** Нет cross-actor reuse или скрытых delta/count; unauthorized cursor безопасно отвергнут; данные не переживают отзыв прав как доступные. Отдельно оценён timing риск без голословного constant-time.

**Физические evidence:** request/response pairs; cache/cursor receipts без секретов; grant transition records; scoped output diffs and restart log.



### Q-L-11 [P2_needs_user]

Сравни ключевые слова на логическом клайме/его версии, на ребре и в обоих местах: какие поисковые/смысловые задачи решает каждый вариант, как append-only исправления и scope влияют на индекс; затем сформулируй заказчику один точный выбор, не трактуя ответ да на или как утверждение обоих?

Почему: Седьмое уточнение оставляет только место keywords неоднозначным; дерево не нуждается в новом подтверждении.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:33-43` (S01); `F:/AnalisysDataSet/99-Template/article-template.md:30-55` (S16)

Тип ответа: Короткая decision table + точная needs_user формулировка и зависимый scope, без выбора вместо заказчика.

Неопределённость: product_with_engineering_comparison; needs_user: keyword location/ownership not confirmed

**Действие:** После выбора: добавить claim keyword и/или edge keyword, append исправление, проверить поиск из AA-only и union и историческую выдачу.

**Ожидаемое:** Индекс следует выбранному контракту; старые bytes/labels сохранены; скрытые keywords не раскрываются через suggestions/counts.

**Физические evidence:** точная цитата решения пользователя; schema version; SQL append events; raw scoped search and history results.



### Q-L-12 [P1]

Каков общий append-only source subblock для local/external источников: что неизменно записывается (URL/path, locator, bytes/hash/version, capture time, provenance), что делать без разрешённого снимка и как добавлять новую редакцию, не считая locality меткой доверия и не инициируя произвольный fetch?

Почему: M6 неверно отождествляет неизменность URL с неизменностью удалённого содержимого; локальный путь тоже изменяем; digest без bytes не гарантирует воспроизведение.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md:75-80` (S02); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:9-15` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:59-60` (S01)

Тип ответа: Source record/event schema + acquisition/trust/permission matrix + states pinned/unpinned/unavailable, not silent success.

Неопределённость: mixed_engineering_product; needs_user: Если нужна retention/retrieval policy за пределами разрешений — эскалировать, не fetch автоматически

**Действие:** Будущие synthetic local/external fixtures меняют содержимое при том же locator; снимок отсутствует/повреждён; добавляется correction и выполняется рестарт.

**Ожидаемое:** Старый locator/снимок не переписан; неприкреплённое содержимое явно unverified; hash mismatch отказ; нет сетевого/файлового доступа вне allowlist.

**Физические evidence:** retained source bytes+SHA256; append event SQL; historical view/readback; raw rejection and acquisition permission receipt.



### Q-L-13 [P1]

Как единый производный tree view различает строки-события и вложенные immutable версии одного logical claim, детерминированно упорядочивает их, пагинирует глубокую цепь без предметного лимита глубины и мигрирует closed schemas/DTO/YAML без свободных будущих dict?

Почему: UI отступ не задаёт идентичность/ordering; текущие UNKNOWN_FIELD и DTO allowlists требуют согласованного изменения; cycles/resources важны.

Источник: `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:35-41` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:63-98` (S03); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\RESEARCH_NOTE_CLAIM_REFINEMENT.md:24-25` (S07); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\artifacts\RESEARCHER_AB002_A.json:871-945` (S09)

Тип ответа: Typed row schema, stable ordering+continuation contract, migration/compatibility и bounded resource strategy без произвольного product depth cap.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** Будущая длинная цепь+siblings+same timestamp events, циклический/чужой parent, pages с разными grants и старый клиент/экспорт.

**Ожидаемое:** Нет рекурсивного crash, пропусков/дублей и hidden total; полный authorized обход; цикл/чужой parent отклонён; старый клиент не принимает неизвестную форму молча.

**Физические evidence:** typed schemas/version negotiation; all page/cursor responses; SQL lineage counts by independent oracle; historical export bytes+hash.



### Q-L-14 [P2]

Какие минимальные механизмы F переносимы после отделения от Dataview: related+anchor, weighted visible-neighbor scoring, derived backlink count и UI; какие проверки нужны против расхождения словарей, JS в similarity-weights.yaml, strength/confidence drift и запрещённых float в dom-c14n/v1?

Почему: Название файла и README не подтверждают работающий config/MCP; score не является приёмкой/истинностью.

Источник: `F:/AnalisysDataSet/99-System/similarity-analysis.js:38-136` (S14); `F:/AnalisysDataSet/99-System/similarity-weights.yaml:7-48` (S15); `F:/AnalisysDataSet/99-Template/article-template.md:49-69` (S16); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py:19-43` (S03)

Тип ответа: Reuse/adapter/reject table с точными functions/locators и отдельным протоколом synthetic offline проверки; не обещание скопировать готовый backend.

Неопределённость: engineering; needs_user: нет новой продуктовой развилки в этом вопросе

**Действие:** Будущий разрешённый offline prototype: pinned synthetic visible set, malformed/missing config, 0/negative/unit numeric examples, duplicated tags и same inputs restart.

**Ожидаемое:** Детерминированное объяснимое ранжирование либо явный config rejection; no silent fallback success; scores не повышают acceptance, decimals имеют явно выбранное compatible encoding.

**Физические evidence:** frozen input/config/vocabulary hashes; actual runner stdout/exit; component outputs and rank explanation; MCP integration evidence отдельно после реализации.



## Влияние на план и очередность — без правки планов



### AB003/TD19

Preserve narrow P0 public DTO fix and internal proof. Do not add graph/basis/refinement/search fields to this fix. Later graph fields must be closed-schema, scope-first from one verified read snapshot.

Не делать: No product/card rewrite by AN003; no free dict future extension; no grants increase; no TD closure.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md:25-43` (S29)



### AB002 plan B/C/D

B scope/DTO foundations precede graph introduction; C should incorporate accepted nested version identity, branch-local current leaf, pin/revalidate/fork semantics and separate admission/convergence; D needs immutable run manifests and schema/link validation. Do not reopen delivered A with unrelated feature expansion.

Не делать: Do not resolve UD-02/06 silently or weaken exact revision checks; no code changes from analysis.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\AB002_PLAN.md:18-28` (S18); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\RS001_RESEARCH.json:67-104` (S08); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\RESEARCH_NOTE_CLAIM_REFINEMENT.md:17-39` (S07)



### FULL_IMPLEMENTATION_PLAN

After RS003, orchestrator should separate confirmed meaning from proposed field layout; add context delivery/use and reopened-baseline E2E acceptance, graph isolation matrix and schema migration. Correct blanket common-ID immutability claim and F YAML assumption in future append-only clarification, not by editing source here.

Не делать: No new tree confirmation; no live/Git/OMH guarantees from a runnable mockup; avoid repeating stale stage summaries as current state.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\FULL_IMPLEMENTATION_PLAN.md:80-90` (S19); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:35-43` (S01)



### OMH existing plan/technical cards (not inspected live)

Parent launches RS003 after material checks, attaches exact Q-L-xx, primary quotes/current hashes, accepted-context semantic requirements, non-delivery distinction and evidence-producing commands. Planning metadata PREPARED/done_unverified is not observed completion. OMH stays task/status owner.

Не делать: No OMH mutation/status claims or API guesses; no autonomous duplicate scheduler; installed/live OMH shape unverified.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:45-51` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\FULL_IMPLEMENTATION_PLAN.md:84-90` (S19); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_CONTINUE_01.md:34-46` (S22)



### Ordering and explicit non-decisions

Requirement dependency only: independently accepted TD19/public DTO foundation before introducing graph; AN003 → parent material validation → RS003 → updated worker scope → worker/reviewer/auditor cycle. Preserve P0. Exact TD19-vs-SEC003 execution order belongs to parent, not this analysis.

Не делать: Do not decide YAML continuation on OMH failure or TD19/SEC sequence; keywords ambiguity blocks only dependent keyword scope.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_CONTINUE_01.md:28-32` (S22); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\FULL_IMPLEMENTATION_PLAN.md:84-89` (S19); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md:13-13` (S29)



## Вердикты / приоритеты / непроверенное



AB003 prepared card reports AU002-A REQUEST_CHANGES; AN002/RS002 completed material is not product acceptance. TD19/20/21 OPEN per prepared input, not re-adjudicated.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md:9-13` (S29); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md:38-43` (S29)



- No basis/refines/accepted_context/typed versioned graph implementation introduced.

- Current mockup has storage/admission/review/dependency primitives, not a completed linked-baseline delivery system.

- F JS, Dataview, scorer/config and MCP integration were not executed.

- H-LINK remains GAP_NOT_IMPLEMENTED; no new tools/list or live security probe performed.

- No runtime product regressions, migrations, concurrency, crash-recovery, Git or live OMH tested.

- TD19/SEC003 order and YAML continuation after OMH failure deliberately undecided.



Неустановленные/непросмотренные входы:

- No frozen source vector from former AN003; cannot prove unchanged source revision.

- No parallel customer session logs read; causal attribution there remains unknown.

- No fresh reviewer/auditor product verdicts executed or reconstructed; inherited prepared card used as declared input.

- Live OMH plan/API and actual model context use not inspected; no state changes made.



## НАХОДКИ (эскап-хэтч)



- Уровень 2 [major]: Orchestrator note conflates logical ID with immutable record key; common logical claim_id need not break immutability. Действие: Recorded critical correction for parent/RS003; source untouched, schema not selected.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:41-43` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_CONTINUE_01.md:26-28` (S22)

- Уровень 2 [major]: F filenames/README overstate readiness: vocabulary .yaml is Markdown; weights .yaml is JS; strength/confidence and vocab names drift. Действие: Recorded adapter/reject boundaries, no F edits or new debt ID; parent can route future source-quality work if needed.

`F:/AnalisysDataSet/relation_type.yaml:1-10` (S12); `F:/AnalisysDataSet/99-System/similarity-weights.yaml:1-48` (S15); `F:/AnalisysDataSet/99-Template/article-template.md:49-55` (S16); `F:/AnalisysDataSet/99-System/relation-types.md:73-82` (S13)

- Уровень 3 [critical]: Graph introduction must not repeat existing TD19 metadata leak; H-LINK is future GAP, not independently reproduced vulnerability. Действие: ESCALATED to parent as P0 dependency; no duplicate TD and no change of TD19 status.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\tech_debt.md:30-36` (S21); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\PL003\failure_map.json:1735-1761` (S10)

- Уровень 3 [major]: Keyword ownership unresolved; UD-02/06 policy forks inherited; engineering record-key choice not a new user re-confirmation of the tree. Действие: ESCALATED product choices with limited dependent scope; independent analysis complete.

`E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md:35-43` (S01); `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\RS001_RESEARCH.json:234-238` (S08)



Уровень 1: продуктовых исправлений не делалось; собственные структурные артефакты проверяются валидатором. Контракт регистрации новых TD не расширяет разрешённые пути: новый дублирующий TD не создан; реальные передаваемые находки записаны здесь и в JSON.



## Самопроверка и ограничение уверенности



degraded_self_check_no_fresh_subagent. skipped: non-interactive delegated context; nested delegation/network/paid forbidden.

Fresh-context review не проводился. Это честная ограниченная самопроверка, не независимая приёмка.

- Could a common logical ID be immutable? Yes with distinct version record key; categorical orchestrator note corrected.

- Could metadata already encode partial admission? Yes; do not claim complete absence.

- Could URL immutability hold without remote snapshot? Recorded URL yes, remote content reproducibility no.

- Could hidden corruption affect generic availability? Yes global gate intentionally preserved; not all-output noninterference claimed.

- Could F files be ready YAML? No, actual source disagrees.



## Валидация материала



Состояние: PASS. Валидатор: `runtime/AN003/validate.py`; квитанция: `runtime/AN003/validation_receipt.json`.

Проверяет форму, покрытие, ссылки и текущие хеши; не доказывает истинность каждого вывода, работоспособность продукта, F или live OMH. Свои JSON/MD и runtime fingerprints входят в output_hashes квитанции.

Воспроизведение: `E:/opencode_harness_portable/.venv/Scripts/python.exe E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/runtime/AN003/validate.py`.

Повтор collect_sources.py снимает новый текущий вектор, а не восстанавливает прежний; для проверки сдачи достаточно validate.py, не перезаписывать ledger до проверки.



## Coverage



- continuation-1-causes → causal_analysis → Q-L-01, Q-L-02, Q-L-07

- continuation-2-markers-and-table → marker_critique → Q-L-03, Q-L-04, Q-L-05, Q-L-06, Q-L-07, Q-L-08, Q-L-11, Q-L-12, Q-L-13

- continuation-3-F → F_reuse → Q-L-06, Q-L-14

- continuation-4-graph-and-context → graph_security → Q-L-01, Q-L-02, Q-L-09, Q-L-10

- continuation-5-exact-RS003 → questions_for_RS003 → Q-L-01, Q-L-02, Q-L-03, Q-L-04, Q-L-05, Q-L-06, Q-L-07, Q-L-08, Q-L-09, Q-L-10, Q-L-11, Q-L-12, Q-L-13, Q-L-14

- continuation-6-plan → plan_impact → Q-L-01, Q-L-04, Q-L-09, Q-L-11

- continuation-7-files-validation → validation → Q-L-13



## Source ledger: текущий SHA256



Снят 2026-11-07T20:59:16.319793+03:00; источников 29. Вектор: `7b39af2259b1ab5c47d18cef570c51835994e80216396683029966e6d0e87066`. Полный машиночитаемый ledger и selected excerpts — runtime/AN003/source_ledger.json, source_excerpts.json. Содержимое источников не изменялось.



- S01 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\REQUIREMENTS.md` (135 строк): `09e890b6df8efd47fd7d5045d4e4391600d3587f159b81d4e8c2786bb9874b70`

- S02 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\CLAIM_ANATOMY_AND_LINK_MARKERS.md` (80 строк): `ceb2acc74c67b3cd042799626f7ce02740aae6039582ca74cfa355c9a55bf0cc`

- S03 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\dom_contract.py` (121 строк): `eeb48733fa2d252f522b609db3b8173a8969ec2ec368f21276b9e0c7af4a5243`

- S04 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\storage.py` (113 строк): `df09acf9406d8113d266a04779be753b1eb4c4c0d81bdd267e717a92271752e0`

- S05 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\projections.py` (77 строк): `2de60ed0e2897cb2220f803503a16f8f194a3b8949f4eaad8983e482dfc6b06e`

- S06 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\mockup\admission.py` (371 строк): `1f35db09af7ed738dcb8a5665e10ae23782961267bbf9370e922b69e28eea42e`

- S07 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\RESEARCH_NOTE_CLAIM_REFINEMENT.md` (39 строк): `19c5b5766e50b8a43dac7c8e9afda44236f28088cc20749cd284376f63059e0e`

- S08 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\RS001_RESEARCH.json` (259 строк): `15d1d74f535b3e5579e2e11e542efe972862120f884f945f4749183e04974f7d`

- S09 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\artifacts\RESEARCHER_AB002_A.json` (2412 строк): `6de87b4e6f2dd9ac0ef087d80521b1de4115830126da7c1dd5d8ea0303430992`

- S10 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\PL003\failure_map.json` (1763 строк): `bf3b538881185e612fe8e38ba15b5370effae05a16cf0e40fbea7acdd6cd3692`

- S11 `F:/AnalisysDataSet/readme.md` (1924 строк): `318fe16d68076596319b28795bc43d0c669a5ed85e30ea19ef734248d0ee99c9`

- S12 `F:/AnalisysDataSet/relation_type.yaml` (39 строк): `72f4467171742b70bffb9dbab4226aab226b6f7d66f53496fa39b2fb684446d0`

- S13 `F:/AnalisysDataSet/99-System/relation-types.md` (156 строк): `7a77703e6e320875bd9bda21e09e4b86811d7b3d18d4dc11ea347e850222acc2`

- S14 `F:/AnalisysDataSet/99-System/similarity-analysis.js` (137 строк): `1cf858bbe602d20b17ce12c106f2325acfafd15ac9b25e1787287b2cea6fde7d`

- S15 `F:/AnalisysDataSet/99-System/similarity-weights.yaml` (149 строк): `9b71dd2860ecd714f81fa0d435e02bba80a4d4259484e91be8327abaac8253c0`

- S16 `F:/AnalisysDataSet/99-Template/article-template.md` (366 строк): `691c726e1bf2b353617f1d06fa6cf547316757965f9cb4d0829ea04cd0a92a1e`

- S17 `F:/AnalisysDataSet/scripts/universal-cards-core.js` (3333 строк): `172bbca2268fb333c8566b886a77580760e6feac8f9084a1e5f3c7a1cb8b14eb`

- S18 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\AB002_PLAN.md` (28 строк): `129c526751325f328de4811d2580737f2f73a4cd83ad16bcbd14d0e7d25e0a86`

- S19 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\docs\FULL_IMPLEMENTATION_PLAN.md` (90 строк): `8a5fad5f56e2398e4faafb748a6acdcddbb208afd40ccebe107a3ee795e24fc2`

- S20 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\PLAN.md` (108 строк): `16ae52bbe4a6ea144f61cdcd2e6875db41f8f22d89b26820bd13850ce38b1a19`

- S21 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\tech_debt.md` (37 строк): `6c32af2751555ae60b19b2604e7e690e6e13a02de38ccd7fc452230c94e8d317`

- S22 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_CONTINUE_01.md` (46 строк): `fa6502d82025f7772ec2d10ffaa97ab4cae39fd851cb593d1e7649e0c22f4af8`

- S23 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AN003_LINKS_ANALYST.md` (37 строк): `86715a8e51470c10813ed5a6d815136de1526ffff92ab96f3a410f7fa603f54b`

- S24 `E:/opencode_harness_portable/docs/CODERS/08_ANALYST_RESEARCHER_CONTRACT.md` (152 строк): `a659489e85014b394e96ef947b3a0fc9d7bf6a1c1b0dc26eec1dc65f545d79e1`

- S25 `E:/opencode_harness_portable/docs/CODERS/09_FINDINGS_ESCAPE_HATCH.md` (75 строк): `4672c5ce1e633305e05465d57b757a1ec09e2bbfad00a2435a63caa14308bcf4`

- S26 `E:/opencode_harness_portable/shared/code-factory-process.md` (195 строк): `10e0fb1ab7af39c5ac948962807021c81fa290590b74e75f9d3e96d223ca9b39`

- S27 `C:/Users/Arhys/AppData/Local/hermes/cache/delegation/live/deleg_91a2b121/task-0.log` (70 строк): `57479b9bd9bc604eef1640000ac68fae3a1a9db08b0ec3c6cd7794b4a78bb1f9`

- S28 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\runtime\AN003\initial_partial.json` (41 строк): `40d596450a4d93b2842891737d04aa6e670651a84583d9640cdaad756ca3ebf4`

- S29 `E:\opencode_harness_portable\projects\omh-baseline-dom-mcp\cards\AB003_TD19_WORKER_PREPARED.md` (43 строк): `1d4a58c79be29a000db8c0ac13df071b2f24b91cea8c13e8fa3a5dbb994bfc64`



## Остаток и передача



Остатка анализа AN003 после PASS собственной структуры нет. Parent проверяет сдачу и запускает RS003 с точными вопросами. RS003 валидирует выводы и сравнивает механизмы, не принимает предлагаемую схему как утверждённую. Затем parent обновляет план/карту следующего worker; реализация и независимые E2E остаются впереди. Product REQUEST_CHANGES и все открытые TD сохраняются.

