"""JSON persistence helpers to implement in this homework."""


def load_metadata(filepath: str) -> dict:
    """Load table schemas or return an empty dict when the file is absent."""
    raise NotImplementedError("Implement load_metadata")


def save_metadata(filepath: str, data: dict) -> None:
    """Save table schemas to a JSON file."""
    raise NotImplementedError("Implement save_metadata")


def load_table_data(table_name: str) -> list[dict]:
    """Load rows for one table from data/<table_name>.json."""
    raise NotImplementedError("Implement load_table_data")


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Save rows for one table to data/<table_name>.json."""
    raise NotImplementedError("Implement save_table_data")
