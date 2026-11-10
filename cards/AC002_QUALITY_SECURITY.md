# AC002 — независимый quality/security review макета

Старт только после устранения spec findings AC001. Роль — reviewer/tester, НЕ author/fixer. Ветка AC, задача AC002. Цель: попытаться опровергнуть заявленные гарантии в рамках локального synthetic mock, не выдавая API-only ACL за OS sandbox.

## Материал

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. REQUIREMENTS.md, docs/SPEC.md, docs/IMPLEMENTATION_PLAN.md, research/AA002_RESEARCH.json, mockup source и README, tests, AB001_RESULT, review/AC001_SPEC_REVIEW. Исходные слова заказчика выше выводов worker. При изменении source после AC001 учитывать stale evidence и затронутые обязательные проверки.

## Проверка

- Strict JSON/schema/coercion: duplicates, bool-as-int, float, unknown privileged fields, malformed base64/surrogate/body limits.
- Identity spoofing и root self-review, production default failclosed; test role mapping только launcher/injected adapter.
- Scope across work/branch/source dependency/query/history/trace/export/outbox/error counts. Выход не может раскрывать чужие origin body/provenance из cross-branch shared claim без разрешения; origin marker сам по себе не разрешение.
- Immutable UPDATE/DELETE через normal SQL, event provenance и возможности bypass admission через append/applicability/archive/exclusion.
- Canonical intent binding, same key diff operation/body/context, dedupe-before-OCC, exact review bindings; dependency checks обязательны при каждом admission, не только при submit.
- Atomic write set/foreign keys, reopen/race/crash and process cleanup; transaction errors не выдавать за complete rollback без query.
- Historical deterministic YAML at exact revision; no caller-provided paths/traversal; no foreign exports on denied request; outbox ack только matching target/version/digest; no false exactly-once.
- Trace не принимает local done/git merge как coverage; archive/stale/pending/conflict/limited scope не green.
- Actual MCP transport и explicit minimal safe Windows env; no stdout diagnostics/leaked secrets, default no live services.
- Code clarity/error paths proportionate to mock, без косметических требований и scope creep.

Реально повторить независимый full pytest/demo и targeted негативные действия в собственной synthetic P/runtime/AC002/. Зафиксировать source/test fingerprints до/после, команды/exit codes и физические выходы. Не читать реальные пользовательские данные и не менять продуктовый source/tests.

## Выход

Только P/review/AC002_QUALITY_SECURITY.md и .json, generated P/runtime/AC002/**. Verdict APPROVE|REQUEST_CHANGES|BLOCK; critical/major/minor findings с exact reproduction, code refs, expected behavior, actual evidence. Runtime isolation NOT_ENFORCED и live Q01/Q02/Q08 остаются ограничениями, не скрываются и не считаются автоматически багом synthetic adapter.

## Приоритет записи вердикта

Вердикт пишет только проверяющий. Первый создаваемый артефакт — `runtime/AC002_QUALITY_SECURITY.md` с verdict-заглушкой `PENDING`; findings дописываются инкрементально. Последние вызовы резервировать на финальную запись verdict и JSON.

Не перечитывать уже известные файлы, не повторять глобальную разведку. Обрыв по лимиту итераций до финальной записи — незавершённая работа (`docs/REVIEW_PROTOCOL.md`): передиспатч продолжения, а не приём обрезанного отчёта.

Никаких fixes/установок/live plugin/config/registry/Git state changes. Не самостоятельно закрывать master или задачи. При критичном вернуть родителю для нового worker→review цикла.
