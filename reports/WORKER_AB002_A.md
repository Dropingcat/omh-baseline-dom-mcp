# AB002-A / C2 — handoff разработчика

**PASS в пределах SIMULATION A1…A9; completion_state=completed; is_approval=false.**
Это не независимая приёмка и не готовность всей системы. LIVE OMH=NOT_TESTED.
Продолжение сохранённого C1, без сборки с нуля. REQUIREMENTS включает новое дерево
immutable уточнений; оно deferred_to_researcher, в A не реализовано. UD-01…06 OPEN.

## Наблюдаемый результат

- Полный новый MCP E2E: **26 PASS / 0 FAIL / 0 NOT_TESTED** среди исполненных вариантов.
  `runtime/AB002_A/matrix-61c246ab/manifest.json` — сырой завершённый результат;
  `runtime/AB002_A/e2e_manifest.json` — дополненный provenance/omissions/read-back ledger.
- E10: **88 SQL-проб**; binding: **23**. Каждая требует конкретного trigger code/diagnostic
  и byte-exact unchanged read-back после rollback; REPLACE/IGNORE/UPSERT не исключены.
- 118 terminal MCP process receipts: 112 exit0 и 6 намеренных exit71.
  Второй lock-процесс записан отдельно: `matrix-61c246ab/E5-S1-S2-writer-lock/lock-process.json`.
- Финальные регрессии: **64 passed**, pytest exit0; demo exit0.
- Повторный физический read-back всех 26 целей/БД совпал с сохранённым final;
  каждый имеющийся ack проверен по observation и текущим физическим байтам,
  count/one-write проверены для доставленных OMH intents.
  `runtime/AB002_A/C2-target-verification.json`, exit0 в `command-C2-72b28e12/command.json`.
- Demo: `runtime/runs/run-20261107T080826Z-e0d6b908/`: 7 принятых tx,
  7 OMH-записей, 14 валидированных ack, AA=4/AB=3, 7 YAML;
  `READY` только fixture-сценария, `owner_close_called=false`.
  Target SHA256: `534522c6904a04cc91131e37691ebad3f588e607a68a60de6bf4688a098f79a0`.

## Изменения и разбор отказов

Сохранён inherited продуктовый путь durable attempt → read-back → observation → ack,
SQL binding/immutable guards, capability/scope и единый integrity gate.
C2 изменил только runner readback resource ownership и точный Windows error oracle,
добавил retained-real-connection регрессию, command capture/verifier и документацию.
Файлы: `mockup/ab002_e2e.py`, `mockup/ab002_matrix.py`,
`tests/test_ab002_runner_resources.py`, `mockup/README.md`,
`runtime/AB002_A/run_command_c2.py`, `runtime/AB002_A/verify_c2.py` и evidence/артефакты.

C1 exit1073807364 остаётся с неизвестной причиной; старые PASS не смешивались с C2.
Старый E10 CHAIN_INTEGRITY разобран по точному SQL в
`runtime/AB002_A/diagnose-E10-1f5f2df5/diagnosis.json`: replay previous_hash
не продолжает current head, отказ до duplicate guard, bytes/rows unchanged.
Строгий oracle не принимает любое исключение и не полагается на порядок триггеров.

Первый **завершённый** C2 full run `matrix-310f7c19` дал 25 PASS/1 FAIL (exit1):
WinError32 при rename до unavailable injection. SQLite context manager не закрывал
readback connection. RED: `command-C2-33bf9b4a` (exit1); явный closing исправил handle,
GREEN: `command-C2-24ea6487` (exit0). Следующая tight-проба
`command-C2-52764e14` (exit1) показала правильный STORAGE_UNAVAILABLE с extended
SQLITE_CANTOPEN_ISDIR=526. Oracle теперь требует точную допустимую пару code/name;
`command-C2-9697d1d3` и затем **вся матрица** завершились exit0.
Старые исходные evidence/logs/failed manifests не удалены. Продуктовые guards не ослаблены.

## Ledger A1…A9 (self-report)

| Инвариант | Наблюдение / evidence в matrix-61c246ab |
|---|---|
| A1 | Liar/unavailable/lost-reply leaves unconfirmed and NOT_READY; recovery reads exact intent/tx/digest/target then records linked observation. `E6-S1-liar/case.json` |
| A2 | Durable attempts precede immutable observations and matched ack; ack-first and foreign predecessors refused; protocol retained from initial implementation. `A1-A2-A5-S1-S6-binding-negatives/case.json` |
| A3 | Real exit71 before/after commit/rename/send; distinct PID restart, read-before-send and one local target write per tx; pending/ambiguous parallel reconcile. `E1-S0-before-commit/case.json` |
| A4 | Public Service.delivery refuses author/reviewer state assignment; delivery absent from MCP tools; role/branch/tool spoof refused. Fixture identity is not production auth. `E8-S3-S5-spoof-incomplete/case.json` |
| A5 | 88 exact immutable/refusal SQL probes plus 23 binding probes; update/delete/replace/ignore/upsert/secondary conflicts; rollback leaves exact rows/files/database hash. `E10-S1-immutable-all-tables/case.json` |
| A6 | Hash and missing-value envelope, AA and AA+AB, rejected by all query/trace/resume/export/sync/sync_status paths with locator and NOT_READY; no side effects. Verified snapshot read_at/head/revisions retained. `E9-S1-envelope/case.json` |
| A7 | Real writer lock, NOTADB corruption, mode=ro, inaccessible directory pathname are distinct. CANTOPEN_ISDIR=526 accepted only as exact code/name pair; restored unavailable database is byte-exact. `E5-S1-S2-writer-lock/case.json` |
| A8 | AA/AB admitted history and exact claim body/origin preserved; spoof/mismatch and immutable mutations leave bytes unchanged; demo owner_close_called=false. `E0-S0-S1-S3-AA-AB/case.json` |
| A9 | Compatible existing schema reopens; explicit additive legacy init preserves all previous facts and distrusts legacy ack; incompatible layout refuses MIGRATION_REQUIRED without reset. `A9-S1-legacy-additive/case.json` |

Все пункты — PASS только в объявленной simulation-границе. Полные ссылки и ограничения
каждого пункта: `artifacts/WORKER_AB002_A.json:per_invariant`.
TD-DOM-13/16 — candidate fixes, требуется независимое подтверждение;
TD-DOM-17 закрывается только в части integrity gate, не offline export packaging.

## Исполненные и пропущенные варианты

E0 AA/AB S0/S1/S3; E1 S0 и S1 before-commit; E2 S1 after-commit;
E3/E4 S1/S6 до/после rename; E5 S1/S2 lock; E6 unavailable, liar, lost reply,
death-after-send; E7 изменённый payload; E8 spoof/incomplete;
E9 envelope/hash на AA и AA+AB; E10 immutable; A1/A2/A5 binding;
E12 AA/AB pending и ambiguous parallel; A7 corrupt/read-only/unavailable;
A9 legacy additive и incompatible. Точный enum и initial revisions находятся в manifest.

NOT_TESTED: E11/S4/new revalidate (UD-02/06); LIVE OMH/Git/production issuer и OS sandbox;
repair corrupt DB (UD-03); полный декартов S0…S6 × E0…E12. Негативы corrupt/incompatible
сохраняют отказ, а не заявляют положительное восстановление по непринятой repair-политике.

## Команды и реальные exit

CWD: `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp`.
Python: `E:/opencode_harness_portable/.venv/Scripts/python.exe`.

```bash
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.ab002_e2e
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q --basetemp=runtime/AB002_A/pytest-final-C2
E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m mockup.demo
E:/opencode_harness_portable/.venv/Scripts/python.exe -B runtime/AB002_A/verify_c2.py
```

Фактический запуск был через `-B runtime/AB002_A/run_command_c2.py` перед аргументами
дочерней команды. E2E timeout600; exit0 — `command-C2-2ce0fd8d/command.json`;
pytest exit0 — `command-C2-35aa41c4/command.json`;
demo exit0 — `command-C2-74f515cd/command.json`;
финальный verifier exit0 — `command-C2-72b28e12/command.json`.
Все команды, PID, started/finished, stdout/stderr, RED и исторический FAIL перечислены в JSON.
При повторе pytest используйте новое basetemp, не очищайте сохранённый.
Verifier привязан к **этому** run-dir и не запускает recovery/repair.

## Отпечатки и конечный target-state

`runtime/AB002_A/fingerprints-C2.json`: SHA256 исходников/tests/README и baseline inputs.
Before/after E2E fingerprints идентичны; все Python/tests и REQUIREMENTS на финальном
read-back совпали с E2E-квитанцией. Только README дополнен после прогона.
`C2-target-verification.json` хранит новый actual read-back по каждой цели, counts и
подтверждения ack; каждый case имеет `C2-target-readback.json` с точными BLOB/file bytes.
Адресный process lookup после прогона не обнаружил mockup launcher/lock/server;
чужие Python не завершались. Старые БД/логи не сбрасывались.

## Ограничения, долги и остаток

Структурная проверка сдачи: `runtime/AB002_A/handoff-validation-C2.json`,
`runtime/AB002_A/command-C2-520523f1/command.json`, exit0: 26 specs совпали с 26
case IDs/variants, проверены 9 инвариантов, 326 referenced paths и финальные fingerprints.
Это машинная проверка артефактов разработчика, не reviewer/auditor verdict.

Нет исполнения-блокера внутри simulation A. Перед приёмкой нужны reviewer → auditor →
analyst → researcher. Самоприёмки нет. Полная система остаётся незавершённой:
B/C/D, head derivation, branch/master readiness API, stale/baseline/revalidation,
convergence и offline export provenance не закрыты этим срезом.
Fixture identity не production authentication; OS/in-process/file-owner изоляция,
внешний checkpoint и лгущий read-back не доказаны. Ack исторический в read_at,
локальная идемпотентность не universal exactly-once; read snapshot может дать writer busy.
Никаких Git-мутаций/установок/сети/live OMH/paid models/секретов.

Предложены (не зарегистрированы вне scope):
- TD-CAND-AB002-C2-RESOURCE (minor, L1): проверить deterministic close прочих raw SQLite
  helper connections и Store.initialize; исправлен именно доказанный readback leak.
- TD-CAND-AB002-C2-RUNNER (minor, L1): перенести обогащённый exact/provenance ledger
  в основной runner при последующем D; сейчас воспроизводимый C2 verifier сохранён отдельно.

Находки L1: Windows resource leak/error oracle исправлены с RED/GREEN и полным E2E.
L2: известный остаток B/C и production boundaries сохранён; L3 новых нет.
Уроки — `runtime/AB002_A/C2_lessons.md`; глобальные skills не менялись из-за write scope.

