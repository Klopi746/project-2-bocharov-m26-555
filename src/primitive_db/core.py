"""Table management and CRUD operations to implement in this homework."""


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Add a table with ID:int, after validating its name and column types."""
    raise NotImplementedError("Implement create_table as your next step")


def drop_table(metadata: dict, table_name: str) -> dict:
    """Remove an existing table from metadata."""
    raise NotImplementedError("Implement drop_table")


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
