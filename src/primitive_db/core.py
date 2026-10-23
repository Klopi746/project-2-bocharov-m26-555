"""Procedural table management and data operations."""

from .constants import ID_COLUMN, ID_DEFINITION, VALID_TYPES
from .utils import validate_name


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
    if schema.get(ID_COLUMN) != "int":
        raise ValueError("В схеме отсутствует обязательный столбец ID:int.")
    return schema


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Add a table with ID:int, after validating its name and column types."""
    validate_name(table_name)
    if table_name in metadata:
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
            raise ValueError(f"Неподдерживаемый тип: {data_type}.")
        if name == ID_COLUMN and data_type != "int":
            raise ValueError("Столбец ID должен иметь тип int.")
        seen.add(name)
        if name != ID_COLUMN:
            definitions.append(definition)
    metadata[table_name] = [ID_DEFINITION, *definitions]
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Remove an existing table from metadata."""
    get_schema(metadata, table_name)
    del metadata[table_name]
    return metadata


def list_tables(metadata: dict) -> list[str]:
    """Return table names in creation order."""
    return list(metadata)


def insert(metadata: dict, table_name: str, values: list) -> list[dict]:
    """Validate values and add a row with an automatically generated ID."""
    raise NotImplementedError("Implement insert")


def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """Return all rows or those matching a where clause."""
    raise NotImplementedError("Implement select")


def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict]:
    """Update rows matching a where clause."""
    raise NotImplementedError("Implement update")


def delete(table_data: list[dict], where_clause: dict) -> list[dict]:
    """Delete rows matching a where clause."""
    raise NotImplementedError("Implement delete")
