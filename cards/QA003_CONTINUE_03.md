# QA003 — CONTINUATION 03 (только финальные артефакты; весь материал уже на диске)

Роль прежняя: QA003 failure-tester. Полный контракт — cards/QA003_FAILURE_TESTER.md; остаток 01/02 — cards/QA003_CONTINUE_01.md, QA003_CONTINUE_02.md. Всё содержание уже записано и проверено; ЭТА карта — только создание двух финальных файлов и финальной validation, не пересборка.

## Подтверждённое состояние (проверить самому, не перезаписывать)
P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.
runtime/QA003/ содержит (validated в CONT-02):
- b-контроль разобран: analyze_b_control.py → analysis/b_control_analysis.json; вердикт PROBE_FIXTURE_BUG_NOT_LEAK; sc-controls.json перегенерированы на 4201 и 4211 → b_control_preserved=true, 0 canaries/id в AA; старые версии сохранены как sc-controls.v1.json (WORM; notes честно помечены).
- failure_map.json (26 rows: 24 PL003 + QA-NOV-01 + SEC-NOV-01; status_vocabulary; counts EXECUTED_NEGATIVE/GAP/NOT_TESTED), scenario_manifest.json (entries 26, status_by_check_count 26), manifests_index.json (36 run-манифестов; 3 create-only с file-hash), env_fingerprint.json.
- verify_final.py — вердиктор отдельным процессом; при CONT-02 имел 3 падения: receipt_identity (исправлено→declares_check), отсутствие финальных артефактов (это и закрывается), и содержимое failure_map/scenario_manifest после перегенерации.
- НЕТ финалов: artifacts/QA003_FAILURE_TESTER.json, reports/QA003_FAILURE_TESTER.md. validation.json существует, но метит passed=false от прошлого прогона.

## Точный остаток (только это, по порядку)
1. Проверить, не появились ли финалы (если появились — стоп и проверь их содержимое; скорее всего нет).
2. Собрать artifacts/QA003_FAILURE_TESTER.json по контракту карты: role/task/status/verdict/completion_state; product_acceptance=false, is_approval=false; source+input+env fingerprints (env_fingerprint.json, code digest 715b1ca8…ba3 пересчитать; дрейф → СТОП/rebind); scenario_manifest_ref + immutable evidence refs+sha256; checked_suspicions (включая раздел-0: «sentinel_leaked_to_target» опровергнуто — oracle-ключ fixture digest 32a4ec1e…; «b_control_preserved=false» — PROBE_FIXTURE_BUG; TD19/prior refs воспроизведены); findings: НЕ duplicimage — только prior refs TD12/15/18/19/20/21/07 с debt_ref, новых debt ID нет; per_check для всех 26 (EXECUTED_NEGATIVE 18 / GAP 4 / NOT_TESTED 4 — статусы по failure_map, не выдумывать); coverage/omissions/limitations (CP-PL-10 busy/read-only подкейсы НЕ воспроизведены — WAL допускает читателей, store.read_only не enforced → NOT_TESTED честно; REPLACE-проба CP-PL-05 не засчитана из-за SQL-ошибки probe); debt_status_changes=[]; remaining=[]; verified_by_commands; completion_state=completed.
3. Написать reports/QA003_FAILURE_TESTER.md: раздел 0 «подозревал→проверил→оказалось», verdict REQUEST_CHANGES (никогда SAFE/secure), coverage/omissions/limitations, findings prior refs, replay/recovery summary, явно: новых продуктивных дефектов не обнаружено, новых debt ID нет.
4. Финальный прогон verify_final.py → validation.json с passed=true (после правок builder'а declares_check/declaring_receipts, если перегенерация failure_map/scenario_manifest нужна — сделай; содержимое уже правильное: 26/26).
5. Проверить наличие всех трёх файлов (artifacts, reports, validation passed=true) — это критерий completed. Ничего другого не трогать.

## Границы (как в основной карте)
Запись ТОЛЬКО artifacts/QA003_FAILURE_TESTER.json, reports/QA003_FAILURE_TESTER.md, runtime/QA003/**. Продукт/tests/PL003/SEC003/tech_debt read-only. Без Git/install/network/paid/субагентов/расширения grants/OMH delta. PY=E:/opencode_harness_portable/.venv/Scripts/python.exe, CWD=P. При лимите — continuation.json той же роли с точным остатком; parent финал не дописывает. Финальный вердикт пишет сам исполнитель.