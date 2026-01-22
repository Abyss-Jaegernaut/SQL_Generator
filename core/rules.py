"""Central place for naming and CRUD rules."""

CRUD_ACTIONS = ["Insert", "GetById", "SelectAll", "Update", "Delete"]
PROC_PREFIX = "SPX"


def procedure_name(table_name: str, action: str) -> str:
    """Return the canonical stored procedure name."""
    return f"{PROC_PREFIX}_{table_name}_{action}"
