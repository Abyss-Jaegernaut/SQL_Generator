from __future__ import annotations

from core import models, validators
from data.storage import Storage


class AppController:
    """Bridge between UI and core logic."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.current_project = models.DatabaseProject(database_name="")
        self._cached_machine_code = None

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

        return "\n\n".join([b for b in blocks if b.strip()])
    
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

    def delete_history_entry(self, entry_id: int) -> None:
        self.storage.delete_history_entry(entry_id)

    def clear_history(self) -> None:
        self.storage.clear_history()

    def get_history(self) -> list[dict]:
        return self.storage.get_history()

    def get_theme(self) -> str:
        return self.storage.get_theme()

    def set_theme(self, theme_name: str) -> None:
        self.storage.set_theme(theme_name)

    # --- HARDWARE-BASED LICENSE SYSTEM ---
    # Obfuscated secret phrase for license system
    @property
    def SECRET_PHRASE(self) -> str:
        # Reconstruct the secret to avoid simple string searches
        return "".join(["SQL_", "GEN", "ERATOR", "_S", "ECRET", "_ABYSS_2026"])

    @property
    def LEGACY_SECRETS(self) -> list[str]:
        """List of previous secret phrases for backward compatibility migration."""
        return [
            # Example: "OLD_SECRET_PHRASE",
            # Add older secrets here when you change the main SECRET_PHRASE
        ]

    def get_machine_code(self) -> str:
        """Get the current machine's hardware code (cached)"""
        if self._cached_machine_code:
            return self._cached_machine_code
            
        try:
            # Try to import our hardware ID module
            from utils.hardware_id import generate_machine_code
            self._cached_machine_code = generate_machine_code()
            return self._cached_machine_code
        except Exception:
            # Fallback if hardware_id module doesn't exist yet
            return "MACH-FALL-BACKK-CODEE"
    
    def is_activated(self) -> bool:
        """Check if the license is activated using hardware-based verification."""
        try:
            # Get the machine code for this computer
            current_machine_code = self.get_machine_code()
            
            # Get the activation key from storage
            stored_key = self.storage.get_license_key()
            
            if not stored_key:
                return False
            
            # Verify if the stored key matches this machine
            from utils.hardware_id import verify_activation_key, generate_activation_key
            
            # 1. Try CURRENT secret
            if verify_activation_key(current_machine_code, stored_key, self.SECRET_PHRASE):
                return True
                
            # 2. Try LEGACY secrets (Migration)
            for old_secret in self.LEGACY_SECRETS:
                if verify_activation_key(current_machine_code, stored_key, old_secret):
                    # Found valid legacy key! Migrate it SILENTLY to new format.
                    try:
                        new_key = generate_activation_key(current_machine_code, self.SECRET_PHRASE)
                        self.storage.set_license_key(new_key)
                        print(f"INFO: License migrated from legacy to current version.")
                    except Exception as e:
                        print(f"WARN: Failed to migrate license: {e}")
                    return True

            return False
        except Exception:
            # If there's any error in hardware verification, assume not activated
            return False

    def activate_license(self, key: str) -> bool:
        """Try to activate with a hardware-based key."""
        try:
            # Get the machine code for this computer
            current_machine_code = self.get_machine_code()
            
            # Verify if the provided key matches this machine
            from utils.hardware_id import verify_activation_key
            if verify_activation_key(current_machine_code, key, self.SECRET_PHRASE):
                # Store the valid key in the database
                self.storage.set_license_key(key)
                
                # Also update the file-based activation for consistency
                from activation_storage import set_activated
                set_activated()
                
                return True
            else:
                return False
        except Exception:
            return False
    
    def generate_activation_key_for_machine(self, machine_code: str) -> str:
        """Generate an activation key for a specific machine code (for developer use)"""
        try:
            from utils.hardware_id import generate_activation_key
            return generate_activation_key(machine_code, self.SECRET_PHRASE)
        except ImportError:
            # If the hardware_id module doesn't exist yet, return a dummy key
            return "DEV-KEY-FOR-" + machine_code[:4]