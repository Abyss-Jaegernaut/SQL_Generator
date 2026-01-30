from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict

from core import models


class Storage:
    """SQLite-backed storage for offline projects."""

    def __init__(self, db_path: str) -> None:
        try:
            self.db_path = self._resolve_db_path(db_path)
            self._init_db()
        except Exception as e:
            # Handle any database initialization errors gracefully
            raise Exception(f"Impossible d'initialiser la base de données: {str(e)}")

    def save_project(self, project: models.DatabaseProject) -> None:
        """Upsert a project. Returns project id."""
        try:
            payload = _project_to_payload(project)
            with sqlite3.connect(self.db_path) as con:
                con.execute(
                    "INSERT INTO projects(name, payload_json) VALUES(?, ?) "
                    "ON CONFLICT(name) DO UPDATE SET payload_json=excluded.payload_json, updated_at=CURRENT_TIMESTAMP",
                    (payload["name"], payload["payload_json"]),
                )
                con.commit()
        except Exception:
            # Silently handle project saving errors
            pass

    def add_history(self, project_name: str, sql_content: str) -> None:
        """Save generated SQL to history, keeping only the last 10 entries."""
        if not sql_content.strip():
            return
            
        try:
            with sqlite3.connect(self.db_path) as con:
                # Insert new entry
                con.execute(
                    "INSERT INTO history(project_name, sql_content) VALUES(?, ?)",
                    (project_name or "Sans nom", sql_content)
                )
                
                # Delete old entries to keep only 10
                con.execute(
                    """
                    DELETE FROM history 
                    WHERE id NOT IN (
                        SELECT id FROM history ORDER BY created_at DESC LIMIT 10
                    )
                    """
                )
                con.commit()
        except Exception:
            # Silently handle history saving errors
            pass

    def delete_history_entry(self, entry_id: int) -> None:
        """Delete a single history entry by ID."""
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("DELETE FROM history WHERE id = ?", (entry_id,))
                con.commit()
        except Exception:
            pass
    
    def clear_history(self) -> None:
        """Clear all history entries."""
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("DELETE FROM history")
                con.execute("DELETE FROM sqlite_sequence WHERE name='history'")
                con.commit()
        except Exception:
            pass

    def get_history(self) -> list[dict]:
        """Retrieve the last 10 history entries."""
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.execute("SELECT id, project_name, sql_content, created_at FROM history ORDER BY created_at DESC")
                rows = cur.fetchall()
            return [{"id": r[0], "project_name": r[1], "sql_content": r[2], "created_at": r[3]} for r in rows]
        except Exception:
            # Return empty history if there's an error
            return []

    def load_project(self, project_id: int) -> models.DatabaseProject:
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.execute("SELECT payload_json FROM projects WHERE id = ?", (project_id,))
                row = cur.fetchone()
            if not row:
                return models.DatabaseProject(database_name="")
            return _payload_to_project(row[0])
        except Exception:
            # Return empty project if there's an error
            return models.DatabaseProject(database_name="")

    def list_projects(self) -> list[dict]:
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.execute("SELECT id, name, updated_at FROM projects ORDER BY updated_at DESC")
                rows = cur.fetchall()
            return [{"id": r[0], "name": r[1], "updated_at": r[2]} for r in rows]
        except Exception:
            # Return empty list if there's an error
            return []

    def load_project_by_name(self, name: str) -> models.DatabaseProject:
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.execute("SELECT payload_json FROM projects WHERE name = ?", (name,))
                row = cur.fetchone()
            if not row:
                return models.DatabaseProject(database_name="")
            return _payload_to_project(row[0])
        except Exception:
            # Return empty project if there's an error
            return models.DatabaseProject(database_name="")

    def get_license_key(self) -> str | None:
        """Retrieve the saved license key if any."""
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.execute("SELECT val FROM config WHERE key = 'license_key'")
                row = cur.fetchone()
            return row[0] if row else None
        except Exception:
            # Return None if there's an error accessing the license key
            return None

    def set_license_key(self, key: str) -> None:
        """Save the license key."""
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute(
                    "INSERT INTO config(key, val) VALUES('license_key', ?) "
                    "ON CONFLICT(key) DO UPDATE SET val=excluded.val",
                    (key,)
                )
                con.commit()
        except Exception:
            # Silently handle license setting errors
            pass

    def get_theme(self) -> str:
        """Retrieve the saved theme name, defaults to 'Clair'."""
        try:
            with sqlite3.connect(self.db_path) as con:
                cur = con.execute("SELECT val FROM config WHERE key = 'theme'")
                row = cur.fetchone()
            return row[0] if row else "Clair"
        except Exception:
            return "Clair"

    def set_theme(self, theme_name: str) -> None:
        """Save the theme name."""
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute(
                    "INSERT INTO config(key, val) VALUES('theme', ?) "
                    "ON CONFLICT(key) DO UPDATE SET val=excluded.val",
                    (theme_name,)
                )
                con.commit()
        except Exception:
            pass

    def _init_db(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
            with sqlite3.connect(self.db_path) as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS config (
                        key TEXT PRIMARY KEY,
                        val TEXT
                    )
                    """
                )
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        payload_json TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_name TEXT,
                        sql_content TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                con.commit()
        except Exception as e:
            raise Exception(f"Impossible de créer les tables de la base de données: {str(e)}")

    def _resolve_db_path(self, db_path: str) -> str:
        # Use APPDATA when available (Windows), fallback to local.
        if os.path.isabs(db_path):
            return db_path
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        app_dir = os.path.join(base, "SQL_GENERATOR")
        # Ensure the directory exists
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, db_path)


def _project_to_payload(project: models.DatabaseProject) -> dict[str, str]:
    # V1.0.1 stores one-table project, but payload supports multiple.
    name = project.database_name.strip() or "default"
    payload = asdict(project)
    return {"name": name, "payload_json": json.dumps(payload, ensure_ascii=False)}


def _payload_to_project(payload_json: str) -> models.DatabaseProject:
    try:
        data = json.loads(payload_json)
        tables = []
        for t in data.get("tables", []):
            cols = [models.ColumnModel(**c) for c in t.get("columns", [])]
            rows = t.get("rows", [])
            tables.append(models.TableModel(name=t.get("name", ""), columns=cols, rows=rows))
        
        return models.DatabaseProject(
            database_name=data.get("database_name", ""),
            dbms=data.get("dbms", "SQL Server"), # Default to SQL Server if missing
            tables=tables
        )
    except Exception:
        # Return empty project if there's an error parsing
        return models.DatabaseProject(database_name="")