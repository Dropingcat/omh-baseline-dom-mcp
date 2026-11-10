# AN006 — анализ подтверждённых находок AU005 + сверка PL003 (CONTINUATION 01)

Роль: ANALYST. Статус: COMPLETED (material synthesis). `product_acceptance=false`, `is_approval=false`. Код не тронут: digest 16 файлов = `1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf` (пересчитан методом SEC003 в начале работы). Записано только в `artifacts/ANALYST_AN006_AU005_FINDINGS.json`, `reports/ANALYST_AN006_AU005_FINDINGS.md`, `runtime/AN006/**`.

## 0. Подозревал → проверил → оказалось

| Подозревал | Проверил | Оказалось |
|---|---|---|
| AU005 — черновик, findings надо перепроверять | Прочитал artifacts+report AU005 полностью; parent верифицировал verifier (exit0) и 3849 хешей; SQL ack-хеши F-01 перечитаны из results.json | Находки F-01..F-04 — подтверждённый материал, не черновик. Трассировка к коду выполнена мной, всё сходится |
| F-01 — «просто idempotency» | admission.py:215-217,335,325-381; delivery.py:44-65 | Дефект identity: outbox digest не содержит view scope/receiver; confirmed() для YAML сверяет только branch/revision; sync skip по confirmed() оставляет union недоставленным, explicit export пишет байты без ack. Физически: 5fadbab7... (AA-only) vs 113628b8... (union-first) |
| F-02 — «кто-то угадал ключи» | admission.py:112-117,175-181; replay frames двух PID | Никакого угадывания: dedupe по (work,'admit:'+principal,key) срабатывает ДО проверок digest/scope кандидата; владение старым key+digest — знание прошлой операции, не capability. Replay не создаёт новых фактов |
| F-03/F-04 — «все AB-строки = утечка» / «все ошибки = эскалация» | public_dto.py:71-75,100-121; projections.py:25,47,53; server.py:212-216; O2 решение заказчика | О2 разрешает origin доступного клайма; F-03 — только non-provenance поля (applicability/excluded_branches). F-04 — отсутствие ветки ZZ (типизированное отсутствие vs INTERNAL_ERROR/SYNCED); не attacker-эскалация |
| «Отсутствие E2E в HUD = отсутствие E2E» | PL003 validation.json, SEC003/QA003 per_check, RV003/AU003 поиск | Наоборот: SEC/QA материалы COMPLETED с RECEIPT; RV003/AU003 отсутствуют в дереве (0 hits) — это остаток, не доказуемое присутствие. Проверено ограниченным поиском |
| O3 — «только наблюдение оркестратора» | continue01_verified.json:O3 + SQL read-back | O3 физически воспроизведён (два PID) — CONFIRMED, REQUEST_CHANGES. Не «наблюдение» |

## 1. Вердикт по AU005 (принят как материал)

AU005: `COMPLETE_WITH_LIMITS` / `REQUEST_CHANGES`, `product_acceptance=false`. Четыре находки подтверждены и трассированы (полная таблица первопричин и evidence — `runtime/AN006/findings_map.json`):

| ID | Sev | Корень в коде | Независимость среза |
|---|---|---|---|
| F-01 | major | admission.py:215-217 (outbox identity без scope/receiver), 335 (skip по confirmed), 325-381; delivery.py:44-65 (identity по (intent,tx,digest,target), YAML branch/revision only) | независим от F-02 (другой путь: sync/delivery vs admit/dedupe); с F-03 делит только риск общего scope-хелпера |
| F-02 | major | admission.py:112-117 (dedupe до binding), 175-181 (порядок candidate→dedupe→проверки) | независим; security-путь, отдельный срез |
| F-03 | minor | public_dto.py:71-75,100-121 (нескалированные list-поля); projections.py:25,47,53; admission.py:277-283 | отделим от F-01/F-02; не менять origin (O2) |
| F-04 | minor | admission.py:111 (head fetchone()[0] → TypeError), 230-233,245-251,325-381; server.py:212-216 (INTERNAL_ERROR) | малый независимый срез |

Связь с AB004: F-01 — дефект интеграции AB004 (scoped YAML через AU004-F-01); F-02/F-03/F-04 — предсуществующие пути/политики, вскрытые новыми условиями. Никакие продукты/тесты/tech_debt/OMH не изменялись.

## 2. Что уже подтверждено (не переоткрывать)

- O1: НЕ скрывать stale; честный сигнал — не дефект; восстановление revalidation — GAP/TD-DOM-15.
- O2: происхождение доступного клайма видно всегда; НЕ раскрывать исходную ветку/голову/dependencies; non-provenance membership/exclude — отдельная политика (F-03).
- O3: delivery identity = tx + receiver + source revision + view scope + byte hash; scoped ACK ≠ full delivery (F-01 CONFIRMED).
- Search: итеративная пере-центрация; depth1..3 — TEST_PARAMETER одного ответа; grants не расширяются; К1/К2/К3 — только после симуляций.
- AU006 — отдельная обязательность; его незавершённые выводы не использовались, его пробы не дублировались.

## 3. Tracing и evidence (кратко; полная карта — findings_map.json)

- **F-01**: s4 delivery: AA-only sync лист с deps={} (5fadbab7..., 1821B); union-first — deps={AB:1} (113628b8..., 1837B); после union sync после AA — файлов не прибавилось, ack не тронут; explicit export создал full bytes (113628b8), `receipt_unchanged_after_explicit_export=true`. `continue01_verified.json:O3` — оба SYNCED, отпечатки различаются.
- **F-02**: s4+s5 replay: AB query SCOPE_DENIED; admit(AA candidate, чужой review, prior AB key/digest) → кешированный AB DEMO_ADMITTED receipt (branch AB, rev1, private claim UUID 32a1d9d3-…, tx 9defba55-…); fresh key → DIGEST_MISMATCH; SQL receipt exists=true; новых фактов нет. PID 5248/3204.
- **F-03**: s1 F2: AA-origin a2 с item.applicability [AA,AB]; excluded_branches [AB]; exclude-событие с branch AB при AA-only; поля не bmap, не скалируются.
- **F-04**: s3 AA_ZZ: query/resume ZZ → INTERNAL_ERROR (TypeError из head() к server catch-all); sync_status → SYNC_STATUS (пусто); sync → SYNCED (пусто). No leak (AB_token=false).

## 4. Вопросы ресерчеру (точные) — runtime/AN006/questions_for_researcher.json

8 вопросов с id/exact_question/why/source/evidence/positive+negative+fault controls:
- Q-F01-01/Q-F01-02: схема identity доставки (tx+receiver+source_revision+view_scope+byte_hash), миграция/legacy receipts, негативные E2E-комбинации (sequential/reversed grant, lost-reply, explicit export) + физический факт каждого чека.
- Q-F02-01/Q-F02-02: модель привязки idempotency, сохраняющая законное восстановление после потерянного ответа; граница «знание ключа ≠ capability».
- Q-F03-01: политика раскрытия non-provenance полей без exists-oracle и без отката O2.
- Q-F04-01: единый typed absence для granted-but-absent ветки на query/resume/sync_status/sync.
- Q-PL003-01: подтвердить отсутствие RV003/AU003 ограниченным поиском + контракт недостающих ролей (без подмены RV004/AU004).
- Q-ORCH-01: верифицировать заявления оркестратора (O3, O2 provenance, приёмка AU005).

## 5. Границы worker-срезов (проект, НЕ применён)

`questions_for_researcher.json:worker_slice_boundaries`:
- WS-F04-TYPED-ABSENCE (низкий риск, без зависимостей, первый) — «что отсутствует» = один типизированный статус, без widening и без raw-деталей.
- WS-F03-SCOPE-POLICY (средний; зависит от Q-F03-01) — полевая политика, без потери origin O2.
- WS-F02-ADMIT-BINDING (высокий риск: admit; зависит от Q-F02-01; отдельный срез) — binding candidate/review/scope в кеш-хит, сохранив легальный retry.
- WS-F01-DELIVERY-IDENTITY (высокий риск: schema/migration; зависит от Q-F01-01/02; отдельный срез) — identity доставки, legacy ack readable, миграция версионируется.
- WS-RV003-AU003-MATERIAL-REVIEW (процессная роль; parent dispatch).

Порядок: F-04 → F-03 (после research) → F-02/F-01 (после research); RV003/AU003 — параллельно как роль.

## 6. PL003 сверка (READ-ONLY) — runtime/AN006/PL003_reconciliation.json

Frozen delta: `runtime/PL003/omh_plan_delta.json` (PREPARED_NOT_APPLIED). Сверка «план → исполнение → доказательство → остаток» по каждой задаче и каждому check_id (CHK-A2-01..07, CP-PL-01..17):

| Задача | План (frozen) | Факт | Доказательство | Остаток |
|---|---|---|---|---|
| PL003 | attach material, material_prepared_only | COMPLETE_MATERIAL | validation.json PASS_MATERIAL_HANDOFF_ONLY 542/542, product_acceptance=false | применение дельты — только оркестратор после валидации хешей |
| SEC003 | update → pending | COMPLETED / REQUEST_CHANGES | artifacts/SEC003_SECURITY.json, runtime/SEC003/ | находки на прежнем digest 715b1ca8… (до AB004); 8 availability/shape → QA003; независимое ревью RV003 отсутствует |
| QA003 | update → pending | COMPLETED / REQUEST_CHANGES | artifacts/QA003_FAILURE_TESTER.json, runtime/QA003/ | CP-PL-02/03/04 NOT_TESTED; CP-PL-11/12/13/17 GAP (нет API); независимый аудит AU003 отсутствует |
| RV003 | независимое ревью SEC/QA материала | NOT_EXECUTED (0 hits по всему дереву; RV004/AU004 — эквивалент по AB004-fix, не материала) | bounded rglob | исполнить роль RV003 по frozen acceptance |
| AU003 | независимый негативный аудит | NOT_EXECUTED (0 hits) | тот же поиск | исполнить AU003 после RV003, на точной текущей версии 1ead2d45… |
| AB003-TD19-P0 | prepared_not_dispatched | PREPARED (карта + worker/reviewer/auditor артефакты есть; TD-DOM-19 open) | cards/, artifacts/WORKER_AB003_TD19.json, tech_debt.md | parent narrow dispatch с фактическим fingerprint; исправление + независимые review/аудит текущей версии |

**Ключевой факт сверки:** SEC003 и QA003 исполнены на code digest `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3` (15 файлов) — это версия ДО правки AB004 (admission/public_dto/server). Текущий digest `1ead2d45…` (16 файлов). Поэтому их находки формально относятся к прежней версии; подтверждение на текущей версии — ровно область недостающих RV003/AU003. Это не откат SEC/QA (выполненное не откатывается) и не закрытие долгов.

Чек-статусы по 24 PL003-идентификаторам: SEC003 → 12 EXECUTED_NEGATIVE / 4 GAP (CP-PL-11,12,13,17) / 8 NOT_TESTED; QA003 → 18 EXECUTED_NEGATIVE / 4 GAP / 3 NOT_TESTED по PL003-идам + 2 собственных (QA-NOV-01, SEC-NOV-01). «Отсутствие записи в HUD ≠ отсутствие E2E и наоборот»: материалы подтверждены физическими evidence-файлами SEC/QA, а не только надписями.

## 7. Подготовленная дельта (PREPARED_NOT_APPLIED) — runtime/AN006/omh_delta_prepared.json

- Зарегистрировать недостающие роли RV003 (независимое ревью SEC/QA материала) и AU003 (негативный аудит на текущей версии) — применить может только оркестратор через OMH-инструменты, с валидацией артефактов и хешей.
- Запланировать worker-срезы WS-F04→F03→F02→F01 после ответов research-вопросов.
- Явный no-op: НЕ откатывать SEC003/QA003 в pending; НЕ закрывать TD19/full-system acceptance; NOT закрывать done_unverified 7/8.
- Дельту НЕ применяю: `applied=false`, никаких OMH-записей, долгов, диспатчей, product-правок.

## 8. Исправления выводов оркестратора (чек-лист 8)

1. O3 — не «наблюдение», а CONFIRMED-дефект: физически воспроизведён AU005 s4 (два PID; ACK-хеши 5fadbab7…/113628b8…, SQL + YAML-файлы). AB004 как «scoped YAML → полная доставка» НЕ принимается.
2. О2 — происхождение доступного клайма законно видимо (решение заказчика 2026-11-08); утверждение «вся provenance = утечка» неточно. Утечка в прежнем смысле относится только к non-provenance полям (F-03).
3. Приёмка: parent принял МАТЕРИАЛ AU005 (verifier exit0 + 3849 хешей + SQL ack read-back), НЕ продукт; AU005 сам REQUEST_CHANGES. Любое «принято = можно закрывать AB004» — ошибка.
4. «SEC/QA прошли» — неверная формулировка: SEC003/QA003 — REQUEST_CHANGES, product_acceptance=false; их вердикты — материал с находками.
5. Всё неподтверждённое (например, датировки precopy) — UNVERIFIED, не факт.

## 9. Не проверено / границы

- Не запускался повторный global E2E; продукт read-only; отсутствуют live OMH/Git/network/install/секреты/субагенты.
- Незавершённый AU006 не читался и не использовался.
- Датировки времени копирования/файлов из прошлых аудитов не верифицировались заново.
- Итоговый выбор схемы миграции F-01 и модели binding F-02 — за исследователем (вопросы поставлены), не за аналитиком.
- Отсутствие RV003/AU003 доказано ограниченным поиском по именам файлов в дереве проекта; если эквивалент существует под другим именем/местом вне дерева — он не обнаружен этим методом (отмечено в Q-PL003-01).

## 10. НАХОДКИ (эскап-хэтч)

- Уровень 1: исправлений не требовалось — продукт не трогался.
- Уровень 2: F-01..F-04 зафиксированы в findings_map.json (не новые TD-ID; привязки: F-01 → RV005 O3 repro, не дубликат TD-DOM-13; F-02 → новый security-путь; F-03 → RV005 O2 remainder; F-04 → связан с TD-DOM-07). PL003-остаток RV003/AU003 зафиксирован в reconciliation; долги не закрывались.
- Уровень 3 [GATE]: ни одно решение заказчика O1/O2/O3/search не переоткрыто. Остаток для оркестратора: (1) применить omh_delta_prepared только после валидации; (2) заdispatch отсутствующих RV003/AU003; (3) worker-срезы F-01..F-04 после research-ответов; (4) НЕ принимать AB004/продукт по этому анализу.

## 11. Воспроизведение/валидация

```bash
PY="$P/.venv/Scripts/python.exe"; env -u PYTHONPATH -u PYTHON -u PYTHON_BIN -u PYTHON_VENV -u VIRTUAL_ENV -u PYTHONSCRIPT -u PYTHONHOME "$PY" -B runtime/AN006/validator_AN006.py
```

Валидатор проверяет: все выходные файлы существуют и валидны; digest кода; `applied=false` у дельты; каждый finding_id покрыт; каждая ссылка на evidence существует; PL003-факты (RV003/AU003 отсутствуют, SEC/QA статусы, чек-иды) согласованы с артефактами; отрицательные контроли (подмена ссылок/долгов/применения) дают FAIL.
