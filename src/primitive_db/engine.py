"""Interactive command loop, persistence and tabular output."""

import prompt
from prettytable import PrettyTable

from . import core, parser, utils
from .constants import APP_TITLE, HELP_TEXT, META_FILE


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
        print("Записей не найдено.")


def execute_data_command(arguments: dict, metadata: dict) -> None:
    """Validate and execute one CRUD or info command."""
    action = arguments["action"]
    table_name = arguments["table"]
    schema = core.get_schema(metadata, table_name)
    if action == "insert":
        rows = core.insert(metadata, table_name, arguments["values"])
        if rows is not None:
            utils.save_table_data(table_name, rows)
            print(f'Запись с ID={rows[-1]["ID"]} успешно добавлена в "{table_name}".')
        return
    rows = utils.load_table_data(table_name)
    if action == "info":
        print(f'Таблица: "{table_name}"')
        print("Столбцы: " + ", ".join(metadata[table_name]))
        print(f"Количество записей: {len(rows)}")
        return
    where_clause = arguments["where"]
    if where_clause is not None:
        core.validate_fields(schema, where_clause)
    if action == "select":
        selected = core.select(rows, where_clause)
        if selected is not None:
            print_rows(schema, selected)
        return
    if action == "update":
        core.validate_fields(schema, arguments["set"], allow_id=False)
        result = core.update(rows, arguments["set"], where_clause)
        count = sum(core.matches(row, where_clause) for row in rows)
        message = f"Записи успешно обновлены: {count}."
    else:
        result = core.delete(rows, where_clause)
        count = len(rows) - len(result) if result is not None else 0
        message = f"Записи успешно удалены: {count}."
    if result is not None:
        utils.save_table_data(table_name, result)
        print(message)


def execute_command(command: str) -> None:
    """Execute a command against database files in the working directory."""
    arguments = parser.parse_command(command)
    if not arguments:
        return
    action = arguments["action"]
    if action == "help":
        print_help()
        return
    if action in ("exit", "q"):
        return
    metadata = utils.load_metadata(META_FILE)
    if action == "create_table":
        table_name = arguments["table"]
        if core.create_table(metadata, table_name, arguments["columns"]) is None:
            return
        utils.save_table_data(table_name, [])
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
        execute_data_command(arguments, metadata)


def run() -> None:
    """Read commands until exit, q, EOF or a keyboard interrupt."""
    print(APP_TITLE)
    print_help()
    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
            if command.lower() in ("exit", "q"):
                return
            execute_command(command)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except (KeyError, ValueError, OSError) as error:
            print(f"Ошибка: {error}")
