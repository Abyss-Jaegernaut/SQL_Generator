"""DBMS-specific SQL builders for SQL Server, MySQL, and PostgreSQL."""
from __future__ import annotations

from core import models, rules


def format_value(value: str, sql_type: str, dbms: str) -> str:
    """Format a value for use in an INSERT statement based on its type."""
    if value is None or value.upper() == "NULL" or value == "(AUTO)":
        return "NULL"
    
    t = sql_type.upper()
    should_quote = any(kw in t for kw in ["CHAR", "TEXT", "DATE", "TIME", "TIMESTAMP", "UUID", "BOOLEAN", "BIT"])
    
    if should_quote:
        # Simple escaping: replace single quote with two single quotes
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
    
    return str(value)


def normalize_dbms_name(dbms: str) -> str:
    """Normalize DBMS name from display format to internal format."""
    dbms_map = {
        "SQL Server": "sqlserver",
        "MySQL": "mysql",
        "PostgreSQL": "postgresql",
        # Also handle already-normalized names for backward compatibility
        "sqlserver": "sqlserver",
        "mysql": "mysql",
        "postgresql": "postgresql"
    }
    return dbms_map.get(dbms, "sqlserver")


def build_database_header(db_name: str, dbms: str) -> str:
    """Generate CREATE DATABASE + USE statements based on DBMS."""
    if not db_name.strip():
        return ""
    
    dbms = normalize_dbms_name(dbms)
    
    if dbms == "sqlserver":
        return f"""IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{db_name}')
BEGIN
    CREATE DATABASE [{db_name}];
END
GO

USE [{db_name}];
GO"""
    
    elif dbms == "mysql":
        return f"""CREATE DATABASE IF NOT EXISTS `{db_name}`;
USE `{db_name}`;"""
    
    elif dbms == "postgresql":
        # PostgreSQL doesn't have IF NOT EXISTS for CREATE DATABASE in standard SQL
        # and you can't CREATE DATABASE in a transaction, so we'll use a comment
        return f"""-- Run this command if database doesn't exist:
-- CREATE DATABASE "{db_name}";

\\c {db_name};"""
    
    return ""


def build_create_table_statement(table: models.TableModel, dbms: str) -> str:
    """Generate CREATE TABLE statement based on DBMS."""
    dbms = normalize_dbms_name(dbms)
    
    if not table.columns:
        return f"-- Table {table.name} has no columns"
    
    lines = []
    for col in table.columns:
        col_def = _build_column_def(col, dbms)
        lines.append(f"    {col_def}")
    
    # Table name quoting
    table_name = _quote_identifier(table.name, dbms)
    
    columns_sql = ",\n".join(lines)
    
    if dbms == "sqlserver":
        return f"CREATE TABLE {table_name} (\n{columns_sql}\n);\nGO"
    else:
        return f"CREATE TABLE IF NOT EXISTS {table_name} (\n{columns_sql}\n);"


def _build_column_def(col: models.ColumnModel, dbms: str) -> str:
    """Build a single column definition."""
    dbms = normalize_dbms_name(dbms)
    col_name = _quote_identifier(col.name, dbms)
    
    # Map type
    sql_type = _map_data_type(col.sql_type, dbms)
    
    # Handle AUTO_INCREMENT/IDENTITY/SERIAL or AUTO-DATETIME
    if col.is_auto_increment:
        if "INT" in sql_type.upper() or "SERIAL" in sql_type.upper():
            if dbms == "sqlserver":
                parts = [col_name, sql_type, "IDENTITY(1,1)"]
            elif dbms == "mysql":
                parts = [col_name, sql_type, "AUTO_INCREMENT"]
            elif dbms == "postgresql":
                if "BIG" in sql_type.upper():
                    parts = [col_name, "BIGSERIAL"]
                else:
                    parts = [col_name, "SERIAL"]
            
            if col.is_primary_key:
                parts.append("PRIMARY KEY")
        
        elif "DATE" in sql_type.upper() or "TIME" in sql_type.upper():
            # Auto-populating date types
            default_val = "CURRENT_TIMESTAMP" # Default for MySQL/Postgres
            if dbms == "sqlserver":
                default_val = "GETDATE()"
            
            parts = [col_name, sql_type, f"DEFAULT {default_val}"]
            if col.is_primary_key:
                parts.append("PRIMARY KEY")
        else:
            # Fallback for other types
            parts = [col_name, sql_type]
            if col.is_primary_key:
                parts.append("PRIMARY KEY")
    else:
        parts = [col_name, sql_type]
        
        if col.is_primary_key:
            parts.append("PRIMARY KEY")
        
        if not col.nullable and not col.is_primary_key:
            parts.append("NOT NULL")
    
    return " ".join(parts)


def _map_data_type(sql_type: str, dbms: str) -> str:
    """Map generic SQL types to DBMS-specific types."""
    sql_type_upper = sql_type.upper()
    
    # Most types are compatible, but handle special cases
    if dbms == "mysql":
        # MySQL uses DATETIME instead of DATETIME2, TEXT instead of VARCHAR(MAX)
        if "VARCHAR(MAX)" in sql_type_upper:
            return "TEXT"
        if "DATETIME2" in sql_type_upper:
            return "DATETIME"
    
    elif dbms == "postgresql":
        # PostgreSQL uses specific types
        if "VARCHAR(MAX)" in sql_type_upper:
            return "TEXT"
        if "DATETIME" in sql_type_upper or "DATETIME2" in sql_type_upper:
            return "TIMESTAMP"
        if sql_type_upper == "BIT":
            return "BOOLEAN"
    
    return sql_type


def _quote_identifier(name: str, dbms: str) -> str:
    """Quote identifier based on DBMS."""
    dbms = normalize_dbms_name(dbms)
    if dbms == "sqlserver":
        return f"[{name}]"
    elif dbms == "mysql":
        return f"`{name}`"
    elif dbms == "postgresql":
        return f'"{name}"'
    return name


def get_statement_terminator(dbms: str) -> str:
    """Get the statement terminator for the DBMS."""
    dbms = normalize_dbms_name(dbms)
    if dbms == "sqlserver":
        return "\nGO"
    else:
        return ""


def build_crud_procedures(table: models.TableModel, dbms: str, actions: list[str]) -> list[str]:
    """Generate requested CRUD procedures for the given table and DBMS."""
    dbms = normalize_dbms_name(dbms)
    blocks = []
    
    if "Insert" in actions:
        blocks.append(_build_proc_insert(table, dbms))
    if "GetById" in actions:
        blocks.append(_build_proc_get_by_id(table, dbms))
    if "SelectAll" in actions:
        blocks.append(_build_proc_select_all(table, dbms))
    if "Update" in actions:
        blocks.append(_build_proc_update(table, dbms))
    if "Delete" in actions:
        blocks.append(_build_proc_delete(table, dbms))
        
    return blocks


def _build_proc_insert(table: models.TableModel, dbms: str) -> str:
    proc_name = rules.procedure_name(table.name, "Insert")
    pk_auto = any(c.is_auto_increment for c in table.primary_keys)
    cols = [c for c in table.columns if not (c.is_primary_key and pk_auto)]
    
    col_names = ", ".join([_quote_identifier(c.name, dbms) for c in cols])
    
    if dbms == "sqlserver":
        params = ",\n".join([f"    @{c.name} {_map_data_type(c.sql_type, dbms)}" for c in cols])
        vals = ", ".join([f"@{c.name}" for c in cols])
        return f"CREATE PROCEDURE {proc_name}\n{params}\nAS\nBEGIN\n    INSERT INTO {_quote_identifier(table.name, dbms)} ({col_names})\n    VALUES ({vals});\nEND\nGO"
    
    elif dbms == "mysql":
        params = ",\n".join([f"    IN p_{c.name} {_map_data_type(c.sql_type, dbms)}" for c in cols])
        vals = ", ".join([f"p_{c.name}" for c in cols])
        return f"CREATE PROCEDURE {proc_name}(\n{params}\n)\nBEGIN\n    INSERT INTO {_quote_identifier(table.name, dbms)} ({col_names})\n    VALUES ({vals});\nEND;"
    
    elif dbms == "postgresql":
        params = ",\n".join([f"    p_{c.name} {_map_data_type(c.sql_type, dbms)}" for c in cols])
        vals = ", ".join([f"p_{c.name}" for c in cols])
        return f"CREATE OR REPLACE PROCEDURE {proc_name}(\n{params}\n)\nLANGUAGE plpgsql\nAS $$\nBEGIN\n    INSERT INTO {_quote_identifier(table.name, dbms)} ({col_names})\n    VALUES ({vals});\nEND;\n$$;"
    
    return f"-- Insert procedure for {dbms} not implemented"


def _build_proc_get_by_id(table: models.TableModel, dbms: str) -> str:
    proc_name = rules.procedure_name(table.name, "GetById")
    if not table.primary_keys: return ""
    pk = table.primary_keys[0]
    
    if dbms == "sqlserver":
        return f"CREATE PROCEDURE {proc_name}\n    @{pk.name} {_map_data_type(pk.sql_type, dbms)}\nAS\nBEGIN\n    SELECT * FROM {_quote_identifier(table.name, dbms)} WHERE {_quote_identifier(pk.name, dbms)} = @{pk.name};\nEND\nGO"
    
    elif dbms == "mysql":
        return f"CREATE PROCEDURE {proc_name}(\n    IN p_{pk.name} {_map_data_type(pk.sql_type, dbms)}\n)\nBEGIN\n    SELECT * FROM {_quote_identifier(table.name, dbms)} WHERE {_quote_identifier(pk.name, dbms)} = p_{pk.name};\nEND;"
    
    elif dbms == "postgresql":
        # In Postgres, functions are often preferred for SELECTs
        return f"CREATE OR REPLACE FUNCTION {proc_name}(p_{pk.name} {_map_data_type(pk.sql_type, dbms)})\nRETURNS SETOF {_quote_identifier(table.name, dbms)}\nLANGUAGE sql\nAS $$\n    SELECT * FROM {_quote_identifier(table.name, dbms)} WHERE {_quote_identifier(pk.name, dbms)} = p_{pk.name};\n$$;"
    
    return f"-- GetById procedure for {dbms} not implemented"


def _build_proc_select_all(table: models.TableModel, dbms: str) -> str:
    proc_name = rules.procedure_name(table.name, "SelectAll")
    
    if dbms == "sqlserver":
        return f"CREATE PROCEDURE {proc_name}\nAS\nBEGIN\n    SELECT * FROM {_quote_identifier(table.name, dbms)};\nEND\nGO"
    
    elif dbms == "mysql":
        return f"CREATE PROCEDURE {proc_name}()\nBEGIN\n    SELECT * FROM {_quote_identifier(table.name, dbms)};\nEND;"
    
    elif dbms == "postgresql":
        return f"CREATE OR REPLACE FUNCTION {proc_name}()\nRETURNS SETOF {_quote_identifier(table.name, dbms)}\nLANGUAGE sql\nAS $$\n    SELECT * FROM {_quote_identifier(table.name, dbms)};\n$$;"
    
    return f"-- SelectAll procedure for {dbms} not implemented"


def _build_proc_update(table: models.TableModel, dbms: str) -> str:
    proc_name = rules.procedure_name(table.name, "Update")
    if not table.primary_keys: return ""
    pk = table.primary_keys[0]
    cols = [c for c in table.columns if not c.is_primary_key]
    
    if dbms == "sqlserver":
        params = ",\n".join([f"    @{c.name} {_map_data_type(c.sql_type, dbms)}" for c in table.columns])
        set_clause = ", ".join([f"{_quote_identifier(c.name, dbms)} = @{c.name}" for c in cols])
        return f"CREATE PROCEDURE {proc_name}\n{params}\nAS\nBEGIN\n    UPDATE {_quote_identifier(table.name, dbms)} SET {set_clause} WHERE {_quote_identifier(pk.name, dbms)} = @{pk.name};\nEND\nGO"
    
    elif dbms == "mysql":
        params = ",\n".join([f"    IN p_{c.name} {_map_data_type(c.sql_type, dbms)}" for c in table.columns])
        set_clause = ", ".join([f"{_quote_identifier(c.name, dbms)} = p_{c.name}" for c in cols])
        return f"CREATE PROCEDURE {proc_name}(\n{params}\n)\nBEGIN\n    UPDATE {_quote_identifier(table.name, dbms)} SET {set_clause} WHERE {_quote_identifier(pk.name, dbms)} = p_{pk.name};\nEND;"
    
    elif dbms == "postgresql":
        params = ",\n".join([f"    p_{c.name} {_map_data_type(c.sql_type, dbms)}" for c in table.columns])
        set_clause = ", ".join([f"{_quote_identifier(c.name, dbms)} = p_{c.name}" for c in cols])
        return f"CREATE OR REPLACE PROCEDURE {proc_name}(\n{params}\n)\nLANGUAGE plpgsql\nAS $$\nBEGIN\n    UPDATE {_quote_identifier(table.name, dbms)} SET {set_clause} WHERE {_quote_identifier(pk.name, dbms)} = p_{pk.name};\nEND;\n$$;"
    
    return f"-- Update procedure for {dbms} not implemented"


def _build_proc_delete(table: models.TableModel, dbms: str) -> str:
    proc_name = rules.procedure_name(table.name, "Delete")
    if not table.primary_keys: return ""
    pk = table.primary_keys[0]
    
    if dbms == "sqlserver":
        return f"CREATE PROCEDURE {proc_name}\n    @{pk.name} {_map_data_type(pk.sql_type, dbms)}\nAS\nBEGIN\n    DELETE FROM {_quote_identifier(table.name, dbms)} WHERE {_quote_identifier(pk.name, dbms)} = @{pk.name};\nEND\nGO"
    
    elif dbms == "mysql":
        return f"CREATE PROCEDURE {proc_name}(\n    IN p_{pk.name} {_map_data_type(pk.sql_type, dbms)}\n)\nBEGIN\n    DELETE FROM {_quote_identifier(table.name, dbms)} WHERE {_quote_identifier(pk.name, dbms)} = p_{pk.name};\nEND;"
    
    elif dbms == "postgresql":
        return f"CREATE OR REPLACE PROCEDURE {proc_name}(\n    p_{pk.name} {_map_data_type(pk.sql_type, dbms)}\n)\nLANGUAGE plpgsql\nAS $$\nBEGIN\n    DELETE FROM {_quote_identifier(table.name, dbms)} WHERE {_quote_identifier(pk.name, dbms)} = p_{pk.name};\nEND;\n$$;"
    
    return f"-- Delete procedure for {dbms} not implemented"
