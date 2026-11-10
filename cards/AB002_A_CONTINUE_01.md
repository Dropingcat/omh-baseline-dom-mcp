# AB002-A-C1 — continuation воркера после лимита

Статус: действующее продолжение cards/AB002_A_WORKER.md, не новая задача с нуля. Роль та же: worker-developer. Независимая приёмка ещё не начиналась.

## Исходный контракт

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp. Прочитать cards/AB002_A_WORKER.md целиком; первичный REQUIREMENTS.md выше предложений. Сохранить A1…A9, scope, запреты, требования вариативных E2E. E2E первичны, unit counts — не приёмка. После сдачи строго reviewer → auditor → analyst → researcher, не параллельное ревью.

## Проверенный остаток на остановке

- runtime/AB002_A/e2e_manifest.json: 22 случая, 21 PASS / 1 FAIL (считано оркестратором из JSON, не по чату).
- Единственный FAIL: runtime/AB002_A/matrix-03b27440/E10-S1-immutable-all-tables/case.json. Реальная ошибка: попытка изменить events получила sqlite3.IntegrityError('CHAIN_INTEGRITY'), а проба immutable на ab002_matrix.py:213 ожидала только IMMUTABLE (либо ACK_REQUIRES_OBSERVED для delivery_events), поэтому сам oracle упал AssertionError. Это не установленная потеря immutability и не установленная безвредность: нужен read-back строк/байтов, вида SQL и реально сработавшего guard.
- artifacts/WORKER_AB002_A.json существует, status PARTIAL, но устарел (нет результата последнего E2E).
- reports/WORKER_AB002_A.md не создан.
- Baseline ложного ack воспроизведён через MCP и сохранён в runtime/AB002_A/baseline-a668de14/; не повторять разведку.
- Код уже изменён: admission.py, storage.py, ports.py; добавлены delivery.py, ab002_launcher.py, ab002_e2e.py, ab002_matrix.py, ab002_lock.py. Проверить реальное дерево, не гадать по старому контракту.

## Порядок continuation

1. ПЕРВЫМ действием прочитай failed case, кратко обнови worker result и создай reports/WORKER_AB002_A.md честным PARTIAL с проверенным остатком. Не писать PENDING/APPROVE. Потом дополнять результат.
2. Разбери E10: конкретный SQL, guard order, старое/новое содержимое всех затронутых строк и хеши. Если продукт нарушает инвариант — фикс продукта и регрессия. Если это проверка слишком узкой диагностической метки — допускается исправить ожидаемую классификацию только с доказанным отказом операции и точным неизменным read-back; НЕ заменять на catch любого IntegrityError/except pass, НЕ удалять asserts, НЕ ослаблять защиту/оракул.
3. Заверши негативные binding-пробы из исходной карты (ack первым, чужой intent/tx/digest/target, отсутствие observation, попытки REPLACE/IGNORE/UPSERT). Не принимать ack по самому тексту ответа порта.
4. Перезапусти фактический воспроизводимый E2E-runner через stdio MCP, с реальными PID/crash/reopen/read-back. Новый run directory; старые факты и логи сохранить. Сначала устанавливать по --help/README/код entrypoint, не придумывать синтаксис.
5. Финальные регрессии и demo, реальные exit codes: из P E:/opencode_harness_portable/.venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests -q --basetemp=runtime/AB002_A/pytest-final-C1 ; затем ... -B -m mockup.demo. Сверить финальное состояние цели, no losses/duplicates/false READY.
6. Обнови mockup/README.md: реальные команды, схема/protocol, migration, приёмочный scope, ограничения simulation и остаток. Source/input fingerprints на конечном дереве.
7. Заверши artifacts/WORKER_AB002_A.json и reports/WORKER_AB002_A.md, e2e_manifest.json. Явные поля per_invariant A1…A9, commands/exit, scope, evidence, not_implemented/not_checked, omissions, security_limits, proposed_debts. Проверь пути и JSON программно. Это self-report, не независимая приёмка.

## Новое требование, не расширяющее scope A

REQUIREMENTS.md дополнен деревом дочерних immutable уточнений клайма; docs/RESEARCH_NOTE_CLAIM_REFINEMENT.md — для следующего researcher. Не реализовывать его в этом continuation. Указать deferred_to_researcher в handoff и новую версию baseline; результаты A не объявлять полной реализацией нового требования.

## Границы и инструменты

Ровно прежняя область записи: P/mockup/**, P/tests/**, P/runtime/**, P/artifacts/WORKER_AB002_A.json и P/reports/WORKER_AB002_A.md. Остальные документы/карты/источники и плагины read-only. Python E:/opencode_harness_portable/.venv/Scripts/python.exe. Доступны file tools/terminal, никакой установки, сети/listeners, Git-мутаций, секретов, paid models, live OMH/пользовательских баз, удаления старого кода/логов и ослабления guards.

LIVE OMH=NOT_TESTED. Не выбирать UD-01…06. Деструктивные пробы только в disposable runtime. Последние вызовы резервировать для результатов. Если лимит — continuation этой же роли, не ложный PASS и не просьба оркестратору дописать за тебя.
