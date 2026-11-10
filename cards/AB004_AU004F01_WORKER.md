# AB004 — worker: AU004-F-01 (dependencies maps без scope-фильтра)

Роль WORKER. Продолжение цели TD-DOM-19 (конфиденциальность скрытой ветки), НОВЫЙ путь, найденный независимым аудитором AU004 на версии code_digest 08aa9a9b978831806bd0ef24fe26f7214ab21b31ca6d2bbe7d27a61bd29bfe6f.
P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. PY=E:/opencode_harness_portable/.venv/Scripts/python.exe, CWD=P, чистый env (env -u PYTHONPATH -u PYTHON -u PYTHON_BIN -u PYTHON_VENV -u VIRTUAL_ENV -u PYTHONSCRIPT -u PYTHONHOME).

## Читать обязательно целиком
artifacts/AUDITOR_AB003_TD19.json (finding AU004-F-01), reports/AUDITOR_AB003_TD19.md, runtime/AU004/au004_probe.py, runtime/AU004/run-au004/results-au004.json, mockup/public_dto.py, mockup/projections.py, mockup/admission.py, docs/SCHEMA_CHANGE_TD19.md, cards/AB003_TD19_WORKER_PREPARED.md (границы), artifacts/RESEARCHER_AB002_A.json (public_schemas).

## Дефект (подтверждён родителем по диску)
AA-only caller (grant {AA}) получает `dependencies={AA:1, AB:2}` в Claim.dependencies и Provenance.dependencies (public_dto: ('map','int')) через dom_query/dom_snapshot/dom_resume и в байтах YAML export (`AB: 2`, grep, runtime/AU004/run-au004/export-probe/exports/AA-2-*.yaml строки 9 и 104). Причина: read_snapshot.revisions фильтруется по гранту, карты dependencies — нет. Условие: union-автор допустил AA-клайм с зависимостью на AB (check_references для claim возвращается рано).

## Решение заказчика/дефолт
Правило «scope-first» уже принято: вызывающий видит только ветки своего гранта. Для карт dependencies: ключи чужих веток УБИРАЮТСЯ из публичного вывода (не маскируются, не заменяются счётчиком или маркером «скрыто»). Внутреннее хранение, claim_snapshots, admission, internal proof и delivery-stamp НЕ меняются.

## Задачи (по порядку)
1. Воспроизвести дефект ДО правки своим прогоном (свой seed, не 92041/3101/7107), raw frames, PID/exit, YAML grep. Сохранить как pre-evidence, не переписывать.
2. Правка ТОЛЬКО в mockup/public_dto.py (и если неизбежно — точечно admission.py/projections.py/server.py). Фильтр на выходе по launch-grant вызывающего для ВСЕХ полей типа map-по-веткам: Claim.dependencies, Provenance.dependencies, и любое другое ('map',…) с ключами-ветками (проверь перечень сам, перечисли в отчёте). Тот же фильтр для YAML export. Оба канала MCP — один объект.
3. Внутренняя логика (trace stale-проверка по полным dependencies, readiness, blockers) считается по ПОЛНЫМ внутренним данным; наружу — только публичный результат. Зафиксируй как observation: reasons вроде STALE_CHECK не называют ветку; оцени, раскрывает ли сам факт staleness существование зависимости, и опиши (не расширяй scope).
4. Варианты E2E (свои seeds, минимум 4 разные начальные условия, реальный MCP stdio): (a) AA-only при deps {AA,AB}; (b) deps только AB; (c) union-caller видит всё; (d) AB-only видит AB, но не AA-ключи у своих клаймов; (e) deps на третью ветку ZZ, не существующую в гранте; (f) повторная проверка YAML export байтами (grep по всем AB-токенам, включая base64-тела канареек); (g) corrupt-ветка: gate по-прежнему единообразный Broken без foreign locator (регрессия TD19). Для каждого — ожидаемый результат и физический read-back (SQL/файл), oracle.
5. Регрессия: pytest -q (допускается ровно 1 прежний документированный падающий test_event_chain_is_verified_and_forgery_is_detected; новых падений быть не должно), smoke, прогон run-post сценариев AB003/RV004/AU004 на новой версии: все должны оставаться зелёными, кроме ожидаемого изменения F-01 (AU004 X1 теперь LEAK_CLOSED).
6. Документация: docs/SCHEMA_CHANGE_AU004F01.md (что убрано/как фильтруется), artifacts/WORKER_AB004_AU004F01.json, reports/WORKER_AB004_AU004F01.md, runtime/AB004/** (pre/post, manifests, sha256, digest до/после).

## Границы
Запись: mockup/public_dto.py (+точечно admission/projections/server при необходимости, перечислить), docs/SCHEMA_CHANGE_AU004F01.md, artifacts/WORKER_AB004_AU004F01.json, reports/WORKER_AB004_AU004F01.md, runtime/AB004/**. Не трогать tests/, tech_debt.md, oracle, чужие артефакты (AB003/RV004/AU004/SEC003/QA003). Не добавлять инструменты/гранты; не реализовывать граф, keywords, куратора; TD20/TD21/UD — вне scope. Без Git/install/network/paid/субагентов/OMH delta. Не ослаблять тесты ради зелёного. product_acceptance=false, is_approval=false, долг не закрывать (закрытие — после независимых reviewer+auditor на этой версии). Пересчитать digest методом SEC003 до и после.

## Лимит
Первым писать честный PARTIAL + first_artifact. Ориентир — 35 вызовов, 4 последних резервировать на JSON/MD/SCHEMA и проверку путей. При лимите — continuation той же роли с точным остатком; родитель финал не дописывает. Вердикт пишет сам исполнитель.
