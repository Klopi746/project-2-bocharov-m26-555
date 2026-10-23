"""Shared paths, supported types and console text."""

APP_TITLE = "***Примитивная база данных***"
META_FILE = "db_meta.json"
DATA_DIR = "data"
VALID_TYPES = ("int", "str", "bool")
TYPE_CLASSES = {"int": int, "str": str, "bool": bool}
ID_COLUMN = "ID"
ID_DEFINITION = "ID:int"
JSON_INDENT = 2
TEMP_SUFFIX = ".tmp"
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
  exit или q                          — выход
Поддерживаемые типы: int, str, bool. Строки вводите в кавычках.
Пример: insert into users values ("Сергей", 28, true)"""
