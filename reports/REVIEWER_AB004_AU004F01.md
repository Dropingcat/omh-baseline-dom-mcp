# REVIEWER RV005 — AB004 / AU004-F-01 на версии 1ead2d45…

**Решение reviewer: APPROVE** (рекомендация; `product_acceptance=false`, `is_approval=false`, долг TD19/AU004-F-01 **не закрыт** — приёмка за OMH/заказчиком).
Условие APPROVE: два признанных наблюдения (O1 staleness, O2 X2) остаются ОТКРЫТЫМИ и требуют решения принимающего / отдельных долгов (предлагаю, не регистрирую).

## 0. Подозревал → проверил → оказалось

| Подозревал | Проверил (своим прогоном) | Оказалось |
|---|---|---|
| Worker, как RV004, проверил только перечисленные поля; в схеме есть ещё пути с ключами/именами чужих веток | Программный обход: все 32 записи `public_dto.RECORDS`, 12 инструментов, 10 видов event value, YAML export → 186 строк «запись.поле» с вердиктом и **assert полноты** (`runtime/RV005/field_inventory.json`); дифф-проекция синтетического экземпляра каждой записи с bmap-ключами {AA,AB,ZZ} при scope={AA} | Карты по ветке — ровно 3 (`Claim.dependencies`, `Provenance.dependencies`, `ReadSnapshot.revisions`) = inventory worker; 0 чужих ключей после проекции; `scope=None` → `SCOPE_REQUIRED` на всех записях с bmap. Но inventory worker — только карты; **значения-имена веток шире**, чем перечислено (см. O2) |
| Фикстуры с пустыми deps снова скроют дыру | Populated: AA deps{AA,AB}, AA deps{AB}, AB deps{AA,AB}, AB deps{AB}, AB-клайм расшарен в AA, AA-клайм расшарен в AB, события в обеих ветках (comment/link/property/conflict/resolve/replacement/archive/converge), в т.ч. на расшаренном и на чужом клайме; owner exclude AA→AB и AB→AA | 6 клаймов с непустыми deps на сид; во всех 18 reader-запусках `dependencies` каждого клайма и каждого события == SQL-карта, отфильтрованная грантом |
| Свип worker мог не «видеть» дефект | Контроль: тот же свип на pre-fix коде (precopy 08aa9a9b) на той же БД | pre-fix: **56 расхождений deps** в 8 снимках (4 пути); новый код: 0. Свип чувствителен. Позитивный контроль: union видит 163 из 218 не-расшаренных канареек (остальные 55 — envelope reason/idempotency key, наружу не проецируются) |
| Утечка в байтах не-JSON каналов: YAML, stderr, wire-кадры, base64 | Канарейки (711 за 3 фикстуры) + id/хеши другой ветки из SQL (3727 игл raw+base64 ×3 выравнивания + декодирование всех b64-строк) по text+structuredContent 1086 вызовов, recv-кадрам, stderr, `exports/*.yaml`, `omh-target.json`: ~7.2 МБ | **0 неожиданных попаданий.** Единственные попадания — `origin_version` клайма, расшаренного в ветку читателя (атрибут видимой записи, ожидаемо) |
| Порча цепочки AB выдаёт локатор или отличает ветку | 4 случая (AB/AA событие × invalid-utf8/wrong-hash) × 2 PID × 7 инструментов, AA-only | 56/56 `CHAIN_BROKEN` с ровно 5 ключами; 0 локаторов в байтах и stderr; БД побайтно не менялась; текст ответа **идентичен** для порчи AB и AA (ветку порчи не отличить) |
| Допуск во время чтения даёт промежуточный leak/ошибку | Читатель AA-only в цикле, пока union пишет 10 допусков (heads AA 2→7, AB 1→6) | 176 чтений, ревизии 2,3,5,6,7 увидены, 0 ошибок, 0 попаданий, 0 расхождений deps. (Первая попытка не пересекалась — читатель увидел одну ревизию — **отброшена и переделана**) |
| Внутренняя логика изменилась | Union: ответы старого и нового кода на одной БД; SQL-хеши фактов до/после | Union идентичен (кроме случайных candidate_id/observed_id); таблицы `claim_snapshots/events/claims/branch_heads/transactions` не менялись ни в одном из 18 запусков; AA-only отличается от pre-fix только deps/read_snapshot/хеш YAML |
| «Staleness раскрывает больше, чем говорит worker» | Свой стенд + код | Подтверждено как узкий канал существования (O1), без имени ветки/ревизии |
| X2 уже ограничен `origin_branch` | Обход схемы + exclude-вариант | **Шире**: ещё `ClaimItem.applicability` (в т.ч. внутри `History.provenance.value.item`), `Trace.origins`, `Residual.claim_origins`, `excluded_branches` (owner-exclude: AA-only видит `['AB']`) |

## 1. Digest и целостность
- Независимый пересчёт (SEC003): `1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf`, 16 файлов — **совпал**. Эталон `08aa9a9b…` пересчитан из `precopy` и совпал с `code_digest_before.json`.
- Изменены ровно `admission.py`, `public_dto.py`, `server.py`; 13 остальных байт-в-байт равны. Тела изменений: передача `scope=context.branches` + `bmap` + YAML из проекции — scope не расширен (те же 12 инструментов/SIGNATURE).
- `tests/` — 18/18 файлов равны хешам baseline (`WORKER_AB002_A.json`); mtime старше правок кода → oracle не ослаблен.
- Manifest worker: 1714 записей, 0 расхождений. В `runtime/AB004` сейчас 1721 файл против 1708 в манифесте: 13 лишних = 4 `manifest.json` (сам и 3 вложенных в `regress/*`) + 9 `.pyc` в `precopy/…/__pycache__` (мои прогоны шли с `-B`). Содержимое evidence не затронуто.
- pytest 63/1 мной **не перезапускался** (сьют пишет `runtime/tmp` вне разрешённой зоны записи); принимаю повтор родителя.

## 2. Перечень полей (свод)
186 строк: `FILTERED_BY_GRANT` 9 (3 bmap + их композиты read_snapshot) · `NO_FOREIGN_BY_CONSTRUCTION` 39 · `FIXED_ENUM_OR_CALLER_OWN` 78 · `USER_DATA_OF_VISIBLE_RECORDS` 42 · `OBSERVED_X2` 13 · `OBSERVED_STALE` 5 · ОТКРЫТО-кандидатов в finding: **0**.
Ключевые «по построению»: `applicable_branches` (событие applicability разрешено только на свою ветку, `admission.py:133`), `supersedes` (только события той же ветки), `IntentStatus.*` (outbox запрошенной ветки), внутренний stamp (chain_head, все ревизии, port_reported) наружу не выходит — только `ReadSnapshot` по гранту. `Claim.properties`: свойство, записанное в AB на расшаренный клайм, AA-only **не видит** (проверено канарейкой).

## 3. Свип (сводка)
3 фикстуры (seeds 61703, 28411, 90517+exclude) × 6 читателей (AA-only, AB-only, union на AA и AB, грант `AA,ZZ`, пустой грант) × все 12 инструментов обеими ролями + пробы чужих веток/кандидатов/payload. Попадания: 0 неожиданных. Пустой грант → SCOPE_DENIED везде; `AA,ZZ` ≡ AA. Доставка: observations == acks == attempts (26/28/30), дублей 0, каждый внутренний stamp содержит chain_head + ревизии {AA,AB} + port_reported + read_at.

## 4. Негативы на своих seeds и атаки
Seeds: 61703, 28411, 90517, 33871, 41907 (не из карты). (a)–(g) воспроизведены (см. JSON). Свои атаки: лишние аргументы `branches/scope/grant/role` → `INVALID_ARGUMENTS`; ветки `AA,AB`, `AB␠`, `ab`, `A*`, `""`, `ZZ`, `AB/../AA`, NUL → единообразный `SCOPE_DENIED`; подмена ключей хранимой карты (`ZZ`, `CNRYKEY…`, `""`) → в выводе и YAML только `AA`; `scope=str/[]/generator/None` in-process: str/[] → пусто (fail-closed), None → `SCOPE_REQUIRED` на всех 5 инструментах; нестроковый ключ → `INVALID_KEY`.

## 5. Наблюдения (оценка)
**O1 Staleness-канал.** Клайм с публичными `dependencies: {}` получает `STALE_CHECK`, `claim_refs` сжимается 2→1, blockers `CRITERIA_NOT_CURRENT`. Имя ветки и ревизия не раскрыты, но **факт** скрытой зависимости и **момент** продвижения чужой ветки выводимы. Серьёзность низкая. По правилу заказчика («чужое убирается, не маскируется») — частичное нарушение следствием. Предлагаю отдельный долг-кандидат или явное принятие; AB004 не расширять. Оговорка: мой стенд уже был stale до продвижения AB (событие converge в AB подняло head) — чистый before/after в сценарии worker b.
**O2 X2 (имена веток значениями).** `origin_branch`/`ClaimItem.applicability`/`Trace.origins`/`Residual.claim_origins`/`excluded_branches` показывают `AB` читателю AA-only для расшаренного клайма. Только имена (две фиксированные), без содержимого; `projections.py` документирует маркер как обязательный. Серьёзность низкая–средняя; формально противоречит правилу, поэтому нужно решение владельца + отдельный долг. Worker перечислил не все поля (нет `ClaimItem.applicability`, `Trace.origins`, `Residual.claim_origins`).
**O3 (инфо).** `delivery.confirmed()` для YAML_EXPORT сверяет только branch/revision → ack, полученный AA-only sync, закрепляет отфильтрованный YAML. Полнота, не утечка; по коду, перекрёстно не запускалось.

## 6. Что не сделано (честно)
pytest не перезапускался; чистый before/after staleness — только у worker; `dom_query` на ветку ZZ при гранте `AA,ZZ` не пробовался; перекрёстная доставка YAML не запускалась; CP-PL-05 REPLACE и CP-PL-10 busy/read-only — NOT_TESTED (не блокируют).

## 7. Артефакты
`artifacts/REVIEWER_AB004_AU004F01.json`, этот отчёт, `runtime/RV005/**` (lib/, step1/, step2/, sweep/{61703,28411,x90517}, neg/, final_checks.json, field_inventory.json, oldcode/ — копия pre-fix для контроля, MASTER_MANIFEST.json, SOURCE_LEDGER.json). Воспроизведение: `lib/sweep.py SEED [--exclude AA:AB,AB:AA --name X]`, `lib/control.py SEED`, `lib/neg.py`, `lib/final_checks.py`, `lib/inventory.py`, `lib/build_artifact.py` (PY=venv, чистый env).
