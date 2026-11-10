# AC001 — независимая приёмка соответствия макета спецификации

Роль: reviewer/auditor, НЕ автор и НЕ fixer. Использовать принцип негативной приёмки harness docs/CODERS/07_AUDITOR_DILIGENCE.md, 03_ACCEPTANCE.md и проектные ограничения. Старт только после артефактов AB001; не принимать собственный код. Логическая ветка AC, задача AC001.

## Вход

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Прочитать полностью REQUIREMENTS.md с исходными словами заказчика, docs/SPEC.md, cards/AB001_BUILDER.md, research/AA002_RESEARCH.json acceptance_matrix и storage/digest/types, runtime/AB001_RESULT.json, mockup/README.md. Затем прочитать весь новый source mockup/ и релевантные tests. Отчёт worker — гипотезы для проверки, не evidence истины.

## Действия

1. Зафиксировать file list и SHA256 source/tests до проверки (без новых pycache/runtime); после проверить неизменность. Git-only diff недостаточен для untracked project.
2. Составить матрицу REQUIREMENTS→код→T01–T20→реально наблюдённый факт. Проверять НЕреализованное и обходы. Не путать simulation-требования с live production gaps Q01/Q02/Q08.
3. Реально выполнить документированные тесты и demo exact E:/opencode_harness_portable/.venv/Scripts/python.exe; temp/basetemp только P/runtime/AC001/. Не устанавливать и не менять source. Свой чистый runtime, не выдавать worker artifacts за свой прогон.
4. Особое внимание: каждый claim origin fields; immutable quote/link/comment/property; correction append gate; stable IDs/replay before OCC; actual process kill/reopen и two-process race, а не имитация exception; разные ветки/shared deps; scope до trace/YAML/outbox/errors; master coverage/current evidence/pending/unknown scope; real MCP subprocess handshake, stdout protocol, role forging failclosed; no fake external ACK.
5. Если поведение не доказано, NOT_TESTED и конкретный недостающий способ проверки. Допускается безопасная read-only Python probe и собственные отрицательные запросы к synthetic DB, созданной в P/runtime/AC001/. Не выполнять destructive операции на чужих файлах/БД, live OMH/Git.
6. Зелёные tests не заменяют соответствие коду; не требовать новый production framework или безграничный hardening сверх scope макета.

## Выход

Только P/review/AC001_SPEC_REVIEW.md и .json, плюс generated P/runtime/AC001/** logs/data. Source/mockup/tests/исходные docs read-only. JSON: task_id, verdict APPROVE|REQUEST_CHANGES|BLOCK, source_fingerprint_before/after, requirement_results[], acceptance_results T01–T20[], findings[{id,severity,requirement,code_refs,evidence,expected_fix}], commands/exit codes, limitations. Наличие 20 названий без physical evidence не покрытие. В финале точные пути и actionable findings, не исправления кодом.

## Приоритет записи вердикта

Вердикт пишет только проверяющий. Первый создаваемый артефакт — `runtime/AC001_SPEC_REVIEW.md`: заголовок, verdict-заглушка `PENDING`, затем findings дописываются по мере подтверждения. Последние вызовы резервировать на финальную запись verdict и JSON.

Не перечитывать файлы, уже перечисленные во входе; не делать глобальную разведку. Если лимит итераций исчерпан до финальной записи — это незавершённая работа (см. `docs/REVIEW_PROTOCOL.md`): оркестратор передиспатчит продолжение, а не примет обрезанный отчёт.

No commit/branch/merge/push, no install/config/plugin/registry changes, no user secrets/DB/transcripts. Любой неожиданный блокер явно вернуть родителю. Нельзя ослаблять спецификацию задним числом ради APPROVE.
