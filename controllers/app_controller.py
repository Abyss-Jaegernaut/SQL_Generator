from __future__ import annotations

from core import models, validators
from data.storage import Storage


class AppController:
    """Bridge between UI and core logic."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.current_project = models.DatabaseProject(database_name="")

    def set_database_name(self, name: str) -> None:
        self.current_project.database_name = name

    def set_dbms(self, dbms: str) -> None:
        self.current_project.dbms = dbms

    def set_tables(self, tables: list[models.TableModel]) -> None:
        self.current_project.tables = tables

    def build_sql_artifacts(self, actions: list[str]) -> str:
        """Return concatenated SQL scripts for all tables based on selected actions."""
        if not self.current_project.tables:
            return ""

        from core import dbms_builders
        
        # Normalize DBMS name from display format to internal format
        dbms = dbms_builders.normalize_dbms_name(self.current_project.dbms)
        blocks: list[str] = []
        
        # Database header (CREATE + USE)
        if "Database" in actions and self.current_project.database_name.strip():
            db_header = dbms_builders.build_database_header(
                self.current_project.database_name.strip(), 
                dbms
            )
            if db_header:
                blocks.append(db_header)

        for table in self.current_project.tables:
            validation = validators.validate_table(table)
            if not validation.is_valid:
                blocks.append("-- ERRORS for " + table.name + " --\n" + "\n".join(validation.errors))
                continue

            # CREATE TABLE (DBMS-specific)
            if "Table" in actions:
                blocks.append(dbms_builders.build_create_table_statement(table, dbms))
            
            # CRUD Stored Procedures
            proc_actions = [a for a in ["Insert", "GetById", "SelectAll", "Update", "Delete"] if a in actions]
            if proc_actions:
                procs = dbms_builders.build_crud_procedures(table, dbms, proc_actions)
                blocks.extend(procs)
            
            # Add INSERT statements if manual data was entered
            if "Data (Inserts)" in actions and table.rows:
                insert_sql = self._generate_insert_statements(table, dbms)
                if insert_sql:
                    blocks.append(f"-- Données saisies pour {table.name}\n{insert_sql}")

        return "\n\n".join(blocks)
    
    def _generate_insert_statements(self, table: models.TableModel, dbms: str) -> str:
        """Generate INSERT statements from manually entered rows."""
        if not table.rows:
            return ""
        
        from core import dbms_builders
        
        # Get non-auto-increment columns
        cols_names = [c.name for c in table.columns if not c.is_auto_increment]
        if not cols_names:
            return ""
        
        lines = []
        for row in table.rows:
            vals = []
            for col in table.columns:
                if col.is_auto_increment:
                    continue
                
                raw = row.get(col.name, "")
                # Format value based on type and DBMS
                formatted = dbms_builders.format_value(raw, col.sql_type, dbms)
                vals.append(formatted)
            lines.append(f"({', '.join(vals)})")
        
        if not lines:
            return ""
        
        # Quote identifiers using DBMS-specific syntax
        table_name = dbms_builders._quote_identifier(table.name, dbms)
        quoted_cols = [dbms_builders._quote_identifier(c, dbms) for c in cols_names]
        
        sql = f"INSERT INTO {table_name} ({', '.join(quoted_cols)}) VALUES\n" + ",\n".join(lines) + ";"
        
        # Add terminator if needed (for SQL Server)
        if dbms == "sqlserver":
            sql += "\nGO"
        
        return sql

    def save_project(self) -> None:
        self.storage.save_project(self.current_project)

    def load_project(self, project_id: int) -> None:
        self.current_project = self.storage.load_project(project_id)

    def list_projects(self) -> list[dict]:
        return self.storage.list_projects()

    def add_to_history(self, sql_content: str) -> None:
        self.storage.add_history(self.current_project.database_name, sql_content)

    def get_history(self) -> list[dict]:
        return self.storage.get_history()

    # --- LICENSE SYSTEM ---
    VALID_LICENSE = "ABCD-1234-EFGH-5678-IJKL"

    def is_activated(self) -> bool:
        """Check if the license is activated by checking both storage methods for consistency."""
        # Check the database-stored license key first
        db_activated = self.storage.get_license_key() == self.VALID_LICENSE
        
        # Also check the file-based activation for backward compatibility
        from activation_storage import is_activated as file_is_activated
        file_activated = file_is_activated()
        
        # If either method indicates activation, consider it activated
        # But prioritize the database method and sync the file if needed
        if db_activated and not file_activated:
            # Database says activated but file doesn't - sync the file
            from activation_storage import set_activated
            set_activated()
        elif file_activated and not db_activated:
            # File says activated but database doesn't - sync the database
            self.storage.set_license_key(self.VALID_LICENSE)
        
        return db_activated or file_activated

    def activate_license(self, key: str) -> bool:
        """Try to activate with a key."""
        if key.strip().upper() == self.VALID_LICENSE:
            self.storage.set_license_key(self.VALID_LICENSE)
            # Also update the file-based activation for consistency
            from activation_storage import set_activated
            set_activated()
            return True
        return False