from __future__ import annotations

from core import models


def generate_sample_rows(table: models.TableModel, n_rows: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for idx in range(1, n_rows + 1):
        row: list[str] = []
        for col in table.columns:
            row.append(_sample_value(col, idx))
        rows.append(row)
    return rows


def to_insert_statements(table: models.TableModel, rows: list[list[str]]) -> str:
    if not rows:
        return ""
    columns = ", ".join(col.name for col in table.columns)
    values_blocks = []
    for row in rows:
        values = ", ".join(row)
        values_blocks.append(f"({values})")
    values_sql = ",\n".join(values_blocks)
    return f"INSERT INTO {table.name} ({columns}) VALUES\n{values_sql};"


def _sample_value(col: models.ColumnModel, idx: int) -> str:
    name = col.name.lower()
    if "id" == name or name.endswith("_id"):
        return str(idx)
    if "name" in name:
        return f"'NAME_{idx}'"
    if "number" in name or "num" in name:
        return f"'NUM-{idx:03d}'"
    if "mode" in name:
        return "'AUTO'"
    return f"'VALUE_{idx}'"
