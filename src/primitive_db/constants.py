"""Shared paths, supported types and console text."""

APP_TITLE = "***Примитивная база данных***"
META_FILE = "db_meta.json"
DATA_DIR = "data"
TYPE_INT = "int"
TYPE_STR = "str"
TYPE_BOOL = "bool"
VALID_TYPES = (TYPE_INT, TYPE_STR, TYPE_BOOL)
TYPE_CLASSES = {TYPE_INT: int, TYPE_STR: str, TYPE_BOOL: bool}
ID_COLUMN = "ID"
ID_DEFINITION = f"{ID_COLUMN}:{TYPE_INT}"
JSON_SUFFIX = ".json"
JSON_INDENT = 2
TEMP_SUFFIX = ".tmp"
EXIT_COMMAND = "exit"
CONFIRMATION_ANSWER = "y"
SUPPORTED_COMMANDS = (
    "create_table",
    "list_tables",
    "drop_table",
    "insert",
    "select",
    "update",
    "delete",
    "info",
    "help",
    EXIT_COMMAND,
)
UNKNOWN_COMMAND_MESSAGE = "Функции {command} нет. Попробуйте снова."
INVALID_VALUE_MESSAGE = "Некорректное значение: {value}. Попробуйте снова."
INPUT_ERROR_PREFIXES = ("Функции ", "Некорректное значение: ")
NO_MATCHING_ROWS_MESSAGE = "Записей не найдено."
INSERT_SUCCESS_MESSAGE = (
    'Запись с ID={identifier} успешно добавлена в таблицу "{table_name}".'
)
UPDATE_SUCCESS_MESSAGE = (
    'Запись с ID={identifier} в таблице "{table_name}" успешно обновлена.'
)
DELETE_SUCCESS_MESSAGE = (
    'Запись с ID={identifier} успешно удалена из таблицы "{table_name}".'
)
HELP_TEXT = """Команды:
  create_table <имя> <столбец:тип> ... — создать таблицу
  list_tables                         — показать список таблиц
  drop_table <имя>                     — удалить таблицу
  insert into <имя> values (...)       — добавить запись без ID
  select from <имя> [where поле = значение]
  update <имя> set поле = значение where поле = значение
  delete from <имя> where поле = значение
  info <имя>                          — схема и число записей
  help                                — справка
  exit                                — выход
Поддерживаемые типы: int, str, bool. Строки вводите в кавычках.
Пример: insert into users values ("Сергей", 28, true)"""
