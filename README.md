# Домашнее задание №2 — примитивная база данных

Дисциплина «Программирование на Python», группа М26-555. Это стартовый
шаблон под конечную структуру задания, а не готовое решение. Работа не сдана.

Приватный репозиторий: [GitHub](https://github.com/Klopi746/project-2-bocharov-m26-555).

## Запуск шаблона

Нужны uv и Python 3.12.10 (версия закреплена в .python-version). Из корня
проекта:

    uv sync
    uv run database
    uv run python -m primitive_db.main
    uv run ruff check .
    uv run ruff format --check .
    uv build
    uvx twine check dist/primitive_db-0.1.0.tar.gz dist/primitive_db-0.1.0-py3-none-any.whl

## Структура

- src/primitive_db/main.py — точка входа;
- src/primitive_db/engine.py — цикл команд;
- src/primitive_db/core.py — будущая логика таблиц и CRUD;
- src/primitive_db/utils.py — будущая работа с JSON-файлами;
- src/primitive_db/parser.py — будущий разбор values, where и set;
- src/primitive_db/decorators.py — будущие декораторы и кэш;
- src/primitive_db/constants.py — имена файлов, типы и другие константы.

## Что доделать вручную

1. Сохранение метаданных в db_meta.json и записей каждой таблицы в data/.
2. Создание, список и удаление таблиц с автодобавлением ID:int.
3. Команды insert, select, update, delete и info; проверка типов int, str,
   bool и генерация ID.
4. Разбор команд и условий с кавычками, вывод select через PrettyTable.
5. Декораторы handle_db_errors, confirm_action и log_time; замыкание
   create_cacher для повторных запросов.
6. Проверки поведения, Ruff, полный сценарий asciinema и ссылка на запись
   в README перед сдачей.

В проекте используются только указанные заданием сторонние библиотеки:
prompt и prettytable; Ruff находится в dev-зависимостях. Локальные
db_meta.json и data/ исключены из Git.
