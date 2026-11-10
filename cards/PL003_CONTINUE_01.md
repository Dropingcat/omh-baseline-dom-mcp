# PL003 — CONTINUATION 01 (та же роль, с места обрыва)

Роль и контракт без изменений: cards/PL003_NEGATIVE_E2E_PLANNER.md + cards/PL003_CYCLE_HANDOFF.md + templates/NEGATIVE_E2E_SECURITY_CONTRACT.md — прочитать полностью. P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Это НЕ новый запуск: предыдущий PL003 (deleg_b2fa931d) оборвался на HTTP 403 провайдера (причина — доступ к модели, не содержание работы). Не переделывать готовое.

## Что уже сделано предыдущим запуском (проверить файлами, не верить этой записи)
runtime/PL003/: capability_inventory.json, public_tool_schemas.json, input_fingerprints.json, support_input_hashes.json, failure_map.json (23 гипотезы), scenario_plan.json (23 сценария/23 checks), card_contracts.json, omh_plan_delta.json, build_maps.py, build_documents.py, validate_material.py (НАПИСАН, НЕ ЗАПУЩЕН).
docs/NEGATIVE_E2E_PLAN.md, cards/SEC003_SECURITY.md, cards/QA003_FAILURE_TESTER.md — записаны (omh_applied=false).
Последний вывод build_maps: static only, product_checks_executed=0, code_digest 715b1ca8…927ba3, gap_count 10.

## Остаток — ТОЧНО
1. Перечитать готовые файлы; убедиться, что они целы и парсятся; снять текущий code digest и сравнить с 715b1ca8…; при расхождении записать, не скрывать.
2. ДОБАВИТЬ в failure_map/scenario_plan/план/обе карты новый канал утечки (новое требование заказчика, пока NOT_IMPLEMENTED): «самочувствующие связи» в стиле Obsidian — backlinks/соседи карточки/дашборды связей. Гипотеза H-LINK: обратные ссылки, счётчики соседей и дашборды могут раскрывать существование/число/ID объектов запрещённой ветки. Это GAP/NOT_IMPLEMENTED (API нет) — чек подготовить как будущий, пометить NOT_IMPLEMENTED, не PASS. Раньше добавленное не удалять.
3. Запустить runtime/PL003/validate_material.py (E:/opencode_harness_portable/.venv/Scripts/python.exe -B). Исправлять ТОЛЬКО свои материалы; если validator находит реальный дефект плана — исправить план, не ослаблять проверку.
4. Записать финальные: artifacts/PLANNER_NEGATIVE_E2E.json (completion_state=completed только если всё выше есть; gap/executed честно: executed=0 — это планирование), reports/PLANNER_NEGATIVE_E2E.md (раздел 0, остаток, GAP, что НЕ проверено), runtime/PL003/validation.json.
5. В отчёте: перечислить пути, число hypotheses/checks/scenarios/gaps, подтвердить omh_plan_delta подготовлен, НЕ применён.

## Границы (прежние)
Пишешь только: docs/NEGATIVE_E2E_PLAN.md, cards/SEC003_SECURITY.md, cards/QA003_FAILURE_TESTER.md, artifacts/PLANNER_NEGATIVE_E2E.json, reports/PLANNER_NEGATIVE_E2E.md, runtime/PL003/**. Остальное read-only. Без Git/install/сети/платных/секретов/атак/правки продукта. Ориентир 8–12 вызовов. При лимите/обрыве — снова continuation той же роли с точным остатком; родитель за тебя не дописывает.
