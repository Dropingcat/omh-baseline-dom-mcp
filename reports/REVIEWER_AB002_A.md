# RV002-A — независимая приёмка AB002-A

**APPROVE только дельты A1…A9, SIMULATION. Блокирующих продуктовых находок нет.**
`completion_state=completed`. Это не приёмка всей системы, не разрешение закрывать OMH-задачу и не замена следующего независимого аудита.

Основной вердикт: `artifacts/REVIEWER_AB002_A.json`.

## Проверенный результат

- Собственный полный stdio MCP прогон: `runtime/AB002_A/matrix-93345211`, **26 PASS / 0 FAIL**, runner PID 6484, exit0. Замороженный manifest: `runtime/RV002_A/frozen-manifest.json`.
- **118** терминальных MCP process receipts: **112 exit0**, **6 намеренных exit71**. Проверены реальные смерти/новые PID, commit/rename/send, writer lock и параллельное восстановление.
- Четыре дополнительно спроектированные проверяющим последовательности: **4 PASS**, включая две разные порчи populated/resumed копий. Сценарии и оракулы собственные; общий raw stdio helper и fault launcher использованы только как транспорт/инъекция.
- **25** собственных негативных SQL-проб с конкретным trigger code/diagnostic и точным сравнением физических байтов. Отдельно повторены runner-пробы: **88 immutable**, **23 binding**.
- Независимый физический повторный read-back **всех 26 своих конечных состояний**, проверка **48 ack** прямыми read-only SQL joins и текущими байтами цели/экспорта. Также физически перепроверены **26 worker final snapshots**.
- Все **34** worker-declared source/tests/README fingerprints совпали. Собственные **42** before/after fingerprints исходников/tests/первичных входов неизменны. Продукт, тесты, документы и карты не редактировались.
- Повторный адресный процессный контроль: **0** Python mockup launcher/lock/server. Своих дочерних процессов не оставлено.

Верификатор: `runtime/RV002_A/verify_physical.py`, PID 12300, exit0; сводка — `runtime/RV002_A/verification-summary.json`. Parent receipt не использовался как независимое доказательство. Unit suite и demo повторно не запускались: число worker unit-тестов не считается приёмкой.

## Собственные вариации и физические факты

### RV-LIAR — лживый attach на уже заполненной цели

Старт: AA rev1 и AB rev1 уже приняты и доставлены; затем добавлен AB rev2 с CRLF, combining Unicode и supplementary character в исходном теле. Новая OMH-запись ещё отсутствует.

Два новых liar subprocess по очереди выполняют resume → sync → trace. Оба attach возвращают ack, но read-only SQL показывает **ноль ack для нового OMH intent**, две unmatched observation с `evidence=null` и `port_reported=ack`. Старые физические байты цели не меняются; trace содержит `SYNC_PENDING` и `ready_for_owner_review=false`.

После смены на доступный порт — **новый PID**, resume → reconcile → повтор sync. В цели три корректные записи на три принятых tx; на новый tx — ровно одна запись и один фактический write. Все шесть итоговых ack связаны с точными observation/attempt/outbox; YAML проверен по фактическим байтам. Старые facts/snapshots сохранены.

Evidence: `runtime/RV002_A/liar-resumed-populated/{result.json,populated-before.json,liar-before-recovery.json,final-physical.json,linked-readonly-SQL.json}` и сырые frames/process receipts рядом.

### RV-CORRUPT-envelope и RV-CORRUPT-hash

Отдельные disposable-копии уже доставленной AA1/AB2 БД с существующими target/export файлами; добавлен pending AA2, перед порчей реально выполнен resume. Повреждён **последний** event, а не первый, как в штатном runner:

- удалён `value`, hash пересчитан: точный отказ `EVENT_SHAPE_INVALID`;
- испорчен hash: точный отказ `EVENT_HASH_MISMATCH`.

Для каждой порчи: query/trace/resume/export/sync/sync_status, обе ветки AA/AB, две новые сессии. Всюду структурированный `CHAIN_BROKEN`, точный `broken_at_seq`, NOT_READY. БД, target, YAML/tmp и write-log **байт-в-байт совпадают** до и после вызовов. Новая доставка/экспорт не возникает. Repair не выполнялся и не объявлен успешным.

Evidence: `runtime/RV002_A/corrupt-resumed-{envelope,hash}/{result.json,after-injection.json,after-refusals.json}` и raw MCP/process receipts.

### RV-BINDING — конкретные binding/immutable отказы

Старт: AB rev1 pending. Проверены ack без observation, чужие intent/tx/digest/target в attempts, затем реальный liar создаёт unmatched observation. До восстановления проверены ack по unmatched/foreign значениям без конфликта с уже существующим ack. После reconcile — REPLACE/IGNORE/UPSERT для attempts/observations/acks/claims/snapshots.

Итог: **25** точных trigger refusals, code1811; ожидаемые `ACK_REQUIRES_OBSERVED`, `DELIVERY_BINDING`, `IMMUTABLE`. После каждого rollback совпадают SQL rows, SHA256 файла БД и точные байты всех физических целей. Через MCP автор не может вызвать sync/назначить ack/подставить role.

Evidence: `runtime/RV002_A/negative-binding-byteexact-v2/{result.json,probes.json,probe-*-before.json,probe-*-after.json,linked-readonly-SQL.json}`.

## Соответствие A1…A9

| Инвариант | Независимо установленный факт |
|---|---|
| A1 | Лживый port ack без target record не создаёт ack; SQL и trace подтверждают pending, новое восстановление даёт одну запись. |
| A2 | Долговечный attempt предшествует observation; ack привязан к observed и точному outbox. Прямые SQL joins и негативы проверены. |
| A3 | Реальные exit71/reopen/reconcile и параллельное восстановление без дубля; внешний эффект вне SQLite write transaction. |
| A4 | Model-facing delivery отсутствует, caller-supplied state/role не принимается; fixture boundary не объявлена auth. |
| A5 | Append-only и duplicate-key guards действуют для REPLACE/IGNORE/UPSERT; точные binding отказы и bytes unchanged. |
| A6 | Оба повреждения fail-closed на шести поверхностях; проверенный read snapshot удерживается до результата/effect, observation фиксирует read_at/head/revisions. |
| A7 | Реальные busy/corrupt/read-only/unavailable различены; точные extended code/name, без payload/OS-path в доменной ошибке. |
| A8 | Exact body/provenance/origin/snapshot сохраняются; trace не вызывает owner close. Глобальные смысловые критерии не принимаются этим выводом. |
| A9 | Existing DB повторно используется; legacy явно требует init, additive installation сохраняет историю; перечисленная incompatible layout получает MIGRATION_REQUIRED без reset. |

Точные source lines и evidence на каждый пункт — `per_invariant` JSON. Все PASS ограничены заявленными комбинациями и simulation boundary, не полным декартовым покрытием.

## Проверка оракулов и собственные неудачные команды

C1 E10: прочитаны код и историческая diagnosis. `CHAIN_INTEGRITY/SQLITE_CONSTRAINT_TRIGGER` действительно сопровождается exact before==after. В текущем runner это разрешено только для старого event replay, чей previous_hash не продолжает current head; произвольное исключение не считается PASS. Собственный полный повтор подтвердил 88 строгих проб.

C2 unavailable: oracle требует точную допустимую пару `SQLITE_CANTOPEN` либо `SQLITE_CANTOPEN_ISDIR`, а не любой SQLite error. Resource regression удерживает реальное соединение, чтобы GC не скрывал незакрытый handle. В просмотренных acceptance paths нет skip/xfail/broad-except success. Полного исторического diff-аудита не заявляю.

Первый собственный driver завершился **exit1** после трёх PASS: четвёртая проба reviewer ожидала binding error, но reused observed UNIQUE key уже был acked и корректно получала `IMMUTABLE`. Это **не продуктовая находка**. Сохранены v1 script/summary/frames; v2 создаёт реальное unmatched observation до recovery, устраняет collision confound, не расширяет допустимые исключения и проходит 25 точных проб с exit0. Частичный v1 не объявлен полным PASS.

Первый inline process-check был невалиден из-за bash dollar expansion и decoding; его номинальный exit0 не принят. Отдельный script со строгой обработкой PowerShell успешно прочитал пустой список процессов. Сырые failed/success receipts сохранены.

## Находки, границы, остаток

**Новых product critical/major/minor findings в проверенной дельте нет.** `findings=[]`.

Предложение `RV002-A-DEBT-01` (minor, будущий D): ссылка отчёта должна указывать immutable run-specific manifest, а не shared mutable manifest. При повторе штатный runner перезаписывает global manifest; reviewer сохранил frozen copy и читает worker run-specific manifest. Долг записан только в собственном JSON: изменение глобального реестра вне write scope.

Явно остаются OPEN/NOT_TESTED:

- E11/S4 и новая revalidation policy, UD-01…06;
- B/C/D: выводимость head, branch/master semantics, baseline/stale/convergence и offline export provenance;
- LIVE OMH/Git/issuer/auth, OS sandbox, external checkpoint, malicious file-owner/in-process/lying read-back;
- refinement tree — deferred_to_researcher;
- все возможные S×E комбинации, production-scale, другие OS/SDK и все варианты несовместимой схемы;
- independent unit/demo rerun и полный исторический diff.

Ack — исторический факт в read_at, не вечная доступность. Локальная идемпотентность не universal exactly-once. Read snapshot может дать concurrent writer bounded busy. Источники дополнительных completion-only input hashes честно отделены от собственных before/after fingerprints.

**Следующий шаг — последовательный AU002-A auditor с новыми начальными условиями. Reviewer его не запускал.** Затем analyst/researcher/следующий worker по фабричной цепочке. Продолжение RV002-A не требуется.

### Находки (эскап-хэтч)

- L1: собственные ошибки oracle/process-check сохранены и устранены только в reviewer runtime; продукт не менялся.
- L2: известный остаток B/C/D и production boundary не закрыт; предложен D evidence debt.
- L3: новых нет.
