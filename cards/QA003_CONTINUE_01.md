# QA003 — CONTINUATION 01 (лимит итераций; 3 сценария выполнены, остаток и финал — здесь)

Роль прежняя: QA003 failure-tester. Полный контракт — cards/QA003_FAILURE_TESTER.md, остаётся в силе. Продолжение той же роли на polza, не пересоздание. Predecessor SEC003 принят (artifacts/SEC003_SECURITY.json completed, verdict REQUEST_CHANGES); findings SEC003-F-01 (TD19) и прочие уже в SEC003; QA их НЕ дублирует.

## Состояние на диске (проверить самому, не перезаписывать)
P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp, runtime/QA003/:
- harness: launcher.py, mcp_client.py, readback.py, generator.py, scenarios.py; first_artifact.json (PARTIAL).
- выполнено на seed 4201, receipts в current-run/: sc-lp-a2-05.json (CHK-A2-05/LP-A2-05; own-key TASK list→TD20 prior ref, foreign sentinel сохраняются, missing-file=valid empty), sc-lp-a2-06.json (CHK-A2-06/LP-A2-06; TASK:[] crash двумя retry (TD20 prior), crash после after_external_send: exit71 attempts=1 obs=0 acks=0 no_ack_before_recovery=True, после recovery SYNCED ack_bound_on_recovery), sc-hp-pl-05.json (CP-PL-05; UPDATE/DELETE/INSERT/upsert → IMMUTABLE/SQLITE_CONSTRAINT; UPDATE branch_heads revision=0 ПРИНЯТ — TD12 prior ref; REPLACE-проба НЕ засчитана: "no such column: x").
- raw frames: raw-lp-a2-05*.jsonl, raw-lp-a2-06*.jsonl и др. run-4201-<8>/ — per-run evidence (progress.json показывают stage 'start', но receipts/raw frames реальные — не трактовать как незаполненные; сверяться с receipts+raw).
- НЕТ: validation.json, continuation.json, artifacts/QA003_FAILURE_TESTER.json, reports/QA003_FAILURE_TESTER.md.

## Точный остаток (в порядке)
1. SC-LP-A2-07 / CHK-A2-07 — malformed shapes/commit/rename (не повторять done; если код-диджест изменился — СТОП и rebind через parent; сейчас 715b1ca8…, проверить пересчётом).
2. SC-HP-PL-06 / CP-PL-06 — concurrency/barrier overlap (real PIDs, recovery).
3. SC-HP-PL-08 / CP-PL-08 — storage/recovery/retention.
4. SC-HP-PL-09 / CP-PL-09 — send/observation/ack binding, restart между send и observation c foreign sentinel.
5. SC-HP-PL-10 / CP-PL-10 — recovery/readback, foreign fields scan на каждом recovery.
6. QA-NOV-01 — собственная risk-комбинация: malformed own tx + foreign sentinel + restart между send и observation (по карте «минимум одну»).
7. QB-TD19-RECHECK — recheck с изменённым порядком и условиями, prior ref (не новый finding).
8. SC-H-LINK / CP-PL-17 — tools/list + AST: если link-sensing поверхности нет → GAP/NOT_IMPLEMENTED со схемными доказательствами (не PASS, не NOT_APPLICABLE).
9. Повтор ключевых сценариев на seed 4211 (второй seed меняет initial data и order; не повторять тот же synthetic log).
10. Финал: failure_map.json + scenario_manifest.json в runtime/QA003 (все check_id со status: EXECUTED_NEGATIVE/CONTROL_FAILED/FINDING/GAP/NOT_TESTED), per-run create-only manifest.json с byte-hash в evidence_refs вне manifest, verification (readback отдельным verifier, сводка statuses/IDs/paths/hash/ack bindings), и собственные artifacts/QA003_FAILURE_TESTER.json + reports/QA003_FAILURE_TESTER.md (раздел 0 подозревал→проверил→оказалось; verdict REQUEST_CHANGES/BLOCK/NO_VIOLATION_OBSERVED_IN_SCOPE — НИКОГДА SAFE/secure; per_check все 24+; findings: ID+severity+debt_ref — TD12/19/20 как prior refs, не дублировать/не закрывать; debt_status_changes=[]; coverage/omissions/limitations/remaining/verified_by_commands).

## Границы (как в основной карте)
Запись ТОЛЬКО artifacts/QA003_FAILURE_TESTER.json, reports/QA003_FAILURE_TESTER.md, runtime/QA003/**. Продукт/tests/PL003/SEC003/tech_debt read-only. PY=E:/opencode_harness_portable/.venv/Scripts/python.exe, CWD=P. raw stdio MCP, real serve, не глобальный ab002_e2e. Не более двух детей; RPC≤25s, child≤90s, role wall≤1800s, payload≤64KiB, ≤16 claims/branch, DB≤16MiB, evidence≤128MiB. Без Git/install/network/paid/субагентов/расширения grants (в т.ч. enforcement не ослаблять)/OMH delta. Не уменьшать покрытие ради completed; не выдавать partial за PASS; первый, неудачный и прерванный run НЕ удалять (WORM). При лимите — continuation.json той же роли с точным остатком; parent финал не дописывает. Финальный вердикт пишет сам исполнитель.