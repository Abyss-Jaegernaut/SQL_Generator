from __future__ import annotations

from core import models, rules


def build_create_table(table: models.TableModel) -> str:
    parts: list[str] = []
    for col in table.columns:
        null_clause = "NOT NULL" if not col.nullable else "NULL"
        identity = " IDENTITY(1,1)" if col.is_primary_key and col.is_auto_increment else ""
        pk = " PRIMARY KEY" if col.is_primary_key else ""
        parts.append(f"    {col.name} {col.sql_type}{identity} {null_clause}{pk}")
    columns_sql = ",\n".join(parts)
    return f"CREATE TABLE {table.name}\n(\n{columns_sql}\n);\nGO"


def build_proc_insert(table: models.TableModel) -> str:
    proc_name = rules.procedure_name(table.name, "Insert")
    include_pk = not _pk_auto_increment(table)
    parameters = _format_parameters(table, include_pk=include_pk)
    columns = ", ".join(_column_names(table, include_pk=include_pk))
    values = ", ".join(_value_references(table, include_pk=include_pk))
    return (
        f"CREATE PROCEDURE {proc_name}\n"
        f"{parameters}\n"
        "AS\n"
        "BEGIN\n"
        f"    INSERT INTO {table.name} ({columns})\n"
        f"    VALUES ({values});\n"
        "END\n"
        "GO"
    )


def build_proc_get_by_id(table: models.TableModel) -> str:
    proc_name = rules.procedure_name(table.name, "GetById")
    pk = table.primary_keys[0]
    return (
        f"CREATE PROCEDURE {proc_name}\n"
        f"    @{pk.name} {pk.sql_type}\n"
        "AS\n"
        "BEGIN\n"
        f"    SELECT * FROM {table.name} WHERE {pk.name} = @{pk.name};\n"
        "END\n"
        "GO"
    )


def build_proc_select_all(table: models.TableModel) -> str:
    proc_name = rules.procedure_name(table.name, "SelectAll")
    return (
        f"CREATE PROCEDURE {proc_name}\n"
        "AS\n"
        "BEGIN\n"
        f"    SELECT * FROM {table.name};\n"
        "END\n"
        "GO"
    )


def build_proc_update(table: models.TableModel) -> str:
    proc_name = rules.procedure_name(table.name, "Update")
    parameters = _format_parameters(table, include_pk=True)
    set_clause = ", ".join(
        f"{col.name} = @{col.name}" for col in table.columns if not col.is_primary_key
    )
    pk = table.primary_keys[0]
    return (
        f"CREATE PROCEDURE {proc_name}\n"
        f"{parameters}\n"
        "AS\n"
        "BEGIN\n"
        f"    UPDATE {table.name}\n"
        f"    SET {set_clause}\n"
        f"    WHERE {pk.name} = @{pk.name};\n"
        "END\n"
        "GO"
    )


def build_proc_delete(table: models.TableModel) -> str:
    proc_name = rules.procedure_name(table.name, "Delete")
    pk = table.primary_keys[0]
    return (
        f"CREATE PROCEDURE {proc_name}\n"
        f"    @{pk.name} {pk.sql_type}\n"
        "AS\n"
        "BEGIN\n"
        f"    DELETE FROM {table.name} WHERE {pk.name} = @{pk.name};\n"
        "END\n"
        "GO"
    )


def _format_parameters(table: models.TableModel, *, include_pk: bool) -> str:
    params = []
    for col in table.columns:
        if not include_pk and col.is_primary_key:
            continue
        params.append(f"    @{col.name} {col.sql_type}")
    if not params:
        return ""
    # SQL Server: params separated by comma except last line is fine too; we format with commas.
    if len(params) == 1:
        return params[0]
    return ",\n".join(params)


def _column_names(table: models.TableModel, *, include_pk: bool) -> list[str]:
    return [
        col.name
        for col in table.columns
        if include_pk or not col.is_primary_key
    ]


def _value_references(table: models.TableModel, *, include_pk: bool) -> list[str]:
    return [
        f"@{col.name}"
        for col in table.columns
        if include_pk or not col.is_primary_key
    ]


def _pk_auto_increment(table: models.TableModel) -> bool:
    if not table.primary_keys:
        return False
    pk = table.primary_keys[0]
    return pk.is_auto_increment
