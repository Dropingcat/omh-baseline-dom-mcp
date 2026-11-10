# AU006 — CONTINUATION 01 (аудитор; запуск умер до финального вердикта)

Роль та же: AUDITOR AU006. Полный контракт — cards/AU006_TASK_BASELINE_AUDITOR.md (читать целиком; TBO-01..10, что атаковать, выходы, границы не менялись). Плюс карта цели/пунктов: docs/TASK_BASELINE_OBLIGATION_2026-11-08.md.

## Состояние (проверено родителем после падения deleg_aacd7f9c)
- Причина — недоступность провайдера (timeout, 1615 с), не вывод по продукту.
- Код не тронут: digest 16 файлов = 1ead2d45373ea85262b5989a9d86e5e6a0ace6feeeabcf41ba633b09a7a450bf (пересчитать в начале методом SEC003).
- Существует и НЕ переписывать:
  - artifacts/AUDITOR_AU006_TASK_BASELINE.json — только начальный PARTIAL (294 байта), verdict=null.
  - runtime/AU006/first_artifact.json, checks.partial.json (7359 б) — частичные проверки TBO.
  - runtime/AU006/host_fixture/ и host_fixture_recheck/ — реальные прогоны с PID/exit (в т.ч. kill-сценарии: author_before_kill exit=1, after_kill exit=0).
  - runtime/AU006/drivers_frozen.json, freeze_sources.py — замороженные драйверы/хеши.
  - runtime/AU006/build_report.py (49 КБ) — уже написанный сборщик отчёта; ПЕРЕД использованием прочитать и проверить, что он собирает итог из фактических данных, а не подставляет готовые выводы.
- Лог: C:/Users/Arhys/AppData/Local/hermes/cache/delegation/live/deleg_aacd7f9c/task-0.log. Слова в логе — не физический эффект; сверять с frames/SQL на диске.

## Остаток
1. Прочитать свои же checks.partial.json, host_fixture/**/results, drivers_frozen.json; составить карту «какие TBO из 10 реально проверены, какими прогонами, где остался пробел». Записать runtime/AU006/continuation_status.json (без фальшивого PASS).
2. Завершить недостающие пробы TBO (приоритет: TBO-02 предварительная сверка/доставка контекста, TBO-03 контроль на доверенной границе, TBO-04/07 ведение ветки и завершение, TBO-09 сбой/повтор). Уже выполненные kill-сценарии не перезапускать без причины.
3. Вынести вердикт по реальному узкому scope: APPROVE_CONTINUOUS / REQUEST_CHANGES / BLOCK. Обязательность, которая существует только в промпте/регламенте, не даёт APPROVE полной цели — это GAP/policy_only с точным описанием.
4. Сдать artifacts/AUDITOR_AU006_TASK_BASELINE.json (финал), reports/AUDITOR_AU006_TASK_BASELINE.md (раздел 0 первым), runtime/AU006/** с manifest+ledger+verifier. product_acceptance=false, is_approval=false, debt_status_changes=[].

## Что учесть (появилось после запуска)
- AU005 закрыт: COMPLETE_WITH_LIMITS / REQUEST_CHANGES; findings F-01 (scoped YAML ack как полная доставка), F-02 (выдача кешированного receipt закрытой AB после сужения grant), F-03/F-04 minor; graph/search/version tree/revalidation/live OMH — GAP. Использовать как готовый вход со ссылкой на hash, не дублировать его пробы.
- AN006 (аналитик) параллельно разбирает эти findings и сверяет PL003. Не ждать, не читать незавершённое, не дублировать.
- Решения заказчика не переоткрывать: O1 (устаревание не скрывать), O2 (происхождение доступного клайма показывать всегда), O3 (receipt = tx+получатель+ревизия+scope+byte hash), итеративный поиск по графу (GAP, не реализовывать), обязательность сверки/ведения (твой предмет).

## Экономия бюджета
Писать на диск порциями (после каждого блока проверок), чтобы обрыв провайдера не терял результат. Резерв последних 5 вызовов на артефакт/отчёт/manifest. При повторе сбоя — честный PARTIAL + точный остаток для continuation той же роли; родитель вердикт не дописывает.
