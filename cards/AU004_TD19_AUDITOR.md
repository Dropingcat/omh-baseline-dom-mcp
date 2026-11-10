# AU004 — независимый НЕГАТИВНЫЙ аудитор: TD-DOM-19 fix на ПОСЛЕ-версии

Роль AUDITOR (независимый негативный; не принимающий, не worker, не reviewer-пересборка). Проверяет **НЕработающие** гарантии исправления TD19 на точной после-версии code_digest **08aa9a9b978831806bd0ef24fe26f7214ab21b31ca6d2bbe7d27a61bd29bfe6f** (изменены mockup/admission.py, mockup/server.py; добавлен mockup/public_dto.py; baseline 715b1ca8…ba3 15 файлов). Работает ПОСЛЕ reviewer RV004 (APPROVE) и worker AB003 (completed, НЕ APPROVE), их receipts — вход, не доказательство.

## Контекст deny-check
- Worker (seed 3101) заявил: smoke 8/8, CHK-A2-01/02 LEAK_CLOSED, A2-03 GATE_UNIFORM_SAFE, DELIVERY PASS, regression 1 failed(pre-existing, документирован)/63 passed. Artifacts: artifacts/WORKER_AB003_TD19.json, reports/WORKER_AB003_TD19.md, docs/SCHEMA_CHANGE_TD19.md, runtime/AB003/{run-pre-3101,run-post-3101,smoke-run,regression}.
- Reviewer RV004 (seed 7107) APPROVE, 5/5 green на своих seeds: CHK-A2-01/02 LEAK_CLOSED, A2-03 GATE_UNIFORM_SAFE, DELIVERY PASS, B-SIDE PASS. Artifacts: artifacts/REVIEWER_AB003_TD19.json, reports/REVIEWER_AB003_TD19.md, runtime/RV004/**.

## Нормативы (читать полностью)
E:/opencode_harness_portable/docs/CODERS/07_AUDITOR_DILIGENCE.md (въедливость, секция 0 обязательна), 09_FINDINGS_ESCAPE_HATCH.md (уровни 1/2/3), 10_CHAIN_CONTRACTS.md §3 (auditor выход), shared/code-factory-process.md. P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp.

## Задача (не пересобирать точный прогон worker/reviewer — НОВЫЕ комбинации)
1. Собственный PARTIAL JSON первой записью. Пересчитать digest самостоятельно (не доверять digest_check worker): sha256(json.dumps(sorted map mockup/**/*.py rel-path->sha256, sort_keys=True)).
2. Воспроизвести НЕгарантии своими свежими seeds+реальными MCP stdio subprocess+PIDs+SQL/file/oracle read-back на копиях, минимум ОДНУ собственную атакующую вариацию СВЕРХ pre/post-прогонов worker и reviewer. Целевые неработающие состояния:
   - public DTO НЕ выдаёт chain_head/глобальные revisions/events/head_hash/foreign broken_event_id **через любой MCP-канал (текст и structuredContent) и в любой ветке/поверхности** (query/snapshot/trace/resume/sync_status/export/sync);
   - глобальный integrity gate (verify_chain) сохранён: НЕ отключён ради ACL, единый безопасный Broken без foreign locator, DB/файлы/export before/after не меняются (только disposable copy);
   - delivery proofs/восстановление сохранены: internal observation stamp полный (chain_head+все revisions+port_reported), observation→attempt→intent→ack связаны, нет дублей записи;
   - оба канала MCP сериализуют ОДИН безопасный объект (text == structuredContent семантически);
   - ▼ НОВЫЕ поверхности, которые worker/reviewer НЕ сеяли:
     (a) AА-claim с dependencies, включающими foreign AB-ветку (например {AA:1, AB:M}, AB>0), прочитанный AA-only caller через dom_query/snapshot/resume/export — проецируется ли `AB:M` в публичном Claim.dependencies (`('map','int')`, без scope-фильтра)? Это утечка foreign-branch revision/existence через легальное поле.
     (b) AА-claim с `applicability`/`applicable_branches`, включающими foreign AB (public Claim.applicable_branches `('list','str')`, без scope-фильтра) — видит ли AA-only caller имя чужой ветки?
     (c) union caller master-trace: origins/residual/blockers — не проецируются ли foreign branch-имена/id в публичный Trace.
     (d) YAML export на fixture с AB-метаданными — scoped ли (нет ли foreign branch/rev/hash внутри байт).
     (e) foreign revisions через storage_error/delivery intents/trace.origins на AA-only.
   - permission/sharing boundary: scope-грант, launch-grants (role/branches), никакой tool-call не промоутит; покрытие check_ids по PL003/SEC-QA.
3. Заполнить секцию 0 (подозрения → проба → observed → OK/finding/UNVERIFIED). Timing — NOT_CHECKED (не измеряется). Не утверждать более широкую безопасность, чем проверено; не принимать продукт.
4. Запись ТОЛЬКО: artifacts/AUDITOR_AB003_TD19.json, reports/AUDITOR_AB003_TD19.md, runtime/AU004/**. Продукт/tech_debt/tests/AB003/RV004 evidence read-only.

## Вердикт
product_acceptance=false, is_approval=false; verdict **APPROVE_CONTINUOUS / REQUEST_CHANGES / BLOCK** (никогда SAFE). findings[] с severity+debt_ref (TD19 не дублировать; новый TD — только если найден НОВЫЙ путь). debt_status_changes=[] + рекомендация (полное закрытие TD19 — решение OMH/заказчика). При лимите — честный PARTIAL + continuation.json той же роли с точным остатком; родитель финал не дописывает. Сам пишу вердикт.

## Инструменты/безопасность
PY=E:/opencode_harness_portable/.venv/Scripts/python.exe, CWD=P. Не более двух детей одновременно. raw stdio MCP через real serve subprocess. НЕ глобальный ab002_e2e. Только disposable копии для коррупции; не трогаю product/tests/tech_debt/AB003/RV004. Не запускаю других агентов. Real PID фиксировать, свои subprocess закрывать.