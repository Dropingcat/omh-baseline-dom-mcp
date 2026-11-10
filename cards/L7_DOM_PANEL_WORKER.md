# L7 — панель «DOM» справа в Hermes Desktop (ветки клаймов, кандидаты, готовность)

Роль WORKER. Срез небольшой и независимый. Продукт `mockup/**` меняется **только добавлением нового модуля** `mockup/overview.py`; существующие файлы продукта не править (параллельно идут другие срезы).

P=E:/opencode_harness_portable/projects/omh-baseline-dom-mcp; PY=E:/opencode_harness_portable/.venv/Scripts/python.exe; CWD=P; чистый PYTHON* env, `-I` для скриптов.

## Зачем (слова заказчика)
«отображение DOM веток клаймов справа в окне плагинов Hermes». Панель — по образцу панели ОМН: desktop-плагин + Python-backend внутри шлюза. Панель только **показывает**, ничего не пишет и не допускает.

## Что проверено оркестратором (читать как данные, перепроверить)
- Панель ОМН: `C:/Users/Arhys/AppData/Local/hermes/desktop-plugins/omh/plugin.js` (регистрация: `ctx.registerMany([{area: PANES_AREA, title, data:{placement:'right', width}, render}])`, данные через `ctx.rest('/hud')`); backend `.../plugins/omh/dashboard/plugin_api.py` + `manifest.json` `{"name","api":"plugin_api.py","tab":{"hidden":true}}`; роутер монтируется как `/api/plugins/<id>/...` **в процессе шлюза и отвечает за собственный Hermes home шлюза** (`profile` в запросе не читается). Backend подгружается, только если id есть в `plugins.enabled` конфига. Прочитать эти файлы целиком как образец.
- Правила desktop-плагина: `C:/Users/Arhys/AppData/Local/hermes/skills/general/hermes-desktop-plugins/SKILL.md` и `templates/plugin.js` (без JSX, только `jsx()`; импорты только `@hermes/plugin-sdk`, `react`, `react/jsx-runtime`; цвета только темой `var(--ui-*)`; хуки `useQuery` с `refetchInterval`, не свой цикл опроса).
- Схема БД: `mockup/storage.py` (таблицы `binding, branch_heads, candidates, reviews, transactions, claims, events, claim_snapshots, outbox, delivery_*`; схема менялась 3 раза, `PRAGMA user_version`). Живая пилотная база (read-only): `runtime/ORIENT/home/dom.sqlite3` — 2 ветки (AA ревизия 3, AB 0), 4 клайма, 4 кандидата.

## Что сделать

### 1. `mockup/overview.py` — единственная точка чтения для панели
`python -m mockup.overview --directory <run dir inside runtime/> [--branch X]` → JSON в stdout, схема `dom_overview/v1`. **Только чтение**: SQLite открывать `file:...?mode=ro` (uri), без создания файлов/WAL-записей; отсутствие базы → типизированный ответ `{"status":"NO_DATABASE"}`, не исключение. Содержимое:
- `binding` (work_ref, instance, `user_version`), `simulated`;
- `branches[]`: `branch`, `head_revision`, `claims_count`, `pending_count`, `last_tx_at`;
- `claims[]` (на ветку, лимит параметром, по умолчанию 200, с `total`): `claim_id`, `origin_branch`, `origin_version`, `content_type`, **короткий превью текста ≤160 символов** (из `raw` через безопасное декодирование; бинарное — `[binary N bytes]`), `raw_sha256`, `admitted_tx`, **`review_level`** если колонка/факт есть, иначе `null` (метка появится в L0; не выдумывать);
- `pending[]`: кандидаты не допущенные и **не отклонённые** (отклонённые — отдельным счётчиком `rejected_count`), метаданные без тела;
- `delivery`: на ветку число intent по состояниям `pending/ambiguous/ack`;
- `generated_at`, `schema_version`, `warnings[]` (например неизвестный `user_version`).
Устойчивость: неизвестная версия схемы или отсутствующая таблица → `warnings[]` + частичный ответ, не падение.

### 2. Backend `plugin/dom-branches/plugins/dom-branches/dashboard/{manifest.json,plugin_api.py}`
Образец — backend ОМН (чистые функции отдельно от роутера, `APIRouter` может отсутствовать). Маршруты `GET /overview`, `GET /branch?branch=X`. Каталог DOM берётся **из `<hermes_home>/dom-branches.json`** (`{"directory": "..."}`), потому что backend отвечает за home шлюза: у default и writer разные шлюзы и разные каталоги. Каталог обязан лежать внутри `P/runtime` (проверка resolve+is_relative_to, `..`/симлинки/абсолютные чужие — отказ). Вызывает `mockup.overview` подпроцессом `PY -I -m mockup.overview` (`PYTHONPATH=P`, таймаут 10 с, без shell), ошибки возвращает **записью с HTTP 200** (`{"error": "..."}`) — как делает ОМН.

### 3. Desktop-плагин `plugin/dom-branches/desktop-plugins/dom-branches/plugin.js`
`id: 'dom-branches'`, `defaultEnabled: false`, панель `placement: 'right'`, `title: 'dom'` (рядом с «omh»). Показывает: заголовок с work_ref и меткой `SIMULATION`, если `simulated`; дерево веток (ветка, ревизия, число клаймов, pending); раскрытие ветки → список клаймов (id коротко, тип, превью, `origin_version`, бейдж `review_level`: `self`/`independent`/`—`); блок «не завершено» (pending) с отдельным счётчиком отклонённых; строка доставки (pending/ambiguous/ack). Пустая/ошибочная база — понятное состояние (`NO_DATABASE`, `reader error`), не пустой экран. Опрос `useQuery` с `refetchInterval` не быстрее 5 с. Тексты — через `ctx.i18n.register` (ru/en), без захардкоженных цветов.

### 4. Установка — НЕ делать
Файлы собрать в `P/plugin/dom-branches/` с `INSTALL.md` (куда копировать для default и для writer; строка для `plugins.enabled`; пример `dom-branches.json`; как откатить). В Hermes home, конфиги и профили **не писать** — установку выполняет оркестратор после ревью.

## Проверки (код, не «посмотрел»)
- `overview` на копии `runtime/ORIENT/home` (копировать в `runtime/L7/`): счёт клаймов/кандидатов/веток **равен** прямому SQL-запросу; превью ≤160; тело клайма целиком не отдаётся из `pending`.
- Read-only: до/после `sha256` файла БД и отсутствие `-wal/-shm/-journal` новых; попытка записи через соединение `overview` невозможна (`mode=ro`).
- Негатив: `--directory` вне `runtime/`; `..`; симлинк наружу; отсутствующая база; повреждённая база; база с иным `user_version`; пустая база; `dom-branches.json` с чужим каталогом → отказ с записью, без исключений и без утечки путей чужих каталогов.
- Backend: чистые функции вызываются без FastAPI (импорт без него не падает); ошибка подпроцесса → `{"error"}`, 200.
- Плагин: статический разбор `plugin.js` — нет JSX, нет импортов кроме разрешённых, нет hex/rgb цветов, зона `panes`, `placement:'right'` (`node --check` если node есть; иначе парсер по запрещённым паттернам). Живую загрузку в приложении **не заявлять** — она не проверена.
- Регрессия: `pytest` проекта проходит так же, как до среза (число passed/failed до и после, продукт не менялся кроме нового файла); digest 16 файлов продукта `3cd21d96…` не изменился (новый файл не входит в digest — зафиксировать способ).

## Выходы
`artifacts/WORKER_L7.json` (`changed_files[]`, `new_files[]`, `digest_product_before/after`, `checks[]` с фактами, `not_verified[]` — как минимум «загрузка плагина в приложении», `product_acceptance=false`, `is_approval=false`), `reports/WORKER_L7.md`, `plugin/dom-branches/**`, `runtime/L7/**`.

## Границы
Не трогать: существующие файлы `mockup/**`, `tests/`, `tech_debt`, конфиги Hermes, профили, живую БД `runtime/ORIENT/home` (только копия), `runtime/WRITER`. Без Git/install/платных/сети/секретов/субагентов. Долги не закрывать. Ориентир 45 вызовов; первым — честный PARTIAL; при обрыве — continuation той же роли с точным остатком.
