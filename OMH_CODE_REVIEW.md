# Проверка OMH и выбор механизмов для DOM

Статус: статическая проверка исходников, не live-приёмка. Исследован установленный профиль default. Исходники плагинов не изменялись. Разработка DOM не запускалась.

Корень evidence: C:/Users/Arhys/AppData/Local/hermes/plugins/omh/.

## Подтверждено родительским чтением кода

| Вопрос | Наблюдение | Evidence |
|---|---|---|
| Создание плана | set строит todo record из items; session приходит из host kwargs. Нельзя задавать произвольный home при записи | tools/todo_tool.py:221–246, 248–295 |
| Ошибка входа | возвращает invalid_todo и строку error. Агрегированный предметный missing_fields в просмотренном handler отсутствует | tools/todo_tool.py:302–307 |
| Хеши | final args, destination и payload получают digest; body приватного аргумента вырезается перед фиксацией | egress_attempts.py:150–170 |
| Канонизация | JSON с ensure_ascii=True, sort_keys=True, компактными separators и allow_nan=False; не объявлять полной реализацией RFC 8785 | egress_attempts.py:27–29 |
| Атомарность egress | BEGIN IMMEDIATE, проверка identity, INSERT, commit; rollback на ошибках | egress_attempt_receipts.py:164–215 |
| Повторы | уникальность session_ref/tool_call_ref; тот же вызов с другим fingerprint отклоняется | egress_attempt_receipts.py:167–189, 352–359 |
| Хранилище egress | journal_mode=DELETE, synchronous=FULL, foreign_keys=ON | egress_attempt_receipts.py:331–359 |
| Граница гарантии egress | approval_ref и idempotency_key явно None; повтор already_recorded блокируется; tool status ok записывается как returned, не как подтверждённый внешний успех | egress_attempts.py:167–179, 200–205 |
| Checkpoint | требует accepted=True, но фиксирует acceptance=model_declared_accepted; revision/environment приходят аргументами | completion_store.py:228–260 |
| Актуальность | exact revision/environment плюс возраст; сдвиг версии делает запись stale | completion_store.py:263–276 |
| Декларации не приёмка | проекция сохраняет completion.status=not_verified даже при полном наборе положительных деклараций | completion_store.py:279–296 |
| Независимость команды | запрет board worker принимать себя; запрет известному delegated helper; host session required; import team engine может завершиться omh_team_core_unavailable | tools/team_tool.py:77–111 |

## Дополнительные выводы дочернего статического аудита

Дочерний аудит также прочитал todo_store.py, document_chunk_plan.py, team_gate.py и completion_store.py. Его выводы, не перепроверенные целиком родителем:

- todo_store использует lock + временный файл + os.replace; whole-list set читает прошлое состояние до write-lock; это не OCC всей операции.
- Инициализация todo не является импортом DOM-базы и не проверяет полноту предметных требований.
- Document plan — план чтения по страницам/символам, не импортёр фактов. Возможен не content-hash, а fallback на label/size/mtime.
- В отдельном interpreter дочернего аудитора пакет omh не обнаружен. Это не доказательство недоступности в процессе Hermes; team engine live не испытан.
- Нормализаторы todo не подходят для хранения точных исходных цитат.

## Что заимствовать и чего не обещать

Заимствовать паттерны: host-bound session и paths; валидатор; fingerprint аргументов; короткие SQLite-транзакции; unique identity; version/environment-bound evidence; раздельные состояния declaration/observation/acceptance.

Не копировать весь OMH как хранилище клаймов: строгий append-only, долговечный глобальный DOM, missing_fields[], область доступа к клаймам, expected_revision и защита от смысловой подмены нужны отдельно. Не переносить literal SHA/JSON-политику без собственного контракта формата.

Идемпотентность DOM должна быть на уровне намерения операции и payload, переживающего новую сессию/tool_call_id. Egress OMH в просмотренном пути защищает повтор конкретного host call, а не exactly-once внешнего эффекта.

## Agora: ограниченная проверка пригодности

Корень: C:/Users/Arhys/AppData/Local/hermes/plugins/agora/.

plugin.yaml описывает автономную командную разработку, motion/voting и управление задачами. Для этой задачи брать workflow нельзя — получился бы второй управляющий контур.

agora/chat.py:52–97 показывает полезный узкий паттерн: идемпотентное создание по ключу chat-root:<project_name>, получение реального task id, read-back фактического состояния. Это не пример неизменяемого журнала: там же есть UPDATE tasks и commit. Не заимствовать в DOM прямую правку статусов.

## Итог

Предпочтение: собственный небольшой слой строгого хранения/допуска, использующий OMH как владельца плана и разрешений. Заимствовать проверенные локальные паттерны, а не создавать новый оркестратор. Рекомендованный протокол в ADMISSION_AND_INTEGRITY_DESIGN.md. Работоспособность нового слоя должна быть доказана отдельным сквозным прогоном; текущие документы — не реализация.
