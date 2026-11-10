# WORKER_L7 — панель «dom» (DONE_WITH_NOTES)

product_acceptance=false, is_approval=false. Установка в Hermes home НЕ выполнялась.

## Сделано
- `mockup/overview.py` (единственный новый файл продукта): `python -m mockup.overview --directory <dir in runtime/> [--branch X] [--limit N]` → `dom_overview/v1`. `mode=ro` + `query_only`, typed-статусы `OK/NO_DATABASE/EMPTY_DATABASE/READER_ERROR/DIRECTORY_REFUSED/INVALID_ARGUMENT`, никогда не бросает.
- Backend `plugin/dom-branches/plugins/dom-branches/dashboard/{manifest.json,plugin_api.py}`: `GET /overview`, `GET /branch?branch=X`; каталог из `<home>/dom-branches.json`, внутри `P/runtime`; подпроцесс без shell, 10 с; ошибки — запись `{error}` с HTTP 200.
- Desktop `plugin/dom-branches/desktop-plugins/dom-branches/plugin.js`: панель `dom` справа, SIMULATION, дерево веток → клаймы (бейдж review_level `self/independent/—`), «Не завершено» + отдельно «Отклонено», строка доставки, состояния NO_DATABASE/reader error, `useQuery` 5 с, i18n ru/en, цвета только `var(--…)`.
- `plugin/dom-branches/INSTALL.md` (default и writer, plugins.enabled, пример dom-branches.json, откат).

## Проверки (72, не прошли: [])
Подробно `artifacts/WORKER_L7.json` → `checks[]`; скрипты `runtime/L7/probes/`.
- Копия ORIENT (`runtime/L7/home`): 2 ветки, 4 клайма (AA=4, AB=0), pending=1, rejected=0 — равно прямому SQL; превью ≤160 (макс. 160); из pending нет тела (ключи без payload).
- Read-only: sha256 БД и состав каталога до/после совпали (`3f94533b…`), INSERT/CREATE/DELETE/PRAGMA user_version через соединение overview → `attempt to write a readonly database`. Живая ORIENT не менялась.
- Негативы (в т.ч. через CLI, rc=0): вне runtime, корень проекта, `..`, symlink наружу, symlink dom.sqlite3 наружу, нет БД/каталога, битая БД, пустая, user_version=7 (warning), частичные таблицы, неизвестная/невалидная ветка; backend: чужой/`..`/относительный/ссылка/неверный тип/нет файла/битый JSON/нет python/таймаут/exit≠0 → запись `error`, без путей чужих каталогов.
- Backend без FastAPI импортируется; router через FastAPI TestClient (venv Hermes) — 200 на всех маршрутах.
- plugin.js: `node --check` ок; только 3 разрешённых импорта; нет JSX/hex/rgb; зона `panes`, `placement:'right'`; node-прогон `register()` с заглушками SDK.
- Регрессия: pytest до `3 failed, 61 passed`, после `3 failed, 61 passed` (те же 3 падения уже были до среза); digest 16 файлов `3cd21d96…` не изменился (overview.py исключён из подсчёта — метод в json).

## Отклонения от карты
- Backend runs `PY -I -B -c <bootstrap with sys.path.insert(P)> --directory ...` instead of `PY -I -m mockup.overview` + PYTHONPATH: -I makes the interpreter ignore PYTHONPATH and cwd, so the literal form cannot import mockup. Isolation intent (no user site, no PYTHON* env, no bytecode) preserved; PYTHONPATH=P is still set but inert.
- binding has no `instance` column; `instance` = run dir relative to runtime/ (e.g. L7/home); `policy_prefix` (12 chars) added.
- `simulated` is not stored as a column; derived from transaction receipts (all simulated=true -> true), default true when no receipt evidence (simulated_source says which).
- last_tx_at taken from the first event payload server_time of the branch's latest transaction (transactions has no time column); null if absent.
- claims[] is a flat list with a `branch` field, up to `limit` (default 200) PER branch; claims_count is the exact total per branch.
- A DB with no tables (zero-byte or fresh sqlite) returns status EMPTY_DATABASE; corrupt -> READER_ERROR; refused dir -> DIRECTORY_REFUSED (all with an `error` text without paths for the last two where applicable).

## Не проверено
- load/render of plugin.js in the Hermes Desktop app (Reload desktop plugins, pane appears right of omh, visual layout)
- mounting of the backend router by the real running gateway (only TestClient + pure functions checked)
- plugin id dom-branches in plugins.enabled and plugin dir without plugin.yaml/__init__.py being accepted by the host loader beyond dashboard discovery (code read in _discover_dashboard_plugins only)
- review_level badge with real data (no column exists yet; only null path and the shim levelView tested)
- delivery ack counting uses delivery_acks+matched observation structure, not delivery.confirmed() fingerprint/evidence re-verification
- writer profile install (no writer run dir chosen; INSTALL.md has a placeholder)
