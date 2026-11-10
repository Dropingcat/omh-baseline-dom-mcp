# SEC003 — CONTINUATION 03 (только финализация; прогоны уже записаны)

Роль прежняя: SEC003 специалист по безопасности. Полный контракт — cards/SEC003_SECURITY.md; статус/остаток 02 — cards/SEC003_CONTINUE_02.md. Харнесс починен и прогоны уже записаны; эта карта НЕ про новый анализ и не переписывание харнесса.

## Подтверждённое состояние на диске (проверить самому, не перезаписывать вслепую)
P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.
- Харнесс (починен 02): launch.py, raw_mcp.py, oracle.py, engine.py, scenarios.py, build_maps.py, digest_check.py, manifest_run.py, verify.py в runtime/SEC003/.
- Прогоны с evidence: run-3101-85478e2b/ (первый, evidence; hp-04 с прежним багом), run-3101-f7fc7e4b/ и run-3109-31020cee/ (канонические). Оба канонических: SEED*_EXIT=0, progress.json 13/13 done, statuses: CHK-A2-01..04, SEC-NOV-01, CP-PL-01,02,03,04,07,14,15,16 → EXECUTED_NEGATIVE; CP-PL-11,12,13,17 → GAP.
- TD-DOM-19 воспроизведён (read_snapshot.chain_head/revisions/trace.chain.events видимы AA-only при fixed AA), B-контроль и AA positive control в receipts. Код-диджест 715b1ca… совпал (дрейфа нет).
- failure_map.json (24 rows) и scenario_manifest.json уже записаны.

## Точный остаток (только это)
1. manifest_run.py для run-3101-f7fc7e4b и run-3109-31020cee (create-only per-run manifest.json, точный byte hash вынести в evidence_ref вне manifest; «latest» только навигация).
2. verify.py последним → runtime/SEC003/validation.json (statuses/IDs/paths/hashes/evidence refs + присутствие отчёта; реальный exit).
3. Финальные артефакты:
   - artifacts/SEC003_SECURITY.json (role/task/status/verdict/completion_state/completion; product_acceptance=false, is_approval=false; source/input/env fingerprints; scenario_manifest_ref + immutable evidence refs с hashes; section-0 «подозревал PYTHONPATH → опровергнута (parents[2]/importlib.util — подтверждены)»; findings: ТОЛЬКО TD19 reproduction с debt_ref (не дублировать/не закрывать TD19/20/21); per_check для всех 24 (QA-переданные → честно NOT_TESTED); coverage/omissions/limitations/not_checked/remaining/continuation_required/verified_by_commands; debt_status_changes=[]).
   - reports/SEC003_SECURITY.md (раздел 0, verdict REQUEST_CHANGES — НЕ SAFE, coverage/omissions, findings, собственная section0).
4. completion_state=completed только когда эти файлы и validation.json существуют и читаются; до этого честно PARTIAL/in_progress.

## Границы (как в основной карте)
Запись ТОЛЬКО artifacts/SEC003_SECURITY.json, reports/SEC003_SECURITY.md, runtime/SEC003/**. Продукт/tests/PL003/tech_debt/другое read-only. PY=E:/opencode_harness_portable/.venv/Scripts/python.exe, CWD=P, чистый env (без PYTHONPATH-тени хоста; '-B'). Без Git/install/network/paid/субагентов/расширения grants/OMH delta/правки харнесса на мелкое. Не перезапускать полностью без причины. При лимите — continuation.json той же роли с точным остатком; parent финал не дописывает. Финальный вердикт пишет сам исполнитель.