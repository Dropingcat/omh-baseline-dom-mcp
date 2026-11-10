# Подключение макета DOM к сессии Hermes (оркестратор) — 2026-11-08

Сделано: `hermes mcp add dom_sim` (штатная команда, ручной правки config.yaml не было). Подключено 12 инструментов: dom_init, dom_resume, dom_submit, dom_review, dom_admit, dom_append, dom_query, dom_snapshot, dom_trace, dom_export, dom_sync_status, dom_sync.

Параметры запуска:
- команда: `E:/opencode_harness_portable/.venv/Scripts/python.exe -m mockup.server`, PYTHONPATH = проект;
- каталог данных: `runtime/ORIENT/home` (отдельный, не трогает прежние прогоны);
- роль: `author` (фиксированная при запуске; смена роли = другой запуск);
- режим: simulation (по умолчанию), live-привязки нет;
- лог: `runtime/ORIENT/dom.log`.

Ограничения (честно):
- Это SIMULATION. Роль задаёт launcher, а не аутентификация (fixture roles ≠ auth, `not_checked` AU006).
- Инструменты появятся только в новой сессии или после `/reload-mcp`: hot-reload в уже идущую сессию не гарантирован.
- Версия кода — `3cd21d96` (W1 приёмка не завершена: RV007 CONFORM, AU008 REQUEST_CHANGES на c26812b3).

Откат: `hermes mcp remove dom_sim`.

Что проверяем: может ли оркестратор (я) вести этот проект через DOM — записать в базлайн текущее состояние плана, потерять контекст и восстановить его беспамятным `dom_resume`.
