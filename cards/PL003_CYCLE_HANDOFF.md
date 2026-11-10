# PL003 — дополнение к исходной техкарте после RS002-A

Базовая карта: cards/PL003_NEGATIVE_E2E_PLANNER.md, читать полностью. Этот overlay добавляет актуальные входы/остаток и не меняет исходный baseline. Запускается сейчас после completed researcher, не параллельно с ним. Текущий продукт REQUEST_CHANGES.

## Прочитанный и проверенный хендофф

Родитель проверил artifacts/RESEARCHER_AB002_A.json и reports/RESEARCHER_AB002_A.md, completion_state completed/status COMPLETE_MATERIAL, product_acceptance=false, no continuation, 5 дословных Q-A2-01…05, все required поля, 7 LP-A2/CHK-A2, 93 current frozen inputs и output/evidence hashes. Команда дала PASS_MATERIAL_HANDOFF_ONLY/exit0, не продуктовый E2E.

Фактический текущий code digest: 715b1ca81f6d8c47f4f43f3977f1150d95583968c876edb556fde4c7ba927ba3 (sha256 json.dumps(sorted map mockup/**/*.py path→sha256,sort_keys=True), UTF8; Windows separators нормализованы /). Это не Git revision. При старте переснять и проверить, не выдумывать commit.

Новые точные входы:
- artifacts/RESEARCHER_AB002_A.json: planner_handoff, worker_fix_contract, поля public/internal/privileged, public_schemas; reports/RESEARCHER_AB002_A.md §§PL003 delta/GAP и Worker fix;
- runtime/RS002_A/validation.json, input_hashes.json, evidence_catalog.json, immutable_reference_example.json — собственные material proof, НЕ новый security E2E;
- cards/AB003_TD19_WORKER_PREPARED.md — P0 fix подготовлен, НЕ DISPATCHED, не live grant;
- точные auditor/analyst/reviewer файлы AB002_A из base card. Родитель оставляет приёмку REQUEST_CHANGES.

## Как употребить материал

1. LP-A2-01…07 / CHK-A2-01…07 перенести без потери связей в failure map; сохранить state observed vs hypothesis. Known TD19 не переименовывать в новую гипотезу/новый долг. Добавить новые риски из capability/code inventory, а не повторять только семёрку.
2. Нужна настоящая карта public ingress→trusted context/scope→SQL/graph→output/effect с актуальными file:line и source hashes. Не объявлять кэш/ранжирование реализованными без кода. Selective search, dedicated branch search и nested child refinement отсутствовали в inventory RS002; перепроверить и явно GAP/NOT_IMPLEMENTED, не заменить snapshot/replacement.
3. В негативном плане ровно различить: существующая веточная фильтрация snapshot; отсутствие search/refinement; domain error vs raw crash; confidentiality/integrity/readiness/availability. Global failure signal допустим, локатор foreign event — нет; не обещать timing noninterference без probe.
4. TD20 baseline пока fail-stop: domain-safe отказ — ожидаемая будущая реализация, но старый AttributeError — finding. Обязательный per-intent YAML continuation НЕ СОГЛАСОВАН (RS002-DEC-CONTINUE), не писать его в oracle как уже обязательный. TD19 не ждёт нового разрешения на прекращение утечки.
5. SEC003/QA003 — свои реальные E2E через MCP/PID/SQL/files/read-back, только disposable fixtures. Их роль не правит продукт; known defects/новые сведения не маскировать успешными тестами. PL003 только планирует, не запускает атаки/агентов.
6. Run-specific immutable manifests, exact hashes/source/input/environment, положительные контроли+неблагополучные runs сохраняются. Shared latest pointer не sole evidence. Отдельный trusted fixture oracle, не скрытая выдача foreign values в роль AA. Сильную OS-изоляцию simulation не обеспечивает.

## Самостоятельная сдача/лимит

Пути outputs/границы ровно из base card; новые support scripts только runtime/PL003/**. Финальный JSON — свой, не родителя. Программно проверить обязательные операции (write/read/append-only update/selective search/branch search), уникальные hypothesis/check/scenario IDs и связи, 7 входных LP-A2 checks, две заполненные карты, OMH delta и все локальные evidence refs. Gap count и executed count честные: planning не тестирование. Исходные файлы product/tests/debts/прошлые evidence read-only.

Ориентир 18–24 calls, последние 4 — сохранение+validation. Сперва минимальный PARTIAL, затем файлы пакетами; в MD не дублировать весь большой JSON. При cap — continuation с точным остатком, не фиктивный COMPLETE. В финале именовать пути для родительской проверки. По завершении parent применяет OMH delta и диспатчит SEC003, не ты.
