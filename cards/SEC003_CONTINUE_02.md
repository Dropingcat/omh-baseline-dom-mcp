# SEC003 — CONTINUATION 02 (после лимита итераций; переход на polza)

Роль прежняя: SEC003 специалист по безопасности, НЕ product worker, НЕ принимающий. Полный контракт — cards/SEC003_SECURITY.md, читать целиком, остаётся в силе. Продолжение той же роли, не пересоздание и не дописывание оркестратором.

## Что произошло
deleg_89245538 (модель deepseek/deepseek-v4-flash-0731, провайдер polza) выполнил 50 api_calls и упёрся в max_iterations, успев:
- прочитать все обязательные входы и подтвердить fingerprint код-диджест 715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3 (совпал, дрейфа кода нет);
- собрать собственный харнесс в P/runtime/SEC003/: launch.py, raw_mcp.py, oracle.py, engine.py, scenarios.py, build_maps.py, smoke/* (смокtools-list 12 tools, domain-safe отказы) и first_artifact.json (PARTIAL);
- зафиксировать подтверждённый на source TD-DOM-19 (admission.integrity_gate/verify_chain, READ_SNAPSHOT chain_head/revisions на всех поверхностях) — воспроизведение, НЕ повторная регистрация;
- записать GAP-SEARCH / GAP-BRANCH-SEARCH / GAP-REFINEMENT / GAP-LINKS и пр. как GAP/NOT_IMPLEMENTED (wire и smoke подтверждают отсутствие поверхностей).

## Фактическое состояние на диске (ПРОВЕРИТЬ, не перезаписывать вслепую)
ls runtime/SEC003/:
- есть: first_artifact.json, launch.py, raw_mcp.py, oracle.py, engine.py, scenarios.py, build_maps.py, smoke/{frames-*.jsonl, frames-stderr-*.log, dom.sqlite3}.
- НЕТ run-*/ — НИ ОДНОГО. Фоновый seed-3101-прогон упал до создания run_dir: из интпы отчета, команда была `... runtime/SEC003/scenarios.py` и вывод показал:
  File "...\runtime\SEC003\scenarios.py", line 19, in <module>
      from runtime.SEC003.engine import (...)
  ModuleNotFoundError: No module named 'runtime'
  (exit 1). Последствие: харнесс есть, но НИ ОДИН сценарный прогон и ни один receipt/results/progress НЕ записан.

Первопричина импорт-сбоя в харнессе НЕ установлена с уверенностью: scenarios.py вставляет строки 16-17 sys.path.insert(0, P) где P=HERE.parents[2], но при запуске «python scenarios.py» отсюда может не хватать проекта в sys.path/PYTHONPATH (субагент отмечал, что хостовый PYTHONPATH тенит mcp/pydantic и что он «починил PYTHON* env в children», но сам прогон после этой правки видимо не перезапустил / упал иначе). Разобраться самому, что именно мешает, и выполнить прогоны.

## Точный остаток (продолжить с места падения)
1. Диагностировать и починить запуск scenarios.py (себе во runtime/SEC003, не продукт): добиться, чтобы воркер прогонял СВОЙ харнесс корректно (cwd=P, чистый PYTHONPATH на проект-venv, без теней от хостового venv; модуль runtime.SEC003.* импортируется).
2. Выполнить seed-3101: запустить run и Собрать результаты (progress.json/results.json/receipt-*.json) в созданной run-3101-*/ директории. Не пропустить положительные контроли (AA own admit; B-only B read; B-control повтор после негативов).
3. Выполнить seed-3109 тем же способом (собственная run-3109-*/, изоляция fixture).
4. build_maps.py поверх обоих результатов → runtime/SEC003/failure_map.json + scenario_manifest.json (все 24 check_id каждому status: EXECUTED_NEGATIVE/CONTROL_FAILED/FINDING/GAP/NOT_TESTED; НЕ фиктивные PL003-тесты, а состояния исполнения этой роли).
5. Per-run create-only manifest.json с точными byte-хашами (create-only, hash вынести в own result evidence_ref — «latest» только навигация).
6. Отдельный независимый verifier: statuses/IDs/paths/hashes/evidence refs и присутствие отчёта; физические PID/exit/raw frames.
7. Финал: artifacts/SEC003_SECURITY.json + reports/SEC003_SECURITY.md (раздел 0 «подозревал → проверил → оказалось» включая опровергнутые, verdict REQUEST_CHANGES/BLOCK/NO_VIOLATION_OBSERVED_IN_SCOPE — НЕ SAFE, coverage/omissions, findings с debt_refs; TD19/20/21 не дублировать и не закрывать; debt_status_changes=[]). completion_state=completed ТОЛЬКО если полный материал сдан; product_acceptance=false, is_approval=false. При лимите — continuation.json той же роли с точным остатком.

## Границы (как в основной карте)
Запись ТОЛЬКО artifacts/SEC003_SECURITY.json, reports/SEC003_SECURITY.md, runtime/SEC003/**. Продукт/tests/PL003/tech_debt read-only. Без Git/install/network/paid/субагентов/расширения grants/OMH delta. Не более двух детей; RPC≤25s, child≤90s, role wall≤1800s, PY сам .venv-проекта. Не запускать глобальный mockup.ab002_e2e. Хост PYTHONPATH тень mcp/pydantic — отработать.