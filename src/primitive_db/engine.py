"""Command loop; table and CRUD dispatch belong here later."""

import prompt

from .constants import APP_TITLE


def print_help() -> None:
    """Show the commands currently available in the starter."""
    print("Команды: help — справка, exit — выход.")
    print("Команды базы данных пока не реализованы.")


def run() -> None:
    """Run the starter console until the user exits."""
    print(APP_TITLE)
    print_help()
    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command == "exit":
            return
        if command == "help":
            print_help()
        else:
            print("Команда пока не реализована. Введите help или exit.")
