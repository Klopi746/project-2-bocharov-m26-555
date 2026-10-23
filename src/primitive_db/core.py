"""Procedural table management and data operations."""

from .constants import (
    ID_COLUMN,
    ID_DEFINITION,
    INVALID_VALUE_MESSAGE,
    TYPE_CLASSES,
    TYPE_INT,
    VALID_TYPES,
)
from .decorators import confirm_action, handle_db_errors, log_time
from .utils import load_table_data, table_storage_key, validate_name


def get_schema(metadata: dict, table_name: str) -> dict[str, str]:
    """Return ordered column types, rejecting missing or malformed schemas."""
    validate_name(table_name)
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    columns = metadata[table_name]
    if not isinstance(columns, list):
        raise ValueError(f'Некорректная схема таблицы "{table_name}".')
    schema = {}
    for definition in columns:
        if not isinstance(definition, str) or definition.count(":") != 1:
            raise ValueError(f"Некорректное описание столбца: {definition!r}.")
        name, data_type = definition.split(":")
        validate_name(name)
        if name in schema or data_type not in VALID_TYPES:
            raise ValueError(f"Повторяющийся столбец или неверный тип: {definition}.")
        schema[name] = data_type
    if schema.get(ID_COLUMN) != TYPE_INT:
        raise ValueError(f"В схеме отсутствует обязательный столбец {ID_DEFINITION}.")
    return schema


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Add a table with ID:int, after validating its name and column types."""
    validate_name(table_name)
    storage_key = table_storage_key(table_name)
    if any(table_storage_key(name) == storage_key for name in metadata):
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    definitions = []
    seen = set()
    for definition in columns:
        if not isinstance(definition, str) or definition.count(":") != 1:
            raise ValueError(f"Ожидается столбец:тип, получено {definition!r}.")
        name, data_type = definition.split(":")
        validate_name(name)
        if name in seen:
            raise ValueError(f'Столбец "{name}" указан несколько раз.')
        if data_type not in VALID_TYPES:
            raise ValueError(INVALID_VALUE_MESSAGE.format(value=data_type))
        if name == ID_COLUMN and data_type != TYPE_INT:
            raise ValueError(f"Столбец {ID_COLUMN} должен иметь тип {TYPE_INT}.")
        seen.add(name)
        if name != ID_COLUMN:
            definitions.append(definition)
    metadata[table_name] = [ID_DEFINITION, *definitions]
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Remove an existing table from metadata."""
    get_schema(metadata, table_name)
    del metadata[table_name]
    return metadata


@handle_db_errors
def list_tables(metadata: dict) -> list[str]:
    """Return table names in creation order."""
    return list(metadata)


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list) -> list[dict]:
    """Validate values and add a row with an automatically generated ID."""
    schema = get_schema(metadata, table_name)
    columns = [name for name in schema if name != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(f"Ожидается {len(columns)} значений, получено {len(values)}.")
    fields = dict(zip(columns, values))
    validate_fields(schema, fields, allow_id=False)
    table_data = load_table_data(table_name)
    identifiers = [row[ID_COLUMN] for row in table_data]
    if any(type(value) is not int or value < 1 for value in identifiers):
        raise ValueError("Существующие ID должны быть положительными целыми числами.")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("В таблице повторяются ID.")
    new_id = max(identifiers, default=0) + 1
    return [*table_data, {ID_COLUMN: new_id, **fields}]


def validate_fields(schema: dict, fields: dict, *, allow_id: bool = True) -> None:
    """Check column names and exact types, keeping bool distinct from int."""
    for name, value in fields.items():
        if name not in schema:
            raise KeyError(f'Столбец "{name}" не существует.')
        if name == ID_COLUMN and not allow_id:
            raise ValueError("ID создаётся автоматически и не может быть изменён.")
        if type(value) is not TYPE_CLASSES[schema[name]]:
            raise ValueError(INVALID_VALUE_MESSAGE.format(value=value))


def _validate_row_clause(table_data: list[dict], clause: dict) -> None:
    """Validate a clause against existing rows before performing any changes."""
    if not clause:
        raise ValueError("Условие не должно быть пустым.")
    for row in table_data:
        for name, value in clause.items():
            if name not in row:
                raise KeyError(f'Столбец "{name}" не существует.')
            if type(row[name]) is not type(value):
                raise ValueError(f'Неверный тип значения для столбца "{name}".')


def matches(row: dict, where_clause: dict) -> bool:
    """Compare fields with exact types rather than treating True as 1."""
    return all(
        type(row[name]) is type(value) and row[name] == value
        for name, value in where_clause.items()
    )


@handle_db_errors
@log_time
def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """Return all rows or those matching a where clause."""
    if where_clause is None:
        return [row.copy() for row in table_data]
    _validate_row_clause(table_data, where_clause)
    return [row.copy() for row in table_data if matches(row, where_clause)]


@handle_db_errors
def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict]:
    """Update rows matching a where clause."""
    if ID_COLUMN in set_clause:
        raise ValueError("ID создаётся автоматически и не может быть изменён.")
    _validate_row_clause(table_data, set_clause)
    _validate_row_clause(table_data, where_clause)
    return [
        {**row, **set_clause} if matches(row, where_clause) else row.copy()
        for row in table_data
    ]


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list[dict], where_clause: dict) -> list[dict]:
    """Delete rows matching a where clause."""
    _validate_row_clause(table_data, where_clause)
    return [row.copy() for row in table_data if not matches(row, where_clause)]
