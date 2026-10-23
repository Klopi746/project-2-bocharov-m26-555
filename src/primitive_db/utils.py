"""Read and atomically save table schemas and rows as UTF-8 JSON."""

import json
import os

from .constants import DATA_DIR, JSON_INDENT, TEMP_SUFFIX


def validate_name(name: str) -> None:
    """Reject empty names and names that could escape the data directory."""
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError(f"Некорректное имя: {name!r}. Используйте имя без пробелов.")


def table_path(table_name: str) -> str:
    """Return a safe relative filename for one table."""
    validate_name(table_name)
    return os.path.join(DATA_DIR, f"{table_name}.json")


def _load_json(filepath: str, empty):
    """Read JSON without treating malformed files as an empty database."""
    try:
        with open(filepath, encoding="utf-8") as source:
            return json.load(source)
    except FileNotFoundError:
        return empty


def _save_json(filepath: str, data) -> None:
    """Replace a JSON file only after the complete new content is written."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    temporary_path = filepath + TEMP_SUFFIX
    try:
        with open(temporary_path, "w", encoding="utf-8") as destination:
            json.dump(data, destination, ensure_ascii=False, indent=JSON_INDENT)
            destination.write("\n")
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary_path, filepath)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def load_metadata(filepath: str) -> dict:
    """Load table schemas; a missing file represents a new empty database."""
    metadata = _load_json(filepath, {})
    if not isinstance(metadata, dict):
        raise ValueError("Файл метаданных должен содержать JSON-объект.")
    return metadata


def save_metadata(filepath: str, data: dict) -> None:
    """Atomically save the table schemas."""
    _save_json(filepath, data)


def load_table_data(table_name: str) -> list[dict]:
    """Load rows from data/<table_name>.json, or return an empty list."""
    rows = _load_json(table_path(table_name), [])
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Файл таблицы должен содержать список JSON-объектов.")
    return rows


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Atomically save rows belonging to a validated table name."""
    _save_json(table_path(table_name), data)


def remove_table_data(table_name: str) -> None:
    """Remove the data file of a table after a confirmed drop operation."""
    try:
        os.remove(table_path(table_name))
    except FileNotFoundError:
        pass
