# QA003 — E2E отказоустойчивость / восстановление (negative failure-tester)

Роль QA003 (континуация 03, финальные артефакты). Полный контракт: `cards/QA003_FAILURE_TESTER.md`; план и весь материал — в `runtime/QA003/`. Кодовая ревизия заморожена на byte-дигесте `715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3` (пересчитан теми же sorted-json hashes mockup/**/*.py — совпадение).

## 0. Подозревал → проверил → оказалось

| Подозрение | Проверил | Оказалось |
|---|---|---|
| `sentinel_leaked_to_target=true` — продукт протёк foreign sentinel в target | QA-NOV-01 (own risk-derived: malformed own tx + foreign sentinel + restart между send и observation, liar→ambiguous port); сравнение с oracle-ключом `setup_target` в `omh-target.json` | **Опровергнуто.** `sentinel_leaked_to_target=true` — это fixture-ключ, который оракул (`setup_target`) сам пишет в `omh-target.json` (foreign-sentinel-77, fixture digest `32a4ec1e320b80ef`), а не артефакт пути доставки продукта. Нет foreign receipt; единственный ack привязан к своему matched-наблюдению; эффект остаётся ambiguous. Не утечка. |
| `b_control_preserved=false` — B-контроль сломан / AB протёк в AA | `analyze_b_control.py`: пересчёт с receipt + read-only fixture DB (claims.raw, branch_heads, ab_claim_ids, канарейки) | **PROBE_FIXTURE_BUG_NOT_LEAK.** Все 3 AB claim ID и AB body-канарейка видны B-only до и после негативов; ни одного AB body-канарейки/claim ID в AA-поверхностях. Причина — `generator.claim_item()` не пробрасывает idx в `raw_bytes()`, все claim ветки несут одну канарейку (idx=0); probe ожидал 3 различных токена. B-контроль фактически сохранён (`b_control_actually_preserved=true`). |
| TD19/20/21 recheck подтвердит prior утечки | Перезапуск с изменённым порядком поверх (export→resume→sync_status→trace→snapshot→query); два seed | **Prior воспроизведены, не закрыты и не дублированы.** CHK-A2-01/02/04 — скрытая AB-revision-метаданные в AA read-поверхностях (TD-DOM-19, prior SEC003-F-01); CHK-A2-05/06 — raw AttributeError shape (TD-DOM-20); CHK-A2-07 — tamper-отказ через run-специфичные create-only манифесты (TD-DOM-21). |
| H-LINK / selective-search / backlink поверхности раскроют существование/ID запрещённой ветки | tools/list + AST-скан (CP-PL-11/12/13/17) | **GAP, не утечка.** Поверхностей нет на проводе (12 tools) и в AST; GAP-SEARCH/BRANCH-SEARCH/REFINEMENT/LINKS записаны, не PASS и не NOT_APPLICABLE. |
| REPLACE-проба (CP-PL-05) докажет перезапись | UPDATE/DELETE/INSERT OR IGNORE/upsert + REPLACE probe | UPDATE claims/DELETE event/INSERT OR IGNORE/upsert — IMMUTABLE (1811), строки байт-идентичны. `UPDATE branch_heads SET revision=0` принят (rowcount=1) — prior TD-DOM-12. REPLACE-проба упала «no such column: x» (SQL-ошибка probe) и **НЕ засчитана**. |
| CP-PL-10 busy/read-only вызовут lock/отказ | storage-негативы: invalid header, directory-at-path, legacy layout, busy, read-only | Куры: STORAGE_CORRUPT (26), STORAGE_UNAVAILABLE (CANTOPEN_ISDIR 526), MIGRATION_REQUIRED (bytes preserved). Части занятости: WAL допускает читателей, read вернул SNAPSHOT — lock **не воспроизвёлся**; store.read_only — не enforced ФС-состояние. **Оба подкейса NOT_TESTED честно**, не PASS. |

## Вердикт

**REQUEST_CHANGES.** Исполнитель не принимает продукт: `product_acceptance=false`, `is_approval=false`. Статусы — состояния исполнения негативного тестирования, НЕ acceptance. Вердикт никогда не формулируется как SAFE/secure/full-system-исправно: негативные тесты не доказывают отсутствие дефектов, а воспроизводят/опрокидывают гарантии по реальному пути.

## Покрытие

26 check_id (все 24 PL003 + own QA-NOV-01 + SEC-NOV-01), статусы по `failure_map.json` (счёт пересчитан в Python, не вручную):

| Статус | Кол-во | Чеки |
|---|---|---|
| EXECUTED_NEGATIVE | 18 | CHK-A2-01…07, CP-PL-01, 05, 06, 07, 08, 09, 10, 14, 15, 16, QA-NOV-01 |
| GAP | 4 | CP-PL-11, 12, 13, 17 |
| NOT_TESTED | 4 | CP-PL-02, 03, 04, SEC-NOV-01 |

Receipts: 52 refs (28 runtime receipt-файлов, два seed), каждый с SHA256; run-манифесты 36; manifests_index 36. ack→observation→attempt binding и foreign-field-скан по recovery DB — 0 нарушений. B-контроль после негативов воспроизведён.

## Находки (эскап-хэтч)

Все — **prior refs**, referenced через `debt_ref`, НЕ дублируются и НЕ закрываются. Новых debt ID НЕТ, новых продуктивных дефектов в этой фазе не обнаружено.

- **TD-DOM-12** (CP-PL-05): `UPDATE branch_heads SET revision=0` принят (rowcount=1), остальные write-формы IMMUTABLE-refused.
- **TD-DOM-15 / TD-DOM-18** (CP-PL-06): stale/archive/convergence-поведение на двух seed; retained, не re-registered.
- **TD-DOM-19** (CHK-A2-01/02/03/04; prior SEC003-F-01): из AA-поверхностей видны out-of-scope AB-метаданные/paths; references carry foreign broken_event_id UUID в отказном пути.
- **TD-DOM-20** (CHK-A2-05/06): raw AttributeError на own-key TASK list/scalar/null при «absent != invalid» поведении; TASK:[] fail-stop воспроизведён свежими процессами.
- **TD-DOM-21** (CHK-A2-07): shared mutable pointer; tamper-копия отклонена по хэшу, run-специфичные create-only манифесты использованы.
- **TD-DOM-07** (CP-PL-14): третья ветка ZZ отсутствует (branch allocator), GAP — не самовольное расширение WORK.
- **TD-DOM-06/08** (CP-PL-14): OS-изоляция/live-auth не следуют из simulation (логическая граница harness), reference не закрыты.

## Пропуски (omissions) и ограничения (limitations)

- CP-PL-10 **busy** и **read-only** подкейсы честно **NOT_TESTED** (WAL снимает lock для читателей; store.read_only не enforced ФС-состояние) — не PASS.
- CP-PL-02/03/04 NOT_TESTED QA (prior SEC003 evidence стоит).
- CP-PL-12 REPLACE-проба не засчитана из-за SQL-ошибки probe («no such column: x»).
- CP-PL-01/14/15/16 PARTIAL: MCP unknown-principal как отдельный случай, полный internal proof/YAML-штамп, третья ветка ZZ, noninterference.
- Timing — только bounded exploratory (12 randomized paired AA/seed), timing-claims не делаются.
- Нет претензии на полное Cartesian-покрытие / acceptance / all-channel noninterference; строгий OS-sandbox / external checkpoint / live auth / Git / OMH не следуют из simulation.

## Replay / recovery

- code digest совпадёт (715b1ca8…ba3) при перегенерации failure_map/scenario_manifest/manifests_index — builder СТОП-нет при дрейфе.
- verify_final.py (отдельный read-only процесс) валидирует все статусы/IDs/paths/hash/ack-bindings и присутствие обоих финальных файлов; успешный driver exit — не verdict.
- Два seed (4201/4211) меняют начальные данные и порядок; первый неудачный/BARRIER_TIMEOUT run сохранён как evidence, не удалён.
- Неудачные/частичные подкейсы (busy, read-only, REPLACE) зафиксированы как NOT_TESTED/незасчитанные, а не как PASS.

## Дополнительно

Либо completed=true при полном материале. New debt ids: `[]`. `debt_status_changes: []`. `continuation_required=false`. Вердикт пишет сам исполнитель; parent после read-back точного target и validation диспатчит следующее звено.