"""Interactive command loop, persistence and tabular output."""

import json

import prompt
from prettytable import PrettyTable

from . import core, parser, utils
from .constants import (
    APP_TITLE,
    DELETE_SUCCESS_MESSAGE,
    EXIT_COMMAND,
    HELP_TEXT,
    ID_COLUMN,
    INSERT_SUCCESS_MESSAGE,
    META_FILE,
    NO_MATCHING_ROWS_MESSAGE,
    UPDATE_SUCCESS_MESSAGE,
)
from .decorators import create_cacher, handle_db_errors


def print_help() -> None:
    """Show the supported commands and their syntax."""
    print(HELP_TEXT)


def print_rows(schema: dict, rows: list[dict]) -> None:
    """Display rows in schema order, including headers for an empty result."""
    table = PrettyTable()
    table.field_names = list(schema)
    for row in rows:
        table.add_row([row[name] for name in schema])
    print(table)
    if not rows:
        print(NO_MATCHING_ROWS_MESSAGE)


def print_change_messages(action: str, table_name: str, identifiers: list[int]) -> None:
    """Report each changed record using the assignment's console messages."""
    template = UPDATE_SUCCESS_MESSAGE if action == "update" else DELETE_SUCCESS_MESSAGE
    if not identifiers:
        print(NO_MATCHING_ROWS_MESSAGE)
    for identifier in identifiers:
        print(template.format(identifier=identifier, table_name=table_name))


def execute_data_command(arguments: dict, metadata: dict, cache_result) -> None:
    """Validate and execute one CRUD or info command."""
    action = arguments["action"]
    table_name = arguments["table"]
    schema = core.get_schema(metadata, table_name)
    if action == "insert":
        rows = core.insert(metadata, table_name, arguments["values"])
        if rows is not None:
            utils.save_table_data(table_name, rows)
            print(
                INSERT_SUCCESS_MESSAGE.format(
                    identifier=rows[-1][ID_COLUMN], table_name=table_name
                )
            )
        return
    rows = utils.load_table_data(table_name)
    if action == "info":
        print(f"Таблица: {table_name}")
        print("Столбцы: " + ", ".join(metadata[table_name]))
        print(f"Количество записей: {len(rows)}")
        return
    where_clause = arguments["where"]
    if where_clause is not None:
        core.validate_fields(schema, where_clause)
    if action == "select":
        key = json.dumps(
            [table_name, schema, rows, where_clause],
            ensure_ascii=False,
            sort_keys=True,
        )
        selected = cache_result(key, lambda: core.select(rows, where_clause))
        if selected is not None:
            print_rows(schema, selected)
        return
    if action == "update":
        core.validate_fields(schema, arguments["set"], allow_id=False)
        result = core.update(rows, arguments["set"], where_clause)
    else:
        result = core.delete(rows, where_clause)
    if result is not None:
        utils.save_table_data(table_name, result)
        identifiers = [
            row[ID_COLUMN] for row in rows if core.matches(row, where_clause)
        ]
        print_change_messages(action, table_name, identifiers)


@handle_db_errors
def execute_command(command: str, cache_result=None) -> None:
    """Execute a command against database files in the working directory."""
    arguments = parser.parse_command(command)
    if not arguments:
        return
    action = arguments["action"]
    if action == "help":
        print_help()
        return
    if action == EXIT_COMMAND:
        return
    metadata = utils.load_metadata(META_FILE)
    if action == "create_table":
        table_name = arguments["table"]
        if core.create_table(metadata, table_name, arguments["columns"]) is None:
            return
        utils.create_table_data(table_name)
        utils.save_metadata(META_FILE, metadata)
        print(
            f'Таблица "{table_name}" успешно создана со столбцами: '
            + ", ".join(metadata[table_name])
        )
    elif action == "drop_table":
        table_name = arguments["table"]
        if core.drop_table(metadata, table_name) is None:
            return
        utils.save_metadata(META_FILE, metadata)
        utils.remove_table_data(table_name)
        print(f'Таблица "{table_name}" успешно удалена.')
    elif action == "list_tables":
        tables = core.list_tables(metadata)
        print("\n".join(f"- {name}" for name in tables) or "Таблиц пока нет.")
    else:
        execute_data_command(arguments, metadata, cache_result or create_cacher())


def run() -> None:
    """Read commands until exit, EOF or a keyboard interrupt."""
    print(APP_TITLE)
    print_help()
    cache_result = create_cacher()
    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
            if command.lower() == EXIT_COMMAND:
                return
            execute_command(command, cache_result)
        except (EOFError, KeyboardInterrupt):
            print()
            return
