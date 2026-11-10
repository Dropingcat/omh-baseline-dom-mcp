# dom-branches — панель «dom» (DOM-ветки клаймов), установка

Только чтение: панель показывает ветки, клаймы, незавершённые кандидаты и доставку. Ничего не пишет и не допускает.
Статус: файлы собраны в `P/plugin/dom-branches/`; **в Hermes home не установлено**, загрузка плагина в приложении **не проверена**.

P = `E:/opencode_harness_portable/projects/omh-baseline-dom-mcp`

## Состав

| Что | Откуда (в P) | Куда |
|---|---|---|
| backend | `plugin/dom-branches/plugins/dom-branches/dashboard/{manifest.json,plugin_api.py}` | `<HOME>/plugins/dom-branches/dashboard/` |
| desktop-плагин | `plugin/dom-branches/desktop-plugins/dom-branches/plugin.js` | `<HOME>/desktop-plugins/dom-branches/plugin.js` |
| каталог DOM | (создать) | `<HOME>/dom-branches.json` |
| читатель | `mockup/overview.py` (уже в P) | не копируется; backend вызывает его из P |

`<HOME>`: у каждого шлюза свой Hermes home и свой backend (profile в запросе backend не читает):
- default: `C:/Users/Arhys/AppData/Local/hermes`
- writer: `C:/Users/Arhys/AppData/Local/hermes/profiles/writer`

## Шаги (на каждый HOME отдельно)

1. Скопировать (PowerShell или bash):
   ```
   mkdir <HOME>/plugins/dom-branches/dashboard
   copy P/plugin/dom-branches/plugins/dom-branches/dashboard/* <HOME>/plugins/dom-branches/dashboard/
   mkdir <HOME>/desktop-plugins/dom-branches
   copy P/plugin/dom-branches/desktop-plugins/dom-branches/plugin.js <HOME>/desktop-plugins/dom-branches/
   ```
2. Создать `<HOME>/dom-branches.json` — каталог запуска DOM этого шлюза; обязан лежать внутри `P/runtime` (абсолютный путь, без `..`, без ссылок наружу):
   - default (пилот ORIENT):
     ```json
     {"directory": "E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/runtime/ORIENT/home"}
     ```
   - writer (каталог писателя выбирает оркестратор; пример-заглушка):
     ```json
     {"directory": "E:/opencode_harness_portable/projects/omh-baseline-dom-mcp/runtime/WRITER/<run dir>"}
     ```
   Каталог должен содержать `dom.sqlite3`; иначе панель покажет `NO_DATABASE`.
3. В `<HOME>/config.yaml` добавить id в `plugins.enabled` (иначе backend не импортируется):
   ```yaml
   plugins:
     enabled:
       - dom-branches
   ```
   (рядом с уже существующими `agora`, `omh` и т.д.; ничего не удалять).
4. Перезапустить шлюз (backend монтируется при старте/по hot-mount, см. `_mount_plugin_api_routes` в `hermes_cli/web_server_dashboard.py`).
5. В приложении: Settings → Plugins → включить `DOM branches` (`defaultEnabled: false`), ⌘K → **Reload desktop plugins**. Панель `dom` откроется справа рядом с `omh`.

Backend запускает `E:/opencode_harness_portable/.venv/Scripts/python.exe -I -B -c <bootstrap>` с `mockup.overview` (shell нет, таймаут 10 с, cwd = P). `-I` игнорирует `PYTHONPATH`, поэтому корень проекта передаётся аргументом bootstrap, а не окружением (отличие от формулировки карты «`-I -m` + PYTHONPATH», которая в таком виде не импортирует `mockup`).
Пути P и PY зашиты константами в `plugin_api.py` (`PROJECT_ROOT`, `PYTHON`); при переезде проекта поправить их.

## Проверка вручную после установки (не сделана)

- `GET /api/plugins/dom-branches/overview` → JSON `dom_overview/v1` либо `{"error": ...}` с HTTP 200.
- Без `dom-branches.json` или с чужим каталогом — запись `{"error": ...}`, панель пишет `reader error`.

## Откат

1. Удалить из `plugins.enabled` строку `dom-branches` (config.yaml).
2. Удалить `<HOME>/plugins/dom-branches/`, `<HOME>/desktop-plugins/dom-branches/`, `<HOME>/dom-branches.json`.
3. Перезапустить шлюз и ⌘K → Reload desktop plugins.
Данные DOM (`runtime/**`) откат не затрагивает: панель их не изменяет.

## Исправление после первой установки (2026-11-09)
Первая установка не загрузилась: `Failed to load plugin 'dom-branches': No __init__.py`. Hermes требует у backend-плагина `plugins/<id>/__init__.py` с `register(ctx)` и `plugin.yaml` (`name`, `kind: backend`, `has_dashboard: true`). Оба файла теперь в `plugin/dom-branches/plugins/dom-branches/`. Копировать их вместе с `dashboard/`. Проверка: после `hermes plugins enable dom-branches` в `logs/errors.log` не должно быть строки `Failed to load plugin 'dom-branches'`.
