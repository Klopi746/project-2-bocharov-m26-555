"""Parse database commands without evaluating user-supplied Python code."""

import shlex

from .constants import (
    EXIT_COMMAND,
    INVALID_VALUE_MESSAGE,
    SUPPORTED_COMMANDS,
    UNKNOWN_COMMAND_MESSAGE,
)


def tokenize(command: str) -> list[str]:
    """Split syntax outside quotes while keeping quoted literals intact."""
    tokens = []
    current = []
    quote = None
    escaped = False
    for character in command:
        if quote:
            current.append(character)
            if escaped:
                escaped = False
            elif character == "\\" and quote == '"':
                escaped = True
            elif character == quote:
                quote = None
        elif character in ("'", '"'):
            if current:
                raise ValueError("Перед строкой в кавычках нужен разделитель.")
            quote = character
            current.append(character)
        elif character.isspace() or character in "(),=":
            if current:
                tokens.append("".join(current))
                current = []
            if character in "(),=":
                tokens.append(character)
        else:
            if current and current[0] in ("'", '"'):
                raise ValueError("После строки в кавычках нужен разделитель.")
            current.append(character)
    if quote:
        raise ValueError("Не закрыта кавычка в строковом значении.")
    if current:
        tokens.append("".join(current))
    return tokens


def parse_value(token: str):
    """Convert one quoted str, integer or true/false literal."""
    if token.startswith(("'", '"')):
        values = shlex.split(token)
        if len(values) == 1:
            return values[0]
    elif token.lower() in ("true", "false"):
        return token.lower() == "true"
    elif token.lstrip("+-").isdigit() and token.lstrip("+-"):
        try:
            return int(token)
        except ValueError:
            pass
    raise ValueError(INVALID_VALUE_MESSAGE.format(value=token))


def parse_values(tokens: list[str]) -> list:
    """Read a comma-separated values (...) block, including an empty block."""
    if len(tokens) < 2 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("После values ожидается список значений в скобках.")
    values = tokens[1:-1]
    if not values:
        return []
    if len(values) % 2 == 0 or any(token != "," for token in values[1::2]):
        raise ValueError("Значения должны быть разделены запятыми.")
    return [parse_value(token) for token in values[::2]]


def parse_assignment(tokens: list[str]) -> dict:
    """Read exactly one column = value clause."""
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError("Ожидается условие: столбец = значение.")
    return {tokens[0]: parse_value(tokens[2])}


def parse_command(command: str) -> dict:
    """Return the command name, table name and typed command arguments."""
    tokens = tokenize(command)
    if not tokens:
        return {}
    action = tokens[0].lower()
    if action not in SUPPORTED_COMMANDS:
        raise ValueError(UNKNOWN_COMMAND_MESSAGE.format(command=tokens[0]))
    if action in ("help", EXIT_COMMAND, "list_tables") and len(tokens) == 1:
        return {"action": action}
    if action == "create_table" and len(tokens) >= 2:
        return {"action": action, "table": tokens[1], "columns": tokens[2:]}
    if action in ("drop_table", "info") and len(tokens) == 2:
        return {"action": action, "table": tokens[1]}
    if action == "insert" and len(tokens) >= 5:
        if tokens[1].lower() == "into" and tokens[3].lower() == "values":
            return {
                "action": action,
                "table": tokens[2],
                "values": parse_values(tokens[4:]),
            }
    if action in ("select", "delete") and len(tokens) >= 3:
        if tokens[1].lower() == "from":
            if len(tokens) == 3 and action == "select":
                return {"action": action, "table": tokens[2], "where": None}
            if len(tokens) >= 4 and tokens[3].lower() == "where":
                return {
                    "action": action,
                    "table": tokens[2],
                    "where": parse_assignment(tokens[4:]),
                }
    if action == "update" and len(tokens) == 10:
        if tokens[2].lower() == "set" and tokens[6].lower() == "where":
            return {
                "action": action,
                "table": tokens[1],
                "set": parse_assignment(tokens[3:6]),
                "where": parse_assignment(tokens[7:]),
            }
    raise ValueError(INVALID_VALUE_MESSAGE.format(value=command))
