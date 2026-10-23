"""Error handling, confirmation, timing decorators and a closure-based cache."""

import time

import prompt

from .constants import CONFIRMATION_ANSWER, INPUT_ERROR_PREFIXES


def _preserve_metadata(wrapper, function):
    """Keep function identity without importing another runtime library."""
    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    wrapper.__wrapped__ = function
    return wrapper


def handle_db_errors(function):
    """Report expected database errors and return None on failure."""

    def wrapper(*args, **kwargs):
        """Call the function without terminating the command loop on errors."""
        try:
            return function(*args, **kwargs)
        except (KeyError, ValueError, OSError) as error:
            message = (
                str(error.args[0])
                if isinstance(error, KeyError) and error.args
                else str(error)
            )
            if message.startswith(INPUT_ERROR_PREFIXES):
                print(message)
            else:
                print(f"Ошибка: {message}")
            return None

    return _preserve_metadata(wrapper, function)


def confirm_action(action_name: str):
    """Require an explicit y before a destructive operation."""

    def decorator(function):
        """Wrap an operation with its confirmation question."""

        def wrapper(*args, **kwargs):
            """Run only the confirmed operation, returning None on cancellation."""
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ',
                empty=True,
            )
            if answer != CONFIRMATION_ANSWER:
                print("Операция отменена.")
                return None
            return function(*args, **kwargs)

        return _preserve_metadata(wrapper, function)

    return decorator


def log_time(function):
    """Measure an operation with a monotonic clock, including failed calls."""

    def wrapper(*args, **kwargs):
        """Print elapsed seconds and preserve the wrapped result."""
        started = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(f"Функция {function.__name__} выполнилась за {elapsed:.3f} секунд")

    return _preserve_metadata(wrapper, function)


def create_cacher():
    """Return cache_result(key, value_func) with private storage in a closure."""
    cache = {}

    def cache_result(key, value_func):
        """Reuse a successful result, calling value_func only on a cache miss."""
        if key in cache:
            print("Результат получен из кэша.")
            return cache[key]
        result = value_func()
        if result is not None:
            cache[key] = result
        return result

    return cache_result
