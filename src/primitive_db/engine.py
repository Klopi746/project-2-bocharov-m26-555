"""Interactive command loop and table-management dispatch."""

import shlex

import prompt

from . import core, utils
from .constants import APP_TITLE, HELP_TEXT, META_FILE


def print_help() -> None:
    """Show the supported commands and their syntax."""
    print(HELP_TEXT)


def execute_command(command: str) -> None:
    """Execute one table command against metadata from the working directory."""
    arguments = shlex.split(command)
    if not arguments:
        return
    action = arguments[0].lower()
    metadata = utils.load_metadata(META_FILE)
    if action == "create_table" and len(arguments) >= 2:
        table_name = arguments[1]
        core.create_table(metadata, table_name, arguments[2:])
        utils.save_table_data(table_name, [])
        utils.save_metadata(META_FILE, metadata)
        print(
            f'Таблица "{table_name}" успешно создана со столбцами: '
            + ", ".join(metadata[table_name])
        )
    elif action == "drop_table" and len(arguments) == 2:
        table_name = arguments[1]
        core.drop_table(metadata, table_name)
        utils.save_metadata(META_FILE, metadata)
        utils.remove_table_data(table_name)
        print(f'Таблица "{table_name}" успешно удалена.')
    elif action == "list_tables" and len(arguments) == 1:
        tables = core.list_tables(metadata)
        print("\n".join(f"- {name}" for name in tables) or "Таблиц пока нет.")
    else:
        raise ValueError("Некорректная команда или число аргументов. Введите help.")


def run() -> None:
    """Read commands until exit, q, EOF or a keyboard interrupt."""
    print(APP_TITLE)
    print_help()
    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command.lower() in ("exit", "q"):
            return
        if command.lower() == "help":
            print_help()
            continue
        try:
            execute_command(command)
        except (KeyError, ValueError, OSError) as error:
            print(f"Ошибка: {error}")
