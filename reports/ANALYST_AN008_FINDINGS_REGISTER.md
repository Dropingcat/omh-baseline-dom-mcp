# AN008 — сводный реестр находок и технических реализаций

Роль ANALYST · артефакт: `artifacts/ANALYST_AN008_FINDINGS_REGISTER.json` · `product_acceptance=false`, `is_approval=false` (это реестр, не приёмка).

## 0. Что проверял и что оказалось

**Что читал (34 файла, sha256 в `runtime/AN008/source_ledger.json`):** все аудиты/ревью AB003–AB006 и AU006, исследования RS006–RS009, анализы AN006/AN007, WORKER-артефакты AB003–AB007 (digest before/after), LIVE_WAVE1_VERIFY/RUN, GATE001_REPORT, решения в `docs/` (DECISION_BRIEF, EXISTENCE_SIGNAL_POLICY, WORKQUEUE, LIVE_WAVE1_FINDINGS, DECISION_NU_AU006_01_02), код `mockup/admission.py` (текущий digest **3cd21d96…** пересчитан независимо).

**Что оказалось (сверка с фактическими артефактами):**

1. **FIXED_VERIFIED только 3 находки** — AU004-F-01 (RV005 APPROVE на 1ead2d45…), AU005-F-02 и AU005-F-04 (RV005: REVIEWER_AB005 + AUDITOR_AB005 APPROVE на ca227b17…). Валидатор механически сверяет digest с артефактами-одобрениями на диске.
2. **RV006 F1/F2/F3 и AU008-A-01 — код есть (3cd21d96…), но формальная приёмка не записана**: `reports/REVIEWER_AB007.md` существует и фиксирует CONFORM с закрытием всех четырёх на той же версии, однако `artifacts/REVIEWER_AB007.json` отсутствует. По карте (FIXED_VERIFIED = независимый APPROVE **записанный** на той же версии) статус — FIXED_AWAITING_ACCEPTANCE; при появлении артефакта → переклассификация в FIXED_VERIFIED.
3. **AU006-F-04 и LVER-C3 — FIXED_AWAITING_ACCEPTANCE**: корень (нет pending-discovery) закрыт W1 в продукте (AB006 + AB007), подтверждён срезово RV006/AU008 и прототипом RS007 (pos1 memoryless), но живой повторный прогон C3 с полностью беспамятным континуатором против 3cd21d96 не выполнялся — срезовые PASS не заменяют живой E2E.
4. **AU008-L-01/L-02 — LATENT**: подтверждены в текущем коде (3cd21d96): `_pending_page` (admission.py:506-514) деривирует REJECTED, но не фильтрует терминальные; admit не проверяет decision. Активируются при появлении reject-пути — поэтому RS009 обязан идти целиком (см. §3).
5. **Открытыми остаются 10 + 1 POLICY**: AU005-F-01 (W6), AU005-F-03 (WS-F03), AU006-F-01..03, F-05 (W7), LVER-D1/D3/D4 (гигиена волны), AU007-LOW-01 (устойчивость idempotency), GATE001-F-02 (policy).
6. **Добавлено аналитиком** (не было в списке родителя, но «найдено аналитиком» по карте): AU007-LOW-01 (corrupt idempotency → INTERNAL_ERROR) и AU007-LOW-02 (namespacing — NOT_A_DEFECT) из `AUDITOR_AB005.json findings[]`.
7. **Реестр ровно один раз** — все F-находки родителей (включая закрытые) присутствуют; слияния дублей: D2 → LVER-C3, AU008-A-01 ↔ RV006-F2 (один тикет, не double-charge), F1 ↔ AU008-O-01 (O-01 опроверг security-класс), C3 ↔ AU006-F-04 (корень общий, scope разный — не слиты).
8. **Рекомендации не противоречат решениям**: O1/O2/O3, NU-AU006-01 (карта вариантов, выбор за заказчиком), «(б) частично (в)» и L1+L2 (L3 запрещён) учтены; POLITICY-записи помечены needs_user.

## 1. Реестр (таблица)

| id | severity | class | status | evidence (ядро) | fix_slice | блокеры |
|---|---|---|---|---|---|---|
| AU006-F-01 | blocking | ложная готовность | **OPEN** | AUDITOR_AU006_TASK_BASELINE.json:findings[0]; ANALYST_AN007_AU006_FINDINGS.json:orchestrator_claim_corrections[0] | S10-W7-E1/E2/E3 (последний в W7 по AN007 fix_order: после … | NU-AU006-01 (вариант политики недоступности (а)/(б)/(в)/(г)); NU-AU006-02 (авторизация изолированного живого эксперимента гейта) |
| AU004-F-01 | major | утечка | **FIXED_VERIFIED** | AUDITOR_AB003_TD19.json:verdict_rationale; WORKER_AB004_AU004F01.json:code_digest_before/code_digest_after | S0 (закрыт: AB003→RV004 APPROVE→AB004→RV005 APPROVE на 1ea… | — |
| AU005-F-02 | major | утечка | **FIXED_VERIFIED** | AUDITOR_AB004_AU004F01.json:findings[1]; REVIEWER_AB005.json:slice_verdicts WS-F02-ADMIT-BINDING | S0 (закрыт: AB005 + RV005 на ca227b17) | — |
| AU005-F-01 | major | ложная готовность | **OPEN** | AUDITOR_AB004_AU004F01.json:findings[0]; ANALYST_AN006_AU005_FINDINGS.json:findings_summary[0] | S6-W6 (идентичность доставки; исследование RS006 готово; п… | W1 идёт первой (WORKQUEUE правило 1/3); независимая приёмка среза (reviewer+auditor) после реализации |
| AU006-F-02 | major | ложная готовность | **OPEN** | ANALYST_AN007_AU006_FINDINGS.json:findings_map[1] absence_inventory; after.sql.json: | S8-W7-F02 (первый в W7; по контурам независим от F-05 — мо… | — |
| AU006-F-03 | major | ложная готовность | **OPEN** | ANALYST_AN007_AU006_FINDINGS.json:findings_map[2] state_table; after.sql.json: | S9-W7-F03 (после/вместе с W1 — без discovery pending нет п… | — |
| AU006-F-04 | major | недоказуемость | **FIXED_AWAITING_ACCEPTANCE** | ANALYST_AN007_AU006_FINDINGS.json:findings_map[3]; WORKER_AB006.json:pos_results pos1_memoryless_continuation | S6-W1 (pending-видимость реализована AB006 и доработана AB… | волна 2: повторный прогон C3 с полностью беспамятным континуатором (LIVE_WAVE1_FINDINGS §5.3); запись RV007-артефакта |
| AU006-F-05 | major | ложная готовность | **OPEN** | ANALYST_AN007_AU006_FINDINGS.json:findings_map[4]; results.json: | S8-W7-F05 (OMH-сторона; параллелен F-02 по контурам) | живой OMH read-only: срез исполняется OMH-дельтой оркестратора (PREPARED_NOT_APPLIED по AN006); NU-AU006-01: какой статус при недоступности DOM/LLM |
| LVER-C3 | major | недоказуемость | **FIXED_AWAITING_ACCEPTANCE** | LIVE_WAVE1_VERIFY.json:criteria[2] C3; LIVE_WAVE1_FINDINGS_2026-11-08.md:§2 | S6-W1 + волна 2 | волна 2: беспамятный континуатор (новый процесс, 0 унаследованных id, 0 чтения прошлых файлов); запись RV007-артефакта |
| AU008-L-01 | medium | латентная | **LATENT** | AUDITOR_AB006.json:findings[0]; admission.py:506-514 (3cd21d96) | S2-WS-REJECT (обязан идти ЦЕЛИКОМ: dom_reject + терминальн… | не закрывать отдельно: L-01/L-02/dom_reject — один срез S2 |
| AU008-L-02 | medium | латентная | **LATENT** | AUDITOR_AB006.json:findings[1]; admission.py:(3cd21d96) | S2-WS-REJECT (вместе с L-01 и dom_reject) | не закрывать отдельно: срез S2 |
| GATE001-F-02 | medium | неудобство | **POLICY** | GATE001_REPORT.json:decision_matrix.noninteractive_terminates; GATE001_REPORT.json:decision_matrix.fail_closed_on_raise | S10-W7-E3 (код только ПОСЛЕ решений NU-AU006-01/02 — gover… | NU-AU006-02 (авторизация эксперимента); NU-AU006-01 (политика недоступности) |
| RV006-F2 | medium | недоказуемость | **FIXED_AWAITING_ACCEPTANCE** | REVIEWER_AB006.json:findings F2 / checks RV006-10; admission.py:466-503 (_pending_page) | S1-AB007 | artifacts/REVIEWER_AB007.json отсутствует |
| LVER-D3 | moderate | недоказуемость (доказательная база прогона) | **OPEN** | LIVE_WAVE1_VERIFY.json:discrepancies D3; LIVE_WAVE1_FINDINGS_2026-11-08.md:§3 D3 | S3-W3 (один процесс — один таймлайн; кадр на каждый шаг; о… | — |
| AU005-F-04 | minor | недоказуемость | **FIXED_VERIFIED** | AUDITOR_AB004_AU004F01.json:findings[3]; REVIEWER_AB005.json:slice_verdicts WS-F04-TYPED-ABSENCE | S0 (закрыт: AB005 + RV005 на ca227b17) | — |
| AU005-F-03 | minor | утечка | **OPEN** | AUDITOR_AB004_AU004F01.json:findings[2]; continue01_reconciliation.json:O2_raw | S7-WS-F03 (O2-непровенансные поля; параллелен W6/W7) | O2 закреплён заказчиком: провенанс доступного клайма виден всегда — не переоткрывать, фильтровать только непровенансные поля |
| LVER-D1 | minor | недоказуемость | **OPEN** | LIVE_WAVE1_VERIFY.json:discrepancies D1; LIVE_WAVE1_FINDINGS_2026-11-08.md:§3 D1 | S3-W4 (авто-сверка «артефакт↔диск↔БД» перед сдачей волны; … | — |
| LVER-D4 | minor | недоказуемость | **OPEN** | LIVE_WAVE1_VERIFY.json:discrepancies D4; LIVE_WAVE1_FINDINGS_2026-11-08.md:§3 D4 | S3-W4 (авто-сверка полей RUN.json ↔ summary.json ↔ кадры) | — |
| AU007-LOW-01 | low | недоказуемость | **OPEN** | AUDITOR_AB005.json:findings[0]; c5c_corrupt: | S13-ROBUST (малый срез устойчивости; параллелен W6/W7) | — |
| AU007-LOW-02 | low | — | **NOT_A_DEFECT** | AUDITOR_AB005.json:findings[1]; AUDITOR_AB005.json:own_runs C2_BYPASS | нет | — |
| AU008-A-01 | low | недоказуемость | **FIXED_AWAITING_ACCEPTANCE** | AUDITOR_AB006.json:findings[2]; admission.py:466-471 | S1-AB007 (тот же тикет, что RV006-F2; не засчитывать дважды) | artifacts/REVIEWER_AB007.json отсутствует |
| RV006-F1 | low | неудобство | **FIXED_AWAITING_ACCEPTANCE** | REVIEWER_AB006.json:findings F1 / checks RV006-09; WORKER_AB007.json:digest_before/digest_after | S1-AB007 (код готов; приёмка = запись RV007-артефакта) | artifacts/REVIEWER_AB007.json отсутствует — отчёт reports/REVIEWER_AB007.md (CONFORM на 3cd21d96) есть, формальная запись артефакта не завершена |
| RV006-F3 | low | недоказуемость | **FIXED_AWAITING_ACCEPTANCE** | REVIEWER_AB006.json:findings F3; admission.py:503 | S1-AB007 | artifacts/REVIEWER_AB007.json отсутствует |
| GATE001-F-01 | info | опровержение гипотезы | **NOT_A_DEFECT** | GATE001_REPORT.json:runs G1..G5; GATE001_REPORT.json:decision_matrix.fail_closed_on_raise | нет (поддерживающее доказательство для W7/E3) | — |

Статусы: **FV**=FIXED_VERIFIED, **FAA**=FIXED_AWAITING_ACCEPTANCE, **LAT**=LATENT, **NAD**=NOT_A_DEFECT.

## 2. Реализации для незакрытых (подробно в артефакте `implementations[]`)

| IMP | находки | источник/варианты | суть |
|---|---|---|---|
| IMP-01 | AU005-F-01 | artifacts/RESEARCHER_RS006_AU005_FIXES.json | delivery.py: идентичность доставки = (intent, receiver, view_scope_digest, source_revision |
| IMP-02 | AU005-F-03 | artifacts/RESEARCHER_RS006_AU005_FIXES.json | public_dto.py (71-75,100-105,113-121): отделить обязательную провенанс-проекцию (origin_br |
| IMP-03 | AU006-F-01 | artifacts/GATE001_REPORT.json | E2 (DOM-сторона, реализуема уже сейчас в mockup): submit/admit принимают обязательный base |
| IMP-04 | AU006-F-02 | документы/вопросы AN007 + варианты (2) |  |
| IMP-05 | AU006-F-03 | artifacts/ANALYST_AN007_AU006_FINDINGS.json + варианты (2) |  |
| IMP-06 | AU006-F-05 | artifacts/ANALYST_AN007_AU006_FINDINGS.json + варианты (2) |  |
| IMP-07 | AU008-L-01 | artifacts/RESEARCHER_RS009_REJECT_PATH.json | admission.py _pending_page (476-500) и _pending_count (546+): исключить терминальные ADMIT |
| IMP-08 | AU008-L-02 | artifacts/RESEARCHER_RS009_REJECT_PATH.json | admission.py admit (218-224): читать last review и проверять decision=='approve'; иначе CA |
| IMP-09 | LVER-D1, LVER-D4 | d + варианты (2) |  |
| IMP-10 | LVER-D3 | d + варианты (2) |  |
| IMP-12 | GATE001-F-02 | artifacts/GATE001_REPORT.json | primed-allow 'get baseline': non-interactive команда, дающая агенту намеренно пройти гейт  |
| IMP-13 | AU007-LOW-01 | документы/вопросы AN007 + варианты (2) |  |

Ключевые правила реализаций: AU005-F-01 берёт RS006 answers_f01 (идентичность доставки = intent+receiver+view_scope_digest+source_revision+delivered_byte_hash, UNIQUE-индекс, legacy-ack инертны); L-01/L-02 берут RS009 (31/31 PASS, V-PEND-REJ/V-COUNT/CANDIDATE_REJECTED); AU006-F-01/GATE001-F-02 — только после решений NU-AU006-01/02, E1+E2 первыми, E3 hardening; AU006-F-02/03/05 — по AN007 Q-AN007-01/03/02 (F-02 и F-05 — варианты, т.к. отдельного RS-исследования нет), плюс у каждого OPEN — негативный контроль (в `fix_slice_neg_control`).

## 3. Порядок срезов (15) с зависимостями

- **S0-closed** (Закрытые срезы (история)) — находки: AU004-F-01, AU005-F-02, AU005-F-04; state: CLOSED; требует завершённых: —
  - примечание: AB003/RV004, AB004/RV005, AB005/RV005 — независимые APPROVE на версиях 08aa9a9b/1ead2d45/ca227b17
- **S1-AB007** (Фикс пагинации pending (RV006 F1-F3 + AU008-A-01)) — находки: RV006-F1, RV006-F2, RV006-F3, AU008-A-01; state: CODE_DONE_AWAITING_ACCEPTANCE (3cd21d96; reports/REVIEWER_AB007.md = CONFORM, artifacts/REVIEWER_AB007.json отсутствует); требует завершённых: S0-closed
  - примечание: меняет admission.py (_pending_page) — следующий срез, трогающий ту же функцию, обязан идти после приёмки S1
- **S2-WS-REJECT** (Путь отказа RS009 (dom_reject + dom_drop + гейты)) — находки: AU008-L-01, AU008-L-02; state: PLANNED (исследование готово: RS009 31/31); требует завершённых: S1-AB007
  - **ЦЕЛИКОМ (mandatory together)**: dom_reject (словарь reason_code, rationale, INDEPENDENCE); dom_drop (root-автор, drops-таблица); терминальный фильтр _pending_page (ADMITTED/REJECTED/DROPPED вне items и count); гейт decision=='approve' в admit (CANDIDATE_REJECTED)
  - примечание: ЧАСТИЧНОЕ исполнение среза запрещено: если реализуют reject без pending-фильтра и admit-гейта — L-01/L-02 из LATENT станут активными. Словарь без OTHER; апелляция — re-review другим root (порог owner-гейта — вопрос заказчика NU-03)
- **S3-W3W4** (Гигиена прогона (W3/W4): один процесс—один таймлайн; авто-сверка артефактов) — находки: LVER-D1, LVER-D3, LVER-D4; state: PLANNED; требует завершённых: —
  - до: волна 2 (без этого волна 2 недоказуема)
  - примечание: не продукт; пакет с W5; приёмка — повторный прогон без расхождений
- **S4-W5** (Критерии волны: разделить C1 на «содержимое»/«происхождение», уточнить C4-C7) — находки: —; state: PLANNED; требует завершённых: —
  - до: волна 2
  - примечание: правка acceptance_wave1.json; охватывает C1* (спорный критерий), C4 NOT_CHECKED
- **S5-W2** (Сценарий устаревания (C4): основание принято → в источнике новая версия → сигнал в ответе) — находки: —; state: PLANNED; требует завершённых: S1-AB007, S3-W3W4, S4-W5
  - примечание: без видимости незавершённого (W1) сценарий нечем продолжить — W1 блокирует W2 (WORKQUEUE правило 1/2)
- **S6-W6** (Идентичность доставки (AU005-F-01)) — находки: AU005-F-01; state: READY_FOR_WORKER (исследование RS006 готово: answers_f01, прототип m1..m7/d1); требует завершённых: S1-AB007
  - нельзя взаимозачесть: не засчитывается за W1 и наоборот (WORKQUEUE правило 3)
  - нельзя взаимозачесть: F-01 (AU005) не заменяет AU006-F-01 (разные объекты: квитанция доставки vs сверка базлайна)
  - примечание: срез в составе AB005-цепочки по плану RS006: WS-F04(закрыт) → WS-F02(закрыт) → WS-F01 → WS-F03; F-02 и F-01 принимаются раздельно
- **S7-WS-F03** (O2-непровенансные branch-поля (AU005-F-03)) — находки: AU005-F-03; state: READY_FOR_WORKER (исследование RS006 answers_other Q-F03-01); требует завершённых: —
  - параллельно: S6-W6, S8-W7-F02, S8-W7-F05
  - примечание: не требует W1; может идти параллельно
- **S8-W7-F02F05** (W7 часть 1: достаточность оснований (F-02) + DOM-эвиденс (F-05)) — находки: AU006-F-02, AU006-F-05; state: PLANNED (F-02: варианты IMP-04; F-05: IMP-06 по Q-AN007-02); требует завершённых: —
  - примечание: независимы по контурам (DOM-контракт vs OMH-reducer) — вместе или параллельно; AN007 fix_order: F-02 первым
- **S9-W7-F03** (W7 часть 2: ready-дерево (F-03)) — находки: AU006-F-03; state: PLANNED (IMP-05); требует завершённых: S1-AB007
  - примечание: F-04 (discovery pending) — предусловие практического закрытия F-03 (клиент должен уметь dispose); F-04 уже реализован в S1/W1 — нужна его приёмка
- **S10-W7-F01E** (W7 часть 3: сверка базлайна (E1/E2/E3) + primed-allow) — находки: AU006-F-01, GATE001-F-02; state: PLANNED (IMP-03, IMP-12); требует завершённых: S8-W7-F02F05, S9-W7-F03
  - примечание: GATE001 уже доказал работоспособность хука (E3 viable) — обязательность сверки (E1/E2/E3) разрешена к планированию после GATE001; F-01 (AU006) последний в W7 по AN007 fix_order
- **S11-HISTORY** (История работы (RS008: dom_history, keyset, правило эмиссии, reject/drop чтение)) — находки: —; state: PLANNED (исследование RS008 готово: варианты A..E, 23/23 PASS); требует завершённых: S2-WS-REJECT
  - примечание: после reject-пути: истории нечего сказать про отказ, пока отказ нельзя записать; «что отвергли» — ответить нечем
- **S12-SIGNAL** (Сигнал существования расхождения (политика L1/L2)) — находки: —; state: PLANNED (политика принята: docs/EXISTENCE_SIGNAL_POLICY_2026-11-08.md; L3 запрещён); требует завершённых: S2-WS-REJECT
  - примечание: L2 по опоре требует контестации/отказа; L1 — агрегат на старте базлайна; вопрос заказчика NU-04 (факт форка для AA-only)
- **S13-ROBUST** (Устойчивость idempotency-кеша (AU007-LOW-01)) — находки: AU007-LOW-01; state: PLANNED (IMP-13 V1); требует завершённых: —
  - параллельно: S6-W6, S7-WS-F03
- **S14-W8** (Идентичность плана (PLAN_ITEM, семейства, impact)) — находки: —; state: NOT_STARTED (docs/PLAN_IDENTITY_AND_IMPACT_2026-11-08.md); требует завершённых: S1-AB007, S5-W2
  - примечание: W8 не начинать, пока W1-W2 не закрыты (WORKQUEUE правило 5)

**Правила порядка (slice_rules):**
- W1 (S1/S6-W1) идёт первой и блокирует W2; W6 (идентичность доставки) не засчитывается за W1 и наоборот — разные объекты (кеш допуска/доставка ≠ видимость незавершённого)
- Путь отказа RS009 (S2) обязан идти ЦЕЛИКОМ: dom_reject + терминальный фильтр _pending_page (REJECTED не в pending) + гейт decision в admit — иначе латентные AU008-L-01/L-02 становятся активными при появлении reject-пути
- E1/E2/E3 (обязательность сверки) — разрешены после того, как GATE001 доказал работоспособность хука (fail-closed, хостовое покрытие); исполнение — после решений NU-AU006-01/02
- История (RS008) и сигнал существования (L1/L2) идут после пути отказа — иначе на вопрос «что отвергли» ответить нечем
- Гигиена прогона (W3/W4/W5) — не продукт, но без неё волна 2 недоказуема; делается пакетом до волны 2
- Ни одна находка не закрывается по факту карты/прогона/согласия заказчика: только независимые reviewer+auditor на ТОЙ ЖЕ версии кода (сверка digest)
- Ни одна находка не закрывается «исправлением» другой: каждая требует своей негативной E2E (AN007 cannot_substitute)
- AU008-A-01 и RV006-F2 — один тикет (AB007): не засчитывать дважды

**Критическая связка:** S2-WS-REJECT обязан идти целиком и после S1-AB007 (та же функция `_pending_page`). Если реализовать reject-путь без терминального фильтра pending и без гейта `decision=='approve'` в admit — латентные AU008-L-01/L-02 станут активными. История (S11) и сигнал L1/L2 (S12) — строго после S2: «что отвергли» нечем ответить, пока отказ не записывается.

## 4. Что осталось без решения (needs_user)

- **NU-01** — блокирует: S10 (E1/E2/E3): без политики нельзя спроектировать гейт и статусы, IMP-03, IMP-12. Какую политику выбрать при недоступности DOM/LLM/хуков: (а) останавливать только материальные изменения, (б) ограниченный офлайн-журнал со сверкой, (в) останавливать всё, (г) работа только с явной регистрацией «вне базы» и автоподъёмом? Рекомендация аналитиков: (а) как база + узкая часть (б) только для наблюдений (DECISION_NU:62-64); выбор за заказчиком.
- **NU-02** — блокирует: S10, IMP-03 (выбор точки контроля), IMP-12 (E3 rollout). Авторизуете ли изолированный живой эксперимент гейта (отдельный профиль/БД/ветка/задача, хук только для него, kill-switch + TTL + уборка) для измерения H1-H5 (порядок хука, fail-open/closed, отказ старта, задержка, ложные отказы)? Без него выбор «хук vs обёртка запуска» недоказуем, и защита остаётся политикой.
- **NU-03** — блокирует: S2 (полная реализация апелляции; основной reject-контракт реализуем и без неё). Кто и по какому порогу может запросить re-review/апелляцию отвергнутого кандидата (owner-гейт)? RS009 спроектировал «re-review другим независимым root», но порог «кто может запросить» — открытый policy-вопрос.
- **NU-04** — блокирует: S12 (часть реализации L1/L2). Показывать ли AA-only клиенту САМ ФАКТ расхождения веток (форк существует), без содержимого? O2 это не закрепляет; RS008 q7: по умолчанию — не показывать (no-marker правило, согласовано с bmap-фильтром AU004-F-01).
- **NU-05** — блокирует: S10 (семантика базлайнового гейта). Пустой baseline: типизированный NO_BASELINE (информационно + запрет засчитывать покрытие) или reject? DECISION_BRIEF п.3: рекомендован NO_BASELINE; не решено.
- **NU-06** — блокирует: (вне реестра: слайс графа). Граф связей при запросе клайма: подтвердить числовые значения глубины (минимум 1, потолок 3). Связано с AU004-F-01-классом как предусловие графа (dependencies — рёбра без фильтра), но сам граф — отдельная функция вне реестра.
- **NU-07** — блокирует: (вне реестра). Разные ветки с 2-5 актуальными версиями: кто и как сводит (DECISION_BRIEF п.2)? ОТКРЫТО. Влияет на проекцию FORKED/граф, не на текущие находки реестра.
- **NU-08** — блокирует: (вне реестра). Кто признаёт сходимость версий (политика дублей уже принята: возврат с обоснованием отличий; механизм признания — нет, DECISION_BRIEF п.4).

Решение по NU-01/NU-02 — обязательное условие S10 (AU006-F-01, GATE001-F-02); без них обязательность сверки остаётся политикой (цена отказа — AU006-F-01 UNVERIFIED_live, DECISION_NU:99).

## 5. Валидация

`runtime/AN008/validate_an008.py` (exit 0): позитивные проверки PASS, негативных контролей 12, все отвергнуты как ожидалось (ALL_REJECTED_AS_EXPECTED). Полный чек-лист отклонений: находка без evidence; FIXED_VERIFIED без независимого APPROVE на той же версии (механическая сверка digest с артефактом); реализация, дублирующая RS-исследование без ссылки; OPEN без fix_slice/негативного контроля; реестр без закрытых находок и без обязательного набора id; дубли id; битые ссылки срезов; расхождение coverage.

Покрытие: источников 34, находок 24, реализаций 12, срезов 15, вопросов заказчику 8.
