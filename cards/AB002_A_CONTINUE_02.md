# AB002-A-C2 — продолжение после обрыва владельца

Роль: worker-developer, та же задача AB002-A. Не независимый проверяющий. Продолжить сохранённое C1, не повторять анализ/исследование и не пересобирать с нуля.

## Полный контракт и приоритет

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Читать cards/AB002_A_WORKER.md (A1…A9, scope, E2E и все запреты), cards/AB002_A_CONTINUE_01.md и эту карту. REQUIREMENTS.md — первичный авторский базлайн; docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md отложен для researcher, не реализовывать refinement в A.

Слова заказчика: «продолжай тогда». Продолжение разрешено, не завершение по неизвестному результату.

## Наблюдаемое состояние

Делегирование C1 закончилось `owner exited before recording terminal result`, это НЕ обычный completed и НЕ доказательство, что все side effects не случились. Живых субагентов нет. Перед повторными операциями читать фактические БД/manifest/командные квитанции и дерево исходников.

- runtime/AB002_A/command-C1-2cc42bf0/command.json фиксирует `-m mockup.ab002_e2e`, exit_code=1073807364, started 2026-11-06T22:58:15Z, finished 23:02:17Z. Причина прерывания не установлена, не объявлять timeout/defect без evidence.
- stdout.log в той же директории содержит PASS через E9 S1-hash. В `matrix-b5627919/E9-S1-S3-envelope` остались кадры/БД, но конец всего прогона не подтверждён.
- Нынешний mockup/ab002_matrix.py уже содержит новые binding cases и specs (около 26 вариантов); НЕ требовать старого количества 22 и не объявлять их пройденными из старого manifest.
- artifacts/WORKER_AB002_A.json и reports/WORKER_AB002_A.md существуют, но остались PARTIAL/устарели. Обновить фактический остаток первым результатом.
- E10-tight-C1-244c7711 и diagnose-E10-1f5f2df5 содержат read-back для разбора E10; старый FAIL CHAIN_INTEGRITY вместо IMMUTABLE нельзя просто скрыть. Прочитать результат и строгий исправленный oracle.
- runtime/AB002_A/run_command_c1.py сохраняет реальные stdout/stderr/exit. Проводной E2E занимает более четырёх минут. Выставлять щедрый timeout 600 секунд; не обрывать весь прогон коротким tool timeout. Если требуется дольше — tracked background process + процессный контроль (если инструмент доступен), без бесконтрольных polling loops и без ожидания дочернего агента.

## Конкретные действия

1. Инвентаризировать текущий manifest, C1 diagnostics, runner/процессные квитанции; сверить source/input fingerprints. Честный PARTIAL со статусом unknown для недописанных результатов. Дочерние тестовые процессы прошлой задачи проверять адресно по commandline/пути, не убивать чужие Python.
2. Завершить E10/binding probes: точный SQL, правильный отказ и неизменность байтов до/после, не catch любого исключения/except pass. Если реально сломан продукт — минимальный фикс + исходный отрицательный сквозной сценарий.
3. Запустить нынешнюю полную E2E-матрицу настоящим stdio MCP через отдельные процессы с достаточным timeout. Сначала прочитать фактический CLI, не выдумывать опции. Каждый случай — actual, PID/exit и read-back. Только новый run-dir, старые факты не удалять. При частичном повторе связывать evidence с точным исходным fingerprint и условиями, не смешивать старый PASS и новый код молча.
4. Если сквозной прогон полностью завершён — обязательные регрессии и happy-path demo, реальные exit: Python E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q --basetemp=runtime/AB002_A/pytest-final-C2; затем -B -m mockup.demo. Зелёные unit не заменяют E2E и восстановление.
5. Финализировать mockup/README.md с точными командами/ограничениями, runtime/AB002_A/e2e_manifest.json, artifacts/WORKER_AB002_A.json и reports/WORKER_AB002_A.md. Приёмочный ledger A1…A9, executed/omitted variants, paths, fingerprints, commands/exit, actual target-state, known failures, proposed debt, security limits, not_checked/UD. PARTIAL допустим, is_approval=false всегда.

## Scope и безопасность

Писать только P/mockup/**, P/tests/**, P/runtime/**, P/artifacts/WORKER_AB002_A.json, P/reports/WORKER_AB002_A.md. Остальное read-only. Никаких Git-мутаций, установок, сети/listeners, paid models, секретов, live OMH/реальных пользовательских БД, удаления существующего кода/логов, ослабления guard/oracle, skip/xfail. Разрушительные пробы только disposable runtime. LIVE OMH=NOT_TESTED, UD-01…06 не выбирать.

## Завершение и бюджет

Без новой глобальной разведки. Оставить вызовы на документы/JSON и проверку. Не откладывать write-result на последний вызов. Если снова лимит/обрыв — честный remaining/continuation_required и доказанные пройденные стадии; не выдавать неполный запуск за PASS. Только после полной сдачи всех артефактов оркестратор запускает reviewer, затем auditor, затем analyst/researcher.
